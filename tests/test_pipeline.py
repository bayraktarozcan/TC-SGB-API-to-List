"""Tests for pipeline orchestration with mocked data."""

from __future__ import annotations

from unittest.mock import AsyncMock, patch

import pytest

from scripts.src.client import AsyncAPIClient
from scripts.src.models import (
    AddressRecord,
    IOCType,
    NormalizedIOC,
    PipelineStats,
    ScoredIOC,
    ValidatedIOC,
)
from scripts.src.pipeline import Pipeline, run_pipeline_sync


@pytest.fixture
def client() -> AsyncAPIClient:
    return AsyncAPIClient(base_url="http://test.com")


@pytest.fixture
def pipeline(client: AsyncAPIClient) -> Pipeline:
    return Pipeline(client=client)


@pytest.fixture
def records() -> list[AddressRecord]:
    return [
        AddressRecord(
            id=1,
            url="evil-phish.com",
            type="domain",
            desc="PH",
            source="US",
            date="2024-01-01",
            criticality_level=3,
            connectiontype="PH",
        ),
        AddressRecord(
            id=2,
            url="malware-cnc.net",
            type="domain",
            desc="MC",
            source="SO",
            date="2024-01-02",
            criticality_level=1,
            connectiontype="BC",
        ),
        AddressRecord(
            id=3,
            url="192.0.2.1",
            type="ip",
            desc="CA",
            source="RS",
            date="2024-01-03",
            criticality_level=2,
            connectiontype="AC",
        ),
        AddressRecord(
            id=4,
            url="spam.xyz",
            type="domain",
            desc="MD",
            source="IH",
            date="2024-01-04",
            criticality_level=5,
            connectiontype="MF",
        ),
        AddressRecord(
            id=5,
            url="",
            type="",
            desc="",
            source="",
            date="",
            criticality_level=10,
            connectiontype="",
        ),
    ]


class TestPipelineInit:
    def test_default_config(self):
        p = Pipeline()
        assert isinstance(p.client, AsyncAPIClient)
        assert p.client.base_url == "https://siberguvenlik.gov.tr"
        assert p.min_quality_score == 0.0
        assert p.max_criticality == 10
        assert p.per_page == 9999

    def test_custom_config(self):
        custom_client = AsyncAPIClient(base_url="http://custom.com")
        p = Pipeline(
            client=custom_client,
            per_page=500,
            max_pages=5,
            min_quality_score=30.0,
            max_criticality=5,
            skip_validation=True,
            skip_dedup=True,
        )
        assert p.client.base_url == "http://custom.com"
        assert p.per_page == 500
        assert p.max_pages == 5
        assert p.min_quality_score == 30.0
        assert p.max_criticality == 5
        assert p.skip_validation is True
        assert p.skip_dedup is True


class TestPipelineValidate:
    def test_valid_records_pass(self, pipeline, records):
        validated, rejected = pipeline._stage_validate(records)
        assert len(validated) >= 3
        assert rejected >= 1

    def test_empty_record_rejected(self, pipeline, records):
        _validated, rejected = pipeline._stage_validate(records)
        assert rejected >= 1

    def test_all_invalid(self, pipeline):
        bad = [AddressRecord(id=1, url="", type=""), AddressRecord(id=2, url="", type="")]
        validated, rejected = pipeline._stage_validate(bad)
        assert len(validated) == 0
        assert rejected == 2

    def test_returns_2_tuple(self, pipeline, records):
        result = pipeline._stage_validate(records)
        assert isinstance(result, tuple)
        assert len(result) == 2


class TestPipelineNormalize:
    def test_lowercase_domains(self, pipeline):
        validated = [
            ValidatedIOC(raw_url="EVIL.COM", ioc_type=IOCType.DOMAIN),
            ValidatedIOC(raw_url="GOOD.NET", ioc_type=IOCType.DOMAIN),
        ]
        normalized = pipeline._stage_normalize(validated)
        assert len(normalized) == 2
        assert normalized[0].value == "evil.com"
        assert normalized[1].value == "good.net"

    def test_empty_filtered(self, pipeline):
        validated = [
            ValidatedIOC(raw_url="", ioc_type=IOCType.DOMAIN),
            ValidatedIOC(raw_url="good.com", ioc_type=IOCType.DOMAIN),
        ]
        normalized = pipeline._stage_normalize(validated)
        assert len(normalized) == 1


class TestPipelineDedup:
    def test_removes_duplicates(self, pipeline):
        iocs = [
            ScoredIOC(
                value="a.com", ioc_type=IOCType.DOMAIN, criticality_level=5, quality_score=80.0
            ),
            ScoredIOC(
                value="b.com", ioc_type=IOCType.DOMAIN, criticality_level=3, quality_score=90.0
            ),
            ScoredIOC(
                value="a.com", ioc_type=IOCType.DOMAIN, criticality_level=1, quality_score=70.0
            ),
        ]
        deduped, dup_count = pipeline._stage_dedup(iocs)
        assert len(deduped) == 2
        assert dup_count == 1
        # The higher-scored a.com should be kept
        a_values = [d.quality_score for d in deduped if d.value == "a.com"]
        assert a_values == [80.0]

    def test_no_duplicates(self, pipeline):
        iocs = [
            ScoredIOC(
                value="a.com", ioc_type=IOCType.DOMAIN, criticality_level=5, quality_score=80.0
            ),
            ScoredIOC(
                value="b.com", ioc_type=IOCType.DOMAIN, criticality_level=3, quality_score=90.0
            ),
        ]
        deduped, dup_count = pipeline._stage_dedup(iocs)
        assert len(deduped) == 2
        assert dup_count == 0


class TestPipelineQuality:
    def test_scores_applied(self, pipeline):
        iocs = [
            NormalizedIOC(value="evil-phish.com", ioc_type=IOCType.DOMAIN, criticality_level=3),
            NormalizedIOC(value="malware-cnc.net", ioc_type=IOCType.DOMAIN, criticality_level=1),
        ]
        scored, _rejected = pipeline._stage_quality(iocs)
        assert len(scored) > 0
        for s in scored:
            assert 0 <= s.quality_score <= 100

    def test_filter_by_min_score(self, pipeline):
        pipeline.min_quality_score = 50.0
        iocs = [
            NormalizedIOC(
                value="known-benign.com",
                ioc_type=IOCType.DOMAIN,
                criticality_level=10,
            ),
            NormalizedIOC(
                value="totally-malicious.xyz",
                ioc_type=IOCType.DOMAIN,
                criticality_level=1,
            ),
        ]
        scored, _rejected = pipeline._stage_quality(iocs)
        values = [s.value for s in scored]
        # known-benign.com should be filtered out by quality scoring
        for s in scored:
            assert s.quality_score >= 50.0


class TestPipelineRun:
    @pytest.mark.asyncio
    async def test_run_empty_records(self, pipeline):
        with patch.object(pipeline, "_stage_fetch", new_callable=AsyncMock) as mock_fetch:
            mock_fetch.return_value = ([], 0.0)
            scored, stats = await pipeline.run()
            assert isinstance(stats, PipelineStats)
            assert stats.total_fetched == 0
            assert scored == []

    @pytest.mark.asyncio
    async def test_run_with_mocked_fetch(self, pipeline, records):
        with patch.object(pipeline, "_stage_fetch", new_callable=AsyncMock) as mock_fetch:
            mock_fetch.return_value = (records, 1.5)
            scored, stats = await pipeline.run()
            assert stats.fetch_duration_seconds == 1.5
            assert len(scored) > 0

    @pytest.mark.asyncio
    async def test_run_with_all_stages(self, pipeline):
        records = [
            AddressRecord(
                id=1,
                url="evil.com",
                type="domain",
                desc="PH",
                source="US",
                date="2024-01-01",
                criticality_level=3,
                connectiontype="PH",
            ),
            AddressRecord(
                id=2,
                url="bad.net",
                type="domain",
                desc="MC",
                source="SO",
                date="2024-01-02",
                criticality_level=1,
                connectiontype="BC",
            ),
        ]
        with patch.object(pipeline, "_stage_fetch", new_callable=AsyncMock) as mock_fetch:
            mock_fetch.return_value = (records, 0.5)
            _scored, stats = await pipeline.run()
            assert stats.after_validation >= 0
            assert stats.pipeline_duration_seconds >= 0

    @pytest.mark.asyncio
    async def test_run_returns_tuple(self, pipeline):
        with patch.object(pipeline, "_stage_fetch", new_callable=AsyncMock) as mock_fetch:
            mock_fetch.return_value = ([], 0.0)
            result = await pipeline.run()
            assert isinstance(result, tuple)
            assert len(result) == 2


class TestPipelineStats:
    def test_stats_summary(self):
        stats = PipelineStats(
            total_fetched=100,
            after_validation=80,
            validation_rejected=20,
            after_normalization=75,
            after_dedup=60,
            duplicates_removed=15,
            after_quality=50,
            quality_rejected=10,
            by_type={"domain": 40, "ip": 10},
            fetch_duration_seconds=5.3,
            pipeline_duration_seconds=12.1,
        )
        s = stats.summary()
        assert "Fetched:          100" in s
        assert "By type:" in s

    def test_stats_defaults(self):
        stats = PipelineStats()
        assert stats.total_fetched == 0
        assert stats.errors == []


class TestPipelineSync:
    def test_run_pipeline_sync_is_callable(self):
        assert callable(run_pipeline_sync)
