"""Guards for the Python compatibility floor and its EOL automation."""

from __future__ import annotations

import shutil
from datetime import date
from io import BytesIO
from pathlib import Path

from Scripts import bump_python_floor as module
from Scripts.bump_python_floor import (
    FLOOR_DECLARATIONS,
    REPLACEMENTS,
    _version_key,
    apply_bump,
    find_drift,
    read_floor,
    resolve_floor,
)
from Scripts.verify_mirror import marker_value

REPO_ROOT = Path(__file__).resolve().parents[1]

CYCLES = {
    "3.15": {"status": "bugfix", "end_of_life": "2031-10"},
    "3.14": {"status": "bugfix", "end_of_life": "2030-10"},
    "3.13": {"status": "security", "end_of_life": "2029-10"},
    "3.12": {"status": "security", "end_of_life": "2028-10"},
    "3.11": {"status": "security", "end_of_life": "2027-10"},
    "3.10": {"status": "end-of-life", "end_of_life": "2026-10-01"},
}


class TestResolveFloor:
    def test_oldest_supported_wins(self):
        assert resolve_floor(CYCLES, date(2026, 11, 21)) == "3.11"

    def test_end_of_life_status_is_excluded(self):
        cycles = dict(CYCLES)
        cycles["3.11"] = {"status": "end-of-life", "end_of_life": "2027-10"}
        assert resolve_floor(cycles, date(2026, 11, 21)) == "3.12"

    def test_passed_eol_date_is_excluded_even_when_status_lags(self):
        cycles = dict(CYCLES)
        cycles["3.11"] = {"status": "security", "end_of_life": "2026-10"}
        assert resolve_floor(cycles, date(2026, 11, 21)) == "3.12"

    def test_month_rollover_boundary(self):
        cycles = {
            "3.11": {"status": "security", "end_of_life": "2027-10"},
            "3.12": {"status": "security", "end_of_life": "2028-10"},
        }
        assert resolve_floor(cycles, date(2027, 10, 31)) == "3.11"
        assert resolve_floor(cycles, date(2027, 11, 1)) == "3.12"

    def test_missing_eol_date_is_treated_as_supported(self):
        cycles = {
            "3.11": {"status": "security"},
            "3.12": {"status": "security", "end_of_life": "2028-10"},
        }
        assert resolve_floor(cycles, date(2026, 11, 21)) == "3.11"

    def test_empty_calendar_rejected(self):
        import pytest

        with pytest.raises(ValueError, match="no supported"):
            resolve_floor({}, date(2026, 11, 21))


def _payload():
    import json

    return BytesIO(json.dumps({f"3.{n}": {"status": "security"} for n in range(5, 20)}).encode())


class TestFetchCycles:
    def test_valid_payload(self, monkeypatch):
        monkeypatch.setattr(module.urllib.request, "urlopen", lambda *_a, **_k: _payload())
        assert len(module.fetch_cycles()) == 15

    def test_retry_then_success(self, monkeypatch):
        calls = []

        def fake_urlopen(*_a, **_k):
            calls.append(1)
            if len(calls) < 2:
                raise OSError("transient")
            return _payload()

        monkeypatch.setattr(module.urllib.request, "urlopen", fake_urlopen)
        monkeypatch.setattr(module.time, "sleep", lambda _n: None)
        assert module.fetch_cycles(attempts=2) == module.fetch_cycles(attempts=1)
        assert len(calls) >= 2

    def test_exhausted_retries_raise(self, monkeypatch):
        def fail(*_a, **_k):
            raise OSError("down")

        monkeypatch.setattr(module.urllib.request, "urlopen", fail)
        monkeypatch.setattr(module.time, "sleep", lambda _n: None)
        import pytest

        with pytest.raises(RuntimeError, match="could not fetch"):
            module.fetch_cycles(attempts=2)

    def test_incomplete_payload_rejected(self, monkeypatch):
        monkeypatch.setattr(
            module.urllib.request,
            "urlopen",
            lambda *_a, **_k: BytesIO(b'{"a": 1}'),
        )
        monkeypatch.setattr(module.time, "sleep", lambda _n: None)
        import pytest

        with pytest.raises(RuntimeError, match="could not fetch"):
            module.fetch_cycles(attempts=1)


class TestFloorParity:
    def test_live_tree_has_no_drift(self):
        assert find_drift(REPO_ROOT) == []

    def test_declared_floor_matches_pyproject(self):
        assert read_floor(REPO_ROOT) == "3.11"

    def test_guard_flags_planted_drift(self, tmp_path: Path):
        _copy_declarations(tmp_path)
        (tmp_path / "pyproject.toml").write_text(
            (tmp_path / "pyproject.toml")
            .read_bytes()
            .decode("utf-8")
            .replace('requires-python = ">=3.11"', 'requires-python = ">=3.12"', 1),
            encoding="utf-8",
        )
        assert find_drift(tmp_path), "planting a drift must be detected"

    def test_guard_flags_missing_file(self, tmp_path: Path):
        _copy_declarations(tmp_path)
        (tmp_path / ".gitlab-ci.yml").unlink()
        assert any("missing file" in problem for problem in find_drift(tmp_path))

    def test_guard_flags_missing_classifier(self, tmp_path: Path):
        _copy_declarations(tmp_path)
        path = tmp_path / "pyproject.toml"
        path.write_bytes(
            path.read_bytes().replace(b'    "Programming Language :: Python :: 3.11",\n', b"")
        )
        assert any("missing metadata" in problem for problem in find_drift(tmp_path))

    def test_read_floor_raises_without_declaration(self, tmp_path: Path):
        import pytest

        (tmp_path / "pyproject.toml").write_text("[project]\n", encoding="utf-8")
        with pytest.raises(ValueError, match="requires-python not found"):
            read_floor(tmp_path)

    def test_missing_declared_file_is_reported(self, tmp_path: Path):
        (tmp_path / "pyproject.toml").write_text('requires-python = ">=3.11"\n', encoding="utf-8")
        assert any("missing file" in p for p in find_drift(tmp_path))


class TestApplyBump:
    def test_bump_updates_every_declaration(self, tmp_path: Path):
        _copy_declarations(tmp_path)
        changed = apply_bump(tmp_path, "3.11", "3.12")
        assert set(changed) == set(REPLACEMENTS)
        assert find_drift(tmp_path) == []
        assert read_floor(tmp_path) == "3.12"

    def test_bump_refreshes_mirror_marker(self, tmp_path: Path):
        _copy_declarations(tmp_path)
        before = marker_value((tmp_path / "AGENTS.md").read_bytes().decode("utf-8"))
        apply_bump(tmp_path, "3.11", "3.12")
        after = marker_value((tmp_path / "AGENTS.md").read_bytes().decode("utf-8"))
        assert after is not None
        assert after != before
        mirror_after = marker_value((tmp_path / "AGENTS-TR.md").read_bytes().decode("utf-8"))
        assert mirror_after == after

    def test_classifier_dedup_on_bump(self, tmp_path: Path):
        _copy_declarations(tmp_path)
        apply_bump(tmp_path, "3.11", "3.12")
        text = (tmp_path / "pyproject.toml").read_bytes().decode("utf-8")
        assert text.count("Programming Language :: Python :: 3.12") == 1
        assert "Programming Language :: Python :: 3.11" not in text

    def test_apply_never_downgrades_by_convention(self):
        assert _version_key("3.11") < _version_key("3.12")
        assert _version_key("3.12") > _version_key("3.11")

    def test_check_refuses_downgrade(self, monkeypatch, capsys):
        monkeypatch.setattr(module, "read_floor", lambda _root: "3.12")
        monkeypatch.setattr(module, "find_drift", lambda _root: [])
        monkeypatch.setattr(
            module,
            "fetch_cycles",
            lambda: {
                "3.11": {"status": "security", "end_of_life": "2027-10"},
                "3.12": {"status": "security", "end_of_life": "2028-10"},
            },
        )
        assert module._check(REPO_ROOT) == 0
        assert "refusing to downgrade" in capsys.readouterr().err

    def test_check_writes_github_outputs(self, monkeypatch, tmp_path: Path):
        output = tmp_path / "outputs"
        monkeypatch.setenv("GITHUB_OUTPUT", str(output))
        monkeypatch.setattr(module, "fetch_cycles", lambda: CYCLES)
        monkeypatch.setattr(module, "find_drift", lambda _root: [])
        assert module._check(REPO_ROOT) == 0
        text = output.read_text(encoding="utf-8")
        assert "desired=3.11" in text
        assert "current=3.11" in text
        assert "changed=false" in text

    def test_check_reports_drift(self, monkeypatch):
        monkeypatch.setattr(module, "fetch_cycles", lambda: CYCLES)
        monkeypatch.setattr(module, "find_drift", lambda _root: ["planted drift"])
        assert module._check(REPO_ROOT) == 2

    def test_main_apply_writes_expected_files(self, monkeypatch, tmp_path: Path, capsys):
        monkeypatch.setattr(module, "__file__", str(tmp_path / "Scripts" / "x.py"))
        monkeypatch.setattr("sys.argv", ["prog", "apply", "3.12"])
        monkeypatch.chdir(tmp_path)
        (tmp_path / "pyproject.toml").write_text(
            'requires-python = ">=3.11"\npython_version = "3.11"\n', encoding="utf-8"
        )
        assert module.main() == 0
        assert "Python floor 3.11 -> 3.12" in capsys.readouterr().out

    def test_main_check_delegates(self, monkeypatch):
        monkeypatch.setattr("sys.argv", ["prog", "check"])
        monkeypatch.setattr(module, "_check", lambda _root: 0)
        assert module.main() == 0

    def test_main_rejects_bad_version(self, monkeypatch):
        import pytest

        monkeypatch.setattr("sys.argv", ["prog", "apply", "python3"])
        with pytest.raises(SystemExit):
            module.main()


def _copy_declarations(destination: Path) -> None:
    for name in FLOOR_DECLARATIONS:
        source = REPO_ROOT / name
        target = destination / name
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(source, target)
