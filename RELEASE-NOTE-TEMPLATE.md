[English](#-english) | [Türkçe](#-türkçe)

<a id="-english"></a>

# Release Note Template

> Copy the template below, replace placeholders with actual values, and use it when creating GitHub Releases.

> **MANDATORY: Every release MUST be bilingual (English + Turkish), following the same format as README.md.**
> All section headings, descriptions, tables, and code comments must appear in both languages.
> Use the combined template below — English block first, then Turkish block separated by `---`.

---

```markdown
## TC-SGB-API-to-List v{VERSION}

> **{ONE_LINE_HIGHLIGHT}**
>
> **{TEK_SATIR_VURGULAMA}**

---

### What's New / Yenilikler

{FEATURE_LIST}

### Improvements / İyileştirmeler

{IMPROVEMENT_LIST}

### Bug Fixes / Hata Düzeltmeleri

{BUG_FIX_LIST}

### Breaking Changes / Kırıcı Değişiklikler

{BREAKING_CHANGES_OR_NONE}

### Statistics / İstatistikler

| Metric | Value |
|--------|-------|
| IOC Output Formats | {N} |
| Total IOCs Fetched | ~{N} |
| Validated IOCs | ~{N} |
| Final IOCs (after dedup) | ~{N} |
| Test Suite | {N} tests passing |
| Type Safety | mypy clean |
| Lint | ruff clean |

### Installation / Kurulum

````bash
git clone https://github.com/bayraktarozcan/TC-SGB-API-to-List.git
cd TC-SGB-API-to-List
python -m venv .venv
.venv\Scripts\activate   # Windows
pip install -r requirements.txt
````

### Quick Start / Hızlı Başlangıç

````bash
python scripts/main.py fetch
python scripts/main.py generate --input output/raw_records.json
python scripts/main.py health
````

### Documentation / Dokümantasyon

- [Wiki](https://github.com/bayraktarozcan/TC-SGB-API-to-List/wiki)
- [Architecture / Mimari](https://github.com/bayraktarozcan/TC-SGB-API-to-List/wiki/Architecture)
- [API Analysis / API Analizi](https://github.com/bayraktarozcan/TC-SGB-API-to-List/wiki/API-Analysis)
- [Data Flow / Veri Akışı](https://github.com/bayraktarozcan/TC-SGB-API-to-List/wiki/Data-Flow)

---

**Full Changelog / Tam Değişiklik Günlüğü**: https://github.com/bayraktarozcan/TC-SGB-API-to-List/compare/{PREV_TAG}...v{VERSION}
```

---

### Example: v0.1.0.0

```markdown
## TC-SGB-API-to-List v0.1.0.0

> **Initial public release — Full IOC pipeline with 17 output formats and 490,000+ threat indicators**

---

### What's New

- Complete IOC pipeline: fetch → validate → normalize → score → dedup → output
- 17 output formats (NextDNS, AdGuard, Suricata, nftables, MikroTik, STIX 2.1, MISP, etc.)
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
| IOC Output Formats | 17 |
| Total IOCs Fetched | ~490,000 |
| Final IOCs (after dedup) | ~479,000 |
| Test Suite | 330 tests passing |

**Full Changelog**: https://github.com/bayraktarozcan/TC-SGB-API-to-List/releases/tag/v0.1.0.0
```

---

<a id="-türkçe"></a>

# Sürüm Notu Şablonu

> Aşağıdaki şablonu kopyalayın, yer tutucuları gerçek değerlerle değiştirin ve GitHub Release'leri oluştururken kullanın.

> **ZORUNLU: Her release bilingual (İngilizce + Türkçe) olmalıdır, README.md ile aynı format izlenmelidir.**
> Tüm bölüm başlıkları, açıklamalar, tablolar ve kod yorumları her iki dilde de yer almalıdır.
> Aşağıdaki birleşik şablonu kullanın — önce İngilizce blok, ardından `---` ile ayrılmış Türkçe blok.

---

```markdown
## TC-SGB-API-to-List v{SÜRÜM}

> **{TEK SATIR_VURGULAMA}**

---

### Yenilikler / Eklenenler

{ÖZELLİK_LISTESİ}

### İyileştirmeler / Değiştirilenler

{İYİLEŞTİRME_LISTESİ}

### Hata Düzeltmeleri / Düzeltilenler

{HATA_DÜZELTME_LISTESİ}

### Kırıcı Değişiklikler / Değişenler

{KIRICI_DEĞİŞİKLİKLER_Veya_YOK}

### İstatistikler / Sayılar

| Metrik | Değer |
|--------|-------|
| IOC Çıktı Formatı | {N} |
| Çekilen Toplam IOC | ~{N} |
| Doğrulanmış IOC | ~{N} |
| Nihai IOC (tekilleştirmeden sonra) | ~{N} |
| Test Paketi | {N} test geçiyor |
| Tip Güvenliği | mypy temiz |
| Lint | ruff temiz |

### Kurulum / Yükleme

````bash
git clone https://github.com/bayraktarozcan/TC-SGB-API-to-List.git
cd TC-SGB-API-to-List
python -m venv .venv
.venv\Scripts\activate   # Windows
pip install -r requirements.txt
````

### Hızlı Başlangıç / Başlangıç

````bash
python scripts/main.py fetch
python scripts/main.py generate --input output/raw_records.json
python scripts/main.py health
````

### Dokümantasyon / Belgeler

- [Wiki](https://github.com/bayraktarozcan/TC-SGB-API-to-List/wiki)
- [Mimari](https://github.com/bayraktarozcan/TC-SGB-API-to-List/wiki/Architecture)
- [API Analizi](https://github.com/bayraktarozcan/TC-SGB-API-to-List/wiki/API-Analysis)
- [Veri Akışı](https://github.com/bayraktarozcan/TC-SGB-API-to-List/wiki/Data-Flow)

---

**Tam Değişiklik Günlüğü**: https://github.com/bayraktarozcan/TC-SGB-API-to-List/compare/{ÖNCEKİ_ETİKET}...v{SÜRÜM}
```

---

### Örnek: v0.1.0.0

```markdown
## TC-SGB-API-to-List v0.1.0.0

> **İlk kamuya açık sürüm — 17 çıktı formatı ve 490.000'den fazla tehdit göstergesi ile tam IOC hattı**

---

### Yenilikler

- Tam IOC hattı: çek → doğrula → normalleştir → puanla → tekilleştir → çıktı
- 17 çıktı formatı (NextDNS, AdGuard, Suricata, nftables, MikroTik, STIX 2.1, MISP, vb.)
- Kalite puanı bilinçli çözümleme ile çapraz tür tekilleştirme
- RFC6761 uyumlu ayrılmış alan adı işleme
- 330 test geçiyor, ruff temiz, mypy temiz

### Hata Düzeltmeleri

- Ayrılmış alan adı yanlış pozitifleri çözüldü
- nftables ve MikroTik için IPv6/IPv4 adres ailesi ayrımı
- HTTP istemcisi yaşam döngüsü ve hata işleme iyileştirmeleri

### İstatistikler

| Metrik | Değer |
|--------|-------|
| IOC Çıktı Formatı | 17 |
| Çekilen Toplam IOC | ~490.000 |
| Nihai IOC (tekilleştirmeden sonra) | ~479.000 |
| Test Paketi | 330 test geçiyor |

**Tam Değişiklik Günlüğü**: https://github.com/bayraktarozcan/TC-SGB-API-to-List/releases/tag/v0.1.0.0
```
