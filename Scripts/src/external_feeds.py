"""Third-party threat-feed mirrors for the Brave/AdGuard filter-lists branch.

Each source below is an independently curated domain blocklist published by a
national CERT or trusted abuse-feed operator. Adding a new source is a data
change: append one :class:`ExternalFeed` entry to :data:`EXTERNAL_FEEDS`.

Every source is fetched, parsed, and published independently: one unreachable
or malformed feed never blocks the others or the TC-SGB pipeline.

Retired source: the Azerbaijani `blacklist.gov.az` feed is out of scope. It is
no longer fetched, validated, or published, because its contents proved
unreliable and unsuitable for a curated blocklist. The publication safety
policy, the per-feed audit files, and the ``validate-external`` gate it was
introduced with stay in place for every source listed below.

Source numbering is contiguous: ``01`` Türkiye, ``02`` Polonya, ``03``
Slovenya. ``04`` is reserved for Lithuania (NKSC), whose source sits behind a
Cloudflare challenge and cannot be fetched yet, so no entry may take it.
"""

from __future__ import annotations

import asyncio
import csv
import io
import json
import logging
import re
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import httpx

from .outputs import _bare_ip, _normalize_rule_host
from .safety import Decision, SafetyRecord, decide_host

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class ExternalFeed:
    """One third-party blocklist source."""

    key: str
    url: str
    format: str
    output_file: str
    title: str
    homepage: str


EXTERNAL_FEEDS: tuple[ExternalFeed, ...] = (
    ExternalFeed(
        key="cert-pl",
        url="https://hole.cert.pl/domains/v2/domains.txt",
        format="lines",
        output_file="02-polonya-certpl_adguard.txt",
        title="Polonya | CERT.PL Hole Domains (AdGuard)",
        homepage="https://hole.cert.pl/",
    ),
    ExternalFeed(
        key="cert-si",
        url="https://www.cert.si/misp/rpz/all.txt",
        format="csv",
        output_file="03-slovenya-certsi_adguard.txt",
        title="Slovenya | CERT.SI MISP RPZ Domains (AdGuard)",
        homepage="https://www.cert.si/",
    ),
)

FETCH_TIMEOUT = 120.0
FETCH_MAX_RETRIES = 3
MAX_FEED_BYTES = 50 * 1024 * 1024


class ExternalFeedError(Exception):
    """Raised when a single external feed cannot be fetched."""


async def fetch_feed_text(feed: ExternalFeed, timeout: float = FETCH_TIMEOUT) -> str:
    """Download one feed as text with retries and exponential backoff."""
    last_error = "no attempts made"
    async with httpx.AsyncClient(timeout=timeout, follow_redirects=True) as client:
        for attempt in range(FETCH_MAX_RETRIES):
            try:
                response = await client.get(
                    feed.url,
                    headers={"User-Agent": "TC-SGB-API-to-List/1.0 (threat-intel mirror)"},
                )
                if response.status_code == 200:
                    if len(response.content) > MAX_FEED_BYTES:
                        raise ExternalFeedError(
                            f"{feed.key}: payload exceeds {MAX_FEED_BYTES} bytes"
                        )
                    return response.text
                last_error = f"HTTP {response.status_code}"
                logger.warning(
                    "Feed %s returned %s (attempt %d/%d)",
                    feed.key,
                    response.status_code,
                    attempt + 1,
                    FETCH_MAX_RETRIES,
                )
            except (httpx.TimeoutException, httpx.TransportError) as e:
                last_error = str(e)
                logger.warning(
                    "Feed %s transport error (attempt %d/%d): %s",
                    feed.key,
                    attempt + 1,
                    FETCH_MAX_RETRIES,
                    e,
                )
            if attempt < FETCH_MAX_RETRIES - 1:
                await asyncio.sleep(2**attempt)
    raise ExternalFeedError(f"{feed.key}: failed after {FETCH_MAX_RETRIES} attempts ({last_error})")


def _clean_candidate(raw: str) -> str | None:
    """Normalize one candidate domain; None when unusable."""
    text = raw.strip().lower().rstrip(".")
    if not text or text.startswith("#"):
        return None
    bare = _bare_ip(text)
    if bare is not None:
        return bare
    return _normalize_rule_host(text)


def parse_hosts(text: str) -> list[str]:
    """Parse hosts-file style feeds: comments plus bare or IP-prefixed domains."""
    hosts: list[str] = []
    seen: set[str] = set()
    for line in text.splitlines():
        line = line.split("#", 1)[0].strip()
        if not line:
            continue
        tokens = line.split()
        if len(tokens) == 1:
            candidates = tokens
        elif _bare_ip(tokens[0]) is not None:
            candidates = tokens[1:]
        else:
            continue
        for token in candidates:
            host = _clean_candidate(token)
            if host is not None and host not in seen:
                seen.add(host)
                hosts.append(host)
    return hosts


def parse_lines(text: str) -> list[str]:
    """Parse bare one-domain-per-line feeds."""
    hosts: list[str] = []
    seen: set[str] = set()
    for line in text.splitlines():
        host = _clean_candidate(line)
        if host is not None and host not in seen:
            seen.add(host)
            hosts.append(host)
    return hosts


def parse_csv_domain(text: str) -> list[str]:
    """Parse CSV feeds carrying a domain column (e.g. ``timestamp,domain``)."""
    hosts: list[str] = []
    seen: set[str] = set()
    reader = csv.reader(io.StringIO(text))
    domain_index: int | None = None
    for row in reader:
        if not row or all(not cell.strip() for cell in row):
            continue
        if domain_index is None:
            lowered = [cell.strip().lower() for cell in row]
            if "domain" in lowered:
                domain_index = lowered.index("domain")
                continue
            domain_index = len(row) - 1
        if domain_index >= len(row):
            continue
        host = _clean_candidate(row[domain_index])
        if host is not None and host not in seen:
            seen.add(host)
            hosts.append(host)
    return hosts


PARSERS = {
    "hosts": parse_hosts,
    "lines": parse_lines,
    "csv": parse_csv_domain,
}


def extract_source_timestamp(text: str) -> str | None:
    """Return the feed's own update stamp when it declares one."""
    match = re.search(r"(?im)^[#;]?\s*latest update at:\s*(.+?)\s*$", text)
    if match:
        return match.group(1)
    return None


def apply_policy(
    hosts: list[str], *, source: str
) -> tuple[list[str], list[SafetyRecord], list[SafetyRecord]]:
    """Split parsed hosts into accepted, rejected, and review records."""
    accepted: list[str] = []
    rejected: list[SafetyRecord] = []
    review: list[SafetyRecord] = []
    for host in hosts:
        record = decide_host(host, source=source)
        if record.decision == Decision.ACCEPT:
            accepted.append(host)
        elif record.decision == Decision.REJECT:
            rejected.append(record)
        else:
            review.append(record)
    return accepted, rejected, review


def generate_external_adguard(
    feed: ExternalFeed,
    hosts: list[str],
    generated_at: datetime | None = None,
    source_updated: str | None = None,
) -> str:
    """Render one external feed as an AdGuard ``||domain^`` list."""
    ts = (generated_at or datetime.now(UTC)).isoformat()
    header = (
        f"! Title: {feed.title}\n"
        "! Expires: 2 days\n"
        f"! Last updated: {ts}\n"
        f"! Homepage: {feed.homepage}\n"
        f"! Source: {feed.url}\n"
    )
    if source_updated:
        header += f"! Source updated: {source_updated}\n"
    lines = [f"||{host}^" for host in hosts]
    return header + "\n".join(lines) + ("\n" if lines else "")


def _read_existing_hosts(path: Path) -> list[str] | None:
    """Read the ``||host^`` rules from a previously written list, if any."""
    if not path.is_file():
        return None
    hosts: list[str] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.startswith("||") and line.endswith("^"):
            hosts.append(line[2:-1])
    return hosts


def _write_audit(
    out_dir: Path,
    feed: ExternalFeed,
    accepted: list[str],
    rejected: list[SafetyRecord],
    review: list[SafetyRecord],
    generated_at: datetime | None,
    source_updated: str | None,
) -> str:
    """Write the per-feed audit file; returns its path."""
    audit = {
        "feed": feed.key,
        "generated_at": (generated_at or datetime.now(UTC)).isoformat(),
        "source_updated": source_updated,
        "accepted": len(accepted),
        "rejected": len(rejected),
        "review": len(review),
        "decisions": [
            {
                "indicator": record.indicator,
                "decision": record.decision.value,
                "reason": record.reason,
            }
            for record in (*rejected, *review)
        ],
    }
    path = out_dir / f"{feed.key}_audit.json"
    path.write_text(json.dumps(audit, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return str(path)


def _write_snapshot(out_dir: Path, feed: ExternalFeed, text: str) -> str:
    """Keep the raw fetched source for reproducibility."""
    path = out_dir / f"{feed.key}_source.txt"
    path.write_text(text, encoding="utf-8")
    return str(path)


async def fetch_all_feeds(
    feeds: tuple[ExternalFeed, ...] = EXTERNAL_FEEDS,
    output_dir: str | Path = "Output/External",
    generated_at: datetime | None = None,
) -> dict[str, dict[str, Any]]:
    """Fetch every feed independently; one failure never blocks the others.

    Parsed hosts pass the publication safety policy before rendering; held
    records land in a per-feed audit file instead of the blocklist. Files
    are written only when their rules change. Returns a per-feed status
    mapping with ``status`` (written/skipped/failed/empty), ``rules``,
    ``rejected``/``review`` counts, and ``path``/``error`` details.
    """
    out_dir = Path(output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    results: dict[str, dict[str, Any]] = {}
    for feed in feeds:
        try:
            text = await fetch_feed_text(feed)
            parser = PARSERS[feed.format]
            hosts = parser(text)
        except (ExternalFeedError, KeyError) as e:
            logger.warning("Skipping feed %s: %s", feed.key, e)
            results[feed.key] = {"status": "failed", "rules": 0, "error": str(e)}
            continue
        if not hosts:
            logger.warning("Feed %s parsed to zero hosts; keeping previous file", feed.key)
            results[feed.key] = {"status": "empty", "rules": 0}
            continue
        accepted, rejected, review = apply_policy(hosts, source=feed.key)
        if rejected:
            logger.warning("Feed %s held %d indicators by safety policy", feed.key, len(rejected))
        if review:
            logger.warning("Feed %s held %d indicators for review", feed.key, len(review))
        source_updated = extract_source_timestamp(text)
        content = generate_external_adguard(feed, accepted, generated_at, source_updated)
        path = out_dir / feed.output_file
        audit_path = _write_audit(
            out_dir, feed, accepted, rejected, review, generated_at, source_updated
        )
        snapshot_path = _write_snapshot(out_dir, feed, text)
        outcome: dict[str, Any] = {
            "rules": len(accepted),
            "rejected": len(rejected),
            "review": len(review),
            "audit_path": audit_path,
            "snapshot_path": snapshot_path,
            "path": str(path),
        }
        if _read_existing_hosts(path) == accepted:
            results[feed.key] = {"status": "skipped", **outcome}
            continue
        path.write_text(content, encoding="utf-8")
        results[feed.key] = {"status": "written", **outcome}
    return results


def audit_external_lists(
    output_dir: str | Path = "Output/External",
    feed_key: str | None = None,
    feeds: tuple[ExternalFeed, ...] | None = None,
) -> dict[str, dict[str, Any]]:
    """Verify published lists against the safety policy without fetching.

    Returns per-feed verdicts with ``ok``, ``rules``, ``violations``, and
    ``path``. Used by the ``validate-external`` command locally and in CI.
    """
    out_dir = Path(output_dir)
    known = EXTERNAL_FEEDS if feeds is None else feeds
    selected = [feed for feed in known if feed_key is None or feed.key == feed_key]
    verdicts: dict[str, dict[str, Any]] = {}
    if feed_key is not None and not selected:
        return {feed_key: {"ok": False, "rules": 0, "violations": [], "error": "unknown feed"}}
    for feed in selected:
        path = out_dir / feed.output_file
        hosts = _read_existing_hosts(path)
        if hosts is None:
            verdicts[feed.key] = {
                "ok": True,
                "skipped": True,
                "rules": 0,
                "violations": [],
                "path": str(path),
                "note": "file missing",
            }
            continue
        violations = [
            host for host in hosts if decide_host(host, source=feed.key).decision != Decision.ACCEPT
        ]
        verdicts[feed.key] = {
            "ok": not violations,
            "rules": len(hosts),
            "violations": violations,
            "path": str(path),
        }
    return verdicts
