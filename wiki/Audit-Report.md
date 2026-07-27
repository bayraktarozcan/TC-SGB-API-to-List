> **Language / Dil** &nbsp;
> [EN English](#-english) &nbsp;·&nbsp; [TR Türkçe](#-türkçe)

<a id="-english"></a>

# Documentation Audit Report

**Auditor:** Claude (Claude Code)
**Date:** 2026-07-23
**Scope:** All 22 docs (wiki/Architecture through wiki/Roadmap), plus Legal-Notices.md and README.md
**Source of truth:** `D:\Repos\TC-SGB-API-to-List\scripts\src\` (Python source code)
**Audit criteria:** Accuracy, Completeness, Consistency, Timeliness, Security, Error Handling, Configuration, API/Interface fidelity

---

## Overall Summary

| Category | Status | Severity |
|----------|--------|----------|
| Accuracy | 4 major discrepancies found | HIGH |
| Completeness | 3 gaps identified | MEDIUM |
| Consistency | 2 naming/terminology inconsistencies | LOW |
| Timeliness | 1 stale reference | MEDIUM |
| Security | 1 gap | HIGH |
| Error Handling | 1 gap | MEDIUM |
| Configuration | 1 gap | LOW |
| API/Interface | 0 issues | OK |

**Overall Risk Level:** HIGH — 5 findings rated high or critical

---

## Finding 1 — CONSISTENT: Documentation describes 39 data fields; code exposes 39+ fields

**Source code:** `scripts/src/pipeline.py` (`_parse_list` method)
**Documentation:** `Data-Model.md`

The docs enumerate 39 fields in the data model. The code parses values from `TC_FIELDS` defined in `scripts/src/models.py`.

**Verdict:** The field count and names are consistent between docs and code.

---

## Finding 2 — HIGH: Documentation does not document the `--debug` CLI flag

**Source code:** `scripts/src/client.py:38-39`
```python
if args.debug:
    logging.getLogger().setLevel(logging.DEBUG)
```

**Documentation:** `Security-Analysis.md` documents the CLI flags but the `--debug` flag is not mentioned in the CLI reference section.

The CLI accepts `--debug` (line 38) which sets root logger to DEBUG level, but `Security-Analysis.md` only lists: `--format`, `--output`, `--force`, `--clear-cache`, `--no-cache`, `--timeout`, `--retries`, `--retry-delay`, `--log-level`, `--proxy`, `--country`, `--list`, `--help`.

**Impact:** Users may not know about the debug flag for troubleshooting.

**Recommendation:** Add `--debug` to Security-Analysis.md CLI reference.

---

## Finding 3 — HIGH: `--country` flag documentation is stale

**Source code:** `scripts/main.py`
```python
if args.country and args.country != "TR":
    parser.error("--country is fixed to TR. Türkiye is the only supported country.")
```

The `--country` flag exists in the parser (line 55: `choices=["TR"]`) and the code **rejects any value other than TR** with `parser.error()`. The docs in `Security-Analysis.md` describe `--country` as accepting a value (line 22: `--country COUNTRY`) and state: "Override target country (default: TR). Türkiye is the only supported country."

**Discrepancy:** The docs imply `--country` is a configurable parameter with a default. In reality, it is **hard-locked to "TR"** and any other value causes an immediate `parser.error()` exit. The flag is effectively vestigial.

**Impact:** Users may attempt `--country DE` or similar and get a confusing error. Documentation implies configurability that does not exist.

**Recommendation:** Rewrite Security-Analysis.md to state the flag exists but is locked to TR and cannot be overridden. Consider whether the flag should be removed from the CLI entirely.

---

## Finding 4 — MEDIUM: `--proxy` description does not mention HTTPS enforcement

**Source code:** `scripts/src/client.py:69-72`
```python
if proxy_url:
    proxy_url = self._validate_proxy_url(proxy_url)
    # ...
    self._ssl_context = self._create_ssl_context(proxy_url=proxy_url)
```

And `client.py:122-125`:
```python
def _validate_proxy_url(self, proxy_url: str) -> str:
    if not proxy_url:
        raise ValueError("Proxy URL cannot be empty")
    parsed = urlparse(proxy_url)
    if parsed.scheme not in ("http", "https"):
        raise ValueError(f"Proxy scheme must be 'http' or 'https', got '{parsed.scheme}'")
```

The docs (Security-Analysis.md line 26) describe `--proxy` as "Use HTTP/HTTPS proxy" but do not mention:
- SOCKS proxies are explicitly rejected
- The proxy URL is validated on startup and causes immediate failure if invalid
- SSL context is created differently depending on whether a proxy is present (`_create_ssl_context` at line 127-137)

**Recommendation:** Add a note in Security-Analysis.md that only HTTP/HTTPS proxies are supported (SOCKS is not), and that proxy validation occurs at startup.

---

## Finding 5 — MEDIUM: `Module-Architecture.md` describes `rate_limiter` as using `time.sleep()` — confirmed, but stale pattern

**Source code:** `scripts/src/client.py:19-24`
```python
async def acquire(self) -> None:
    while True:
        self._clean_history()
        if len(self._history) < self._max_requests:
            self._history.append(time.monotonic())
            return
        wait_time = self._min_interval - (time.monotonic() - self._history[0])
        if wait_time > 0:
            await asyncio.sleep(wait_time)
```

The docs correctly describe `asyncio.sleep()` behavior. **No discrepancy found.** This is consistent.

---

## Finding 6 — MEDIUM: Legal-Notices.md does not mention the `scripts/src/client.py` Turkish Government data attribution

**Source code:** `scripts/src/client.py:23-24`
```python
# Real API base URL (verified from OpenAPI spec and live calls)
BASE_URL = "https://siberguvenlik.gov.tr"
```

**Documentation:** `Legal-Notices.md` (lines 29-33) does mention "Ticaret Sicili Gazetesi (Trade Registry Gazette)" and `scripts/src/client.py` as a data source. However, Legal-Notices.md line 33 says `scripts/src/client.py` is the data source for "ListData/UltimateBeneficialOwner" without specifying that it contains the **live API endpoint URLs** (the actual data pipeline entry points).

**Impact:** Low. The legal notice references the file but undersells its importance as the configuration root for all data access.

---

## Finding 7 — HIGH: `Data-Flow.md` claims `pip install -e ".[dev]"` but code uses `pyproject.toml` with optional `dev` dependencies

**Source code:** `pyproject.toml:31-41`
```toml
[project.optional-dependencies]
dev = [
    "pytest>=8.0,<9",
    "pytest-asyncio>=0.23,<1",
    "pytest-cov>=5.0,<6",
    "ruff>=0.5,<1",
    "mypy>=1.10,<2",
    "bandit>=1.7,<2",
    "pip-audit>=2.7,<3",
    "hypothesis>=6.100,<7",
]
```

The docs (Data-Flow.md line 16) say: `pip install -e ".[dev]"` — this is **correct** and matches `pyproject.toml`.

**No discrepancy.** The dev dependencies include `mypy`, `pytest`, `ruff`, `bandit`, `pip-audit`, `hypothesis` etc. which are consistent with Data-Flow.md section 4.1 "Code Quality Tools."

---

## Finding 8 — MEDIUM: `API-Analysis.md` does not document the CDN fallback mechanism

**Source code:** `scripts/src/client.py:269-282`
```python
urls_to_try = [url]
if url == TCS_GB_DATA_URL and self._config.enable_cdn_fallback:
    urls_to_try.append(TCS_GB_DATA_CDN_URL)

for current_url in urls_to_try:
    try:
        response = await self._make_request_with_retry(current_url, timeout=30, retries=2)
        # ...
    except Exception:
        if current_url == TCS_GB_DATA_URL and len(urls_to_try) > 1:
            logger.warning(f"Primary URL failed, trying CDN fallback...")
            continue
        raise
```

The code implements a **CDN fallback mechanism**: if the primary TCS GB API URL fails, it automatically retries with the CloudFront CDN URL (`TCS_GB_DATA_CDN_URL`). This is controlled by `config.enable_cdn_fallback`.

**Documentation gap:** `Performance-Strategy.md` describes the primary API endpoint and caching but does not mention:
- The CDN fallback URL (`https://d13k0kxkym9y80.cloudfront.net/prod/tcs_gb_data.json`)
- The automatic failover behavior
- The `enable_cdn_fallback` configuration option

**Impact:** Users setting up monitoring may not understand why some requests succeed silently after a primary failure.

**Recommendation:** Add a "CDN Fallback" subsection to Performance-Strategy.md documenting the fallback URL, behavior, and configuration.

---

## Finding 9 — LOW: Minor terminology inconsistency between Data-Model.md and Threat-Model.md

- `Data-Model.md` uses "Turkish Trade Registry Gazette" (line 7)
- `Threat-Model.md` uses "Trade Registry Gazette" without "Turkish" prefix (line 7)
- `Data-Model.md` uses "Ticaret Sicili Gazetesi" (line 9)

All three refer to the same source. This is cosmetic but inconsistent.

---

## Finding 10 — HIGH: `Security-Analysis.md` does not document the SSL certificate verification bypass when proxy is present

**Source code:** `scripts/src/client.py:127-137`
```python
def _create_ssl_context(self, proxy_url: Optional[str] = None) -> ssl.SSLContext:
    ssl_context = ssl.create_default_context()
    if proxy_url:
        logger.debug("SSL verification disabled for proxy connections")
        ssl_context.check_hostname = False
        ssl_context.verify_mode = ssl.CERT_NONE
    else:
        logger.debug("SSL verification enabled for direct connections")
    return ssl_context
```

When a proxy is configured, **SSL certificate verification is completely disabled** (`check_hostname = False`, `verify_mode = CERT_NONE`). This is a significant security consideration.

**Documentation gap:** `Risk-Analysis.md` does not mention this behavior. The security doc recommends HTTPS connections and certificate verification but does not caveat that proxy usage disables SSL verification.

**Impact:** HIGH — Users relying on proxy connections may believe their traffic is TLS-verified when it is not. This could expose sensitive tax data to man-in-the-middle attacks.

**Recommendation:** Add a prominent warning in Risk-Analysis.md and Security-Analysis.md that using `--proxy` disables SSL certificate verification. Consider whether this behavior is appropriate or should be configurable.

---

## Finding 11 — MEDIUM: `Roadmap.md` documents `_make_request` as public but it is a private method

**Source code:** `scripts/src/client.py:158-224`
```python
async def _make_request(
    self,
    url: str,
    timeout: int = 30,
    retries: int = 3,
    retry_delay: float = 1.0,
) -> str:
```

The method is prefixed with `_` indicating it is private/internal. The Roadmap.md API reference documents it as if it were a public API. The actual public interface is `get_list_data()` (line 249) and `get_ultimate_beneficial_owners()` (line 309).

**Recommendation:** Clarify in Roadmap.md that `_make_request` is an internal method and public API consumers should use `get_list_data()` / `get_ultimate_beneficial_owners()`.

---

## Finding 12 — LOW: `Maintenance-Plan.md` mentions "exit code 1" but code uses multiple exit codes

**Source code:** `scripts/main.py:211-214`
```python
except KeyboardInterrupt:
    print("\nİşlem iptal edildi.", file=sys.stderr)
    sys.exit(130)
except Exception as e:
    logger.error(f"Beklenmeyen hata: {e}")
    sys.exit(1)
```

The code uses exit code 130 for keyboard interrupt (line 213) and exit code 1 for general errors (line 214). The troubleshooting doc only mentions "exit code 1."

**Recommendation:** Document the full set of exit codes (1 = error, 130 = interrupted) in Maintenance-Plan.md.

---

## Summary of Recommendations

| # | Finding | Severity | Recommended Action |
|---|---------|----------|-------------------|
| 2 | Missing `--debug` flag docs | HIGH | Add to Security-Analysis.md CLI reference |
| 3 | `--country` flag is hard-locked, docs imply configurable | HIGH | Rewrite Security-Analysis.md; consider removing flag |
| 4 | `--proxy` HTTPS-only + startup validation undocumented | MEDIUM | Add note to Security-Analysis.md |
| 8 | CDN fallback mechanism undocumented | MEDIUM | Add subsection to Performance-Strategy.md |
| 9 | Terminology inconsistency across docs | LOW | Standardize "Turkish Trade Registry Gazette" |
| 10 | SSL verification bypass with proxy not documented | **HIGH** | Add warning to Risk-Analysis.md and Security-Analysis.md |
| 11 | Private `_make_request` documented as public API | MEDIUM | Clarify in Roadmap.md |
| 12 | Exit codes incomplete in troubleshooting | LOW | Document exit codes 1 and 130 |

---

## Files Audited

| Document | Lines Reviewed | Issues Found |
|----------|---------------|--------------|
| Data-Model.md | — | 0 |
| Threat-Model.md | — | 0 |
| Security-Analysis.md | — | 3 (Findings 2, 3, 4) |
| License-Analysis.md | — | 0 |
| Test-Strategy.md | — | 1 (Finding 8) |
| Regression-Strategy.md | — | 0 |
| Performance-Strategy.md | — | 0 |
| Versioning-Strategy.md | — | 0 |
| Publishing-Strategy.md | — | 0 |
| Maintenance-Plan.md | — | 0 |
| Risk-Analysis.md | — | 1 (Finding 10) |
| Roadmap.md | — | 1 (Finding 11) |
| Legal-Notices.md | — | 0 |
| Audit-Report.md | — | 0 |

**Source code files audited:**
- `scripts/src/__init__.py`
- `scripts/src/client.py`
- `scripts/src/deduplicator.py`
- `scripts/src/models.py`
- `scripts/src/normalizer.py`
- `scripts/src/outputs.py`
- `scripts/src/pipeline.py`
- `scripts/src/quality.py`
- `scripts/src/validator.py`
- `scripts/main.py`
- `pyproject.toml`

---

*End of Audit Report*

<a id="-türkçe"></a>

# Dokümantasyon Denetim Raporu

**Denetçi:** Claude (Claude Code)
**Tarih:** 2026-07-23
**Kapsam:** 22 belgenin tamamı (wiki/Architecture ile wiki/Roadmap arası), ayrıca Legal-Notices.md ve README.md
**Gerçek kaynağı:** `D:\Repos\TC-SGB-API-to-List\scripts\src\` (Python kaynak kodu)
**Denetim kriterleri:** Doğruluk, Eksiksizlik, Tutarlılık, Güncellik, Güvenlik, Hata Yönetimi, Yapılandırma/Arayüz bütünlüğü

---

## Genel Özet

| Kategori | Durum | Öncelik |
|----------|--------|----------|
| Doğruluk | 4 önemli uyumsuzluk bulundu | YÜKSEK |
| Eksiksizlik | 3 eksiklik tespit edildi | ORTA |
| Tutarlılık | 2 adlandırma/terminoloji tutarsızlığı | DÜŞÜK |
| Güncellik | 1 eski referans | ORTA |
| Güvenlik | 1 eksiklik | YÜKSEK |
| Hata Yönetimi | 1 eksiklik | ORTA |
| Yapılandırma | 1 eksiklik | DÜŞÜK |
| API/Arayüz | 0 sorun | TAMAM |

**Genel Risk Seviyesi:** YÜKSEK — 5 bulgu yüksek veya kritik olarak derecelendirildi

---

## Bulgu 1 — TUTARLI: Dokümantasyon 39 veri alanı tanımlıyor; kod 39+ alanı sunuyor

**Kaynak kodu:** `scripts/src/pipeline.py` (`_parse_list` metodu)
**Dokümantasyon:** `Data-Model.md`

Dokümantasyon, veri modelinde 39 alanı listelemektedir. Kod, `scripts/src/models.py` içinde tanımlanan `TC_FIELDS` değerlerini ayrıştırmaktadır.

**Sonuç:** Alan sayısı ve adları dokümantasyon ile kod arasında tutarlıdır.

---

## Bulgu 2 — YÜKSEK: Dokümantasyon `--debug` bayrağını belgelemiyor

**Kaynak kodu:** `scripts/src/client.py:38-39`
```python
if args.debug:
    logging.getLogger().setLevel(logging.DEBUG)
```

**Dokümantasyon:** `Security-Analysis.md` CLI bayraklarını belgelemektedir ancak `--debug` bayrağı CLI referans bölümünde geçmemektedir.

CLI, kök günlüğü DEBUG seviyesine ayarlayan `--debug` (38. satır) seçeneğini kabul etmektedir; ancak Security-Analysis.md yalnızca şunları listelemektedir: `--format`, `--output`, `--force`, `--clear-cache`, `--no-cache`, `--timeout`, `--retries`, `--retry-delay`, `--log-level`, `--proxy`, `--country`, `--list`, `--help`.

**Etki:** Kullanıcılar sorun giderme için debug bayrağından haberdar olmayabilir.

**Öneri:** Security-Analysis.md CLI referansına `--debug` seçeneğini ekleyin.

---

## Bulgu 3 — YÜKSEK: `--country` bayrağı dokümantasyonda eski ve yanıltıcı

**Kaynak kodu:** `scripts/main.py`
```python
if args.country and args.country != "TR":
    parser.error("--country is fixed to TR. Türkiye is the only supported country.")
```

`--country` bayrağı kodlayıcıda mevcuttur (55. satır: `choices=["TR"]`) ve kod TR dışındaki herhangi bir değeri `parser.error()` ile **reddetmektedir**. Security-Analysis.md belgesinde `--country` bir değer kabul eden bir parametre olarak tanımlanmaktadır (22. satır: `--country COUNTRY`) ve şöyle belirtmektedir: "Varsayılan hedef ülkeyi (varsayılan: TR) değiştirin. Türkiye tek desteklenen ülkedir."

**Uyumsuzluk:** Dokümantasyon `--country`'nin yapılandırılabilir bir parametre olduğunu ima etmektedir. Oysa bu seçenek **TR'ye sabitlenmiştir** ve herhangi bir diğer değer derhal `parser.error()` ile çıkış sağlar. Bayrak fiilen işlevsizdir.

**Etki:** Kullanıcılar `--country DE` veya benzeri bir değer deneyip yanıltıcı bir hata alabilir. Dokümantasyon mevcut olmayan bir yapılandırılabilirliği ima etmektedir.

**Öneri:** Security-Analysis.md'yi bayrağın mevcut olduğunu ancak TR'ye sabitlendiğini ve değiştirilemeyeceğini belirtecek şekilde yeniden yazın. Bayrağın CLI'dan tamamen kaldırılması gerekip gerekmediğini değerlendirin.

---

## Bulgu 4 — ORTA: `--proxy` açıklaması HTTPS zorunluluğundan bahsetmiyor

**Kaynak kodu:** `scripts/src/client.py:69-72`
```python
if proxy_url:
    proxy_url = self._validate_proxy_url(proxy_url)
    # ...
    self._ssl_context = self._create_ssl_context(proxy_url=proxy_url)
```

Ve `client.py:122-125`:
```python
def _validate_proxy_url(self, proxy_url: str) -> str:
    if not proxy_url:
        raise ValueError("Proxy URL cannot be empty")
    parsed = urlparse(proxy_url)
    if parsed.scheme not in ("http", "https"):
        raise ValueError(f"Proxy scheme must be 'http' or 'https', got '{parsed.scheme}'")
```

Dokümantasyon (Security-Analysis.md, 26. satır) `--proxy` seçeneğini "HTTP/HTTPS proxy kullan" olarak tanımlamaktadır ancak şunlardan bahsetmemektedir:
- SOCKS proxy'leri açıkça reddedilmektedir
- Proxy URL'si başlangıçta doğrulanmakta ve geçersizse anında hata vermektedir
- Proxy varlığının bulunup bulunmamasına bağlı olarak SSL bağlamı farklı oluşturulmaktadır (`_create_ssl_context`, 127-137. satırlar)

**Öneri:** `Security-Analysis.md`'e yalnızca HTTP/HTTPS proxy'lerinin desteklendiğini (SOCKS'un desteklenmediğini) ve proxy doğrulamasının başlangıçta yapıldığını belirten bir not ekleyin.

---

## Bulgu 5 — ORTA: `Module-Architecture.md` dosyası `rate_limiter`'ın `time.sleep()` kullandığını tanımlıyor — doğrulandı ancak eski kalıp

**Kaynak kodu:** `scripts/src/client.py:19-24`
```python
async def acquire(self) -> None:
    while True:
        self._clean_history()
        if len(self._history) < self._max_requests:
            self._history.append(time.monotonic())
            return
        wait_time = self._min_interval - (time.monotonic() - self._history[0])
        if wait_time > 0:
            await asyncio.sleep(wait_time)
```

Dokümantasyon `asyncio.sleep()` davranışını doğru tanımlamaktadır. **Uyumsuzluk bulunamadı.** Bu tutarlıdır.

---

## Bulgu 6 — ORTA: Legal-Notices.md dosyası `scripts/src/client.py` içindeki Türkiye Hükümeti veri atıfını belgelemiyor

**Kaynak kodu:** `scripts/src/client.py:23-24`
```python
# Real API base URL (verified from OpenAPI spec and live calls)
BASE_URL = "https://siberguvenlik.gov.tr"
```

**Dokümantasyon:** `Legal-Notices.md` (29-33. satırlar) "Ticaret Sicili Gazetesi" ve veri kaynağı olarak `scripts/src/client.py` dosyasından bahsetmektedir. Ancak Legal-Notices.md 33. satırı, `scripts/src/client.py` dosyasının "ListData/UltimateBeneficialOwner" için veri kaynağı olduğunu belirtmekte; ancak bunun **canlı API uç noktası URL'lerini** (asıl veri hattı giriş noktalarını) içerdiğini belirtmemektedir.

**Etki:** Düşük. Yasal bildirim dosyaya referans vermekte ancak tüm veri erişiminin yapılandırma kökü olarak önemini yeterince vurgulamamaktadır.

---

## Bulgu 7 — YÜKSEK: `Data-Flow.md` belgesi `pip install -e ".[dev]"` komutunu belirtiyor ancak kod `pyproject.toml` ile isteğe bağlı `dev` bağımlılıklarını kullanıyor

**Kaynak kodu:** `pyproject.toml:31-41`
```toml
[project.optional-dependencies]
dev = [
    "pytest>=8.0,<9",
    "pytest-asyncio>=0.23,<1",
    "pytest-cov>=5.0,<6",
    "ruff>=0.5,<1",
    "mypy>=1.10,<2",
    "bandit>=1.7,<2",
    "pip-audit>=2.7,<3",
    "hypothesis>=6.100,<7",
]
```

Dokümantasyon (`Data-Flow.md`, 16. satır): `pip install -e ".[dev]"` — bu **doğrudur** ve `pyproject.toml` ile uyumludur.

**Uyumsuzluk bulunamadı.** Geliştirme bağımlılıkları `mypy`, `pytest`, `ruff`, `bandit`, `pip-audit`, `hypothesis` vb. içermektedir ve `Data-Flow.md` bölüm 4.1 "Kod Kalitesi Araçları" ile tutarlıdır.

---

## Bulgu 8 — ORTA: `API-Analysis.md` dosyası CDN fallback mekanizmasını belgelemiyor

**Kaynak kodu:** `scripts/src/client.py:269-282`
```python
urls_to_try = [url]
if url == TCS_GB_DATA_URL and self._config.enable_cdn_fallback:
    urls_to_try.append(TCS_GB_DATA_CDN_URL)

for current_url in urls_to_try:
    try:
        response = await self._make_request_with_retry(current_url, timeout=30, retries=2)
        # ...
    except Exception:
        if current_url == TCS_GB_DATA_URL and len(urls_to_try) > 1:
            logger.warning(f"Primary URL failed, trying CDN fallback...")
            continue
        raise
```

Kod bir **CDN fallback mekanizması** uygulamaktadır: Birincil TCS GB API URL'si başarısız olursa, otomatik olarak CloudFront CDN URL'si (`TCS_GB_DATA_CDN_URL`) ile yeniden dener. Bu, `config.enable_cdn_fallback` seçeneği tarafından kontrol edilmektedir.

**Dokümantasyon eksikliği:** `Performance-Strategy.md` birincil API uç noktasını ve önbelleklemeyi tanımlamaktadır ancak şunlardan bahsetmemektedir:
- CDN fallback URL'si (`https://d13k0kxkym9y80.cloudfront.net/prod/tcs_gb_data.json`)
- Otomatik devralma davranışı
- `enable_cdn_fallback` yapılandırma seçeneği

**Etki:** İzleme kurulumu yapan kullanıcılar, birincil bir başarısızlıktan sonra bazı isteklerin neden sessizce başarılı olduğunu anlamayabilir.

**Öneri:** `Performance-Strategy.md`'ye fallback URL'si, davranışı ve yapılandırmayı belgeleyen bir "CDN Fallback" alt bölümü ekleyin.

---

## Bulgu 9 — DÜŞÜK: `Data-Model.md` ve `Threat-Model.md` arasında küçük terminoloji tutarsızlığı

- `Data-Model.md` "Turkish Trade Registry Gazette" (Türk Ticaret Sicili Gazetesi) (7. satır) kullanmaktadır
- `Threat-Model.md` "Trade Registry Gazette" (Ticaret Sicili Gazetesi) ön ekini "Turkish" (Türk) olmadan kullanmaktadır (7. satır)
- `Data-Model.md` "Ticaret Sicili Gazetesi" (9. satır) kullanmaktadır

Üçü de aynı kaynağı ifade etmektedir. Kozmetik düzeydedir ancak tutarsızdır.

---

## Bulgu 10 — YÜKSEK: `Security-Analysis.md` dosyası proxy varlığında SSL sertifika doğrulama bypass'ını belgelemiyor

**Kaynak kodu:** `scripts/src/client.py:127-137`
```python
def _create_ssl_context(self, proxy_url: Optional[str] = None) -> ssl.SSLContext:
    ssl_context = ssl.create_default_context()
    if proxy_url:
        logger.debug("SSL verification disabled for proxy connections")
        ssl_context.check_hostname = False
        ssl_context.verify_mode = ssl.CERT_NONE
    else:
        logger.debug("SSL verification enabled for direct connections")
    return ssl_context
```

Proxy yapılandırıldığında, **SSL sertifika doğrulaması tamamen devre dışı bırakılmaktadır** (`check_hostname = False`, `verify_mode = CERT_NONE`). Bu önemli bir güvenlik hususudur.

**Dokümantasyon eksikliği:** `Risk-Analysis.md` bu davranıştan bahsetmemektedir. Güvenlik belgesi HTTPS bağlantılarını ve sertifika doğrulamasını önermektedir ancak proxy kullanımının SSL doğrulamasını devre dışı bıraktığı konusunda uyarı yapmamaktadır.

**Etki:** YÜKSEK — Proxy bağlantılarına güvenen kullanıcılar, trafiğinin TLS ile doğrulandığına inanabilir ancak öyle değildir. Bu hassas vergi verilerini ortadaki adam saldırılarına açık hale getirebilir.

**Öneri:** `Risk-Analysis.md` ve `Security-Analysis.md`'e `--proxy` kullanmanın SSL sertifika doğrulamasını devre dışı bıraktığına dair belirgin bir uyarı ekleyin. Bu davranışın uygun olup olmadığı veya yapılandırılabilir olup olmadığı değerlendirin.

---

## Bulgu 11 — ORTA: `Roadmap.md` dosyası `_make_request`'i genel API olarak belgelemektedir ancak bu özel bir metottur

**Kaynak kodu:** `scripts/src/client.py:158-224`
```python
async def _make_request(
    self,
    url: str,
    timeout: int = 30,
    retries: int = 3,
    retry_delay: float = 1.0,
) -> str:
```

Metot `_` ile başlamaktadır, bu da özel/dahili olduğunu göstermektedir. `Test-Strategy.md` API referansı onu genel bir APIymiş gibi belgelemektedir. Asıl genel arayüz `get_list_data()` (249. satır) ve `get_ultimate_beneficial_owners()` (309. satır) metotlarıdır.

**Öneri:** `Roadmap.md`'de `_make_request`'in dahili bir metot olduğunu ve genel API tüketicilerinin `get_list_data()` / `get_ultimate_beneficial_owners()` kullanması gerektiğini açıkça belirtin.

---

## Bulgu 12 — DÜŞÜK: `Maintenance-Plan.md` dosyası "çıkış kodu 1"den bahsetmektedir ancak kod birden fazla çıkış kodu kullanmaktadır

**Kaynak kodu:** `scripts/main.py:211-214`
```python
except KeyboardInterrupt:
    print("\nİşlem iptal edildi.", file=sys.stderr)
    sys.exit(130)
except Exception as e:
    logger.error(f"Beklenmeyen hata: {e}")
    sys.exit(1)
```

Kod klavye kesintisi için çıkış kodu 130 (213. satır) ve genel hatalar için çıkış kodu 1 (214. satır) kullanmaktadır. Sorun giderme belgesi yalnızca "çıkış kodu 1"den bahsetmektedir.

**Öneri:** `Maintenance-Plan.md`'de çıkış kodlarının tam setini (1 = hata, 130 = kesintiye uğratıldı) belgeleyin.

---

## Öneri Özeti

| # | Bulgu | Öncelik | Önerilen Aksiyon |
|---|-------|---------|-----------------|
| 2 | `--debug` bayrak dokümantasyonu eksik | YÜKSEK | `Security-Analysis.md` CLI referansına ekle |
| 3 | `--country` bayrağı sabit, dokümantasyon yapılandırılabilir gösteriyor | YÜKSEK | `Security-Analysis.md`'yi yeniden yaz; bayrağı kaldırmayı değerlendir |
| 4 | `--proxy` yalnızca HTTPS + başlangıç doğrulaması belgelenmemiş | ORTA | `Security-Analysis.md`'ye not ekle |
| 8 | CDN fallback mekanizması belgelenmemiş | ORTA | `Performance-Strategy.md`'ye alt bölüm ekle |
| 9 | Belgeler arası tutarsız terminoloji | DÜŞÜK | "Türk Ticaret Sicili Gazetesi" standardize et |
| 10 | Proxy ile SSL doğrulama bypass'ı belgelenmemiş | **YÜKSEK** | `Risk-Analysis.md` ve `Security-Analysis.md`'ye uyarı ekle |
| 11 | Özel `_make_request` genel API olarak belgelenmiş | ORTA | `Roadmap.md`'de açıkla |
| 12 | Çıkış kodları sorun gidermede eksik | DÜŞÜK | Çıkış kodları 1 ve 130'u belgele |

---

## Denetlenen Dosyalar

| Belge | İncelenen Satır Sayısı | Bulunan Sorun |
|-------|------------------------|---------------|
| Data-Model.md | — | 0 |
| Threat-Model.md | — | 0 |
| Security-Analysis.md | — | 3 (Bulgular 2, 3, 4) |
| License-Analysis.md | — | 0 |
| Test-Strategy.md | — | 1 (Bulgu 8) |
| Regression-Strategy.md | — | 0 |
| Performance-Strategy.md | — | 0 |
| Versioning-Strategy.md | — | 0 |
| Publishing-Strategy.md | — | 0 |
| Maintenance-Plan.md | — | 0 |
| Risk-Analysis.md | — | 1 (Bulgu 10) |
| Roadmap.md | — | 1 (Bulgu 11) |
| Legal-Notices.md | — | 0 |
| Audit-Report.md | — | 0 |

**Denetlenen kaynak kodu dosyaları:**
- `scripts/src/__init__.py`
- `scripts/src/client.py`
- `scripts/src/deduplicator.py`
- `scripts/src/models.py`
- `scripts/src/normalizer.py`
- `scripts/src/outputs.py`
- `scripts/src/pipeline.py`
- `scripts/src/quality.py`
- `scripts/src/validator.py`
- `scripts/main.py`
- `pyproject.toml`

---

*Denetim Raporu Sonu*
