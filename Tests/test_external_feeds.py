"""Tests for third-party threat-feed fetching, parsing, and AdGuard rendering."""

from __future__ import annotations

import json
import re
from datetime import UTC, datetime
from pathlib import Path
from unittest.mock import AsyncMock, patch

import httpx
import pytest

from Scripts.src.external_feeds import (
    EXTERNAL_FEEDS,
    ExternalFeed,
    ExternalFeedError,
    apply_policy,
    audit_external_lists,
    extract_source_timestamp,
    fetch_all_feeds,
    fetch_feed_text,
    generate_external_adguard,
    parse_csv_domain,
    parse_hosts,
    parse_lines,
)

FEED = ExternalFeed(
    key="test",
    url="https://example.com/feed.txt",
    format="lines",
    output_file="test_adguard.txt",
    title="Test Feed (AdGuard)",
    homepage="https://example.com/",
)

FIXED_AT = datetime(2026, 10, 12, tzinfo=UTC)


def test_feed_table_valid():
    keys = [feed.key for feed in EXTERNAL_FEEDS]
    assert len(keys) >= 1
    assert len(set(keys)) == len(keys)
    outputs = [feed.output_file for feed in EXTERNAL_FEEDS]
    assert len(set(outputs)) == len(outputs)
    for feed in EXTERNAL_FEEDS:
        assert feed.url.startswith("https://")
        assert feed.output_file.endswith("_adguard.txt")


def test_parse_hosts():
    text = (
        "# comment line\n"
        "\n"
        "evil.com\n"
        "0.0.0.0 bad.net # inline comment\n"
        "127.0.0.1 evil.com\n"
        "not a domain!!\n"
    )
    assert parse_hosts(text) == ["evil.com", "bad.net"]


def test_parse_lines():
    text = "evil.com\n\nBAD.NET.\n   \nnot a domain!!\nevil.com\n"
    assert parse_lines(text) == ["evil.com", "bad.net"]


def test_parse_csv_domain():
    text = "timestamp,domain\n2026-10-12 13:50:13+00:00,evil.com\n, bad.net\n"
    assert parse_csv_domain(text) == ["evil.com", "bad.net"]


def test_parse_csv_domain_without_header_uses_last_column():
    text = "2026-10-12,feed,evil.com\n2026-10-11,feed,bad.net\n"
    assert parse_csv_domain(text) == ["evil.com", "bad.net"]


def test_generate_external_adguard():
    content = generate_external_adguard(FEED, ["evil.com", "bad.net"], FIXED_AT)
    assert content.startswith("! Title: Test Feed (AdGuard)\n")
    assert "! Expires: 2 days\n" in content
    assert f"! Source: {FEED.url}\n" in content
    assert "||evil.com^\n||bad.net^\n" in content


@pytest.mark.asyncio
async def test_fetch_all_feeds_writes_skips_and_tolerates_failure(tmp_path: Path):
    async def fake_fetch(feed: ExternalFeed) -> str:
        if feed.key == "ok":
            return "evil.com\n"
        raise ExternalFeedError("boom")

    feeds = (
        ExternalFeed(
            "ok", "https://ok.example/f", "lines", "ok_adguard.txt", "OK", "https://ok.example/"
        ),
        ExternalFeed(
            "down",
            "https://down.example/f",
            "lines",
            "down_adguard.txt",
            "Down",
            "https://down.example/",
        ),
    )
    with patch("Scripts.src.external_feeds.fetch_feed_text", side_effect=fake_fetch):
        first = await fetch_all_feeds(feeds, output_dir=tmp_path)
        assert first["ok"]["status"] == "written"
        assert first["ok"]["rules"] == 1
        assert first["down"]["status"] == "failed"

        second = await fetch_all_feeds(feeds, output_dir=tmp_path)
        assert second["ok"]["status"] == "skipped"
        assert second["down"]["status"] == "failed"


@pytest.mark.asyncio
async def test_fetch_all_feeds_keeps_previous_file_on_empty_parse(tmp_path: Path):
    async def fake_fetch(feed: ExternalFeed) -> str:
        return "# nothing usable here\n"

    with patch("Scripts.src.external_feeds.fetch_feed_text", side_effect=fake_fetch):
        results = await fetch_all_feeds((FEED,), output_dir=tmp_path)
        assert results["test"]["status"] == "empty"
        assert not (tmp_path / FEED.output_file).exists()


@pytest.mark.asyncio
async def test_fetch_feed_text_retries_then_raises() -> None:
    feed = ExternalFeed("x", "https://x.example/f", "lines", "x.txt", "X", "https://x.example/")
    with patch("httpx.AsyncClient.get", new_callable=AsyncMock) as mock_get:
        mock_get.side_effect = httpx.TimeoutException("slow")
        with pytest.raises(ExternalFeedError):
            await fetch_feed_text(feed)
        assert mock_get.await_count == 3


def test_extract_source_timestamp():
    text = "# hosts file\n# Latest update at: 2026-09-29 02:10:00\n\nevil.com\n"
    assert extract_source_timestamp(text) == "2026-09-29 02:10:00"
    assert extract_source_timestamp("evil.com\nbad.net\n") is None


def test_generate_external_adguard_with_source_updated():
    content = generate_external_adguard(FEED, ["evil.com"], FIXED_AT, "2026-09-29 02:10:00")
    assert "! Source updated: 2026-09-29 02:10:00\n" in content
    assert "! Last updated: 2026-10-12T00:00:00+00:00\n" in content


def test_apply_policy_splits_verdicts():
    accepted, rejected, review = apply_policy(
        ["evil.com", "google.com", "docs.google.com"], source="test"
    )
    assert accepted == ["evil.com"]
    assert [r.indicator for r in rejected] == ["google.com"]
    assert [r.indicator for r in review] == ["docs.google.com"]
    assert all(r.source == "test" for r in (*rejected, *review))


@pytest.mark.asyncio
async def test_fetch_all_feeds_applies_policy_and_writes_audit(tmp_path: Path):
    async def fake_fetch(feed: ExternalFeed) -> str:
        return (
            "# Latest update at: 2026-09-29 02:10:00\n"
            "evil.com\n"
            "google.com\n"
            "www.google.com\n"
            "docs.google.com\n"
        )

    with patch("Scripts.src.external_feeds.fetch_feed_text", side_effect=fake_fetch):
        results = await fetch_all_feeds((FEED,), output_dir=tmp_path, generated_at=FIXED_AT)

    outcome = results["test"]
    assert outcome["status"] == "written"
    assert outcome["rules"] == 1
    assert outcome["rejected"] == 2
    assert outcome["review"] == 1
    content = (tmp_path / FEED.output_file).read_text(encoding="utf-8")
    assert "||evil.com^\n" in content
    assert "||google.com^" not in content
    assert "! Source updated: 2026-09-29 02:10:00\n" in content

    audit = json.loads((tmp_path / "test_audit.json").read_text(encoding="utf-8"))
    assert audit["feed"] == "test"
    assert (audit["accepted"], audit["rejected"], audit["review"]) == (1, 2, 1)
    assert {d["indicator"] for d in audit["decisions"]} == {
        "google.com",
        "www.google.com",
        "docs.google.com",
    }
    assert (tmp_path / "test_source.txt").read_text(encoding="utf-8").startswith("# Latest")


@pytest.mark.asyncio
async def test_fetch_all_feeds_all_rejected_still_writes_empty_list(tmp_path: Path):
    async def fake_fetch(feed: ExternalFeed) -> str:
        return "google.com\n"

    with patch("Scripts.src.external_feeds.fetch_feed_text", side_effect=fake_fetch):
        results = await fetch_all_feeds((FEED,), output_dir=tmp_path, generated_at=FIXED_AT)

    assert results["test"]["status"] == "written"
    assert results["test"]["rules"] == 0


def test_audit_external_lists_pass_and_fail(tmp_path: Path):
    good = tmp_path / "good_adguard.txt"
    good.write_text("! Title: G\n||evil.com^\n", encoding="utf-8")
    bad = tmp_path / "bad_adguard.txt"
    bad.write_text("! Title: B\n||evil.com^\n||google.com^\n", encoding="utf-8")
    feeds = (
        ExternalFeed(
            "good", "https://g.example/", "lines", "good_adguard.txt", "G", "https://g.example/"
        ),
        ExternalFeed(
            "bad", "https://b.example/", "lines", "bad_adguard.txt", "B", "https://b.example/"
        ),
    )
    verdicts = audit_external_lists(tmp_path, feeds=feeds)
    assert verdicts["good"] == {
        "ok": True,
        "rules": 1,
        "violations": [],
        "path": str(good),
    }
    assert verdicts["bad"]["ok"] is False
    assert verdicts["bad"]["violations"] == ["google.com"]


def test_audit_external_lists_missing_and_unknown_feed(tmp_path: Path):
    verdicts = audit_external_lists(tmp_path, feeds=(FEED,))
    assert verdicts["test"]["ok"] is True
    assert verdicts["test"]["skipped"] is True
    unknown = audit_external_lists(tmp_path, feed_key="nope")
    assert unknown["nope"]["ok"] is False


# ---------------------------------------------------------------------------
# publish-scope guards
# ---------------------------------------------------------------------------

REPO_ROOT = Path(__file__).resolve().parent.parent
SCHEDULE = REPO_ROOT / ".github" / "workflows" / "schedule.yml"
RETIRED_AZ_FILE = "03-azerbaycan-blacklist_adguard.txt"


def test_feed_scope_is_pinned():
    assert [feed.key for feed in EXTERNAL_FEEDS] == ["cert-pl", "cert-si"]
    numbers = []
    for feed in EXTERNAL_FEEDS:
        match = re.match(r"(\d{2})-", feed.output_file)
        assert match, feed.output_file
        numbers.append(match.group(1))
    assert numbers == sorted(set(numbers)), f"file numbers must be unique and ordered: {numbers}"
    assert "04" not in numbers, "04 is reserved for Lithuania (NKSC, Cloudflare-blocked)"


def test_schedule_publishes_exactly_the_configured_feeds():
    workflow = SCHEDULE.read_text(encoding="utf-8")
    loop = re.search(r"for KEY in ([^;]+); do", workflow)
    assert loop, "feed loop not found in schedule.yml"
    assert set(loop.group(1).split()) == {feed.key for feed in EXTERNAL_FEEDS}
    for feed in EXTERNAL_FEEDS:
        assert f"{feed.key}:{feed.output_file[:2]}-" in workflow, feed.key
        assert feed.output_file in workflow, feed.output_file


def test_retired_azerbaijan_feed_is_purged_not_published():
    assert all("blacklist.gov.az" not in feed.url for feed in EXTERNAL_FEEDS)
    assert all(feed.key != "blacklist-az" for feed in EXTERNAL_FEEDS)
    workflow = SCHEDULE.read_text(encoding="utf-8")
    purge_lines = [line for line in workflow.splitlines() if RETIRED_AZ_FILE in line]
    assert len(purge_lines) == 1, f"retired file named outside the purge loop: {purge_lines}"
    assert purge_lines[0].strip().startswith("for STALE in")
    assert RETIRED_AZ_FILE not in workflow.replace(purge_lines[0], "")
