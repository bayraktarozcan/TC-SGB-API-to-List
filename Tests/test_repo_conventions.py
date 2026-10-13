"""Repository convention guards from the AGENTS.md project layer.

Each guard below pins one project-layer invariant (version parity, document
reachability, ignore-file compliance, spelling). Every guard was seen to fail during
development by planting the violation it exists to catch, then reverting.
"""

from __future__ import annotations

import re
import shutil
import subprocess
import tomllib
from pathlib import Path
from typing import ClassVar

REPO_ROOT = Path(__file__).resolve().parent.parent


def _read(name: str) -> str:
    return (REPO_ROOT / name).read_text(encoding="utf-8")


EXEMPT_FILES: dict[str, str] = {
    "CHANGELOG.md": "<!-- guard-exempt: historical-record -->",
    "AGENTS.md": "<!-- guard-exempt: rule-quotation -->",
}
"""Files exempt from spelling/rename guards, each with its scoped marker.

CHANGELOG.md is the historical record; AGENTS.md must quote the banned
spelling to forbid it. _tracked_text_files skips exactly these files, and
TestExemptMarkers proves each declared marker is still present.
"""


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
            _read("Docs/Repository-Structure.md"),
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


def _tracked_text_files() -> dict[str, str]:
    git = shutil.which("git")
    assert git is not None, "git is required for repo-convention guards"
    out = subprocess.run([git, "ls-files", "-z"], cwd=REPO_ROOT, capture_output=True, check=True)
    files: dict[str, str] = {}
    for rel in out.stdout.decode("utf-8").split("\0"):
        if not rel or rel in EXEMPT_FILES:
            continue
        try:
            raw = (REPO_ROOT / rel).read_bytes()
        except OSError:
            continue
        if b"\x00" in raw[:8192]:
            continue
        try:
            files[rel] = raw.decode("utf-8")
        except UnicodeError:
            continue
    return files


class TestRenameGuards:
    """No live file references a retired spelling; new spellings are present.

    Old spellings are stored split so this file never names them contiguously
    (else it would report itself). Exempt files are declared once in
    EXEMPT_FILES with a scoped in-file marker (see TestExemptMarkers).
    """

    RENAMED: ClassVar[list[tuple[tuple[str, str], str]]] = [
        (("script", "s/"), "Scripts/"),
        (("script", "s."), "Scripts."),
        (("test", "s/"), "Tests/"),
        (("wik", "i/"), "Docs/"),
        (("doc", "s/"), "Site/"),
        (("dat", "a/"), "Data/"),
        (("outpu", "t/"), "Output/"),
        (("benchmar", "k/"), "Benchmark/"),
        (("example", "s/"), "Examples/"),
        (("schem", "a/"), "Schema/"),
        (("blocklist", "s/"), "Blocklists/"),
        (("_Sidebar", ".md"), "Sidebar.md"),
        (("_Footer", ".md"), "Footer.md"),
    ]

    @classmethod
    def _find(cls, mapping: list[tuple[tuple[str, str], str]], files: dict[str, str]) -> list[str]:
        bad: list[str] = []
        for rel, text in sorted(files.items()):
            for (head, tail), _new in mapping:
                pat = re.compile(r"(?<![A-Za-z0-9_/-])" + re.escape(head + tail))
                if pat.search(text):
                    bad.append(f"{rel}: {head + tail}")
                    break
        return bad

    def test_no_retired_spellings(self):
        files = _tracked_text_files()
        assert files, "no tracked files found"
        assert self._find(self.RENAMED, files) == []

    def test_new_spellings_present(self):
        haystack = "\n".join(_tracked_text_files().values())
        for _old, new in self.RENAMED:
            assert new in haystack, f"new spelling absent: {new}"
        for dirname in ("Scripts", "Tests", "Docs", "Site", "Data", "Output"):
            assert (REPO_ROOT / dirname).is_dir(), f"missing dir: {dirname}"

    def test_checker_flags_retired_spelling(self):
        mapping = [((("olddi", "r/")), "Newdir/")]
        assert self._find(mapping, {"x": "see olddir/file"}) == ["x: olddir/"]
        assert self._find(mapping, {"x": "see Newdir/file"}) == []


class TestIocSpelling:
    """IoC is the single standard spelling; the all-caps form appears nowhere live.

    Banned spellings are stored split so this file never names them
    contiguously (else it would report itself). Exempt files are declared
    once in EXEMPT_FILES with a scoped in-file marker (see TestExemptMarkers).
    """

    BANNED: ClassVar[list[tuple[str, str]]] = [
        ("IO", "C"),
        ("IO", "Cs"),
        ("IO", "CType"),
        ("ValidatedIO", "C"),
        ("NormalizedIO", "C"),
        ("ScoredIO", "C"),
    ]
    PRESENT: ClassVar[list[str]] = ["IoCType", "ValidatedIoC", "NormalizedIoC", "ScoredIoC"]

    @classmethod
    def _find(cls, banned: list[tuple[str, str]], files: dict[str, str]) -> list[str]:
        bad: list[str] = []
        for rel, text in sorted(files.items()):
            for head, tail in banned:
                full = head + tail
                pat = re.compile(r"(?<![A-Za-z0-9_])" + re.escape(full) + r"(?![A-Za-z0-9_])")
                if pat.search(text):
                    bad.append(f"{rel}: {full}")
                    break
        return bad

    def test_no_banned_spellings(self):
        files = _tracked_text_files()
        assert files, "no tracked files found"
        assert self._find(self.BANNED, files) == []

    def test_new_spellings_present(self):
        haystack = "\n".join(_tracked_text_files().values())
        for new in self.PRESENT:
            assert new in haystack, f"new spelling absent: {new}"

    def test_checker_flags_banned_spelling(self):
        assert self._find([(("b", "ad"))], {"x": "see bad word"}) == ["x: bad"]
        assert self._find([(("b", "ad"))], {"x": "see good word"}) == []


class TestExemptMarkers:
    """Every guard exemption is a scoped in-file marker, and each one is present.

    A whole-file exclusion with no declaration would rot silently: the file
    could stop being historical (or stop quoting the rule) while the exclusion
    lives on. This test fails by name the moment a marker goes missing.
    """

    def test_markers_present(self):
        assert EXEMPT_FILES, "no exemptions declared"
        for rel, marker in EXEMPT_FILES.items():
            path = REPO_ROOT / rel
            assert path.is_file(), f"exempt file missing: {rel}"
            assert marker in path.read_text(encoding="utf-8"), f"exempt marker missing: {rel}"

    def test_exempt_files_skipped(self):
        assert all(rel not in _tracked_text_files() for rel in EXEMPT_FILES)
