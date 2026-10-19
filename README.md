[English](#-english) | [Türkçe](#-türkçe)

<a id="-english"></a>

# TC-SGB-API-to-List

**Automated Threat Intelligence Pipeline for the T.C. Siber Güvenlik Başkanlığı (Cyber Security Presidency) API**

[![CI](https://github.com/bayraktarozcan/TC-SGB-API-to-List/actions/workflows/ci.yml/badge.svg)](https://github.com/bayraktarozcan/TC-SGB-API-to-List/actions/workflows/ci.yml)
[![Scheduled Pipeline](https://github.com/bayraktarozcan/TC-SGB-API-to-List/actions/workflows/schedule.yml/badge.svg)](https://github.com/bayraktarozcan/TC-SGB-API-to-List/actions/workflows/schedule.yml)
[![CodeQL](https://github.com/bayraktarozcan/TC-SGB-API-to-List/actions/workflows/codeql.yml/badge.svg)](https://github.com/bayraktarozcan/TC-SGB-API-to-List/actions/workflows/codeql.yml)
[![Pages](https://github.com/bayraktarozcan/TC-SGB-API-to-List/actions/workflows/deploy.yml/badge.svg)](https://github.com/bayraktarozcan/TC-SGB-API-to-List/actions/workflows/deploy.yml)
[![Hygiene](https://github.com/bayraktarozcan/TC-SGB-API-to-List/actions/workflows/hygiene.yml/badge.svg)](https://github.com/bayraktarozcan/TC-SGB-API-to-List/actions/workflows/hygiene.yml)
[![Link Check](https://github.com/bayraktarozcan/TC-SGB-API-to-List/actions/workflows/link-check.yml/badge.svg)](https://github.com/bayraktarozcan/TC-SGB-API-to-List/actions/workflows/link-check.yml)
[![GitLab Pipeline](https://gitlab.com/bayraktarozcan/TC-SGB-API-to-List/badges/main/pipeline.svg)](https://gitlab.com/bayraktarozcan/TC-SGB-API-to-List/-/commits/main)
[![GitLab Coverage](https://gitlab.com/bayraktarozcan/TC-SGB-API-to-List/badges/main/coverage.svg)](https://gitlab.com/bayraktarozcan/TC-SGB-API-to-List/-/commits/main)
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
- **Scheduled Pipeline** — GitHub Actions cron for automated updates every day (19:00 UTC)
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
tc-sgb generate -i Output/raw_records.json

# Fetch and display health status
tc-sgb health

# Fetch third-party threat feeds (CERT.PL, CERT.SI)
tc-sgb fetch-external

# Verify published external lists against the safety policy (no fetching)
tc-sgb validate-external
```

### Data Download

Latest pre-generated IoC outputs are published automatically (daily, 19:00 UTC) to the rolling GitHub Release `ioc-data`. The five large-format files are distributed through stable download URLs (small formats remain tracked in the `Output/` directory):

| Format | File | Size (approx.) |
|--------|------|----------------|
| Raw records | [raw_records.json](https://github.com/bayraktarozcan/TC-SGB-API-to-List/releases/download/ioc-data/raw_records.json) | 129 MB |
| Structured JSON | [threat_intel_json.json](https://github.com/bayraktarozcan/TC-SGB-API-to-List/releases/download/ioc-data/threat_intel_json.json) | 130 MB |
| SQLite database | [threat_intel_sqlite.db](https://github.com/bayraktarozcan/TC-SGB-API-to-List/releases/download/ioc-data/threat_intel_sqlite.db) | 96 MB |
| Suricata JSON | [threat_intel_suricata.json](https://github.com/bayraktarozcan/TC-SGB-API-to-List/releases/download/ioc-data/threat_intel_suricata.json) | 203 MB |
| Structured YAML | [threat_intel_yaml.yaml](https://github.com/bayraktarozcan/TC-SGB-API-to-List/releases/download/ioc-data/threat_intel_yaml.yaml) | 97 MB |

> Download via `wget`/`curl`/`Invoke-WebRequest` or browse the [release page](https://github.com/bayraktarozcan/TC-SGB-API-to-List/releases/tag/ioc-data). All other formats are generated to `Output/` when you run the pipeline locally.
>
> **Brave / AdGuard users:** release-asset links are served as file downloads, which
> Brave rejects as custom filter lists. Subscribe to the
> [plain-text mirror](https://raw.githubusercontent.com/bayraktarozcan/TC-SGB-API-to-List/filter-lists/01-turkiye-sgb_adguard.txt)
> instead (`brave://adblock` → Add filter list via URL); it is refreshed daily.
> Two more curated lists (Poland, Slovenia) are published on
> the same branch and refreshed by the same workflow; files are numbered so
> Brave shows them in country order (`04` is reserved for Lithuania, whose
> source sits behind a Cloudflare challenge and cannot be fetched yet):
>
> - [02-polonya-certpl_adguard.txt](https://raw.githubusercontent.com/bayraktarozcan/TC-SGB-API-to-List/filter-lists/02-polonya-certpl_adguard.txt)
> - [03-slovenya-certsi_adguard.txt](https://raw.githubusercontent.com/bayraktarozcan/TC-SGB-API-to-List/filter-lists/03-slovenya-certsi_adguard.txt)
>
> The Azerbaijani `blacklist.gov.az` list is out of scope: its contents proved
> unreliable and unsuitable for a curated blocklist, so it is no longer
> fetched or published.

### Publication safety

Syntax validation checks rule shape; the safety policy in `Scripts/src/safety.py`
decides whether blocking a host wholesale is safe to publish. High-impact hosts
are rejected outright, shared user-content infrastructure goes to review, and
every held indicator lands in a per-feed audit file (`Output/External/`) with
its reason — never silently dropped. The scheduled workflow publishes only
lists passing `tc-sgb validate-external`; a failing feed keeps serving its last
good snapshot.

## Project Structure

```
TC-SGB-API-to-List/
├── Scripts/
│   ├── main.py                  # CLI entry point
│   └── src/
│       ├── models.py            # Pydantic data models
│       ├── client.py            # Async API client
│       ├── external_feeds.py    # Third-party threat-feed mirrors
│       ├── safety.py            # Publication safety policy (shared)
│       ├── validator.py         # IoC validation
│       ├── normalizer.py        # IoC normalization
│       ├── deduplicator.py      # Deduplication
│       ├── quality.py           # Quality scoring
│       ├── outputs.py           # 16 output format generators
│       └── pipeline.py          # Pipeline orchestrator
├── Tests/                       # Test suite
├── Docs/                        # Documentation (bilingual)
├── Schema/                      # JSON Schema & OpenAPI spec
├── Data/                        # Runtime data cache
├── Output/                      # Generated IoC output files (small formats tracked; large formats via `ioc-data` release)
├── Examples/                    # Usage examples
├── Benchmark/                   # Performance benchmarks
└── .github/workflows/           # CI/CD pipelines
```

## Documentation

| Document | Description |
|----------|-------------|
| [Architecture](Docs/Architecture.md) | System design and component overview |
| [Data Flow](Docs/Data-Flow.md) | Pipeline data flow and transformations |
| [Module Architecture](Docs/Module-Architecture.md) | Module responsibilities and interfaces |
| [Repository Structure](Docs/Repository-Structure.md) | Directory layout and file purposes |
| [API Analysis](Docs/API-Analysis.md) | TC SGB API endpoints and capabilities |
| [Data Model](Docs/Data-Model.md) | Pydantic models and schemas |
| [Threat Model](Docs/Threat-Model.md) | STRIDE threat analysis |
| [Security Analysis](Docs/Security-Analysis.md) | Security posture and hardening |
| [License Analysis](Docs/License-Analysis.md) | Legal and licensing considerations |
| [Test Strategy](Docs/Test-Strategy.md) | Testing approach and coverage |
| [Regression Strategy](Docs/Regression-Strategy.md) | Regression testing methodology |
| [Performance Strategy](Docs/Performance-Strategy.md) | Performance benchmarks and optimization |
| [Versioning Strategy](Docs/Versioning-Strategy.md) | Semantic versioning approach |
| [Publishing Strategy](Docs/Publishing-Strategy.md) | Distribution and publishing |
| [Maintenance Plan](Docs/Maintenance-Plan.md) | Ongoing maintenance procedures |
| [Risk Analysis](Docs/Risk-Analysis.md) | Risk assessment and mitigation |
| [Roadmap](Docs/Roadmap.md) | Development roadmap |
| [Legal Notices](Docs/Legal-Notices.md) | Legal and compliance notices |

### Project documents

| Document | Description |
|----------|-------------|
| [Changelog](CHANGELOG.md) | Version history |
| [Contributing](CONTRIBUTING.md) | Contribution guidelines |
| [Security](SECURITY.md) | Security reporting process |
| [Support](SUPPORT.md) | Where to ask questions and how to report an issue |
| [Privacy](PRIVACY.md) | What the project collects, stores, and transmits |
| [Code of Conduct](CODE_OF_CONDUCT.md) | Code of conduct |
| [Release notes](RELEASE-NOTE-TEMPLATE.md) | Skeleton that release notes follow |
| [Agent guide](AGENTS.md) | Operating rules for humans and coding agents |
| [License](LICENSE) | License terms |
| [Notice](NOTICE) | Third-party attribution and trademark notices |
| [Code owners](CODEOWNERS) | Defines code owners |

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
pytest Tests/ -v

# Run linter
ruff check Scripts/ Tests/

# Run type checker
mypy Scripts/
```

## Roadmap

- [x] Core pipeline (fetch → validate → normalize → score → dedup → output)
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

This project is licensed under the [MIT License](LICENSE). See [LEGAL_NOTICES](Docs/Legal-Notices.md) for important legal information regarding data redistribution.

## Disclaimer

This tool is provided as-is for legitimate cybersecurity research and defense purposes. Users are responsible for compliance with all applicable laws and regulations.

---

<a id="-türkçe"></a>

# TC-SGB-API-to-List

**T.C. Siber Güvenlik Başkanlığı (Cyber Security Presidency) API'si için Otomatik Tehdit İstihbaratı Hattı**

[![CI](https://github.com/bayraktarozcan/TC-SGB-API-to-List/actions/workflows/ci.yml/badge.svg)](https://github.com/bayraktarozcan/TC-SGB-API-to-List/actions/workflows/ci.yml)
[![Scheduled Pipeline](https://github.com/bayraktarozcan/TC-SGB-API-to-List/actions/workflows/schedule.yml/badge.svg)](https://github.com/bayraktarozcan/TC-SGB-API-to-List/actions/workflows/schedule.yml)
[![CodeQL](https://github.com/bayraktarozcan/TC-SGB-API-to-List/actions/workflows/codeql.yml/badge.svg)](https://github.com/bayraktarozcan/TC-SGB-API-to-List/actions/workflows/codeql.yml)
[![Pages](https://github.com/bayraktarozcan/TC-SGB-API-to-List/actions/workflows/deploy.yml/badge.svg)](https://github.com/bayraktarozcan/TC-SGB-API-to-List/actions/workflows/deploy.yml)
[![Hygiene](https://github.com/bayraktarozcan/TC-SGB-API-to-List/actions/workflows/hygiene.yml/badge.svg)](https://github.com/bayraktarozcan/TC-SGB-API-to-List/actions/workflows/hygiene.yml)
[![Link Check](https://github.com/bayraktarozcan/TC-SGB-API-to-List/actions/workflows/link-check.yml/badge.svg)](https://github.com/bayraktarozcan/TC-SGB-API-to-List/actions/workflows/link-check.yml)
[![GitLab Pipeline](https://gitlab.com/bayraktarozcan/TC-SGB-API-to-List/badges/main/pipeline.svg)](https://gitlab.com/bayraktarozcan/TC-SGB-API-to-List/-/commits/main)
[![GitLab Coverage](https://gitlab.com/bayraktarozcan/TC-SGB-API-to-List/badges/main/coverage.svg)](https://gitlab.com/bayraktarozcan/TC-SGB-API-to-List/-/commits/main)
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
- **Zamanlanmış Hat** — Her gün (19:00 UTC) otomatik güncellemeler için GitHub Actions cron zamanlayıcısı
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
tc-sgb generate -i Output/raw_records.json

# Sağlık durumunu görüntüle
tc-sgb health

# Üçüncü taraf tehdit akışlarını çek (CERT.PL, CERT.SI)
tc-sgb fetch-external

# Yayımlanmış harici listeleri güvenlik politikasına göre doğrula (çekme yok)
tc-sgb validate-external
```

### Veri İndirme

En güncel önceden üretilmiş IoC çıktıları (her gün, 19:00 UTC) yuvarlanan GitHub Release'i `ioc-data`'da otomatik olarak yayınlanır. Beş büyük biçim dosyası kararlı indirme bağlantıları üzerinden dağıtılır (küçük biçimler `Output/` dizininde izlenmeye devam eder):

| Biçim | Dosya | Yaklaşık Boyut |
|-------|-------|----------------|
| Ham kayıtlar | [raw_records.json](https://github.com/bayraktarozcan/TC-SGB-API-to-List/releases/download/ioc-data/raw_records.json) | 129 MB |
| Yapılandırılmış JSON | [threat_intel_json.json](https://github.com/bayraktarozcan/TC-SGB-API-to-List/releases/download/ioc-data/threat_intel_json.json) | 130 MB |
| SQLite veritabanı | [threat_intel_sqlite.db](https://github.com/bayraktarozcan/TC-SGB-API-to-List/releases/download/ioc-data/threat_intel_sqlite.db) | 96 MB |
| Suricata JSON | [threat_intel_suricata.json](https://github.com/bayraktarozcan/TC-SGB-API-to-List/releases/download/ioc-data/threat_intel_suricata.json) | 203 MB |
| Yapılandırılmış YAML | [threat_intel_yaml.yaml](https://github.com/bayraktarozcan/TC-SGB-API-to-List/releases/download/ioc-data/threat_intel_yaml.yaml) | 97 MB |

> `wget`/`curl`/`Invoke-WebRequest` ile indirin veya [release sayfasını](https://github.com/bayraktarozcan/TC-SGB-API-to-List/releases/tag/ioc-data) inceleyin. Diğer tüm biçimler hattı yerel olarak çalıştırdığınızda `Output/` dizinine üretilir.
>
> **Brave / AdGuard kullanıcıları:** release bağlantıları dosya indirme olarak sunulur ve
> Brave bunları özel filtre listesi olarak kabul etmez. Bunun yerine her gün güncellenen
> [düz metin aynayı](https://raw.githubusercontent.com/bayraktarozcan/TC-SGB-API-to-List/filter-lists/01-turkiye-sgb_adguard.txt)
> kullanın (`brave://adblock` → Add filter list via URL).
> Aynı dalda, aynı iş akışıyla güncellenen iki seçkin liste daha yayınlanır
> (Polonya, Slovenya); dosyalar numaralıdır, böylece Brave onları
> ülke sırasıyla gösterir (`04` Litvanya için ayrılmıştır; kaynağı bir
> Cloudflare doğrulamasının arkasında olduğu için henüz çekilemiyor):
>
> - [02-polonya-certpl_adguard.txt](https://raw.githubusercontent.com/bayraktarozcan/TC-SGB-API-to-List/filter-lists/02-polonya-certpl_adguard.txt)
> - [03-slovenya-certsi_adguard.txt](https://raw.githubusercontent.com/bayraktarozcan/TC-SGB-API-to-List/filter-lists/03-slovenya-certsi_adguard.txt)
>
> Azerbaycan `blacklist.gov.az` listesi kapsam dışıdır: içeriği güvenilir
> olmadığı ve seçkin bir engel listesi için uygun düşmediği için artık
> çekilmiyor veya yayımlanmıyor.

### Yayımlama güvenliği

Sözdizimi doğrulaması kural biçimini denetler; `Scripts/src/safety.py` içindeki
güvenlik politikası bir makinenin toptan engellenmesinin yayımlanmasının güvenli
olup olmadığına karar verir. Yüksek etkili makineler doğrudan reddedilir, ortak
kullanıcı içerik altyapısı incelemeye ayrılır ve tutulan her gösterge gerekçesiyle
birlikte akış başına denetim dosyasına (`Output/External/`) yazılır — asla sessizce
düşürülmez. Zamanlanmış iş akışı yalnızca `tc-sgb validate-external` geçen listeleri
yayımlar; koşamayan akış son iyi anlık görüntüyü sunmaya devam eder.

## Proje Yapısı

```
TC-SGB-API-to-List/
├── Scripts/
│   ├── main.py                  # CLI giriş noktası
│   └── src/
│       ├── models.py            # Pydantic veri modelleri
│       ├── client.py             # Asenkron API istemcisi
│       ├── external_feeds.py    # Üçüncü taraf tehdit akışı aynaları
│       ├── safety.py            # Yayımlama güvenlik politikası (ortak)
│       ├── validator.py         # IoC doğrulama
│       ├── normalizer.py        # IoC normalleştirme
│       ├── deduplicator.py      # Tekilleştirme
│       ├── quality.py           # Kalite puanlama
│       ├── outputs.py           # 16 çıktı biçimi üreteçleri
│       └── pipeline.py          # Hat koordinatörü
├── Tests/                       # Test paketi
├── Docs/                        # Dokümantasyon (çift dilli)
├── Schema/                      # JSON Schema ve OpenAPI belirtimi
├── Data/                        # Çalışma zamanı veri önbelleği
├── Output/                      # Üretilen IoC çıktı dosyaları (küçük biçimler izlenir; büyük biçimler `ioc-data` release'i aracılığıyla)
├── Examples/                    # Kullanım örnekleri
├── Benchmark/                   # Performans karşılaştırmaları
└── .github/workflows/           # CI/CD hatları
```

## Dokümantasyon

| Belge | Açıklama |
|-------|----------|
| [Mimari](Docs/Architecture.md) | Sistem tasarımı ve bileşen genel bakışı |
| [Veri Akışı](Docs/Data-Flow.md) | Hat veri akışı ve dönüşümleri |
| [Modül Mimarisi](Docs/Module-Architecture.md) | Modül sorumlulukları ve arayüzleri |
| [Depo Yapısı](Docs/Repository-Structure.md) | Dizin yerleşimi ve dosya amaçları |
| [API Analizi](Docs/API-Analysis.md) | TC SGB API uç noktaları ve yetenekleri |
| [Veri Modeli](Docs/Data-Model.md) | Pydantic modelleri ve şemaları |
| [Tehdit Modeli](Docs/Threat-Model.md) | STRIDE tehdit analizi |
| [Güvenlik Analizi](Docs/Security-Analysis.md) | Güvenlik duruşu ve sertleştirme |
| [Lisans Analizi](Docs/License-Analysis.md) | Hukuki ve lisanslama hususları |
| [Test Stratejisi](Docs/Test-Strategy.md) | Test yaklaşımı ve kapsama |
| [Regresyon Stratejisi](Docs/Regression-Strategy.md) | Regresyon test metodolojisi |
| [Performans Stratejisi](Docs/Performance-Strategy.md) | Performans karşılaştırmaları ve optimizasyon |
| [Sürüm Stratejisi](Docs/Versioning-Strategy.md) | Semantik sürümleme yaklaşımı |
| [Yayın Stratejisi](Docs/Publishing-Strategy.md) | Dağıtım ve yayınlanma |
| [Bakım Planı](Docs/Maintenance-Plan.md) | Sürekli bakım prosedürleri |
| [Risk Analizi](Docs/Risk-Analysis.md) | Risk değerlendirmesi ve azaltma |
| [Yol Haritası](Docs/Roadmap.md) | Geliştirme yol haritası |
| [Yasal Bildirimler](Docs/Legal-Notices.md) | Hukuki ve uyum bildirimleri |

### Proje belgeleri

| Belge | Açıklama |
|-------|----------|
| [Değişiklik Günlüğü](CHANGELOG.md) | Sürüm geçmişi |
| [Katkıda Bulunma](CONTRIBUTING.md) | Katkı yönergeleri |
| [Güvenlik](SECURITY.md) | Güvenlik bildirim süreci |
| [Destek](SUPPORT.md) | Soru sorma ve sorun bildirme yeri |
| [Gizlilik](PRIVACY.md) | Projenin ne topladığı, sakladığı ve ilettiği |
| [Davranış Kuralları](CODE_OF_CONDUCT.md) | Davranış kuralları |
| [Sürüm notları](RELEASE-NOTE-TEMPLATE.md) | Sürüm notlarının izlediği iskelet |
| [Ajan kılavuzu](AGENTS.md) | İnsanlar ve kodlama ajanları için çalışma kuralları |
| [Lisans](LICENSE) | Lisans koşulları |
| [Bildirim](NOTICE) | Üçüncü taraf atıfları ve marka bildirimleri |
| [Kod sahipleri](CODEOWNERS) | Kod sahiplerini tanımlar |

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
pytest Tests/ -v

# Linter'ı çalıştır
ruff check Scripts/ Tests/

# Tip kontrolcüyü çalıştır
mypy Scripts/
```

## Yol Haritası

- [x] Çekirdek hat (çek → doğrula → normalleştir → puanla → tekilleştir → çıktı)
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

Bu proje [MIT Lisansı](LICENSE) altında lisanslanmıştır. Veri yeniden dağıtımı ile ilgili önemli yasal bilgiler için [YASAL BİLDİRİMLER](Docs/Legal-Notices.md) dosyasına bakın.

## Sorumluluk Reddi

Bu araç, meşru siber güvenlik araştırması ve savunma amaçları için olduğu gibi sağlanmaktadır. Kullanıcılar, geçerli tüm yasa ve düzenlemelere uymaktan sorumludur.
