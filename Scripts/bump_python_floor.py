"""Resolve and bump the Python compatibility floor from the upstream PEP calendar.

The declared floor lives in ``pyproject.toml`` (``requires-python``) and is the
single source of truth. Upstream truth is the Python release calendar published
by the core team at https://peps.python.org/api/release-cycle.json.

Usage::

    python Scripts/bump_python_floor.py check
    python Scripts/bump_python_floor.py apply 3.12
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
import time
import urllib.request
from datetime import date
from pathlib import Path

from Scripts.verify_mirror import marker_value, sync_sha

PEPS_URL = "https://peps.python.org/api/release-cycle.json"
PLACEHOLDER = "\u00a7"
VERSION_RE = r"[0-9]+\.[0-9]+"

# Strict declarations must carry exactly the declared floor.
FLOOR_DECLARATIONS: dict[str, tuple[str, ...]] = {
    "pyproject.toml": (
        'requires-python = ">={old}"',
        'python_version = "{old}"',
        "wait for Python {old}+ baseline",
    ),
    ".github/workflows/ci.yml": ('python-version: ["{old}", "3.x"]',),
    ".gitlab-ci.yml": ('PYTHON_VERSION: "{old}"',),
    "AGENTS.md": ("Python `>={old}`",),
    "AGENTS-TR.md": ("Python `>={old}`",),
    "CONTRIBUTING.md": ("Python {old}+",),
    "Docs/Architecture.md": ("| Python         | {old}+    |",),
    "Docs/Home.md": (
        "| **Python Version** | {old}+ |",
        "| **Python Sürümü** | {old}+ |",
    ),
    "Docs/Performance-Strategy.md": ("Python: {old} (compat floor)",),
    "Docs/Publishing-Strategy.md": ('requires-python = ">={old}"',),
    "Docs/Repository-Structure.md": (
        'requires-python = ">={old}"',
        'python_version = "{old}"',
    ),
    "Docs/Troubleshooting.md": ("Python {old}\u2013",),
    "README.md": ("python-{old}+-blue", "Python {old}+"),
    "Site/index.html": ("Python {old}+",),
}

# Classifiers enumerate every supported version, so other versions are valid;
# the floor merely has to be present exactly once.
SUPPORTED_METADATA: dict[str, tuple[str, ...]] = {
    "pyproject.toml": ('"Programming Language :: Python :: {old}"',),
    "Docs/Publishing-Strategy.md": ('"Programming Language :: Python :: {old}"',),
}

REPLACEMENTS = {**FLOOR_DECLARATIONS, **SUPPORTED_METADATA}

MARKER_RE = re.compile(r"<!-- mirror-sync: sync-sha=[0-9a-fA-F]+ -->")
OPTIONAL_FILES = frozenset({"AGENTS-TR.md"})


def read_floor(root: Path) -> str:
    """Read the declared floor from pyproject.toml, the single source of truth."""
    text = (root / "pyproject.toml").read_text(encoding="utf-8")
    match = re.search(rf'requires-python = ">=({VERSION_RE})"', text)
    if match is None:
        raise ValueError("requires-python not found in pyproject.toml")
    return match.group(1)


def _version_key(version: str) -> tuple[int, ...]:
    return tuple(int(part) for part in version.split("."))


def resolve_floor(cycles: dict[str, dict[str, str]], today: date | None = None) -> str:
    """Return the oldest Python minor that is still supported upstream.

    A version counts as unsupported when the core team marks it end-of-life or
    when its scheduled EOL date has passed, whichever comes first. Reading both
    signals keeps the result correct if the status field lags the schedule.
    """
    today = today or date.today()
    supported = []
    for version, detail in cycles.items():
        if detail.get("status") == "end-of-life":
            continue
        eol_raw = detail.get("end_of_life", "")
        eol_match = re.match(r"(\d{4})-(\d{2})", eol_raw)
        if eol_match:
            year, month = int(eol_match.group(1)), int(eol_match.group(2))
            eol = date(year + (month == 12), 1 if month == 12 else month + 1, 1)
            if eol <= today:
                continue
        supported.append(version)
    if not supported:
        raise ValueError("no supported Python version in the release calendar")
    return min(supported, key=_version_key)


def fetch_cycles(attempts: int = 3) -> dict[str, dict[str, str]]:
    """Fetch the trusted release calendar with bounded retries for transient failures."""
    last_error: Exception | None = None
    for attempt in range(1, attempts + 1):
        try:
            # Fixed, trusted HTTPS URL from the Python core team; no caller input.
            with urllib.request.urlopen(PEPS_URL, timeout=30) as response:  # nosec B310
                data = json.load(response)
            if not isinstance(data, dict) or len(data) < 10:
                raise ValueError("release calendar looks incomplete")
            return data
        except (OSError, ValueError, json.JSONDecodeError) as exc:
            last_error = exc
            if attempt < attempts:
                time.sleep(2**attempt)
    raise RuntimeError(f"could not fetch {PEPS_URL} after {attempts} attempts") from last_error


def _render(template: str, version: str) -> str:
    return template.replace("{old}", version)


def _pattern(template: str) -> re.Pattern[str]:
    escaped = re.escape(_render(template, PLACEHOLDER))
    return re.compile(escaped.replace(re.escape(PLACEHOLDER), f"({VERSION_RE})"))


def find_drift(root: Path) -> list[str]:
    """Return human-readable mismatches between the declared floor and its copies."""
    floor = read_floor(root)
    problems: list[str] = []
    for name, templates in FLOOR_DECLARATIONS.items():
        path = root / name
        if not path.exists():
            if name not in OPTIONAL_FILES:
                problems.append(f"{name}: missing file")
            continue
        text = path.read_bytes().decode("utf-8")
        for template in templates:
            matches = _pattern(template).findall(text)
            if not matches:
                problems.append(f"{name}: missing declaration {_render(template, floor)!r}")
            elif any(version != floor for version in matches):
                problems.append(
                    f"{name}: {template!r} uses {sorted(set(matches))}, expected {floor}"
                )
    for name, templates in SUPPORTED_METADATA.items():
        path = root / name
        if not path.exists():
            if name not in OPTIONAL_FILES:
                problems.append(f"{name}: missing file")
            continue
        text = path.read_bytes().decode("utf-8")
        for template in templates:
            if _render(template, floor) not in text:
                problems.append(f"{name}: missing metadata {_render(template, floor)!r}")
    return problems


def apply_bump(root: Path, old: str, new: str) -> list[str]:
    """Apply the floor change to every declaration; return the changed paths."""
    changed: list[str] = []
    for name, templates in FLOOR_DECLARATIONS.items():
        path = root / name
        if not path.exists():
            continue
        original = path.read_bytes().decode("utf-8")
        updated = original
        for template in templates:
            updated = updated.replace(_render(template, old), _render(template, new))
        if updated != original:
            path.write_bytes(updated.encode("utf-8"))
            changed.append(name)
    for name, templates in SUPPORTED_METADATA.items():
        path = root / name
        if not path.exists():
            continue
        original = path.read_bytes().decode("utf-8")
        updated = original
        for template in templates:
            old_line = _render(template, old)
            new_line = _render(template, new)
            if new_line in updated:
                updated = "\n".join(
                    line
                    for line in updated.split("\n")
                    if line.strip().rstrip(",") != old_line.strip().rstrip(",")
                )
            else:
                updated = updated.replace(old_line, new_line)
        if updated != original:
            path.write_bytes(updated.encode("utf-8"))
            if name not in changed:
                changed.append(name)
    if "AGENTS.md" in changed or "AGENTS-TR.md" in changed:
        refresh_mirror_marker(root)
    return changed


def refresh_mirror_marker(root: Path) -> None:
    """Recompute the mirror marker after a source-side edit, never by copying one side."""
    source = root / "AGENTS.md"
    mirror = root / "AGENTS-TR.md"
    if not (source.exists() and mirror.exists()):
        return
    sha = sync_sha(source.read_bytes().decode("utf-8"))
    for path in (source, mirror):
        original = path.read_bytes().decode("utf-8")
        if marker_value(original) == sha:
            continue
        updated = MARKER_RE.sub(f"<!-- mirror-sync: sync-sha={sha} -->", original)
        if updated != original:
            path.write_bytes(updated.encode("utf-8"))


def _check(root: Path) -> int:
    current = read_floor(root)
    desired = resolve_floor(fetch_cycles())
    if _version_key(desired) < _version_key(current):
        print(
            f"upstream floor {desired} is below declared {current}; refusing to downgrade",
            file=sys.stderr,
        )
        desired = current
    changed = desired != current
    output = {
        "desired": desired,
        "current": current,
        "changed": "true" if changed else "false",
    }
    for key, value in output.items():
        print(f"{key}={value}")
    out_file = os.environ.get("GITHUB_OUTPUT")
    if out_file:
        with Path(out_file).open("a", encoding="utf-8") as handle:
            for key, value in output.items():
                handle.write(f"{key}={value}\n")
    problems = find_drift(root)
    if problems:
        print("floor parity problems:", file=sys.stderr)
        for problem in problems:
            print(f"  {problem}", file=sys.stderr)
        return 2
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("check", help="compare declared floor with upstream calendar")
    apply_parser = sub.add_parser("apply", help="bump the declared floor everywhere")
    apply_parser.add_argument("version", help="new floor, for example 3.12")
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[1]
    if args.command == "check":
        return _check(root)
    if re.fullmatch(VERSION_RE, args.version) is None:
        parser.error("version must look like 3.12")
    old = read_floor(root)
    changed = apply_bump(root, old, args.version)
    print(f"Python floor {old} -> {args.version}: {len(changed)} files updated")
    for name in changed:
        print(f"  {name}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
