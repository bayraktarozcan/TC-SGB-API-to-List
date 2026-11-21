"""Tests for the tracked pre-push hook installer."""

from __future__ import annotations

from pathlib import Path

import pytest

from Scripts import install_hooks


class TestHooksDirectory:
    def test_default_directory(self, tmp_path: Path, monkeypatch):
        (tmp_path / ".git").mkdir()
        (tmp_path / ".git" / "config").write_text("[core]\n", encoding="utf-8")
        monkeypatch.setattr(install_hooks, "ROOT", tmp_path)
        assert install_hooks.hooks_directory() == tmp_path / ".git" / "hooks"

    def test_configured_directory(self, tmp_path: Path, monkeypatch):
        (tmp_path / ".git").mkdir()
        (tmp_path / ".git" / "config").write_text(
            "[core]\n\thooksPath = custom/hooks\n", encoding="utf-8"
        )
        monkeypatch.setattr(install_hooks, "ROOT", tmp_path)
        assert install_hooks.hooks_directory() == tmp_path / "custom" / "hooks"

    def test_absolute_directory(self, tmp_path: Path, monkeypatch):
        (tmp_path / ".git").mkdir()
        absolute = tmp_path.parent / "absolute-hooks"
        (tmp_path / ".git" / "config").write_text(
            f"[core]\n\thooksPath = {absolute}\n", encoding="utf-8"
        )
        monkeypatch.setattr(install_hooks, "ROOT", tmp_path)
        assert install_hooks.hooks_directory() == absolute

    def test_config_with_duplicate_pushurl(self, tmp_path: Path, monkeypatch):
        (tmp_path / ".git").mkdir()
        (tmp_path / ".git" / "config").write_text(
            '[core]\n\thooksPath = hooks\n[remote "origin"]\n\tpushurl = a\n\tpushurl = b\n',
            encoding="utf-8",
        )
        monkeypatch.setattr(install_hooks, "ROOT", tmp_path)
        assert install_hooks.hooks_directory() == tmp_path / "hooks"


class TestInstall:
    def test_install_copies_hook(self, tmp_path: Path, monkeypatch):
        source_dir = tmp_path / "Scripts"
        source_dir.mkdir()
        (source_dir / "pre-push").write_text("#!/bin/sh\ntrue\n", encoding="utf-8")
        (tmp_path / ".git").mkdir()
        (tmp_path / ".git" / "config").write_text("[core]\n", encoding="utf-8")
        monkeypatch.setattr(install_hooks, "ROOT", tmp_path)
        monkeypatch.setattr(install_hooks, "SOURCE", source_dir / "pre-push")
        monkeypatch.setattr("sys.argv", ["install_hooks.py"])
        install_hooks.main()
        target = tmp_path / ".git" / "hooks" / "pre-push"
        assert target.read_text(encoding="utf-8") == "#!/bin/sh\ntrue\n"

    def test_install_backs_up_existing_hook(self, tmp_path: Path, monkeypatch):
        source_dir = tmp_path / "Scripts"
        source_dir.mkdir()
        (source_dir / "pre-push").write_text("new\n", encoding="utf-8")
        hooks = tmp_path / ".git" / "hooks"
        hooks.mkdir(parents=True)
        (hooks / "pre-push").write_text("old\n", encoding="utf-8")
        (tmp_path / ".git" / "config").write_text("[core]\n", encoding="utf-8")
        monkeypatch.setattr(install_hooks, "ROOT", tmp_path)
        monkeypatch.setattr(install_hooks, "SOURCE", source_dir / "pre-push")
        monkeypatch.setattr("sys.argv", ["install_hooks.py"])
        install_hooks.main()
        backups = list(hooks.glob("pre-push.*.bak"))
        assert len(backups) == 1
        assert backups[0].read_text(encoding="utf-8") == "old\n"
        assert (hooks / "pre-push").read_text(encoding="utf-8") == "new\n"

    def test_uninstall_removes_hook(self, tmp_path: Path, monkeypatch):
        (tmp_path / ".git").mkdir()
        hooks = tmp_path / ".git" / "hooks"
        hooks.mkdir()
        (hooks / "pre-push").write_text("x\n", encoding="utf-8")
        (tmp_path / ".git" / "config").write_text("[core]\n", encoding="utf-8")
        monkeypatch.setattr(install_hooks, "ROOT", tmp_path)
        monkeypatch.setattr("sys.argv", ["install_hooks.py", "--uninstall"])
        install_hooks.main()
        assert not (hooks / "pre-push").exists()

    def test_install_rejects_missing_source(self, tmp_path: Path, monkeypatch):
        (tmp_path / ".git").mkdir()
        (tmp_path / ".git" / "config").write_text("[core]\n", encoding="utf-8")
        monkeypatch.setattr(install_hooks, "ROOT", tmp_path)
        monkeypatch.setattr(install_hooks, "SOURCE", tmp_path / "missing")
        monkeypatch.setattr("sys.argv", ["install_hooks.py"])
        with pytest.raises(SystemExit, match="missing tracked hook"):
            install_hooks.main()
