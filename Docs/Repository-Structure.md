> **Language / Dil** &nbsp;
> [EN English](#-english) &nbsp;·&nbsp; [TR Türkçe](#-türkçe)

<a id="-english"></a>

# Repository Structure

## Directory Tree

```
TC-SGB-API-to-List/
├── .github/
│   ├── actions/
│   │   └── refresh-gitlab-release/
│   │       └── action.yml              # Composite action: refresh the GitLab release
│   ├── ISSUE_TEMPLATE/
│   │   ├── bug_report.yaml
│   │   ├── config.yml
│   │   └── feature_request.yaml
│   ├── linters/
│   │   ├── .markdownlint.json
│   │   └── .yamllint.yml
│   ├── workflows/
│   │   ├── auto-merge.yml              # Auto-merge trusted PRs
│   │   ├── ci.yml                      # Main CI pipeline
│   │   ├── codeql.yml                  # CodeQL security analysis
│   │   ├── dependabot-auto-merge.yml   # Auto-merge Dependabot PRs
│   │   ├── deploy.yml                  # Deploy the static site to Pages
│   │   ├── hygiene.yml                 # actionlint + deep mojibake scan
│   │   ├── link-check.yml              # lychee link checking
│   │   ├── mirror-gitlab.yml           # Mirror the rolling release to GitLab
│   │   ├── schedule.yml                # Scheduled data fetch
│   │   └── wiki-sync.yml               # Docs-to-wiki sync
│   ├── dependabot.yml                   # Dependency updates
│   ├── FUNDING.yml
│   └── pull_request_template.md
│
├── Scripts/
│   ├── __init__.py                    # Package init
│   ├── main.py                        # CLI entry point
│   ├── verify_mirror.py               # Mirror verifier: sync-sha + structure parity
│   └── src/
│       ├── __init__.py                # Source package init
│       ├── changelog.py               # Persistent changelog: diff vs previous snapshot
│       ├── client.py                  # Async API client (httpx)
│       ├── deduplicator.py            # Deduplication engine
│       ├── external_feeds.py          # Third-party feed mirrors (Brave/AdGuard branch)
│       ├── models.py                  # Pydantic data models & enums
│       ├── mojibake.py                # Mojibake detection for CI gates
│       ├── normalizer.py              # Data normalization functions
│       ├── outputs.py                 # Output generation (16 formats)
│       ├── pipeline.py                # Pipeline orchestrator
│       ├── quality.py                 # Quality scoring & FP detection
│       ├── safety.py                  # Publication safety policy
│       └── validator.py               # Input validation functions
│
├── Tests/                             # Flat test structure (no subdirs)
│   ├── __init__.py
│   ├── conftest.py                    # Shared fixtures
│   ├── test_catalog.py                # manifest.json + Blocklists/*.json catalog
│   ├── test_changelog.py              # Changelog generation & diff engine
│   ├── test_client.py
│   ├── test_deduplicator.py
│   ├── test_external_feeds.py         # Third-party feed fetch/parse/render
│   ├── test_fuzz.py
│   ├── test_main.py                   # CLI entry point
│   ├── test_mirror_sync.py            # Mirror verifier contract & drift axes
│   ├── test_models.py
│   ├── test_mojibake.py               # Mojibake scanner
│   ├── test_normalizer.py
│   ├── test_outputs.py
│   ├── test_performance.py
│   ├── test_pipeline.py
│   ├── test_quality.py
│   ├── test_regression.py
│   ├── test_repo_conventions.py       # Repository convention guards
│   ├── test_safety.py                 # Publication safety policy
│   └── test_validator.py
│
├── Output/                            # Generated output files
│   ├── .gitkeep
│   ├── manifest.json                  # Tracked: release manifest
│   ├── Blocklists/                    # Tracked: per-format blocklist catalogs
│   │   ├── adguard.json
│   │   ├── crowdsec.json
│   │   ├── csv.json
│   │   ├── dnsmasq.json
│   │   ├── index.json                 # Catalog index
│   │   ├── ipset.json
│   │   ├── json.json
│   │   ├── mikrotik.json
│   │   ├── nextdns.json
│   │   ├── nftables.json
│   │   ├── pihole.json
│   │   ├── raw_records.json
│   │   ├── rpz.json
│   │   ├── sqlite.json
│   │   ├── suricata.json
│   │   ├── technitium.json
│   │   ├── unbound.json
│   │   └── yaml.json
│   ├── raw_records.json               # ⚠ Large-format files are NOT tracked in git — published to the rolling release `ioc-data`
│   ├── threat_intel_adguard.txt
│   ├── threat_intel_csv.csv
│   ├── threat_intel_crowdsec.yaml
│   ├── threat_intel_dnsmasq.conf
│   ├── threat_intel_ipset.ipset
│   ├── threat_intel_json.json         # ⚠ See note above (published via `ioc-data` release)
│   ├── threat_intel_mikrotik.rsc
│   ├── threat_intel_nextdns.txt
│   ├── threat_intel_nftables.nft
│   ├── threat_intel_pihole.txt
│   ├── threat_intel_rpz.zone
│   ├── threat_intel_sqlite.db         # ⚠ See note above (published via `ioc-data` release)
│   ├── threat_intel_suricata.json     # ⚠ See note above (published via `ioc-data` release)
│   ├── threat_intel_technitium.zone
│   ├── threat_intel_unbound.conf
│   ├── threat_intel_yaml.yaml         # ⚠ See note above (published via `ioc-data` release)
│   └── Logs/
│       └── fetch_<timestamp>.md       # Per-run changelog (generated)
│
├── Schema/
│   ├── address.schema.json
│   └── openapi.yaml
│
├── Data/
│   └── .gitkeep
│
├── Examples/
│   └── .gitkeep
│
├── Benchmark/
│   └── .gitkeep
│
├── Docs/
│   ├── Planning/
│   │   └── .gitkeep
│   ├── Footer.md
│   ├── Sidebar.md
│   ├── API-Analysis.md
│   ├── Architecture.md
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
│   ├── Troubleshooting.md
│   └── Versioning-Strategy.md
│
├── pyproject.toml                     # Project metadata & build config
├── requirements.txt                   # Pinned dependencies
├── .env.example                       # Environment variable template
├── .gitignore                         # Git ignore rules
├── .gitattributes                     # Git attributes
├── .editorconfig                      # Editor config
├── .gitlab-ci.yml                     # GitLab CI pipeline
├── README.md                          # Project overview
├── CHANGELOG.md                       # Version changelog
├── CONTRIBUTING.md                    # Contribution guidelines
├── CODE_OF_CONDUCT.md                 # Code of conduct
├── SECURITY.md                        # Security policy
├── SUPPORT.md                         # Support channels
├── PRIVACY.md                         # Privacy statement
├── NOTICE                             # Third-party attributions
├── LICENSE                            # License file
├── CODEOWNERS                         # Code owners
├── RELEASE-NOTE-TEMPLATE.md           # Release note template
├── AGENTS.md                          # Agent & contributor rules
│
└── Site/                              # GitHub Pages landing page
    ├── .nojekyll
    └── index.html                     # Landing page
```

## Key Files Description

### Source Code (`Scripts/src/`)

| File | Purpose |
|------|---------|
| `__init__.py` | Package init |
| `client.py` | `AsyncAPIClient` class — async HTTP client with pagination, retries, and rate limiting |
| `models.py` | Enums (`IoCType`, `DescriptionCategory`, `Source`, `ConnectionType`), Pydantic models (`PaginatedResponse`, `AddressRecord`, `DescriptionRecord`, `ConnectionTypeRecord`, `SourceRecord`, `IncidentRecord`, `AnnouncementRecord`, `ValidatedIoC`, `NormalizedIoC`, `ScoredIoC`, `PipelineStats`) |
| `validator.py` | Functions: `validate_ioc()`, `validate_records_batch()`, plus IP/domain validation helpers |
| `normalizer.py` | Functions: `normalize_ioc()`, `normalize_batch()`, plus type-specific normalizers |
| `deduplicator.py` | `DeduplicationResult` class, functions: `deduplicate()`, `get_dedup_stats()` |
| `quality.py` | Functions: `score_ioc()`, `score_iocs()`, `filter_false_positives()`, plus FP detection helpers |
| `outputs.py` | 16 `generate_*()` functions + `FORMAT_REGISTRY` dict + `generate_all()` orchestrator |
| `pipeline.py` | `Pipeline` class (orchestrator), `run_pipeline_sync()` entry point |
| `changelog.py` | Functions: `generate_changelog()`, `format_changelog_markdown()`, IoC diff engine |

### Tests (`Tests/`)

Flat structure — no subdirectories. 15 files total, 487 tests, 99% coverage.

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
| `test_changelog.py` | Changelog generation & diff engine |
| `test_main.py` | CLI entry point & pipeline wiring |

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
from .models import AddressRecord, NormalizedIoC, PipelineStats, ScoredIoC, ValidatedIoC
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
from .models import AddressRecord, IoCType, ValidatedIoC

# normalizer.py imports
import re
from urllib.parse import urlparse
from .models import IoCType, NormalizedIoC, ValidatedIoC

# deduplicator.py imports
import logging
from .models import IoCType, ScoredIoC

# quality.py imports
import ipaddress, re
from urllib.parse import urlparse
from .models import IoCType, NormalizedIoC, ScoredIoC

# outputs.py imports
import csv, io, json, logging, sqlite3
from collections.abc import Sequence
from datetime import UTC, datetime
from pathlib import Path
import yaml
from .models import IoCType, ScoredIoC
```

## Build Configuration

```toml
# pyproject.toml
[build-system]
requires = ["setuptools>=68.0"]
build-backend = "setuptools.build_meta"

[project]
name = "tc-sgb-api-list"
version = "0.3.2.0"
description = "Threat Intelligence Pipeline for TC SGB API — IoC fetcher, validator, and multi-format exporter"
requires-python = ">=3.11"
license = "MIT"
dependencies = [
    "httpx>=0.28,<1",
    "pydantic>=2.10,<3",
    "python-dotenv>=1.0,<2",
    "pyyaml>=6.0,<7",
]

[project.scripts]
tc-sgb = "Scripts.main:main"

[tool.pytest.ini_options]
testpaths = ["Tests"]

[tool.ruff]
target-version = "py311"
line-length = 100

[tool.mypy]
python_version = "3.11"
strict = true

[tool.coverage.run]
source = ["Scripts"]
branch = true
```

<a id="-türkçe"></a>

# Depo Yapısı

## Dizin Ağacı

```
TC-SGB-API-to-List/
├── .github/
│   ├── actions/
│   │   └── refresh-gitlab-release/
│   │       └── action.yml              # Bileşik eylem: GitLab sürümünü yenile
│   ├── ISSUE_TEMPLATE/
│   │   ├── bug_report.yaml
│   │   ├── config.yml
│   │   └── feature_request.yaml
│   ├── linters/
│   │   ├── .markdownlint.json
│   │   └── .yamllint.yml
│   ├── workflows/
│   │   ├── auto-merge.yml              # Güvenilen PR'ları otomatik birleştir
│   │   ├── ci.yml                      # Ana CI hattı
│   │   ├── codeql.yml                  # CodeQL güvenlik analizi
│   │   ├── dependabot-auto-merge.yml   # Dependabot PR'larını otomatik birleştir
│   │   ├── deploy.yml                  # Statik siteyi Pages'e dağıt
│   │   ├── hygiene.yml                 # actionlint + derin mojibake taraması
│   │   ├── link-check.yml              # lychee bağlantı denetimi
│   │   ├── mirror-gitlab.yml           # Yuvarlanan sürümü GitLab'a yansıt
│   │   ├── schedule.yml                # Zamanlanmış veri çekme
│   │   └── wiki-sync.yml               # Docs -> wiki eşitleme
│   ├── dependabot.yml                   # Bağımlılık güncellemeleri
│   ├── FUNDING.yml
│   └── pull_request_template.md
│
├── Scripts/
│   ├── __init__.py                    # Paket başlatma
│   ├── main.py                        # CLI giriş noktası
│   ├── verify_mirror.py               # Ayna doğrulayıcı: sync-sha + yapı paritesi
│   └── src/
│       ├── __init__.py                # Kaynak paket başlatma
│       ├── changelog.py               # Kalıcı değişiklik günlüğü: önceki anlık görüntüyle fark
│       ├── client.py                  # Asenkron API istemcisi (httpx)
│       ├── deduplicator.py            # Tekilleştirme motoru
│       ├── external_feeds.py          # Üçüncü taraf feed aynaları (Brave/AdGuard dalı)
│       ├── models.py                  # Pydantic veri modelleri ve enum'lar
│       ├── mojibake.py                # CI kapıları için mojibake tespiti
│       ├── normalizer.py              # Veri normalizasyon fonksiyonları
│       ├── outputs.py                 # Çıktı üretimi (16 biçim)
│       ├── pipeline.py                # Hat orkestratörü
│       ├── quality.py                 # Kalite puanlama ve FP tespiti
│       ├── safety.py                  # Yayın güvenliği politikası
│       └── validator.py               # Girdi doğrulama fonksiyonları
│
├── Tests/                             # Düz test yapısı (alt dizin yok)
│   ├── __init__.py
│   ├── conftest.py                    # Paylaşılan fixture'lar
│   ├── test_catalog.py                # manifest.json + Blocklists/*.json kataloğu
│   ├── test_changelog.py              # Değişiklik günlüğü üretimi ve fark motoru
│   ├── test_client.py
│   ├── test_deduplicator.py
│   ├── test_external_feeds.py         # Üçüncü taraf feed çekme/ayrıştırma/render
│   ├── test_fuzz.py
│   ├── test_main.py                   # CLI giriş noktası
│   ├── test_mirror_sync.py            # Ayna doğrulayıcı sözleşmesi ve drift eksenleri
│   ├── test_models.py
│   ├── test_mojibake.py               # Mojibake tarayıcısı
│   ├── test_normalizer.py
│   ├── test_outputs.py
│   ├── test_performance.py
│   ├── test_pipeline.py
│   ├── test_quality.py
│   ├── test_regression.py
│   ├── test_repo_conventions.py       # Depo kuralı koruyucuları
│   ├── test_safety.py                 # Yayın güvenliği politikası
│   └── test_validator.py
│
├── Output/                            # Üretilen çıktı dosyaları
│   ├── .gitkeep
│   ├── manifest.json                  # İzlenir: sürüm bildirimi
│   ├── Blocklists/                    # İzlenir: biçim başına blocklist katalogları
│   │   ├── adguard.json
│   │   ├── crowdsec.json
│   │   ├── csv.json
│   │   ├── dnsmasq.json
│   │   ├── index.json                 # Katalog dizini
│   │   ├── ipset.json
│   │   ├── json.json
│   │   ├── mikrotik.json
│   │   ├── nextdns.json
│   │   ├── nftables.json
│   │   ├── pihole.json
│   │   ├── raw_records.json
│   │   ├── rpz.json
│   │   ├── sqlite.json
│   │   ├── suricata.json
│   │   ├── technitium.json
│   │   ├── unbound.json
│   │   └── yaml.json
│   ├── raw_records.json               # ⚠ Büyük biçim dosyaları git'te İZLENMEZ — `ioc-data` yuvarlanan release'i ile yayınlanır
│   ├── threat_intel_adguard.txt
│   ├── threat_intel_csv.csv
│   ├── threat_intel_crowdsec.yaml
│   ├── threat_intel_dnsmasq.conf
│   ├── threat_intel_ipset.ipset
│   ├── threat_intel_json.json         # ⚠ Yukarıdaki nota bakın (`ioc-data` release'i ile yayınlanır)
│   ├── threat_intel_mikrotik.rsc
│   ├── threat_intel_nextdns.txt
│   ├── threat_intel_nftables.nft
│   ├── threat_intel_pihole.txt
│   ├── threat_intel_rpz.zone
│   ├── threat_intel_sqlite.db         # ⚠ Yukarıdaki nota bakın (`ioc-data` release'i ile yayınlanır)
│   ├── threat_intel_suricata.json     # ⚠ Yukarıdaki nota bakın (`ioc-data` release'i ile yayınlanır)
│   ├── threat_intel_technitium.zone
│   ├── threat_intel_unbound.conf
│   ├── threat_intel_yaml.yaml         # ⚠ Yukarıdaki nota bakın (`ioc-data` release'i ile yayınlanır)
│   └── Logs/
│       └── fetch_<timestamp>.md       # Koşu başına değişiklik günlüğü (üretilir)
│
├── Schema/
│   ├── address.schema.json
│   └── openapi.yaml
│
├── Data/
│   └── .gitkeep
│
├── Examples/
│   └── .gitkeep
│
├── Benchmark/
│   └── .gitkeep
│
├── Docs/
│   ├── Planning/
│   │   └── .gitkeep
│   ├── Footer.md
│   ├── Sidebar.md
│   ├── API-Analysis.md
│   ├── Architecture.md
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
│   ├── Troubleshooting.md
│   └── Versioning-Strategy.md
│
├── pyproject.toml                     # Proje meta verileri ve derleme yapılandırması
├── requirements.txt                   # Sabitlenmiş bağımlılıklar
├── .env.example                       # Ortam değişkenleri şablonu
├── .gitignore                         # Git yok sayma kuralları
├── .gitattributes                     # Git nitelikleri
├── .editorconfig                      # Editör yapılandırması
├── .gitlab-ci.yml                     # GitLab CI hattı
├── README.md                          # Proje genel bakışı
├── CHANGELOG.md                       # Sürüm değişiklik günlüğü
├── CONTRIBUTING.md                    # Katkı yönergeleri
├── CODE_OF_CONDUCT.md                 # Davranış kuralları
├── SECURITY.md                        # Güvenlik politikası
├── SUPPORT.md                         # Destek kanalları
├── PRIVACY.md                         # Gizlilik bildirimi
├── NOTICE                             # Üçüncü taraf atıfları
├── LICENSE                            # Lisans dosyası
├── CODEOWNERS                         # Kod sahipleri
├── RELEASE-NOTE-TEMPLATE.md           # Sürüm notu şablonu
├── AGENTS.md                          # Ajan ve katkı kuralları
│
└── Site/                              # GitHub Pages landing sayfası
    ├── .nojekyll
    └── index.html                     # Landing sayfası
```

## Temel Dosya Açıklamaları

### Kaynak Kodu (`Scripts/src/`)

| Dosya | Amaç |
|-------|------|
| `__init__.py` | Paket başlatma |
| `client.py` | `AsyncAPIClient` sınıfı — sayfalama, yeniden deneme ve hız sınırlama ile asenkron HTTP istemcisi |
| `models.py` | Enum'lar (`IoCType`, `DescriptionCategory`, `Source`, `ConnectionType`), Pydantic modelleri (`PaginatedResponse`, `AddressRecord`, `DescriptionRecord`, `ConnectionTypeRecord`, `SourceRecord`, `IncidentRecord`, `AnnouncementRecord`, `ValidatedIoC`, `NormalizedIoC`, `ScoredIoC`, `PipelineStats`) |
| `validator.py` | Fonksiyonlar: `validate_ioc()`, `validate_records_batch()`, IP/alan adı doğrulama yardımcıları |
| `normalizer.py` | Fonksiyonlar: `normalize_ioc()`, `normalize_batch()`, türe özgü normalleştiriciler |
| `deduplicator.py` | `DeduplicationResult` sınıfı, fonksiyonlar: `deduplicate()`, `get_dedup_stats()` |
| `quality.py` | Fonksiyonlar: `score_ioc()`, `score_iocs()`, `filter_false_positives()`, FP tespit yardımcıları |
| `outputs.py` | 16 `generate_*()` fonksiyonu + `FORMAT_REGISTRY` sözlüğü + `generate_all()` orkestratörü |
| `pipeline.py` | `Pipeline` sınıfı (orkestratör), `run_pipeline_sync()` giriş noktası |
| `changelog.py` | Fonksiyonlar: `generate_changelog()`, `format_changelog_markdown()`, IoC fark motoru |

### Testler (`Tests/`)

Düz yapı — alt dizin yok. Toplam 15 dosya, 487 test, %99 kapsama.

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
| `test_outputs.py` | Çıktı biçimi üretimi |
| `test_pipeline.py` | Uçtan uca hat orkestrasyonu |
| `test_regression.py` | Anlık görüntü / çıktı kararlılığı |
| `test_fuzz.py` | Özelliğe dayalı ve fuzz testleri |
| `test_performance.py` | Verimlilik ölçümleri |
| `test_changelog.py` | Changelog üretimi ve fark motoru |
| `test_main.py` | CLI giriş noktası ve hat bağlantısı |

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
from .models import AddressRecord, NormalizedIoC, PipelineStats, ScoredIoC, ValidatedIoC
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
from .models import AddressRecord, IoCType, ValidatedIoC

# normalizer.py imports
import re
from urllib.parse import urlparse
from .models import IoCType, NormalizedIoC, ValidatedIoC

# deduplicator.py imports
import logging
from .models import IoCType, ScoredIoC

# quality.py imports
import ipaddress, re
from urllib.parse import urlparse
from .models import IoCType, NormalizedIoC, ScoredIoC

# outputs.py imports
import csv, io, json, logging, sqlite3
from collections.abc import Sequence
from datetime import UTC, datetime
from pathlib import Path
import yaml
from .models import IoCType, ScoredIoC
```

## Derleme Yapılandırması

```toml
# pyproject.toml
[build-system]
requires = ["setuptools>=68.0"]
build-backend = "setuptools.build_meta"

[project]
name = "tc-sgb-api-list"
version = "0.3.2.0"
description = "Threat Intelligence Pipeline for TC SGB API — IoC fetcher, validator, and multi-format exporter"
requires-python = ">=3.11"
license = "MIT"
dependencies = [
    "httpx>=0.28,<1",
    "pydantic>=2.10,<3",
    "python-dotenv>=1.0,<2",
    "pyyaml>=6.0,<7",
]

[project.scripts]
tc-sgb = "Scripts.main:main"

[tool.pytest.ini_options]
testpaths = ["Tests"]

[tool.ruff]
target-version = "py311"
line-length = 100

[tool.mypy]
python_version = "3.11"
strict = true

[tool.coverage.run]
source = ["Scripts"]
branch = true
```
