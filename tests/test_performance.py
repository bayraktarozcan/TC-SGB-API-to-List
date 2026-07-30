"""Performance benchmarks: measure time for processing 100, 1000, 10000 IoCs."""

from __future__ import annotations

import random
import string
import time
from datetime import datetime

import pytest

from scripts.src.deduplicator import deduplicate
from scripts.src.models import (
    ConnectionType,
    DescriptionCategory,
    IOCType,
    NormalizedIOC,
    ScoredIOC,
    Source,
    ValidatedIOC,
)
from scripts.src.normalizer import normalize_batch
from scripts.src.outputs import (
    generate_adguard,
    generate_csv,
    generate_json,
    generate_nextdns,
    generate_sqlite,
)
from scripts.src.quality import filter_false_positives, score_ioc


def _random_domain(length: int = 12) -> str:
    chars = string.ascii_lowercase + string.digits + "-"
    return "".join(random.choices(chars, k=length)) + ".com"


def _generate_iocs(count: int, dup_ratio: float = 0.2) -> list[NormalizedIOC]:
    """Generate N NormalizedIOCs with a controlled duplicate ratio (for normalize/quality)."""
    unique_count = int(count * (1 - dup_ratio))
    iocs: list[NormalizedIOC] = []
    descs = list(DescriptionCategory)
    sources = list(Source)
    conns = list(ConnectionType)

    for i in range(unique_count):
        iocs.append(
            NormalizedIOC(
                value=_random_domain(),
                ioc_type=random.choice([IOCType.DOMAIN, IOCType.IP]),
                desc=random.choice(descs),
                source=random.choice(sources),
                date=datetime(2024, 1, 1),
                criticality_level=random.randint(1, 10),
                connectiontype=random.choice(conns),
                original_id=i,
            )
        )

    dup_count = count - unique_count
    for _ in range(dup_count):
        original = random.choice(iocs[:unique_count])
        iocs.append(
            NormalizedIOC(
                value=original.value,
                ioc_type=original.ioc_type,
                desc=original.desc,
                source=original.source,
                date=original.date,
                criticality_level=random.randint(1, 10),
                connectiontype=original.connectiontype,
                original_id=original.original_id,
            )
        )

    random.shuffle(iocs)
    return iocs


def _generate_scored_for_dedup(count: int, dup_ratio: float = 0.2) -> list[ScoredIOC]:
    """Generate N ScoredIOCs with controlled duplicate ratio (for dedup tests)."""
    unique_count = int(count * (1 - dup_ratio))
    iocs: list[ScoredIOC] = []
    descs = list(DescriptionCategory)
    sources = list(Source)
    conns = list(ConnectionType)

    for i in range(unique_count):
        iocs.append(
            ScoredIOC(
                value=_random_domain(),
                ioc_type=random.choice([IOCType.DOMAIN, IOCType.IP]),
                desc=random.choice(descs),
                source=random.choice(sources),
                date=datetime(2024, 1, 1),
                criticality_level=random.randint(1, 10),
                connectiontype=random.choice(conns),
                original_id=i,
                quality_score=random.uniform(20, 100),
                false_positive_risk="low",
            )
        )

    dup_count = count - unique_count
    for _ in range(dup_count):
        original = random.choice(iocs[:unique_count])
        iocs.append(
            ScoredIOC(
                value=original.value,
                ioc_type=original.ioc_type,
                desc=original.desc,
                source=original.source,
                date=original.date,
                criticality_level=random.randint(1, 10),
                connectiontype=original.connectiontype,
                original_id=original.original_id,
                quality_score=random.uniform(20, 100),
                false_positive_risk="low",
            )
        )

    random.shuffle(iocs)
    return iocs


def _generate_validated_iocs(count: int) -> list[ValidatedIOC]:
    iocs: list[ValidatedIOC] = []
    for i in range(count):
        iocs.append(
            ValidatedIOC(
                raw_url=_random_domain(),
                ioc_type=IOCType.DOMAIN,
                desc=random.choice(list(DescriptionCategory)),
                source=random.choice(list(Source)),
                date=datetime(2024, 1, 1),
                criticality_level=random.randint(1, 10),
                connectiontype=random.choice(list(ConnectionType)),
                original_id=i,
            )
        )
    return iocs


def _generate_scored_iocs(count: int) -> list[ScoredIOC]:
    iocs: list[ScoredIOC] = []
    for i in range(count):
        iocs.append(
            ScoredIOC(
                value=_random_domain(),
                ioc_type=random.choice([IOCType.DOMAIN, IOCType.IP]),
                desc=random.choice(list(DescriptionCategory)),
                source=random.choice(list(Source)),
                date=datetime(2024, 1, 1),
                criticality_level=random.randint(1, 10),
                connectiontype=random.choice(list(ConnectionType)),
                original_id=i,
                quality_score=random.uniform(20, 100),
                false_positive_risk="low",
            )
        )
    return iocs


# ---------------------------------------------------------------------------
# Normalization benchmarks
# ---------------------------------------------------------------------------


class TestNormalizationPerf:
    @pytest.mark.slow
    def test_normalize_100(self):
        iocs = _generate_validated_iocs(100)
        t0 = time.perf_counter()
        normalize_batch(iocs)
        elapsed = time.perf_counter() - t0
        assert elapsed < 5.0

    @pytest.mark.slow
    def test_normalize_1000(self):
        iocs = _generate_validated_iocs(1000)
        t0 = time.perf_counter()
        normalize_batch(iocs)
        elapsed = time.perf_counter() - t0
        assert elapsed < 30.0

    @pytest.mark.slow
    def test_normalize_10000(self):
        iocs = _generate_validated_iocs(10000)
        t0 = time.perf_counter()
        normalize_batch(iocs)
        elapsed = time.perf_counter() - t0
        assert elapsed < 120.0


# ---------------------------------------------------------------------------
# Deduplication benchmarks
# ---------------------------------------------------------------------------


class TestDedupPerf:
    @pytest.mark.slow
    def test_dedup_100(self):
        iocs = _generate_scored_for_dedup(100, dup_ratio=0.3)
        t0 = time.perf_counter()
        result = deduplicate(iocs)
        elapsed = time.perf_counter() - t0
        assert elapsed < 2.0
        assert result.removed_count > 0
        assert len(result.kept) + result.removed_count == 100

    @pytest.mark.slow
    def test_dedup_1000(self):
        iocs = _generate_scored_for_dedup(1000, dup_ratio=0.3)
        t0 = time.perf_counter()
        result = deduplicate(iocs)
        elapsed = time.perf_counter() - t0
        assert elapsed < 10.0

    @pytest.mark.slow
    def test_dedup_10000(self):
        iocs = _generate_scored_for_dedup(10000, dup_ratio=0.3)
        t0 = time.perf_counter()
        result = deduplicate(iocs)
        elapsed = time.perf_counter() - t0
        assert elapsed < 60.0


# ---------------------------------------------------------------------------
# Quality scoring benchmarks
# ---------------------------------------------------------------------------


class TestQualityPerf:
    @pytest.mark.slow
    def test_score_100(self):
        iocs = _generate_iocs(100, dup_ratio=0)
        t0 = time.perf_counter()
        scored = [score_ioc(ioc) for ioc in iocs]
        elapsed = time.perf_counter() - t0
        assert elapsed < 2.0

    @pytest.mark.slow
    def test_score_1000(self):
        iocs = _generate_iocs(1000, dup_ratio=0)
        t0 = time.perf_counter()
        scored = [score_ioc(ioc) for ioc in iocs]
        elapsed = time.perf_counter() - t0
        assert elapsed < 15.0

    @pytest.mark.slow
    def test_score_10000(self):
        iocs = _generate_iocs(10000, dup_ratio=0)
        t0 = time.perf_counter()
        scored = [score_ioc(ioc) for ioc in iocs]
        elapsed = time.perf_counter() - t0
        assert elapsed < 90.0

    @pytest.mark.slow
    def test_filter_10000(self):
        scored = _generate_scored_iocs(10000)
        t0 = time.perf_counter()
        accepted, rejected = filter_false_positives(scored, min_score=20)
        elapsed = time.perf_counter() - t0
        assert elapsed < 5.0
        assert len(accepted) + rejected == 10000


# ---------------------------------------------------------------------------
# Output generation benchmarks
# ---------------------------------------------------------------------------


class TestOutputPerf:
    @pytest.mark.slow
    def test_json_10000(self):
        scored = _generate_scored_iocs(10000)
        t0 = time.perf_counter()
        out = generate_json(scored)
        elapsed = time.perf_counter() - t0
        assert elapsed < 5.0
        assert len(out) > 1000

    @pytest.mark.slow
    def test_csv_10000(self):
        scored = _generate_scored_iocs(10000)
        t0 = time.perf_counter()
        out = generate_csv(scored)
        elapsed = time.perf_counter() - t0
        assert elapsed < 5.0

    @pytest.mark.slow
    def test_nextdns_10000(self):
        scored = _generate_scored_iocs(10000)
        t0 = time.perf_counter()
        out = generate_nextdns(scored)
        elapsed = time.perf_counter() - t0
        assert elapsed < 5.0

    @pytest.mark.slow
    def test_sqlite_10000(self, temp_dir):
        scored = _generate_scored_iocs(10000)
        db_path = temp_dir / "perf.db"
        t0 = time.perf_counter()
        generate_sqlite(scored, db_path)
        elapsed = time.perf_counter() - t0
        assert elapsed < 10.0

    @pytest.mark.slow
    def test_adguard_10000(self):
        scored = _generate_scored_iocs(10000)
        t0 = time.perf_counter()
        out = generate_adguard(scored)
        elapsed = time.perf_counter() - t0
        assert elapsed < 5.0


# ---------------------------------------------------------------------------
# Full pipeline benchmark
# ---------------------------------------------------------------------------


class TestPipelinePerf:
    @pytest.mark.slow
    def test_full_pipeline_100(self):
        validated = _generate_validated_iocs(100)
        t0 = time.perf_counter()
        normalized = normalize_batch(validated)
        scored = [score_ioc(ioc) for ioc in normalized]
        from scripts.src.quality import filter_false_positives

        filtered, _ = filter_false_positives(scored, min_score=20)
        generate_json(filtered)
        elapsed = time.perf_counter() - t0
        assert elapsed < 10.0

    @pytest.mark.slow
    def test_full_pipeline_1000(self):
        validated = _generate_validated_iocs(1000)
        t0 = time.perf_counter()
        normalized = normalize_batch(validated)
        scored = [score_ioc(ioc) for ioc in normalized]
        from scripts.src.quality import filter_false_positives

        filtered, _ = filter_false_positives(scored, min_score=20)
        generate_json(filtered)
        elapsed = time.perf_counter() - t0
        assert elapsed < 60.0

    @pytest.mark.slow
    def test_full_pipeline_10000(self):
        validated = _generate_validated_iocs(10000)
        t0 = time.perf_counter()
        normalized = normalize_batch(validated)
        scored = [score_ioc(ioc) for ioc in normalized]
        from scripts.src.quality import filter_false_positives

        filtered, _ = filter_false_positives(scored, min_score=20)
        generate_json(filtered)
        elapsed = time.perf_counter() - t0
        assert elapsed < 300.0
