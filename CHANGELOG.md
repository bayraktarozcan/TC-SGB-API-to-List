[English](#-english) | [Türkçe](#-türkçe)

<a id="-english"></a>

# Changelog

All notable changes to this project will be documented in this file.
The format is based on [Keep a Changelog](https://keepachangelog.com/).

## [v0.1.0.0] — 2026-07-27

### Added

- Complete IOC pipeline: fetch → validate → normalize → score → dedup → output
- 17 output formats: NextDNS, AdGuard, Pi-hole, dnsmasq, Unbound, RPZ, Technitium, MikroTik, nftables, ipset, Suricata, CSV, JSON, YAML, SQLite, STIX 2.1, MISP
- Async API client with retry logic and rate limiting
- Pydantic data models for IOC validation
- Quality scoring system for false-positive risk assessment
- Cross-type deduplication (domain↔URL bidirectional)
- IDN/Punycode normalization for internationalized domains
- RFC6761 compliant reserved domain handling
- CLI commands: `fetch`, `generate`, `stats`, `validate`, `health`
- CI/CD with GitHub Actions (CI, scheduled pipeline, CodeQL)
- 330 tests passing, ruff clean, mypy clean
- Bilingual documentation (English/Turkish) — 22 wiki pages
- GitHub Pages landing page

### Fixed

- Broken `.venv` recreation with proper pyvenv.cfg
- Missing `pytest-asyncio` and `types-PyYAML` dependencies
- Dead entry point in pyproject.toml
- `.env.example` with correct SGB API settings (no auth required)
- httpx AsyncClient missing `follow_redirects`
- `test.com` false positive in validator (RFC6761 reserved domain)
- YAML dumper type annotation (`type[yaml.SafeDumper]`)
- nftables/MikroTik IPv6 in IPv4 sets split into separate address families
- `--max-records 0` now correctly fetches all records
- SQLite table name standardized to `iocs`

### Changed

- Badge URLs corrected to `bayraktarozcan/TC-SGB-API-to-List`
- Pipeline order: Fetch → Validate → Normalize → Score → Dedup
- `docs/` renamed to `wiki/` for GitHub Wiki usage
- CLI command `pipeline` renamed to `fetch`
- Output directory tracked in git via Git LFS

---

<a id="-türkçe"></a>

# Değişiklik Günlüğü

Bu projedeki tüm dikkat çekici değişiklikler bu dosyada belgelenecektir.
Format, [Keep a Changelog](https://keepachangelog.com/)'a dayanmaktadır.

## [v0.1.0.0] — 2026-07-27

### Eklenen

- Tam IOC hattı: çek → doğrula → normalleştir → puanla → tekilleştir → çıktı
- 17 çıktı formatı: NextDNS, AdGuard, Pi-hole, dnsmasq, Unbound, RPZ, Technitium, MikroTik, nftables, ipset, Suricata, CSV, JSON, YAML, SQLite, STIX 2.1, MISP
- Yeniden deneme mantığı ve hız sınırlaması ile asenkron API istemcisi
- IOC doğrulama için Pydantic veri modelleri
- Yanlış pozitif risk değerlendirmesi için kalite puanlama sistemi
- Çapraz tür tekilleştirme (alan adı↔URL çift yönlü)
- Uluslararası alan adları için IDN/Punycode normalleştirmesi
- RFC6761 uyumlu ayrılmış alan adı işleme
- CLI komutları: `fetch`, `generate`, `stats`, `validate`, `health`
- GitHub Actions ile CI/CD (CI, zamanlanmış hat, CodeQL)
- 330 test geçiyor, ruff temiz, mypy temiz
- Çift dilli dokümantasyon (İngilizce/Türkçe) — 22 wiki sayfası
- GitHub Pages açılış sayfası

### Düzeltilen

- Kırık `.venv` yeniden oluşturma (doğru pyvenv.cfg ile)
- Eksik `pytest-asyncio` ve `types-PyYAML` bağımlılıkları
- pyproject.toml'da ölü giriş noktası
- `.env.example` doğru SGB API ayarlarıyla (kimlik doğrulama gerekmez)
- httpx AsyncClient'da eksik `follow_redirects`
- Validator'da `test.com` yanlış pozitifi (RFC6761 ayrılmış alan adı)
- YAML dumper tip notasyonu (`type[yaml.SafeDumper]`)
- nftables/MikroTik IPv6, IPv4 kümelerinden ayrı ailelere bölündü
- `--max-records 0` artık tüm kayıtları doğru şekilde çekiyor
- SQLite tablo adı `iocs` olarak standardize edildi

### Değiştirilen

- Rozet URL'leri `bayraktarozcan/TC-SGB-API-to-List` olarak düzeltildi
- Hat sırası: Çek → Doğrula → Normalleştir → Puanla → Tekilleştir
- `docs/` GitHub Wiki kullanımı için `wiki/` olarak yeniden adlandırıldı
- CLI komutu `pipeline` → `fetch` olarak yeniden adlandırıldı
- Çıktı dizini Git LFS ile git'te izleniyor
