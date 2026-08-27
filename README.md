[English](#english) | [Türkçe](#turkish)

<a id="english"></a>

# TC-SGB-API-to-List

**Automated Threat Intelligence Pipeline for the T.C. Siber Güvenlik Başkanlığı (Cyber Security Presidency) API**

[![CI](https://github.com/bayraktarozcan/TC-SGB-API-to-List/actions/workflows/ci.yml/badge.svg)](https://github.com/bayraktarozcan/TC-SGB-API-to-List/actions/workflows/ci.yml)
[![Scheduled Pipeline](https://github.com/bayraktarozcan/TC-SGB-API-to-List/actions/workflows/schedule.yml/badge.svg)](https://github.com/bayraktarozcan/TC-SGB-API-to-List/actions/workflows/schedule.yml)
[![CodeQL](https://github.com/bayraktarozcan/TC-SGB-API-to-List/actions/workflows/codeql.yml/badge.svg)](https://github.com/bayraktarozcan/TC-SGB-API-to-List/actions/workflows/codeql.yml)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)

---

## Overview

TC-SGB-API-to-List fetches IoC (Indicator of Compromise) data from the TC SGB public API (`https://siberguvenlik.gov.tr/api/`), processes it through a robust multi-stage pipeline, and outputs structured threat intelligence in **16 interoperable formats** compatible with leading DNS filtering and security tools.

## Features

- **Automated IoC Fetching** — Paginated retrieval from the TC SGB API with retry logic and rate limiting
- **Validation & Normalization** — Pydantic-based data models with IoC type inference and format normalization
- **Deduplication** — Efficient set-based deduplication across fetches
- **Quality Scoring** — Multi-factor quality assessment for each IoC
- **16 Output Formats**:
  - DNS: NextDNS, AdGuard, Pi-hole, dnsmasq, Unbound, RPZ, Technitium, MikroTik
  - Firewall: nftables, ipset
  - IDS/IPS: Suricata, CrowdSec
  - Data: CSV, JSON, YAML, SQLite
- **Scheduled Pipeline** — GitHub Actions cron for automated updates every 6 hours
- **Bilingual Documentation** — Full English and Turkish documentation

## Quick Start

### Prerequisites

- Python 3.11+
- pip or Poetry

### Installation

```bash
git clone https://github.com/bayraktarozcan/TC-SGB-API-to-List.git
cd TC-SGB-API-to-List
pip install -e .
```

### Usage

```bash
# Run the full pipeline
tc-sgb fetch

# Generate outputs from previously saved raw data
tc-sgb generate -i output/raw_records.json

# Fetch and display health status
tc-sgb health
```

### Data Download

Latest pre-generated IoC outputs are published automatically (every 6 hours) to the rolling GitHub Release `ioc-data`. The five large-format files are distributed through stable download URLs (small formats remain tracked in the `output/` directory):

| Format | File | Size (approx.) |
|--------|------|----------------|
| Raw records | [raw_records.json](https://github.com/bayraktarozcan/TC-SGB-API-to-List/releases/download/ioc-data/raw_records.json) | 129 MB |
| Structured JSON | [threat_intel_json.json](https://github.com/bayraktarozcan/TC-SGB-API-to-List/releases/download/ioc-data/threat_intel_json.json) | 130 MB |
| SQLite database | [threat_intel_sqlite.db](https://github.com/bayraktarozcan/TC-SGB-API-to-List/releases/download/ioc-data/threat_intel_sqlite.db) | 96 MB |
| Suricata JSON | [threat_intel_suricata.json](https://github.com/bayraktarozcan/TC-SGB-API-to-List/releases/download/ioc-data/threat_intel_suricata.json) | 203 MB |
| Structured YAML | [threat_intel_yaml.yaml](https://github.com/bayraktarozcan/TC-SGB-API-to-List/releases/download/ioc-data/threat_intel_yaml.yaml) | 97 MB |

> Download via `wget`/`curl`/`Invoke-WebRequest` or browse the [release page](https://github.com/bayraktarozcan/TC-SGB-API-to-List/releases/tag/ioc-data). All other formats are generated to `output/` when you run the pipeline locally.

## Project Structure

```
TC-SGB-API-to-List/
├── scripts/
│   ├── main.py                  # CLI entry point
│   └── src/
│       ├── models.py            # Pydantic data models
│       ├── client.py            # Async API client
│       ├── validator.py         # IoC validation
│       ├── normalizer.py        # IoC normalization
│       ├── deduplicator.py      # Deduplication
│       ├── quality.py           # Quality scoring
│       ├── outputs.py           # 16 output format generators
│       └── pipeline.py          # Pipeline orchestrator
├── tests/                       # Test suite
├── wiki/                        # Documentation (bilingual)
├── schema/                      # JSON Schema & OpenAPI spec
├── data/                        # Runtime data cache
├── output/                      # Generated IoC output files (small formats tracked; large formats via `ioc-data` release)
├── examples/                    # Usage examples
├── benchmark/                   # Performance benchmarks
└── .github/workflows/           # CI/CD pipelines
```

## Documentation

| Document | Description |
|----------|-------------|
| [Architecture](wiki/Architecture.md) | System design and component overview |
| [Data Flow](wiki/Data-Flow.md) | Pipeline data flow and transformations |
| [Module Architecture](wiki/Module-Architecture.md) | Module responsibilities and interfaces |
| [Repository Structure](wiki/Repository-Structure.md) | Directory layout and file purposes |
| [API Analysis](wiki/API-Analysis.md) | TC SGB API endpoints and capabilities |
| [Data Model](wiki/Data-Model.md) | Pydantic models and schemas |
| [Threat Model](wiki/Threat-Model.md) | STRIDE threat analysis |
| [Security Analysis](wiki/Security-Analysis.md) | Security posture and hardening |
| [License Analysis](wiki/License-Analysis.md) | Legal and licensing considerations |
| [Test Strategy](wiki/Test-Strategy.md) | Testing approach and coverage |
| [Regression Strategy](wiki/Regression-Strategy.md) | Regression testing methodology |
| [Performance Strategy](wiki/Performance-Strategy.md) | Performance benchmarks and optimization |
| [Versioning Strategy](wiki/Versioning-Strategy.md) | Semantic versioning approach |
| [Publishing Strategy](wiki/Publishing-Strategy.md) | Distribution and publishing |
| [Maintenance Plan](wiki/Maintenance-Plan.md) | Ongoing maintenance procedures |
| [Risk Analysis](wiki/Risk-Analysis.md) | Risk assessment and mitigation |
| [Roadmap](wiki/Roadmap.md) | Development roadmap |
| [Legal Notices](wiki/Legal-Notices.md) | Legal and compliance notices |

## Configuration

Copy `.env.example` to `.env` and configure as needed:

```bash
cp .env.example .env
```

## Development

```bash
# Install dev dependencies
pip install -e ".[dev]"
pip install -r requirements.txt

# Run tests
pytest tests/ -v

# Run linter
ruff check scripts/ tests/

# Run type checker
mypy scripts/
```

## Roadmap

- [x] Core pipeline (fetch → validate → normalize → dedup → score → output)
- [x] 16 output formats
- [x] CI/CD with GitHub Actions
- [x] Comprehensive test suite
- [ ] Docker containerization
- [ ] PyPI publishing
- [ ] Additional threat intel sources (CISA KEV, Spamhaus, URLhaus)
- [ ] Web dashboard

## Contributing

Contributions are welcome! Please read our [contributing guidelines](CONTRIBUTING.md) before submitting a pull request.

## License

This project is licensed under the [MIT License](LICENSE). See [LEGAL_NOTICES](wiki/Legal-Notices.md) for important legal information regarding data redistribution.

## Disclaimer

This tool is provided as-is for legitimate cybersecurity research and defense purposes. Users are responsible for compliance with all applicable laws and regulations.

---

<a id="turkish"></a>

# TC-SGB-API-to-List

**T.C. Siber Güvenlik Başkanlığı (Cyber Security Presidency) API'si için Otomatik Tehdit İstihbaratı Hattı**

[![CI](https://github.com/bayraktarozcan/TC-SGB-API-to-List/actions/workflows/ci.yml/badge.svg)](https://github.com/bayraktarozcan/TC-SGB-API-to-List/actions/workflows/ci.yml)
[![Scheduled Pipeline](https://github.com/bayraktarozcan/TC-SGB-API-to-List/actions/workflows/schedule.yml/badge.svg)](https://github.com/bayraktarozcan/TC-SGB-API-to-List/actions/workflows/schedule.yml)
[![CodeQL](https://github.com/bayraktarozcan/TC-SGB-API-to-List/actions/workflows/codeql.yml/badge.svg)](https://github.com/bayraktarozcan/TC-SGB-API-to-List/actions/workflows/codeql.yml)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)

---

## Genel Bakış

TC-SGB-API-to-List, TC SGB kamu API'sinden (`https://siberguvenlik.gov.tr/api/`) IoC (İhlal Göstergesi) verilerini çeker, güçlü bir çok aşamalı hat üzerinden işler ve **16 birlikte çalışabilir biçimde** yapılandırılmış tehdit istihbaratı çıktısı üretir.

## Özellikler

- **Otomatik IoC Çekme** — Yeniden deneme mantığı ve hız sınırlaması ile sayfalı veri çekme
- **Doğrulama ve Normalleştirme** — Pydantic tabanlı veri modelleri ile IoC türü çıkarma ve biçim normalleştirme
- **Tekilleştirme** — Çekimler arasında verimli küme tabanlı tekilleştirme
- **Kalite Puanlama** — Her IoC için çok faktörlü kalite değerlendirmesi
- **16 Çıktı Formatı**:
  - DNS: NextDNS, AdGuard, Pi-hole, dnsmasq, Unbound, RPZ, Technitium, MikroTik
  - Güvenlik Duvarı: nftables, ipset
  - IDS/IPS: Suricata, CrowdSec
  - Veri: CSV, JSON, YAML, SQLite
- **Zamanlanmış Hat** — Her 6 saatte bir otomatik güncellemeler için GitHub Actions cron zamanlayıcısı
- **Çift Dilli Dokümantasyon** — Tam İngilizce ve Türkçe dokümantasyon

## Hızlı Başlangıç

### Ön Gereksinimler

- Python 3.11+
- pip veya Poetry

### Kurulum

```bash
git clone https://github.com/bayraktarozcan/TC-SGB-API-to-List.git
cd TC-SGB-API-to-List
pip install -e .
```

### Kullanım

```bash
# Tam hattı çalıştır
tc-sgb fetch

# Daha önce kaydedilmiş ham veriden çıktı üret
tc-sgb generate -i output/raw_records.json

# Sağlık durumunu görüntüle
tc-sgb health
```

### Veri İndirme

En güncel önceden üretilmiş IoC çıktıları (her 6 saatte bir) yuvarlanan GitHub Release'i `ioc-data`'da otomatik olarak yayınlanır. Beş büyük biçim dosyası kararlı indirme bağlantıları üzerinden dağıtılır (küçük biçimler `output/` dizininde izlenmeye devam eder):

| Biçim | Dosya | Yaklaşık Boyut |
|-------|-------|----------------|
| Ham kayıtlar | [raw_records.json](https://github.com/bayraktarozcan/TC-SGB-API-to-List/releases/download/ioc-data/raw_records.json) | 129 MB |
| Yapılandırılmış JSON | [threat_intel_json.json](https://github.com/bayraktarozcan/TC-SGB-API-to-List/releases/download/ioc-data/threat_intel_json.json) | 130 MB |
| SQLite veritabanı | [threat_intel_sqlite.db](https://github.com/bayraktarozcan/TC-SGB-API-to-List/releases/download/ioc-data/threat_intel_sqlite.db) | 96 MB |
| Suricata JSON | [threat_intel_suricata.json](https://github.com/bayraktarozcan/TC-SGB-API-to-List/releases/download/ioc-data/threat_intel_suricata.json) | 203 MB |
| Yapılandırılmış YAML | [threat_intel_yaml.yaml](https://github.com/bayraktarozcan/TC-SGB-API-to-List/releases/download/ioc-data/threat_intel_yaml.yaml) | 97 MB |

> `wget`/`curl`/`Invoke-WebRequest` ile indirin veya [release sayfasını](https://github.com/bayraktarozcan/TC-SGB-API-to-List/releases/tag/ioc-data) inceleyin. Diğer tüm biçimler hattı yerel olarak çalıştırdığınızda `output/` dizinine üretilir.

## Proje Yapısı

```
TC-SGB-API-to-List/
├── scripts/
│   ├── main.py                  # CLI giriş noktası
│   └── src/
│       ├── models.py            # Pydantic veri modelleri
│       ├── client.py             # Asenkron API istemcisi
│       ├── validator.py         # IoC doğrulama
│       ├── normalizer.py        # IoC normalleştirme
│       ├── deduplicator.py      # Tekilleştirme
│       ├── quality.py           # Kalite puanlama
│       ├── outputs.py           # 16 çıktı biçimi üreteçleri
│       └── pipeline.py          # Hat koordinatörü
├── tests/                       # Test paketi
├── wiki/                        # Dokümantasyon (çift dilli)
├── schema/                      # JSON Schema ve OpenAPI belirtimi
├── data/                        # Çalışma zamanı veri önbelleği
├── output/                      # Üretilen IoC çıktı dosyaları (küçük biçimler izlenir; büyük biçimler `ioc-data` release'i aracılığıyla)
├── examples/                    # Kullanım örnekleri
├── benchmark/                   # Performans karşılaştırmaları
└── .github/workflows/           # CI/CD hatları
```

## Dokümantasyon

| Belge | Açıklama |
|-------|----------|
| [Mimari](wiki/Architecture.md) | Sistem tasarımı ve bileşen genel bakışı |
| [Veri Akışı](wiki/Data-Flow.md) | Hat veri akışı ve dönüşümleri |
| [Modül Mimarisi](wiki/Module-Architecture.md) | Modül sorumlulukları ve arayüzleri |
| [Depo Yapısı](wiki/Repository-Structure.md) | Dizin yerleşimi ve dosya amaçları |
| [API Analizi](wiki/API-Analysis.md) | TC SGB API uç noktaları ve yetenekleri |
| [Veri Modeli](wiki/Data-Model.md) | Pydantic modelleri ve şemaları |
| [Tehdit Modeli](wiki/Threat-Model.md) | STRIDE tehdit analizi |
| [Güvenlik Analizi](wiki/Security-Analysis.md) | Güvenlik duruşu ve sertleştirme |
| [Lisans Analizi](wiki/License-Analysis.md) | Hukuki ve lisanslama hususları |
| [Test Stratejisi](wiki/Test-Strategy.md) | Test yaklaşımı ve kapsama |
| [Regresyon Stratejisi](wiki/Regression-Strategy.md) | Regresyon test metodolojisi |
| [Performans Stratejisi](wiki/Performance-Strategy.md) | Performans karşılaştırmaları ve optimizasyon |
| [Sürüm Stratejisi](wiki/Versioning-Strategy.md) | Semantik sürümleme yaklaşımı |
| [Yayın Stratejisi](wiki/Publishing-Strategy.md) | Dağıtım ve yayınlanma |
| [Bakım Planı](wiki/Maintenance-Plan.md) | Sürekli bakım prosedürleri |
| [Risk Analizi](wiki/Risk-Analysis.md) | Risk değerlendirmesi ve azaltma |
| [Yol Haritası](wiki/Roadmap.md) | Geliştirme yol haritası |
| [Yasal Bildirimler](wiki/Legal-Notices.md) | Hukuki ve uyum bildirimleri |

## Yapılandırma

`.env.example` dosyasını `.env` olarak kopyalayın ve gerektiğince yapılandırın:

```bash
cp .env.example .env
```

## Geliştirme

```bash
# Geliştirici bağımlılıklarını kur
pip install -e ".[dev]"
pip install -r requirements.txt

# Testleri çalıştır
pytest tests/ -v

# Linter'ı çalıştır
ruff check scripts/ tests/

# Tip kontrolcüyü çalıştır
mypy scripts/
```

## Yol Haritası

- [x] Çekirdek hat (çek → doğrula → normalleştir → tekilleştir → puanla → çıktı)
- [x] 16 çıktı biçimi
- [x] GitHub Actions ile CI/CD
- [x] Kapsamlı test paketi
- [ ] Docker konteynerleştirme
- [ ] PyPI yayınlama
- [ ] Ek tehdit istihbaratı kaynakları (CISA KEV, Spamhaus, URLhaus)
- [ ] Web kontrol paneli

## Katkıda Bulunma

Katkılar memnuniyetle karşılanmaktadır! Lütfen pull request göndermeden önce [katkı yönergelerimizi](CONTRIBUTING.md) okuyun.

## Lisans

Bu proje [MIT Lisansı](LICENSE) altında lisanslanmıştır. Veri yeniden dağıtımı ile ilgili önemli yasal bilgiler için [YASAL BİLDİRİMLER](wiki/Legal-Notices.md) dosyasına bakın.

## Sorumluluk Reddi

Bu araç, meşru siber güvenlik araştırması ve savunma amaçları için olduğu gibi sağlanmaktadır. Kullanıcılar, geçerli tüm yasa ve düzenlemelere uymaktan sorumludur.
