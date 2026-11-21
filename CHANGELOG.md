<!-- guard-exempt: historical-record -->
[English](#-english) | [Türkçe](#-türkçe)

<a id="-english"></a>

# Changelog

All notable changes to this project will be documented in this file.
The format is based on [Keep a Changelog](https://keepachangelog.com/).

## [Unreleased]

### Added

- **EOL-aware Python floor automation** — `.github/workflows/python-floor.yml` reads the Python core team's release calendar (`https://peps.python.org/api/release-cycle.json`) weekly and opens an auto-merge PR when the oldest supported minor advances beyond the declared floor. `Scripts/bump_python_floor.py` resolves the floor, refuses downgrades, retries transient network failures, and updates every declaration; `Tests/test_python_floor.py` pins parity across the manifest, CI matrices, mypy target and documentation.
- **Canonical release records** — `.github/release-bodies/` holds the title and bilingual body for every release, generated from this changelog; `Tests/test_release_notes.py` pins title shape, section parity and absence of bare issue tokens. All nine releases on both hosts were rewritten to this source.
- **Text hygiene guards** — every tracked text file now ends with LF, enforced by `Tests/test_repo_conventions.py::TestFinalNewline`; the release-note guard now checks every changelog bullet, not only the first three.

## [v0.3.2.2] — 2026-11-21

### Changed

- **Documentation consistency (EN+TR)** — corrected heading title case in troubleshooting, planning and privacy docs, refreshed stale test counts (`487`/`650` → `728`) and the agent-guide coverage baseline (`~97%` → `~99%`), and mirrored the agent-guide corrections with a refreshed `sync-sha`.
- **Release records completed** — the v0.3.2.1 changelog now covers the full tag diff (`Added` section plus the missing fetch, feed, automation and housekeeping fixes), and the published release notes now declare the `filter-lists` URL move as a breaking change and record the Azerbaijani feed retirement.

### Fixed

- **Historical CHANGELOG defect** — the duplicate `### Changed` heading in v0.3.2.0 was merged and the superseded weekday schedule entry was folded into the final daily-schedule bullet, with the transition documented in both languages.

## [v0.3.2.1] — 2026-11-21

### Added

- **Publication safety policy** — `Scripts/src/safety.py` applies a shared verdict gate (`decide_host`) to both the main TC-SGB line and the external-feed mirrors, with `Tests/test_safety.py` pinning the verdicts; high-impact hosts are rejected, shared user-content infrastructure is held for review, and every held indicator is written to a per-feed audit file instead of being dropped silently.
- **Third-party feed mirrors** — CERT.PL (Poland) and CERT.SI (Slovenia) lists are fetched, validated, and published to the `filter-lists` branch; the existing TC-SGB list is `01`, and the mirrors use country-prefixed, ordered filenames.
- **Country-prefixed titles** — external filter-list entries carry pipe-separated country titles and ordered filenames instead of the former `Blocklist` suffix.
- **Local mirror verifier** — `Scripts/verify_mirror.py` checks the EN/TR agent-guide pair mechanically (hash marker, section count, heading depth sequence, code fences, tables, action-checklist order) and ships a fixture suite for the drift classes.

### Changed

- **CI dependency policy: always-latest** — version pinning was removed from `AGENTS.md`; third-party GitHub Actions now use `@main`/`@master` or floating major tags, Docker images use `latest`, and the repository setting `sha_pinning_required` is `false` so non-SHA refs pass workflow validation. The same rule is recorded in the Turkish mirror with a matching `sync-sha`.
- **Python CI matrix** — CI now tests Python 3.11 (compatibility floor) plus the latest 3.x on both GitHub Actions and GitLab; the floor in `pyproject.toml` is unchanged.
- **Dependency-update tooling removed** — `deps-update.yml`, `sync_deps.py`, `requirements.in`, `requirements-dev.in`, and `requirements-dev.txt` were deleted. They existed only to compile and refresh pinned snapshots that no consumer used; every CI job installs from `pyproject.toml` with `pip install -e ".[dev]"`, so the weekly compile-and-PR cycle was dead weight. `requirements.txt` is kept as an unpinned `@latest` runtime list.
- **Runtime dependencies unpinned in `pyproject.toml`** — `httpx`, `pydantic`, `python-dotenv`, and `pyyaml` no longer carry `==` pins; `pip install -e .` resolves to the latest compatible versions, matching the always-latest policy. `requirements.txt` is also unpinned (`@latest` semantics), not a compiled snapshot.
- **Gitleaks resolves the latest release at runtime** — the GitLab `secret-scan` job queries the GitHub releases API for the newest tag, downloads that release's binary, and verifies it against the release's own `checksums.txt`; no static version or hash is embedded, so the scan stays current for the lifetime of the project.
- **Python toolchain follows latest** — single-version jobs (lint, auto-merge, scheduled fetch) use `3.x`; the GitLab default image is `python:slim`; the `3.11` entry remains only as the deliberate compatibility-floor leg of the test/build matrix.
- **Dependabot/branch-ref clarification** — `AGENTS.md` no longer claims Dependabot bumps branch-based action refs (Dependabot updates version numbers/commit identifiers, not `@main`); branch refs self-update from upstream, while the `github-actions` ecosystem stays configured for any future version-pinned ref.
- **Audit-consistency sweep across docs/manifests** — removed stale pinning prescriptions from `AGENTS.md` (obsolete pip-audit ignores, "no transitive lockfile" bypass, source-of-truth pointers) and from `Docs/Security-Analysis.md`, `Risk-Analysis.md`, `Threat-Model.md`, `Maintenance-Plan.md`, `Performance-Strategy.md` (EN+TR): always-latest policy, branch-based action refs, regenerated lock snapshots, removed retired `rich` dependency and non-existent Snyk/safety tooling examples. A later pass removed the compiled-snapshot model entirely (see above). Merged duplicate `Fixed`/`Düzeltilen` headings in this changelog and restored Keep a Changelog section order. Follow-up sweep fixed residual artifacts from that pass (`deps-updatet` token, half-updated EN/TR parity rows, leftover Snyk/`safety check` references, `@v3` codecov example, specific `3.11.7` patch in Performance-Strategy samples). Other version examples in regression and publishing docs are illustrative JSON fixtures and remain unchanged.

### Removed

- **Azerbaijan feed retired from scope** — the `blacklist.gov.az` list proved unreliable and unsuitable for a curated blocklist, so it is no longer fetched, validated, or published; `03-azerbaycan-blacklist_adguard.txt` is dropped from the `filter-lists` branch. The publication safety policy, per-feed audits, and the `validate-external` gate it was introduced with keep running for the remaining feeds.
- **BREAKING (data mirror): list order fixed** — Slovenia takes the freed `03` slot (`05-slovenya-certsi_adguard.txt` → `03-slovenya-certsi_adguard.txt`), so numbering runs 01–03 with `04` still reserved for Lithuania, whose source sits behind a Cloudflare challenge and cannot be fetched yet. Subscribers to the raw `filter-lists` branch must update the Slovenian URL; the package API is unchanged.

### Fixed

- **GitHub Actions `startup_failure` on non-SHA refs** — resolved by disabling `sha_pinning_required`; all workflows (CI, CodeQL, Mirror, Deploy, scheduled fetch, link check) now start and complete.
- **GitLab `link-check` job** — lychee runs with an empty entrypoint (the GitLab-generated shell script was being read as a config file); the Cisco EULA URL, which returns 403 to bots, is excluded in both the GitHub and GitLab link-check configurations.
- **CI `pip-audit` gate** — setuptools is upgraded before `pip-audit` in the CI security job so known advisories do not block the build. The weekly update PR that originally needed this was later removed with the compiled-snapshot tooling.
- **S3 service roots no longer blocked wholesale** — a URL indicator could be promoted to its host (`||s3.amazonaws.com^`), blocking every bucket on the endpoint. Shared S3 service endpoints are now recognised by the safety policy, so a URL on one is never promoted to a host rule; bucket-specific hosts remain eligible.
- **Fetch pagination** — the server's `pageCount`/`totalCount` metadata is no longer trusted, so every API page is fetched even when the server reports a smaller count.
- **Missing external feed files** — an unreachable or absent feed file is skipped with a `skipped` verdict instead of failing the whole publish gate.
- **Scheduled automation hardening** — valid `scheduled-fetch-*` branch names, rebase instead of merge for scheduled and Dependabot PR branches, Türkiye-time labels in commit messages, and the `filter-lists` branch mirrored to GitLab.
- **Housekeeping** — the duplicate lowercase `Output/blocklists` tree was removed, and best-effort validator parsing now uses `contextlib.suppress`.

## [v0.3.2.0] — 2026-10-12

### Added

- **Environment-driven configuration** — the CLI honors `TC_SGB_LOG_LEVEL` and `TC_SGB_OUTPUT_DIR` (`--output` falls back to the environment variable, then to `Output`)
- **IoC spelling guard** — `Tests/test_repo_conventions.py::TestIocSpelling` pins the single standard spelling across the tracked tree (banned forms stored split so the guard never names them; CHANGELOG history and the AGENTS.md rule quote stay out of scope)

### Changed

- **IoC is the single standard spelling** — `IOCType` → `IoCType`, `ValidatedIOC` → `ValidatedIoC`, `NormalizedIOC` → `NormalizedIoC`, `ScoredIOC` → `ScoredIoC` (plus test classes, doc snippets, JSON Schema descriptions, and issue/PR templates); `AGENTS.md` now records the rule so the spelling holds by convention and by test
- **GitLab CI re-enabled with badges** — after completing the account-level identity verification, project-level CI/CD is on again, so `.gitlab-ci.yml` pipelines run on GitLab shared runners; the GitLab-native pipeline and coverage badges were restored in the project and in the README
- **Daily schedule** — the scheduled fetch pipeline now runs every day at 19:00 UTC (`cron: "0 19 * * *"`), superseding the weekday 06:00 UTC cadence (`cron: "0 6 * * 1-5"`) introduced earlier in this release cycle.
- **`health --retries` aligned** — now defaults to 5, matching `fetch`/`stats`/`validate`
- **Privacy statement strengthened** — `PRIVACY.md` now states explicitly that the project collects, stores, sells, or shares no user data and is committed to maintaining that stance, and asks users to review the SGB website's policies periodically as rules can change
- **Governance files** — `NOTICE` added with dependency license attributions; `CODEOWNERS` (moved to the repository root) now also requires owner review for `tests/` and root-level docs
- **Dual-language coverage completed** — `pull_request_template.md` and `AGENTS.md` now use the repo's `[English] | [Türkçe]` two-section structure, matching README, CHANGELOG, wiki pages, and the other root docs
- **Only the latest release supported** — whenever a new version is published, every previous release is immediately deprecated and marked `[DEPRECATED]` in its GitHub release title; `SECURITY.md` and the release-note template now state that only the latest release receives fixes, and the rolling `ioc-data` release is exempt because it always hosts the current dataset

### Fixed

- **`or` swallowed falsy flags** — `AsyncAPIClient(max_retries=0)` / `rate_limit=0` / `timeout=0` are now respected (`is not None` guards), so rate limiting can be genuinely disabled
- **IDN/punycode domains were dropped** — validation now IDNA-encodes before domain checks and accepts `xn--…` TLDs, so unicode international domains pass validation instead of being rejected before normalization
- **`--skip-validation` mistyped IoCs** — skipped records keep an inferred type (IP, IP6, URL, …) instead of being stamped as DOMAIN unconditionally
- **Metadata lost on cross-type dedup** — when a higher-scored URL replaces a domain, the domain's metadata is merged into the replacement
- **Logging used f-string interpolation** — logger calls now use lazy `%`-style args, enforced by ruff `G004`
- **GitLab coverage badge misread the TOTAL line** — the coverage regex matched greedily and captured a single digit (`9` → `9.0%`); it now anchors on the pytest `TOTAL` summary line and reads `99%`

## [v0.3.1.0] — 2026-09-10

### Added

- **Deterministic output timestamps** — `generate_adguard`, `generate_rpz`, `generate_technitium` and `generate_suricata` accept an optional `generated_at`; when absent the timestamp falls back to the newest IoC `date`, so outputs are byte-stable for identical input sets (no more time-of-run flakiness in regression tests)
- **New tests**: +25 — `value`-shape `validate` records, API-fetch branch, skip-validation and `max_criticality` branches, client reopen-after-close, canonical cross-type dedup, non-mutating metadata merge, helper coverage (477 tests passing)

### Changed

- **Weekly cadence everywhere** — README (EN+TR), `docs/index.html` (EN+TR), wiki, and the scheduled-release note now state the weekly Friday 22:00 UTC schedule instead of the stale "every 6 hours"
- **`cmd_validate` is resilient** — accepts both API (`url`) and fetch-snapshot (`value`) record shapes, skips non-dict/malformed records with a warning instead of crashing the whole run, and fails with a clear error on non-list JSON
- **No overlapping scheduled runs** — `schedule.yml` gained a `concurrency` group so a new fetch waits for the previous one instead of running in parallel
- **Cross-type dedup canonicalization** — the domain index lower-cases and strips trailing dots (`EVIL.COM.` ≡ `evil.com`); `_merge_metadata` now returns a copy and never mutates its inputs
- **CLI polish** — parser `prog` is now `tc-sgb`; `--formats` tolerates whitespace around comma-separated values

### Fixed

- **`PipelineStats.summary()` ordering** — "After dedup" was printed before "After quality"; the quality stage now prints in its real pipeline position
- **Unused mypy override removed** — the `tests.*` section that mypy flagged as unused

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

## [Yayınlanmamış]

### Eklenen

- **Python alt sınırı için EOL otomasyonu** — `.github/workflows/python-floor.yml`, Python çekirdek ekibinin yayın takvimini (`https://peps.python.org/api/release-cycle.json`) haftalık okur ve desteklenen en eski küçük sürüm bildirilen alt sınırı geçtiğinde otomatik birleştirme PR'ı açar. `Scripts/bump_python_floor.py` alt sınırı çözer, düşürmeyi reddeder, geçici ağ hatalarını yeniden dener ve tüm bildirimleri günceller; `Tests/test_python_floor.py` bildirim, CI matrisleri, mypy hedefi ve dokümantasyon arasındaki pariteyi sabitler.
- **Kanonik yayın kayıtları** — `.github/release-bodies/`, bu değişiklik günlüğünden üretilen her yayının başlığını ve iki dilli gövdesini tutar; `Tests/test_release_notes.py` başlık biçimini, bölüm eşliğini ve çıplak issue belirteçlerinin olmamasını sabitler. İki hosttaki dokuz yayın da bu kaynağa göre yeniden yazıldı.
- **Metin hijyen bekçileri** — izlenen her metin dosyası artık LF ile bitiyor; `Tests/test_repo_conventions.py::TestFinalNewline` bunu sabitler. Yayın notu bekçisi artık değişiklik günlüğündeki yalnızca ilk üç maddeyi değil, tüm maddeleri denetler.

## [v0.3.2.2] — 2026-11-21

### Değiştirilen

- **Dokümantasyon tutarlılığı (EN+TR)** — sorun giderme, planlama ve gizlilik belgelerindeki başlık büyütmesi düzeltildi; bayat test sayıları (`487`/`650` → `728`) ve ajan kılavuzu kapsama temel değeri (`~%97` → `~%99`) güncellendi; ajan kılavuzu düzeltmeleri aynaya yansıtılıp `sync-sha` yenilendi.
- **Sürüm kayıtları tamamlandı** — v0.3.2.1 günlüğü artık tüm etiket farkını kapsıyor (`Eklenen` bölümü ve eksik çekme, akış, otomasyon ve temizlik düzeltmeleri); yayımlanan sürüm notları `filter-lists` URL taşınmasını kırıcı değişiklik olarak bildiriyor ve Azerbaycan akışının kaldırılmasını kaydediyor.

### Düzeltilen

- **Tarihsel CHANGELOG kusuru** — v0.3.2.0'daki yinelenen `### Değiştirilen` başlığı birleştirildi ve geçersiz kılınan hafta içi zamanlama maddesi nihai günlük zamanlama maddesine dahil edilip geçiş her iki dilde belgelendi.

## [v0.3.2.1] — 2026-11-21

### Eklenen

- **Yayımlama güvenlik politikası** — `Scripts/src/safety.py`, hem TC-SGB ana hattına hem harici akış aynalarına paylaşılı karar kapısı (`decide_host`) uygular; `Tests/test_safety.py` kararları sabitledir. Yüksek etkili ana makineler reddedilir, paylaşımlı kullanıcı içeriği altyapısı incelemeye alınır ve tutulan her gösterge sessizce düşürülmek yerine akış başına denetim dosyasına yazılır.
- **Üçüncü taraf akış aynaları** — CERT.PL (Polonya) ve CERT.SI (Slovenya) listeleri çekilir, doğrulanır ve `filter-lists` dalında yayımlanır; mevcut TC-SGB listesi `01`'dir ve aynalar ülke önekli, sıralı dosya adları kullanır.
- **Ülke önekli başlıklar** — harici filtre listesi girdileri artık eski `Blocklist` son eki yerine boru ayracıyla ayrılmış ülke başlıkları ve sıralı dosya adları taşır.
- **Yerel ayna doğrulayıcısı** — `Scripts/verify_mirror.py`, EN/TR ajan kılavuzu çiftini mekanik olarak denetler (sağlama işareti, bölüm sayısı, başlık derinliği sırası, kod blokları, tablolar, eylem denetim listesi sırası) ve süren sınıfı sabitleme dosyalarıyla birlikte gelir.

### Değiştirilen

- **CI bağımlılık politikası: her daim en güncel** — `AGENTS.md`'den sürüm sabitleme kuralı kaldırıldı; üçüncü taraf GitHub Actions artık `@main`/`@master` veya kayan büyük sürüm etiketleri, Docker görüntüleri `latest` kullanıyor ve depo ayarı `sha_pinning_required` değeri `false`, böylece SHA olmayan ref'ler iş akışı doğrulamasından geçiyor. Aynı kural Türkçe aynada eşleşen `sync-sha` ile kayıtlı.
- **Python CI matrisi** — CI artık hem GitHub Actions hem GitLab'da Python 3.11 (uyumluluk alt sınırı) ve en güncel 3.x sürümünü sınıyor; `pyproject.toml` içindeki alt sınır değişmedi.
- **Bağımlılık güncelleme araçları kaldırıldı** — `deps-update.yml`, `sync_deps.py`, `requirements.in`, `requirements-dev.in` ve `requirements-dev.txt` silindi. Bunlar yalnızca hiçbir tüketicisi olmayan pin'li anlık görüntüleri derlemek ve yenilemek için vardı; tüm CI işleri `pip install -e ".[dev]"` ile `pyproject.toml`'dan kuruyor, dolayısıyla haftalık derleme-PR döngüsü gereksizdi. `requirements.txt` pin'siz bir `@latest` çalışma zamanı listesi olarak korundu.
- **Çalışma zamanı bağımlılıkları `pyproject.toml`'da sabitlenmedi** — `httpx`, `pydantic`, `python-dotenv` ve `pyyaml` artık `==` pin'i taşımıyor; `pip install -e .` en güncel uyumlu sürümleri çözüyor, bu da her daim en güncel politikasıyla eşleşiyor. `requirements.txt` de pin'sizdir (`@latest` semantiği), derlenmiş anlık görüntü değildir.
- **Gitleaks en güncel sürümü çalışma zamanında çözüyor** — GitLab `secret-scan` işi GitHub releases API'sinden en yeni etiketi sorgular, o sürümün ikilisini indirir ve sürümün kendi `checksums.txt` dosyasıyla doğrular; statik sürüm veya hash gömülmediği için tarama projenin tüm yaşam döngüsü boyunca güncel kalır.
- **Python araç zinciri en günceli izliyor** — tek sürümlü işler (lint, auto-merge, zamanlanmış çekim) artık `3.x` kullanıyor; GitLab varsayılan görüntüsü `python:slim`; `3.11` girişi yalnızca test/derleme matrisindeki kasıtlı uyumluluk-alt-sınır bacağı olarak kalıyor.
- **Dependabot/dal-ref açıklaması** — `AGENTS.md` artık Dependabot'ın dal tabanlı eylem ref'lerini yükselttiğini iddia etmiyor (Dependabot sürüm numarası/commit tanıtıcısı günceller, `@main`'i değil); dal ref'leri yukarı akıştan kendiliğinden güncellenir, `github-actions` ekosistemi ise gelecekteki sürüm sabitli ref'ler için yapılandırılmış kalır.
- **Doküman/bildirim denetim uyumu** — `AGENTS.md` (bayat pip-audit ignore'ları, "geçişli kilit dosyası yok" bypass'ı, doğruluk kaynağı işaretleri) ve `Docs/Security-Analysis.md`, `Risk-Analysis.md`, `Threat-Model.md`, `Maintenance-Plan.md`, `Performance-Strategy.md` dosyalarındaki (EN+TR) sabitleme talimatları her daim en güncel politikasıyla uyumlu hale getirildi: dal tabanlı eylem ref'leri, kaldırılmış `rich` bağımlılığı ve var olmayan Snyk/safety örnekleri temizlendi. Sonraki bir geçişte derlenmiş anlık görüntü modeli tamamen kaldırıldı (yukarıya bakın). Bu günlükteki yinelenen `Düzeltilen` başlıkları birleştirildi ve Keep a Changelog bölüm sırası düzeltildi. Takip taramasında o geçişin kalıntıları temizlendi (`deps-updatet` belirteci, yarım kalmış EN/TR parite satırları, kalan Snyk/`safety check` atıfları, `@v3` codecov örneği, Performance-Strategy örneklerindeki spesifik `3.11.7` yama sürümü). Regresyon ve yayın belgelerindeki diğer sürüm örnekleri açıklayıcı JSON sabitleridir, değiştirilmedi.

### Silinen

- **Azerbaycan akışı kapsamdan çıkarıldı** — `blacklist.gov.az` listesi güvenilir olmadığı ve seçkin bir engel listesi için uygun düşmediği için artık çekilmiyor, doğrulanmıyor veya yayımlanmıyor; `03-azerbaycan-blacklist_adguard.txt` dosyası `filter-lists` dalından çıkarıldı. Yayımlama güvenlik politikası, akış başına denetimler ve akışla birlikte gelen `validate-external` kapısı kalan akışlarda çalışmaya devam ediyor.
- **KIRICI (veri aynası): liste sırası düzeltildi** — Slovenya boşalan `03` numarasını aldı (`05-slovenya-certsi_adguard.txt` → `03-slovenya-certsi_adguard.txt`), böylece numaralandırma 01–03 arasında akıyor ve `04` hâlâ Litvanya için ayrılmış; kaynağının arkasında bir Cloudflare doğrulaması olduğu için henüz çekilemiyor. Ham `filter-lists` dalına abone olanlar Slovenya URL'sini güncellemeli; paket API'si değişmedi.

### Düzeltilen

- **SHA olmayan ref'lerde GitHub Actions `startup_failure`** — `sha_pinning_required` kapatılarak çözüldü; tüm iş akışları (CI, CodeQL, Mirror, Deploy, zamanlanmış çekim, bağlantı denetimi) artık başlıyor ve tamamlanıyor.
- **GitLab `link-check` işi** — lychee boş entrypoint ile çalışıyor (GitLab'in ürettiği kabuk betiği yapılandırma dosyası olarak okunuyordu); botlara 403 döndüren Cisco EULA URL'si hem GitHub hem GitLab bağlantı denetimi yapılandırmalarında hariç tutuluyor.
- **CI `pip-audit` kapısı** — CI güvenlik işinde `pip-audit` öncesinde setuptools yükseltiliyor, böylece bilinen uyarılar derlemeyi engellemiyor. Başlangıçta bunu gerektiren haftalık güncelleme PR'ı, derlenmiş anlık görüntü araçlarıyla birlikte daha sonra kaldırıldı.
- **S3 servis kökleri artık toptan engellenmiyor** — bir URL göstergesi ana makinesine yükseltilerek (`||s3.amazonaws.com^`) uçtaki tüm bucket'ları engelleyebiliyordu. Paylaşımlı S3 servis uçları artık güvenlik politikası tarafından tanınıyor; böyle bir uçtaki URL ana makine kuralına yükseltilmiyor, bucket'a özgü ana makineler kurala dönüşmeye devam ediyor.
- **Çekme sayfalaması** — sunucunun `pageCount`/`totalCount` üst verisi artık güvenilmez; sunucu daha küçük bir sayı bildirse de tüm API sayfaları çekilir.
- **Eksik harici akış dosyaları** — erişilemeyen veya var olmayan bir akış dosyası, tüm yayımlama kapısını başarısız kılmak yerine `skipped` kararıyla atlanır.
- **Zamanlanmış otomasyon sağlamlaştırması** — geçerli `scheduled-fetch-*` dal adları, zamanlanmış ve Dependabot PR dallarında birleştirme yerine rebase, commit iletilerinde Türkiye saati etiketi ve `filter-lists` dalının GitLab'a aynalanması.
- **Düzeltme** — yinelenen küçük harfli `Output/blocklists` ağacı kaldırıldı ve iyimser doğrulayıcı ayrıştırması `contextlib.suppress` kullanacak şekilde değiştirildi.

## [v0.3.2.0] — 2026-10-12

### Eklenen

- **Ortam değişkeniyle yapılandırma** — CLI, `TC_SGB_LOG_LEVEL` ve `TC_SGB_OUTPUT_DIR` değişkenlerini dikkate alır (`--output` önce ortam değişkenine, sonra `Output` dizinine düşer)
- **IoC yazım bekçisi** — `Tests/test_repo_conventions.py::TestIocSpelling` tek standart yazımı izlenen ağaç genelinde sabitler (yasak biçimler bekçinin kendini ihbar etmemesi için bölünmüş saklanır; CHANGELOG tarihi ve AGENTS.md kural alıntısı kapsam dışıdır)

### Değiştirilen

- **IoC tek standart yazımdır** — `IOCType` → `IoCType`, `ValidatedIOC` → `ValidatedIoC`, `NormalizedIOC` → `NormalizedIoC`, `ScoredIOC` → `ScoredIoC` (test sınıfları, doküman parçacıkları, JSON Schema açıklamaları ve issue/PR şablonları dahil); `AGENTS.md` artık kuralı kaydeder, böylece yazım hem gelenekle hem testle korunur
- **Günlük zamanlama** — zamanlanmış çekim hattı artık her gün 19:00 UTC'de çalışır (`cron: "0 19 * * *"`), bu da aynı sürüm döngüsünde daha önce getirilen hafta içi 06:00 UTC düzenini (`cron: "0 6 * * 1-5"`) geçersiz kılar.
- **GitLab CI rozetlerle yeniden etkin** — hesap düzeyindeki kimlik doğrulama tamamlandıktan sonra proje düzeyi CI/CD yeniden açıldı, böylece `.gitlab-ci.yml` hatları GitLab paylaşımlı koşucularında çalışır; GitLab yerel hat ve kapsama rozetleri projede ve README'de geri getirildi
- **`health --retries` hizalandı** — artık `fetch`/`stats`/`validate` ile eşleşecek şekilde varsayılan olarak 5
- **Gizlilik bildirimi güçlendirildi** — `PRIVACY.md` artık projenin hiçbir kullanıcı verisi toplamadığını, depolamadığını, satmadığını veya paylaşmadığını ve bu tutumu sürdürme taahhüdünü açıkça belirtir; kurallar değişebileceği için kullanıcılardan SGB web sitesinin politikalarını düzenli olarak gözden geçirmelerini ister
- **Yönetişim dosyaları** — bağımlılık lisansı atıflarıyla `NOTICE` eklendi; (depo köküne taşınan) `CODEOWNERS` artık `tests/` ve kök düzeyindeki dokümanlar için de sahip incelemesi gerektirir
- **İki dilli kapsam tamamlandı** — `pull_request_template.md` ve `AGENTS.md` artık deponun `[English] | [Türkçe]` iki bölümlü yapısını kullanır; README, CHANGELOG, wiki sayfaları ve diğer kök dokümanlarla eşleşir
- **Yalnızca en son sürüm desteklenir** — yeni bir sürüm yayınlandığında önceki tüm sürümler derhal kullanımdan kaldırılır ve GitHub sürüm başlıklarında `[DEPRECATED]` olarak işaretlenir; `SECURITY.md` ve sürüm notu şablonu artık yalnızca en son sürümün düzeltme aldığını belirtir ve yuvarlanan `ioc-data` release'i her zaman güncel veriyi barındırdığı için muaf tutulur

### Düzeltilen

- **`or` falsy bayrakları yutuyordu** — `AsyncAPIClient(max_retries=0)` / `rate_limit=0` / `timeout=0` artık dikkate alınır (`is not None` kontrolleri), böylece hız sınırlama gerçekten kapatılabilir
- **IDN/punycode alan adları düşürülüyordu** — doğrulama artık alan adı kontrollerinden önce IDNA kodlaması yapar ve `xn--…` TLD'lerini kabul eder, böylece unicode uluslararası alan adları reddedilmek yerine doğrulamayı geçer
- **`--skip-validation` IoC türlerini yanlış atıyordu** — atlanan kayıtlar koşulsuz DOMAIN olarak damgalanmak yerine çıkarımsal bir tür (IP, IP6, URL, …) korur
- **Çapraz tür tekilleştirmede meta veri kaybı** — daha yüksek puanlı bir URL bir alan adının yerini aldığında, alan adının meta verisi değiştirilen kayda birleştirilir
- **Günlükleme f-string interpolasyonu kullanıyordu** — logger çağrıları artık tembel `%`-stili argümanlar kullanır; ruff `G004` ile zorunlu kılınır
- **GitLab kapsama rozeti TOTAL satırını yanlış okuyordu** — kapsama regex'i açgözlü eşleşip tek bir rakam yakalıyordu (`9` → `9.0%`); artık pytest `TOTAL` özet satırına sabitlenir ve `99%` okur

## [v0.3.1.0] — 2026-09-10

### Eklenen

- **Deterministik çıktı zaman damgaları** — `generate_adguard`, `generate_rpz`, `generate_technitium` ve `generate_suricata` isteğe bağlı `generated_at` parametresini kabul eder; yoksa zaman damgası en yeni IoC `date` değerine döner, böylece aynı girdi kümesi için çıktılar bayt-bazlı kararlıdır (regresyon testlerinde artık çalışma-anı tutarsızlığı yok)
- **Yeni testler**: +25 — `value` biçimli `validate` kayıtları, API-çekme dalı, skip-validation ve `max_criticality` dalları, kapatma-sonrası yeniden açma, kanonik çapraz tür tekilleştirme, mutasyon yapmayan meta veri birleştirme, yardımcı fonksiyon kapsamı (477 test geçiyor)

### Değiştirilen

- **Haftalık hat düzeni her yerde** — README (EN+TR), `docs/index.html` (EN+TR), wiki ve zamanlanmış sürüm notu artık haftalık Cuma 22:00 UTC programını belirtiyor (eski "her 6 saatte bir" yerine)
- **`cmd_validate` artık dayanıklı** — hem API (`url`) hem de çekim-anlık görüntüsü (`value`) kayıt şekillerini kabul eder, dict olmayan/hatalı kayıtları tüm çalışmayı kırmak yerine uyarıyla atlar ve list olmayan JSON için net bir hata verir
- **Örtüşen zamanlanmış çalıştırma yok** — `schedule.yml` artık önceki çalıştırma bitmeden yenisi başlamasın diye `concurrency` grubuna sahip
- **Çapraz tür tekilleştirme kanonikleştirmesi** — alan adı dizini küçük harfe çevirir ve sondaki noktaları siler (`EVIL.COM.` ≡ `evil.com`); `_merge_metadata` artık bir kopya döndürür ve girdilerini asla değiştirmez
- **CLI cilası** — ayrıştırıcı `prog` değeri artık `tc-sgb`; `--formats` virgülle ayrılmış değerlerin etrafındaki boşlukları yok sayar

### Düzeltilen

- **`PipelineStats.summary()` sıralaması** — "After dedup" daha önce "After quality" satırından önce yazdırılıyordu; kalite aşaması artık gerçek hat konumunda görünüyor
- **Kullanılmayan mypy override kaldırıldı** — mypy'nin kullanılmadığını işaretlediği `tests.*` bölümü silindi

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
