"""Tests for Pydantic models: valid/invalid data, serialization, deserialization."""

from __future__ import annotations

from datetime import datetime

import pytest
from pydantic import ValidationError

from scripts.src.models import (
    AddressRecord,
    AnnouncementRecord,
    ConnectionType,
    ConnectionTypeRecord,
    DescriptionCategory,
    DescriptionRecord,
    IncidentRecord,
    IOCType,
    NormalizedIOC,
    PaginatedResponse,
    PipelineStats,
    ScoredIOC,
    Source,
    SourceRecord,
    ValidatedIOC,
)


class TestIOCType:
    def test_all_values(self):
        assert set(IOCType) == {
            IOCType.DOMAIN,
            IOCType.URL,
            IOCType.IP,
            IOCType.IP6,
            IOCType.IP6NET,
        }

    def test_string_values(self):
        assert IOCType.DOMAIN.value == "domain"
        assert IOCType.IP6.value == "ip6"
        assert IOCType.IP6NET.value == "ip6net"

    def test_from_string(self):
        assert IOCType("url") == IOCType.URL


class TestDescriptionCategory:
    def test_all_codes(self):
        assert DescriptionCategory.PHISHING.value == "PH"
        assert DescriptionCategory.FINANCIAL_PHISHING.value == "BP"
        assert DescriptionCategory.CYBER_ATTACK.value == "CA"

    def test_from_code(self):
        assert DescriptionCategory("MD") == DescriptionCategory.MALWARE_DIST_DOMAIN


class TestSource:
    def test_all_sources(self):
        assert len(Source) == 5
        assert Source.USOM.value == "US"
        assert Source.SGB.value == "SB"


class TestConnectionType:
    def test_all_types(self):
        assert len(ConnectionType) == 8
        assert ConnectionType.APT_CNC.value == "AC"
        assert ConnectionType.PHISHING.value == "PH"


class TestAddressRecord:
    def test_valid_record(self):
        r = AddressRecord(id=1, url="evil.com", type="domain")
        assert r.id == 1
        assert r.url == "evil.com"
        assert r.criticality_level == 10

    def test_defaults(self):
        r = AddressRecord(id=1)
        assert r.url == ""
        assert r.type == ""
        assert r.desc == ""
        assert r.source == ""
        assert r.criticality_level == 10

    def test_from_dict(self):
        r = AddressRecord(**{"id": 5, "url": "test.com", "criticality_level": 3})
        assert r.criticality_level == 3

    def test_invalid_missing_id(self):
        with pytest.raises(ValidationError):
            AddressRecord(url="test.com")


class TestDescriptionRecord:
    def test_valid(self):
        r = DescriptionRecord(id="PH", tr_title="Phishing", en_title="Phishing")
        assert r.tr_title == "Phishing"

    def test_defaults(self):
        r = DescriptionRecord(id="PH")
        assert r.tr_title == ""
        assert r.en_title == ""


class TestConnectionTypeRecord:
    def test_valid(self):
        r = ConnectionTypeRecord(id="AC", tr_title="APT CNC", en_title="APT CNC")
        assert r.tr_title == "APT CNC"


class TestSourceRecord:
    def test_valid(self):
        r = SourceRecord(id="US", tr_title="USOM", en_title="USOM")
        assert r.tr_title == "USOM"


class TestIncidentRecord:
    def test_valid(self):
        r = IncidentRecord(id=1, title="Incident", desc="desc", date="2024-01-01")
        assert r.title == "Incident"
        assert r.desc == "desc"

    def test_defaults(self):
        r = IncidentRecord(id=1)
        assert r.title == ""
        assert r.desc == ""


class TestAnnouncementRecord:
    def test_valid(self):
        r = AnnouncementRecord(id=1, title="Title", desc="Desc", date="2024-01-01")
        assert r.desc == "Desc"


class TestPaginatedResponse:
    def test_basic(self):
        p = PaginatedResponse[AddressRecord](models=[], totalCount=0, page=0, pageCount=0)
        assert p.models == []
        assert p.totalCount == 0

    def test_aliases(self):
        p = PaginatedResponse[AddressRecord].model_validate(
            {"models": [{"id": 1, "url": "a.com"}], "totalCount": 1, "page": 0, "pageCount": 1}
        )
        assert len(p.models) == 1
        assert p.pageCount == 1

    def test_default_factory(self):
        p = PaginatedResponse[AddressRecord]()
        assert p.models == []
        assert p.page == 0


class TestValidatedIOC:
    def test_valid_minimal(self):
        v = ValidatedIOC(raw_url="evil.com", ioc_type=IOCType.DOMAIN)
        assert v.raw_url == "evil.com"
        assert v.ioc_type == IOCType.DOMAIN
        assert v.validation_errors == []

    def test_with_all_fields(self):
        v = ValidatedIOC(
            raw_url="evil.com",
            ioc_type=IOCType.DOMAIN,
            desc=DescriptionCategory.PHISHING,
            source=Source.USOM,
            date=datetime(2024, 1, 1),
            criticality_level=1,
            connectiontype=ConnectionType.PHISHING,
            original_id=1,
            validation_errors=["warn"],
        )
        assert v.desc == DescriptionCategory.PHISHING
        assert v.connectiontype == ConnectionType.PHISHING


class TestNormalizedIOC:
    def test_valid(self):
        n = NormalizedIOC(value="evil.com", ioc_type=IOCType.DOMAIN)
        assert n.value == "evil.com"
        assert n.normalization_notes == []

    def test_with_notes(self):
        n = NormalizedIOC(
            value="evil.com",
            ioc_type=IOCType.DOMAIN,
            normalization_notes=["lowercased", "trimmed"],
        )
        assert len(n.normalization_notes) == 2


class TestScoredIOC:
    def test_valid(self):
        s = ScoredIOC(
            value="evil.com", ioc_type=IOCType.DOMAIN, quality_score=85.0, false_positive_risk="low"
        )
        assert s.quality_score == 85.0
        assert s.false_positive_risk == "low"

    def test_defaults(self):
        s = ScoredIOC(value="x", ioc_type=IOCType.IP)
        assert s.quality_score == 0.0
        assert s.false_positive_risk == "low"
        assert s.flags == []


class TestPipelineStats:
    def test_defaults(self):
        ps = PipelineStats()
        assert ps.total_fetched == 0
        assert ps.by_type == {}
        assert ps.errors == []

    def test_summary(self):
        ps = PipelineStats(
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
        s = ps.summary()
        assert "Fetched:          100" in s
        assert "By type:" in s

    def test_summary_with_errors(self):
        ps = PipelineStats(errors=["err1", "err2", "err3"])
        s = ps.summary()
        assert "Errors:" in s

    def test_summary_many_errors_truncated(self):
        ps = PipelineStats(errors=[f"err{i}" for i in range(10)])
        s = ps.summary()
        # Should only show first 5
        assert "err4" in s
        assert "err5" not in s


class TestSerialization:
    def test_validated_ioc_roundtrip(self):
        v = ValidatedIOC(
            raw_url="evil.com",
            ioc_type=IOCType.DOMAIN,
            desc=DescriptionCategory.PHISHING,
            source=Source.USOM,
        )
        data = v.model_dump()
        v2 = ValidatedIOC.model_validate(data)
        assert v2.raw_url == v.raw_url
        assert v2.ioc_type == v.ioc_type

    def test_scored_ioc_json_roundtrip(self):
        s = ScoredIOC(
            value="evil.com",
            ioc_type=IOCType.DOMAIN,
            quality_score=95.0,
            flags=["benign_domain"],
        )
        j = s.model_dump_json()
        s2 = ScoredIOC.model_validate_json(j)
        assert s2.quality_score == 95.0
        assert s2.flags == ["benign_domain"]

    def test_address_record_from_json(self):
        data = {"id": 1, "url": "test.com", "criticality_level": 5}
        r = AddressRecord.model_validate(data)
        assert r.criticality_level == 5

    def test_pipeline_stats_roundtrip(self):
        ps = PipelineStats(total_fetched=50, errors=["x"])
        data = ps.model_dump()
        ps2 = PipelineStats.model_validate(data)
        assert ps2.total_fetched == 50
        assert ps2.errors == ["x"]
