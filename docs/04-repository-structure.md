[English](#english) | [Türkçe](#turkish)

<a id="english"></a>

# Repository Structure

## Directory Tree

```
TC-SGB-API-to-List/
├── .github/
│   ├── workflows/
│   │   ├── ci.yml                  # Main CI pipeline
│   │   ├── release.yml             # Release automation
│   │   └── scheduled.yml           # Scheduled data fetch
│   └── dependabot.yml              # Dependency updates
│
├── src/
│   └── tc_sgb/
│       ├── __init__.py             # Package init, version
│       ├── __main__.py             # CLI entry point
│       ├── client.py               # API client (httpx)
│       ├── models.py               # Pydantic data models
│       ├── validator.py            # Input validation
│       ├── normalizer.py           # Data normalization
│       ├── deduplicator.py         # Deduplication engine
│       ├── quality.py              # Quality assurance
│       ├── outputs.py              # Output generation (16+ formats)
│       ├── pipeline.py             # Pipeline orchestrator
│       ├── config.py               # Configuration management
│       └── logging_config.py       # Structured logging setup
│
├── tests/
│   ├── __init__.py
│   ├── conftest.py                 # Shared fixtures
│   ├── unit/
│   │   ├── __init__.py
│   │   ├── test_client.py
│   │   ├── test_models.py
│   │   ├── test_validator.py
│   │   ├── test_normalizer.py
│   │   ├── test_deduplicator.py
│   │   ├── test_quality.py
│   │   ├── test_outputs.py
│   │   └── test_pipeline.py
│   ├── integration/
│   │   ├── __init__.py
│   │   ├── test_api_integration.py
│   │   ├── test_end_to_end.py
│   │   └── test_format_roundtrip.py
│   ├── regression/
│   │   ├── __init__.py
│   │   ├── snapshots/              # Snapshot test data
│   │   │   ├── expected_output.json
│   │   │   ├── expected_stix.json
│   │   │   └── expected_csv.csv
│   │   └── test_regression.py
│   ├── property/
│   │   ├── __init__.py
│   │   ├── test_normalization_properties.py
│   │   ├── test_dedup_properties.py
│   │   └── test_validation_properties.py
│   ├── fuzz/
│   │   ├── __init__.py
│   │   ├── fuzz_validator.py
│   │   ├── fuzz_normalizer.py
│   │   └── fuzz_client.py
│   └── performance/
│       ├── __init__.py
│       ├── benchmarks.py
│       └── test_throughput.py
│
├── config/
│   ├── default.yaml               # Default configuration
│   ├── production.yaml             # Production overrides
│   ├── whitelist.txt               # False positive whitelist
│   └── formats.yaml                # Output format configuration
│
├── output/                         # Generated output files
│   ├── json/
│   ├── csv/
│   ├── stix/
│   ├── misp/
│   ├── openioc/
│   ├── sigma/
│   ├── yara/
│   ├── cef/
│   ├── leef/
│   ├── syslog/
│   ├── html/
│   ├── markdown/
│   ├── pdf/
│   ├── splunk/
│   ├── qradar/
│   ├── elastic/
│   └── grafana/
│
├── docs/
│   ├── 01-architecture.md
│   ├── 02-data-flow.md
│   ├── 03-module-architecture.md
│   ├── 04-repository-structure.md
│   ├── 05-api-analysis.md
│   ├── 06-data-model.md
│   ├── 07-threat-model.md
│   ├── 08-security-analysis.md
│   ├── 09-license-analysis.md
│   ├── 10-test-strategy.md
│   ├── 11-regression-strategy.md
│   ├── 12-performance-strategy.md
│   ├── 13-versioning-strategy.md
│   ├── 14-publishing-strategy.md
│   ├── 15-maintenance-plan.md
│   ├── 16-risk-analysis.md
│   ├── 17-roadmap.md
│   └── LEGAL_NOTICES.md
│
├── scripts/
│   ├── fetch_iocs.py               # Standalone fetch script
│   ├── validate_outputs.py         # Output validation
│   └── generate_report.py          # Report generation
│
├── pyproject.toml                  # Project metadata & build config
├── README.md                       # Project overview
├── CHANGELOG.md                    # Version changelog
├── LICENSE                         # License file
├── SECURITY.md                     # Security policy
├── CONTRIBUTING.md                 # Contribution guidelines
└── .gitignore                      # Git ignore rules
```

## Key Files Description

### Source Code (`src/tc_sgb/`)

| File | Lines (est.) | Purpose |
|------|-------------|---------|
| `__init__.py` | ~20 | Package metadata, `__version__` |
| `__main__.py` | ~50 | CLI entry point (`python -m tc_sgb`) |
| `client.py` | ~250 | Async HTTP client with retry logic |
| `models.py` | ~300 | Pydantic models, enums, schemas |
| `validator.py` | ~400 | 12 validation rules, batch processing |
| `normalizer.py` | ~350 | Type-specific normalization transforms |
| `deduplicator.py` | ~300 | 3-level dedup strategy engine |
| `quality.py` | ~400 | Statistics, FP detection, scoring |
| `outputs.py` | ~800 | 16+ output format generators |
| `pipeline.py` | ~350 | End-to-end orchestration |
| `config.py` | ~150 | YAML config loading, validation |
| `logging_config.py` | ~80 | Structured JSON logging |

### Configuration (`config/`)

| File | Purpose |
|------|---------|
| `default.yaml` | Default pipeline settings |
| `production.yaml` | Production environment overrides |
| `whitelist.txt` | Known benign domains/IPs (one per line) |
| `formats.yaml` | Output format enable/disable and options |

### Tests (`tests/`)

| Directory | Count (est.) | Focus |
|-----------|-------------|-------|
| `unit/` | ~40 tests | Individual module testing |
| `integration/` | ~10 tests | API and end-to-end flows |
| `regression/` | ~15 tests | Snapshot and output stability |
| `property/` | ~20 tests | Invariant-based testing |
| `fuzz/` | ~5 tests | Crash and edge case discovery |
| `performance/` | ~8 tests | Throughput and latency benchmarks |

### Build & CI

| File | Purpose |
|------|---------|
| `pyproject.toml` | Package metadata, dependencies, tool config |
| `.github/workflows/ci.yml` | Lint, type check, test on PR |
| `.github/workflows/release.yml` | Build and publish on tag |
| `.github/workflows/scheduled.yml` | Daily automated data fetch |
| `.github/dependabot.yml` | Automated dependency updates |

## Module Import Graph

```python
# Top-level imports (pipeline.py)
from tc_sgb.client import SGBAPIClient
from tc_sgb.validator import IOCValidator
from tc_sgb.normalizer import IOCNormalizer
from tc_sgb.deduplicator import IOCDeduplicator
from tc_sgb.quality import QualityEngine
from tc_sgb.outputs import OutputEngine
from tc_sgb.models import IOCRecord, PipelineConfig
from tc_sgb.config import load_config

# client.py imports
import httpx
import asyncio
from tc_sgb.models import APIResponse, IOCRecord, ClientConfig

# models.py imports
from pydantic import BaseModel, Field, ConfigDict
from enum import Enum
from datetime import datetime

# validator.py imports
from tc_sgb.models import IOCRecord, ValidationError, ValidationConfig

# normalizer.py imports
from tc_sgb.models import NormalizedIOC, IOCType
import idna  # IDN/punycode
import ipaddress

# deduplicator.py imports
from tc_sgb.models import NormalizedIOC, DedupResult, DedupConfig
import hashlib

# quality.py imports
from tc_sgb.models import NormalizedIOC, QualityReport, QualityConfig

# outputs.py imports
from tc_sgb.models import NormalizedIOC, OutputFile, OutputConfig
import json
import csv
import orjson
from jinja2 import Template
```

## Build Configuration

```toml
# pyproject.toml
[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[project]
name = "tc-sgb-api-list"
version = "1.0.0"
description = "Turkish National Cyber Security Directorate IOC processor"
requires-python = ">=3.11"
license = "MIT"

[project.scripts]
tc-sgb = "tc_sgb.__main__:main"

[tool.pytest.ini_options]
testpaths = ["tests"]
asyncio_mode = "auto"

[tool.ruff]
target-version = "py311"
line-length = 100

[tool.mypy]
python_version = "3.11"
strict = true

[tool.coverage.run]
source = ["tc_sgb"]
branch = true
```

<a id="turkish"></a>

# Depo Yapısı

## Dizin Ağacı

```
TC-SGB-API-to-List/
├── .github/
│   ├── workflows/
│   │   ├── ci.yml                  # Ana CI hattı
│   │   ├── release.yml             # Sürüm otomasyonu
│   │   └── scheduled.yml           # Zamanlanmış veri çekme
│   └── dependabot.yml              # Bağımlılık güncellemeleri
│
├── src/
│   └── tc_sgb/
│       ├── __init__.py             # Paket başlatma, sürüm
│       ├── __main__.py             # CLI giriş noktası
│       ├── client.py               # API istemcisi (httpx)
│       ├── models.py               # Pydantic veri modelleri
│       ├── validator.py            # Girdi doğrulama
│       ├── normalizer.py           # Veri normalizasyonu
│       ├── deduplicator.py         # Tekilleştirme motoru
│       ├── quality.py              # Kalite güvencesi
│       ├── outputs.py              # Çıktı üretimi (16+ format)
│       ├── pipeline.py             # Boru hattı orkestratörü
│       ├── config.py               # Yapılandırma yönetimi
│       └── logging_config.py       # Yapılandırılmış günlük ayarı
│
├── tests/
│   ├── __init__.py
│   ├── conftest.py                 # Paylaşılan fixture'lar
│   ├── unit/
│   │   ├── __init__.py
│   │   ├── test_client.py
│   │   ├── test_models.py
│   │   ├── test_validator.py
│   │   ├── test_normalizer.py
│   │   ├── test_deduplicator.py
│   │   ├── test_quality.py
│   │   ├── test_outputs.py
│   │   └── test_pipeline.py
│   ├── integration/
│   │   ├── __init__.py
│   │   ├── test_api_integration.py
│   │   ├── test_end_to_end.py
│   │   └── test_format_roundtrip.py
│   ├── regression/
│   │   ├── __init__.py
│   │   ├── snapshots/              # Anlık görüntü test verileri
│   │   │   ├── expected_output.json
│   │   │   ├── expected_stix.json
│   │   │   └── expected_csv.csv
│   │   └── test_regression.py
│   ├── property/
│   │   ├── __init__.py
│   │   ├── test_normalization_properties.py
│   │   ├── test_dedup_properties.py
│   │   └── test_validation_properties.py
│   ├── fuzz/
│   │   ├── __init__.py
│   │   ├── fuzz_validator.py
│   │   ├── fuzz_normalizer.py
│   │   └── fuzz_client.py
│   └── performance/
│       ├── __init__.py
│       ├── benchmarks.py
│       └── test_throughput.py
│
├── config/
│   ├── default.yaml               # Varsayılan yapılandırma
│   ├── production.yaml             # Üretim ortamı geçersiz kılınmaları
│   ├── whitelist.txt               # Yanlış pozitif beyaz liste
│   └── formats.yaml                # Çıktı formatı yapılandırması
│
├── output/                         # Üretilen çıktı dosyaları
│   ├── json/
│   ├── csv/
│   ├── stix/
│   ├── misp/
│   ├── openioc/
│   ├── sigma/
│   ├── yara/
│   ├── cef/
│   ├── leef/
│   ├── syslog/
│   ├── html/
│   ├── markdown/
│   ├── pdf/
│   ├── splunk/
│   ├── qradar/
│   ├── elastic/
│   └── grafana/
│
├── docs/
│   ├── 01-architecture.md
│   ├── 02-data-flow.md
│   ├── 03-module-architecture.md
│   ├── 04-repository-structure.md
│   ├── 05-api-analysis.md
│   ├── 06-data-model.md
│   ├── 07-threat-model.md
│   ├── 08-security-analysis.md
│   ├── 09-license-analysis.md
│   ├── 10-test-strategy.md
│   ├── 11-regression-strategy.md
│   ├── 12-performance-strategy.md
│   ├── 13-versioning-strategy.md
│   ├── 14-publishing-strategy.md
│   ├── 15-maintenance-plan.md
│   ├── 16-risk-analysis.md
│   ├── 17-roadmap.md
│   └── LEGAL_NOTICES.md
│
├── scripts/
│   ├── fetch_iocs.py               # Bağımsız çekme betiği
│   ├── validate_outputs.py         # Çıktı doğrulama
│   └── generate_report.py          # Rapor üretimi
│
├── pyproject.toml                  # Proje meta verileri ve derleme yapılandırması
├── README.md                       # Proje genel bakışı
├── CHANGELOG.md                    # Sürüm değişiklik günlüğü
├── LICENSE                         # Lisans dosyası
├── SECURITY.md                     // Güvenlik politikası
├── CONTRIBUTING.md                 # Katkı yönergeleri
└── .gitignore                      # Git yok sayma kuralları
```

## Temel Dosya Açıklamaları

### Kaynak Kodu (`src/tc_sgb/`)

| Dosya | Satır (tahmini) | Amaç |
|-------|-----------------|------|
| `__init__.py` | ~20 | Paket meta verileri, `__version__` |
| `__main__.py` | ~50 | CLI giriş noktası (`python -m tc_sgb`) |
| `client.py` | ~250 | Yeniden deneme mantığı olan asenkron HTTP istemcisi |
| `models.py` | ~300 | Pydantic modelleri, enum'lar, şemalar |
| `validator.py` | ~400 | 12 doğrulama kuralı, toplu işleme |
| `normalizer.py` | ~350 | Türe özgü normalizasyon dönüşümleri |
| `deduplicator.py` | ~300 | 3 katmanlı tekilleştirme stratejisi motoru |
| `quality.py` | ~400 | İstatistikler, FP tespiti, puanlama |
| `outputs.py` | ~800 | 16+ çıktı formatı üreteçleri |
| `pipeline.py` | ~350 | Uçtan uca orkestrasyon |
| `config.py` | ~150 | YAML yapılandırma yükleme, doğrulama |
| `logging_config.py` | ~80 | Yapılandırılmış JSON günlük kaydı |

### Yapılandırma (`config/`)

| Dosya | Amaç |
|-------|------|
| `default.yaml` | Varsayılan boru hattı ayarları |
| `production.yaml` | Üretim ortamı geçersiz kılınmaları |
| `whitelist.txt` | Bilinen iyi niyetli alan adları/IP'ler satır başına bir tane |
| `formats.yaml` | Çıktı formatı etkinleştirme/devre dışı bırakma ve seçenekler |

### Testler (`tests/`)

| Dizin | Sayı (tahmini) | Odak |
|-------|----------------|------|
| `unit/` | ~40 test | Tekil modül testleri |
| `integration/` | ~10 test | API ve uçtan uca akışlar |
| `regression/` | ~15 test | Anlık görüntü ve çıktı kararlılığı |
| `property/` | ~20 test | İnvariant tabanlı testler |
| `fuzz/` | ~5 test | Çökme ve sınır durumu keşfi |
| `performance/` | ~8 test | Verimlilik ve gecikme ölçümleri |

### Derleme ve CI

| Dosya | Amaç |
|-------|------|
| `pyproject.toml` | Paket meta verileri, bağımlılıklar, araç yapılandırması |
| `.github/workflows/ci.yml` | PR üzerinde lint, tür kontrolü, test |
| `.github/workflows/release.yml` | Etiketleme üzerinde derleme ve yayımlama |
| `.github/workflows/scheduled.yml` | Günlük otomatik veri çekme |
| `.github/dependabot.yml` | Otomatik bağımlılık güncellemeleri |

## Modül İçe Aktarma Grafiği

```python
# Top-level imports (pipeline.py)
from tc_sgb.client import SGBAPIClient
from tc_sgb.validator import IOCValidator
from tc_sgb.normalizer import IOCNormalizer
from tc_sgb.deduplicator import IOCDeduplicator
from tc_sgb.quality import QualityEngine
from tc_sgb.outputs import OutputEngine
from tc_sgb.models import IOCRecord, PipelineConfig
from tc_sgb.config import load_config

# client.py imports
import httpx
import asyncio
from tc_sgb.models import APIResponse, IOCRecord, ClientConfig

# models.py imports
from pydantic import BaseModel, Field, ConfigDict
from enum import Enum
from datetime import datetime

# validator.py imports
from tc_sgb.models import IOCRecord, ValidationError, ValidationConfig

# normalizer.py imports
from tc_sgb.models import NormalizedIOC, IOCType
import idna  # IDN/punycode
import ipaddress

# deduplicator.py imports
from tc_sgb.models import NormalizedIOC, DedupResult, DedupConfig
import hashlib

# quality.py imports
from tc_sgb.models import NormalizedIOC, QualityReport, QualityConfig

# outputs.py imports
from tc_sgb.models import NormalizedIOC, OutputFile, OutputConfig
import json
import csv
import orjson
from jinja2 import Template
```

## Derleme Yapılandırması

```toml
# pyproject.toml
[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[project]
name = "tc-sgb-api-list"
version = "1.0.0"
description = "Turkish National Cyber Security Directorate IOC processor"
requires-python = ">=3.11"
license = "MIT"

[project.scripts]
tc-sgb = "tc_sgb.__main__:main"

[tool.pytest.ini_options]
testpaths = ["tests"]
asyncio_mode = "auto"

[tool.ruff]
target-version = "py311"
line-length = 100

[tool.mypy]
python_version = "3.11"
strict = true

[tool.coverage.run]
source = ["tc_sgb"]
branch = true
```
