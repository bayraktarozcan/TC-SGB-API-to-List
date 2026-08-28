[English](#-english) | [Türkçe](#-türkçe)

<a id="-english"></a>

# Changelog

All notable changes to this project will be documented in this file.
The format is based on [Keep a Changelog](https://keepachangelog.com/).

## [v0.3.0.0] — 2026-08-28

### Added

- **GitHub Pages via GitHub Actions** — new `deploy.yml` workflow deploys the site from `docs/` in ~22 seconds, bypassing the slow/hanging legacy Jekyll builder (previously 40+ minutes stuck)
- **New test files**: `tests/test_main.py` and `tests/test_outputs.py` added — 452 tests now passing

### Changed

- **GitHub Pages source** moved from repo root to `docs/`, fully isolating the 233 MB `output/` directory from the published site (IoCs served via the `ioc-data` rolling release, small formats still tracked in `output/`)
- **Large-format outputs** — `raw_records.json`, `threat_intel_json.json`, `threat_intel_sqlite.db`, `threat_intel_suricata.json`, `threat_intel_yaml.yaml` moved out of git (Git LFS removed). These five files are now distributed via the rolling GitHub Release `ioc-data` with stable URLs. Small formats stay tracked in `output/`.
- **GitHub Actions upgraded to Node 24** — `configure-pages@v6`, `upload-pages-artifact@v5`, `deploy-pages@v5` (removes Node 20 deprecation warnings)
- **Docs truth-anchor fixes** — IoC count aligned to 478,709, pipeline duration to ~6.2 min, architecture diagrams updated to the 16 real formats
- **Release note**: LFS line replaced with `ioc-data` rolling release guidance

### Fixed

- **Schedule workflow stability** — unique branch names for auto-merge PRs, supersede stuck PRs, keep branch up to date, AUTO_MERGE_TOKEN PAT for CI-on-PR, LFS-pointer-safe sqlite output
- **Pipeline duration/facts** — replaced fabricated 4.2s timings with measured pipeline times (fetch+process ~240s, 16-format export ~131s)

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

## [v0.3.0.0] — 2026-08-28

### Eklenen

- **GitHub Actions ile GitHub Pages** — yeni `deploy.yml` workflow'u siteyi `docs/`'tan ~22 saniyede dağıtır; yavaş/takılan eski Jekyll derleyicisini atlar (önceden 40+ dakika takılı kalıyordu)
- **Yeni test dosyaları**: `tests/test_main.py` ve `tests/test_outputs.py` eklendi — 452 test geçiyor

### Değiştirilen

- **GitHub Pages kaynağı** repo kökünden `docs/`'a taşındı; 233 MB'lık `output/` dizini yayınlanan siteden tamamen izole edildi (IoC'ler `ioc-data` yuvarlanan release aracılığıyla sunuluyor, küçük formatlar `output/` içinde izlenmeye devam ediyor)
- **Büyük biçim çıktıları** — `raw_records.json`, `threat_intel_json.json`, `threat_intel_sqlite.db`, `threat_intel_suricata.json`, `threat_intel_yaml.yaml` git'ten çıkarıldı (Git LFS kaldırıldı). Bu beş dosya artık stabil URL'lerle `ioc-data` yuvarlanan GitHub Release'i üzerinden dağıtılıyor. Küçük biçimler `output/` içinde izlenmeye devam ediyor.
- **GitHub Actions Node 24'e yükseltildi** — `configure-pages@v6`, `upload-pages-artifact@v5`, `deploy-pages@v5` (Node 20 deprecation uyarılarını kaldırır)
- **Dokümantasyon truth-anchor düzeltmeleri** — IoC sayısı 478,709'a, hat süresi ~6.2 dk'ya hizalandı, mimari diyagramlar gerçek 16 formata güncellendi
- **Sürüm notu**: LFS satırı `ioc-data` yuvarlanan release yönergesiyle değiştirildi

### Düzeltilen

- **Schedule workflow kararlılığı** — auto-merge PR'ları için benzersiz dal adları, takılan PR'ları aşma, dalı güncel tutma, PR'da çalışan CI için AUTO_MERGE_TOKEN PAT, LFS-pointer-güvenli sqlite çıktısı
- **Hat süresi/gerçekler** — uydurma 4.2s süreleri ölçülen hat süreleriyle değiştirildi (çek+işleme ~240s, 16-format dışa aktarma ~131s)

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
