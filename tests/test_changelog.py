"""Tests for changelog generation: first-run, diff, _load_previous, _build_markdown."""

from __future__ import annotations

import json
from pathlib import Path

from scripts.src.changelog import (
    _build_markdown,
    _load_previous,
    _write_first_run_log,
    generate_changelog,
)


class TestLoadPrevious:
    def test_no_file(self, temp_dir: Path):
        assert _load_previous(temp_dir / "nonexistent.json") is None

    def test_valid_list(self, temp_dir: Path):
        data = [{"type": "domain", "value": "evil.com"}]
        path = temp_dir / "raw_records.json"
        path.write_text(json.dumps(data), encoding="utf-8")
        result = _load_previous(path)
        assert result == data

    def test_invalid_json(self, temp_dir: Path):
        path = temp_dir / "raw_records.json"
        path.write_text("not json {{{", encoding="utf-8")
        assert _load_previous(path) is None

    def test_non_list_json(self, temp_dir: Path):
        path = temp_dir / "raw_records.json"
        path.write_text(json.dumps({"key": "value"}), encoding="utf-8")
        assert _load_previous(path) is None


class TestWriteFirstRunLog:
    def test_creates_log_file(self, temp_dir: Path):
        logs_dir = temp_dir / "logs"
        logs_dir.mkdir()
        _write_first_run_log(logs_dir, 100)
        files = list(logs_dir.glob("fetch_*.md"))
        assert len(files) == 1
        content = files[0].read_text(encoding="utf-8")
        assert "100" in content
        assert "ilk" in content

    def test_file_count_and_timestamp(self, temp_dir: Path):
        logs_dir = temp_dir / "logs"
        logs_dir.mkdir()
        _write_first_run_log(logs_dir, 500)
        files = list(logs_dir.glob("fetch_*.md"))
        assert files[0].name.startswith("fetch_")


class TestBuildMarkdown:
    def test_with_new_and_removed(self):
        lines = _build_markdown(
            ts_label="2024-01-01 00:00:00 UTC",
            total_current=100,
            total_previous=90,
            new_records=[
                {
                    "value": "new.com",
                    "type": "domain",
                    "source": "US",
                    "criticality_level": 3,
                    "quality_score": 85.0,
                    "false_positive_risk": "low",
                }
            ],
            removed_records=[
                {"value": "old.com", "type": "domain", "source": "RS", "criticality_level": 5}
            ],
        )
        text = "\n".join(lines)
        assert "100" in text
        assert "90" in text
        assert "+10" in text
        assert "new.com" in text
        assert "old.com" in text

    def test_no_new_no_removed(self):
        lines = _build_markdown(
            ts_label="2024-01-01",
            total_current=50,
            total_previous=50,
            new_records=[],
            removed_records=[],
        )
        text = "\n".join(lines)
        assert "Yeni IOC yok" in text
        assert "Silinen IOC yok" in text
        assert "Net değişim: **+0**" in text

    def test_negative_delta(self):
        lines = _build_markdown(
            ts_label="2024-01-01",
            total_current=80,
            total_previous=100,
            new_records=[],
            removed_records=[{"value": "x.com", "type": "domain"}],
        )
        text = "\n".join(lines)
        assert "-20" in text

    def test_new_records_table_structure(self):
        lines = _build_markdown(
            ts_label="2024-01-01",
            total_current=1,
            total_previous=0,
            new_records=[
                {
                    "value": "a.com",
                    "type": "domain",
                    "source": "US",
                    "criticality_level": 2,
                    "quality_score": 90.0,
                    "false_positive_risk": "low",
                }
            ],
            removed_records=[],
        )
        text = "\n".join(lines)
        assert "| Değer | Tip | Kaynak | Kritiklik | Güven Skoru | FP Riski |" in text

    def test_removed_records_table_structure(self):
        lines = _build_markdown(
            ts_label="2024-01-01",
            total_current=0,
            total_previous=1,
            new_records=[],
            removed_records=[
                {"value": "b.com", "type": "ip", "source": "SO", "criticality_level": 7}
            ],
        )
        text = "\n".join(lines)
        assert "| Değer | Tip | Kaynak | Kritiklik |" in text


class TestGenerateChangelog:
    def test_first_run_returns_none(self, temp_dir: Path):
        result = generate_changelog(temp_dir, [{"type": "domain", "value": "a.com"}])
        assert result is None
        logs = list((temp_dir / "logs").glob("fetch_*.md"))
        assert len(logs) == 1

    def test_second_run_returns_path(self, temp_dir: Path):
        previous = [{"type": "domain", "value": "old.com"}]
        (temp_dir / "raw_records.json").write_text(json.dumps(previous), encoding="utf-8")
        current = [{"type": "domain", "value": "new.com"}]
        result = generate_changelog(temp_dir, current)
        assert result is not None
        assert result.exists()
        assert result.suffix == ".md"
        content = result.read_text(encoding="utf-8")
        assert "new.com" in content
        assert "old.com" in content

    def test_creates_logs_dir(self, temp_dir: Path):
        generate_changelog(temp_dir, [])
        assert (temp_dir / "logs").is_dir()

    def test_diff_with_same_records(self, temp_dir: Path):
        records = [{"type": "domain", "value": "same.com"}]
        (temp_dir / "raw_records.json").write_text(json.dumps(records), encoding="utf-8")
        result = generate_changelog(temp_dir, records)
        assert result is not None
        content = result.read_text(encoding="utf-8")
        assert "Yeni IOC yok" in content
        assert "Silinen IOC yok" in content
