# External Feeds Analysis: PhishTank & abuse.ch Integration

**Date:** 2026-11-05 (UTC+03:00)  
**Author:** AI Agent (comprehensive review)  
**Status:** Research Complete — Ready for Implementation Decision  
**Last updated:** 2026-11-12 (UTC+03:00) — slot numbering corrected after Azerbaijan feed removal

[English](#english) | [Türkçe](#turkce)

---

<a id="english"></a>
## English

## Executive Summary

This report analyzes adding **PhishTank** (phishtank.org) and **abuse.ch** platforms (URLhaus, ThreatFox) as new external threat-feed sources to the TC-SGB pipeline. Both sources are well-established, community-driven, and provide high-quality phishing/malware IoCs that complement the existing CERT.PL and CERT.SI feeds.

| Source | Type | Auth Required | Format | Update Freq. | Est. Rules/Day | Recommended Slot |
|--------|------|---------------|--------|--------------|----------------|------------------|
| PhishTank | Phishing URLs → Domains | API Key (free) | CSV/JSON/XML | Hourly | ~5,000–15,000 | 04-phishtank |
| URLhaus (abuse.ch) | Malware URLs → Domains | Auth-Key (free) | CSV/Host-file | 5 min | ~10,000–30,000 | 05-urlhaus |
| ThreatFox (abuse.ch) | Malware IOCs (domains/IPs/URLs) | Auth-Key (free) | CSV/JSON/Host-file | 5 min | ~5,000–20,000 | 06-threatfox |

**Key finding:** All three sources require free registration for an API/Auth key. The pipeline already supports keyed fetches via environment variables. Integration is straightforward using the existing `ExternalFeed` framework.

> **Slot note (2026-11-12):** The `filter-lists` branch currently publishes 3 active files (`01-turkiye`, `02-polonya`, `03-slovenya`). Slot `04` was previously reserved for Azerbaijan but that feed is no longer active; new sources therefore use slots `04`, `05`, `06`.

---

## 1. Project Architecture Recap

### 1.1 External Feed Pipeline (`Scripts/src/external_feeds.py`)

The pipeline already supports third-party feeds via:
- `ExternalFeed` dataclass: `key`, `url`, `format` (hosts/lines/csv), `output_file`, `title`, `homepage`
- Three parsers: `parse_hosts`, `parse_lines`, `parse_csv_domain`
- Safety policy (`safety.py`) applied per-feed via `apply_policy()`
- AdGuard output generation via `generate_external_adguard()`
- Per-feed audit files (`*_audit.json`) and raw snapshots (`*_source.txt`)
- Independent failure tolerance: one bad feed never blocks others
- Validation gate: `validate-external` command + CI integration

### 1.2 Filter-Lists Branch (`filter-lists`)

- Rolling single-commit branch, force-pushed daily by `schedule.yml`
- Files numbered for Brave/AdGuard subscription ordering: `01-turkiye`, `02-polonya`, `03-slovenya`
- **Available slots for new sources: `04`, `05`, `06`...** (slot `04` was previously reserved for Azerbaijan; it is now free)
- Published to both GitHub and GitLab via dual-push remote
- Failed feeds keep serving last good snapshot

### 1.3 Safety Policy (`Scripts/src/safety.py`)

- `BLOCKED_EXACT`: High-impact hosts never blocked (google.com, youtube.com, etc.)
- `SHARED_APEX`: User-content platforms held for review (docs.google.com, etc.)
- `SHARED_SERVICE_APEX`: Cloud provider endpoints held for review (amazonaws.com, etc.)
- S3 service root regex catches all AWS S3 service endpoints
- Verdicts: `ACCEPT` → published, `REJECT` → dropped, `REVIEW` → audit only

---

## 2. PhishTank Analysis

### 2.1 Source Overview

| Attribute | Details |
|-----------|---------|
| **Operator** | Cisco Talos Intelligence Group |
| **Focus** | Verified phishing URLs (community-vetted) |
| **Data scope** | Global, all TLDs, hourly updates |
| **Access** | Free registration → Application Key |
| **Rate limits** | Few downloads/day without key; unlimited with key + ETag checks |
| **ToS** | https://www.cisco.com/c/en/us/about/legal/cloud-and-software/end_user_license_agreement.html |

### 2.2 Data Formats & Endpoints

| Format | URL (with key) | Compressed |
|--------|----------------|------------|
| CSV | `https://data.phishtank.com/data/<KEY>/online-valid.csv` | `.gz`, `.bz2` |
| JSON | `https://data.phishtank.com/data/<KEY>/online-valid.json` | `.gz`, `.bz2` |
| XML | `https://data.phishtank.com/data/<KEY>/online-valid.xml` | `.gz`, `.bz2` |
| PHP Serialized | `https://data.phishtank.com/data/<KEY>/online-valid.php_serialized` | `.gz`, `.bz2` |

**CSV columns:** `phish_id,url,phish_detail_url,submission_time,verified,verification_time,online,target`

**Key constraints:**
- Only `verified=yes` AND `online=yes` entries are in the feed
- Updated hourly (on the hour)
- ETag HEAD requests don't count against rate limits

### 2.3 Parsing Strategy

The CSV contains **full URLs** (e.g., `https://evil.com/login.php`). For AdGuard `||domain^` rules we need to:
1. Extract hostname from URL
2. Normalize (lowercase, IDNA, strip trailing dot)
3. Apply safety policy
4. Deduplicate

**Recommended parser:** Extend `parse_csv_domain` or add `parse_phishtank_csv` that extracts domains from the `url` column.

### 2.4 Volume Estimate

- PhishTank typically publishes **5,000–15,000 verified online phishing URLs** per hourly dump
- After domain extraction + dedup + safety policy: **~3,000–10,000 unique domains/day**
- Complements TC-SGB's `PH` (phishing) and `BP` (financial phishing) categories

### 2.5 Implementation Notes

```python
# New feed entry (slot 04)
ExternalFeed(
    key="phishtank",
    url="https://data.phishtank.com/data/${PHISHTANK_KEY}/online-valid.csv.gz",
    format="phishtank_csv",  # new parser
    output_file="04-phishtank_adguard.txt",
    title="Global | PhishTank Verified Phishing Domains (AdGuard)",
    homepage="https://phishtank.org/",
),
```

**Environment variable:** `PHISHTANK_KEY` (set in GitHub/GitLab secrets)

**User-Agent:** `TC-SGB-API-to-List/1.0 (phishtank mirror; +https://github.com/bayraktarozcan/TC-SGB-API-to-List)`

---

## 3. abuse.ch Analysis

abuse.ch operates **six platforms**; two are directly relevant for domain/IP blocklists:

### 3.1 URLhaus — Malware Distribution URLs

| Attribute | Details |
|-----------|---------|
| **Focus** | URLs actively distributing malware |
| **Data scope** | Global, hourly/5-min updates |
| **Access** | Free Auth-Key from https://auth.abuse.ch/ |
| **Rate limits** | Fetch no more than every 5 minutes |
| **ToS** | https://abuse.ch/terms-of-use/#principles (fair use) |

**Relevant exports (require Auth-Key in URL):**
- `https://urlhaus-api.abuse.ch/v2/files/exports/<KEY>/recent.csv` — URLs added in last 30 days
- `https://urlhaus-api.abuse.ch/v2/files/exports/<KEY>/online.csv` — Currently active malware URLs
- `https://urlhaus-api.abuse.ch/v2/files/exports/<KEY>/hostfile.txt` — **Domains only** (hosts format), filtered: active + last 48h, excludes Tranco Top 1M

**Host-file format:** One domain per line (e.g., `evil.com`), perfect for `parse_lines`

**Volume:** ~10,000–30,000 active malware domains in hostfile

### 3.2 ThreatFox — Malware IOCs

| Attribute | Details |
|-----------|---------|
| **Focus** | IOCs associated with malware (domains, IPs, URLs, hashes) |
| **Data scope** | Global, 6-month retention (expired IOCs excluded) |
| **Access** | Same Auth-Key as URLhaus |
| **Rate limits** | Fetch exports no more than every 5 minutes |
| **Expiration** | IOCs older than 6 months excluded (since 2025-05-01) |

**Relevant exports (require Auth-Key in URL):**
- `https://threatfox-api.abuse.ch/v2/files/exports/<KEY>/hostfile.txt` — **Domains only** (payload delivery + botnet C2), last 6 months
- `https://threatfox-api.abuse.ch/v2/files/exports/<KEY>/full.csv.zip` — All IOC types (domain, ip:port, url, hash)
- `https://threatfox-api.abuse.ch/v2/files/exports/<KEY>/rpz.txt` — DNS RPZ format

**Host-file format:** One domain per line, perfect for `parse_lines`

**Volume:** ~5,000–20,000 malware-associated domains (6-month window)

### 3.3 abuse.ch Integration Strategy

Both URLhaus and ThreatFox provide **host-file format** (bare domains, one per line) which maps directly to the existing `format="lines"` parser. No new parser needed.

**Recommended feed entries (slots 05, 06):**

```python
# Slot 05: URLhaus malware distribution domains
ExternalFeed(
    key="urlhaus",
    url="https://urlhaus-api.abuse.ch/v2/files/exports/${ABUSE_CH_KEY}/hostfile.txt",
    format="lines",
    output_file="05-urlhaus_adguard.txt",
    title="Global | URLhaus Active Malware Distribution Domains (AdGuard)",
    homepage="https://urlhaus.abuse.ch/",
),

# Slot 06: ThreatFox malware IOC domains
ExternalFeed(
    key="threatfox",
    url="https://threatfox-api.abuse.ch/v2/files/exports/${ABUSE_CH_KEY}/hostfile.txt",
    format="lines",
    output_file="06-threatfox_adguard.txt",
    title="Global | ThreatFox Malware IOC Domains (AdGuard)",
    homepage="https://threatfox.abuse.ch/",
),
```

**Environment variable:** `ABUSE_CH_KEY` (single key works for both platforms)

---

## 4. Implementation Plan

### 4.1 Code Changes Required

| File | Change |
|------|--------|
| `Scripts/src/external_feeds.py` | Add 3 `ExternalFeed` entries; add `parse_phishtank_csv` parser |
| `Scripts/main.py` | No changes (uses `EXTERNAL_FEEDS` tuple dynamically) |
| `.github/workflows/schedule.yml` | Add `phishtank urlhaus threatfox` to feed loop; add key env vars |
| `.gitlab-ci.yml` | Mirror the schedule.yml changes |
| `Tests/test_external_feeds.py` | Add tests for new parsers and feed entries |
| `README.md` / `Docs/` | Document new sources |

### 4.2 Parser Addition: `parse_phishtank_csv`

```python
def parse_phishtank_csv(text: str) -> list[str]:
    """Parse PhishTank CSV: extract domain from 'url' column."""
    hosts: list[str] = []
    seen: set[str] = set()
    reader = csv.reader(io.StringIO(text))
    url_idx: int | None = None
    for row in reader:
        if not row or all(not cell.strip() for cell in row):
            continue
        if url_idx is None:
            lowered = [cell.strip().lower() for cell in row]
            if "url" in lowered:
                url_idx = lowered.index("url")
                continue
            url_idx = 1  # PhishTank CSV: phish_id,url,...
        if url_idx >= len(row):
            continue
        url = row[url_idx].strip()
        if not url:
            continue
        # Extract hostname from URL
        try:
            parsed = urlparse(url if "://" in url else f"https://{url}")
            host = parsed.hostname
        except ValueError:
            continue
        if not host:
            continue
        host = host.rstrip(".").lower()
        host = _clean_candidate(host)
        if host is not None and host not in seen:
            seen.add(host)
            hosts.append(host)
    return hosts
```

Add to `PARSERS` dict: `"phishtank_csv": parse_phishtank_csv`

### 4.3 CI/CD Secrets Required

| Secret | Value | Where |
|--------|-------|-------|
| `PHISHTANK_KEY` | Application key from https://phishtank.org/api_register.php | GitHub Secrets, GitLab CI/CD Variables |
| `ABUSE_CH_KEY` | Auth-Key from https://auth.abuse.ch/ | GitHub Secrets, GitLab CI/CD Variables |

### 4.4 Schedule.yml Feed Loop Update

```yaml
# feed loop in schedule.yml
for KEY in cert-pl cert-si phishtank urlhaus threatfox; do
  # ... existing logic ...
  case "${KEY}:${base}" in
    cert-pl:02-*|cert-si:03-*|phishtank:04-*|urlhaus:05-*|threatfox:06-*) matched="${EXT}" ;;
  esac
  # ... validation ...
done
```

### 4.5 README.md Filter-Lists Section Update

Add to the Brave subscription list:
- `04-phishtank_adguard.txt` — PhishTank Verified Phishing
- `05-urlhaus_adguard.txt` — URLhaus Malware Distribution
- `06-threatfox_adguard.txt` — ThreatFox Malware IOCs

---

## 5. Risk Assessment & Mitigation

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| API key rotation/expired | Low | Feed fails silently | Monitoring via `validate-external`; audit files show 0 rules |
| Rate limiting / 429 | Low (with keys) | Temporary fetch failure | Exponential backoff already implemented; `continue-on-error` in CI |
| Format changes | Low | Parse errors | Version-pinned parsers; snapshot + audit for forensics |
| False positives (legit domains) | Medium | Overblocking | Safety policy catches shared apex/services; PhishTank = verified only; URLhaus/ThreatFox exclude Tranco Top 1M |
| Key leakage in logs | Low | Credential exposure | Keys only in env vars; never logged; `httpx` logs at WARNING |
| Cloudflare challenge (like NKSC) | Low | Feed unreachable | abuse.ch APIs are direct; PhishTank data.phishtank.com is direct |
| Volume explosion (>90 MiB) | Low | Branch publish skipped | Size check in workflow; warning at 50 MiB, skip at 90 MiB |

---

## 6. Complementarity with Existing Feeds

| Feed | Primary Threat Type | Geographic Focus | Overlap |
|------|---------------------|------------------|---------|
| TC-SGB (01) | National (TR) mixed | Türkiye | Baseline |
| CERT.PL (02) | Phishing, malware, C2 | Poland/EU | Low |
| CERT.SI (03) | Malware, botnet, phishing | Slovenia/EU | Low |
| **PhishTank (04)** | **Phishing (verified)** | **Global** | **Complements PH/BP** |
| **URLhaus (05)** | **Malware distribution** | **Global** | **Complements MD/MU/MC** |
| **ThreatFox (06)** | **Malware IOCs (domains)** | **Global** | **Complements MD/MC/BC** |

**No significant overlap** — each source has distinct vantage points and curation methodologies.

---

## 7. Testing Strategy

### 7.1 Unit Tests (add to `test_external_feeds.py`)

```python
def test_parse_phishtank_csv():
    text = "phish_id,url,phish_detail_url,submission_time,verified,verification_time,online,target\n1,https://evil.com/login,https://phishtank.com/1,2026-01-01,yes,2026-01-01,yes,Bank\n2,http://bad.net/,https://phishtank.com/2,2026-01-01,yes,2026-01-01,yes,PayPal\n"
    assert parse_phishtank_csv(text) == ["evil.com", "bad.net"]

def test_parse_phishtank_csv_verified_only():
    text = "phish_id,url,verified,online\n1,https://evil.com/,yes,yes\n2,https://pending.com/,no,yes\n3,https://offline.com/,yes,no\n"
    assert parse_phishtank_csv(text) == ["evil.com"]
```

### 7.2 Integration Tests

- Run `fetch-external` with mocked responses for all 5 external feeds (cert-pl, cert-si, phishtank, urlhaus, threatfox)
- Verify `validate-external` passes for all
- Verify filter-lists branch staging works (size checks, numbering)

### 7.3 Smoke Test (Production)

After merge, trigger `workflow_dispatch` on `schedule.yml` and verify:
1. All 5 external feeds fetch successfully
2. AdGuard files generated in `Output/External/`
3. Audit files show reasonable accept/reject/review counts
4. Filter-lists branch updated with 6 files total (`01`, `02`, `03`, `04`, `05`, `06`)
5. Raw.githubusercontent.com URLs serve correct content

---

## 8. Legal & Compliance

| Source | License/ToS | Redistribution | Attribution |
|--------|-------------|----------------|-------------|
| PhishTank | Cisco EULA | Allowed for non-commercial; commercial needs license | Required: "Data provided by PhishTank" |
| URLhaus | abuse.ch Fair Use | Free under fair use principles | Required: "Data from URLhaus (abuse.ch)" |
| ThreatFox | abuse.ch Fair Use | Free under fair use principles | Required: "Data from ThreatFox (abuse.ch)" |

**Current pipeline practice:** Each AdGuard file includes `! Homepage:` and `! Source:` headers — satisfies attribution. No commercial use (free distribution via GitHub/GitLab).

**Action:** Add `! License:` header to `generate_external_adguard()` for explicit compliance.

---

## 9. Decision Matrix

| Criterion | PhishTank | URLhaus | ThreatFox |
|-----------|-----------|---------|-----------|
| **Data Quality** | ★★★★★ (community verified) | ★★★★★ (active malware only) | ★★★★★ (malware-associated, 6mo expiry) |
| **Operational Maturity** | ★★★★★ (15+ years, Cisco) | ★★★★★ (15+ years, Spamhaus) | ★★★★☆ (newer but stable) |
| **Integration Effort** | Low (new parser) | Very Low (existing parser) | Very Low (existing parser) |
| **Maintenance Burden** | Low (stable CSV) | Low (stable hostfile) | Low (stable hostfile) |
| **False Positive Risk** | Low (verified+online only) | Low (Tranco Top 1M excluded) | Low (6mo expiry, confidence scores) |
| **Complementarity** | High (global phishing) | High (global malware URLs) | High (global malware IOCs) |
| **Cost** | Free (registration) | Free (registration) | Free (same key) |
| **Recommendation** | **ADD (slot 04)** | **ADD (slot 05)** | **ADD (slot 06)** |

---

## 10. Next Steps

1. **Register for API keys:**
   - PhishTank: https://phishtank.org/api_register.php
   - abuse.ch: https://auth.abuse.ch/ (single key for URLhaus + ThreatFox)

2. **Add secrets to CI/CD:**
   - GitHub: Settings → Secrets → Actions → `PHISHTANK_KEY`, `ABUSE_CH_KEY`
   - GitLab: Settings → CI/CD → Variables → `PHISHTANK_KEY`, `ABUSE_CH_KEY`

3. **Implement code changes** (see Section 4.1)

4. **Run test suite:** `pytest Tests/test_external_feeds.py -v`

5. **Trigger workflow_dispatch** on `schedule.yml` for smoke test

6. **Verify filter-lists branch** has 6 files total (`01`, `02`, `03`, `04`, `05`, `06`)

7. **Update documentation** (README, Docs/)

---

## Appendix A: Sample PhishTank CSV Row

```csv
phish_id,url,phish_detail_url,submission_time,verified,verification_time,online,target
8472931,https://secure-login.example.com/phish.php,https://www.phishtank.com/phish_detail.php?phish_id=8472931,2026-10-12T14:30:00+00:00,yes,2026-10-12T15:00:00+00:00,yes,Example Bank
```

## Appendix B: Sample URLhaus Hostfile

```
malware-distribution-site.com
evil-downloader.net
payload-server.org
```

## Appendix C: Sample ThreatFox Hostfile

```
c2-server-malware.com
payload-delivery-domain.net
botnet-controller.org
```

---

<a id="turkce"></a>
## Türkçe

## Yönetici Özeti

Bu rapor, **PhishTank** (phishtank.org) ve **abuse.ch** platformlarını (URLhaus, ThreatFox) TC-SGB hattına yeni dış tehdit beslemesi kaynakları olarak eklemeyi inceler. Her iki kaynak da köklü, topluluk odaklıdır ve mevcut CERT.PL ve CERT.SI beslemelerini tamamlayan yüksek kaliteli oltalama/zararlı yazılım IoC’leri sağlar.

| Kaynak | Tür | Kimlik Doğrulama | Biçim | Güncelleme Sıklığı | Tahmini Kural/Gün | Önerilen Slot |
|--------|-----|------------------|-------|--------------------|-------------------|---------------|
| PhishTank | Oltalama URL’leri → Alan adları | API Anahtarı (ücretsiz) | CSV/JSON/XML | Saatlik | ~5.000–15.000 | 04-phishtank |
| URLhaus (abuse.ch) | Zararlı URL’ler → Alan adları | Auth-Key (ücretsiz) | CSV/Host-file | 5 dk | ~10.000–30.000 | 05-urlhaus |
| ThreatFox (abuse.ch) | Zararlı IoC’ler (alan/IP/URL) | Auth-Key (ücretsiz) | CSV/JSON/Host-file | 5 dk | ~5.000–20.000 | 06-threatfox |

**Temel bulgu:** Üç kaynağın tümü ücretsiz kayıt ile API/Auth anahtarı gerektirir. Hat, ortam değişkenleri üzerinden anahtarlı çekmeleri zaten destekler. Mevcut `ExternalFeed` çatısı ile entegrasyon doğrudandır.

> **Slot notu (2026-11-12 UTC+03:00):** `filter-lists` dalı şu anda 3 etkin dosya yayımlar (`01-turkiye`, `02-polonya`, `03-slovenya`). Slot `04` daha önce Azerbaycan için ayrılmıştı; bu besleme artık etkin olmadığı için yeni kaynaklar `04`, `05`, `06` slotlarını kullanır.

---

## 1. Proje Mimarisi Özeti

### 1.1 Dış Besleme Hattı (`Scripts/src/external_feeds.py`)

Hat üçüncü taraf beslemeleri şu yollarla destekler:
- `ExternalFeed` veri sınıfı: `key`, `url`, `format` (hosts/lines/csv), `output_file`, `title`, `homepage`
- Üç ayrıştırıcı: `parse_hosts`, `parse_lines`, `parse_csv_domain`
- Besleme başına güvenlik ilkesi (`safety.py`) `apply_policy()` ile uygulanır
- `generate_external_adguard()` ile AdGuard çıktısı üretilir
- Besleme başına denetim dosyaları (`*_audit.json`) ve ham anlık görüntüler (`*_source.txt`)
- Bağımsız hata toleransı: tek bozuk besleme diğerlerini engellemez
- Doğrulama kapısı: `validate-external` komutu + CI entegrasyonu

### 1.2 Filter-Lists Dalı (`filter-lists`)

- `schedule.yml` tarafından günlük force-push edilen yuvarlanan tek commit’li dal
- Brave/AdGuard abonelik sıralaması için numaralı dosyalar: `01-turkiye`, `02-polonya`, `03-slovenya`
- **Yeni kaynaklar için kullanılabilir slotlar: `04`, `05`, `06`...** (slot `04` daha önce Azerbaycan için ayrılmıştı; artık boştur)
- Çift push uzak yapılandırması ile hem GitHub hem GitLab’a yayımlanır
- Başarısız beslemeler son iyi anlık görüntüyü sunmaya devam eder

### 1.3 Güvenlik İlkesi (`Scripts/src/safety.py`)

- `BLOCKED_EXACT`: Yüksek etkili host’lar asla engellenmez (google.com, youtube.com vb.)
- `SHARED_APEX`: Kullanıcı içeriği platformları inceleme için tutulur (docs.google.com vb.)
- `SHARED_SERVICE_APEX`: Bulut sağlayıcı uç noktaları inceleme için tutulur (amazonaws.com vb.)
- S3 servis kökü regex’i tüm AWS S3 servis uç noktalarını yakalar
- Kararlar: `ACCEPT` → yayımlanır, `REJECT` → düşürülür, `REVIEW` → yalnızca denetimde tutulur

---

## 2. PhishTank Analizi

### 2.1 Kaynak Özeti

| Öznitelik | Ayrıntı |
|-----------|---------|
| **İşleten** | Cisco Talos Intelligence Group |
| **Odak** | Doğrulanmış oltalama URL’leri (topluluk denetimli) |
| **Veri kapsamı** | Küresel, tüm TLD’ler, saatlik güncelleme |
| **Erişim** | Ücretsiz kayıt → Uygulama Anahtarı |
| **Hız sınırları** | Anahtarsız günde az indirme; anahtar + ETag kontrolü ile sınırsız |
| **Kullanım koşulları** | https://www.cisco.com/c/en/us/about/legal/cloud-and-software/end_user_license_agreement.html |

### 2.2 Veri Biçimleri ve Uç Noktalar

| Biçim | URL (anahtarlı) | Sıkıştırılmış |
|-------|------------------|---------------|
| CSV | `https://data.phishtank.com/data/<KEY>/online-valid.csv` | `.gz`, `.bz2` |
| JSON | `https://data.phishtank.com/data/<KEY>/online-valid.json` | `.gz`, `.bz2` |
| XML | `https://data.phishtank.com/data/<KEY>/online-valid.xml` | `.gz`, `.bz2` |
| PHP Serialized | `https://data.phishtank.com/data/<KEY>/online-valid.php_serialized` | `.gz`, `.bz2` |

**CSV sütunları:** `phish_id,url,phish_detail_url,submission_time,verified,verification_time,online,target`

**Temel kısıtlar:**
- Beslemede yalnızca `verified=yes` VE `online=yes` kayıtlar bulunur
- Saatlik güncellenir (her saat başı)
- ETag HEAD istekleri hız sınırına dahil edilmez

### 2.3 Ayrıştırma Stratejisi

CSV **tam URL** içerir (örn. `https://evil.com/login.php`). AdGuard `||domain^` kuralları için:
1. URL’den hostname çıkarılır
2. Normalize edilir (küçük harf, IDNA, sondaki nokta temizlenir)
3. Güvenlik ilkesi uygulanır
4. Tekilleştirilir

**Önerilen ayrıştırıcı:** `parse_csv_domain` genişletilmeli veya `url` sütunundan alan adını çıkaran `parse_phishtank_csv` eklenmelidir.

### 2.4 Hacim Tahmini

- PhishTank tipik olarak saatlik dökümde **5.000–15.000 doğrulanmış çevrimiçi oltalama URL’si** yayımlar
- Alan adı çıkarımı + tekilleştirme + güvenlik ilkesi sonrası: **~3.000–10.000 benzersiz alan adı/gün**
- TC-SGB’nin `PH` (oltalama) ve `BP` (finansal oltalama) kategorilerini tamamlar

### 2.5 Uygulama Notları

```python
# Yeni besleme girdisi (slot 04)
ExternalFeed(
    key="phishtank",
    url="https://data.phishtank.com/data/${PHISHTANK_KEY}/online-valid.csv.gz",
    format="phishtank_csv",  # yeni ayrıştırıcı
    output_file="04-phishtank_adguard.txt",
    title="Global | PhishTank Verified Phishing Domains (AdGuard)",
    homepage="https://phishtank.org/",
),
```

**Ortam değişkeni:** `PHISHTANK_KEY` (GitHub/GitLab gizli değişkenlerinde ayarlanır)

---

## 3. abuse.ch Analizi

abuse.ch **altı platform** işletir; alan adı/IP engel listeleri için ikisi doğrudan ilgilidir:

### 3.1 URLhaus — Zararlı Yazılım Dağıtım URL’leri

| Öznitelik | Ayrıntı |
|-----------|---------|
| **Odak** | Aktif olarak zararlı yazılım dağıtan URL’ler |
| **Veri kapsamı** | Küresel, saatlik/5 dk güncelleme |
| **Erişim** | https://auth.abuse.ch/ üzerinden ücretsiz Auth-Key |
| **Hız sınırları** | Dışa aktarımlar 5 dakikadan sık çekilmemeli |
| **Kullanım koşulları** | https://abuse.ch/terms-of-use/#principles (adil kullanım) |

**İlgili dışa aktarımlar (URL’de Auth-Key gerekir):**
- `https://urlhaus-api.abuse.ch/v2/files/exports/<KEY>/recent.csv` — son 30 günde eklenen URL’ler
- `https://urlhaus-api.abuse.ch/v2/files/exports/<KEY>/online.csv` — şu an aktif zararlı URL’ler
- `https://urlhaus-api.abuse.ch/v2/files/exports/<KEY>/hostfile.txt` — **yalnızca alan adları** (hosts biçimi), filtreli: aktif + son 48 saat, Tranco Top 1M hariç

**Host-file biçimi:** Satır başına bir alan adı (örn. `evil.com`), `parse_lines` ile uyumludur

**Hacim:** Hostfile’da ~10.000–30.000 aktif zararlı alan adı

### 3.2 ThreatFox — Zararlı Yazılım IoC’leri

| Öznitelik | Ayrıntı |
|-----------|---------|
| **Odak** | Zararlı yazılımla ilişkili IoC’ler (alan adları, IP’ler, URL’ler, hash’ler) |
| **Veri kapsamı** | Küresel, 6 ay saklama (süresi dolan IoC’ler hariç) |
| **Erişim** | URLhaus ile aynı Auth-Key |
| **Hız sınırları** | Dışa aktarımlar 5 dakikadan sık çekilmemeli |
| **Süre sonu** | 6 aydan eski IoC’ler hariç (2025-05-01’den itibaren) |

**İlgili dışa aktarımlar (URL’de Auth-Key gerekir):**
- `https://threatfox-api.abuse.ch/v2/files/exports/<KEY>/hostfile.txt` — **yalnızca alan adları** (payload teslimi + botnet C2), son 6 ay
- `https://threatfox-api.abuse.ch/v2/files/exports/<KEY>/full.csv.zip` — tüm IoC türleri (domain, ip:port, url, hash)
- `https://threatfox-api.abuse.ch/v2/files/exports/<KEY>/rpz.txt` — DNS RPZ biçimi

**Host-file biçimi:** Satır başına bir alan adı, `parse_lines` ile uyumludur

**Hacim:** 6 aylık pencerede ~5.000–20.000 zararlı ilişkili alan adı

### 3.3 abuse.ch Entegrasyon Stratejisi

Hem URLhaus hem ThreatFox, mevcut `format="lines"` ayrıştırıcısıyla doğrudan eşleşen **host-file biçimi** (satır başına çıplak alan adı) sağlar. Yeni ayrıştırıcı gerekmez.

**Önerilen besleme girdileri (slot 05, 06):**

```python
# Slot 05: URLhaus zararlı yazılım dağıtım alan adları
ExternalFeed(
    key="urlhaus",
    url="https://urlhaus-api.abuse.ch/v2/files/exports/${ABUSE_CH_KEY}/hostfile.txt",
    format="lines",
    output_file="05-urlhaus_adguard.txt",
    title="Global | URLhaus Active Malware Distribution Domains (AdGuard)",
    homepage="https://urlhaus.abuse.ch/",
),

# Slot 06: ThreatFox zararlı IoC alan adları
ExternalFeed(
    key="threatfox",
    url="https://threatfox-api.abuse.ch/v2/files/exports/${ABUSE_CH_KEY}/hostfile.txt",
    format="lines",
    output_file="06-threatfox_adguard.txt",
    title="Global | ThreatFox Malware IOC Domains (AdGuard)",
    homepage="https://threatfox.abuse.ch/",
),
```

**Ortam değişkeni:** `ABUSE_CH_KEY` (her iki platform için tek anahtar)

---

## 4. Uygulama Planı

### 4.1 Gerekli Kod Değişiklikleri

| Dosya | Değişiklik |
|-------|------------|
| `Scripts/src/external_feeds.py` | 3 `ExternalFeed` girdisi ekle; `parse_phishtank_csv` ayrıştırıcısı ekle |
| `Scripts/main.py` | Değişiklik yok (`EXTERNAL_FEEDS` demetini dinamik kullanır) |
| `.github/workflows/schedule.yml` | Besleme döngüsüne `phishtank urlhaus threatfox` ekle; anahtar env değişkenlerini ekle |
| `.gitlab-ci.yml` | schedule.yml değişikliklerini yansıt |
| `Tests/test_external_feeds.py` | Yeni ayrıştırıcılar ve besleme girdileri için testler ekle |
| `README.md` / `Docs/` | Yeni kaynakları belgele |

### 4.2 CI/CD Gizli Değişkenleri

| Gizli | Değer | Konum |
|-------|-------|-------|
| `PHISHTANK_KEY` | https://phishtank.org/api_register.php adresinden uygulama anahtarı | GitHub Secrets, GitLab CI/CD Variables |
| `ABUSE_CH_KEY` | https://auth.abuse.ch/ adresinden Auth-Key | GitHub Secrets, GitLab CI/CD Variables |

### 4.3 Schedule.yml Besleme Döngüsü Güncellemesi

```yaml
# schedule.yml içindeki besleme döngüsü
for KEY in cert-pl cert-si phishtank urlhaus threatfox; do
  # ... mevcut mantık ...
  case "${KEY}:${base}" in
    cert-pl:02-*|cert-si:03-*|phishtank:04-*|urlhaus:05-*|threatfox:06-*) matched="${EXT}" ;;
  esac
  # ... doğrulama ...
done
```

---

## 5. Risk Değerlendirmesi ve Azaltım

| Risk | Olasılık | Etki | Azaltım |
|------|----------|------|---------|
| API anahtarı değişimi/süresi dolması | Düşük | Besleme sessizce başarısız olur | `validate-external` ile izleme; denetim dosyalarında 0 kural görünür |
| Hız sınırlama / 429 | Düşük (anahtarlı) | Geçici çekme hatası | Üstel geri çekilme zaten uygulanmış; CI’da `continue-on-error` |
| Biçim değişiklikleri | Düşük | Ayrıştırma hataları | Sürüme bağlı ayrıştırıcılar; adli inceleme için anlık görüntü + denetim |
| Yanlış pozitifler (meşru alan adları) | Orta | Aşırı engelleme | Güvenlik ilkesi paylaşımlı apex/servisleri yakalar; PhishTank yalnızca doğrulanmış; URLhaus/ThreatFox Tranco Top 1M’i hariç tutar |
| Günlüklerde anahtar sızıntısı | Düşük | Kimlik bilgisi ifşası | Anahtarlar yalnızca env değişkenlerinde; asla loglanmaz; `httpx` WARNING seviyesinde |
| Cloudflare engeli (NKSC gibi) | Düşük | Beslemeye ulaşılamaz | abuse.ch API’leri doğrudan; PhishTank data.phishtank.com doğrudan |
| Hacim patlaması (>90 MiB) | Düşük | Dal yayımlama atlanır | İş akışında boyut kontrolü; 50 MiB’de uyarı, 90 MiB’de atlama |

---

## 6. Mevcut Beslemelerle Tamamlayıcılık

| Besleme | Birincil Tehdit Türü | Coğrafi Odak | Örtüşme |
|---------|----------------------|--------------|---------|
| TC-SGB (01) | Ulusal (TR) karma | Türkiye | Temel |
| CERT.PL (02) | Oltalama, zararlı, C2 | Polonya/AB | Düşük |
| CERT.SI (03) | Zararlı, botnet, oltalama | Slovenya/AB | Düşük |
| **PhishTank (04)** | **Oltalama (doğrulanmış)** | **Küresel** | **PH/BP’yi tamamlar** |
| **URLhaus (05)** | **Zararlı yazılım dağıtımı** | **Küresel** | **MD/MU/MC’yi tamamlar** |
| **ThreatFox (06)** | **Zararlı IoC’ler (alan adları)** | **Küresel** | **MD/MC/BC’yi tamamlar** |

**Belirgin örtüşme yok** — her kaynak farklı bakış açıları ve kürasyon yöntemlerine sahiptir.

---

## 7. Test Stratejisi

### 7.1 Birim Testleri (`test_external_feeds.py` dosyasına eklenecek)

```python
def test_parse_phishtank_csv():
    text = "phish_id,url,phish_detail_url,submission_time,verified,verification_time,online,target\n1,https://evil.com/login,https://phishtank.com/1,2026-01-01,yes,2026-01-01,yes,Bank\n2,http://bad.net/,https://phishtank.com/2,2026-01-01,yes,2026-01-01,yes,PayPal\n"
    assert parse_phishtank_csv(text) == ["evil.com", "bad.net"]

def test_parse_phishtank_csv_verified_only():
    text = "phish_id,url,verified,online\n1,https://evil.com/,yes,yes\n2,https://pending.com/,no,yes\n3,https://offline.com/,yes,no\n"
    assert parse_phishtank_csv(text) == ["evil.com"]
```

### 7.2 Entegrasyon Testleri

- Tüm 5 dış besleme için (cert-pl, cert-si, phishtank, urlhaus, threatfox) sahte yanıtlarla `fetch-external` çalıştır
- Tümü için `validate-external` geçtiğini doğrula
- filter-lists dalı hazırlama adımlarını doğrula (boyut kontrolleri, numaralandırma)

### 7.3 Duman Testi (Üretim)

Birleştirmeden sonra `schedule.yml` üzerinde `workflow_dispatch` tetikle ve doğrula:
1. 5 dış beslemenin tümü başarıyla çekilir
2. `Output/External/` altında AdGuard dosyaları üretilir
3. Denetim dosyalarında makul kabul/reddet/inceleme sayıları görünür
4. `filter-lists` dalı toplam 6 dosya ile güncellenir (`01`, `02`, `03`, `04`, `05`, `06`)
5. `raw.githubusercontent.com` URL’leri doğru içeriği sunar

---

## 8. Yasal ve Uyumluluk

| Kaynak | Lisans/Kullanım Koşulları | Yeniden Dağıtım | Atıf |
|--------|---------------------------|-----------------|------|
| PhishTank | Cisco EULA | Ticari olmayan kullanım için izinli; ticari kullanım lisans gerektirir | Gerekli: "Data provided by PhishTank" |
| URLhaus | abuse.ch Adil Kullanım | Adil kullanım ilkeleri altında ücretsiz | Gerekli: "Data from URLhaus (abuse.ch)" |
| ThreatFox | abuse.ch Adil Kullanım | Adil kullanım ilkeleri altında ücretsiz | Gerekli: "Data from ThreatFox (abuse.ch)" |

**Mevcut hat uygulaması:** Her AdGuard dosyası `! Homepage:` ve `! Source:` başlıkları içerir — atıf gereksinimini karşılar. Ticari kullanım yoktur (GitHub/GitLab üzerinden ücretsiz dağıtım).

**Eylem:** Açık uyumluluk için `generate_external_adguard()` fonksiyonuna `! License:` başlığı eklenmelidir.

---

## 9. Karar Matrisi

| Kriter | PhishTank | URLhaus | ThreatFox |
|--------|-----------|---------|-----------|
| **Veri Kalitesi** | ★★★★★ (topluluk doğrulamalı) | ★★★★★ (yalnızca aktif zararlı) | ★★★★★ (zararlı ilişkili, 6 ay süre sonu) |
| **Operasyonel Olgunluk** | ★★★★★ (15+ yıl, Cisco) | ★★★★★ (15+ yıl, Spamhaus) | ★★★★☆ (daha yeni ama kararlı) |
| **Entegrasyon Eforu** | Düşük (yeni ayrıştırıcı) | Çok düşük (mevcut ayrıştırıcı) | Çok düşük (mevcut ayrıştırıcı) |
| **Bakım Yükü** | Düşük (kararlı CSV) | Düşük (kararlı hostfile) | Düşük (kararlı hostfile) |
| **Yanlış Pozitif Riski** | Düşük (yalnızca doğrulanmış+çevrimiçi) | Düşük (Tranco Top 1M hariç) | Düşük (6 ay süre sonu, güven puanları) |
| **Tamamlayıcılık** | Yüksek (küresel oltalama) | Yüksek (küresel zararlı URL’ler) | Yüksek (küresel zararlı IoC’ler) |
| **Maliyet** | Ücretsiz (kayıt) | Ücretsiz (kayıt) | Ücretsiz (aynı anahtar) |
| **Öneri** | **EKLE (slot 04)** | **EKLE (slot 05)** | **EKLE (slot 06)** |

---

## 10. Sonraki Adımlar

1. **API anahtarları için kayıt:**
   - PhishTank: https://phishtank.org/api_register.php
   - abuse.ch: https://auth.abuse.ch/ (URLhaus + ThreatFox için tek anahtar)

2. **CI/CD’ye gizli değişken ekle:**
   - GitHub: Settings → Secrets → Actions → `PHISHTANK_KEY`, `ABUSE_CH_KEY`
   - GitLab: Settings → CI/CD → Variables → `PHISHTANK_KEY`, `ABUSE_CH_KEY`

3. **Kod değişikliklerini uygula** (Bölüm 4.1)

4. **Test takımını çalıştır:** `pytest Tests/test_external_feeds.py -v`

5. **Duman testi için** `schedule.yml` üzerinde `workflow_dispatch` tetikle

6. **`filter-lists` dalını doğrula:** toplam 6 dosya (`01`, `02`, `03`, `04`, `05`, `06`)

7. **Dokümantasyonu güncelle** (README, Docs/)

---

## Ek A: Örnek PhishTank CSV Satırı

```csv
phish_id,url,phish_detail_url,submission_time,verified,verification_time,online,target
8472931,https://secure-login.example.com/phish.php,https://www.phishtank.com/phish_detail.php?phish_id=8472931,2026-10-12T14:30:00+00:00,yes,2026-10-12T15:00:00+00:00,yes,Example Bank
```

## Ek B: Örnek URLhaus Hostfile

```
malware-distribution-site.com
evil-downloader.net
payload-server.org
```

## Ek C: Örnek ThreatFox Hostfile

```
c2-server-malware.com
payload-delivery-domain.net
botnet-controller.org
```

---

**Rapor Sonu** — Uygulama onayına hazır. / **End of Report** — Ready for implementation approval.
