[English](#-english) | [Türkçe](#-türkçe)

<a id="-english"></a>

# Changelog

All notable changes to this project will be documented in this file.
The format is based on [Keep a Changelog](https://keepachangelog.com/).

## [v0.2.0.1] — 2026-07-30

### Fixed

- **Mypy errors**: None-safe `base_url` resolution, `validated` redefinition, `python-dotenv` stub
- **Cross-type dedup logic**: domain→URL dedup sorted so domains are processed first
- **`.gitignore`**: `output500/` → `output/` (typo)
- **`pyproject.toml`**: removed unused `rich` dependency
- **`auto-merge.yml`**: missing `PR_URL` env var in Approve step, `--delete-branch` fallback
- **`ci.yml`**: `pip install -r requirements.txt` → `pip install -e ".[dev]"`
- **`schedule.yml`**: `--force` → `--force-with-lease`; `pip install -r requirements.txt` → `pip install -e .`
- **Release note**: format count 17→16, IoC count ~483.690

### Changed

- **index.html**: 32 occurrences of format count updated 17→16
- **Wiki pages**: 10 wiki files format count 17→16
- **`.env` loading**: `python-dotenv` eklendi, `load_dotenv()` in `_setup_logging()`
- **`min_quality_score` default**: `0.0` → `quality.DEFAULT_QUALITY_THRESHOLD` (20.0)
- **`skip_validation`**: implemented in `_stage_validate()`
- **`max_criticality`**: implemented in `_stage_quality()`
- **`merge_metadata`**: `_merge_metadata()` helper for source/desc/connectiontype
- **Private `_request` usage**: `client.fetch_address_count()` public method
- **`__init__.py`**: all main symbols re-exported (`__all__`)
- **Client env var support**: `AsyncAPIClient.__init__` reads `TC_SGB_*` env vars
- **Auto-merge workflow**: new `.github/workflows/auto-merge.yml`

## [v0.2.0.0] — 2026-07-30

### Added

- **100% test coverage** — 438 tests across 14 test files (mypy strict, ruff clean)
- **Comprehensive wiki documentation** — 20 bilingual (EN/TR) pages
- **Production-ready CLI** — `tc-sgb fetch`, `tc-sgb generate`, `tc-sgb stats`, `tc-sgb validate`, `tc-sgb health`
- **Standardized IoC casing** — RFC 9424 compliant throughout
- **Turkish i18n sweep** — grammar and orthography corrections across all docs

### Fixed

- Wiki stale class references removed (20 pages)
- Repository structure file counts corrected
- Version numbers aligned to v0.2.0.0
- Package name in wheel filename
- Sidebar stale "Audit Report" link
- English `.badge-version` text-transform override
- Footer LICENSE link now points to actual file (EN + TR)
- Turkish IoCları → tehdit göstergeleri (IoC)

### Changed

- Pipeline order: Fetch → Validate → Normalize → Score → Dedup
- Robust network error handling via httpx `TransportError`
- Expanded false-positive detection: private IPs, reserved domains, 50+ benign domains
- CodeQL v4, pytest 9.x compatible CI

## [v0.1.0.0] — 2026-07-27

### Added

- Complete IoC pipeline: fetch → validate → normalize → score → dedup → output
- 16 output formats: NextDNS, AdGuard, Pi-hole, dnsmasq, Unbound, RPZ, Technitium, MikroTik, nftables, ipset, Suricata, CrowdSec, CSV, JSON, YAML, SQLite
- Async API client with retry logic and rate limiting
- Pydantic data models for IoC validation
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
Biçim, [Keep a Changelog](https://keepachangelog.com/)'a dayanmaktadır.

## [v0.2.0.1] — 2026-07-30

### Düzeltilen

- **Mypy hataları**: None-safe `base_url`, `validated` yeniden tanımı, `python-dotenv` stub
- **Çapraz tür dedup sıralaması**: domain→URL işleme önceliği
- **`.gitignore`**: `output500/` → `output/` (yazım hatası)
- **`pyproject.toml`**: kullanılmayan `rich` bağımlılığı kaldırıldı
- **`auto-merge.yml`**: eksik `PR_URL` env değişkeni, `--delete-branch` fallback
- **`ci.yml`**: `pip install -r requirements.txt` → `pip install -e ".[dev]"`
- **`schedule.yml`**: `--force` → `--force-with-lease`; `pip install -r requirements.txt` → `pip install -e .`
- **Sürüm notu**: biçim sayısı 17→16, IoC sayısı ~483.690

### Değiştirilen

- **index.html**: 32 yerde biçim sayısı 17→16
- **Wiki sayfaları**: 10 wiki dosyasında biçim sayısı 17→16
- **`.env` yükleme**: `python-dotenv` eklendi, `load_dotenv()` `_setup_logging()` içinde
- **`min_quality_score` varsayılanı**: `0.0` → `quality.DEFAULT_QUALITY_THRESHOLD` (20.0)
- **`skip_validation`**: `_stage_validate()` içinde uygulandı
- **`max_criticality`**: `_stage_quality()` içinde uygulandı
- **`merge_metadata`**: `_merge_metadata()` helper ile eklendi
- **Private `_request`**: `client.fetch_address_count()` public metodu
- **`__init__.py`**: tüm ana semboller re-export edildi (`__all__`)
- **Client env var desteği**: `AsyncAPIClient.__init__` `TC_SGB_*` env değişkenlerini okur
- **Auto-merge workflow**: yeni `.github/workflows/auto-merge.yml`

## [v0.2.0.0] — 2026-07-30

### Eklenen

- **%100 test kapsaması** — 14 test dosyasında 438 test (mypy strict, ruff temiz)
- **Kapsamlı wiki dokümantasyonu** — 20 iki dilli (EN/TR) sayfa
- **Üretime hazır CLI** — `tc-sgb fetch`, `tc-sgb generate`, `tc-sgb stats`, `tc-sgb validate`, `tc-sgb health`
- **Standartize edilmiş IoC kullanımı** — RFC 9424 uyumlu
- **Türkçe dil düzeltmeleri** — tüm dokümanlarda dil bilgisi ve yazım düzeltmeleri

### Düzeltilen

- Wiki eski sınıf referansları kaldırıldı (20 sayfa)
- Depo yapısı dosya sayıları düzeltildi
- Sürüm numaraları v0.2.0.0 ile hizalandı
- Tekerlek dosyasındaki paket adı
- Kenar çubuğundaki güncel olmayan "Audit Report" bağlantısı
- `.badge-version` İngilizce metin dönüşümü
- Altbilgi LICENSE bağlantısı (EN + TR)
- IoCları → tehdit göstergeleri (IoC)

### Değiştirilen

- Hat sırası: Çek → Doğrula → Normalleştir → Puanla → Tekilleştir
- httpx `TransportError` ile güçlü ağ hata yönetimi
- Genişletilmiş yanlış pozitif tespiti: özel IP'ler, ayrılmış alan adları, 50+ bilinen iyi alan adı
- CodeQL v4, pytest 9.x uyumlu CI

## [v0.1.0.0] — 2026-07-27

### Eklenen

- Tam IoC hattı: çek → doğrula → normalleştir → puanla → tekilleştir → çıktı
- 16 çıktı biçimi: NextDNS, AdGuard, Pi-hole, dnsmasq, Unbound, RPZ, Technitium, MikroTik, nftables, ipset, Suricata, CrowdSec, CSV, JSON, YAML, SQLite
- Yeniden deneme mantığı ve hız sınırlaması ile asenkron API istemcisi
- IoC doğrulama için Pydantic veri modelleri
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
