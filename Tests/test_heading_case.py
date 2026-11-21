"""Tests for the heading title-case convention in tracked documentation."""

from __future__ import annotations

import re
import subprocess
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]

STOP = {
    "a",
    "an",
    "and",
    "as",
    "at",
    "but",
    "by",
    "for",
    "from",
    "in",
    "into",
    "nor",
    "of",
    "on",
    "onto",
    "or",
    "over",
    "per",
    "so",
    "than",
    "that",
    "the",
    "to",
    "up",
    "via",
    "with",
    "yet",
    "when",
    "before",
    "after",
    "ve",
    "veya",
    "ile",
    "için",
    "bir",
    "bu",
    "da",
    "de",
    "ya",
    "ki",
}
EXEMPT_HEADINGS = frozenset({"CHANGELOG.md"})
EXEMPT_NAMES = frozenset({"md", "yml", "yaml", "json", "py", "abc", "abcch", "ch", "ip"})
DOMAIN_RE = re.compile(r"\b[\w-]+\.(?:com|org|net|io|dev|ch|md)\b", re.IGNORECASE)


def _tracked_markdown() -> list[str]:
    out = subprocess.run(
        ["git", "ls-files", "-z", "*.md"],  # noqa: S607
        cwd=REPO_ROOT,
        capture_output=True,
        check=True,
    )
    return [name for name in out.stdout.decode("utf-8").split("\0") if name]


def _strip(text: str) -> str:
    text = re.sub(r"`[^`]*`", " ", text)
    text = re.sub(r"\[([^\]]*)\]\([^)]*\)", r"\1", text)
    text = re.sub(r"<[^>]+>", " ", text)
    text = re.sub(r'"[^"]*"', " ", text)  # quoted exact output
    text = re.sub(r"[\w-]+\.[\w-]+", " ", text)  # domains and filenames
    text = re.sub(r"\bv\d+(?:\.\w+)+\b", " ", text)  # version tags like v1.x
    return re.sub(r"^\s*#+\s*", "", text).strip()


def find_violations(root: Path = REPO_ROOT, names: list[str] | None = None) -> list[str]:
    bad: list[str] = []
    for name in names if names is not None else _tracked_markdown():
        if name in EXEMPT_HEADINGS or name.startswith(".github/release-bodies/"):
            continue
        path = root / name
        if not path.is_file():
            continue
        in_fence = False
        for lineno, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
            if line.lstrip().startswith("```"):
                in_fence = not in_fence
                continue
            if in_fence or not line.startswith("#"):
                continue
            heading = _strip(line)
            for match in re.finditer(r"[^\W\d_][\w'’\-]*", heading, re.UNICODE):
                word = match.group(0)
                low = word.lower()
                if not word[0].islower() or low in STOP:
                    continue
                if low in EXEMPT_NAMES or DOMAIN_RE.match(word):
                    continue
                if low.startswith(("v", "py")) and any(c.isdigit() for c in word):
                    continue
                bad.append(f"{name}:{lineno}:{word}")
    return bad


def test_all_headings_use_title_case():
    assert find_violations() == []


def test_checker_flags_lowercase_heading(tmp_path: Path):
    planted = tmp_path / "x.md"
    planted.write_text("## lowercase Heading\n", encoding="utf-8")
    assert find_violations(tmp_path, ["x.md"]) == ["x.md:1:lowercase"]
