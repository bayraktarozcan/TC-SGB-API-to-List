"""Tests for deduplication across IOC types."""

from __future__ import annotations

from unittest.mock import patch

from scripts.src.deduplicator import (
    DeduplicationResult,
    _extract_domain_from_url,
    _make_dedup_key,
    deduplicate,
    get_dedup_stats,
)
from scripts.src.models import DescriptionCategory, IOCType, ScoredIOC, Source


def _make_scored_ioc(
    value: str,
    ioc_type: IOCType = IOCType.DOMAIN,
    criticality_level: int = 5,
    original_id: int = 0,
    quality_score: float = 50.0,
    desc: DescriptionCategory | None = None,
    source: Source | None = None,
) -> ScoredIOC:
    return ScoredIOC(
        value=value,
        ioc_type=ioc_type,
        criticality_level=criticality_level,
        original_id=original_id,
        desc=desc,
        source=source,
        quality_score=quality_score,
    )


class TestDeduplicate:
    def test_returns_deduplication_result(self):
        iocs = [_make_scored_ioc("a.com")]
        result = deduplicate(iocs)
        assert isinstance(result, DeduplicationResult)

    def test_no_duplicates(self):
        iocs = [_make_scored_ioc("a.com"), _make_scored_ioc("b.com"), _make_scored_ioc("c.com")]
        result = deduplicate(iocs)
        assert len(result.kept) == 3
        assert result.removed_count == 0
        assert result.merge_log == []

    def test_exact_duplicates_keeps_highest_score(self):
        iocs = [
            _make_scored_ioc("a.com", quality_score=50.0),
            _make_scored_ioc("a.com", quality_score=90.0),
        ]
        result = deduplicate(iocs)
        assert len(result.kept) == 1
        assert result.kept[0].quality_score == 90.0
        assert result.removed_count == 1

    def test_exact_duplicates_keeps_first_when_equal(self):
        iocs = [
            _make_scored_ioc("a.com", original_id=1, quality_score=50.0),
            _make_scored_ioc("a.com", original_id=2, quality_score=50.0),
        ]
        result = deduplicate(iocs)
        assert len(result.kept) == 1
        assert result.kept[0].original_id == 1

    def test_different_types_same_value_not_deduped(self):
        iocs = [
            _make_scored_ioc("10.0.0.1", IOCType.IP),
            _make_scored_ioc("10.0.0.1", IOCType.IP6),
        ]
        result = deduplicate(iocs)
        assert len(result.kept) == 2
        assert result.removed_count == 0

    def test_url_domain_cross_dedup(self):
        iocs = [
            _make_scored_ioc("evil.com", IOCType.DOMAIN, quality_score=50.0),
            _make_scored_ioc("https://evil.com/path", IOCType.URL, quality_score=90.0),
        ]
        result = deduplicate(iocs)
        # URL has higher score, so it replaces the domain
        assert len(result.kept) == 1
        assert result.kept[0].ioc_type == IOCType.URL
        assert result.kept[0].quality_score == 90.0

    def test_url_domain_dedup_keeps_domain_if_higher_score(self):
        iocs = [
            _make_scored_ioc("evil.com", IOCType.DOMAIN, quality_score=90.0),
            _make_scored_ioc("https://evil.com/path", IOCType.URL, quality_score=50.0),
        ]
        result = deduplicate(iocs)
        assert len(result.kept) == 1
        assert result.kept[0].ioc_type == IOCType.DOMAIN

    def test_empty_input(self):
        result = deduplicate([])
        assert result.kept == []
        assert result.removed_count == 0
        assert result.merge_log == []

    def test_single_item(self):
        result = deduplicate([_make_scored_ioc("only.com")])
        assert len(result.kept) == 1
        assert result.removed_count == 0

    def test_many_duplicates(self):
        iocs = [_make_scored_ioc("same.com", quality_score=float(i)) for i in range(100)]
        result = deduplicate(iocs)
        assert len(result.kept) == 1
        assert result.removed_count == 99
        # Should keep the highest score
        assert result.kept[0].quality_score == 99.0

    def test_mixed_duplicates(self):
        iocs = [
            _make_scored_ioc("a.com", quality_score=10.0),
            _make_scored_ioc("b.com", quality_score=20.0),
            _make_scored_ioc("a.com", quality_score=30.0),
            _make_scored_ioc("c.com", quality_score=40.0),
            _make_scored_ioc("b.com", quality_score=50.0),
            _make_scored_ioc("b.com", quality_score=60.0),
        ]
        result = deduplicate(iocs)
        assert len(result.kept) == 3
        assert result.removed_count == 3
        kept_values = sorted([k.value for k in result.kept])
        assert kept_values == ["a.com", "b.com", "c.com"]

    def test_merge_log_populated(self):
        iocs = [
            _make_scored_ioc("a.com", quality_score=10.0),
            _make_scored_ioc("a.com", quality_score=90.0),
        ]
        result = deduplicate(iocs)
        assert len(result.merge_log) == 1
        assert "Replaced" in result.merge_log[0]

    def test_merge_metadata_flag(self):
        iocs = [
            _make_scored_ioc("a.com", quality_score=50.0),
            _make_scored_ioc("a.com", quality_score=90.0),
        ]
        result = deduplicate(iocs, merge_metadata=True)
        assert len(result.kept) == 1

    def test_no_merge_metadata(self):
        iocs = [
            _make_scored_ioc("a.com", quality_score=50.0),
            _make_scored_ioc("a.com", quality_score=90.0),
        ]
        result = deduplicate(iocs, merge_metadata=False)
        assert len(result.kept) == 1

    def test_preserves_types_independent(self):
        iocs = [
            _make_scored_ioc("evil.com", IOCType.DOMAIN, quality_score=50.0),
            _make_scored_ioc("evil.com", IOCType.URL, quality_score=50.0),
        ]
        result = deduplicate(iocs)
        assert len(result.kept) == 2

    def test_deterministic_results(self):
        iocs = [_make_scored_ioc("x.com", quality_score=float(i)) for i in range(10)]
        r1 = deduplicate(iocs)
        r2 = deduplicate(iocs)
        assert [u.value for u in r1.kept] == [u.value for u in r2.kept]
        assert r1.removed_count == r2.removed_count


# ---------------------------------------------------------------------------
# _extract_domain_from_url edge cases
# ---------------------------------------------------------------------------


class TestExtractDomainFromUrl:
    def test_valid_url(self):
        assert _extract_domain_from_url("https://evil.com/path") == "evil.com"

    def test_empty_string(self):
        assert _extract_domain_from_url("") is None

    def test_no_scheme(self):
        result = _extract_domain_from_url("evil.com")
        assert result is None

    def test_trailing_dot_stripped(self):
        assert _extract_domain_from_url("https://evil.com.") == "evil.com"

    def test_lowercase(self):
        assert _extract_domain_from_url("https://EVIL.COM/path") == "evil.com"

    def test_garbage_url_returns_none(self):
        assert _extract_domain_from_url("not a url at all") is None

    def test_urlparse_raises_returns_none(self):
        with patch("urllib.parse.urlparse", side_effect=Exception("boom")):
            assert _extract_domain_from_url("https://evil.com/path") is None


# ---------------------------------------------------------------------------
# _make_dedup_key edge cases
# ---------------------------------------------------------------------------


class TestMakeDedupKey:
    def test_domain_key(self):
        key = _make_dedup_key("evil.com", IOCType.DOMAIN)
        assert key == "domain|evil.com"

    def test_ip_key(self):
        _unused = _make_scored_ioc  # just to check syntax
        assert _make_dedup_key("10.0.0.1", IOCType.IP) == "ip|10.0.0.1"

    def test_url_key_with_domain(self):
        key = _make_dedup_key("https://evil.com/path", IOCType.URL)
        assert "url|" in key
        assert "domain|evil.com" in key

    def test_url_key_without_valid_domain(self):
        key = _make_dedup_key("https://", IOCType.URL)
        assert key == "url|https://"

    def test_strips_whitespace_and_trailing_dot(self):
        key = _make_dedup_key("  EVIL.COM.  ", IOCType.DOMAIN)
        assert key == "domain|evil.com"


# ---------------------------------------------------------------------------
# get_dedup_stats
# ---------------------------------------------------------------------------


class TestGetDedupStats:
    def test_basic(self):
        stats = get_dedup_stats(100, 80)
        assert stats == {"before": 100, "after": 80, "removed": 20}

    def test_no_duplicates(self):
        stats = get_dedup_stats(50, 50)
        assert stats["removed"] == 0

    def test_all_duplicates(self):
        stats = get_dedup_stats(100, 0)
        assert stats["removed"] == 100

    def test_empty_input(self):
        stats = get_dedup_stats(0, 0)
        assert stats == {"before": 0, "after": 0, "removed": 0}
