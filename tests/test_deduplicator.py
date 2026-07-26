"""Tests for deduplication across IOC types."""

from __future__ import annotations

from scripts.src.deduplicator import DeduplicationResult, deduplicate
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
        value=value, ioc_type=ioc_type,
        criticality_level=criticality_level,
        original_id=original_id, desc=desc, source=source,
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
