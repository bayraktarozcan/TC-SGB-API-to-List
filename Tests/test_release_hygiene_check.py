"""Tests for the live published-release hygiene audit."""

from __future__ import annotations

from Scripts import check_release_hygiene as module


def release(tag: str, title: str, body: str) -> dict[str, str]:
    return {"tag_name": tag, "name": title, "body": body}


def gl_release(tag: str, title: str, body: str) -> dict[str, str]:
    return {"tag_name": tag, "name": title, "description": body}


BODY = (
    "[English](#-english) | [Türkçe](#-türkçe)\n"
    '<a id="-english"></a>\n'
    "# TC-SGB-API-to-List v1.0.0.0\n"
    + "".join(f"### {h}\n\n- item\n" for h in module.EN_SECTIONS)
    + '<a id="-türkçe"></a>\n'
    "# TC-SGB-API-to-List v1.0.0.0\n" + "".join(f"### {h}\n\n- madde\n" for h in module.TR_SECTIONS)
)


class TestNorm:
    def test_normalizes_line_endings(self):
        assert module.norm("a\r\nb\rc\n") == "a\nb\nc"

    def test_current_version_from_oracle(self):
        assert module.current_version() == "v0.3.2.2"


class TestCheck:
    def test_clean_pair(self, monkeypatch):
        gh = {"v1.0.0.0": release("v1.0.0.0", "v1.0.0.0 — Good Title", BODY)}
        gl = {"v1.0.0.0": gl_release("v1.0.0.0", "v1.0.0.0 — Good Title", BODY)}
        monkeypatch.setattr(module, "releases", lambda: (gh, gl))
        monkeypatch.setattr(module, "current_version", lambda: "v1.0.0.0")
        assert module.check() == []

    def test_deprecated_prefix_required(self, monkeypatch, capsys):
        gh = {
            "v0.9.0.0": release("v0.9.0.0", "v0.9.0.0 — Old", BODY.replace("v1.0.0.0", "v0.9.0.0"))
        }
        gl = {"v0.9.0.0": gl_release("v0.9.0.0", "v0.9.0.0 — Old", gh["v0.9.0.0"]["body"])}
        monkeypatch.setattr(module, "releases", lambda: (gh, gl))
        monkeypatch.setattr(module, "current_version", lambda: "v1.0.0.0")
        failures = module.check()
        assert any("title-format" in f for f in failures)

    def test_rolling_release_exempt(self, monkeypatch):
        body = BODY.replace("v1.0.0.0", "IoC Data")
        gh = {"ioc-data": release("ioc-data", "IoC Data (Large Formats)", body)}
        gl = {"ioc-data": gl_release("ioc-data", "IoC Data (Large Formats)", body)}
        monkeypatch.setattr(module, "releases", lambda: (gh, gl))
        monkeypatch.setattr(module, "current_version", lambda: "v1.0.0.0")
        assert module.check() == []

    def test_pair_count_mismatch(self, monkeypatch):
        gh = {"v1.0.0.0": release("v1.0.0.0", "v1.0.0.0 — Good Title", BODY)}
        monkeypatch.setattr(module, "releases", lambda: (gh, {}))
        monkeypatch.setattr(module, "current_version", lambda: "v1.0.0.0")
        assert any("pair-count" in f for f in module.check())

    def test_bare_issue_token_detected(self, monkeypatch):
        bad = BODY.replace("- item\n", "- fix #123\n", 1)
        gh = {"v1.0.0.0": release("v1.0.0.0", "v1.0.0.0 — Good Title", bad)}
        gl = {"v1.0.0.0": gl_release("v1.0.0.0", "v1.0.0.0 — Good Title", bad)}
        monkeypatch.setattr(module, "releases", lambda: (gh, gl))
        monkeypatch.setattr(module, "current_version", lambda: "v1.0.0.0")
        assert any("no-garbage" in f for f in module.check())

    def test_body_structure_detected(self, monkeypatch):
        bad = BODY.replace("### Documentation", "### Extra")
        gh = {"v1.0.0.0": release("v1.0.0.0", "v1.0.0.0 — Good Title", bad)}
        gl = {"v1.0.0.0": gl_release("v1.0.0.0", "v1.0.0.0 — Good Title", bad)}
        monkeypatch.setattr(module, "releases", lambda: (gh, gl))
        monkeypatch.setattr(module, "current_version", lambda: "v1.0.0.0")
        assert any("body-structure" in f for f in module.check())

    def test_cross_host_mismatch_detected(self, monkeypatch):
        gh = {"v1.0.0.0": release("v1.0.0.0", "v1.0.0.0 — Good Title", BODY)}
        gl = {"v1.0.0.0": gl_release("v1.0.0.0", "v1.0.0.0 — Other Title", BODY)}
        monkeypatch.setattr(module, "releases", lambda: (gh, gl))
        monkeypatch.setattr(module, "current_version", lambda: "v1.0.0.0")
        assert any("cross-host" in f for f in module.check())

    def test_missing_anchor_detected(self, monkeypatch):
        bad = BODY.replace('<a id="-türkçe"></a>', "")
        gh = {"v1.0.0.0": release("v1.0.0.0", "v1.0.0.0 — Good Title", bad)}
        gl = {"v1.0.0.0": gl_release("v1.0.0.0", "v1.0.0.0 — Good Title", bad)}
        monkeypatch.setattr(module, "releases", lambda: (gh, gl))
        monkeypatch.setattr(module, "current_version", lambda: "v1.0.0.0")
        assert any("body-structure" in f for f in module.check())

    def test_foreign_heading_detected(self, monkeypatch):
        bad = BODY.replace("### Özet", "# TC-SGB-API-to-List v9.9.9.9\n\n### Özet")
        gh = {
            "v1.0.0.0": release("v1.0.0.0", "v1.0.0.0 — Good Title", bad),
            "v9.9.9.9": release("v9.9.9.9", "[DEPRECATED] v9.9.9.9 — Old", BODY),
        }
        gl = {
            "v1.0.0.0": gl_release("v1.0.0.0", "v1.0.0.0 — Good Title", bad),
            "v9.9.9.9": gl_release("v9.9.9.9", "[DEPRECATED] v9.9.9.9 — Old", BODY),
        }
        monkeypatch.setattr(module, "releases", lambda: (gh, gl))
        monkeypatch.setattr(module, "current_version", lambda: "v1.0.0.0")
        assert any("no-garbage" in f for f in module.check())

    def test_main_returns_failure(self, monkeypatch):
        monkeypatch.setattr(module, "check", lambda: ["FAIL planted"])
        assert module.main() == 1
