"""Tests for third-party threat-feed fetching, parsing, and AdGuard rendering."""

from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path
from unittest.mock import AsyncMock, patch

import httpx
import pytest

from Scripts.src.external_feeds import (
    EXTERNAL_FEEDS,
    ExternalFeed,
    ExternalFeedError,
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
