> **Language / Dil** &nbsp;
> [EN English](#-english) &nbsp;·&nbsp; [TR Türkçe](#-türkçe)

<a id="-english"></a>

# Repository Structure

## Directory Tree

```
TC-SGB-API-to-List/
├── .github/
│   ├── ISSUE_TEMPLATE/
│   │   ├── bug_report.yaml
│   │   ├── config.yml
│   │   └── feature_request.yaml
│   ├── linters/
│   │   ├── .markdownlint.json
│   │   └── .yamllint.yml
│   ├── workflows/
│   │   ├── ci.yml                     # Main CI pipeline
│   │   ├── codeql.yml                 # CodeQL security analysis
│   │   └── schedule.yml               # Scheduled data fetch
│   ├── CODEOWNERS
│   ├── dependabot.yml                  # Dependency updates
│   ├── FUNDING.yml
│   └── pull_request_template.md
│
├── scripts/
│   ├── __init__.py                    # Package init
│   ├── main.py                        # CLI entry point
│   └── src/
│       ├── __init__.py                # Source package init
│       ├── client.py                  # Async API client (httpx)
│       ├── models.py                  # Pydantic data models & enums
│       ├── validator.py               # Input validation functions
│       ├── normalizer.py              # Data normalization functions
│       ├── deduplicator.py            # Deduplication engine
│       ├── quality.py                 # Quality scoring & FP detection
│       ├── outputs.py                 # Output generation (17 formats)
│       └── pipeline.py                # Pipeline orchestrator
│
├── tests/                             # Flat test structure (no subdirs)
│   ├── __init__.py
│   ├── conftest.py                    # Shared fixtures
│   ├── test_client.py
│   ├── test_deduplicator.py
│   ├── test_fuzz.py
│   ├── test_models.py
│   ├── test_normalizer.py
│   ├── test_outputs.py
│   ├── test_performance.py
│   ├── test_pipeline.py
│   ├── test_quality.py
│   ├── test_regression.py
│   └── test_validator.py
│
├── output/                            # Generated output files
│   ├── .gitkeep
│   ├── raw_records.json
│   ├── threat_intel_adguard.txt
│   ├── threat_intel_csv.csv
│   ├── threat_intel_crowdsec.yaml
│   ├── threat_intel_dnsmasq.conf
│   ├── threat_intel_ipset.ipset
│   ├── threat_intel_json.json
│   ├── threat_intel_mikrotik.rsc
│   ├── threat_intel_nextdns.txt
│   ├── threat_intel_nftables.nft
│   ├── threat_intel_pihole.txt
│   ├── threat_intel_rpz.zone
│   ├── threat_intel_sqlite.db
│   ├── threat_intel_suricata.json
│   ├── threat_intel_technitium.zone
│   ├── threat_intel_unbound.conf
│   ├── threat_intel_yaml.yaml
│   └── regen/
│       ├── threat_intel_adguard.txt
│       ├── threat_intel_csv.csv
│       └── threat_intel_nextdns.txt
│
├── schema/
│   ├── address.schema.json
│   └── openapi.yaml
│
├── data/
│   └── .gitkeep
│
├── examples/
│   └── .gitkeep
│
├── benchmark/
│   └── .gitkeep
│
├── wiki/
│   ├── _Footer.md
│   ├── _Sidebar.md
│   ├── API-Analysis.md
│   ├── Architecture.md
│   ├── Audit-Report.md
│   ├── Data-Flow.md
│   ├── Data-Model.md
│   ├── Home.md
│   ├── Legal-Notices.md
│   ├── License-Analysis.md
│   ├── Maintenance-Plan.md
│   ├── Module-Architecture.md
│   ├── Performance-Strategy.md
│   ├── Publishing-Strategy.md
│   ├── Regression-Strategy.md
│   ├── Repository-Structure.md
│   ├── Risk-Analysis.md
│   ├── Roadmap.md
│   ├── Security-Analysis.md
│   ├── Test-Strategy.md
│   ├── Threat-Model.md
│   └── Versioning-Strategy.md
│
├── pyproject.toml                     # Project metadata & build config
├── requirements.txt                   # Pinned dependencies
├── .env.example                       # Environment variable template
├── .gitignore                         # Git ignore rules
├── .gitattributes                     # Git attributes
├── .editorconfig                      # Editor config
├── README.md                          # Project overview
├── CONTRIBUTING.md                    # Contribution guidelines
├── SECURITY.md                        # Security policy
├── CODE_OF_CONDUCT.md                 # Code of conduct
├── CHANGELOG.md                       # Version changelog
├── RELEASE-NOTE-TEMPLATE.md           # Release note template
├── LICENSE                            # License file
├── index.html                         # Landing page
└── bandit-report.json                 # Security scan report
```

## Key Files Description

### Source Code (`scripts/src/`)

| File | Purpose |
|------|---------|
| `__init__.py` | Package init |
| `client.py` | `AsyncAPIClient` class — async HTTP client with pagination, retries, and rate limiting |
| `models.py` | Enums (`IOCType`, `DescriptionCategory`, `Source`, `ConnectionType`), Pydantic models (`PaginatedResponse`, `AddressRecord`, `DescriptionRecord`, `ConnectionTypeRecord`, `SourceRecord`, `IncidentRecord`, `AnnouncementRecord`, `ValidatedIOC`, `NormalizedIOC`, `ScoredIOC`, `PipelineStats`) |
| `validator.py` | Functions: `validate_ioc()`, `validate_records_batch()`, plus IP/domain validation helpers |
| `normalizer.py` | Functions: `normalize_ioc()`, `normalize_batch()`, plus type-specific normalizers |
| `deduplicator.py` | `DeduplicationResult` class, functions: `deduplicate()`, `get_dedup_stats()` |
| `quality.py` | Functions: `score_ioc()`, `score_iocs()`, `filter_false_positives()`, plus FP detection helpers |
| `outputs.py` | 17 `generate_*()` functions + `FORMAT_REGISTRY` dict + `generate_all()` orchestrator |
| `pipeline.py` | `Pipeline` class (orchestrator), `run_pipeline_sync()` entry point |

### Tests (`tests/`)

Flat structure — no subdirectories. 13 files total, 330 tests, ~73% coverage.

| File | Focus |
|------|-------|
| `__init__.py` | Package marker |
| `conftest.py` | Shared pytest fixtures |
| `test_client.py` | API client mocking and retry logic |
| `test_models.py` | Pydantic model validation |
| `test_validator.py` | Input validation rules |
| `test_normalizer.py` | Data normalization transforms |
| `test_deduplicator.py` | Deduplication logic |
| `test_quality.py` | Quality scoring & FP detection |
| `test_outputs.py` | Output format generation |
| `test_pipeline.py` | End-to-end pipeline orchestration |
| `test_regression.py` | Snapshot / output stability |
| `test_fuzz.py` | Property-based & fuzz testing |
| `test_performance.py` | Throughput benchmarks |

### Build & CI

| File | Purpose |
|------|---------|
| `pyproject.toml` | Package metadata, dependencies, tool config (ruff, mypy, pytest) |
| `requirements.txt` | Pinned dependency versions |
| `.github/workflows/ci.yml` | Lint, type check, test on PR |
| `.github/workflows/codeql.yml` | CodeQL security analysis |
| `.github/workflows/schedule.yml` | Scheduled automated data fetch |
| `.github/dependabot.yml` | Automated dependency updates |

## Module Import Graph

```python
# pipeline.py imports
from .client import AsyncAPIClient
from .models import AddressRecord, NormalizedIOC, PipelineStats, ScoredIOC, ValidatedIOC
from .normalizer import normalize_ioc
from .quality import score_ioc
from .validator import validate_ioc

# client.py imports
import httpx
from .models import (AddressRecord, AnnouncementRecord, ConnectionTypeRecord,
                     DescriptionRecord, IncidentRecord, SourceRecord)

# models.py imports
from pydantic import BaseModel, Field
from enum import Enum
from datetime import datetime
from typing import Generic, TypeVar

# validator.py imports
import ipaddress, re
from urllib.parse import urlparse
from .models import AddressRecord, IOCType, ValidatedIOC

# normalizer.py imports
import re
from urllib.parse import urlparse
from .models import IOCType, NormalizedIOC, ValidatedIOC

# deduplicator.py imports
import logging
from .models import IOCType, ScoredIOC

# quality.py imports
import ipaddress, re
from urllib.parse import urlparse
from .models import IOCType, NormalizedIOC, ScoredIOC

# outputs.py imports
import csv, io, json, logging, sqlite3
from collections.abc import Sequence
from datetime import UTC, datetime
from pathlib import Path
import yaml
from .models import IOCType, ScoredIOC
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
description = "Threat Intelligence Pipeline for TC SGB API"
requires-python = ">=3.11"
license = "MIT"
dependencies = ["httpx>=0.27,<1", "pydantic>=2.0,<3", "rich>=13.0,<14"]

[project.scripts]
tc-sgb = "scripts.main:main"

[tool.pytest.ini_options]
testpaths = ["tests"]

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
│   ├── ISSUE_TEMPLATE/
│   │   ├── bug_report.yaml
│   │   ├── config.yml
│   │   └── feature_request.yaml
│   ├── linters/
│   │   ├── .markdownlint.json
│   │   └── .yamllint.yml
│   ├── workflows/
│   │   ├── ci.yml                     # Ana CI hattı
│   │   ├── codeql.yml                 # CodeQL güvenlik analizi
│   │   └── schedule.yml               # Zamanlanmış veri çekme
│   ├── CODEOWNERS
│   ├── dependabot.yml                  # Bağımlılık güncellemeleri
│   ├── FUNDING.yml
│   └── pull_request_template.md
│
├── scripts/
│   ├── __init__.py                    # Paket başlatma
│   ├── main.py                        # CLI giriş noktası
│   └── src/
│       ├── __init__.py                # Kaynak paket başlatma
│       ├── client.py                  # Asenkron API istemcisi (httpx)
│       ├── models.py                  # Pydantic veri modelleri ve enum'lar
│       ├── validator.py               # Girdi doğrulama fonksiyonları
│       ├── normalizer.py              # Veri normalizasyon fonksiyonları
│       ├── deduplicator.py            # Tekilleştirme motoru
│       ├── quality.py                 # Kalite puanlama ve FP tespiti
│       ├── outputs.py                 # Çıktı üretimi (17 format)
│       └── pipeline.py                # Hat orkestratörü
│
├── tests/                             # Düz test yapısı (alt dizin yok)
│   ├── __init__.py
│   ├── conftest.py                    # Paylaşılan fixture'lar
│   ├── test_client.py
│   ├── test_deduplicator.py
│   ├── test_fuzz.py
│   ├── test_models.py
│   ├── test_normalizer.py
│   ├── test_outputs.py
│   ├── test_performance.py
│   ├── test_pipeline.py
│   ├── test_quality.py
│   ├── test_regression.py
│   └── test_validator.py
│
├── output/                            # Üretilen çıktı dosyaları
│   ├── .gitkeep
│   ├── raw_records.json
│   ├── threat_intel_adguard.txt
│   ├── threat_intel_csv.csv
│   ├── threat_intel_crowdsec.yaml
│   ├── threat_intel_dnsmasq.conf
│   ├── threat_intel_ipset.ipset
│   ├── threat_intel_json.json
│   ├── threat_intel_mikrotik.rsc
│   ├── threat_intel_nextdns.txt
│   ├── threat_intel_nftables.nft
│   ├── threat_intel_pihole.txt
│   ├── threat_intel_rpz.zone
│   ├── threat_intel_sqlite.db
│   ├── threat_intel_suricata.json
│   ├── threat_intel_technitium.zone
│   ├── threat_intel_unbound.conf
│   ├── threat_intel_yaml.yaml
│   └── regen/
│       ├── threat_intel_adguard.txt
│       ├── threat_intel_csv.csv
│       └── threat_intel_nextdns.txt
│
├── schema/
│   ├── address.schema.json
│   └── openapi.yaml
│
├── data/
│   └── .gitkeep
│
├── examples/
│   └── .gitkeep
│
├── benchmark/
│   └── .gitkeep
│
├── wiki/
│   ├── _Footer.md
│   ├── _Sidebar.md
│   ├── API-Analysis.md
│   ├── Architecture.md
│   ├── Audit-Report.md
│   ├── Data-Flow.md
│   ├── Data-Model.md
│   ├── Home.md
│   ├── Legal-Notices.md
│   ├── License-Analysis.md
│   ├── Maintenance-Plan.md
│   ├── Module-Architecture.md
│   ├── Performance-Strategy.md
│   ├── Publishing-Strategy.md
│   ├── Regression-Strategy.md
│   ├── Repository-Structure.md
│   ├── Risk-Analysis.md
│   ├── Roadmap.md
│   ├── Security-Analysis.md
│   ├── Test-Strategy.md
│   ├── Threat-Model.md
│   └── Versioning-Strategy.md
│
├── pyproject.toml                     # Proje meta verileri ve derleme yapılandırması
├── requirements.txt                   # Sabitlenmiş bağımlılıklar
├── .env.example                       # Ortam değişkenleri şablonu
├── .gitignore                         # Git yok sayma kuralları
├── .gitattributes                     # Git nitelikleri
├── .editorconfig                      # Editör yapılandırması
├── README.md                          # Proje genel bakışı
├── CONTRIBUTING.md                    # Katkı yönergeleri
├── SECURITY.md                        # Güvenlik politikası
├── CODE_OF_CONDUCT.md                 # Davranış kuralları
├── CHANGELOG.md                       # Sürüm değişiklik günlüğü
├── RELEASE-NOTE-TEMPLATE.md           # Sürüm notu şablonu
├── LICENSE                            # Lisans dosyası
├── index.html                         # Landing sayfası
└── bandit-report.json                 # Güvenlik tarama raporu
```

## Temel Dosya Açıklamaları

### Kaynak Kodu (`scripts/src/`)

| Dosya | Amaç |
|-------|------|
| `__init__.py` | Paket başlatma |
| `client.py` | `AsyncAPIClient` sınıfı — sayfalama, yeniden deneme ve hız sınırlama ile asenkron HTTP istemcisi |
| `models.py` | Enum'lar (`IOCType`, `DescriptionCategory`, `Source`, `ConnectionType`), Pydantic modelleri (`PaginatedResponse`, `AddressRecord`, `DescriptionRecord`, `ConnectionTypeRecord`, `SourceRecord`, `IncidentRecord`, `AnnouncementRecord`, `ValidatedIOC`, `NormalizedIOC`, `ScoredIOC`, `PipelineStats`) |
| `validator.py` | Fonksiyonlar: `validate_ioc()`, `validate_records_batch()`, IP/alan adı doğrulama yardımcıları |
| `normalizer.py` | Fonksiyonlar: `normalize_ioc()`, `normalize_batch()`, türe özgü normalleştiriciler |
| `deduplicator.py` | `DeduplicationResult` sınıfı, fonksiyonlar: `deduplicate()`, `get_dedup_stats()` |
| `quality.py` | Fonksiyonlar: `score_ioc()`, `score_iocs()`, `filter_false_positives()`, FP tespit yardımcıları |
| `outputs.py` | 17 `generate_*()` fonksiyonu + `FORMAT_REGISTRY` sözlüğü + `generate_all()` orkestratörü |
| `pipeline.py` | `Pipeline` sınıfı (orkestratör), `run_pipeline_sync()` giriş noktası |

### Testler (`tests/`)

Düz yapı — alt dizin yok. Toplam 13 dosya, 330 test, ~73% kapsama.

| Dosya | Odak |
|-------|------|
| `__init__.py` | Paket işaretleme |
| `conftest.py` | Paylaşılan pytest fixture'ları |
| `test_client.py` | API istemcisi mock'lama ve yeniden deneme mantığı |
| `test_models.py` | Pydantic model doğrulama |
| `test_validator.py` | Girdi doğrulama kuralları |
| `test_normalizer.py` | Veri normalizasyonu dönüşümleri |
| `test_deduplicator.py` | Tekilleştirme mantığı |
| `test_quality.py` | Kalite puanlama ve FP tespiti |
| `test_outputs.py` | Çıktı formatı üretimi |
| `test_pipeline.py` | Uçtan uca hat orkestrasyonu |
| `test_regression.py` | Anlık görüntü / çıktı kararlılığı |
| `test_fuzz.py` | Özelliğe dayalı ve fuzz testleri |
| `test_performance.py` | Verimlilik ölçümleri |

### Derleme ve CI

| Dosya | Amaç |
|-------|------|
| `pyproject.toml` | Paket meta verileri, bağımlılıklar, araç yapılandırması (ruff, mypy, pytest) |
| `requirements.txt` | Sabitlenmiş bağımlılık sürümleri |
| `.github/workflows/ci.yml` | PR üzerinde lint, tür kontrolü, test |
| `.github/workflows/codeql.yml` | CodeQL güvenlik analizi |
| `.github/workflows/schedule.yml` | Zamanlanmış otomatik veri çekme |
| `.github/dependabot.yml` | Otomatik bağımlılık güncellemeleri |

## Modül İçe Aktarma Grafiği

```python
# pipeline.py imports
from .client import AsyncAPIClient
from .models import AddressRecord, NormalizedIOC, PipelineStats, ScoredIOC, ValidatedIOC
from .normalizer import normalize_ioc
from .quality import score_ioc
from .validator import validate_ioc

# client.py imports
import httpx
from .models import (AddressRecord, AnnouncementRecord, ConnectionTypeRecord,
                     DescriptionRecord, IncidentRecord, SourceRecord)

# models.py imports
from pydantic import BaseModel, Field
from enum import Enum
from datetime import datetime
from typing import Generic, TypeVar

# validator.py imports
import ipaddress, re
from urllib.parse import urlparse
from .models import AddressRecord, IOCType, ValidatedIOC

# normalizer.py imports
import re
from urllib.parse import urlparse
from .models import IOCType, NormalizedIOC, ValidatedIOC

# deduplicator.py imports
import logging
from .models import IOCType, ScoredIOC

# quality.py imports
import ipaddress, re
from urllib.parse import urlparse
from .models import IOCType, NormalizedIOC, ScoredIOC

# outputs.py imports
import csv, io, json, logging, sqlite3
from collections.abc import Sequence
from datetime import UTC, datetime
from pathlib import Path
import yaml
from .models import IOCType, ScoredIOC
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
description = "Threat Intelligence Pipeline for TC SGB API"
requires-python = ">=3.11"
license = "MIT"
dependencies = ["httpx>=0.27,<1", "pydantic>=2.0,<3", "rich>=13.0,<14"]

[project.scripts]
tc-sgb = "scripts.main:main"

[tool.pytest.ini_options]
testpaths = ["tests"]

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
