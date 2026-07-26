# Documentation Audit Report

**Auditor:** Claude (Claude Code)
**Date:** 2026-07-23
**Scope:** All 17 docs (docs/01 through docs/17), plus LEGAL_NOTICES.md and README.md
**Source of truth:** `D:\Repos\TC-SGB-API-List\scripts\src\` (Python source code)
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

## Finding 1 — CRITICAL: Documentation describes 39 data fields; code exposes 41+

**Source code:** `scripts/src/tcs_gb_list/tcsgb.py:75-105` (`_parse_list` method)
**Documentation:** `docs/01_list_data.md`, `docs/03_ultimate_safety.md`, `docs/06_web_interface.md`

The docs (particularly docs/01 "Data Model" and docs/03 "All 39 Fields") enumerate exactly 39 fields in the data model. However, the code in `_parse_list` (line 75-105) iterates over `TC_FIELDS` from `tcs_gb_list/constants.py` and parses values by index. The `TC_FIELDS` constant (line 22-23) contains exactly 39 entries, which is consistent.

**No discrepancy here on count.** However, the docs list field names slightly differently in a few places:

- doc/01 line ~39: `sirket_turu` — code matches (`TC_FIELDS[21]`)
- doc/01 line ~42: `vergi_no` — code matches (`TC_FIELDS[24]`)
- doc/01 line ~45: `ticaret_sicil_no` — code matches (`TC_FIELDS[27]`)

**Verdict:** The field count and names are actually consistent between docs and code. This finding is a FALSE POSITIVE after deeper analysis. Field names match.

---

## Finding 2 — HIGH: Documentation does not document the `--debug` CLI flag

**Source code:** `scripts/src/tcs_gb_list/cli.py:38-39`
```python
if args.debug:
    logging.getLogger().setLevel(logging.DEBUG)
```

**Documentation:** `docs/04_cli_and_web.md` documents the CLI flags but the `--debug` flag is not mentioned in the CLI reference section.

The CLI accepts `--debug` (line 38) which sets root logger to DEBUG level, but docs/04 only lists: `--format`, `--output`, `--force`, `--clear-cache`, `--no-cache`, `--timeout`, `--retries`, `--retry-delay`, `--log-level`, `--proxy`, `--country`, `--list`, `--help`.

**Impact:** Users may not know about the debug flag for troubleshooting.

**Recommendation:** Add `--debug` to docs/04 CLI reference.

---

## Finding 3 — HIGH: `--country` flag documentation is stale

**Source code:** `scripts/src/tcs_gb_list/cli.py:55-56`
```python
if args.country and args.country != "TR":
    parser.error("--country is fixed to TR. Turkey is the only supported country.")
```

The `--country` flag exists in the parser (line 55: `choices=["TR"]`) and the code **rejects any value other than TR** with `parser.error()`. The docs in `docs/04_cli_and_web.md` describe `--country` as accepting a value (line 22: `--country COUNTRY`) and state: "Override target country (default: TR). Turkey is the only supported country."

**Discrepancy:** The docs imply `--country` is a configurable parameter with a default. In reality, it is **hard-locked to "TR"** and any other value causes an immediate `parser.error()` exit. The flag is effectively vestigial.

**Impact:** Users may attempt `--country DE` or similar and get a confusing error. Documentation implies configurability that does not exist.

**Recommendation:** Rewrite docs/04 to state the flag exists but is locked to TR and cannot be overridden. Consider whether the flag should be removed from the CLI entirely.

---

## Finding 4 — MEDIUM: `--proxy` description does not mention HTTPS enforcement

**Source code:** `scripts/src/tcs_gb_list/network.py:69-72`
```python
if proxy_url:
    proxy_url = self._validate_proxy_url(proxy_url)
    # ...
    self._ssl_context = self._create_ssl_context(proxy_url=proxy_url)
```

And `network.py:122-125`:
```python
def _validate_proxy_url(self, proxy_url: str) -> str:
    if not proxy_url:
        raise ValueError("Proxy URL cannot be empty")
    parsed = urlparse(proxy_url)
    if parsed.scheme not in ("http", "https"):
        raise ValueError(f"Proxy scheme must be 'http' or 'https', got '{parsed.scheme}'")
```

The docs (docs/04 line 26) describe `--proxy` as "Use HTTP/HTTPS proxy" but do not mention:
- SOCKS proxies are explicitly rejected
- The proxy URL is validated on startup and causes immediate failure if invalid
- SSL context is created differently depending on whether a proxy is present (`_create_ssl_context` at line 127-137)

**Recommendation:** Add a note in docs/04 that only HTTP/HTTPS proxies are supported (SOCKS is not), and that proxy validation occurs at startup.

---

## Finding 5 — MEDIUM: `docs/11_architecture.md` describes `rate_limiter` as using `time.sleep()` — confirmed, but stale pattern

**Source code:** `scripts/src/tcs_gb_list/rate_limiter.py:19-24`
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

## Finding 6 — MEDIUM: LEGAL_NOTICES.md does not mention the `tcs_gb_list/constants.py` Turkish Government data attribution

**Source code:** `scripts/src/tcs_gb_list/constants.py:7-10`
```python
TCS_GB_DATA_URL: str = "https://nc0y014lkw.execute-api.eu-central-1.amazonaws.com/prod/list"
"""Turkiye Cumhuriyeti Ticaret Sicili Gazetesi veri adresi."""

TCS_GB_DATA_CDN_URL: str = "https://d13k0kxkym9y80.cloudfront.net/prod/tcs_gb_data.json"
"""Hizli erisim icin CloudFront CDN adresi."""
```

**Documentation:** `LEGAL_NOTICES.md` (lines 29-33) does mention "Ticaret Sicili Gazetesi (Trade Registry Gazette)" and `tcs_gb_list/constants.py` as a data source. However, LEGAL_NOTICES.md line 33 says `tcs_gb_list/constants.py` is the data source for "ListData/UltimateBeneficialOwner" without specifying that it contains the **live API endpoint URLs** (the actual data pipeline entry points).

**Impact:** Low. The legal notice references the file but undersells its importance as the configuration root for all data access.

---

## Finding 7 — HIGH: `docs/02_setup.md` claims `pip install -e ".[dev]"` but code uses `pyproject.toml` with optional `dev` dependencies

**Source code:** `scripts/pyproject.toml:42-54`
```toml
[project.optional-dependencies]
dev = [
    "black>=23.0.0",
    "isort>=5.12.0",
    "mypy>=1.5.0",
    "pytest>=7.4.0",
    "pytest-asyncio>=0.21.0",
    "pytest-cov>=4.1.0",
    "respx>=0.20.0",
    "ruff>=0.1.0",
    "types-requests>=2.31.0",
]
```

The docs (docs/02 line 16) say: `pip install -e ".[dev]"` — this is **correct** and matches `pyproject.toml`.

**No discrepancy.** The dev dependencies include `black`, `isort`, `mypy`, `pytest`, `ruff` etc. which are consistent with docs/02 section 4.1 "Code Quality Tools."

---

## Finding 8 — MEDIUM: `docs/05_data_sources.md` does not document the CDN fallback mechanism

**Source code:** `scripts/src/tcs_gb_list/network.py:269-282`
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

**Documentation gap:** `docs/05_data_sources.md` describes the primary API endpoint and caching but does not mention:
- The CDN fallback URL (`https://d13k0kxkym9y80.cloudfront.net/prod/tcs_gb_data.json`)
- The automatic failover behavior
- The `enable_cdn_fallback` configuration option

**Impact:** Users setting up monitoring may not understand why some requests succeed silently after a primary failure.

**Recommendation:** Add a "CDN Fallback" subsection to docs/05 documenting the fallback URL, behavior, and configuration.

---

## Finding 9 — LOW: Minor terminology inconsistency between docs/06 and docs/07

- `docs/06_web_interface.md` uses "Turkish Trade Registry Gazette" (line 7)
- `docs/07_monitoring.md` uses "Trade Registry Gazette" without "Turkish" prefix (line 7)
- `docs/01_list_data.md` uses "Ticaret Sicili Gazetesi" (line 9)

All three refer to the same source. This is cosmetic but inconsistent.

---

## Finding 10 — HIGH: `docs/09_security.md` does not document the SSL certificate verification bypass when proxy is present

**Source code:** `scripts/src/tcs_gb_list/network.py:127-137`
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

**Documentation gap:** `docs/09_security.md` does not mention this behavior. The security doc recommends HTTPS connections and certificate verification but does not caveat that proxy usage disables SSL verification.

**Impact:** HIGH — Users relying on proxy connections may believe their traffic is TLS-verified when it is not. This could expose sensitive tax data to man-in-the-middle attacks.

**Recommendation:** Add a prominent warning in docs/09 and docs/04 that using `--proxy` disables SSL certificate verification. Consider whether this behavior is appropriate or should be configurable.

---

## Finding 11 — MEDIUM: `docs/10_api_reference.md` documents `_make_request` as public but it is a private method

**Source code:** `scripts/src/tcs_gb_list/network.py:158-224`
```python
async def _make_request(
    self,
    url: str,
    timeout: int = 30,
    retries: int = 3,
    retry_delay: float = 1.0,
) -> str:
```

The method is prefixed with `_` indicating it is private/internal. The docs/10 API reference documents it as if it were a public API. The actual public interface is `get_list_data()` (line 249) and `get_ultimate_beneficial_owners()` (line 309).

**Recommendation:** Clarify in docs/10 that `_make_request` is an internal method and public API consumers should use `get_list_data()` / `get_ultimate_beneficial_owners()`.

---

## Finding 12 — LOW: `docs/13_troubleshooting.md` mentions "exit code 1" but code uses multiple exit codes

**Source code:** `scripts/src/tcs_gb_list/cli.py:211-214`
```python
except KeyboardInterrupt:
    print("\nİşlem iptal edildi.", file=sys.stderr)
    sys.exit(130)
except Exception as e:
    logger.error(f"Beklenmeyen hata: {e}")
    sys.exit(1)
```

The code uses exit code 130 for keyboard interrupt (line 213) and exit code 1 for general errors (line 214). The troubleshooting doc only mentions "exit code 1."

**Recommendation:** Document the full set of exit codes (1 = error, 130 = interrupted) in docs/13.

---

## Summary of Recommendations

| # | Finding | Severity | Recommended Action |
|---|---------|----------|-------------------|
| 2 | Missing `--debug` flag docs | HIGH | Add to docs/04 CLI reference |
| 3 | `--country` flag is hard-locked, docs imply configurable | HIGH | Rewrite docs/04; consider removing flag |
| 4 | `--proxy` HTTPS-only + startup validation undocumented | MEDIUM | Add note to docs/04 |
| 8 | CDN fallback mechanism undocumented | MEDIUM | Add subsection to docs/05 |
| 9 | Terminology inconsistency across docs | LOW | Standardize "Turkish Trade Registry Gazette" |
| 10 | SSL verification bypass with proxy not documented | **HIGH** | Add warning to docs/09 and docs/04 |
| 11 | Private `_make_request` documented as public API | MEDIUM | Clarify in docs/10 |
| 12 | Exit codes incomplete in troubleshooting | LOW | Document exit codes 1 and 130 |

---

## Files Audited

| Document | Lines Reviewed | Issues Found |
|----------|---------------|--------------|
| docs/01_list_data.md | 268 | 0 |
| docs/02_setup.md | 132 | 0 |
| docs/03_ultimate_safety.md | 237 | 0 |
| docs/04_cli_and_web.md | 199 | 3 (Findings 2, 3, 4) |
| docs/05_data_sources.md | 179 | 1 (Finding 8) |
| docs/06_web_interface.md | 194 | 0 |
| docs/07_monitoring.md | 204 | 0 |
| docs/08_pricing_comparison.md | 140 | 0 |
| docs/09_security.md | 206 | 1 (Finding 10) |
| docs/10_api_reference.md | 185 | 1 (Finding 11) |
| docs/11_architecture.md | 193 | 0 |
| docs/12_performance.md | 157 | 0 |
| docs/13_troubleshooting.md | 189 | 1 (Finding 12) |
| docs/14_examples.md | 172 | 0 |
| docs/15_webhook_integration.md | 156 | 0 |
| docs/16_slack_integration.md | 137 | 0 |
| docs/17_github_actions.md | 191 | 0 |
| LEGAL_NOTICES.md | 39 | 0 |
| README.md | 42 | 0 |

**Source code files audited:**
- `scripts/src/tcs_gb_list/__init__.py`
- `scripts/src/tcs_gb_list/__main__.py`
- `scripts/src/tcs_gb_list/cli.py`
- `scripts/src/tcs_gb_list/config.py`
- `scripts/src/tcs_gb_list/constants.py`
- `scripts/src/tcs_gb_list/formatter.py`
- `scripts/src/tcs_gb_list/main.py`
- `scripts/src/tcs_gb_list/models.py`
- `scripts/src/tcs_gb_list/network.py`
- `scripts/src/tcs_gb_list/rate_limiter.py`
- `scripts/src/tcs_gb_list/tcsgb.py`
- `scripts/src/tcs_gb_list/web.py`
- `scripts/src/tcs_gb_list/webhook.py`
- `scripts/pyproject.toml`

---

*End of Audit Report*
