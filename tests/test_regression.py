"""Regression tests ensuring output stability across runs."""

from __future__ import annotations

import json
import sqlite3

import pytest

from scripts.src.models import (
    ConnectionType,
    DescriptionCategory,
    IOCType,
    ScoredIOC,
    Source,
)
from scripts.src.outputs import (
    generate_adguard,
    generate_crowdsec,
    generate_csv,
    generate_dnsmasq,
    generate_ipset,
    generate_json,
    generate_mikrotik,
    generate_nextdns,
    generate_nftables,
    generate_rpz,
    generate_sqlite,
    generate_suricata,
    generate_technitium,
    generate_unbound,
    generate_yaml,
)


@pytest.fixture
def stable_iocs() -> list[ScoredIOC]:
    """Fixed IoC set for deterministic regression tests."""
    return [
        ScoredIOC(
            value="evil-phish.com",
            ioc_type=IOCType.DOMAIN,
            desc=DescriptionCategory.PHISHING,
            source=Source.USOM,
            criticality_level=3,
            connectiontype=ConnectionType.PHISHING,
            quality_score=93.0,
            false_positive_risk="low",
            flags=[],
        ),
        ScoredIOC(
            value="192.0.2.1",
            ioc_type=IOCType.IP,
            desc=DescriptionCategory.CYBER_ATTACK,
            source=Source.RSA,
            criticality_level=2,
            connectiontype=ConnectionType.APT_CNC,
            quality_score=88.0,
            false_positive_risk="low",
            flags=["private_ip"],
        ),
        ScoredIOC(
            value="spam.xyz",
            ioc_type=IOCType.DOMAIN,
            desc=DescriptionCategory.MALWARE_DIST_DOMAIN,
            source=Source.IHBAR,
            criticality_level=5,
            connectiontype=ConnectionType.MALWARE_DOWNLOAD,
            quality_score=82.0,
            false_positive_risk="low",
            flags=[],
        ),
    ]


class TestNextDNSRegression:
    def test_stable_output(self, stable_iocs):
        out1 = generate_nextdns(stable_iocs)
        out2 = generate_nextdns(stable_iocs)
        assert out1 == out2

    def test_domain_count(self, stable_iocs):
        out = generate_nextdns(stable_iocs)
        lines = [line for line in out.split("\n") if line.strip()]
        assert len(lines) == 2  # 2 domains


class TestAdGuardRegression:
    def test_stable_output(self, stable_iocs):
        out1 = generate_adguard(stable_iocs)
        out2 = generate_adguard(stable_iocs)
        lines1 = [line for line in out1.split("\n") if not line.startswith("! Last updated")]
        lines2 = [line for line in out2.split("\n") if not line.startswith("! Last updated")]
        assert lines1 == lines2

    def test_domain_count(self, stable_iocs):
        out = generate_adguard(stable_iocs)
        domain_lines = [line for line in out.split("\n") if line.startswith("||")]
        assert len(domain_lines) == 2


class TestJSONRegression:
    def test_stable_output(self, stable_iocs):
        out1 = generate_json(stable_iocs)
        out2 = generate_json(stable_iocs)
        assert out1 == out2

    def test_parseable_stable(self, stable_iocs):
        data = json.loads(generate_json(stable_iocs))
        assert len(data) == 3
        assert data[0]["value"] == "evil-phish.com"
        assert data[0]["quality_score"] == 93.0

    def test_field_names(self, stable_iocs):
        out = generate_json(stable_iocs)
        data = json.loads(out)
        assert list(data[0].keys()) == [
            "value",
            "type",
            "desc",
            "source",
            "date",
            "criticality_level",
            "connectiontype",
            "quality_score",
            "false_positive_risk",
            "flags",
        ]


class TestCSVRegression:
    def test_stable_output(self, stable_iocs):
        out1 = generate_csv(stable_iocs)
        out2 = generate_csv(stable_iocs)
        assert out1 == out2

    def test_row_values(self, stable_iocs):
        import csv
        import io

        reader = csv.DictReader(io.StringIO(generate_csv(stable_iocs)))
        rows = list(reader)
        assert rows[0]["value"] == "evil-phish.com"
        assert rows[0]["quality_score"] == "93.0000"


class TestYAMLRegression:
    def test_stable_output(self, stable_iocs):
        out1 = generate_yaml(stable_iocs)
        out2 = generate_yaml(stable_iocs)
        assert out1 == out2


class TestDnsmasqRegression:
    def test_stable_output(self, stable_iocs):
        out1 = generate_dnsmasq(stable_iocs)
        out2 = generate_dnsmasq(stable_iocs)
        assert out1 == out2

    def test_format_stable(self, stable_iocs):
        out = generate_dnsmasq(stable_iocs)
        assert "address=/evil-phish.com/0.0.0.0" in out
        assert "address=/spam.xyz/0.0.0.0" in out


class TestUnboundRegression:
    def test_stable_output(self, stable_iocs):
        out1 = generate_unbound(stable_iocs)
        out2 = generate_unbound(stable_iocs)
        assert out1 == out2

    def test_entries_count(self, stable_iocs):
        out = generate_unbound(stable_iocs)
        zone_lines = [line for line in out.split("\n") if "local-zone:" in line]
        assert len(zone_lines) == 2


class TestRPZRegression:
    def test_stable_output(self, stable_iocs):
        out1 = generate_rpz(stable_iocs)
        out2 = generate_rpz(stable_iocs)
        assert out1 == out2

    def test_has_soa(self, stable_iocs):
        out = generate_rpz(stable_iocs)
        assert "SOA" in out


class TestTechnitiumRegression:
    def test_stable_output(self, stable_iocs):
        out1 = generate_technitium(stable_iocs)
        out2 = generate_technitium(stable_iocs)
        assert out1 == out2


class TestMikroTikRegression:
    def test_stable_output(self, stable_iocs):
        out1 = generate_mikrotik(stable_iocs)
        out2 = generate_mikrotik(stable_iocs)
        assert out1 == out2


class TestNftablesRegression:
    def test_stable_output(self, stable_iocs):
        out1 = generate_nftables(stable_iocs)
        out2 = generate_nftables(stable_iocs)
        assert out1 == out2


class TestIpsetRegression:
    def test_stable_output(self, stable_iocs):
        out1 = generate_ipset(stable_iocs)
        out2 = generate_ipset(stable_iocs)
        assert out1 == out2


class TestSuricataRegression:
    def test_stable_output(self, stable_iocs):
        out1 = generate_suricata(stable_iocs)
        out2 = generate_suricata(stable_iocs)
        assert out1 == out2

    def test_json_lines_count(self, stable_iocs):
        out = generate_suricata(stable_iocs)
        lines = [line for line in out.split("\n") if line.strip()]
        assert len(lines) == 3  # 3 IoCs


class TestCrowdSecRegression:
    def test_stable_output(self, stable_iocs):
        out1 = generate_crowdsec(stable_iocs)
        out2 = generate_crowdsec(stable_iocs)
        assert out1 == out2


class TestSQLiteRegression:
    def test_stable_data(self, stable_iocs, temp_dir):
        db1 = temp_dir / "r1.db"
        db2 = temp_dir / "r2.db"
        generate_sqlite(stable_iocs, db1)
        generate_sqlite(stable_iocs, db2)

        conn1 = sqlite3.connect(str(db1))
        conn2 = sqlite3.connect(str(db2))
        rows1 = conn1.execute("SELECT value, quality_score FROM iocs ORDER BY id").fetchall()
        rows2 = conn2.execute("SELECT value, quality_score FROM iocs ORDER BY id").fetchall()
        conn1.close()
        conn2.close()
        assert rows1 == rows2


class TestIdempotency:
    """Running the same output generator multiple times should produce identical results."""

    def test_nextdns_idempotent(self, stable_iocs):
        results = [generate_nextdns(stable_iocs) for _ in range(5)]
        assert len(set(results)) == 1

    def test_json_idempotent(self, stable_iocs):
        results = [generate_json(stable_iocs) for _ in range(5)]
        assert len(set(results)) == 1

    def test_csv_idempotent(self, stable_iocs):
        results = [generate_csv(stable_iocs) for _ in range(5)]
        assert len(set(results)) == 1
