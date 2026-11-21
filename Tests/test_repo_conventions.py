"""Repository convention guards from the AGENTS.md project layer.

Each guard below pins one project-layer invariant (version parity, document
reachability, ignore-file compliance, spelling, mirror sync). Every guard was seen
to fail during development by planting the violation it exists to catch, then
reverting.
"""

from __future__ import annotations

import re
import shutil
import subprocess
import tomllib
from pathlib import Path
from typing import ClassVar

import pytest

from Scripts.verify_mirror import find_drift, marker_value, read_normalized, sync_sha, verify

REPO_ROOT = Path(__file__).resolve().parent.parent


def _read(name: str) -> str:
    return (REPO_ROOT / name).read_text(encoding="utf-8")


EXEMPT_FILES: dict[str, str] = {
    "CHANGELOG.md": "<!-- guard-exempt: historical-record -->",
    "AGENTS.md": "<!-- guard-exempt: rule-quotation -->",
    ".github/release-bodies/ioc-data.md": "<!-- guard-exempt: historical-record -->",
    ".github/release-bodies/v0.1.0.0.md": "<!-- guard-exempt: historical-record -->",
    ".github/release-bodies/v0.2.0.0.md": "<!-- guard-exempt: historical-record -->",
    ".github/release-bodies/v0.2.0.1.md": "<!-- guard-exempt: historical-record -->",
    ".github/release-bodies/v0.3.0.0.md": "<!-- guard-exempt: historical-record -->",
    ".github/release-bodies/v0.3.1.0.md": "<!-- guard-exempt: historical-record -->",
    ".github/release-bodies/v0.3.2.0.md": "<!-- guard-exempt: historical-record -->",
    ".github/release-bodies/v0.3.2.1.md": "<!-- guard-exempt: historical-record -->",
    ".github/release-bodies/v0.3.2.2.md": "<!-- guard-exempt: historical-record -->",
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


class TestLineLength:
    """Every tracked Python file stays within 100 columns.

    Ruff's E501 forgives pragma-trailing lines, so this guard holds the
    project convention where the formatter cannot.
    """

    LIMIT = 100

    @classmethod
    def _find(cls, files: dict[str, str]) -> list[str]:
        bad: list[str] = []
        for rel, text in sorted(files.items()):
            if not rel.endswith(".py"):
                continue
            for lineno, line in enumerate(text.splitlines(), 1):
                if len(line) > cls.LIMIT:
                    bad.append(f"{rel}:{lineno}")
                    break
        return bad

    def test_no_long_lines(self):
        assert self._find(_tracked_text_files()) == []

    def test_checker_flags_long_line(self):
        assert self._find({"x.py": "ok\n" + "y" * 101 + "\n"}) == ["x.py:2"]
        assert self._find({"x.py": "ok\n"}) == []


class TestCaseCollision:
    """No two tracked paths may collide case-insensitively.

    `Output/Blocklists/` and `Output/blocklists/` coexisted once: on a
    case-insensitive checkout they share one directory, so one tree always
    reports phantom modifications and local rebase/merge stops working.
    """

    @classmethod
    def _find(cls, paths: list[str]) -> list[str]:
        seen: dict[str, str] = {}
        bad: list[str] = []
        for rel in sorted(paths):
            key = rel.casefold()
            if key in seen:
                bad.append(f"{seen[key]} collides with {rel}")
            else:
                seen[key] = rel
        return bad

    def test_no_case_collisions(self):
        git = shutil.which("git")
        assert git is not None, "git is required for repo-convention guards"
        out = subprocess.run(
            [git, "ls-files", "-z"], cwd=REPO_ROOT, capture_output=True, check=True
        )
        paths = [rel for rel in out.stdout.decode("utf-8").split("\0") if rel]
        assert self._find(paths) == []

    def test_checker_flags_collision(self):
        assert self._find(["Output/Blocklists/a.json", "Output/blocklists/a.json"]) != []
        assert self._find(["a/b.py"]) == []


class TestFinalNewline:
    """Every tracked text file ends with LF, even when nothing else edits it."""

    @staticmethod
    def _find(files: list[str]) -> list[str]:
        bad: list[str] = []
        for name in files:
            path = REPO_ROOT / name
            try:
                data = path.read_bytes()
            except OSError:
                continue
            if data and not data.endswith(b"\n"):
                bad.append(name)
        return bad

    def test_all_tracked_files_end_with_lf(self):
        out = subprocess.run(
            [shutil.which("git") or "git", "ls-files", "-z"],
            cwd=REPO_ROOT,
            capture_output=True,
            check=True,
        )
        files = [p for p in out.stdout.decode("utf-8").split("\0") if p]
        assert self._find(files) == []

    def test_checker_flags_missing_newline(self):
        planted = REPO_ROOT / "x.md"
        try:
            planted.write_bytes(b"body")
            assert self._find([planted.name]) == ["x.md"]
        finally:
            planted.unlink(missing_ok=True)


class TestActionRefs:
    """Third-party actions use a ref that exists upstream, never a guess.

    The map is local and deterministic so the gate never depends on the
    network. It records each upstream default branch read on 2026-11-21; a
    future upstream rename is a code change that updates this map.
    """

    DEFAULT_BRANCH: ClassVar[dict[str, str]] = {
        "actions/checkout": "main",
        "actions/setup-python": "main",
        "actions/upload-artifact": "main",
        "actions/configure-pages": "main",
        "actions/upload-pages-artifact": "main",
        "actions/deploy-pages": "main",
        "github/codeql-action/init": "main",
        "github/codeql-action/autobuild": "main",
        "github/codeql-action/analyze": "main",
        "lycheeverse/lychee-action": "master",
        "rhysd/actionlint": "main",
        "gitleaks/gitleaks-action": "master",
    }
    REF_RE = re.compile(r"^\s*(?:-\s*)?uses:\s*([^/\s]+/[^@\s]+)@([A-Za-z0-9._-]+)\s*(?:#.*)?$")
    PIN_PATTERNS: ClassVar[dict[str, re.Pattern[str]]] = {
        "pip pin": re.compile(r"==\s*\d"),
        "versioned ref": re.compile(r"@v\d"),
        "pinned image": re.compile(r"image:\s*[^\s]+:\d+\.\d+"),
        "image digest": re.compile(r"@sha256:"),
    }
    PIN_EXEMPT = re.compile(r"^\s*#|python-version:|PYTHON_VERSION:")
    SHA_RE = re.compile(r"^([0-9a-f]{40}|[0-9a-f]{64})$")
    MASTER_NOTE = "master, not main"

    @classmethod
    def _references(cls) -> list[tuple[str, str, str]]:
        found: list[tuple[str, str, str]] = []
        for path in sorted((REPO_ROOT / ".github").rglob("*.yml")):
            for line in path.read_text(encoding="utf-8").splitlines():
                match = cls.REF_RE.match(line)
                if match:
                    found.append((path.name, match.group(1), match.group(2)))
        return found

    @classmethod
    def _exception_docs(cls) -> list[str]:
        bad: list[str] = []
        for path in sorted((REPO_ROOT / ".github").rglob("*.yml")):
            lines = path.read_text(encoding="utf-8").splitlines()
            for lineno, line in enumerate(lines):
                if "@master" not in line:
                    continue
                nearby = " ".join(lines[max(0, lineno - 2) : lineno + 1])
                if cls.MASTER_NOTE not in nearby:
                    bad.append(f"{path.name}:{lineno + 1}: undocumented @master")
        return bad

    @classmethod
    def _find_pins(cls) -> list[str]:
        bad: list[str] = []
        paths = [*sorted((REPO_ROOT / ".github").rglob("*.yml")), REPO_ROOT / ".gitlab-ci.yml"]
        for path in paths:
            if not path.exists():
                continue
            for lineno, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
                if cls.PIN_EXEMPT.search(line):
                    continue
                for name, pattern in cls.PIN_PATTERNS.items():
                    if pattern.search(line):
                        bad.append(f"{path.name}:{lineno}: {name}")
        return bad

    @classmethod
    def _find(cls) -> list[str]:
        bad: list[str] = []
        for path in sorted((REPO_ROOT / ".github").rglob("*.yml")):
            for lineno, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
                match = cls.REF_RE.match(line)
                if not match:
                    continue
                action, ref = match.group(1), match.group(2)
                if action.startswith("./"):
                    continue
                expected = cls.DEFAULT_BRANCH.get(action)
                if expected is None:
                    bad.append(f"{path.name}:{lineno}: unlisted action {action}")
                elif ref != expected:
                    bad.append(f"{path.name}:{lineno}: {action}@{ref} != @{expected}")
        return bad

    def test_every_action_ref_matches_upstream_default(self):
        assert self._find() == []

    def test_ref_count_is_nonzero(self):
        assert len(self._references()) >= 10, "no action references inspected"

    def test_no_commit_sha_pins(self):
        shas = [
            f"{name}: {action}@{ref}"
            for name, action, ref in self._references()
            if self.SHA_RE.fullmatch(ref)
        ]
        assert shas == [], f"full-commit SHA pins: {shas}"

    def test_master_exceptions_are_documented(self):
        assert self._exception_docs() == []

    def test_no_pinned_tool_versions(self):
        assert self._find_pins() == []

    def test_checker_flags_pinned_tool(self):
        planted = "      pip install ruff==1.2.3\n"
        assert self.PIN_PATTERNS["pip pin"].search(planted) is not None
        assert self.PIN_EXEMPT.search(planted) is None

    def test_checker_flags_wrong_ref(self):
        line = "      - uses: lycheeverse/lychee-action@main"
        match = self.REF_RE.match(line)
        assert match is not None
        assert match.group(2) != self.DEFAULT_BRANCH[match.group(1)]

    def test_checker_flags_unlisted_action(self):
        assert self.REF_RE.match("      - uses: unknown/action@main") is not None


class TestMirrorPairGuards:
    """The AGENTS.md mirror contract verifies against the live documents.

    Marker self-agreement holds on every host, including CI; structure parity
    of the real AGENTS.md / AGENTS-TR.md pair runs the shipped verifier
    wherever the gitignored mirror exists, and skips where it does not.
    """

    def test_marker_matches_computed_sha(self):
        source = read_normalized(REPO_ROOT / "AGENTS.md")
        recorded = marker_value(source)
        assert recorded is not None, "AGENTS.md carries no mirror-sync marker"
        assert recorded == sync_sha(source), f"marker stale: {recorded}"

    def test_real_pair_verifies_when_present(self):
        mirror = REPO_ROOT / "AGENTS-TR.md"
        if not mirror.is_file():
            pytest.skip("AGENTS-TR.md absent (local-only layer); parity skipped")
        report = verify(REPO_ROOT / "AGENTS.md", mirror)
        assert report.drift == [], f"mirror drift: {report.drift}"

    def test_guard_detects_planted_drift(self):
        planted = "## A\n\n<!-- mirror-sync: sync-sha=cafe -->\n"
        assert marker_value(planted) == "cafe"
        assert marker_value("no marker here") is None
        assert find_drift("# A\n\n- rule\n", "# A\n") != []
