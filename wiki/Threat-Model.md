> **Language / Dil** &nbsp;
> [EN English](#-english) &nbsp;·&nbsp; [TR Türkçe](#-türkçe)

<a id="-english"></a>

# Threat Model

## Overview

This document presents a STRIDE-based threat model for the TC-SGB-API-to-List threat intelligence pipeline. The system ingests IOC data from an external API, processes it through multiple stages, and outputs to various formats.

## System Boundary

```
+=====================================================================+
|                     TRUST BOUNDARY                                   |
+=====================================================================+
|                                                                     |
|  +-------------------+     +-----------------------------------+   |
|  |                   |     |                                   |   |
|  |  TC SGB API       |     |  TC-SGB-API-to-List Pipeline         |   |
|  |  (Untrusted)      |---->|                                   |   |
|  |                   |     |  - Client (httpx)                 |   |
|  |  External Server  |     |  - Validator                      |   |
|  |  No Auth Required |     |  - Normalizer                     |   |
|  |                   |     |  - Deduplicator                   |   |
|  +-------------------+     |  - Quality Engine                 |   |
|                            |  - Output Engine                  |   |
|  INTERNET                 |  - Pipeline Orchestrator           |   |
|                            |                                   |   |
|                            +-----------------------------------+   |
|                                  |                                |
|                                  v                                |
|                            +-----------+                          |
|                            |  Local     |                         |
|                            |  Filesystem|                         |
|                            +-----------+                          |
|                                                                     |
+=====================================================================+
```

## STRIDE Analysis

### S — Spoofing

| ID | Threat | Description | Likelihood | Impact | Mitigation |
|----|--------|-------------|------------|--------|------------|
| S-01 | API Impersonation | Attacker creates fake API endpoint serving malicious IOCs | LOW | CRITICAL | Certificate pinning, validate TLS, verify API URL in config |
| S-02 | DNS Spoofing | DNS poisoning redirects API calls to attacker server | LOW | CRITICAL | Use IP-based connection or DNS-over-HTTPS, validate certs |
| S-03 | Man-in-the-Middle | Attacker intercepts API responses in transit | MEDIUM | HIGH | Enforce TLS 1.2+, verify certificates, HSTS |
| S-04 | Data Source Spoofing | Compromised upstream feeds inject false IOCs | LOW | HIGH | Checksum validation, source attribution, anomaly detection |

**Mitigations**:
- Use `httpx` with TLS verification enabled by default
- Validate API endpoint URL against hardcoded configuration
- Log all source URLs for audit trail
- Implement response integrity checks (hash verification)
- Use DNS-over-HTTPS or system resolver with validation

### T — Tampering

| ID | Threat | Description | Likelihood | Impact | Mitigation |
|----|--------|-------------|------------|--------|------------|
| T-01 | API Response Tampering | MITM modifies IOC data in transit | LOW | HIGH | TLS, response hashing, tamper detection |
| T-02 | Local File Tampering | Attacker modifies output files on disk | LOW | MEDIUM | File permissions, integrity checks, checksums |
| T-03 | Configuration Tampering | Attacker modifies pipeline config | LOW | HIGH | Config validation, version control, checksums |
| T-04 | IOC Injection | Malicious IOC values cause processing issues | MEDIUM | MEDIUM | Input validation, sanitization, length limits |
| T-05 | Output Tampering | Generated files modified before distribution | LOW | HIGH | File signing, checksums, secure distribution |

**Mitigations**:
- Validate all input data with Pydantic models
- Reject records with unexpected characters or formats
- Generate SHA-256 checksums for all output files
- Store configuration in version control
- Implement output file integrity verification

### R — Repudiation

| ID | Threat | Description | Likelihood | Impact | Mitigation |
|----|--------|-------------|------------|--------|------------|
| R-01 | Processing Denial | Operator denies running pipeline or modifying output | LOW | LOW | Audit logging, timestamps, version control |
| R-02 | API Access Denial | Operator denies accessing TC SGB API | LOW | LOW | API request logging, response caching |
| R-03 | Data Modification Denial | Operator denies altering processed data | LOW | MEDIUM | Hash chains, audit trail, immutable logs |

**Mitigations**:
- Structured JSON logging with timestamps
- Git history for all configuration changes
- Processing metadata embedded in output files
- Audit trail for all pipeline runs

### I — Information Disclosure

| ID | Threat | Description | Likelihood | Impact | Mitigation |
|----|--------|-------------|------------|--------|------------|
| I-01 | API Key Exposure | If auth is ever added, keys exposed in logs/config | LOW | HIGH | Never log secrets, use environment variables |
| I-02 | IOC Data Leakage | Sensitive threat data exposed to unauthorized parties | MEDIUM | MEDIUM | Access controls on output files, secure distribution |
| I-03 | Log Injection | Attacker injects data into logs to exfiltrate info | LOW | MEDIUM | Sanitize log inputs, structured logging |
| I-04 | Metadata Disclosure | Processing metadata reveals infrastructure details | LOW | LOW | Minimize metadata in outputs |
| I-05 | Network Exposure | API traffic intercepted on public networks | LOW | MEDIUM | TLS encryption, VPN for sensitive environments |

**Mitigations**:
- Never log raw IOC data at DEBUG level
- Use structured logging with sanitized fields
- Restrict output file permissions (0644/0755)
- Process data locally, don't expose intermediate results
- Use environment variables for any credentials

### D — Denial of Service

| ID | Threat | Description | Likelihood | Impact | Mitigation |
|----|--------|-------------|------------|--------|------------|
| D-01 | API Rate Limiting | TC SGB API blocks or slows our requests | MEDIUM | MEDIUM | Respectful rate limiting, exponential backoff |
| D-02 | Resource Exhaustion | Extremely large dataset exhausts memory/disk | LOW | HIGH | Memory-efficient processing, streaming, limits |
| D-03 | Disk Space Exhaustion | Output files consume all available disk | LOW | MEDIUM | Disk space checks, output size limits |
| D-04 | CPU Exhaustion | Complex processing blocks system | LOW | LOW | Async processing, resource limits |
| D-05 | API Downtime | TC SGB API becomes unavailable | MEDIUM | HIGH | Retry logic, graceful degradation, caching |

**Mitigations**:
- Implement bounded concurrency (max 5 concurrent requests)
- Use streaming/chunked processing for large datasets
- Check disk space before writing outputs
- Set memory limits and use generators where possible
- Cache last successful fetch for offline operation

### E — Elevation of Privilege

| ID | Threat | Description | Likelihood | Impact | Mitigation |
|----|--------|-------------|------------|--------|------------|
| E-01 | Dependency Vulnerability | Malicious or vulnerable dependency installed | MEDIUM | HIGH | Dependabot, pin versions, audit dependencies |
| E-02 | Code Injection via IOC | IOC value causes code execution during processing | LOW | CRITICAL | No eval/exec, safe string handling, input validation |
| E-03 | Path Traversal | IOC value or config causes file access outside boundaries | LOW | HIGH | Validate paths, use Path objects, sandboxing |
| E-04 | YAML Deserialization | Malicious YAML config causes code execution | LOW | HIGH | Use safe YAML loader only |
| E-05 | Template Injection | IOC value injected into Jinja2 templates | LOW | HIGH | Auto-escaping, sandboxed templates |

**Mitigations**:
- Never use `eval()`, `exec()`, or `subprocess` with user data
- Use Pydantic for all input validation
- Validate file paths using `pathlib.Path.resolve()`
- Use `yaml.safe_load()` only
- Enable Jinja2 auto-escaping
- Pin all dependency versions
- Run with minimal OS permissions

---

## Threat Matrix

```
+=====================================================================+
|  STRIDE Threat Matrix                                               |
+=====================================================================+
|                    | Spoofing | Tampering | Repudiation | Info Disc |
|--------------------|----------|-----------|-------------|-----------|
| API Client         |   S-01   |   T-01    |    R-02     |   I-05    |
| Data Models        |   S-04   |   T-04    |    R-03     |   I-02    |
| Validator          |     -    |   T-04    |      -      |     -     |
| Normalizer         |     -    |   T-04    |      -      |   I-03    |
| Deduplicator       |     -    |     -     |    R-03     |   I-02    |
| Quality Engine     |     -    |     -     |    R-01     |   I-04    |
| Output Engine      |   S-04   |   T-05    |    R-01     |   I-02    |
| Pipeline           |   S-02   |   T-03    |    R-01     |   I-01    |
| Filesystem         |     -    |   T-02    |    R-03     |   I-02    |
+=====================================================================+
|                    | DoS      | Elev Priv |
|--------------------|----------|-----------|
| API Client         |   D-01   |   E-01    |
| Data Models        |     -    |     -     |
| Validator          |     -    |   E-02    |
| Normalizer         |     -    |   E-02    |
| Deduplicator       |   D-02   |     -     |
| Quality Engine     |   D-04   |     -     |
| Output Engine      |   D-03   |   E-03    |
| Pipeline           |   D-05   |   E-01    |
| Filesystem         |   D-03   |   E-03    |
+=====================================================================+
```

## Risk Summary

| Risk Level | Count | Description |
|------------|-------|-------------|
| CRITICAL | 2 | S-01 (API impersonation), E-02 (code injection) |
| HIGH | 6 | T-01, T-02, T-03, T-05, I-01, E-01 |
| MEDIUM | 8 | S-03, T-04, I-02, I-03, D-01, D-02, D-05, E-04 |
| LOW | 8 | S-02, S-04, R-01, R-02, R-03, I-04, D-03, D-04 |

## Security Controls

### Preventive Controls

1. **Input Validation**: All API responses validated through Pydantic models
2. **TLS Enforcement**: HTTPS-only with certificate verification
3. **Rate Limiting**: Bounded concurrency and request throttling
4. **Dependency Auditing**: Automated vulnerability scanning via Dependabot
5. **Secure Coding**: No eval/exec, safe YAML loading, template escaping
6. **Path Validation**: All file operations use resolved paths

### Detective Controls

1. **Audit Logging**: All pipeline operations logged with timestamps
2. **Integrity Checks**: SHA-256 checksums for output files
3. **Anomaly Detection**: Statistical analysis for unusual patterns
4. **Error Monitoring**: Structured error reporting and alerting
5. **Dependency Monitoring**: Automated security advisories

### Corrective Controls

1. **Retry Logic**: Exponential backoff for transient failures
2. **Graceful Degradation**: Continue with partial data on failures
3. **Rollback**: Version-tagged releases enable rollback
4. **Incident Response**: Documented procedures for security events
5. **Backup**: Previous run outputs retained for comparison

## Assumptions

1. The TC SGB API is operated by a trusted government entity
2. The API endpoint uses valid TLS certificates
3. The Python runtime and standard library are trusted
4. The operating system provides basic security primitives
5. Network connectivity to the API endpoint is available
6. Local filesystem permissions are correctly configured

## Out of Scope

- Physical security of the processing environment
- Social engineering attacks against operators
- Supply chain attacks on Python/OS packages (beyond dependency auditing)
- Attacks against the TC SGB infrastructure itself
- Availability of the TC SGB API

---

<a id="-türkçe"></a>

# Tehdit Modeli

## Genel Bakış

Bu belge, TC-SGB-API-to-List tehdit istihbarat hattı için STRIDE tabanlı bir tehdit modeli sunmaktadır. Sistem, harici bir API'den IOC verilerini alır, birden fazla aşamadan geçirir ve çeşitli formatlara çıktı üretir.

## Sistem Sınırı

```
+=====================================================================+
|                     GÜVEN SINIRI                                     |
+=====================================================================+
|                                                                     |
|  +-------------------+     +-----------------------------------+   |
|  |                   |     |                                   |   |
|  |  TC SGB API       |     |  TC-SGB-API-to-List Hattı            |   |
|  |  (Güvenilmez)     |---->|                                   |   |
|  |                   |     |  - İstemci (httpx)                 |   |
|  |  Harici Sunucu    |     |  - Doğrulayıcı                    |   |
|  |  Kimlik Doğrulama |     |  - Normalleştirici                |   |
|  |  Gerektirmez      |     |  - Tekilleştirici                  |   |
|  +-------------------+     |  - Kalite Motoru                   |   |
|                            |  - Çıktı Motoru                   |   |
|  İNTERNET                 |  - Hat Orkestratörü                |   |
|                            |                                   |   |
|                            +-----------------------------------+   |
|                                  |                                |
|                                  v                                |
|                            +-----------+                          |
|                            |  Yerel     |                         |
|                            |  Dosya Sistemi|                    |
|                            +-----------+                          |
|                                                                     |
+=====================================================================+
```

## STRIDE Analizi

### S — Taklit (Spoofing)

| ID | Tehdit | Açıklama | Olasılık | Etki | Azaltma |
|----|--------|----------|----------|------|---------|
| S-01 | API Taklidi | Saldırgan kötü amaçlı IOC sunan sahte bir API uç noktası oluşturur | DÜŞÜK | KRİTİK | Sertifika sabitleme, TLS doğrulama, yapılandırmadaki API URL'sini doğrulama |
| S-02 | DNS Taklidi | DNS zehirlenmesi API çağrılarını salırgan sunucusuna yönlendirir | DÜŞÜK | KRİTİK | IP tabanlı bağlantı veya DNS-over-HTTPS kullanımı, sertifikaları doğrulama |
| S-03 | Araadamıcı Saldırı | Saldıran transitteki API yanıtlarını dinler | ORTA | YÜKSEK | TLS 1.2+ zorunlu kılma, sertifikaları doğrulama, HSTS |
| S-04 | Veri Kaynağı Taklidi | Ele geçirilmiş üst beslemeler yanlış IOC'ler enjekte eder | DÜŞÜK | YÜKSEK | Kontrol toplamı doğrulama, kaynak atıfı, anormallik tespiti |

**Azaltma Önlemleri**:
- Varsayılan olarak TLS doğrulaması etkin olan `httpx` kullanımı
- API uç noktası URL'sini kodlanmış yapılandırmaya göre doğrulama
- Tüm kaynak URL'lerini denetim izi için kaydetme
- Yanıt bütünlüğü kontrolleri uygulama (hash doğrulama)
- Doğrulamalı DNS-over-HTTPS veya sistem çözümleyici kullanma

### T — Kurcalama (Tampering)

| ID | Tehdit | Açıklama | Olasılık | Etki | Azaltma |
|----|--------|----------|----------|------|---------|
| T-01 | API Yanıtı Kurcalama | MITM transitteki IOC verilerini değiştirir | DÜŞÜK | YÜKSEK | TLS, yanıt hash'leme, kurcalama tespiti |
| T-02 | Yerel Dosya Kurcalama | Saldıran disk üzerindeki çıktı dosyalarını değiştirir | DÜŞÜK | ORTA | Dosya izinleri, bütünlük kontrolleri, kontrol toplamları |
| T-03 | Yapılandırma Kurcalama | Saldıran hat yapılandırmasını değiştirir | DÜŞÜK | YÜKSEK | Yapılandırma doğrulama, sürüm kontrolü, kontrol toplamları |
| T-04 | IOC Enjeksiyonu | Kötü amaçlı IOC değerleri işleme sorunlarına neden olur | ORTA | ORTA | Giriş doğrulama, arındırma, uzunluk sınırları |
| T-05 | Çıktı Kurcalama | Üretilen dosyalar dağıtımdan önce değiştirilir | DÜŞÜK | YÜKSEK | Dosya imzalama, kontrol toplamları, güvenli dağıtım |

**Azaltma Önlemleri**:
- Tüm giriş verilerini Pydantic modelleriyle doğrulama
- Beklenmeyen karakterlere veya formatlara sahip kayıtları reddetme
- Tüm çıktı dosyaları için SHA-256 kontrol toplamları üretme
- Yapılandırmayı sürüm kontrolünde saklama
- Çıktı dosyası bütünlüğü doğrulaması uygulama

### R — İnkar (Repudiation)

| ID | Tehdit | Açıklama | Olasılık | Etki | Azaltma |
|----|--------|----------|----------|------|---------|
| R-01 | İşlemeyi İnkâr | Operatör hattı çalıştırmayı veya çıktıyı değiştirmeyi inkâr eder | DÜŞÜK | DÜŞÜK | Denetim kaydı, zaman damgaları, sürüm kontrolü |
| R-02 | API Erişimini İnkâr | Operatör TC SGB API'sine erişimi inkâr eder | DÜŞÜK | DÜŞÜK | API istek kaydı, yanıt önbellekleme |
| R-03 | Veri Değişikliğini İnkâr | Operatör işlenen verileri değiştirmeyi inkâr eder | DÜŞÜK | ORTA | Hash zincirleri, denetim izi, değişmez kayıtlar |

**Azaltma Önlemleri**:
- Zaman damgalı yapılandırılmış JSON kaydı
- Tüm yapılandırma değişiklikleri için Git geçmişi
- Çıktı dosyalarına gömülü işleme meta verisi
- Tüm hat çalışmaları için denetim izi

### I — Bilgi İfşası (Information Disclosure)

| ID | Tehdit | Açıklama | Olasılık | Etki | Azaltma |
|----|--------|----------|----------|------|---------|
| I-01 | API Anahtarı Sızıntısı | Kimlik doğrulama eklenirse anahtarlar kayıtlar/yapılandırmada sızdırılabilir | DÜŞÜK | YÜKSEK | Gizli anahtarları asla kaydetmeme, ortam değişkenleri kullanma |
| I-02 | IOC Veri Sızıntısı | Hassas tehdit verileri yetkisiz taraflara ifşa edilir | ORTA | ORTA | Çıktı dosyalarında erişim kontrolleri, güvenli dağıtım |
| I-03 | Kayıt Enjeksiyonu | Saldıran bilgi sızdırmak için kayıtlara veri enjekte eder | DÜŞÜK | ORTA | Kayıt girdilerini arındırma, yapılandırılmış kaydetme |
| I-04 | Meta Veri İfşası | İşleme meta verisi altyapı detaylarını ortaya çıkarır | DÜŞÜK | DÜŞÜK | Çıktılarda meta veriyi en aza indirme |
| I-05 | Ağ İfşası | API trafiği halka açık ağlarda dinlenir | DÜŞÜK | ORTA | TLS şifreleme, hassas ortamlar için VPN |

**Azaltma Önlemleri**:
- Ham IOC verilerini asla DEBUG düzeyinde kaydetmeme
- Arındırılmış alanlara sahip yapılandırılmış kaydetme kullanma
- Çıktı dosyası izinlerini kısıtlama (0644/0755)
- Verileri yerel olarak işleme, ara sonuçları ifşa etmeme
- Tüm kimlik bilgileri için ortam değişkenlerini kullanma

### D — Hizmet Reddi (Denial of Service)

| ID | Tehdit | Açıklama | Olasılık | Etki | Azaltma |
|----|--------|----------|----------|------|---------|
| D-01 | API Hız Sınırı | TC SGB API isteklerimizi engeller veya yavaşlatır | ORTA | ORTA | Saygılı hız sınırlama, üssel geri çekilme |
| D-02 | Kaynak Tüketimi | Aşırı büyük veri seti belleği/diski tüketir | DÜŞÜK | YÜKSEK | Bellek açısından verimli işleme, akış, sınırlar |
| D-03 | Disk Alanı Tüketimi | Çıktı dosyaları mevcut diskin tamamını tüketir | DÜŞÜK | ORTA | Disk alanı kontrolleri, çıktı boyutu sınırları |
| D-04 | İşlemci Tüketimi | Karmaşık işleme sistemi bloke eder | DÜŞÜK | DÜŞÜK | Eşzamanlı işleme, kaynak sınırları |
| D-05 | API Kesintisi | TC SGB API kullanılamaz hale gelir | ORTA | YÜKSEK | Yeniden deneme mantığı, zarif bozulma, önbellekleme |

**Azaltma Önlemleri**:
- Sınırlı eşzamanlılık uygulama (maks. 5 eşzamanlı istek)
- Büyük veri setleri için akış/parçalı işleme kullanma
- Çıktıları yazmadan önce disk alanını kontrol etme
- Bellek sınırları belirleme ve mümkün olduğunca üreteçler kullanma
- Çevrimdışı çalışma için son başarılı çekimi önbelleğe alma

### E — Ayrıcalık Yükseltme (Elevation of Privilege)

| ID | Tehdit | Açıklama | Olasılık | Etki | Azaltma |
|----|--------|----------|----------|------|---------|
| E-01 | Bağımlılık Zafiyeti | Kötü amaçlı veya zafiyet içeren bağımlılık yüklenir | ORTA | YÜKSEK | Dependabot, sürüm sabitleme, bağımlılık denetimi |
| E-02 | IOC Üzerinden Kod Enjeksiyonu | IOC değeri işleme sırasında kod çalıştırılmasına neden olur | DÜŞÜK | KRİTİK | eval/exec yok, güvenli dize işleme, giriş doğrulama |
| E-03 | Yol Geçişi | IOC değeri veya yapılandırma sınırlar dışında dosya erişimine neden olur | DÜŞÜK | YÜKSEK | Yolları doğrulama, Nesne sınıfları kullanma, sandık oluşturma |
| E-04 | YAML Serileştirme | Kötü amaçlı YAML yapılandırması kod çalıştırılmasına neden olur | DÜŞÜK | YÜKSEK | Yalnızca güvenli YAML yükleyici kullanma |
| E-05 | Şablon Enjeksiyonu | IOC değeri Jinja2 şablonlarına enjekte edilir | DÜŞÜK | YÜKSEK | Otomatik kaçış, sandıklı şablonlar |

**Azaltma Önlemleri**:
- Kullanıcı verileriyle asla `eval()`, `exec()` veya `subprocess` kullanmama
- Tüm giriş doğrulaması için Pydantic kullanma
- Dosya yollarını `pathlib.Path.resolve()` kullanarak doğrulama
- Yalnızca `yaml.safe_load()` kullanma
- Jinja2 otomatik kaçışını etkinleştirme
- Tüm bağımlılık sürümlerini sabitleme
- Minimum işletim sistemi izinleriyle çalıştırma

---

## Tehdit Matrisi

```
+=====================================================================+
|  STRIDE Tehdit Matrisi                                              |
+=====================================================================+
|                    | Taklit | Kurcalama | İnkar | Bilgi İfşası |
|--------------------|--------|-----------|-------|--------------|
| API İstemcisi       |  S-01  |   T-01    | R-02  |     I-05     |
| Veri Modelleri      |  S-04  |   T-04    | R-03  |     I-02     |
| Doğrulayıcı        |    -   |   T-04    |   -   |      -       |
| Normalleştirici    |    -   |   T-04    |   -   |     I-03     |
| Tekilleştirici     |    -   |     -     | R-03  |     I-02     |
| Kalite Motoru      |    -   |     -     | R-01  |     I-04     |
| Çıktı Motoru       |  S-04  |   T-05    | R-01  |     I-02     |
| Hat                |  S-02  |   T-03    | R-01  |     I-01     |
| Dosya Sistemi      |    -   |   T-02    | R-03  |     I-02     |
+=====================================================================+
|                    | Hizmet Reddi | Ayrıcalık Yükseltme |
|--------------------|--------------|---------------------|
| API İstemcisi       |     D-01     |        E-01         |
| Veri Modelleri      |       -      |          -          |
| Doğrulayıcı        |       -      |        E-02         |
| Normalleştirici    |       -      |        E-02         |
| Tekilleştirici     |     D-02     |          -          |
| Kalite Motoru      |     D-04     |          -          |
| Çıktı Motoru       |     D-03     |        E-03         |
| Hat                |     D-05     |        E-01         |
| Dosya Sistemi      |     D-03     |        E-03         |
+=====================================================================+
```

## Risk Özeti

| Risk Seviyesi | Sayı | Açıklama |
|---------------|------|----------|
| KRİTİK | 2 | S-01 (API taklidi), E-02 (kod enjeksiyonu) |
| YÜKSEK | 6 | T-01, T-02, T-03, T-05, I-01, E-01 |
| ORTA | 8 | S-03, T-04, I-02, I-03, D-01, D-02, D-05, E-04 |
| DÜŞÜK | 8 | S-02, S-04, R-01, R-02, R-03, I-04, D-03, D-04 |

## Güvenlik Kontrolleri

### Önleyici Kontroller

1. **Giriş Doğrulaması**: Tüm API yanıtları Pydantic modelleri aracılığıyla doğrulanır
2. **TLS Zorunlu Kılma**: Yalnızca HTTPS ve sertifika doğrulaması
3. **Hız Sınırı**: Sınırlı eşzamanlılık ve istek kısıtlama
4. **Bağımlılık Denetimi**: Dependabot aracılığıyla otomatik zafiyet taraması
5. **Güvenli Kodlama**: eval/exec yok, güvenli YAML yükleme, şablon kaçışı
6. **Yol Doğrulaması**: Tüm dosya işlemleri çözülmüş yollar kullanır

### Tespit Edici Kontroller

1. **Denetim Kaydı**: Tüm hat işlemleri zaman damgalarıyla kaydedilir
2. **Bütünlük Kontrolleri**: Çıktı dosyaları için SHA-256 kontrol toplamları
3. **Anormallik Tespiti**: Olağandışı kalıplar için istatistiksel analiz
4. **Hata İzleme**: Yapılandırılmış hata raporlama ve uyarı
5. **Bağımlılık İzleme**: Otomatik güvenlik duyuruları

### Düzeltici Kontroller

1. **Yeniden Deneme Mantığı**: Geçici hatalar için üssel geri çekilme
2. **Zarif Bozulma**: Hatalarda kısmi verilerle devam etme
3. **Geri Alma**: Sürüm etiketli sürümler geri almayı sağlar
4. **Olay Müdahalesi**: Güvenlik olayları için belgelenmiş prosedürler
5. **Yedekleme**: Karşılaştırma için önceki çalışma çıktıları saklanır

## Varsayımlar

1. TC SGB API'si güvenilir bir devlet kurumu tarafından işletilmektedir
2. API uç noktası geçerli TLS sertifikaları kullanmaktadır
3. Python çalışma zamanı ve standart kütüphane güvenilirdir
4. İşletim sistemi temel güvenlik ilkelerini sağlar
5. API uç noktasına ağ bağlantısı mevcuttur
6. Yerel dosya sistemi izinleri doğru yapılandırılmıştır

## Kapsam Dışı

- İşleme ortamının fiziksel güvenliği
- Operatörlere karşı sosyal mühendislik saldırıları
- Python/OS paketlerine yönelik tedarik zinciri saldırıları (bağımlılık denetiminin ötesinde)
- TC SGB altyapısının kendisine yönelik saldırılar
- TC SGB API'sinin kullanılabilirliği
