"""Tests for the mojibake scanner used in CI gate jobs."""

from __future__ import annotations

import shutil
import subprocess  # nosec B404
from pathlib import Path

import pytest

from scripts.src.mojibake import (
    check_bytes,
    is_binary,
    scan_commit_messages,
    scan_paths,
    scan_tag_messages,
    scan_working_tree,
)
from scripts.src.mojibake import (
    main as mojibake_main,
)

_GIT = shutil.which("git")
requires_git = pytest.mark.skipif(_GIT is None, reason="git executable not found")

# -- Documented corruption: UTF-8 bytes re-decoded as latin-1 and saved again ----
CLEAN_TURKISH = "ilk \u00e7al\u0131\u015fma, \u00f6nceki veri yok\n"  # ilk çalışma
CORRUPT_TURKISH = CLEAN_TURKISH.encode("utf-8").decode("latin-1").encode("utf-8")


def _corrupt(text: str) -> bytes:
    return text.encode("utf-8").decode("latin-1").encode("utf-8")


@pytest.mark.parametrize(
    ("data", "expected_findings"),
    [
        (b"plain ascii text\n", False),
        (CLEAN_TURKISH.encode("utf-8"), False),
        (b"https://x.example/avatar?v=4&q=1\n", False),
        (b"\x00\x01\x02PNG\x00\x00\x00", False),
        (_corrupt("\u00f6nceki"), True),
        ("caf\u00e9 au lait\n".encode("utf-8"), False),  # valid UTF-8 accent is fine
    ],
)
def test_check_bytes(data: bytes, expected_findings: bool) -> None:
    assert bool(check_bytes(data)) is expected_findings


def test_check_bytes_detects_undecodable_text() -> None:
    hits = check_bytes(b"abc\x80\xbd")
    assert hits
    assert "invalid UTF-8" in hits[0]


def test_check_bytes_empty() -> None:
    assert check_bytes(b"") == []


@pytest.mark.parametrize(
    ("data", "expected"),
    [
        (b"\x00abc", True),
        (b"abc", False),
        (b"", False),
    ],
)
def test_is_binary(data: bytes, expected: bool) -> None:
    assert is_binary(data) is expected


def test_scan_paths(tmp_path: Path) -> None:
    clean = tmp_path / "clean.txt"
    clean.write_bytes(CLEAN_TURKISH.encode("utf-8"))
    bad = tmp_path / "bad.txt"
    bad.write_bytes(_corrupt("\u00f6nceki veri yok"))
    findings = scan_paths([clean, bad])
    assert [label for label, _ in findings] == [str(bad)]


def _git(repo: Path, *args: str) -> str:
    assert _GIT is not None
    return subprocess.run(  # nosec B603
        [_GIT, "-C", str(repo), *args],
        check=True,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    ).stdout


@pytest.fixture
def git_repo(tmp_path: Path) -> Path:
    repo = tmp_path / "repo"
    repo.mkdir()
    _git(repo, "init", "-b", "main")
    _git(repo, "config", "user.email", "ci@example.com")
    _git(repo, "config", "user.name", "CI")
    return repo


@requires_git
def test_working_tree_clean(git_repo: Path) -> None:
    (git_repo / "clean.md").write_bytes(CLEAN_TURKISH.encode("utf-8"))
    _git(git_repo, "add", ".")
    _git(git_repo, "commit", "-m", "feat: clean content")
    assert scan_working_tree(git_repo) == []


@requires_git
def test_working_tree_detects_mojibake(git_repo: Path) -> None:
    (git_repo / "bad.md").write_bytes(_corrupt("\u00f6nceki"))
    _git(git_repo, "add", ".")
    _git(git_repo, "commit", "-m", "feat: bad content")
    findings = scan_working_tree(git_repo)
    assert findings
    assert findings[0][0] == "bad.md"


@requires_git
def test_commit_message_detected(git_repo: Path) -> None:
    (git_repo / "a.txt").write_bytes(b"ok\n")
    _git(git_repo, "add", ".")
    _git(git_repo, "commit", "-m", _corrupt("\u00f6ncelik").decode("utf-8"))
    assert scan_commit_messages(git_repo)


@requires_git
def test_tag_message_detected(git_repo: Path) -> None:
    (git_repo / "a.txt").write_bytes(b"ok\n")
    _git(git_repo, "add", ".")
    _git(git_repo, "commit", "-m", "feat: initial")
    _git(git_repo, "tag", "-a", "v1.0.0", "-m", _corrupt("s\u00fcr\u00fcm").decode("utf-8"))
    assert scan_tag_messages(git_repo)


@requires_git
def test_history_detects_removed_blob(git_repo: Path) -> None:
    (git_repo / "x.txt").write_bytes(_corrupt("\u00f6nceki"))
    _git(git_repo, "add", ".")
    _git(git_repo, "commit", "-m", "feat: binary-coded content")
    (git_repo / "x.txt").write_bytes(b"clean\n")
    _git(git_repo, "add", ".")
    _git(git_repo, "commit", "-m", "fix: replace content")
    # HEAD tree is now clean; the old blob must still be caught by history scope.
    from scripts.src.mojibake import scan

    assert scan_working_tree(git_repo) == []
    assert any(label.startswith("blob ") for label, _ in scan("history", git_repo))


# --- main() CLI exit paths ------------------------------------------------


@requires_git
def test_main_clean_repo_exit_zero(git_repo: Path, monkeypatch) -> None:
    (git_repo / "clean.md").write_bytes(CLEAN_TURKISH.encode("utf-8"))
    _git(git_repo, "add", ".")
    _git(git_repo, "commit", "-m", "feat: clean content")
    monkeypatch.chdir(git_repo)
    assert mojibake_main(["--scope", "head"]) == 0


@requires_git
def test_main_corrupt_repo_exit_one(git_repo: Path, monkeypatch) -> None:
    (git_repo / "bad.md").write_bytes(_corrupt("\u00f6nceki"))
    _git(git_repo, "add", ".")
    _git(git_repo, "commit", "-m", "feat: bad content")
    monkeypatch.chdir(git_repo)
    assert mojibake_main(["--scope", "head"]) == 1


@requires_git
def test_main_not_a_git_repo_exit_two(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.chdir(tmp_path)
    assert mojibake_main(["--scope", "head"]) == 2


def test_main_git_missing_exit_two(monkeypatch) -> None:
    import scripts.src.mojibake as mojibake

    monkeypatch.setattr(
        mojibake, "_git_exe", lambda: (_ for _ in ()).throw(FileNotFoundError("no git"))
    )
    assert mojibake_main(["--scope", "head"]) == 2


# --- defensive branches in _iter_history_blobs ----------------------------


class _Sink:
    def __init__(self) -> None:
        self._written = b""

    def write(self, data: bytes) -> int:
        self._written += data
        return len(data)

    def flush(self) -> None:
        pass

    def close(self) -> None:
        pass


class _Source:
    def __init__(self, data: bytes) -> None:
        self._data = data

    def readline(self) -> bytes:
        idx = self._data.find(b"\n")
        if idx == -1:
            chunk, self._data = self._data, b""
        else:
            chunk, self._data = self._data[: idx + 1], self._data[idx + 1 :]
        return chunk

    def read(self, size: int = -1) -> bytes:
        if size == -1:
            chunk, self._data = self._data, b""
            return chunk
        chunk, self._data = self._data[:size], self._data[size:]
        return chunk

    def close(self) -> None:
        pass


class _FakePopen:
    def __init__(
        self, args: list[str], stdin: _Sink | None, stdout: _Source | None, cwd: object
    ) -> None:
        self.args = args
        self.stdin = stdin
        self.stdout = stdout

    def kill(self) -> None:
        pass

    def terminate(self) -> None:
        pass

    def wait(self) -> None:
        pass


def _patch_batch(monkeypatch, revs: str, stream: bytes) -> None:
    import scripts.src.mojibake as mojibake

    monkeypatch.setattr(mojibake, "_run_git", lambda root, *args: revs)

    def fake_popen(args, stdin, stdout, cwd):
        return _FakePopen(args, _Sink(), _Source(stream), cwd)

    monkeypatch.setattr(mojibake.subprocess, "Popen", fake_popen)
    monkeypatch.setattr(mojibake, "_git_exe", lambda: "git")


def _iter(monkeypatch, revs: str, stream: bytes) -> list[tuple[str, bytes]]:
    import scripts.src.mojibake as mojibake

    _patch_batch(monkeypatch, revs, stream)
    return list(mojibake._iter_history_blobs(Path()))


def test_history_blob_yielded(monkeypatch) -> None:
    found = _iter(monkeypatch, "aabb\n", b"aabb blob 2\n\xc3\x80\n")
    assert found == [("aabb", b"\xc3\x80")]


def test_history_malformed_header(monkeypatch) -> None:
    assert _iter(monkeypatch, "aabb\n", b"no spaces here\n") == []


def test_history_non_numeric_size(monkeypatch) -> None:
    assert _iter(monkeypatch, "aabb\n", b"aabb blob xx\n") == []


def test_history_short_payload(monkeypatch) -> None:
    assert _iter(monkeypatch, "aabb\n", b"aabb blob 10\nshort\n") == []


def test_history_eof_header(monkeypatch) -> None:
    assert _iter(monkeypatch, "aabb\n", b"") == []


def test_history_tree_skipped_not_yielded(monkeypatch) -> None:
    assert _iter(monkeypatch, "aabb\n", b"aabb tree 2\nAB\n") == []


def test_history_pipe_error_raises(monkeypatch) -> None:
    import scripts.src.mojibake as mojibake

    monkeypatch.setattr(mojibake, "_run_git", lambda root, *args: "aabb\n")

    def fake_popen(args, stdin, stdout, cwd):
        return _FakePopen(args, None, None, cwd)

    monkeypatch.setattr(mojibake.subprocess, "Popen", fake_popen)
    monkeypatch.setattr(mojibake, "_git_exe", lambda: "git")
    with pytest.raises(RuntimeError):
        list(mojibake._iter_history_blobs(Path()))
