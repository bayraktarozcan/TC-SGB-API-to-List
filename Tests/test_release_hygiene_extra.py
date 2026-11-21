"""Additional branches for the release hygiene auditor."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from Scripts import check_release_hygiene as module
from Tests.test_release_hygiene_check import BODY, gl_release, release


class TestVersionOracle:
    def test_missing_version_exits(self, monkeypatch, tmp_path: Path):
        monkeypatch.setattr(module, "ROOT", tmp_path)
        (tmp_path / "pyproject.toml").write_text("[project]\n", encoding="utf-8")
        with pytest.raises(SystemExit, match="version not found"):
            module.current_version()


class TestReleaseFetch:
    def test_github_and_gitlab_rest(self, monkeypatch):
        class FakeResponse:
            def __enter__(self):
                return self

            def __exit__(self, *_args):
                return None

            def read(self):
                return json.dumps([{"tag_name": "v1"}]).encode()

        class FakeRun:
            def __init__(self, stdout):
                self.stdout = stdout

        def fake_run(*_args, **_kwargs):
            return FakeRun(json.dumps([{"tag_name": "v1"}]))

        def fake_urlopen(*_args, **_kwargs):
            return FakeResponse()

        monkeypatch.setattr(module.subprocess, "run", fake_run)
        monkeypatch.setattr(module.urllib.request, "urlopen", fake_urlopen)
        gh, gl = module.releases()
        assert set(gh) == {"v1"}
        assert set(gl) == {"v1"}

    def test_gitlab_cli_fallback(self, monkeypatch):
        class FakeRun:
            def __init__(self, stdout):
                self.stdout = stdout

        def fake_run(*_args, **_kwargs):
            return FakeRun(json.dumps([{"tag_name": "v1"}]))

        def fail_urlopen(*_args, **_kwargs):
            raise OSError("network blocked")

        monkeypatch.setattr(module.subprocess, "run", fake_run)
        monkeypatch.setattr(module.urllib.request, "urlopen", fail_urlopen)
        gh, gl = module.releases()
        assert set(gh) == {"v1"}
        assert set(gl) == {"v1"}


class TestTitleBranches:
    def _check(self, monkeypatch, title: str):
        gh = {"v1.0.0.0": release("v1.0.0.0", title, BODY)}
        gl = {"v1.0.0.0": gl_release("v1.0.0.0", title, BODY)}
        monkeypatch.setattr(module, "releases", lambda: (gh, gl))
        monkeypatch.setattr(module, "current_version", lambda: "v1.0.0.0")
        return module.check()

    def test_bad_rolling_title(self, monkeypatch):
        gh = {"ioc-data": release("ioc-data", "Wrong Title", BODY)}
        gl = {"ioc-data": gl_release("ioc-data", "Wrong Title", BODY)}
        monkeypatch.setattr(module, "releases", lambda: (gh, gl))
        monkeypatch.setattr(module, "current_version", lambda: "v1.0.0.0")
        assert any("unexpected rolling title" in f for f in module.check())

    def test_malformed_title(self, monkeypatch):
        assert any("bad format" in f for f in self._check(monkeypatch, "no format"))

    def test_current_marked_deprecated(self, monkeypatch):
        assert any(
            "current marked deprecated" in f
            for f in self._check(monkeypatch, "[DEPRECATED] v1.0.0.0 — Old")
        )

    def test_tag_repeated(self, monkeypatch):
        assert any(
            "tag repeated" in f for f in self._check(monkeypatch, "v1.0.0.0 — v1.0.0.0 Title")
        )


class TestGarbageAndParity:
    def _run(self, monkeypatch, body: str, gl_body: str | None = None):
        gh = {"v1.0.0.0": release("v1.0.0.0", "v1.0.0.0 — Good Title", body)}
        gl = {
            "v1.0.0.0": gl_release(
                "v1.0.0.0", "v1.0.0.0 — Good Title", gl_body if gl_body is not None else body
            )
        }
        monkeypatch.setattr(module, "releases", lambda: (gh, gl))
        monkeypatch.setattr(module, "current_version", lambda: "v1.0.0.0")
        return module.check()

    def test_embedded_toc(self, monkeypatch):
        assert any(
            "embedded TOC" in f
            for f in self._run(monkeypatch, BODY.replace("### Özet", "### İçindekiler\n\n### Özet"))
        )

    def test_cross_host_body_mismatch(self, monkeypatch):
        assert any("cross-host" in f for f in self._run(monkeypatch, BODY, BODY + "extra\n"))

    def test_changelog_coverage_detects_missing_bullet(self, monkeypatch, tmp_path: Path):
        changelog = (
            "## [v1.0.0.0] — 2026-11-21\n\n### Added\n\n- missing bullet\n"
            '<a id="-türkçe"></a>\n\n## [v1.0.0.0] — 2026-11-21\n\n### Eklenen\n\n- eksik madde\n'
        )
        (tmp_path / "CHANGELOG.md").write_text(changelog, encoding="utf-8")
        monkeypatch.setattr(module, "ROOT", tmp_path)
        gh = {"v1.0.0.0": release("v1.0.0.0", "v1.0.0.0 — Good Title", BODY)}
        gl = {"v1.0.0.0": gl_release("v1.0.0.0", "v1.0.0.0 — Good Title", BODY)}
        monkeypatch.setattr(module, "releases", lambda: (gh, gl))
        monkeypatch.setattr(module, "current_version", lambda: "v1.0.0.0")
        assert any("changelog-coverage" in f for f in module.check())
