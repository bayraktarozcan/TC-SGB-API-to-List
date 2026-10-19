"""Human-language mirror verifier.

Compares a source document against its translation mirror on two axes: the
reported ``sync-sha`` value and document structure. Neither path is built in:
both arrive as command-line parameters, so this file names no specific mirror
and stays reusable. ``--allow-missing`` tolerates an absent mirror where it is
intentionally absent, such as CI.

Exit codes: 0 clean, 1 drift, 2 usage or state error.
"""

from __future__ import annotations

import argparse
import hashlib
import re
import sys
from collections.abc import Sequence
from dataclasses import dataclass
from pathlib import Path

MARKER_RE = re.compile(r"^<!--[ \t]*mirror-sync:[^\n]*-->\n?", re.MULTILINE)
SHA_RE = re.compile(r"sync-sha=([0-9a-fA-F]+)")
FENCE_RE = re.compile(r"^\s*```")
HEADING_RE = re.compile(r"^(#{1,6}) (.+?)\s*$")
TOP_RULE_RE = re.compile(r"^(?:[-*] \S|\d+\. \S)")
NESTED_ITEM_RE = re.compile(r"^\s+(?:[-*] \S|\d+\. \S)")
CHECKBOX_RE = re.compile(r"^\s*[-*] \[[ xX]\] ")
TABLE_ROW_RE = re.compile(r"^\|.*\|\s*$")
BACKTICK_RE = re.compile(r"`([^`]+)`")

STRUCTURE_NOTE = "note: structure and marker parity are proved; wording still needs a human read."


@dataclass(frozen=True)
class Structure:
    """Comparable shape of a document: counts and sequences, never wording."""

    heading_depths: tuple[int, ...]
    rules_per_section: tuple[int, ...]
    code_fences: int
    table_blocks: int
    checklist_tokens: tuple[str, ...]
    nested_items: int


@dataclass(frozen=True)
class Report:
    """Verifier outcome: the reported value, the drift list, and both shapes."""

    sha: str
    drift: list[str]
    source: Structure
    mirror: Structure


def _normalize(text: str) -> str:
    """Drop a leading BOM and normalize every CRLF and lone CR to LF."""
    return text.lstrip("\ufeff").replace("\r\n", "\n").replace("\r", "\n")


def read_normalized(path: Path) -> str:
    """Read a file as UTF-8, dropping a BOM and normalizing every line ending to LF."""
    return _normalize(path.read_bytes().decode("utf-8"))


def strip_marker(text: str) -> str:
    """Remove the whole mirror-sync marker line, terminator included."""
    return MARKER_RE.sub("", text)


def sync_sha(text: str) -> str:
    """SHA1 of the normalized, marker-stripped text, so one value fits any checkout."""
    payload = strip_marker(_normalize(text)).encode("utf-8")
    return hashlib.sha1(payload, usedforsecurity=False).hexdigest()


def marker_value(text: str) -> str | None:
    """The sync-sha recorded inside an HTML-comment marker, or None when absent."""
    for found in MARKER_RE.finditer(text):
        sha = SHA_RE.search(found.group(0))
        if sha:
            return sha.group(1).lower()
    return None


def structure(text: str) -> Structure:
    """Extract the comparable shape, skipping fenced code for headings and tables."""
    depths: list[int] = []
    rule_counts: list[int] = []
    tokens: list[str] = []
    fences = 0
    tables = 0
    nested = 0
    in_fence = False
    prev_table = False
    for line in text.split("\n"):
        if FENCE_RE.match(line):
            in_fence = not in_fence
            fences += 1
            continue
        if in_fence:
            continue
        heading = HEADING_RE.match(line)
        if heading:
            depths.append(len(heading.group(1)))
            rule_counts.append(0)
        elif TOP_RULE_RE.match(line):
            if rule_counts:
                rule_counts[-1] += 1
        elif NESTED_ITEM_RE.match(line):
            nested += 1
        if CHECKBOX_RE.match(line):
            anchor = BACKTICK_RE.search(line)
            tokens.append(anchor.group(1) if anchor else "")
        is_table = TABLE_ROW_RE.match(line) is not None
        if is_table and not prev_table:
            tables += 1
        prev_table = is_table
    return Structure(
        heading_depths=tuple(depths),
        rules_per_section=tuple(rule_counts),
        code_fences=fences,
        table_blocks=tables,
        checklist_tokens=tuple(tokens),
        nested_items=nested,
    )


def find_drift(source: str, mirror: str) -> list[str]:
    """Report every structural axis where the mirror departed from the source."""
    left, right = structure(source), structure(mirror)
    found: list[str] = []
    if left.heading_depths != right.heading_depths:
        found.append(
            f"heading depth sequence differs: {list(left.heading_depths)} vs "
            f"{list(right.heading_depths)}"
        )
    if left.rules_per_section != right.rules_per_section:
        found.append(
            f"top-level rules per section differ: {list(left.rules_per_section)} vs "
            f"{list(right.rules_per_section)}"
        )
    if left.code_fences != right.code_fences:
        found.append(f"code fences differ: {left.code_fences} vs {right.code_fences}")
    if left.table_blocks != right.table_blocks:
        found.append(f"table blocks differ: {left.table_blocks} vs {right.table_blocks}")
    if left.checklist_tokens != right.checklist_tokens:
        found.append(
            f"action checklist differs: {list(left.checklist_tokens)} vs "
            f"{list(right.checklist_tokens)}"
        )
    return found


def verify(source_path: Path, mirror_path: Path) -> Report:
    """Compare a source/mirror pair and return the reported value plus any drift."""
    source_text = read_normalized(source_path)
    mirror_text = read_normalized(mirror_path)
    reported = sync_sha(source_text)
    found = find_drift(source_text, mirror_text)
    for label, text in (("source", source_text), ("mirror", mirror_text)):
        if marker_value(text) != reported:
            found.append(f"{label} marker is {marker_value(text)}, expected {reported}")
    return Report(
        sha=reported,
        drift=found,
        source=structure(source_text),
        mirror=structure(mirror_text),
    )


def main(argv: Sequence[str] | None = None) -> int:
    """Run the verifier as a command, reporting the value to write into both markers."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source", type=Path)
    parser.add_argument("mirror", type=Path)
    parser.add_argument(
        "--allow-missing",
        action="store_true",
        help="treat an absent mirror as intentional rather than an error",
    )
    args = parser.parse_args(argv)

    if not args.source.is_file():
        print(f"error: source not found: {args.source}", file=sys.stderr)
        return 2
    if not args.mirror.is_file():
        if args.allow_missing:
            print(f"mirror absent ({args.mirror}); allowed, nothing to verify.")
            return 0
        print(f"error: mirror not found: {args.mirror}", file=sys.stderr)
        return 2

    report = verify(args.source, args.mirror)
    print(f"sync-sha: {report.sha}")
    print(
        f"nested sub-items (reported, not compared): "
        f"source={report.source.nested_items} mirror={report.mirror.nested_items}"
    )
    print(STRUCTURE_NOTE)
    if report.drift:
        for item in report.drift:
            print(f"drift: {item}")
        return 1
    print("structure: clean")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
