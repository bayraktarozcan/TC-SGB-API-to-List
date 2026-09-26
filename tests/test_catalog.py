"""Tests for catalog/index generation (manifest.json + blocklists/*.json)."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from scripts.src.models import (
    ConnectionType,
    DescriptionCategory,
    IOCType,
    ScoredIOC,
    Source,
)
from scripts.src.outputs import (
    FORMAT_EXTENSIONS,
    FORMAT_REGISTRY,
    generate_all,
    write_catalog,
)

BASE = "https://github.com/owner/repo/releases/download/ioc-data"


@pytest.fixture
def scored_iocs() -> list[ScoredIOC]:
    return [
        ScoredIOC(
            value="evil-phish.com",
            ioc_type=IOCType.DOMAIN,
            desc=DescriptionCategory.PHISHING,
            source=Source.USOM,
            criticality_level=3,
            connectiontype=ConnectionType.PHISHING,
            quality_score=93.0,
            false_positive_risk="low",
        ),
        ScoredIOC(
            value="192.0.2.1",
            ioc_type=IOCType.IP,
            desc=DescriptionCategory.CYBER_ATTACK,
            source=Source.RSA,
            criticality_level=2,
            connectiontype=ConnectionType.APT_CNC,
            quality_score=88.0,
            false_positive_risk="low",
        ),
    ]


@pytest.fixture
def output_dir(temp_dir: Path, scored_iocs: list[ScoredIOC]) -> Path:
    out = temp_dir / "out"
    generate_all(scored_iocs, out)
    out.joinpath("raw_records.json").write_text("[]\n", encoding="utf-8")
    return out


def _expected_artifact_names() -> set[str]:
    names = {f"threat_intel_{fmt}{ext}" for fmt, ext in FORMAT_EXTENSIONS.items()}
    names.add("raw_records.json")
    return names


class TestWriteCatalog:
    def test_manifest_schema(self, output_dir: Path):
        manifest = write_catalog(output_dir, release_base_url=BASE)
        assert set(manifest) == {"formats"}
        assert set(manifest["formats"]) == _expected_artifact_names()
        for info in manifest["formats"].values():
            assert set(info) == {"bytes", "sha256"}
            assert len(info["sha256"]) == 64
            assert info["bytes"] > 0

    def test_manifest_file_is_deterministic(self, output_dir: Path):
        write_catalog(output_dir, release_base_url=BASE)
        first = output_dir.joinpath("manifest.json").read_bytes()
        write_catalog(output_dir, release_base_url=BASE)
        assert output_dir.joinpath("manifest.json").read_bytes() == first

    def test_blocklists_per_format_files(self, output_dir: Path):
        write_catalog(output_dir, release_base_url=BASE)
        bl = output_dir / "blocklists"
        assert (bl / "mikrotik.json").is_file()
        assert (bl / "raw_records.json").is_file()
        entry = json.loads((bl / "mikrotik.json").read_text(encoding="utf-8"))
        assert entry["format"] == "mikrotik"
        assert entry["file"] == "threat_intel_mikrotik.rsc"
        assert entry["extension"] == ".rsc"
        assert entry["title"]
        assert entry["release_tag"] == "ioc-data"
        assert entry["raw_url"] == f"{BASE}/threat_intel_mikrotik.rsc"
        assert len(entry["sha256"]) == 64

    def test_raw_records_entry(self, output_dir: Path):
        write_catalog(output_dir, release_base_url=BASE)
        entry = json.loads(
            (output_dir / "blocklists" / "raw_records.json").read_text(encoding="utf-8")
        )
        assert entry["format"] == "raw_records"
        assert entry["file"] == "raw_records.json"
        manifest = json.loads(output_dir.joinpath("manifest.json").read_text(encoding="utf-8"))
        assert entry["sha256"] == manifest["formats"]["raw_records.json"]["sha256"]

    def test_index_lists_all_artifacts_sorted(self, output_dir: Path):
        write_catalog(output_dir, release_base_url=BASE)
        index = json.loads((output_dir / "blocklists" / "index.json").read_text(encoding="utf-8"))
        assert index["registry_version"] == 1
        names = [entry["file"] for entry in index["artifacts"]]
        assert names == sorted(names)
        manifest = json.loads(output_dir.joinpath("manifest.json").read_text(encoding="utf-8"))
        assert set(names) == set(manifest["formats"])
        for entry in index["artifacts"]:
            assert entry["raw_url"] == f"{BASE}/{entry['file']}"

    def test_index_is_deterministic(self, output_dir: Path):
        write_catalog(output_dir, release_base_url=BASE)
        first = (output_dir / "blocklists" / "index.json").read_bytes()
        write_catalog(output_dir, release_base_url=BASE)
        assert (output_dir / "blocklists" / "index.json").read_bytes() == first

    def test_missing_artifacts_produce_empty_catalog(self, temp_dir: Path):
        out = temp_dir / "empty"
        write_catalog(out, release_base_url=BASE)
        manifest = json.loads(out.joinpath("manifest.json").read_text(encoding="utf-8"))
        assert manifest["formats"] == {}
        index = json.loads((out / "blocklists" / "index.json").read_text(encoding="utf-8"))
        assert index["artifacts"] == []

    def test_skips_directories_and_missing_raw(self, temp_dir: Path):
        out = temp_dir / "messy"
        out.mkdir()
        (out / "threat_intel_csv.csv").write_text("a,b\n", encoding="utf-8")
        (out / "threat_intel_ignore_dir").mkdir()
        write_catalog(out, release_base_url=BASE)
        formats = json.loads(out.joinpath("manifest.json").read_text(encoding="utf-8"))["formats"]
        assert set(formats) == {"threat_intel_csv.csv"}

    def test_base_url_explicit_wins(self, output_dir: Path):
        write_catalog(output_dir, release_base_url="https://cdn.example.com/dl")
        entry = json.loads((output_dir / "blocklists" / "csv.json").read_text(encoding="utf-8"))
        assert entry["raw_url"] == "https://cdn.example.com/dl/threat_intel_csv.csv"


class TestResolveBaseUrl:
    def test_env_var_overridden_by_explicit(self, output_dir: Path, monkeypatch):
        monkeypatch.setenv("TC_SGB_RELEASE_BASE_URL", "https://mirror.example.com/assets/")
        write_catalog(output_dir, release_base_url=BASE)
        entry = json.loads((output_dir / "blocklists" / "csv.json").read_text(encoding="utf-8"))
        assert entry["raw_url"] == f"{BASE}/threat_intel_csv.csv"

    def test_env_var_used_when_no_explicit(self, temp_dir: Path, monkeypatch):
        monkeypatch.setenv(
            "TC_SGB_RELEASE_BASE_URL",
            "https://mirror.example.com/as",
        )
        out = temp_dir / "env"
        out.mkdir()
        (out / "threat_intel_csv.csv").write_text("a\n", encoding="utf-8")
        write_catalog(out)
        entry = json.loads((out / "blocklists" / "csv.json").read_text(encoding="utf-8"))
        assert entry["raw_url"] == "https://mirror.example.com/as/threat_intel_csv.csv"

    def test_github_repository_env(self, temp_dir: Path, monkeypatch):
        monkeypatch.delenv("TC_SGB_RELEASE_BASE_URL", raising=False)
        monkeypatch.setenv("GITHUB_REPOSITORY", "acme/ioc-lists")
        out = temp_dir / "gh"
        out.mkdir()
        (out / "threat_intel_pihole.txt").write_text("x\n", encoding="utf-8")
        write_catalog(out)
        entry = json.loads((out / "blocklists" / "pihole.json").read_text(encoding="utf-8"))
        assert entry["raw_url"] == (
            "https://github.com/acme/ioc-lists/releases/download/ioc-data/threat_intel_pihole.txt"
        )

    def test_repo_fallback_default(self, temp_dir: Path, monkeypatch):
        monkeypatch.delenv("TC_SGB_RELEASE_BASE_URL", raising=False)
        monkeypatch.delenv("GITHUB_REPOSITORY", raising=False)
        out = temp_dir / "fallback"
        out.mkdir()
        (out / "threat_intel_nextdns.txt").write_text("x\n", encoding="utf-8")
        write_catalog(out)
        entry = json.loads((out / "blocklists" / "nextdns.json").read_text(encoding="utf-8"))
        assert entry["raw_url"] == (
            "https://github.com/bayraktarozcan/TC-SGB-API-to-List/releases/download/"
            "ioc-data/threat_intel_nextdns.txt"
        )

    def test_release_tag_custom(self, temp_dir: Path):
        out = temp_dir / "tagged"
        out.mkdir()
        (out / "threat_intel_pihole.txt").write_text("x\n", encoding="utf-8")
        write_catalog(out, release_tag="v2", release_base_url="https://ex.com/dl")
        entry = json.loads((out / "blocklists" / "pihole.json").read_text(encoding="utf-8"))
        assert entry["release_tag"] == "v2"
        assert entry["raw_url"] == "https://ex.com/dl/threat_intel_pihole.txt"


class TestCatalogAgainstRegistry:
    def test_extensions_cover_all_formats(self):
        assert set(FORMAT_EXTENSIONS) == set(FORMAT_REGISTRY)

    def test_each_extension_startswith_dot(self):
        assert all(ext.startswith(".") for ext in FORMAT_EXTENSIONS.values())

    def test_titles_cover_all_formats(self):
        from scripts.src.outputs import FORMAT_TITLES

        assert set(FORMAT_TITLES) >= set(FORMAT_REGISTRY) | {"raw_records"}
