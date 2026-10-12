"""Third-party threat-feed mirrors for the Brave/AdGuard filter-lists branch.

Each source below is an independently curated domain blocklist published by a
national CERT or trusted abuse-feed operator. Adding a new source is a data
change: append one :class:`ExternalFeed` entry to :data:`EXTERNAL_FEEDS`.

Every source is fetched, parsed, and published independently: one unreachable
or malformed feed never blocks the others or the TC-SGB pipeline.
"""

from __future__ import annotations

import asyncio
import csv
import io
import logging
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import httpx

from .outputs import _bare_ip, _normalize_rule_host

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
        key="blacklist-az",
        url="https://blacklist.gov.az/download/threatfeed",
        format="hosts",
        output_file="03-azerbaycan-blacklist_adguard.txt",
        title="Azerbaycan | Blacklist.gov.az Threat Feed (AdGuard)",
        homepage="https://blacklist.gov.az/",
    ),
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
        output_file="05-slovenya-certsi_adguard.txt",
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


def generate_external_adguard(
    feed: ExternalFeed,
    hosts: list[str],
    generated_at: datetime | None = None,
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


async def fetch_all_feeds(
    feeds: tuple[ExternalFeed, ...] = EXTERNAL_FEEDS,
    output_dir: str | Path = "Output/External",
    generated_at: datetime | None = None,
) -> dict[str, dict[str, Any]]:
    """Fetch every feed independently; one failure never blocks the others.

    Files are written only when their bytes change. Returns a per-feed
    status mapping with ``status`` (written/skipped/failed/empty),
    ``rules``, and ``path``/``error`` details.
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
        content = generate_external_adguard(feed, hosts, generated_at)
        path = out_dir / feed.output_file
        if _read_existing_hosts(path) == hosts:
            results[feed.key] = {"status": "skipped", "rules": len(hosts), "path": str(path)}
            continue
        path.write_text(content, encoding="utf-8")
        results[feed.key] = {"status": "written", "rules": len(hosts), "path": str(path)}
    return results
