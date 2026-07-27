"""Shared fixtures: sample IOC data, mock API responses, temp directories."""

from __future__ import annotations

import tempfile
from collections.abc import Generator
from datetime import datetime
from pathlib import Path
from typing import Any

import pytest

from scripts.src.models import (
    AddressRecord,
    ConnectionType,
    DescriptionCategory,
    IOCType,
    NormalizedIOC,
    ScoredIOC,
    Source,
    ValidatedIOC,
)

# ---------------------------------------------------------------------------
# Sample address records (raw API data)
# ---------------------------------------------------------------------------


@pytest.fixture
def sample_address_records() -> list[AddressRecord]:
    return [
        AddressRecord(
            id=1,
            url="https://evil-phish.com/login",
            type="url",
            desc="PH",
            source="US",
            date="2024-01-15",
            criticality_level=3,
            connectiontype="PH",
        ),
        AddressRecord(
            id=2,
            url="malware-cnc.evil.net",
            type="domain",
            desc="MC",
            source="SO",
            date="2024-02-20",
            criticality_level=1,
            connectiontype="BC",
        ),
        AddressRecord(
            id=3,
            url="192.168.1.100",
            type="ip",
            desc="CA",
            source="US",
            date="2024-03-10",
            criticality_level=5,
            connectiontype="OT",
        ),
        AddressRecord(
            id=4,
            url="2001:db8::1",
            type="ip6",
            desc="MC",
            source="RS",
            date="2024-04-01",
            criticality_level=7,
            connectiontype="MC",
        ),
        AddressRecord(
            id=5,
            url="spam-domain.xyz",
            type="domain",
            desc="MD",
            source="IH",
            date="2024-05-15",
            criticality_level=4,
            connectiontype="MF",
        ),
        AddressRecord(
            id=6,
            url="",
            type="",
            desc="",
            source="",
            date="",
            criticality_level=10,
            connectiontype="",
        ),
        AddressRecord(
            id=7,
            url="localhost",
            type="domain",
            desc="",
            source="SB",
            date="2024-06-01",
            criticality_level=10,
            connectiontype="",
        ),
        AddressRecord(
            id=8,
            url="example.com",
            type="domain",
            desc="",
            source="SB",
            date="2024-06-01",
            criticality_level=10,
            connectiontype="",
        ),
        AddressRecord(
            id=9,
            url="  EVIL-TRIMMED.COM  ",
            type="domain",
            desc="PH",
            source="US",
            date="2024-07-01",
            criticality_level=2,
            connectiontype="PH",
        ),
        AddressRecord(
            id=10,
            url="http://bad.ruːn.com/path",
            type="url",
            desc="BP",
            source="SO",
            date="2024-08-01",
            criticality_level=6,
            connectiontype="EK",
        ),
    ]


@pytest.fixture
def malicious_only_records() -> list[AddressRecord]:
    """Records that should all pass validation."""
    return [
        AddressRecord(
            id=101,
            url="phishing-bank.ru",
            type="domain",
            desc="PH",
            source="US",
            date="2024-01-01",
            criticality_level=2,
            connectiontype="PH",
        ),
        AddressRecord(
            id=102,
            url="cnc-malware.xyz",
            type="domain",
            desc="MC",
            source="SO",
            date="2024-01-02",
            criticality_level=1,
            connectiontype="BC",
        ),
        AddressRecord(
            id=103,
            url="85.214.132.117",
            type="ip",
            desc="CA",
            source="RS",
            date="2024-01-03",
            criticality_level=3,
            connectiontype="AC",
        ),
        AddressRecord(
            id=104,
            url="https://drop.evil.top/mal.exe",
            type="url",
            desc="MU",
            source="IH",
            date="2024-01-04",
            criticality_level=4,
            connectiontype="MF",
        ),
    ]


# ---------------------------------------------------------------------------
# Validated IOC fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
def sample_validated_iocs() -> list[ValidatedIOC]:
    return [
        ValidatedIOC(
            raw_url="evil-phish.com",
            ioc_type=IOCType.DOMAIN,
            desc=DescriptionCategory.PHISHING,
            source=Source.USOM,
            date=datetime(2024, 1, 15),
            criticality_level=3,
            connectiontype=ConnectionType.PHISHING,
            original_id=1,
        ),
        ValidatedIOC(
            raw_url="192.168.1.100",
            ioc_type=IOCType.IP,
            desc=DescriptionCategory.CYBER_ATTACK,
            source=Source.USOM,
            date=datetime(2024, 3, 10),
            criticality_level=5,
            connectiontype=ConnectionType.OTHER,
            original_id=3,
        ),
        ValidatedIOC(
            raw_url="spam.xyz",
            ioc_type=IOCType.DOMAIN,
            desc=DescriptionCategory.MALWARE_DIST_DOMAIN,
            source=Source.IHBAR,
            date=datetime(2024, 5, 15),
            criticality_level=4,
            connectiontype=ConnectionType.MALWARE_DOWNLOAD,
            original_id=5,
        ),
    ]


# ---------------------------------------------------------------------------
# Normalized IOC fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
def sample_normalized_iocs() -> list[NormalizedIOC]:
    return [
        NormalizedIOC(
            value="evil-phish.com",
            ioc_type=IOCType.DOMAIN,
            desc=DescriptionCategory.PHISHING,
            source=Source.USOM,
            date=datetime(2024, 1, 15),
            criticality_level=3,
            connectiontype=ConnectionType.PHISHING,
            original_id=1,
        ),
        NormalizedIOC(
            value="192.168.1.100",
            ioc_type=IOCType.IP,
            desc=DescriptionCategory.CYBER_ATTACK,
            source=Source.USOM,
            date=datetime(2024, 3, 10),
            criticality_level=5,
            connectiontype=ConnectionType.OTHER,
            original_id=3,
        ),
        NormalizedIOC(
            value="malware-cnc.evil.net",
            ioc_type=IOCType.DOMAIN,
            desc=DescriptionCategory.MALWARE_CMD_CENTER,
            source=Source.SOME,
            date=datetime(2024, 2, 20),
            criticality_level=1,
            connectiontype=ConnectionType.BOTNET_CNC,
            original_id=2,
        ),
    ]


@pytest.fixture
def scoreable_iocs() -> list[NormalizedIOC]:
    """IOCs designed to exercise quality scoring: benign, private, normal, no-source."""
    return [
        NormalizedIOC(
            value="google.com",
            ioc_type=IOCType.DOMAIN,
            desc=DescriptionCategory.PHISHING,
            source=Source.USOM,
            date=datetime(2024, 1, 1),
            criticality_level=1,
            connectiontype=ConnectionType.PHISHING,
            original_id=200,
        ),
        NormalizedIOC(
            value="127.0.0.1",
            ioc_type=IOCType.IP,
            desc=DescriptionCategory.CYBER_ATTACK,
            source=Source.USOM,
            date=datetime(2024, 1, 1),
            criticality_level=1,
            connectiontype=ConnectionType.OTHER,
            original_id=201,
        ),
        NormalizedIOC(
            value="totally-malicious-domain.xyz",
            ioc_type=IOCType.DOMAIN,
            desc=DescriptionCategory.MALWARE_CMD_CENTER,
            source=Source.SOME,
            date=datetime(2024, 1, 1),
            criticality_level=2,
            connectiontype=ConnectionType.BOTNET_CNC,
            original_id=202,
        ),
        NormalizedIOC(
            value="no-source-bad.ru",
            ioc_type=IOCType.DOMAIN,
            desc=None,
            source=None,
            date=None,
            criticality_level=10,
            connectiontype=None,
            original_id=203,
        ),
    ]


# ---------------------------------------------------------------------------
# Scored IOC fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
def sample_scored_iocs() -> list[ScoredIOC]:
    return [
        ScoredIOC(
            value="evil-phish.com",
            ioc_type=IOCType.DOMAIN,
            desc=DescriptionCategory.PHISHING,
            source=Source.USOM,
            date=datetime(2024, 1, 15),
            criticality_level=3,
            connectiontype=ConnectionType.PHISHING,
            original_id=1,
            quality_score=93.0,
            false_positive_risk="low",
            flags=[],
        ),
        ScoredIOC(
            value="192.168.1.100",
            ioc_type=IOCType.IP,
            desc=DescriptionCategory.CYBER_ATTACK,
            source=Source.USOM,
            date=datetime(2024, 3, 10),
            criticality_level=5,
            connectiontype=ConnectionType.OTHER,
            original_id=3,
            quality_score=65.0,
            false_positive_risk="low",
            flags=["private_ip"],
        ),
        ScoredIOC(
            value="spam.xyz",
            ioc_type=IOCType.DOMAIN,
            desc=DescriptionCategory.MALWARE_DIST_DOMAIN,
            source=Source.IHBAR,
            date=datetime(2024, 5, 15),
            criticality_level=4,
            connectiontype=ConnectionType.MALWARE_DOWNLOAD,
            original_id=5,
            quality_score=82.0,
            false_positive_risk="low",
            flags=[],
        ),
        ScoredIOC(
            value="cnc.bad.ru",
            ioc_type=IOCType.DOMAIN,
            desc=DescriptionCategory.MALWARE_CMD_CENTER,
            source=Source.RSA,
            date=datetime(2024, 6, 1),
            criticality_level=1,
            connectiontype=ConnectionType.BOTNET_CNC,
            original_id=6,
            quality_score=95.0,
            false_positive_risk="low",
            flags=[],
        ),
    ]


# ---------------------------------------------------------------------------
# Mock API responses (matching real SGB API format)
# ---------------------------------------------------------------------------


@pytest.fixture
def mock_api_page1() -> dict[str, Any]:
    return {
        "models": [
            {
                "id": 1,
                "url": "evil.com",
                "type": "domain",
                "desc": "PH",
                "source": "US",
                "date": "2024-01-01",
                "criticality_level": 3,
                "connectiontype": "PH",
            },
            {
                "id": 2,
                "url": "bad.net",
                "type": "domain",
                "desc": "MC",
                "source": "SO",
                "date": "2024-01-02",
                "criticality_level": 1,
                "connectiontype": "BC",
            },
        ],
        "totalCount": 3,
        "count": 2,
        "page": 0,
        "pageCount": 2,
    }


@pytest.fixture
def mock_api_page2() -> dict[str, Any]:
    return {
        "models": [
            {
                "id": 3,
                "url": "85.214.132.117",
                "type": "ip",
                "desc": "CA",
                "source": "RS",
                "date": "2024-01-03",
                "criticality_level": 2,
                "connectiontype": "AC",
            },
        ],
        "totalCount": 3,
        "count": 1,
        "page": 1,
        "pageCount": 2,
    }


@pytest.fixture
def mock_api_empty() -> dict[str, Any]:
    return {"models": [], "totalCount": 0, "count": 0, "page": 0, "pageCount": 0}


# ---------------------------------------------------------------------------
# Temp directory
# ---------------------------------------------------------------------------


@pytest.fixture
def temp_dir() -> Generator[Path, None, None]:
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


@pytest.fixture
def output_dir(temp_dir: Path) -> Path:
    d = temp_dir / "output"
    d.mkdir()
    return d
