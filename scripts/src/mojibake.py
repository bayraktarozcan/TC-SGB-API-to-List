"""Detect mojibake (UTF-8 corruption) in repository text for CI gates.

Scans every git-tracked file at HEAD, all commit and tag messages, and (in
``history`` scope) every blob reachable from HEAD. Exits non-zero when any
finding is present so pushes cannot smuggle corrupted text into the repo.
"""

from __future__ import annotations

import argparse
import re
import shutil
import subprocess  # nosec B404
import sys
from collections.abc import Iterator, Sequence
from pathlib import Path

MOJIBAKE_REGEX = re.compile(
    r"\u00e2\u20ac[\x80-\xbf]"
    r"|\u00e2\u20ac"
    r"|\u00e2\u201e"
    r"|\u00c2[\u00a6-\u00bf]"
    r"|\u00c3[\u0080-\u00ff]"
    r"|\u00c4[\u0080-\u00ff]"
    r"|\u00c5[\u0080-\u00ff]"
    r"|\u00c6\u2019"
    r"|\ufffd"
)

_NUL_PROBE = 8192


def _git_exe() -> str:
    exe = shutil.which("git")
    if exe is None:
        raise FileNotFoundError("git is not installed or not on PATH")
    return exe


def _run_git(cwd: Path | None, *args: str) -> str:
    proc = subprocess.run(  # noqa: S603 # nosec B603
        [_git_exe(), *args],
        check=True,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        cwd=cwd,
    )
    return proc.stdout


def _git_root(cwd: Path) -> Path:
    return Path(_run_git(cwd, "rev-parse", "--show-toplevel").strip())


def is_binary(data: bytes) -> bool:
    """True when the probe region contains a NUL byte (binary file)."""
    return b"\x00" in data[:_NUL_PROBE]


def scan_text(text: str) -> list[str]:
    """Return mojibake findings for decoded text; empty when clean."""
    return [
        f"mojibake sequence {match.group()!r} at char {match.start()}"
        for match in MOJIBAKE_REGEX.finditer(text)
    ]


def check_bytes(data: bytes) -> list[str]:
    """Return mojibake findings for raw bytes; empty when clean or binary."""
    if not data or is_binary(data):
        return []
    try:
        text = data.decode("utf-8")
    except UnicodeDecodeError as exc:
        return [f"invalid UTF-8 near byte {exc.start}: {exc.reason}"]
    return scan_text(text)


def scan_paths(paths: Sequence[Path]) -> list[tuple[str, list[str]]]:
    """Scan files directly without git (used by tests)."""
    findings: list[tuple[str, list[str]]] = []
    for path in paths:
        hits = check_bytes(path.read_bytes())
        if hits:
            findings.append((str(path), hits))
    return findings


def scan_working_tree(root: Path) -> list[tuple[str, list[str]]]:
    """Scan every git-tracked file at HEAD (relative path, findings)."""
    findings: list[tuple[str, list[str]]] = []
    for rel in _run_git(root, "ls-files", "--cached").splitlines():
        try:
            data = (root / rel).read_bytes()
        except OSError:
            continue
        hits = check_bytes(data)
        if hits:
            findings.append((rel, hits))
    return findings


def scan_commit_messages(root: Path) -> list[tuple[str, list[str]]]:
    """Scan every commit subject/body reachable from HEAD."""
    findings: list[tuple[str, list[str]]] = []
    raw = _run_git(root, "log", "-z", "--format=%B", "HEAD")
    for msg in raw.split("\x00"):
        if not msg.strip():
            continue
        hits = scan_text(msg)
        if hits:
            subject = msg.splitlines()[0][:72]
            findings.append((f"commit: {subject!r}", hits))
    return findings


def scan_tag_messages(root: Path) -> list[tuple[str, list[str]]]:
    """Scan tag names and annotated-tag message subjects."""
    findings: list[tuple[str, list[str]]] = []
    raw = _run_git(
        root,
        "for-each-ref",
        "refs/tags",
        "--format=%(refname)%00%(contents:subject)",
    )
    for line in raw.splitlines():
        fields = line.split("\x00", 1)
        if len(fields) != 2:
            continue
        name, subject = fields
        hits = scan_text(name) + scan_text(subject)
        if hits:
            findings.append((f"tag: {name}", hits))
    return findings


def _iter_history_blobs(root: Path) -> Iterator[tuple[str, bytes]]:
    """Yield (blob_sha, content) for every blob reachable from HEAD."""
    revs = _run_git(root, "rev-list", "--objects", "HEAD")
    shas = [line.split(" ", 1)[0] for line in revs.splitlines() if line]
    proc: subprocess.Popen[bytes] = subprocess.Popen(  # noqa: S603 # nosec B603
        [_git_exe(), "cat-file", "--batch"],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        cwd=root,
    )
    if proc.stdin is None or proc.stdout is None:
        proc.kill()
        raise RuntimeError("could not open git cat-file stream")
    try:
        for sha in shas:
            proc.stdin.write(sha.encode("ascii") + b"\n")
            proc.stdin.flush()
            header = proc.stdout.readline().rstrip(b"\n")
            if not header:
                break
            parts = header.split(b" ")
            if len(parts) != 3:
                break
            obj_type, size_raw = parts[1], parts[2]
            try:
                size = int(size_raw)
            except ValueError:
                break
            payload = proc.stdout.read(size)
            if len(payload) != size:
                break
            proc.stdout.read(1)
            if obj_type == b"blob":
                yield sha, payload
    finally:
        proc.stdin.close()
        proc.stdout.close()
        try:
            proc.terminate()
        except OSError:
            # process already exited; nothing to clean up
            pass
        proc.wait()


def scan(scope: str, root: Path | None = None) -> list[tuple[str, list[str]]]:
    """Run the requested scope and return (label, findings) pairs."""
    root = root or _git_root(Path.cwd())
    findings = scan_working_tree(root)
    findings += scan_commit_messages(root)
    findings += scan_tag_messages(root)
    if scope == "history":
        for sha, payload in _iter_history_blobs(root):
            hits = check_bytes(payload)
            if hits:
                findings.append((f"blob {sha}", hits))
    return findings


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="tc-sgb-mojibake",
        description="Scan repository text for UTF-8 corruption (mojibake).",
    )
    parser.add_argument(
        "--scope",
        choices=("head", "history"),
        default="head",
        help=(
            "head: tracked HEAD files plus commit/tag messages. "
            "history: also every blob reachable from HEAD (slower)."
        ),
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        findings = scan(args.scope)
    except (FileNotFoundError, subprocess.CalledProcessError) as exc:
        print(f"[mojibake] error: {exc}", file=sys.stderr)
        return 2
    if not findings:
        print(f"[mojibake] {args.scope} scope clean")
        return 0
    for label, hits in findings:
        for hit in hits:
            print(f"{label}: {hit}")
    print(f"[mojibake] {len(findings)} problem(s) in {args.scope} scope")
    return 1


if __name__ == "__main__":
    sys.exit(main())
