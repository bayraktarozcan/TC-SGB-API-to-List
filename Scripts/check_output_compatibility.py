"""Validate generated artifacts with the real target tools when available.

Each generator is exercised on a small deterministic IoC set. Tools found on
PATH are invoked for real (``nft -c``, ``unbound-checkconf``, ``dnsmasq --test``,
``suricata -T``); CrowdSec and MikroTik are checked against their documented
data shape because no importable CLI is available in CI. Use --require-tools
in CI so a missing binary fails instead of silently skipping a check.
"""

from __future__ import annotations

import argparse
import shutil
import subprocess  # nosec B404
import sys
import tempfile
from pathlib import Path

from Scripts.src.models import ConnectionType, DescriptionCategory, IoCType, ScoredIoC, Source
from Scripts.src.outputs import (
    generate_crowdsec,
    generate_dnsmasq,
    generate_mikrotik,
    generate_nftables,
    generate_suricata_rules,
    generate_unbound,
)

SURICATA_CONFIG = Path("/etc/suricata/suricata.yaml")


def _sample_iocs() -> list[ScoredIoC]:
    return [
        ScoredIoC(
            value="evil-phish.example",
            ioc_type=IoCType.DOMAIN,
            desc=DescriptionCategory.PHISHING,
            source=Source.USOM,
            criticality_level=3,
            connectiontype=ConnectionType.PHISHING,
            quality_score=93.0,
        ),
        ScoredIoC(
            value="192.0.2.1",
            ioc_type=IoCType.IP,
            desc=DescriptionCategory.CYBER_ATTACK,
            source=Source.RSA,
            criticality_level=2,
            connectiontype=ConnectionType.APT_CNC,
            quality_score=88.0,
        ),
        ScoredIoC(
            value="2001:db8::1",
            ioc_type=IoCType.IP6,
            desc=DescriptionCategory.CYBER_ATTACK,
            source=Source.RSA,
            criticality_level=2,
            connectiontype=ConnectionType.APT_CNC,
            quality_score=88.0,
        ),
    ]


def validate_crowdsec_json(text: str) -> list[str]:
    """Check the flat decision shape documented for cscli decisions import."""
    import json

    try:
        rows = json.loads(text)
    except (json.JSONDecodeError, TypeError) as exc:
        return [f"invalid JSON: {exc}"]
    if not isinstance(rows, list):
        return ["expected a JSON array of decisions"]
    required = {"duration", "reason", "scope", "type", "value"}
    violations: list[str] = []
    for index, row in enumerate(rows):
        if not isinstance(row, dict):
            violations.append(f"decision {index}: expected an object")
            continue
        missing = required - set(row)
        if missing:
            violations.append(f"decision {index}: missing {sorted(missing)}")
    return violations


def validate_suricata_rules(text: str) -> list[str]:
    """Check that loadable rules reference a dataset and carry unique sids."""
    import re

    rules = [line for line in text.splitlines() if line.startswith(("reject ", "drop "))]
    if not rules:
        return ["no Suricata rules emitted"]
    violations: list[str] = []
    sids: list[str] = []
    for rule in rules:
        sid_match = re.search(r"sid:(\d+);", rule)
        if sid_match is None:
            violations.append(f"rule without sid: {rule[:60]}")
        else:
            sids.append(sid_match.group(1))
        if "dataset:isset" not in rule or "load " not in rule:
            violations.append(f"rule without dataset load: {rule[:60]}")
    if len(sids) != len(set(sids)):
        violations.append("duplicate signature ids")
    return violations


def validate_mikrotik(text: str) -> list[str]:
    """Check the version-agnostic RouterOS address-list command shape."""
    commands = [line for line in text.splitlines() if line.startswith("/ip")]
    if not commands:
        return ["no RouterOS commands emitted"]
    return [
        f"unexpected command: {line[:60]}"
        for line in commands
        if "address-list" not in line and "dns static" not in line
    ]


def _run_tool(label: str, command: list[str], cwd: Path, require: bool) -> str:
    executable = command[0]
    if shutil.which(executable) is None:
        if require:
            return f"[FAIL] {label}: required tool {executable} not found on PATH"
        return f"[SKIP] {label}: {executable} not installed"
    try:
        result = subprocess.run(  # noqa: S603 # nosec B603
            command,
            cwd=cwd,
            capture_output=True,
            text=True,
            check=False,
        )
    except OSError as exc:
        return f"[FAIL] {label}: {exc}"
    if result.returncode != 0:
        return f"[FAIL] {label}: {(result.stderr or result.stdout).strip()[:400]}"
    return f"[OK] {label}"


def _structural(label: str, violations: list[str]) -> str:
    if violations:
        return f"[FAIL] {label}: " + "; ".join(violations[:5])
    return f"[OK] {label}"


def run_checks(require_tools: bool = False) -> list[str]:
    """Generate sample outputs and validate them; return one line per check."""
    iocs = _sample_iocs()
    suricata_config = SURICATA_CONFIG
    results: list[str] = []
    with tempfile.TemporaryDirectory() as temp:
        out = Path(temp)
        nft_path = out / "threat_intel_nftables.nft"
        unbound_path = out / "threat_intel_unbound.conf"
        dnsmasq_path = out / "threat_intel_dnsmasq.conf"
        rules_path = out / "threat_intel_suricata.rules"
        generate_nftables(iocs, path=nft_path)
        generate_unbound(iocs, path=unbound_path)
        generate_dnsmasq(iocs, path=dnsmasq_path)
        generate_suricata_rules(iocs, path=rules_path)

        results.append(
            _run_tool("nftables", ["nft", "-c", "-f", nft_path.name], out, require_tools)
        )
        results.append(
            _run_tool("unbound", ["unbound-checkconf", unbound_path.name], out, require_tools)
        )
        results.append(
            _run_tool("dnsmasq", ["dnsmasq", "--test", "-C", dnsmasq_path.name], out, require_tools)
        )
        if suricata_config.is_file():
            results.append(
                _run_tool(
                    "suricata",
                    [
                        "suricata",
                        "-T",
                        "-c",
                        str(suricata_config),
                        "-S",
                        rules_path.name,
                    ],
                    out,
                    require_tools,
                )
            )
        elif require_tools:
            results.append("[FAIL] suricata: no system suricata.yaml found")
        else:
            results.append("[SKIP] suricata: no system suricata.yaml found")

        results.append(_structural("crowdsec", validate_crowdsec_json(generate_crowdsec(iocs))))
        results.append(_structural("mikrotik", validate_mikrotik(generate_mikrotik(iocs))))
    return results


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="tc-sgb-compat",
        description="Validate generated outputs against the target tools.",
    )
    parser.add_argument(
        "--require-tools",
        action="store_true",
        help="Fail when a target tool is missing instead of skipping its check.",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    results = run_checks(require_tools=args.require_tools)
    for line in results:
        print(line)
    failed = [line for line in results if line.startswith("[FAIL]")]
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
