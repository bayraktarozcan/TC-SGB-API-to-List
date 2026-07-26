"""Tests for ALL 16 output format generators with snapshot/structural verification."""

from __future__ import annotations

import csv
import io
import json
import sqlite3

import pytest
import yaml

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
    generate_pihole,
    generate_rpz,
    generate_sqlite,
    generate_suricata,
    generate_technitium,
    generate_unbound,
    generate_yaml,
)


@pytest.fixture
def scored_iocs() -> list[ScoredIOC]:
    return [
        ScoredIOC(
            value="evil-phish.com", ioc_type=IOCType.DOMAIN,
            desc=DescriptionCategory.PHISHING, source=Source.USOM,
            criticality_level=3, connectiontype=ConnectionType.PHISHING,
            quality_score=93.0, false_positive_risk="low",
        ),
        ScoredIOC(
            value="malware-cnc.evil.net", ioc_type=IOCType.DOMAIN,
            desc=DescriptionCategory.MALWARE_CMD_CENTER, source=Source.SOME,
            criticality_level=1, connectiontype=ConnectionType.BOTNET_CNC,
            quality_score=95.0, false_positive_risk="low",
        ),
        ScoredIOC(
            value="85.214.132.117", ioc_type=IOCType.IP,
            desc=DescriptionCategory.CYBER_ATTACK, source=Source.RSA,
            criticality_level=2, connectiontype=ConnectionType.APT_CNC,
            quality_score=88.0, false_positive_risk="low",
        ),
        ScoredIOC(
            value="https://drop.evil.top/mal.exe", ioc_type=IOCType.URL,
            desc=DescriptionCategory.MALWARE_DIST_URL, source=Source.IHBAR,
            criticality_level=4, connectiontype=ConnectionType.MALWARE_DOWNLOAD,
            quality_score=82.0, false_positive_risk="low",
        ),
    ]


class TestNextDNS:
    def test_contains_domains(self, scored_iocs):
        out = generate_nextdns(scored_iocs)
        assert "evil-phish.com" in out
        assert "malware-cnc.evil.net" in out

    def test_no_ip_in_domain_list(self, scored_iocs):
        out = generate_nextdns(scored_iocs)
        lines = [line for line in out.split("\n") if line.strip()]
        for line in lines:
            assert line != "85.214.132.117"

    def test_ends_with_newline(self, scored_iocs):
        out = generate_nextdns(scored_iocs)
        assert out.endswith("\n")

    def test_empty_input(self):
        out = generate_nextdns([])
        assert out == ""


class TestAdGuard:
    def test_header(self, scored_iocs):
        out = generate_adguard(scored_iocs)
        assert "! Title:" in out

    def test_domain_rules(self, scored_iocs):
        out = generate_adguard(scored_iocs)
        assert "||evil-phish.com^" in out

    def test_domains_only(self, scored_iocs):
        out = generate_adguard(scored_iocs)
        lines = [line for line in out.split("\n") if line.startswith("||")]
        assert len(lines) == 2  # only 2 domains in fixture


class TestPiHole:
    def test_starts_with_comment(self, scored_iocs):
        out = generate_pihole(scored_iocs)
        assert out.startswith("# TC-SGB Threat Intelligence")

    def test_contains_domains_only(self, scored_iocs):
        out = generate_pihole(scored_iocs)
        assert "evil-phish.com" in out
        lines = [line for line in out.split("\n") if line.strip() and not line.startswith("#")]
        for line in lines:
            assert line.startswith("0.0.0.0 ")


class TestDnsmasq:
    def test_address_format(self, scored_iocs):
        out = generate_dnsmasq(scored_iocs)
        assert "address=/evil-phish.com/0.0.0.0" in out

    def test_one_entry_per_domain(self, scored_iocs):
        out = generate_dnsmasq(scored_iocs)
        lines = [line for line in out.split("\n") if line.startswith("address=")]
        assert len(lines) == 2  # 2 domains in fixture


class TestUnbound:
    def test_local_zone_format(self, scored_iocs):
        out = generate_unbound(scored_iocs)
        assert 'local-zone: "evil-phish.com" always_nxdomain' in out

    def test_header_comment(self, scored_iocs):
        out = generate_unbound(scored_iocs)
        assert "# TC-SGB Threat Intelligence" in out
        assert "server:" in out


class TestRPZ:
    def test_soa_header(self, scored_iocs):
        out = generate_rpz(scored_iocs)
        assert "$ORIGIN" in out
        assert "SOA" in out

    def test_cname_format(self, scored_iocs):
        out = generate_rpz(scored_iocs)
        assert "evil-phish.com CNAME ." in out

    def test_domains_only(self, scored_iocs):
        out = generate_rpz(scored_iocs)
        lines = [line for line in out.split("\n") if line.endswith(" CNAME .")]
        assert len(lines) == 2  # 2 domains


class TestTechnitium:
    def test_format(self, scored_iocs):
        out = generate_technitium(scored_iocs)
        assert "evil-phish.com. IN A 0.0.0.0" in out

    def test_header(self, scored_iocs):
        out = generate_technitium(scored_iocs)
        assert "Technitium DNS Server" in out


class TestMikroTik:
    def test_address_list_section(self, scored_iocs):
        out = generate_mikrotik(scored_iocs)
        assert "/ip firewall address-list" in out

    def test_no_dns_static(self, scored_iocs):
        out = generate_mikrotik(scored_iocs)
        assert "/ip dns static" not in out

    def test_ip_in_address_list(self, scored_iocs):
        out = generate_mikrotik(scored_iocs)
        assert "85.214.132.117" in out

    def test_all_types(self, scored_iocs):
        out = generate_mikrotik(scored_iocs)
        assert "evil-phish.com" in out
        assert "85.214.132.117" in out
        # URL should not be in output (only domain and IP)
        assert "drop.evil.top" not in out


class TestNftables:
    def test_table_header(self, scored_iocs):
        out = generate_nftables(scored_iocs)
        assert "TC-SGB Threat Intelligence" in out

    def test_set_definition(self, scored_iocs):
        out = generate_nftables(scored_iocs)
        assert "set threat_intel" in out


class TestIpset:
    def test_create_command(self, scored_iocs):
        out = generate_ipset(scored_iocs)
        assert "create threat_intel hash:ip" in out

    def test_add_ips(self, scored_iocs):
        out = generate_ipset(scored_iocs)
        assert "add threat_intel 85.214.132.117" in out

    def test_domains_excluded(self, scored_iocs):
        out = generate_ipset(scored_iocs)
        assert "evil-phish.com" not in out


class TestSuricata:
    def test_json_lines_output(self, scored_iocs):
        out = generate_suricata(scored_iocs)
        lines = [line for line in out.split("\n") if line.strip()]
        for line in lines:
            data = json.loads(line)
            assert "alert" in data
            assert "metadata" in data

    def test_ip_present(self, scored_iocs):
        out = generate_suricata(scored_iocs)
        assert "85.214.132.117" in out

    def test_event_type(self, scored_iocs):
        out = generate_suricata(scored_iocs)
        assert '"event_type": "alert"' in out


class TestCrowdSec:
    def test_ip_list(self, scored_iocs):
        out = generate_crowdsec(scored_iocs)
        assert "85.214.132.117" in out

    def test_no_domains(self, scored_iocs):
        out = generate_crowdsec(scored_iocs)
        assert "evil-phish.com" not in out


class TestCSV:
    def test_has_header(self, scored_iocs):
        out = generate_csv(scored_iocs)
        reader = csv.reader(io.StringIO(out))
        header = next(reader)
        assert "value" in header
        assert "type" in header
        assert "quality_score" in header

    def test_correct_row_count(self, scored_iocs):
        out = generate_csv(scored_iocs)
        reader = csv.reader(io.StringIO(out))
        rows = list(reader)
        assert len(rows) == 5  # header + 4 rows

    def test_parseable(self, scored_iocs):
        out = generate_csv(scored_iocs)
        reader = csv.DictReader(io.StringIO(out))
        for row in reader:
            assert row["value"]
            assert row["type"] in ("domain", "ip", "url", "ip6", "ip6net")


class TestJSON:
    def test_valid_json(self, scored_iocs):
        out = generate_json(scored_iocs)
        data = json.loads(out)
        assert isinstance(data, list)

    def test_correct_length(self, scored_iocs):
        out = generate_json(scored_iocs)
        data = json.loads(out)
        assert len(data) == 4

    def test_fields(self, scored_iocs):
        out = generate_json(scored_iocs)
        data = json.loads(out)
        item = data[0]
        assert "value" in item
        assert "type" in item
        assert "quality_score" in item
        assert "false_positive_risk" in item
        assert "flags" in item

    def test_pretty_printed(self, scored_iocs):
        out = generate_json(scored_iocs)
        assert "\n" in out  # indented


class TestYAML:
    def test_valid_yaml(self, scored_iocs):
        out = generate_yaml(scored_iocs)
        data = yaml.safe_load(out)
        assert isinstance(data, list)

    def test_correct_length(self, scored_iocs):
        out = generate_yaml(scored_iocs)
        data = yaml.safe_load(out)
        assert len(data) == 4

    def test_fields(self, scored_iocs):
        out = generate_yaml(scored_iocs)
        data = yaml.safe_load(out)
        item = data[0]
        assert "value" in item
        assert "type" in item
        assert "quality_score" in item


class TestSQLite:
    def test_returns_string_path(self, scored_iocs, temp_dir):
        db_path = temp_dir / "test.db"
        result = generate_sqlite(scored_iocs, db_path)
        assert isinstance(result, str)

    def test_creates_db_file(self, scored_iocs, temp_dir):
        db_path = temp_dir / "test.db"
        generate_sqlite(scored_iocs, db_path)
        assert db_path.exists()

    def test_correct_row_count(self, scored_iocs, temp_dir):
        db_path = temp_dir / "test.db"
        generate_sqlite(scored_iocs, db_path)
        conn = sqlite3.connect(str(db_path))
        count = conn.execute("SELECT COUNT(*) FROM ioCs").fetchone()[0]
        conn.close()
        assert count == 4

    def test_schema(self, scored_iocs, temp_dir):
        db_path = temp_dir / "test.db"
        generate_sqlite(scored_iocs, db_path)
        conn = sqlite3.connect(str(db_path))
        columns = [row[1] for row in conn.execute("PRAGMA table_info(ioCs)")]
        conn.close()
        assert "value" in columns
        assert "type" in columns
        assert "quality_score" in columns
        assert "flags" in columns

    def test_data_integrity(self, scored_iocs, temp_dir):
        db_path = temp_dir / "test.db"
        generate_sqlite(scored_iocs, db_path)
        conn = sqlite3.connect(str(db_path))
        row = conn.execute(
            "SELECT value, quality_score FROM ioCs WHERE value = ?",
            ("evil-phish.com",),
        ).fetchone()
        conn.close()
        assert row is not None
        assert row[1] == 93.0

    def test_empty_input(self, temp_dir):
        db_path = temp_dir / "empty.db"
        generate_sqlite([], db_path)
        conn = sqlite3.connect(str(db_path))
        count = conn.execute("SELECT COUNT(*) FROM ioCs").fetchone()[0]
        conn.close()
        assert count == 0


class TestEmptyInput:
    def test_all_formats_empty(self, temp_dir):
        iocs: list[ScoredIOC] = []
        assert generate_nextdns(iocs) == ""
        assert generate_pihole(iocs) != ""
        assert json.loads(generate_json(iocs)) == []
        assert yaml.safe_load(generate_yaml(iocs)) == []
