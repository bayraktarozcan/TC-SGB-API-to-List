"""Guards for canonical release titles and bilingual bodies."""

from __future__ import annotations

import re
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
BODIES = REPO_ROOT / ".github" / "release-bodies"
CHANGELOG = REPO_ROOT / "CHANGELOG.md"

TAGS = [
    "v0.3.2.2",
    "v0.3.2.1",
    "v0.3.2.0",
    "v0.3.1.0",
    "v0.3.0.0",
    "ioc-data",
    "v0.2.0.1",
    "v0.2.0.0",
    "v0.1.0.0",
]
LATEST = TAGS[0]
EN_SECTIONS = ["Summary", "Added", "Changed", "Removed", "Fixed", "Files", "Documentation"]
TR_SECTIONS = [
    "Özet",
    "Eklendi",
    "Değiştirilen",
    "Kaldırıldı",
    "Düzeltildi",
    "Dosyalar",
    "Belgelendirme",
]


class TestReleaseTitles:
    def test_every_release_has_canonical_title(self):
        for tag in TAGS:
            path = BODIES / f"{tag}.title"
            assert path.exists(), f"missing canonical title for {tag}"

    def test_tag_appears_once(self):
        for tag in TAGS:
            if tag == "ioc-data":
                continue
            title = (BODIES / f"{tag}.title").read_text(encoding="utf-8").strip()
            assert title.count(tag) == 1, f"{tag}: tag repeated in {title}"

    def test_deprecation_marker_is_a_prefix(self):
        for tag in TAGS:
            title = (BODIES / f"{tag}.title").read_text(encoding="utf-8").strip()
            if tag == LATEST or tag == "ioc-data":
                assert not title.startswith("[DEPRECATED]"), tag
            else:
                assert title.startswith(f"[DEPRECATED] {tag} — "), title

    def test_em_dash_separator(self):
        for tag in TAGS:
            if tag == "ioc-data":
                continue
            title = (BODIES / f"{tag}.title").read_text(encoding="utf-8").strip()
            assert " — " in title, title


class TestReleaseBodies:
    def test_every_release_has_canonical_body(self):
        for tag in TAGS:
            assert (BODIES / f"{tag}.md").exists(), f"missing body for {tag}"

    @pytest.mark.parametrize("tag", TAGS)
    def test_bilingual_sections_present(self, tag: str):
        body = (BODIES / f"{tag}.md").read_text(encoding="utf-8")
        en, tr = body.split('<a id="-türkçe"></a>', 1)
        for section in EN_SECTIONS:
            assert f"### {section}" in en, f"{tag}: EN {section}"
        for section in TR_SECTIONS:
            assert f"### {section}" in tr, f"{tag}: TR {section}"

    @pytest.mark.parametrize("tag", TAGS)
    def test_h1_in_each_half(self, tag: str):
        body = (BODIES / f"{tag}.md").read_text(encoding="utf-8")
        en, tr = body.split('<a id="-türkçe"></a>', 1)
        if tag == "ioc-data":
            assert re.search(r"^# TC-SGB-API-to-List IoC Data$", en, re.M)
            assert re.search(r"^# TC-SGB-API-to-List IoC Verisi$", tr, re.M)
        else:
            assert re.search(r"^# TC-SGB-API-to-List " + re.escape(tag) + r"$", en, re.M)
            assert re.search(r"^# TC-SGB-API-to-List " + re.escape(tag) + r"$", tr, re.M)

    @pytest.mark.parametrize("tag", TAGS)
    def test_no_bare_issue_tokens(self, tag: str):
        body = (BODIES / f"{tag}.md").read_text(encoding="utf-8")
        assert not re.findall(r"(?<![\w/])#\d+\b", body), f"{tag}: bare #N token"

    @pytest.mark.parametrize("tag", [t for t in TAGS if t != "ioc-data"])
    def test_changelog_bullets_are_covered(self, tag: str):
        changelog = CHANGELOG.read_text(encoding="utf-8").split('<a id="-türkçe"></a>')[0]
        section = changelog.split(f"## [{tag}]", 1)[1].split("\n## [", 1)[0]
        source_bullets = [
            line[2:].strip() for line in section.splitlines() if line.startswith("- ")
        ]
        body = (BODIES / f"{tag}.md").read_text(encoding="utf-8")
        for bullet in source_bullets:
            key = re.sub(r"\s+", " ", re.sub(r"\s*\(?#\d+\)?", "", bullet)).strip().rstrip(" .")
            assert key[:40] in body, f"{tag}: bullet not represented: {key[:60]}"

    @pytest.mark.parametrize("tag", TAGS)
    def test_equal_bullet_counts(self, tag: str):
        body = (BODIES / f"{tag}.md").read_text(encoding="utf-8")
        en, tr = body.split('<a id="-türkçe"></a>', 1)
        assert en.count("\n- ") == tr.count("\n- "), f"{tag}: EN/TR bullet counts differ"
