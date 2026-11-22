"""Tests for the output-compatibility gate and its structural validators."""

from __future__ import annotations

import json
from pathlib import Path

from Scripts.check_output_compatibility import (
    _run_tool,
    validate_crowdsec_json,
    validate_mikrotik,
    validate_suricata_rules,
)
from Scripts.src.models import IoCType, ScoredIoC
from Scripts.src.outputs import generate_crowdsec, generate_mikrotik, generate_suricata_rules


def _sample() -> list[ScoredIoC]:
    return [
        ScoredIoC(value="evil-phish.example", ioc_type=IoCType.DOMAIN),
        ScoredIoC(value="192.0.2.1", ioc_type=IoCType.IP),
    ]


class TestCrowdSecShape:
    def test_generated_shape_is_importable(self):
        assert validate_crowdsec_json(generate_crowdsec(_sample())) == []

    def test_nested_shape_is_rejected(self):
        nested = json.dumps({"decisions": [{"duration": "168h", "value": "192.0.2.1"}]})
        assert validate_crowdsec_json(nested) != []

    def test_invalid_json_is_rejected(self):
        assert validate_crowdsec_json("not json") != []


class TestSuricataRulesShape:
    def test_generated_rules_pass(self):
        assert validate_suricata_rules(generate_suricata_rules(_sample())) == []

    def test_rule_without_dataset_is_rejected(self):
        text = 'drop ip any any -> any any (msg:"bad"; sid:9900002; rev:1;)'
        assert validate_suricata_rules(text) != []

    def test_duplicate_sids_are_rejected(self):
        rule = "drop ip any any -> any any (dataset:isset,x, load x.lst; sid:1; rev:1;)"
        assert validate_suricata_rules(f"{rule}\n{rule}") != []


class TestMikrotikShape:
    def test_generated_commands_pass(self):
        assert validate_mikrotik(generate_mikrotik(_sample())) == []

    def test_unknown_command_is_rejected(self):
        assert validate_mikrotik("/ip firewall filter add chain=input") != []


class TestToolPresence:
    def test_missing_tool_skips_by_default(self, tmp_path: Path):
        line = _run_tool("fake", ["definitely-not-a-real-binary-xyz"], tmp_path, False)
        assert line.startswith("[SKIP]")

    def test_missing_tool_fails_when_required(self, tmp_path: Path):
        line = _run_tool("fake", ["definitely-not-a-real-binary-xyz"], tmp_path, True)
        assert line.startswith("[FAIL]")
