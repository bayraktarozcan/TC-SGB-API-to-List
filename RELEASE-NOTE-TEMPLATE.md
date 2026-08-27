[English](#-english) | [Türkçe](#-türkçe)

<a id="-english"></a>

# Release Note Template

> Copy the template below, replace placeholders with actual values, and use it when creating GitHub Releases.

> **MANDATORY: Every release MUST be bilingual (English + Turkish), following the exact same format as README.md.**
> Use the combined template below — English block first, then `---` separator, then Turkish block.
> Each block has its own anchor, headings, and descriptions — never mix languages within a section.

---

````markdown
[English](#-english) | [Türkçe](#-türkçe)

<a id="-english"></a>

## TC-SGB-API-to-List v{VERSION}

> **{ONE_LINE_HIGHLIGHT}**

---

### What's New

{FEATURE_LIST}

### Improvements

{IMPROVEMENT_LIST}

### Bug Fixes

{BUG_FIX_LIST}

### Breaking Changes

{BREAKING_CHANGES_OR_NONE}

### Statistics

| Metric | Value |
|--------|-------|
| IoC Output Formats | {N} |
| Total IoCs Fetched | ~{N} |
| Validated IoCs | ~{N} |
| Final IoCs (after dedup) | ~{N} |
| Test Suite | {N} tests passing |
| Type Safety | mypy clean |
| Lint | ruff clean |

### Installation

````bash
git clone https://github.com/bayraktarozcan/TC-SGB-API-to-List.git
cd TC-SGB-API-to-List
pip install -e .
````

### Quick Start

````bash
tc-sgb fetch
tc-sgb generate -i output/raw_records.json
tc-sgb health
````

### Documentation

- [Wiki](https://github.com/bayraktarozcan/TC-SGB-API-to-List/wiki)
- [Architecture](https://github.com/bayraktarozcan/TC-SGB-API-to-List/wiki/Architecture)
- [API Analysis](https://github.com/bayraktarozcan/TC-SGB-API-to-List/wiki/API-Analysis)
- [Data Flow](https://github.com/bayraktarozcan/TC-SGB-API-to-List/wiki/Data-Flow)

**Full Changelog**: https://github.com/bayraktarozcan/TC-SGB-API-to-List/compare/{PREV_TAG}...v{VERSION}

---

<a id="-türkçe"></a>

## TC-SGB-API-to-List v{SÜRÜM}

> **{TEK_SATIR_VURGULAMA}**

---

### Yenilikler

{ÖZELLİK_LISTESİ}

### İyileştirmeler

{İYİLEŞTİRME_LISTESİ}

### Hata Düzeltmeleri

{HATA_DÜZELTME_LISTESİ}

### Kırıcı Değişiklikler

{KIRICI_DEĞİŞİKLİKLER_VEYA_YOK}

### İstatistikler

| Metrik | Değer |
|--------|-------|
| IoC Çıktı Formatı Sayısı | {N} |
| Çekilen Toplam IoC | ~{N} |
| Doğrulanmış IoC | ~{N} |
| Nihai IoC (tekilleştirmeden sonra) | ~{N} |
| Test Paketi | {N} test geçiyor |
| Tip Güvenliği | mypy temiz |
| Lint | ruff temiz |

### Kurulum

````bash
git clone https://github.com/bayraktarozcan/TC-SGB-API-to-List.git
cd TC-SGB-API-to-List
pip install -e .
````

### Hızlı Başlangıç

````bash
tc-sgb fetch
tc-sgb generate -i output/raw_records.json
tc-sgb health
````

### Dokümantasyon

- [Wiki](https://github.com/bayraktarozcan/TC-SGB-API-to-List/wiki)
- [Mimari](https://github.com/bayraktarozcan/TC-SGB-API-to-List/wiki/Architecture)
- [API Analizi](https://github.com/bayraktarozcan/TC-SGB-API-to-List/wiki/API-Analysis)
- [Veri Akışı](https://github.com/bayraktarozcan/TC-SGB-API-to-List/wiki/Data-Flow)

**Tam Değişiklik Günlüğü**: https://github.com/bayraktarozcan/TC-SGB-API-to-List/compare/{ÖNCEKİ_ETİKET}...v{SÜRÜM}
````

---

<a id="-türkçe"></a>

# Sürüm Notu Şablonu

> Aşağıdaki şablonu kopyalayın, yer tutucuları gerçek değerlerle değiştirin ve GitHub Release'leri oluştururken kullanın.

> **ZORUNLU: Her release çift dilli (İngilizce + Türkçe) olmalıdır, README.md ile aynı biçim bire bir izlenmelidir.**
> Birleşik şablonu kullanın — önce İngilizce blok, ardından `---` ayracı, sonra Türkçe blok.
> Her bloğun kendi çapa noktası, başlıkları ve açıklamaları vardır — bir bölüm içinde diller asla karıştırılmaz.

---

<a id="-english"></a>

# Release Note Template

> Copy the template below, replace placeholders with actual values, and use it when creating GitHub Releases.

> **MANDATORY: Every release MUST be bilingual (English + Turkish), following the exact same format as README.md.**
> Use the combined template below — English block first, then `---` separator, then Turkish block.
> Each block has its own anchor, headings, and descriptions — never mix languages within a section.

---

````markdown
[English](#-english) | [Türkçe](#-türkçe)

<a id="-english"></a>

## TC-SGB-API-to-List v{VERSION}

> **{ONE_LINE_HIGHLIGHT}**

---

### What's New

{FEATURE_LIST}

### Improvements

{IMPROVEMENT_LIST}

### Bug Fixes

{BUG_FIX_LIST}

### Breaking Changes

{BREAKING_CHANGES_OR_NONE}

### Statistics

| Metric | Value |
|--------|-------|
| IoC Output Formats | {N} |
| Total IoCs Fetched | ~{N} |
| Validated IoCs | ~{N} |
| Final IoCs (after dedup) | ~{N} |
| Test Suite | {N} tests passing |
| Type Safety | mypy clean |
| Lint | ruff clean |

### Installation

````bash
git clone https://github.com/bayraktarozcan/TC-SGB-API-to-List.git
cd TC-SGB-API-to-List
pip install -e .
````

### Quick Start

````bash
tc-sgb fetch
tc-sgb generate -i output/raw_records.json
tc-sgb health
````

### Documentation

- [Wiki](https://github.com/bayraktarozcan/TC-SGB-API-to-List/wiki)
- [Architecture](https://github.com/bayraktarozcan/TC-SGB-API-to-List/wiki/Architecture)
- [API Analysis](https://github.com/bayraktarozcan/TC-SGB-API-to-List/wiki/API-Analysis)
- [Data Flow](https://github.com/bayraktarozcan/TC-SGB-API-to-List/wiki/Data-Flow)

**Full Changelog**: https://github.com/bayraktarozcan/TC-SGB-API-to-List/compare/{PREV_TAG}...v{VERSION}

---

<a id="-türkçe"></a>

## TC-SGB-API-to-List v{SÜRÜM}

> **{TEK_SATIR_VURGULAMA}**

---

### Yenilikler

{ÖZELLİK_LISTESİ}

### İyileştirmeler

{İYİLEŞTİRME_LISTESİ}

### Hata Düzeltmeleri

{HATA_DÜZELTME_LISTESİ}

### Kırıcı Değişiklikler

{KIRICI_DEĞİŞİKLİKLER_VEYA_YOK}

### İstatistikler

| Metrik | Değer |
|--------|-------|
| IoC Çıktı Formatı Sayısı | {N} |
| Çekilen Toplam IoC | ~{N} |
| Doğrulanmış IoC | ~{N} |
| Nihai IoC (tekilleştirmeden sonra) | ~{N} |
| Test Paketi | {N} test geçiyor |
| Tip Güvenliği | mypy temiz |
| Lint | ruff temiz |

### Kurulum

````bash
git clone https://github.com/bayraktarozcan/TC-SGB-API-to-List.git
cd TC-SGB-API-to-List
pip install -e .
````

### Hızlı Başlangıç

````bash
tc-sgb fetch
tc-sgb generate -i output/raw_records.json
tc-sgb health
````

### Dokümantasyon

- [Wiki](https://github.com/bayraktarozcan/TC-SGB-API-to-List/wiki)
- [Mimari](https://github.com/bayraktarozcan/TC-SGB-API-to-List/wiki/Architecture)
- [API Analizi](https://github.com/bayraktarozcan/TC-SGB-API-to-List/wiki/API-Analysis)
- [Veri Akışı](https://github.com/bayraktarozcan/TC-SGB-API-to-List/wiki/Data-Flow)

**Tam Değişiklik Günlüğü**: https://github.com/bayraktarozcan/TC-SGB-API-to-List/compare/{ÖNCEKİ_ETİKET}...v{SÜRÜM}
````

---

### Example: v0.1.0.0

````markdown
[English](#-english) | [Türkçe](#-türkçe)

<a id="-english"></a>

## TC-SGB-API-to-List v0.1.0.0

> **Initial public release — Full IoC pipeline with 16 output formats and 483.690+ threat indicators**

---

### What's New

- Complete IoC pipeline: fetch → validate → normalize → score → dedup → output
- 16 output formats (NextDNS, AdGuard, Pi-hole, dnsmasq, Unbound, RPZ, Technitium, MikroTik, nftables, ipset, Suricata, CrowdSec, CSV, JSON, YAML, SQLite)
- Cross-type deduplication with quality-score-aware resolution
- RFC6761 compliant reserved domain handling
- 330 tests passing, ruff clean, mypy clean

### Bug Fixes

- Reserved domain false positives resolved
- IPv6/IPv4 address family separation for nftables and MikroTik
- HTTP client lifecycle and error handling improvements

### Statistics

| Metric | Value |
|--------|-------|
| IoC Output Formats | 16 |
| Total IoCs Fetched | ~483.690 |
| Final IoCs (after dedup) | ~479.000 |
| Test Suite | 330 tests passing |

**Full Changelog**: https://github.com/bayraktarozcan/TC-SGB-API-to-List/releases/tag/v0.1.0.0

---

<a id="-türkçe"></a>

## TC-SGB-API-to-List v0.1.0.0

> **İlk kamuya açık sürüm — 16 çıktı biçimi ve 483.690'dan fazla tehdit göstergesi ile tam IoC hattı**

---

### Yenilikler

- Tam IoC hattı: çek → doğrula → normalleştir → puanla → tekilleştir → çıktı
- 16 çıktı biçimi (NextDNS, AdGuard, Pi-hole, dnsmasq, Unbound, RPZ, Technitium, MikroTik, nftables, ipset, Suricata, CrowdSec, CSV, JSON, YAML, SQLite)
- Kalite puanını dikkate alan çözümleme ile çapraz tür tekilleştirme
- RFC6761 uyumlu ayrılmış alan adı işleme
- 330 test geçiyor, ruff temiz, mypy temiz

### Hata Düzeltmeleri

- Ayrılmış alan adı yanlış pozitifleri çözüldü
- nftables ve MikroTik için IPv6/IPv4 adres ailesi ayrımı
- HTTP istemcisi yaşam döngüsü ve hata işleme iyileştirmeleri

### İstatistikler

| Metrik | Değer |
|--------|-------|
| IoC Çıktı Formatı Sayısı | 16 |
| Çekilen Toplam IoC | ~483.690 |
| Nihai IoC (tekilleştirmeden sonra) | ~479.000 |
| Test Paketi | 330 test geçiyor |

**Tam Değişiklik Günlüğü**: https://github.com/bayraktarozcan/TC-SGB-API-to-List/releases/tag/v0.1.0.0
````
