> **Language / Dil** &nbsp;
> [EN English](#-english) &nbsp;·&nbsp; [TR Türkçe](#-türkçe)

<a id="-english"></a>

# Risk Analysis

## Overview

This document presents a comprehensive risk matrix for the TC-SGB-API-to-List project, identifying, assessing, and mitigating risks across technical, operational, legal, and security dimensions.

## Risk Matrix

### Risk Assessment Scale

| Likelihood | Score | Description |
|------------|-------|-------------|
| Rare | 1 | < 5% chance of occurring |
| Unlikely | 2 | 5-20% chance |
| Possible | 3 | 20-50% chance |
| Likely | 4 | 50-80% chance |
| Almost Certain | 5 | > 80% chance |

| Impact | Score | Description |
|--------|-------|-------------|
| Negligible | 1 | Minimal disruption, no data loss |
| Minor | 2 | Short delay, no data loss |
| Moderate | 3 | Significant delay, some data loss |
| Major | 4 | Extended outage, data loss |
| Catastrophic | 5 | Permanent damage, legal consequences |

**Risk Score** = Likelihood × Impact

| Score Range | Risk Level | Action Required |
|-------------|------------|-----------------|
| 1-4 | LOW | Monitor, accept |
| 5-9 | MEDIUM | Mitigate, plan |
| 10-15 | HIGH | Active mitigation required |
| 16-25 | CRITICAL | Immediate action required |

---

## Technical Risks

| ID | Risk | Likelihood | Impact | Score | Level | Mitigation |
|----|------|------------|--------|-------|-------|------------|
| T-01 | API endpoint changes without notice | 3 | 4 | 12 | HIGH | Version pinning, API monitoring, graceful degradation |
| T-02 | API downtime/availability issues | 3 | 3 | 9 | MEDIUM | Retry logic, caching, fallback to previous data |
| T-03 | Rate limiting introduced by API | 2 | 3 | 6 | MEDIUM | Conservative rate limits, backoff, caching |
| T-04 | Response format changes | 2 | 4 | 8 | MEDIUM | Strict schema validation, early detection |
| T-05 | Dataset size grows beyond capacity | 2 | 3 | 6 | MEDIUM | Streaming processing, chunked memory management |
| T-06 | Python version incompatibility | 2 | 2 | 4 | LOW | Support 2+ versions, CI matrix testing |
| T-07 | Dependency vulnerability discovered | 3 | 3 | 9 | MEDIUM | Dependabot, pinning, regular audits |
| T-08 | Memory exhaustion on large datasets | 2 | 3 | 6 | MEDIUM | Streaming, generators, memory limits |
| T-09 | Disk space exhaustion | 1 | 2 | 2 | LOW | Disk space checks, output rotation |
| T-10 | Network connectivity issues | 3 | 2 | 6 | MEDIUM | Retry, exponential backoff, offline mode |

---

## Operational Risks

| ID | Risk | Likelihood | Impact | Score | Level | Mitigation |
|----|------|------------|--------|-------|-------|------------|
| O-01 | CI/CD pipeline failure | 3 | 2 | 6 | MEDIUM | Manual fallback, pipeline monitoring |
| O-02 | PyPI publish failure | 2 | 2 | 4 | LOW | Retry, manual upload, test PyPI first |
| O-03 | Configuration error | 2 | 3 | 6 | MEDIUM | Config validation, schema checks |
| O-04 | Log data loss | 1 | 1 | 1 | LOW | Multiple log destinations |
| O-05 | Incorrect output format | 2 | 2 | 4 | LOW | Format validation, snapshot tests |
| O-06 | Operator unavailability | 2 | 2 | 4 | LOW | Documentation, automation, bus factor |
| O-07 | Backup failure | 1 | 2 | 2 | LOW | Git-based backup, multiple remotes |
| O-08 | Monitoring blind spots | 2 | 3 | 6 | MEDIUM | Comprehensive metrics, alerting |

---

## Security Risks

| ID | Risk | Likelihood | Impact | Score | Level | Mitigation |
|----|------|------------|--------|-------|-------|------------|
| S-01 | Supply chain attack (dependency) | 2 | 5 | 10 | HIGH | Pin dependencies, audit, Dependabot |
| S-02 | Compromised GitHub Actions | 1 | 5 | 5 | MEDIUM | Pin action SHAs, minimal permissions |
| S-03 | API impersonation/MITM | 1 | 5 | 5 | MEDIUM | TLS verification, certificate pinning |
| S-04 | Data exfiltration via logs | 2 | 3 | 6 | MEDIUM | Sanitize logs, structured logging |
| S-05 | Code injection via IoC values | 1 | 5 | 5 | MEDIUM | Input validation, no eval/exec |
| S-06 | Credential exposure | 1 | 4 | 4 | LOW | Environment variables, no secrets in code |
| S-07 | Unauthorized access to outputs | 2 | 3 | 6 | MEDIUM | File permissions, access controls |
| S-08 | Malicious pull request | 2 | 4 | 8 | MEDIUM | PR reviews, CI checks, branch protection |

---

## Legal Risks

| ID | Risk | Likelihood | Impact | Score | Level | Mitigation |
|----|------|------------|--------|-------|-------|------------|
| L-01 | Violation of TC SGB terms of service | 2 | 5 | 10 | HIGH | Legal review, compliance monitoring |
| L-02 | Copyright infringement claim | 1 | 5 | 5 | MEDIUM | Respect ToS, no redistribution |
| L-03 | License violation in dependencies | 1 | 3 | 3 | LOW | License compatibility checks |
| L-04 | Data privacy violation | 1 | 4 | 4 | LOW | No PII in IoC data, compliance review |
| L-05 | Export control violation | 1 | 4 | 4 | LOW | Check export regulations |

---

## Data Risks

| ID | Risk | Likelihood | Impact | Score | Level | Mitigation |
|----|------|------------|--------|-------|-------|------------|
| D-01 | Data corruption during processing | 2 | 3 | 6 | MEDIUM | Checksums, validation, immutable records |
| D-02 | Incomplete data fetch | 2 | 3 | 6 | MEDIUM | Page count verification, retry |
| D-03 | Data quality degradation | 3 | 2 | 6 | MEDIUM | Quality checks, anomaly detection |
| D-04 | Duplicate data in output | 2 | 2 | 4 | LOW | Deduplication, output validation |
| D-05 | Stale data in output | 3 | 2 | 6 | MEDIUM | Freshness checks, staleness alerts |
| D-06 | False positives in output | 3 | 2 | 6 | MEDIUM | FP detection, whitelisting |
| D-07 | Missing IoC types | 1 | 2 | 2 | LOW | Type coverage monitoring |

---

## Business Risks

| ID | Risk | Likelihood | Impact | Score | Level | Mitigation |
|----|------|------------|--------|-------|-------|------------|
| B-01 | Project abandonment | 2 | 3 | 6 | MEDIUM | Documentation, community, bus factor |
| B-02 | API deprecation by TC SGB | 1 | 4 | 4 | LOW | Monitor announcements, fallback sources |
| B-03 | Competing solution emerges | 3 | 1 | 3 | LOW | Focus on unique value, community |
| B-04 | User trust erosion | 2 | 3 | 6 | MEDIUM | Transparency, security, reliability |
| B-05 | Resource constraints | 2 | 2 | 4 | LOW | Automation, efficient design |

---

## Risk Heat Map

```
+=====================================================================+
|  Risk Heat Map                                                       |
+=====================================================================+

  Impact
    5 | S-01  T-01  L-01  L-02  S-03
      | T-06  S-02  S-05  S-03  B-02
    4 | L-04  L-05  T-04  S-01  L-01
      | L-06  B-02  S-08  S-06
    3 | T-02  T-05  D-01  O-01  D-06
      | T-08  O-03  D-02  D-05  D-03
    2 | T-09  O-02  B-05  O-08  D-05
      | O-04  O-06  T-07  B-04
    1 | T-10  O-07  O-04  B-03
      |       L-03  O-05  B-05
      +----------------------------------
        1      2      3      4      5
                  Likelihood

  Legend:
  +-------+-------+-------+-------+-------+
  | LOW   | MEDIUM| HIGH  |CRITICAL|      |
  | 1-4   | 5-9   | 10-15 | 16-25  |      |
  +-------+-------+-------+-------+-------+
```

---

## Risk Response Plans

### High/Critical Risks

#### T-01: API Endpoint Changes (Score: 12)

```
Response Plan:
1. Detection
   - Monitor API responses for schema changes
   - Run validation tests after each fetch
   - Alert on unexpected response structure

2. Immediate Response
   - Pause pipeline if validation fails
   - Investigate change scope
   - Check TC SGB announcements

3. Remediation
   - Update models/validators if needed
   - Test with new format
   - Deploy fix

4. Prevention
   - Subscribe to TC SGB notifications
   - Maintain API compatibility layer
   - Regular API testing
```

#### S-01: Supply Chain Attack (Score: 10)

```
Response Plan:
1. Detection
   - Dependabot security alerts
   - pip-audit vulnerability reports
   - Manual dependency review

2. Immediate Response
   - Assess vulnerability impact
   - Check if affected version was used
   - Rollback if necessary

3. Remediation
   - Update to patched version
   - Verify no compromise occurred
   - Update lock file

4. Prevention
   - Pin all dependencies
   - Regular security audits
   - Use trusted sources only
```

#### L-01: TC SGB ToS Violation (Score: 10)

```
Response Plan:
1. Detection
   - Regular ToS review
   - Legal counsel consultation
   - User reports

2. Immediate Response
   - Assess violation scope
   - Pause affected operations
   - Consult legal counsel

3. Remediation
   - Remove violating content
   - Update compliance procedures
   - Document changes

4. Prevention
   - Regular legal review
   - Compliance monitoring
   - Clear documentation
```

---

## Risk Monitoring

### Monthly Risk Review

```yaml
Monthly Review Checklist:
  - [ ] Review all HIGH/CRITICAL risks
  - [ ] Check for new risks
  - [ ] Update risk scores
  - [ ] Verify mitigations are effective
  - [ ] Review incident reports
  - [ ] Update risk register
```

### Risk Register

| Last Updated | Total Risks | HIGH | MEDIUM | LOW |
|--------------|-------------|------|--------|-----|
| 2025-01-20 | 30 | 4 | 16 | 10 |

<a id="-türkçe"></a>

# Risk Analizi

## Genel Bakış

Bu belge, TC-SGB-API-to-List projesi için kapsamlı bir risk matrisi sunmakta; teknik, operasyonel, yasal ve güvenlik boyutlarında riskleri belirleyerek değerlendirmekte ve azaltma stratejileri önermektedir.

## Risk Matrisi

### Risk Değerlendirme Ölçeği

| Olasılık | Puan | Açıklama |
|----------|------|----------|
| Nadir | 1 | < %5 olasılık |
| Olasız | 2 | %5-20 olasılık |
| Mümkün | 3 | %20-50 olasılık |
| Muhtemel | 4 | %50-80 olasılık |
| Neredeyse Kesin | 5 | > %80 olasılık |

| Etki | Puan | Açıklama |
|------|------|----------|
| Önemsiz | 1 | Asgari kesinti, veri kaybı yok |
| Küçük | 2 | Kısa gecikme, veri kaybı yok |
| Orta | 3 | Önemli gecikme, kısmi veri kaybı |
| Büyük | 4 | Uzun süreli kesinti, veri kaybı |
| Felaket | 5 | Kalıcı hasar, yasal sonuçlar |

**Risk Puanı** = Olasılık × Etki

| Puan Aralığı | Risk Seviyesi | Gerekli Aksiyon |
|--------------|---------------|-----------------|
| 1-4 | DÜŞÜK | İzleme, kabul etme |
| 5-9 | ORTA | Azaltma, planlama |
| 10-15 | YÜKSEK | Aktif azaltma gerekli |
| 16-25 | KRİTİK | Acil aksiyon gerekli |

---

## Teknik Riskler

| ID | Risk | Olasılık | Etki | Puan | Seviye | Azaltma |
|----|------|----------|------|------|--------|---------|
| T-01 | Bildirim yapılmadan API uç noktası değişiklikleri | 3 | 4 | 12 | YÜKSEK | Sürüm sabitleme, API izleme, zarif bozulma |
| T-02 | API kesinti süresi/erişilebilirlik sorunları | 3 | 3 | 9 | ORTA | Yeniden deneme mantığı, önbellekleme, önceki verilere geri dönüş |
| T-03 | API tarafından hız kısıtlaması uygulanması | 2 | 3 | 6 | ORTA | Muhafazakar hız limitleri, geri çekilme, önbellekleme |
| T-04 | Yanıt biçimi değişiklikleri | 2 | 4 | 8 | ORTA | Katı şema doğrulama, erken tespit |
| T-05 | Veri seti boyutunun kapasiteyi aşması | 2 | 3 | 6 | ORTA | Akış işleme, parçalı bellek yönetimi |
| T-06 | Python sürüm uyumsuzluğu | 2 | 2 | 4 | DÜŞÜK | 2+ sürüm desteği, CI matris testi |
| T-07 | Bağımlılık açığının keşfedilmesi | 3 | 3 | 9 | ORTA | Dependabot, sabitleme, düzenli denetimler |
| T-08 | Büyük veri setlerinde tükenme | 2 | 3 | 6 | ORTA | Akış, üreteçler, bellek limitleri |
| T-09 | Disk alanı tükenmesi | 1 | 2 | 2 | DÜŞÜK | Disk alanı kontrolleri, çıktı döndürme |
| T-10 | Ağ bağlantısı sorunları | 3 | 2 | 6 | ORTA | Yeniden deneme, üstel geri çekilme, çevrimdışı mod |

---

## Operasyonel Riskler

| ID | Risk | Olasılık | Etki | Puan | Seviye | Azaltma |
|----|------|----------|------|------|--------|---------|
| O-01 | CI/CD hattı arızası | 3 | 2 | 6 | ORTA | Manuel geri dönüş, hattı izleme |
| O-02 | PyPI yayımlama hatası | 2 | 2 | 4 | DÜŞÜK | Yeniden deneme, manuel yükleme, önce test PyPI |
| O-03 | Yapılandırma hatası | 2 | 3 | 6 | ORTA | Yapılandırma doğrulama, şema kontrolleri |
| O-04 | Günlük veri kaybı | 1 | 1 | 1 | DÜŞÜK | Çoklu günlük hedefi |
| O-05 | Yanlış çıktı biçimi | 2 | 2 | 4 | DÜŞÜK | Biçim doğrulama, anlık görüntü testleri |
| O-06 | Operatörün kullanılamaması | 2 | 2 | 4 | DÜŞÜK | Dokümantasyon, otomasyon, otobüs faktörü |
| O-07 | Yedekleme arızası | 1 | 2 | 2 | DÜŞÜK | Tabanlı yedekleme, çoklu uzak depolar |
| O-08 | İzleme kör noktaları | 2 | 3 | 6 | ORTA | Kapsamlı metrikler, uyarılar |

---

## Güvenlik Riskleri

| ID | Risk | Olasılık | Etki | Puan | Seviye | Azaltma |
|----|------|----------|------|------|--------|---------|
| S-01 | Tedarik zinciri saldırısı (bağımlılık) | 2 | 5 | 10 | YÜKSEK | Bağımlılıkları sabitleme, denetim, Dependabot |
| S-02 | Ele geçirilmiş GitHub Actions | 1 | 5 | 5 | ORTA | Action SHA'larını sabitleme, asgari izinler |
| S-03 | API taklidi/MITM | 1 | 5 | 5 | ORTA | TLS doğrulama, sertifika sabitleme |
| S-04 | Günlükler aracılığıyla veri sızıntısı | 2 | 3 | 6 | ORTA | Günlük temizleme, yapılandırılmış günlük kaydı |
| S-05 | IoC değerleri üzerinden kod enjeksiyonu | 1 | 5 | 5 | ORTA | Girdi doğrulaması, eval/exec kullanmama |
| S-06 | Kimlik bilgilerinin ifşası | 1 | 4 | 4 | DÜŞÜK | Ortam değişkenleri, kodda sır tutmama |
| S-07 | Çıktılara yetkisiz erişim | 2 | 3 | 6 | ORTA | Dosya izinleri, erişim kontrolleri |
| S-08 | Kötü niyetli pull request | 2 | 4 | 8 | ORTA | PR incelemeleri, CI kontrolleri, dal koruma |

---

## Yasal Riskler

| ID | Risk | Olasılık | Etki | Puan | Seviye | Azaltma |
|----|------|----------|------|------|--------|---------|
| L-01 | TC SGB hizmet şartlarının ihlali | 2 | 5 | 10 | YÜKSEK | Hukuki inceleme, uyumluluk izleme |
| L-02 | Telif hakkı ihlali iddiası | 1 | 5 | 5 | ORTA | Hizmet şartlarına saygı, yeniden dağıtım yapmama |
| L-03 | Bağımlılıklarda lisans ihlali | 1 | 3 | 3 | DÜŞÜK | Lisans uyumluluğu kontrolleri |
| L-04 | Veri gizliliği ihlali | 1 | 4 | 4 | DÜŞÜK | IoC verisinde Kişisel Veri Bulunmaması, uyumluluk incelemesi |
| L-05 | İhracat kontrolü ihlali | 1 | 4 | 4 | DÜŞÜK | İhracat düzenlemelerini kontrol etme |

---

## Veri Riskleri

| ID | Risk | Olasılık | Etki | Puan | Seviye | Azaltma |
|----|------|----------|------|------|--------|---------|
| D-01 | İşleme sırasında veri bozulması | 2 | 3 | 6 | ORTA | Sağlam toplama, doğrulama, değişmez kayıtlar |
| D-02 | Eksik veri çekimi | 2 | 3 | 6 | ORTA | Sayfa sayısı doğrulama, yeniden deneme |
| D-03 | Veri kalitesinin düşmesi | 3 | 2 | 6 | ORTA | Kalite kontrolleri, anomalisi tespiti |
| D-04 | Çıktıda tekrarlanan veri | 2 | 2 | 4 | DÜŞÜK | Tekilleştirme, çıktı doğrulama |
| D-05 | Çıktıda eski veri | 3 | 2 | 6 | ORTA | Tazelik kontrolleri, eskime uyarıları |
| D-06 | Çıktıda yanlış pozitifler | 3 | 2 | 6 | ORTA | Yanlış pozitif tespiti, beyaz liste |
| D-07 | Eksik IoC türleri | 1 | 2 | 2 | DÜŞÜK | Tür kapsama izleme |

---

## İş Riskleri

| ID | Risk | Olasılık | Etki | Puan | Seviye | Azaltma |
|----|------|----------|------|------|--------|---------|
| B-01 | Projenin terk edilmesi | 2 | 3 | 6 | ORTA | Dokümantasyon, topluluk, otobüs faktörü |
| B-02 | TC SGB tarafından API'nin kullanımdan kaldırılması | 1 | 4 | 4 | DÜŞÜK | Duyuruları izleme, yedek kaynaklar |
| B-03 | Rakip çözümün ortaya çıkması | 3 | 1 | 3 | DÜŞÜK | Benzersiz değere odaklanma, topluluk |
| B-04 | Kullanıcı güveninin erozyona uğraması | 2 | 3 | 6 | ORTA | Şeffaflık, güvenlik, güvenilirlik |
| B-05 | Kaynak kısıtlamaları | 2 | 2 | 4 | DÜŞÜK | Otomasyon, verimli tasarım |

---

## Risk Haritası

```
+=====================================================================+
|  Risk Haritası                                                       |
+=====================================================================+

  Etki
    5 | S-01  T-01  L-01  L-02  S-03
      | T-06  S-02  S-05  S-03  B-02
    4 | L-04  L-05  T-04  S-01  L-01
      | L-06  B-02  S-08  S-06
    3 | T-02  T-05  D-01  O-01  D-06
      | T-08  O-03  D-02  D-05  D-03
    2 | T-09  O-02  B-05  O-08  D-05
      | O-04  O-06  T-07  B-04
    1 | T-10  O-07  O-04  B-03
      |       L-03  O-05  B-05
      +----------------------------------
        1      2      3      4      5
                  Olasılık

  Gösterim:
  +-------+-------+-------+-------+-------+
  | DÜŞÜK | ORTA  | YÜKSEK|KRİTİK|       |
  | 1-4   | 5-9   | 10-15 | 16-25 |       |
  +-------+-------+-------+-------+-------+
```

---

## Risk Yanıt Planları

### Yüksek/Kritik Riskler

#### T-01: API Uç Noktası Değişiklikleri (Puan: 12)

```
Yanıt Planı:
1. Tespit
   - API yanıtlarını şema değişiklikleri için izleme
   - Her çekimden sonra doğrulama testleri çalıştırma
   - Beklenmeyen yanıt yapısında uyarı

2. Acil Yanıt
   - Doğrulama başarısız olursa hattı durdurma
   - Değişiklik kapsamını araştırma
   - TC SGB duyurularını kontrol etme

3. Çözüm
   - Gerekirse modelleri/doğrulayıcıları güncelleme
   - Yeni biçimde test etme
   - Düzeltmeyi dağıtma

4. Önleme
   - TC SGB bildirimlerine abone olma
   - API uyumluluk katmanını sürdürme
   - Düzenli API testi
```

#### S-01: Tedarik Zinciri Saldırısı (Puan: 10)

```
Yanıt Planı:
1. Tespit
   - Dependabot güvenlik uyarıları
   - pip-audit zafiyet raporları
   - Manuel bağımlılık incelemesi

2. Acil Yanıt
   - Açığın etkisini değerlendirme
   - Etkilenen sürümün kullanılıp kullanılmadığını kontrol etme
   - Gerekirse geri alma

3. Çözüm
   - Yamalanmış sürüme güncelleme
   - Herhangi bir ihlalin gerçekleşmediğini doğrulama
   - Kilit dosyasını güncelleme

4. Önleme
   - Tüm bağımlılıkları sabitleme
   - Düzenli güvenlik denetimleri
   - Yalnızca güvenilir kaynakları kullanma
```

#### L-01: TC SGB Hizmet Şartları İhlali (Puan: 10)

```
Yanıt Planı:
1. Tespit
   - Düzenli hizmet şartları incelemesi
   - Hukuki danışman görüşü
   - Kullanıcı bildirimleri

2. Acil Yanıt
   - İhlal kapsamını değerlendirme
   - Etkilenen işlemleri durdurma
   - Hukuki danışmana danışma

3. Çözüm
   - İhlal eden içeriği kaldırma
   - Uyumluluk prosedürlerini güncelleme
   - Değişiklikleri belgeleme

4. Önleme
   - Düzenli hukuki inceleme
   - Uyumluluk izleme
   - Açık dokümantasyon
```

---

## Risk İzleme

### Aylık Risk İncelemesi

```yaml
Aylık İnceleme Kontrol Listesi:
  - [ ] Tüm YÜKSEK/KRİTİK riskleri inceleme
  - [ ] Yeni riskleri kontrol etme
  - [ ] Risk puanlarını güncelleme
  - [ ] Azaltmaların etkili olduğunu doğrulama
  - [ ] Olay raporlarını inceleme
  - [ ] Risk kaydını güncelleme
```

### Risk Kaydı

| Son Güncelleme | Toplam Risk | YÜKSEK | ORTA | DÜŞÜK |
|----------------|-------------|--------|------|-------|
| 2025-01-20 | 30 | 4 | 16 | 10 |
