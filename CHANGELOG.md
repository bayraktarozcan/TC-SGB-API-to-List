# Changelog / Değişiklik Günlüğü

All notable changes to this project will be documented in this file.
The format is based on [Keep a Changelog](https://keepachangelog.com/).

Bu dosya, projedeki tüm dikkat çekici değişiklikleri belgeleyecektir.
Format, [Keep a Changelog](https://keepachangelog.com/)'a dayanmaktadır.

## [Unreleased]

### Added / Eklenen

- Full pipeline: fetch, validate, normalize, dedup, score, output (16+ formats)
- Async API client with retry and rate limiting
- Pydantic data models for IOC validation
- Quality scoring system for IOC reliability assessment
- Output formats: NextDNS, AdGuard, Pi-hole, dnsmasq, Unbound, RPZ, Technitium, MikroTik, nftables, ipset, Suricata, CrowdSec, CSV, JSON, YAML, SQLite
- Comprehensive test suite (330 tests)
- CI/CD with GitHub Actions (CI, scheduled pipeline, CodeQL)
- Bilingual documentation (English/Turkish)
- 17 detailed technical documentation files

### Changed / Değiştirilen

- Fixed badge URLs to use correct repository path
- Improved error handling in API client
- Split nftables IPv6/IPv4 into separate sets
- Split MikroTik IPv6/IPv4 into separate address-lists
- Fixed YAML type annotation in output generator
- Added RFC6761 reserved domain false-positive prevention
- Added `--max-records 0` support for unlimited fetch

### Fixed / Düzeltilen

- Broken `.venv` recreation with proper pyvenv.cfg
- Missing `pytest-asyncio` and `types-PyYAML` dependencies
- Dead entry point in pyproject.toml
- `.env.example` with correct SGB API settings
- httpx AsyncClient missing `follow_redirects`
- `test.com` false positive in validator

---

## [1.0.0] - 2025-01-01

### Added / Eklenen

- Initial release
- Core IOC pipeline (fetch → validate → normalize → dedup → score → output)
- 16+ output formats
- CLI interface with `fetch`, `generate`, `stats`, `validate`, `health` commands
- GitHub Actions CI/CD
- Comprehensive documentation
