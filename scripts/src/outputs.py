"""Output generators for all 16 supported threat-intel / DNS-filter formats.

Each generator accepts a list of ScoredIOC objects and writes (or returns) the
format-specific output.  They are pure functions — no I/O is performed except
for the SQLite database which needs a file path.
"""

from __future__ import annotations

import csv
import io
import json
import logging
import sqlite3
from collections.abc import Sequence
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import yaml

from .models import IOCType, ScoredIOC

logger = logging.getLogger(__name__)

# YAML setup — use safe dumper if available.
_yaml_dumper: type[yaml.SafeDumper] = yaml.SafeDumper


def _domains_only(iocs: Sequence[ScoredIOC]) -> list[ScoredIOC]:
    """Filter to domain-type IoCs only (used by most DNS filter formats)."""
    return [ioc for ioc in iocs if ioc.ioc_type == IOCType.DOMAIN]


def _domains_and_urls(iocs: Sequence[ScoredIOC]) -> list[ScoredIOC]:
    """Domains and URLs."""
    return [ioc for ioc in iocs if ioc.ioc_type in (IOCType.DOMAIN, IOCType.URL)]


# ---------------------------------------------------------------------------
# 1. NextDNS — plain domain list
# ---------------------------------------------------------------------------


def generate_nextdns(iocs: Sequence[ScoredIOC], path: str | Path | None = None) -> str:
    """Generate NextDNS-format plain domain list (one per line)."""
    lines = [ioc.value for ioc in _domains_only(iocs)]
    content = "\n".join(lines) + ("\n" if lines else "")
    if path:
        Path(path).write_text(content, encoding="utf-8")
    return content


# ---------------------------------------------------------------------------
# 2. AdGuard — AdBlock filter format
# ---------------------------------------------------------------------------


def generate_adguard(iocs: Sequence[ScoredIOC], path: str | Path | None = None) -> str:
    """Generate AdGuard blocklist: ||domain^"""
    lines = [f"||{ioc.value}^" for ioc in _domains_only(iocs)]
    ts = datetime.now(UTC).isoformat()
    header = (
        "! Title: TC-SGB Threat Intelligence Blocklist\n"
        f"! Last updated: {ts}\n"
        "! Homepage: https://siberguvenlik.gov.tr\n"
    )
    content = header + "\n".join(lines) + ("\n" if lines else "")
    if path:
        Path(path).write_text(content, encoding="utf-8")
    return content


# ---------------------------------------------------------------------------
# 3. Pi-hole — hosts format
# ---------------------------------------------------------------------------


def generate_pihole(iocs: Sequence[ScoredIOC], path: str | Path | None = None) -> str:
    """Generate Pi-hole hosts format: 0.0.0.0 domain"""
    lines = [f"0.0.0.0 {ioc.value}" for ioc in _domains_only(iocs)]
    header = "# TC-SGB Threat Intelligence — Pi-hole hosts format\n"
    content = header + "\n".join(lines) + ("\n" if lines else "")
    if path:
        Path(path).write_text(content, encoding="utf-8")
    return content


# ---------------------------------------------------------------------------
# 4. dnsmasq
# ---------------------------------------------------------------------------


def generate_dnsmasq(iocs: Sequence[ScoredIOC], path: str | Path | None = None) -> str:
    """Generate dnsmasq config: address=/domain/0.0.0.0"""
    lines = [f"address=/{ioc.value}/0.0.0.0" for ioc in _domains_only(iocs)]
    content = "\n".join(lines) + ("\n" if lines else "")
    if path:
        Path(path).write_text(content, encoding="utf-8")
    return content


# ---------------------------------------------------------------------------
# 5. Unbound
# ---------------------------------------------------------------------------


def generate_unbound(iocs: Sequence[ScoredIOC], path: str | Path | None = None) -> str:
    """Generate Unbound config: local-zone: \"domain\" always_nxdomain"""
    lines = [f'local-zone: "{ioc.value}" always_nxdomain' for ioc in _domains_only(iocs)]
    header = "# TC-SGB Threat Intelligence — Unbound config\nserver:\n"
    content = header + "\n".join(lines) + ("\n" if lines else "")
    if path:
        Path(path).write_text(content, encoding="utf-8")
    return content


# ---------------------------------------------------------------------------
# 6. RPZ — Response Policy Zone
# ---------------------------------------------------------------------------


def generate_rpz(iocs: Sequence[ScoredIOC], path: str | Path | None = None) -> str:
    """Generate RPZ zone file with SOA header."""
    now = datetime.now(UTC)
    serial = now.strftime("%Y%m%d01")
    soa = (
        "$ORIGIN threatintel.rpz.\n"
        "$TTL 300\n"
        "@ IN SOA localhost. admin.localhost. (\n"
        f"    {serial}  ; serial\n"
        "    3600       ; refresh\n"
        "    600        ; retry\n"
        "    86400      ; expire\n"
        "    300        ; minimum\n"
        ")\n"
        "@ IN NS localhost.\n\n"
    )
    lines = [f"{ioc.value} CNAME ." for ioc in _domains_only(iocs)]
    content = soa + "\n".join(lines) + ("\n" if lines else "")
    if path:
        Path(path).write_text(content, encoding="utf-8")
    return content


# ---------------------------------------------------------------------------
# 7. Technitium — zone file format
# ---------------------------------------------------------------------------


def generate_technitium(iocs: Sequence[ScoredIOC], path: str | Path | None = None) -> str:
    """Generate Technitium DNS Server zone file format."""
    now = datetime.now(UTC)
    serial = now.strftime("%Y%m%d01")
    header = (
        "; Technitium DNS Server — Threat Intelligence Zone\n"
        "; Generated by TC-SGB-Intel\n\n"
        "$ORIGIN threatint.local.\n"
        "$TTL 300\n\n"
        "@ IN SOA ns1.threatint.local. admin.threatint.local. (\n"
        f"    {serial}  ; serial\n"
        "    3600       ; refresh (1 hour)\n"
        "    600        ; retry (10 min)\n"
        "    86400      ; expire (1 day)\n"
        "    300        ; minimum (5 min)\n"
        ")\n\n"
        "; Name server\n"
        "@ IN NS ns1.threatint.local.\n"
        "ns1 IN A 127.0.0.1\n\n"
        "; Blocked domains\n"
    )
    lines = [f"{ioc.value}. IN A 0.0.0.0" for ioc in _domains_only(iocs)]
    content = header + "\n".join(lines) + ("\n" if lines else "")
    if path:
        Path(path).write_text(content, encoding="utf-8")
    return content


# ---------------------------------------------------------------------------
# 8. MikroTik — RouterOS address-list script
# ---------------------------------------------------------------------------


def generate_mikrotik(iocs: Sequence[ScoredIOC], path: str | Path | None = None) -> str:
    """Generate MikroTik RouterOS firewall address-list script."""
    lines = [
        "# TC-SGB Threat Intelligence — MikroTik address-list\n"
        "# Import with: /import file-name=threat_intel.rsc\n"
    ]
    for ioc in iocs:
        if ioc.ioc_type == IOCType.IP:
            lines.append(
                f"/ip firewall address-list add list=threat_intel"
                f' address={ioc.value} comment="SGB-Intel"'
            )
        elif ioc.ioc_type == IOCType.IP6:
            lines.append(
                f"/ipv6 firewall address-list add list=threat_intel"
                f' address={ioc.value} comment="SGB-Intel"'
            )
        elif ioc.ioc_type == IOCType.DOMAIN:
            lines.append(f'/ip dns static add name={ioc.value} address=0.0.0.0 comment="SGB-Intel"')
    content = "\n".join(lines) + "\n"
    if path:
        Path(path).write_text(content, encoding="utf-8")
    return content


# ---------------------------------------------------------------------------
# 9. nftables — nft set format
# ---------------------------------------------------------------------------


def generate_nftables(iocs: Sequence[ScoredIOC], path: str | Path | None = None) -> str:
    """Generate nftables set for blocking."""
    header = (
        "# TC-SGB Threat Intelligence — nftables set\n"
        "# Add this to your nftables.conf or import as a set\n\n"
        "table inet filter {\n"
    )
    ipv4_lines: list[str] = []
    ipv6_lines: list[str] = []
    domain_lines: list[str] = []
    for ioc in iocs:
        if ioc.ioc_type == IOCType.IP:
            ipv4_lines.append(f"            {ioc.value},")
        elif ioc.ioc_type == IOCType.IP6:
            ipv6_lines.append(f"            {ioc.value},")
        elif ioc.ioc_type == IOCType.DOMAIN:
            domain_lines.append(f"            {ioc.value},")

    content = header
    if ipv4_lines:
        content += (
            "    set threat_intel {\n"
            "        type ipv4_addr\n"
            "        flags interval\n"
            "        elements = {\n"
        )
        content += "\n".join(ipv4_lines) + "\n"
        content += "        }\n    }\n"

    if ipv6_lines:
        content += (
            "    set threat_intel6 {\n"
            "        type ipv6_addr\n"
            "        flags interval\n"
            "        elements = {\n"
        )
        content += "\n".join(ipv6_lines) + "\n"
        content += "        }\n    }\n"

    if domain_lines:
        content += (
            "    set threat_intel_domains {\n"
            "        type dns_name\n"
            "        flags interval\n"
            "        elements = {\n"
        )
        content += "\n".join(domain_lines) + "\n"
        content += "        }\n    }\n"

    content += "}\n"

    if path:
        Path(path).write_text(content, encoding="utf-8")
    return content


# ---------------------------------------------------------------------------
# 10. ipset
# ---------------------------------------------------------------------------


def generate_ipset(iocs: Sequence[ScoredIOC], path: str | Path | None = None) -> str:
    """Generate ipset list format."""
    lines = [
        "create threat_intel hash:ip family inet hashsize 4096 maxelem 500000",
        "create threat_intel6 hash:ip family inet6 hashsize 4096 maxelem 500000",
    ]
    for ioc in iocs:
        if ioc.ioc_type == IOCType.IP:
            lines.append(f"add threat_intel {ioc.value}")
        elif ioc.ioc_type == IOCType.IP6:
            lines.append(f"add threat_intel6 {ioc.value}")
    content = "\n".join(lines) + ("\n" if lines else "")
    if path:
        Path(path).write_text(content, encoding="utf-8")
    return content


# ---------------------------------------------------------------------------
# 11. Suricata — EVE JSON IoC format
# ---------------------------------------------------------------------------


def generate_suricata(iocs: Sequence[ScoredIOC], path: str | Path | None = None) -> str:
    """Generate Suricata EVE-format JSON lines for IoCs."""
    lines: list[str] = []
    for ioc in iocs:
        entry: dict[str, Any] = {
            "timestamp": (ioc.date or datetime.now(UTC)).strftime("%Y-%m-%dT%H:%M:%S+00:00"),
            "flow_id": ioc.original_id,
            "event_type": "alert",
            "src_ip": "0.0.0.0",  # nosec B104 — placeholder IP for Suricata EVE JSON output
            "src_port": 0,
            "dest_ip": ioc.value if ioc.ioc_type in (IOCType.IP, IOCType.IP6) else "0.0.0.0",  # nosec B104
            "dest_port": 0,
            "proto": "ip",
            "alert": {
                "action": "blocked",
                "gid": 1,
                "signature_id": 9000000 + ioc.original_id,
                "severity": ioc.criticality_level,
                "category": ioc.desc.value if ioc.desc else "unknown",
                "signature": (
                    f"TC-SGB Intel — {ioc.desc.value if ioc.desc else 'IoC'} — {ioc.value[:128]}"
                ),
            },
            "metadata": {
                "source": ioc.source.value if ioc.source else "unknown",
                "connection_type": ioc.connectiontype.value if ioc.connectiontype else "unknown",
                "ioc_type": ioc.ioc_type.value,
                "quality_score": ioc.quality_score,
            },
        }
        lines.append(json.dumps(entry))

    content = "\n".join(lines) + ("\n" if lines else "")
    if path:
        Path(path).write_text(content, encoding="utf-8")
    return content


# ---------------------------------------------------------------------------
# 12. CrowdSec — Decision list YAML
# ---------------------------------------------------------------------------


def generate_crowdsec(iocs: Sequence[ScoredIOC], path: str | Path | None = None) -> str:
    """Generate CrowdSec decision list YAML format."""
    decisions: list[dict[str, Any]] = []
    for ioc in iocs:
        if ioc.ioc_type not in (IOCType.IP, IOCType.IP6):
            continue
        decisions.append(
            {
                "decisions": [
                    {
                        "duration": "168h",  # 7 days
                        "type": "ban",
                        "value": ioc.value,
                        "scope": "IP",
                        "origin": "TC-SGB-Intel",
                        "scenario": (
                            f"Threat intelligence: {ioc.desc.value if ioc.desc else 'malicious'}"
                        ),
                    }
                ]
            }
        )
    content: str = yaml.dump(
        decisions,
        Dumper=_yaml_dumper,
        default_flow_style=False,
        allow_unicode=True,
    )
    if path:
        Path(path).write_text(content, encoding="utf-8")
    return content


# ---------------------------------------------------------------------------
# 13. CSV
# ---------------------------------------------------------------------------


def generate_csv(iocs: Sequence[ScoredIOC], path: str | Path | None = None) -> str:
    """Generate CSV with all IoC fields."""
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(
        [
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
    )
    for ioc in iocs:
        writer.writerow(
            [
                ioc.value,
                ioc.ioc_type.value,
                ioc.desc.value if ioc.desc else "",
                ioc.source.value if ioc.source else "",
                ioc.date.isoformat() if ioc.date else "",
                ioc.criticality_level,
                ioc.connectiontype.value if ioc.connectiontype else "",
                f"{ioc.quality_score:.4f}",
                ioc.false_positive_risk,
                "|".join(ioc.flags),
            ]
        )
    content = output.getvalue()
    if path:
        Path(path).write_text(content, encoding="utf-8")
    return content


# ---------------------------------------------------------------------------
# 14. JSON
# ---------------------------------------------------------------------------


def generate_json(iocs: Sequence[ScoredIOC], path: str | Path | None = None) -> str:
    """Generate pretty-printed JSON array."""
    data = [
        {
            "value": ioc.value,
            "type": ioc.ioc_type.value,
            "desc": ioc.desc.value if ioc.desc else None,
            "source": ioc.source.value if ioc.source else None,
            "date": ioc.date.isoformat() if ioc.date else None,
            "criticality_level": ioc.criticality_level,
            "connectiontype": ioc.connectiontype.value if ioc.connectiontype else None,
            "quality_score": ioc.quality_score,
            "false_positive_risk": ioc.false_positive_risk,
            "flags": ioc.flags,
        }
        for ioc in iocs
    ]
    content = json.dumps(data, indent=2, ensure_ascii=False)
    if path:
        Path(path).write_text(content, encoding="utf-8")
    return content


# ---------------------------------------------------------------------------
# 15. YAML
# ---------------------------------------------------------------------------


def generate_yaml(iocs: Sequence[ScoredIOC], path: str | Path | None = None) -> str:
    """Generate YAML sequence."""
    data = [
        {
            "value": ioc.value,
            "type": ioc.ioc_type.value,
            "desc": ioc.desc.value if ioc.desc else None,
            "source": ioc.source.value if ioc.source else None,
            "date": ioc.date.isoformat() if ioc.date else None,
            "criticality_level": ioc.criticality_level,
            "connectiontype": ioc.connectiontype.value if ioc.connectiontype else None,
            "quality_score": ioc.quality_score,
            "false_positive_risk": ioc.false_positive_risk,
            "flags": ioc.flags,
        }
        for ioc in iocs
    ]
    content: str = yaml.dump(
        data,
        Dumper=_yaml_dumper,
        default_flow_style=False,
        allow_unicode=True,
    )
    if path:
        Path(path).write_text(content, encoding="utf-8")
    return content


# ---------------------------------------------------------------------------
# 16. SQLite
# ---------------------------------------------------------------------------

SQLITE_SCHEMA = """
CREATE TABLE IF NOT EXISTS iocs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    value TEXT NOT NULL,
    type TEXT NOT NULL,
    desc TEXT,
    source TEXT,
    date TEXT,
    criticality_level INTEGER,
    connectiontype TEXT,
    quality_score REAL,
    false_positive_risk TEXT,
    flags TEXT,
    created_at TEXT DEFAULT (datetime('now')),
    UNIQUE(value, type)
);

CREATE INDEX IF NOT EXISTS idx_iocs_type ON iocs(type);
CREATE INDEX IF NOT EXISTS idx_iocs_source ON iocs(source);
CREATE INDEX IF NOT EXISTS idx_iocs_desc ON iocs(desc);
CREATE INDEX IF NOT EXISTS idx_iocs_quality ON iocs(quality_score);
CREATE INDEX IF NOT EXISTS idx_iocs_criticality ON iocs(criticality_level);

CREATE TABLE IF NOT EXISTS pipeline_runs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    run_date TEXT DEFAULT (datetime('now')),
    total_fetched INTEGER,
    after_validation INTEGER,
    after_normalization INTEGER,
    after_dedup INTEGER,
    after_quality INTEGER,
    duration_seconds REAL
);
"""


def generate_sqlite(iocs: Sequence[ScoredIOC], path: str | Path | None = None) -> str:
    """Generate a SQLite database with the IoCs.

    Returns the path to the created database as a string.
    """
    if path is None:
        path = Path("threat_intel.db")
    else:
        path = Path(path)

    conn = sqlite3.connect(str(path))
    try:
        conn.executescript(SQLITE_SCHEMA)

        rows = [
            (
                ioc.value,
                ioc.ioc_type.value,
                ioc.desc.value if ioc.desc else None,
                ioc.source.value if ioc.source else None,
                ioc.date.isoformat() if ioc.date else None,
                ioc.criticality_level,
                ioc.connectiontype.value if ioc.connectiontype else None,
                ioc.quality_score,
                ioc.false_positive_risk,
                "|".join(ioc.flags),
            )
            for ioc in iocs
        ]
        conn.executemany(
            """INSERT OR REPLACE INTO iocs
               (value, type, desc, source, date, criticality_level,
                connectiontype, quality_score, false_positive_risk, flags)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            rows,
        )
        conn.commit()
        logger.info("SQLite: wrote %d IoCs to %s", len(rows), path)
    finally:
        conn.close()

    return str(path)


# ---------------------------------------------------------------------------
# Registry
# ---------------------------------------------------------------------------

FORMAT_REGISTRY: dict[str, Any] = {
    "nextdns": generate_nextdns,
    "adguard": generate_adguard,
    "pihole": generate_pihole,
    "dnsmasq": generate_dnsmasq,
    "unbound": generate_unbound,
    "rpz": generate_rpz,
    "technitium": generate_technitium,
    "mikrotik": generate_mikrotik,
    "nftables": generate_nftables,
    "ipset": generate_ipset,
    "suricata": generate_suricata,
    "crowdsec": generate_crowdsec,
    "csv": generate_csv,
    "json": generate_json,
    "yaml": generate_yaml,
    "sqlite": generate_sqlite,
}


def generate_all(
    iocs: Sequence[ScoredIOC],
    output_dir: str | Path,
    *,
    formats: list[str] | None = None,
) -> dict[str, str]:
    """Generate all requested output formats.

    Parameters
    ----------
    iocs:
        Scored and deduplicated IoCs.
    output_dir:
        Directory to write output files into.
    formats:
        List of format names to generate.  None = all formats.

    Returns
    -------
    Dict mapping format name → file path (or inline content for SQLite).
    """
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    active_formats = formats or list(FORMAT_REGISTRY.keys())
    results: dict[str, str] = {}

    ext_map = {
        "nextdns": ".txt",
        "adguard": ".txt",
        "pihole": ".txt",
        "dnsmasq": ".conf",
        "unbound": ".conf",
        "rpz": ".zone",
        "technitium": ".zone",
        "mikrotik": ".rsc",
        "nftables": ".nft",
        "ipset": ".ipset",
        "suricata": ".json",
        "crowdsec": ".yaml",
        "csv": ".csv",
        "json": ".json",
        "yaml": ".yaml",
        "sqlite": ".db",
    }

    for fmt in active_formats:
        gen_func = FORMAT_REGISTRY.get(fmt)
        if gen_func is None:
            logger.warning("Unknown format: %s", fmt)
            continue
        ext = ext_map.get(fmt, ".out")
        filepath = output_dir / f"threat_intel_{fmt}{ext}"
        try:
            if fmt == "sqlite":
                result_path = gen_func(iocs, path=filepath)
                results[fmt] = result_path
            else:
                gen_func(iocs, path=filepath)
                results[fmt] = str(filepath)
            logger.info("Generated %s → %s", fmt, filepath)
        except Exception as exc:
            logger.error("Failed to generate %s: %s", fmt, exc)
            results[fmt] = f"ERROR: {exc}"

    return results
