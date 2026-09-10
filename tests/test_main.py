"""Tests for the CLI entry point in ``scripts/main.py``."""

from __future__ import annotations

import json
import sys
from argparse import Namespace
from pathlib import Path
from unittest.mock import AsyncMock, patch

import pytest

from scripts.main import (
    _coerce_address_record,
    _parse_formats,
    build_parser,
    cmd_fetch,
    cmd_generate,
    cmd_health,
    cmd_stats,
    cmd_validate,
    main,
)
from scripts.src.models import (
    AddressRecord,
    ConnectionTypeRecord,
    DescriptionRecord,
    PipelineStats,
    SourceRecord,
)

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _make_args(**overrides) -> Namespace:
    """Build a Namespace with the defaults the parser would supply."""
    defaults = {
        "output": "output",
        "per_page": 9999,
        "rps": 5.0,
        "timeout": 60.0,
        "retries": 5,
        "max_records": None,
        "formats": None,
        "input": None,
    }
    defaults.update(overrides)
    return Namespace(**defaults)


def _write_raw_json(path: Path, items: list[dict]) -> None:
    path.write_text(json.dumps(items, indent=2, ensure_ascii=False), encoding="utf-8")


# ---------------------------------------------------------------------------
# _parse_formats / _coerce_address_record
# ---------------------------------------------------------------------------


class TestParseFormats:
    def test_none_returns_none(self):
        assert _parse_formats(None) is None

    def test_empty_string_returns_none(self):
        assert _parse_formats("") is None
        assert _parse_formats("   ") is None

    def test_splits_and_strips(self):
        assert _parse_formats("adguard, rpz ,technitium") == ["adguard", "rpz", "technitium"]

    def test_all_empty_parts_returns_none(self):
        assert _parse_formats(" , , ") is None


class TestCoerceAddressRecord:
    def test_url_shape(self):
        record = _coerce_address_record({"id": 7, "url": "evil.com", "type": "domain"})
        assert record is not None
        assert record.url == "evil.com"
        assert record.id == 7

    def test_value_shape(self):
        record = _coerce_address_record(
            {
                "id": 7,
                "value": "evil.com",
                "type": "domain",
                "desc": "PH",
                "source": "US",
                "date": "2024-01-01",
                "criticality_level": 2,
                "connectiontype": "PH",
            }
        )
        assert record is not None
        assert record.url == "evil.com"
        assert record.criticality_level == 2

    def test_url_shape_wins_over_value(self):
        record = _coerce_address_record({"id": 1, "url": "a.com", "value": "b.com"})
        assert record is not None
        assert record.url == "a.com"

    def test_malformed_url_shape_returns_none(self):
        assert _coerce_address_record({"url": "a.com", "value": "b.com"}) is None

    def test_missing_both_returns_none(self):
        assert _coerce_address_record({"id": 1}) is None


# ---------------------------------------------------------------------------
# build_parser
# ---------------------------------------------------------------------------


class TestBuildParser:
    def test_fetch_defaults(self):
        parser = build_parser()
        args = parser.parse_args(["fetch"])
        assert args.command == "fetch"
        assert args.output == "output"
        assert args.per_page == 9999
        assert args.rps == 5.0
        assert args.timeout == 60.0
        assert args.retries == 5
        assert args.max_records is None
        assert args.formats is None

    def test_generate_requires_input(self):
        parser = build_parser()
        with pytest.raises(SystemExit):
            parser.parse_args(["generate"])

    def test_validate_input_defaults_to_none(self):
        parser = build_parser()
        args = parser.parse_args(["validate"])
        assert args.input is None

    def test_unknown_command_fails(self):
        parser = build_parser()
        with pytest.raises(SystemExit):
            parser.parse_args(["nope"])


# ---------------------------------------------------------------------------
# cmd_fetch
# ---------------------------------------------------------------------------


class TestCmdFetch:
    async def test_fetch_writes_raw_and_outputs(self, temp_dir: Path, sample_scored_iocs):
        out = temp_dir / "out"
        pipeline = AsyncMock()
        pipeline.run = AsyncMock(return_value=(sample_scored_iocs, PipelineStats(total_fetched=4)))
        client = AsyncMock()

        with (
            patch("scripts.main.AsyncAPIClient", return_value=client),
            patch("scripts.main.Pipeline", return_value=pipeline),
        ):
            await cmd_fetch(_make_args(output=str(out), formats="pihole,csv"))

        assert (out / "raw_records.json").exists()
        assert (out / "threat_intel_pihole.txt").exists()
        client.close.assert_awaited_once()
        pipeline.run.assert_awaited_once()

    async def test_fetch_writes_changelog(self, temp_dir: Path, sample_scored_iocs):
        out = temp_dir / "out"
        pipeline = AsyncMock()
        pipeline.run = AsyncMock(return_value=(sample_scored_iocs, PipelineStats()))
        client = AsyncMock()

        with (
            patch("scripts.main.AsyncAPIClient", return_value=client),
            patch("scripts.main.Pipeline", return_value=pipeline),
        ):
            await cmd_fetch(_make_args(output=str(out)))

        assert (out / "raw_records.json").exists()
        assert list((out / "logs").glob("fetch_*.md"))


# ---------------------------------------------------------------------------
# cmd_generate
# ---------------------------------------------------------------------------


class TestCmdGenerate:
    def _scored_item(self, value: str, ioc_type: str = "domain", **extra) -> dict:
        item = {
            "id": 1,
            "value": value,
            "type": ioc_type,
            "desc": "PH",
            "source": "US",
            "date": "2024-01-01",
            "criticality_level": 3,
            "connectiontype": "PH",
            "quality_score": 90.0,
            "false_positive_risk": "low",
        }
        item.update(extra)
        return item

    async def test_generate_from_raw_file(self, temp_dir: Path):
        src = temp_dir / "raw_records.json"
        out = temp_dir / "out"
        _write_raw_json(src, [self._scored_item("evil-phish.com")])

        await cmd_generate(_make_args(input=str(src), output=str(out), formats="pihole,csv"))

        assert (out / "threat_intel_pihole.txt").exists()
        assert (out / "threat_intel_csv.csv").exists()

    async def test_generate_missing_input(self, temp_dir: Path, capsys):
        with pytest.raises(SystemExit) as exc:
            await cmd_generate(_make_args(input=str(temp_dir / "nope.json")))
        assert exc.value.code == 1
        assert "not found" in capsys.readouterr().err

    async def test_generate_skips_unparseable(self, temp_dir: Path, capsys):
        src = temp_dir / "raw_records.json"
        out = temp_dir / "out"
        _write_raw_json(
            src,
            [
                self._scored_item("evil-phish.com"),
                self._scored_item("bad", ioc_type="not-a-type"),
            ],
        )

        await cmd_generate(_make_args(input=str(src), output=str(out), formats="pihole"))

        assert "Skipping record" in capsys.readouterr().err
        assert (out / "threat_intel_pihole.txt").exists()


# ---------------------------------------------------------------------------
# cmd_stats
# ---------------------------------------------------------------------------


class TestCmdStats:
    async def test_stats_prints_metadata(self, capsys):
        client = AsyncMock()
        client.fetch_metadata = AsyncMock(
            return_value={
                "descriptions": {
                    "PH": DescriptionRecord(id="PH", en_title="Phishing", tr_title="Oltalama")
                },
                "connection_types": {
                    "PH": ConnectionTypeRecord(id="PH", en_title="Phishing", tr_title="Oltalama")
                },
                "sources": {"US": SourceRecord(id="US", en_title="USOM", tr_title="USOM")},
            }
        )
        client.fetch_address_count = AsyncMock(return_value={"total": 12345, "pages": 2})

        with patch("scripts.main.AsyncAPIClient", return_value=client):
            await cmd_stats(_make_args())

        out = capsys.readouterr().out
        assert "Phishing" in out
        assert "USOM" in out
        assert "12,345" in out
        client.close.assert_awaited_once()


# ---------------------------------------------------------------------------
# cmd_validate
# ---------------------------------------------------------------------------


class TestCmdValidate:
    async def test_validate_valid_records(self, temp_dir: Path, malicious_only_records, capsys):
        src = temp_dir / "raw_records.json"
        items = [r.model_dump() for r in malicious_only_records]
        _write_raw_json(src, items)

        with patch("scripts.main.AsyncAPIClient", return_value=AsyncMock()):
            await cmd_validate(_make_args(input=str(src)))

        out = capsys.readouterr().out
        assert "4 valid" in out
        assert "0 rejected" in out

    async def test_validate_with_scored_raw_records(self, temp_dir: Path, capsys):
        """P0-1: records written by ``cmd_fetch`` (``value`` key) are validated correctly."""
        src = temp_dir / "raw_records.json"
        items = [
            {
                "id": 101,
                "value": "example-phishing.net",
                "type": "domain",
                "desc": "PH",
                "source": "US",
                "date": "2024-01-01",
                "criticality_level": 2,
                "connectiontype": "PH",
            },
            {
                "id": 102,
                "value": "cnc-malware.xyz",
                "type": "domain",
                "desc": "MC",
                "source": "SO",
                "date": "2024-01-02",
                "criticality_level": 1,
                "connectiontype": "BC",
            },
            {
                "id": 103,
                "value": "192.0.2.1",
                "type": "ip",
                "desc": "CA",
                "source": "RS",
                "date": "2024-01-03",
                "criticality_level": 3,
                "connectiontype": "AC",
            },
            {
                "id": 104,
                "value": "https://drop.evil.top/mal.exe",
                "type": "url",
                "desc": "MU",
                "source": "IH",
                "date": "2024-01-04",
                "criticality_level": 4,
                "connectiontype": "MF",
            },
        ]
        _write_raw_json(src, items)
        with patch("scripts.main.AsyncAPIClient", return_value=AsyncMock()):
            await cmd_validate(_make_args(input=str(src)))
        out = capsys.readouterr().out
        assert "4 valid" in out
        assert "0 rejected" in out

    async def test_validate_skips_non_dict_records(self, temp_dir: Path, capsys):
        src = temp_dir / "raw_records.json"
        _write_raw_json(src, ["not-a-dict", 123, None])
        with patch("scripts.main.AsyncAPIClient", return_value=AsyncMock()):
            await cmd_validate(_make_args(input=str(src)))
        captured = capsys.readouterr()
        assert "0 valid" in captured.out
        assert "Skipping record" in captured.err

    async def test_validate_skips_malformed_records(self, temp_dir: Path, capsys):
        src = temp_dir / "raw_records.json"
        _write_raw_json(src, [{"no_value_or_url": True}])
        with patch("scripts.main.AsyncAPIClient", return_value=AsyncMock()):
            await cmd_validate(_make_args(input=str(src)))
        captured = capsys.readouterr()
        assert "0 valid" in captured.out
        assert "Skipping record" in captured.err

    async def test_validate_rejects_non_list_json(self, temp_dir: Path):
        src = temp_dir / "raw_records.json"
        src.write_text('{"bad": "not-a-list"}', encoding="utf-8")
        with patch("scripts.main.AsyncAPIClient", return_value=AsyncMock()):
            with pytest.raises(SystemExit) as exc:
                await cmd_validate(_make_args(input=str(src)))
            assert exc.value.code == 1

    async def test_validate_missing_input(self, temp_dir: Path):
        with (
            patch("scripts.main.AsyncAPIClient", return_value=AsyncMock()),
            pytest.raises(SystemExit) as exc,
        ):
            await cmd_validate(_make_args(input=str(temp_dir / "nope.json")))
        assert exc.value.code == 1

    async def test_validate_rejects_records(self, temp_dir: Path, sample_address_records, capsys):
        src = temp_dir / "raw_records.json"
        items = [r.model_dump() for r in sample_address_records]
        _write_raw_json(src, items)

        with patch("scripts.main.AsyncAPIClient", return_value=AsyncMock()):
            await cmd_validate(_make_args(input=str(src)))

        out = capsys.readouterr().out
        assert "rejected" in out

    async def test_validate_fetch_from_api(self, capsys):
        client = AsyncMock()
        client.fetch_addresses = AsyncMock(
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
        )
        with patch("scripts.main.AsyncAPIClient", return_value=client):
            await cmd_validate(_make_args(input=None, max_records=100))
        out = capsys.readouterr().out
        assert "2 valid" in out


# ---------------------------------------------------------------------------
# cmd_health
# ---------------------------------------------------------------------------


class TestCmdHealth:
    async def test_health_ok(self, capsys):
        client = AsyncMock()
        client.health_check = AsyncMock(return_value=True)
        client.base_url = "http://test"
        client.stats = {}

        with patch("scripts.main.AsyncAPIClient", return_value=client):
            await cmd_health(_make_args())

        out = capsys.readouterr().out
        assert "healthy" in out.lower()
        client.close.assert_awaited_once()

    async def test_health_fail_exits(self):
        client = AsyncMock()
        client.health_check = AsyncMock(return_value=False)

        with (
            patch("scripts.main.AsyncAPIClient", return_value=client),
            pytest.raises(SystemExit) as exc,
        ):
            await cmd_health(_make_args())
        assert exc.value.code == 1


# ---------------------------------------------------------------------------
# main()
# ---------------------------------------------------------------------------


class TestMain:
    def test_no_command_prints_help(self, capsys):
        with patch.object(sys, "argv", ["tc-sgb"]), pytest.raises(SystemExit) as exc:
            main()
        assert exc.value.code == 0
        assert "usage" in capsys.readouterr().out.lower()

    def test_health_command_dispatch(self, capsys):
        client = AsyncMock()
        client.health_check = AsyncMock(return_value=True)
        client.base_url = "http://test"
        client.stats = {}

        with (
            patch.object(sys, "argv", ["tc-sgb", "health"]),
            patch("scripts.main.AsyncAPIClient", return_value=client),
        ):
            main()

        out = capsys.readouterr().out
        assert "healthy" in out.lower()
        assert "Completed in" in out
