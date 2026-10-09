"""Repository convention guards from the AGENTS.md project layer.

Each guard below pins one project-layer invariant (version parity, document
reachability, ignore-file compliance). Every guard was seen to fail during
development by planting the violation it exists to catch, then reverting.
"""

from __future__ import annotations

import re
import tomllib
from pathlib import Path
from typing import ClassVar

REPO_ROOT = Path(__file__).resolve().parent.parent


def _read(name: str) -> str:
    return (REPO_ROOT / name).read_text(encoding="utf-8")


class TestVersionParity:
    """pyproject.toml is the version oracle; all stated versions must match it."""

    def _oracle(self) -> str:
        data = tomllib.loads((REPO_ROOT / "pyproject.toml").read_bytes().decode("utf-8"))
        version = data["project"]["version"]
        assert re.fullmatch(r"\d+\.\d+\.\d+\.\d+", version), f"not four-part: {version}"
        return version

    def test_changelog_newest_matches_pyproject(self):
        version = self._oracle()
        headings = re.findall(r"^## \[v([0-9.]+)\]", _read("CHANGELOG.md"), re.MULTILINE)
        assert headings, "no version headings in CHANGELOG.md"
        assert headings[0] == version, f"CHANGELOG newest {headings[0]} != {version}"

    def test_wiki_quotes_match_pyproject(self):
        version = self._oracle()
        quotes = re.findall(
            r'^version = "([0-9.]+)"',
            _read("wiki/Repository-Structure.md"),
            re.MULTILINE,
        )
        assert len(quotes) >= 2, f"expected EN+TR quotes, found {quotes}"
        assert all(q == version for q in quotes), f"{quotes} != {version}"


class TestDocReachability:
    """Every tracked root document is linked from README.md."""

    ROOT_DOCS: ClassVar[list[str]] = [
        "AGENTS.md",
        "CHANGELOG.md",
        "CODE_OF_CONDUCT.md",
        "CODEOWNERS",
        "CONTRIBUTING.md",
        "LICENSE",
        "NOTICE",
        "PRIVACY.md",
        "RELEASE-NOTE-TEMPLATE.md",
        "SECURITY.md",
        "SUPPORT.md",
    ]
    # README.md is the hub itself (linked to by SUPPORT.md); self-link excluded.

    def test_every_root_doc_linked(self):
        readme = _read("README.md")
        missing = [
            doc for doc in self.ROOT_DOCS if f"]({doc})" not in readme and f"]({doc}#" not in readme
        ]
        assert not missing, f"root docs without README link: {missing}"

    def test_listed_docs_exist(self):
        for doc in self.ROOT_DOCS:
            assert (REPO_ROOT / doc).is_file(), f"missing root doc: {doc}"


class TestIgnoreCompliance:
    """Guard the marker re-include and scratch patterns in .gitignore."""

    def test_marker_reinclude_ordered(self):
        lines = _read(".gitignore").splitlines()
        idx_pattern = next(i for i, line in enumerate(lines) if line == "._*")
        idx_reinclude = next(i for i, line in enumerate(lines) if line == "!._dont_migrate_")
        assert idx_reinclude > idx_pattern, "re-include must follow the pattern it narrows"

    def test_scratch_pattern_present(self):
        assert "/scratch/" in _read(".gitignore").splitlines()

    def test_no_markers_in_tracked_tree(self):
        found = [
            p
            for p in REPO_ROOT.rglob("._dont_migrate_")
            if ".git" not in p.parts and ".venv" not in p.parts
        ]
        assert found == [], f"marker outside an ignored layer root: {found}"
