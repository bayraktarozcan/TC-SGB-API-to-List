> **Language / Dil** &nbsp;
> [EN English](#-english) &nbsp;·&nbsp; [TR Türkçe](#-türkçe)

<a id="-english"></a>

# Repository Structure

## Directory Tree

```
TC-SGB-API-to-List/
├── .github/
│   ├── workflows/
│   │   ├── ci.yml                  # Main CI pipeline
│   │   ├── release.yaml             # Release automation
│   │   └── scheduled.yml           # Scheduled data fetch
│   └── dependabot.yml              # Dependency updates
│
├── scripts/
│   ├── __init__.py                 # Package init
│   ├── main.py                     # CLI entry point
│   └── src/
│       ├── __init__.py             # Source package init
│       ├── client.py               # API client (httpx)
│       ├── models.py               # Pydantic data models
│       ├── validator.py            # Input validation
│       ├── normalizer.py           # Data normalization
│       ├── deduplicator.py         # Deduplication engine
│       ├── quality.py              # Quality assurance
│       ├── outputs.py              # Output generation (16+ formats)
│       └── pipeline.py             # Pipeline orchestrator
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
├── wiki/
│   ├── Architecture.md
│   ├── Data-Flow.md
│   ├── Module-Architecture.md
│   ├── Repository-Structure.md
│   ├── API-Analysis.md
│   ├── Data-Model.md
│   ├── Threat-Model.md
│   ├── Security-Analysis.md
│   ├── License-Analysis.md
│   ├── Test-Strategy.md
│   ├── Regression-Strategy.md
│   ├── Performance-Strategy.md
│   ├── Versioning-Strategy.md
│   ├── Publishing-Strategy.md
│   ├── Maintenance-Plan.md
│   ├── Risk-Analysis.md
│   ├── Roadmap.md
│   └── Legal-Notices.md
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

### Source Code (`scripts/src/`)

| File | Lines (est.) | Purpose |
|------|-------------|---------|
| `__init__.py` | ~5 | Package init |
| `client.py` | ~250 | Async HTTP client with retry logic |
| `models.py` | ~300 | Pydantic models, enums, schemas |
| `validator.py` | ~400 | 12 validation rules, batch processing |
| `normalizer.py` | ~350 | Type-specific normalization transforms |
| `deduplicator.py` | ~300 | 3-level dedup strategy engine |
| `quality.py` | ~400 | Statistics, FP detection, scoring |
| `outputs.py` | ~800 | 16+ output format generators |
| `pipeline.py` | ~350 | End-to-end orchestration |

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
| `.github/workflows/release.yaml` | Build and publish on tag |
| `.github/workflows/scheduled.yml` | Daily automated data fetch |
| `.github/dependabot.yml` | Automated dependency updates |

## Module Import Graph

```python
# Top-level imports (pipeline.py)
from scripts.src.client import SGBAPIClient
from scripts.src.validator import IOCValidator
from scripts.src.normalizer import IOCNormalizer
from scripts.src.deduplicator import IOCDeduplicator
from scripts.src.quality import QualityEngine
from scripts.src.outputs import OutputEngine
from scripts.src.models import IOCRecord, PipelineConfig

# client.py imports
import httpx
import asyncio
from scripts.src.models import APIResponse, IOCRecord, ClientConfig

# models.py imports
from pydantic import BaseModel, Field, ConfigDict
from enum import Enum
from datetime import datetime

# validator.py imports
from scripts.src.models import IOCRecord, ValidationError, ValidationConfig

# normalizer.py imports
from scripts.src.models import NormalizedIOC, IOCType
import ipaddress

# deduplicator.py imports
from scripts.src.models import NormalizedIOC, DedupResult, DedupConfig
import hashlib

# quality.py imports
from scripts.src.models import NormalizedIOC, QualityReport, QualityConfig

# outputs.py imports
from scripts.src.models import NormalizedIOC, OutputFile, OutputConfig
import json
import csv
```

## Build Configuration

```toml
# pyproject.toml
[build-system]
requires = ["setuptools>=68.0", "setuptools-scm>=8.0"]
build-backend = "setuptools.build_meta"

[project]
name = "tc-sgb-api-list"
version = "1.0.0"
description = "Turkish National Cyber Security Directorate IOC processor"
requires-python = ">=3.11"
license = "MIT"

[project.scripts]
tc-sgb = "scripts.main:main"

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
source = ["scripts"]
branch = true
```

<a id="-türkçe"></a>

# Depo Yapısı

## Dizin Ağacı

```
TC-SGB-API-to-List/
├── .github/
│   ├── workflows/
│   │   ├── ci.yml                  # Ana CI hattı
│   │   ├── release.yaml             # Sürüm otomasyonu
│   │   └── scheduled.yml           # Zamanlanmış veri çekme
│   └── dependabot.yml              # Bağımlılık güncellemeleri
│
├── scripts/
│   ├── __init__.py                 # Paket başlatma
│   ├── main.py                     # CLI giriş noktası
│   └── src/
│       ├── __init__.py             # Kaynak paket başlatma
│       ├── client.py               # API istemcisi (httpx)
│       ├── models.py               # Pydantic veri modelleri
│       ├── validator.py            # Girdi doğrulama
│       ├── normalizer.py           # Veri normalizasyonu
│       ├── deduplicator.py         # Tekilleştirme motoru
│       ├── quality.py              # Kalite güvencesi
│       ├── outputs.py              # Çıktı üretimi (16+ format)
│       └── pipeline.py             # Hat orkestratörü
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
├── wiki/
│   ├── Architecture.md
│   ├── Data-Flow.md
│   ├── Module-Architecture.md
│   ├── Repository-Structure.md
│   ├── API-Analysis.md
│   ├── Data-Model.md
│   ├── Threat-Model.md
│   ├── Security-Analysis.md
│   ├── License-Analysis.md
│   ├── Test-Strategy.md
│   ├── Regression-Strategy.md
│   ├── Performance-Strategy.md
│   ├── Versioning-Strategy.md
│   ├── Publishing-Strategy.md
│   ├── Maintenance-Plan.md
│   ├── Risk-Analysis.md
│   ├── Roadmap.md
│   └── Legal-Notices.md
│
├── pyproject.toml                  # Proje meta verileri ve derleme yapılandırması
├── README.md                       # Proje genel bakışı
├── CHANGELOG.md                    # Sürüm değişiklik günlüğü
├── LICENSE                         # Lisans dosyası
├── SECURITY.md                     # Güvenlik politikası
├── CONTRIBUTING.md                 # Katkı yönergeleri
└── .gitignore                      # Git yok sayma kuralları
```

## Temel Dosya Açıklamaları

### Kaynak Kodu (`scripts/src/`)

| Dosya | Satır (tahmini) | Amaç |
|-------|-----------------|------|
| `__init__.py` | ~5 | Paket başlatma |
| `client.py` | ~250 | Yeniden deneme mantığı olan asenkron HTTP istemcisi |
| `models.py` | ~300 | Pydantic modelleri, enum'lar, şemalar |
| `validator.py` | ~400 | 12 doğrulama kuralı, toplu işleme |
| `normalizer.py` | ~350 | Türe özgü normalizasyon dönüşümleri |
| `deduplicator.py` | ~300 | 3 katmanlı tekilleştirme stratejisi motoru |
| `quality.py` | ~400 | İstatistikler, FP tespiti, puanlama |
| `outputs.py` | ~800 | 16+ çıktı formatı üreteçleri |
| `pipeline.py` | ~350 | Uçtan uca orkestrasyon |

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
| `.github/workflows/release.yaml` | Etiketleme üzerinde derleme ve yayımlama |
| `.github/workflows/scheduled.yml` | Günlük otomatik veri çekme |
| `.github/dependabot.yml` | Otomatik bağımlılık güncellemeleri |

## Modül İçe Aktarma Grafiği

```python
# Top-level imports (pipeline.py)
from scripts.src.client import SGBAPIClient
from scripts.src.validator import IOCValidator
from scripts.src.normalizer import IOCNormalizer
from scripts.src.deduplicator import IOCDeduplicator
from scripts.src.quality import QualityEngine
from scripts.src.outputs import OutputEngine
from scripts.src.models import IOCRecord, PipelineConfig

# client.py imports
import httpx
import asyncio
from scripts.src.models import APIResponse, IOCRecord, ClientConfig

# models.py imports
from pydantic import BaseModel, Field, ConfigDict
from enum import Enum
from datetime import datetime

# validator.py imports
from scripts.src.models import IOCRecord, ValidationError, ValidationConfig

# normalizer.py imports
from scripts.src.models import NormalizedIOC, IOCType
import ipaddress

# deduplicator.py imports
from scripts.src.models import NormalizedIOC, DedupResult, DedupConfig
import hashlib

# quality.py imports
from scripts.src.models import NormalizedIOC, QualityReport, QualityConfig

# outputs.py imports
from scripts.src.models import NormalizedIOC, OutputFile, OutputConfig
import json
import csv
```

## Derleme Yapılandırması

```toml
# pyproject.toml
[build-system]
requires = ["setuptools>=68.0", "setuptools-scm>=8.0"]
build-backend = "setuptools.build_meta"

[project]
name = "tc-sgb-api-list"
version = "1.0.0"
description = "Turkish National Cyber Security Directorate IOC processor"
requires-python = ">=3.11"
license = "MIT"

[project.scripts]
tc-sgb = "scripts.main:main"

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
source = ["scripts"]
branch = true
```
