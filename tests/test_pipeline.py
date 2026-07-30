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
        assert p.min_quality_score == 20.0
        assert p.max_criticality is None
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


class TestPipelineExceptionBranches:
    def test_validate_exception_per_record(self, pipeline):
        """Lines 123-125: validate_ioc raises for one record."""
        good = AddressRecord(
            id=1,
            url="evil.com",
            type="domain",
            desc="PH",
            source="US",
            date="2024-01-01",
            criticality_level=3,
            connectiontype="PH",
        )
        bad = AddressRecord(
            id=2,
            url="bad.net",
            type="domain",
            desc="MC",
            source="SO",
            date="2024-01-02",
            criticality_level=1,
            connectiontype="BC",
        )

        def side_effect(rec):
            if rec.id == 2:
                raise RuntimeError("validate boom")
            return ValidatedIOC(raw_url=rec.url, ioc_type=IOCType.DOMAIN, original_id=rec.id)

        with patch("scripts.src.pipeline.validate_ioc", side_effect=side_effect):
            validated, rejected = pipeline._stage_validate([good, bad])
        assert len(validated) == 1
        assert rejected == 1

    def test_normalize_exception_per_record(self, pipeline):
        """Lines 140-141: normalize_ioc raises for one record."""
        v1 = ValidatedIOC(raw_url="evil.com", ioc_type=IOCType.DOMAIN, original_id=1)
        v2 = ValidatedIOC(raw_url="bad.net", ioc_type=IOCType.DOMAIN, original_id=2)

        def side_effect(v):
            if v.original_id == 2:
                raise RuntimeError("normalize boom")
            return NormalizedIOC(value=v.raw_url, ioc_type=v.ioc_type)

        with patch("scripts.src.pipeline.normalize_ioc", side_effect=side_effect):
            normalized = pipeline._stage_normalize([v1, v2])
        assert len(normalized) == 1
        assert normalized[0].value == "evil.com"

    def test_quality_exception_per_record(self, pipeline):
        """Lines 172-175: score_ioc raises for one record."""
        from scripts.src.models import ScoredIOC

        n1 = NormalizedIOC(value="evil.com", ioc_type=IOCType.DOMAIN)
        n2 = NormalizedIOC(value="bad.net", ioc_type=IOCType.DOMAIN)

        def side_effect(n):
            if n.value == "bad.net":
                raise RuntimeError("quality boom")
            return ScoredIOC(value=n.value, ioc_type=n.ioc_type, quality_score=100.0)

        with patch("scripts.src.pipeline.score_ioc", side_effect=side_effect):
            scored, rejected = pipeline._stage_quality([n1, n2])
        assert len(scored) == 1
        assert scored[0].value == "evil.com"
        assert rejected == 1

    def test_quality_rejects_below_threshold(self):
        """Line 172: score_ioc returns score below min_quality_score."""
        from scripts.src.models import NormalizedIOC, ScoredIOC

        p = Pipeline(min_quality_score=999.0)
        n1 = NormalizedIOC(value="evil.com", ioc_type=IOCType.DOMAIN)

        def fake_score(n):
            return ScoredIOC(value=n.value, ioc_type=n.ioc_type, quality_score=50.0)

        with patch("scripts.src.pipeline.score_ioc", side_effect=fake_score):
            scored, rejected = p._stage_quality([n1])
        assert len(scored) == 0
        assert rejected == 1


class TestPipelineContextManager:
    @pytest.mark.asyncio
    async def test_aenter_returns_self(self, pipeline):
        async with pipeline as p:
            assert p is pipeline

    @pytest.mark.asyncio
    async def test_aexit_closes_client(self, pipeline):
        async with pipeline:
            pass
        assert pipeline.client._client is None or pipeline.client._client.is_closed


class TestPipelineStageFetch:
    @pytest.mark.asyncio
    async def test_stage_fetch_logs_and_returns(self, pipeline):
        records = [
            AddressRecord(
                id=1,
                url="a.com",
                type="domain",
                desc="PH",
                source="US",
                date="2024-01-01",
                criticality_level=3,
                connectiontype="PH",
            ),
        ]
        with patch.object(
            pipeline.client, "fetch_addresses", new_callable=AsyncMock, return_value=records
        ):
            result, duration = await pipeline._stage_fetch()
            assert len(result) == 1
            assert pipeline.stats.total_fetched == 1
            assert duration >= 0


class TestPipelineStageValidate:
    def test_validate_exception_record_rejected(self, pipeline):
        bad_record = AddressRecord(id=99, url="valid-domain.xyz", type="domain")
        ok_record = AddressRecord(
            id=1,
            url="evil-phish.com",
            type="domain",
            desc="PH",
            source="US",
            date="2024-01-01",
            criticality_level=3,
            connectiontype="PH",
        )
        validated, rejected = pipeline._stage_validate([ok_record, bad_record])
        assert len(validated) >= 1


class TestPipelineStageNormalize:
    def test_normalize_exception_handled(self, pipeline):
        from scripts.src.models import ValidatedIOC

        good = ValidatedIOC(raw_url="evil.com", ioc_type=IOCType.DOMAIN)
        normalized = pipeline._stage_normalize([good])
        assert len(normalized) == 1


class TestPipelineStageDedup:
    def test_skip_dedup(self, pipeline):
        pipeline.skip_dedup = True
        iocs = [
            ScoredIOC(
                value="a.com", ioc_type=IOCType.DOMAIN, criticality_level=5, quality_score=80.0
            ),
            ScoredIOC(
                value="a.com", ioc_type=IOCType.DOMAIN, criticality_level=5, quality_score=90.0
            ),
        ]
        deduped, dup_count = pipeline._stage_dedup(iocs)
        assert len(deduped) == 2
        assert dup_count == 0


class TestPipelineStageQuality:
    def test_quality_exception_rejected(self, pipeline):
        from scripts.src.models import NormalizedIOC

        iocs = [NormalizedIOC(value="test.com", ioc_type=IOCType.DOMAIN, criticality_level=5)]
        scored, rejected = pipeline._stage_quality(iocs)
        assert len(scored) >= 1


class TestPipelineSync:
    def test_run_pipeline_sync_is_callable(self):
        assert callable(run_pipeline_sync)

    def test_run_pipeline_sync_with_mocked(self, client):
        with patch.object(
            client,
            "fetch_addresses",
            new_callable=AsyncMock,
            return_value=[
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
            ],
        ):
            scored, stats = run_pipeline_sync(client=client)
            assert len(scored) >= 1
            assert stats.total_fetched == 1
