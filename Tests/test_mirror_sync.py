"""Fixture suite for the mirror verifier (Scripts/verify_mirror.py).

Pins the verifier's behaviour on synthetic source/mirror pairs: the sync-sha
contract, every structural drift axis, the tolerated granularity, the ordered
action checklist, and an absent mirror. The real pair is exercised by running
the verifier itself, not from here.
"""

from __future__ import annotations

import re
from pathlib import Path

from Scripts.verify_mirror import (
    find_drift,
    main,
    marker_value,
    read_normalized,
    structure,
    sync_sha,
)

REPO_ROOT = Path(__file__).resolve().parent.parent
VERIFIER = REPO_ROOT / "Scripts" / "verify_mirror.py"

SOURCE = """
# Title

Intro paragraph.

## Rules

- first rule
- second rule
  - nested detail

## Checklist

- [ ] run `alpha`
- [ ] run `beta`

## Table

| A | B |
| --- | --- |
| 1 | 2 |

```bash
echo hi
```
"""

MIRROR = """
# Baslik

Giris paragrafi.

## Kurallar

- birinci kural
- ikinci kural
  - alt ayrinti

## Kontrol

- [ ] calistir `alpha`
- [ ] calistir `beta`

## Tablo

| A | B |
| --- | --- |
| 1 | 2 |

```bash
echo merhaba
```
"""

MARKER = "<!-- mirror-sync: sync-sha=0123456789abcdef0123456789abcdef01234567 -->"


def _body(text: str) -> str:
    return text.rstrip("\n") + "\n"


def _marker(value: str) -> str:
    return f"<!-- mirror-sync: sync-sha={value} -->\n"


def _write(tmp_path: Path, name: str, text: str) -> Path:
    path = tmp_path / name
    path.write_text(text, encoding="utf-8")
    return path


class TestSyncSha:
    def test_clean_pair_has_no_drift(self):
        assert find_drift(SOURCE, MIRROR) == []

    def test_marker_line_excluded_from_sha(self):
        assert sync_sha(SOURCE + MARKER + "\n") == sync_sha(SOURCE)

    def test_crlf_matches_lf(self):
        assert sync_sha(SOURCE.replace("\n", "\r\n")) == sync_sha(SOURCE)

    def test_bom_dropped(self, tmp_path: Path):
        plain = _write(tmp_path, "plain.md", SOURCE)
        marked = tmp_path / "bom.md"
        marked.write_bytes(b"\xef\xbb\xbf" + SOURCE.encode("utf-8"))
        assert read_normalized(marked) == read_normalized(plain)

    def test_prose_mention_of_marker_keyword_is_kept(self):
        prose = f"Remove the `mirror-sync` comment line, then hash.\n{SOURCE}"
        assert sync_sha(prose) != sync_sha(SOURCE)

    def test_marker_value_absent(self):
        assert marker_value(SOURCE) is None

    def test_marker_value_reads_comment(self):
        assert marker_value(f"{SOURCE}\n{MARKER}\n") == "0123456789abcdef0123456789abcdef01234567"

    def test_marker_value_ignores_prose(self):
        assert marker_value("mention of mirror-sync but no comment") is None


class TestStructure:
    def test_fenced_heading_is_not_a_heading(self):
        fenced = "```\n# not a heading\n```\n"
        assert structure(fenced).heading_depths == ()

    def test_nested_items_counted_not_compared(self):
        expanded = SOURCE.replace("- second rule\n", "- second rule\n  - more\n  - even\n")
        assert structure(expanded).nested_items > structure(SOURCE).nested_items
        assert find_drift(SOURCE, expanded) == []


class TestDriftAxes:
    def test_extra_section(self):
        found = find_drift(SOURCE, SOURCE + "\n## Extra\n")
        assert any("heading depth" in item for item in found)

    def test_deeper_heading(self):
        found = find_drift(SOURCE, SOURCE.replace("## Table", "### Table"))
        assert any("heading depth" in item for item in found)

    def test_removed_rule(self):
        found = find_drift(SOURCE, SOURCE.replace("- second rule\n", ""))
        assert any("top-level rules" in item for item in found)

    def test_added_code_fence(self):
        found = find_drift(SOURCE, SOURCE + "\n```\nextra\n```\n")
        assert any("code fences" in item for item in found)

    def test_extra_table_block(self):
        found = find_drift(SOURCE, SOURCE + "\n| C | D |\n| --- | --- |\n")
        assert any("table blocks" in item for item in found)

    def test_checklist_reorder(self):
        reordered = SOURCE.replace(
            "- [ ] run `alpha`\n- [ ] run `beta`\n", "- [ ] run `beta`\n- [ ] run `alpha`\n"
        )
        assert any("action checklist" in item for item in find_drift(SOURCE, reordered))

    def test_checklist_loss(self):
        dropped = SOURCE.replace("- [ ] run `beta`\n", "")
        assert any("action checklist" in item for item in find_drift(SOURCE, dropped))

    def test_checklist_anchor_drop(self):
        stripped = SOURCE.replace("run `beta`", "run beta")
        assert any("action checklist" in item for item in find_drift(SOURCE, stripped))


class TestToleratedGranularity:
    def test_checklist_rewording_kept(self):
        reworded = SOURCE.replace("run `alpha`", "please run `alpha` now")
        assert find_drift(SOURCE, reworded) == []

    def test_table_row_change_kept(self):
        assert find_drift(SOURCE, SOURCE.replace("| 1 | 2 |", "| 9 | 8 |")) == []

    def test_table_row_count_change_kept(self):
        assert find_drift(SOURCE, SOURCE.replace("| 1 | 2 |", "| 1 | 2 |\n| 3 | 4 |")) == []


class TestCli:
    def test_clean_pair_exit_zero(self, tmp_path: Path, capsys):
        value = sync_sha(_body(SOURCE))
        src = _write(tmp_path, "source.md", _body(SOURCE) + _marker(value))
        mir = _write(tmp_path, "mirror.md", _body(MIRROR) + _marker(value))
        assert main([str(src), str(mir)]) == 0
        out = capsys.readouterr().out
        assert f"sync-sha: {value}" in out
        assert "structure: clean" in out

    def test_drift_exit_one(self, tmp_path: Path, capsys):
        src = _write(tmp_path, "source.md", SOURCE)
        mir = _write(tmp_path, "mirror.md", SOURCE.replace("- second rule\n", ""))
        assert main([str(src), str(mir)]) == 1
        assert "drift:" in capsys.readouterr().out

    def test_stale_marker_exit_one(self, tmp_path: Path):
        src = _write(tmp_path, "source.md", SOURCE + MARKER + "\n")
        mir = _write(tmp_path, "mirror.md", MIRROR + MARKER + "\n")
        assert main([str(src), str(mir)]) == 1

    def test_missing_mirror_errors_without_flag(self, tmp_path: Path, capsys):
        src = _write(tmp_path, "source.md", SOURCE)
        assert main([str(src), str(tmp_path / "absent.md")]) == 2
        assert "error: mirror not found" in capsys.readouterr().err

    def test_missing_mirror_allowed_with_flag(self, tmp_path: Path, capsys):
        src = _write(tmp_path, "source.md", SOURCE)
        assert main([str(src), str(tmp_path / "absent.md"), "--allow-missing"]) == 0
        assert "allowed" in capsys.readouterr().out

    def test_missing_source_errors(self, tmp_path: Path):
        assert main([str(tmp_path / "absent.md"), str(tmp_path / "absent2.md")]) == 2


class TestNoHardcodedPath:
    def test_verifier_hardcodes_no_document_path(self):
        assert re.search(r"[A-Za-z0-9_-]+\.md", VERIFIER.read_text(encoding="utf-8")) is None
