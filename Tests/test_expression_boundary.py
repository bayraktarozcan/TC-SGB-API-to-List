"""Tests for workflow expression boundaries.

Any ``${{ ... }}`` inside a ``run:`` block is shell text before it is a string,
so user-controlled values must reach it through ``env:``. Constants such as
``github.repository`` and ``github.run_id`` are allowed; PR titles, head refs
and issue bodies are not.
"""

from __future__ import annotations

import re
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
WORKFLOWS = REPO_ROOT / ".github" / "workflows"

ALLOWED = (
    "github.repository",
    "github.run_id",
    "github.event_name",
    "github.event.pull_request.number",
    "inputs.pr_number",
    "steps.pr.outputs.pr_number",
)
FORBIDDEN = (
    "github.event.pull_request.title",
    "github.event.issue.title",
    "github.event.pull_request.head.ref",
    "github.event.head_commit.message",
    "github.event.comment.body",
)


def _run_lines(path: Path) -> list[tuple[int, str]]:
    result: list[tuple[int, str]] = []
    in_run = False
    base = 0
    for lineno, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        stripped = line.lstrip()
        if re.match(r"(?:-\s*)?run:\s*[|>]-?", stripped):
            in_run = True
            base = len(line) - len(stripped)
            continue
        if in_run:
            if stripped and (len(line) - len(stripped)) <= base and not stripped.startswith("-"):
                in_run = False
                continue
            result.append((lineno, line))
    return result


def find_expressions() -> list[str]:
    bad: list[str] = []
    for path in sorted(WORKFLOWS.glob("*.yml")):
        for lineno, line in _run_lines(path):
            for expression in re.findall(r"\$\{\{\s*([^}]+?)\s*\}\}", line):
                if any(token in expression for token in FORBIDDEN):
                    bad.append(f"{path.name}:{lineno}: unsafe {expression}")
                elif not any(token in expression for token in ALLOWED):
                    bad.append(f"{path.name}:{lineno}: unclassified {expression}")
    return bad


def test_no_user_controlled_expressions_in_run_blocks():
    assert find_expressions() == []


def test_checker_flags_pr_title(tmp_path: Path):
    workflow = tmp_path / "x.yml"
    workflow.write_text(
        "jobs:\n  a:\n    steps:\n      - run: |\n"
        '          echo "${{ github.event.pull_request.title }}"\n',
        encoding="utf-8",
    )
    original = WORKFLOWS
    try:
        globals()["WORKFLOWS"] = tmp_path
        assert any("unsafe" in item for item in find_expressions())
    finally:
        globals()["WORKFLOWS"] = original
