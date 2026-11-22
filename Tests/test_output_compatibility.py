"""Tests for the output-compatibility gate and its structural validators."""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path
from unittest.mock import patch

from Scripts.check_output_compatibility import (
    _run_tool,
    _structural,
    build_parser,
    main,
    run_checks,
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


class TestStructuralValidators:
    def test_crowdsec_rejects_non_object_rows(self):
        assert validate_crowdsec_json("[[]]") != []

    def test_crowdsec_rejects_missing_keys(self):
        assert validate_crowdsec_json('[{"value": "192.0.2.1"}]') != []

    def test_suricata_rejects_empty_and_missing_sid(self):
        assert validate_suricata_rules("") != []
        text = "drop ip any any -> any any (dataset:isset,x, load x.lst;)"
        assert validate_suricata_rules(text) != []

    def test_mikrotik_rejects_empty(self):
        assert validate_mikrotik("") != []


class TestToolPresence:
    def test_missing_tool_skips_by_default(self, tmp_path: Path):
        line = _run_tool("fake", ["definitely-not-a-real-binary-xyz"], tmp_path, False)
        assert line.startswith("[SKIP]")

    def test_missing_tool_fails_when_required(self, tmp_path: Path):
        line = _run_tool("fake", ["definitely-not-a-real-binary-xyz"], tmp_path, True)
        assert line.startswith("[FAIL]")

    def test_successful_tool(self, tmp_path: Path):
        line = _run_tool("python", [sys.executable, "-c", "pass"], tmp_path, False)
        assert line == "[OK] python"

    def test_failing_tool(self, tmp_path: Path):
        line = _run_tool(
            "python", [sys.executable, "-c", "import sys; sys.exit(2)"], tmp_path, False
        )
        assert line.startswith("[FAIL]")

    def test_os_error_is_reported(self, tmp_path: Path):
        with (
            patch("Scripts.check_output_compatibility.shutil.which", return_value="python"),
            patch("Scripts.check_output_compatibility.subprocess.run", side_effect=OSError("boom")),
        ):
            line = _run_tool("python", ["python"], tmp_path, False)
        assert "boom" in line


class TestStructuralResult:
    def test_pass_and_fail_lines(self):
        assert _structural("x", []) == "[OK] x"
        assert _structural("x", ["bad"]).startswith("[FAIL]")


class TestRunChecks:
    def test_missing_tools_are_skipped(self):
        with patch("Scripts.check_output_compatibility.shutil.which", return_value=None):
            lines = run_checks()
        assert any(line.startswith("[SKIP]") for line in lines)
        assert any(line.startswith("[OK] crowdsec") for line in lines)

    def test_suricata_config_branch(self):
        with (
            patch("Scripts.check_output_compatibility.shutil.which", return_value=None),
            patch.object(Path, "is_file", return_value=True),
        ):
            lines = run_checks()
        assert any(line.startswith("[SKIP] suricata") for line in lines)

    def test_missing_suricata_config_fails_when_required(self):
        with (
            patch("Scripts.check_output_compatibility.shutil.which", return_value=None),
            patch.object(Path, "is_file", return_value=False),
        ):
            lines = run_checks(require_tools=True)
        assert any(line.startswith("[FAIL] suricata") for line in lines)

    def test_nft_command_override(self):
        with (
            patch.dict(os.environ, {"TC_SGB_NFT_COMMAND": "sudo -n nft"}),
            patch("Scripts.check_output_compatibility._run_tool", return_value="[OK] x") as run,
        ):
            run_checks()
        call = next(item for item in run.call_args_list if item.args[0] == "nftables")
        assert call.args[1][:3] == ["sudo", "-n", "nft"]

    def test_suricata_uses_writable_log_dir(self):
        with (
            patch.object(Path, "is_file", return_value=True),
            patch("Scripts.check_output_compatibility._run_tool", return_value="[OK] x") as run,
        ):
            run_checks()
        call = next(item for item in run.call_args_list if item.args[0] == "suricata")
        assert "-l" in call.args[1]


class TestCli:
    def test_parser_flag(self):
        assert build_parser().parse_args(["--require-tools"]).require_tools is True

    def test_main_clean(self):
        with patch("Scripts.check_output_compatibility.run_checks", return_value=["[OK] x"]):
            assert main([]) == 0

    def test_main_failure(self):
        with patch("Scripts.check_output_compatibility.run_checks", return_value=["[FAIL] x"]):
            assert main(["--require-tools"]) == 1
