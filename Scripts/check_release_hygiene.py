"""Audit published releases on every host from the canonical CHANGELOG."""

from __future__ import annotations

import json
import os
import re
import subprocess  # nosec B404
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
GH_REPO = "bayraktarozcan/TC-SGB-API-to-List"
GL_PROJECT = "86517312"

EN_SECTIONS = {"Summary", "Added", "Changed", "Removed", "Fixed", "Files", "Documentation"}
TR_SECTIONS = {
    "Özet",
    "Eklendi",
    "Değiştirilen",
    "Kaldırıldı",
    "Düzeltildi",
    "Dosyalar",
    "Belgelendirme",
}


def norm(value: str) -> str:
    return value.replace("\r\n", "\n").replace("\r", "\n").strip()


def current_version() -> str:
    text = (ROOT / "pyproject.toml").read_text(encoding="utf-8")
    match = re.search(r'^version = "(\d+\.\d+\.\d+\.\d+)"', text, re.MULTILINE)
    if not match:
        raise SystemExit("version not found in pyproject.toml")
    return "v" + match.group(1)


def releases() -> tuple[dict[str, dict[str, str]], dict[str, dict[str, str]]]:
    gh_raw = subprocess.run(  # noqa: S603  # nosec B603, B607
        ["gh", "api", "--paginate", f"repos/{GH_REPO}/releases"],  # noqa: S607  # nosec B607
        capture_output=True,
        text=True,
        encoding="utf-8",
        check=True,
    ).stdout
    gh = {r["tag_name"]: r for r in json.loads(gh_raw)}
    token = os.environ.get("GITLAB_PUSH_TOKEN", "")
    if token:
        request = urllib.request.Request(
            f"https://gitlab.com/api/v4/projects/{GL_PROJECT}/releases?per_page=100",
            headers={"PRIVATE-TOKEN": token},
        )
        with urllib.request.urlopen(request, timeout=30) as response:  # nosec B310  # noqa: S310
            gl_data = json.load(response)
    else:
        gl_data = json.loads(
            subprocess.run(  # noqa: S603  # nosec B603, B607
                ["glab", "api", f"projects/{GL_PROJECT}/releases"],  # noqa: S607  # nosec B607
                capture_output=True,
                text=True,
                encoding="utf-8",
                check=True,
            ).stdout
        )
    gl = {r["tag_name"]: r for r in gl_data}
    return gh, gl


def check() -> list[str]:
    failures: list[str] = []
    gh, gl = releases()
    latest = current_version()
    if set(gh) != set(gl):
        failures.append(f"pair-count: GH {sorted(gh)} != GL {sorted(gl)}")
    else:
        print(f"PASS pair-count: {len(gh)} releases on both hosts")

    bad_titles = []
    for tag, record in gh.items():
        title = record["name"]
        if tag == "ioc-data":
            if title != "IoC Data (Large Formats)":
                bad_titles.append(f"{tag}: unexpected rolling title: {title}")
            continue
        if not re.fullmatch(r"(?:\[DEPRECATED\] )?" + re.escape(tag) + r" — \S.*", title):
            bad_titles.append(f"{tag}: bad format: {title}")
        elif tag != latest and not title.startswith("[DEPRECATED] "):
            bad_titles.append(f"{tag}: missing prefix")
        elif tag == latest and "[DEPRECATED]" in title:
            bad_titles.append(f"{tag}: current marked deprecated")
        elif title.count(tag) != 1:
            bad_titles.append(f"{tag}: tag repeated {title.count(tag)} times")
    if bad_titles:
        failures.append("title-format: " + ", ".join(bad_titles))
    else:
        print("PASS title-format: all titles canonical")

    bad_bodies = []
    garbage = []
    for tag, record in gh.items():
        body = record.get("body") or ""
        anchor = '<a id="-türkçe"></a>'
        if anchor not in body:
            bad_bodies.append(f"{tag}: no bilingual anchor")
            continue
        en, tr = body.split(anchor, 1)
        missing = [h for h in EN_SECTIONS if f"### {h}" not in en]
        missing += [h for h in TR_SECTIONS if f"### {h}" not in tr]
        if missing:
            bad_bodies.append(f"{tag}: missing {missing}")
        if re.search(r"(?<![\w/])#\d+\b", body):
            garbage.append(f"{tag}: bare #N")
        if "Table of Contents" in body or "İçindekiler" in body:
            garbage.append(f"{tag}: embedded TOC")
        for other in gh:
            if other != tag and f"# TC-SGB-API-to-List {other}\n" in body:
                garbage.append(f"{tag}: other version heading")
    if bad_bodies:
        failures.append("body-structure: " + ", ".join(bad_bodies))
    else:
        print("PASS body-structure: bilingual sections present")
    if garbage:
        failures.append("no-garbage: " + ", ".join(garbage))
    else:
        print("PASS no-garbage: no bare #N, TOC or foreign headings")

    mismatches = []
    for tag, record in gh.items():
        gl_record = gl.get(tag)
        if gl_record is None:
            continue
        if norm(record["name"]) != norm(gl_record["name"]):
            mismatches.append(f"{tag}: title")
        if norm(record.get("body") or "") != norm(gl_record.get("description") or ""):
            mismatches.append(f"{tag}: body")
    if mismatches:
        failures.append("cross-host: " + ", ".join(mismatches))
    else:
        print("PASS cross-host: titles and bodies byte-identical after LF normalization")
    return failures


def main() -> int:
    failures = check()
    for failure in failures:
        print(f"FAIL {failure}")
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
