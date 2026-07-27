# TC-SGB-API-to-List v{VERSION}

> **{HIGHLIGHT}**

---

## What's New

{FEATURES}

## Improvements

{IMPROVEMENTS}

## Bug Fixes

{BUG_FIXES}

## Breaking Changes

{BREAKING_CHANGES}

## Statistics

| Metric | Value |
|--------|-------|
| IOC Output Formats | 17 |
| Total IOCs Fetched | ~490,000 |
| Test Coverage | 330 tests passing |
| Type Safety | mypy clean |
| Lint | ruff clean |

## Installation

```bash
git clone https://github.com/bayraktarozcan/TC-SGB-API-to-List.git
cd TC-SGB-API-to-List
python -m venv .venv
.venv\Scripts\activate  # Windows
pip install -r requirements.txt
```

## Quick Start

```bash
python scripts/main.py fetch
python scripts/main.py generate --input output/raw_records.json
python scripts/main.py health
```

## Documentation

- [Wiki](https://github.com/bayraktarozcan/TC-SGB-API-to-List/wiki)
- [Architecture](https://github.com/bayraktarozcan/TC-SGB-API-to-List/wiki/Architecture)
- [API Analysis](https://github.com/bayraktarozcan/TC-SGB-API-to-List/wiki/API-Analysis)
- [Output Formats](https://github.com/bayraktarozcan/TC-SGB-API-to-List/wiki/Data-Flow)

---

**Full Changelog**: https://github.com/bayraktarozcan/TC-SGB-API-to-List/compare/{PREV_TAG}...v{VERSION}
