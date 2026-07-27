> **Language / Dil** &nbsp;
> [EN English](#-english) &nbsp;·&nbsp; [TR Türkçe](#-türkçe)

<a id="-english"></a>

# License and Redistribution Analysis

## Overview

This document analyzes the legal and licensing constraints governing the TC-SGB-API-to-List project, specifically regarding the use and redistribution of data obtained from the Turkish National Cyber Security Directorate (T.C. Siber Güvenlik Başkanlığı) API.

## Legal Framework

### Governing Law

The content published by the TC SGB is governed by:

- **Turkish Copyright Law No. 5846** (Fikir ve Sanat Eserleri Kanunu)
- **Terms of Service** published at https://siberguvenlik.gov.tr/yasal-uyarilar

### Copyright Holder

All intellectual property rights for the content published on siberguvenlik.gov.tr belong to the **Directorate of Cyber Security** (Siber Güvenlik Dairesi Başkanlığı), operating under the Turkish Ministry of Transport and Infrastructure.

## Legal Warnings Summary

The following restrictions apply to all content published by TC SGB:

### Prohibited Activities

| Activity | Status | Legal Basis |
|----------|--------|-------------|
| Reproduction of content | **PROHIBITED** without written permission | Copyright Law 5846 |
| Modification of content | **PROHIBITED** without source attribution | Copyright Law 5846 |
| Republishing content | **PROHIBITED** without written permission | Copyright Law 5846 |
| Distribution of content | **PROHIBITED** without written permission | Copyright Law 5846 |
| Use on other websites | **PROHIBITED** without written permission | Copyright Law 5846 |
| Reverse engineering programs | **PROHIBITED** | Copyright Law 5846 |
| Commercial use without permission | **PROHIBITED** | Copyright Law 5846 |

### Permitted Activities

| Activity | Status | Conditions |
|----------|--------|------------|
| Accessing the API | **PERMITTED** | Public endpoint, no auth required |
| Integrating with security systems | **PERMITTED** | As explicitly stated in API description |
| Local processing for security purposes | **PERMITTED** | Integration with firewalls, SIEM, etc. |
| Using the TXT feed (url-list.txt) | **PERMITTED** | Still published alongside API |

## API-Specific License Terms

### Explicit Integration Permission

The TC SGB API documentation explicitly states that the API is designed for integration with security systems:

> "otomatik olarak erişilerek güvenlik duvarı, SIEM, url filtreleme ve DNS gibi uygulama/sistemlerin entegre edilebilmesi"

**Translation**: "to be automatically accessed and integrated with applications/systems such as firewalls, SIEM, URL filtering, and DNS"

This implies:

1. **Automated access is intended** — The API is designed for programmatic consumption
2. **Security system integration is intended** — Firewalls, SIEM, URL filtering, DNS are explicitly named
3. **The data is meant to be used** — Not just viewed, but integrated into security infrastructure

### Deprecated Endpoints

| Endpoint | Status | Date | Notes |
|----------|--------|------|-------|
| `url-list.xml` | Deprecated | Feb 2024 | Replaced by REST API |
| `url-list.txt` | Active | Ongoing | Still published |
| REST API | Active | Current | Primary interface |

## Project License Analysis

### The Code Itself

| Component | License | Notes |
|-----------|---------|-------|
| TC-SGB-API-to-List source code | MIT License | Freely distributable |
| Python dependencies | Various | Permissive licenses (MIT, BSD, Apache) |
| Documentation | CC-BY-4.0 | Attribution required |

### The Data

| Component | License | Redistribution |
|-----------|---------|----------------|
| IOC data from API | TC SGB Terms | **RESTRICTED** |
| Processed/derived data | TC SGB Terms | **RESTRICTED** |
| Aggregated statistics | Gray area | **CAUTION** |
| Raw API responses | TC SGB Terms | **RESTRICTED** |

## Redistribution Recommendations

### What You CAN Do

```
+=====================================================================+
|  PERMITTED USES                                                     |
+=====================================================================+

  1. Run the pipeline locally
     - Fetch data from TC SGB API
     - Process and normalize IOCs
     - Use for your own security infrastructure

  2. Integrate with security systems
     - Feed IOCs into firewalls
     - Import into SIEM platforms
     - Configure URL filtering
     - Update DNS sinkholes

  3. Use the open-source code
     - Clone the repository
     - Modify for your own use
     - Deploy in your environment

  4. Process data locally
     - Validate and normalize
     - Deduplicate
     - Generate private reports
```

### What You CANNOT Do

```
+=====================================================================+
|  PROHIBITED USES                                                    |
+=====================================================================+

  1. Do NOT republish raw data on GitHub
     - No output/*.json commits
     - No IOC value listings in README
     - No bulk data dumps in issues/PRs

  2. Do NOT create a public data mirror
     - No alternative distribution sites
     - No public API re-serves
     - No public databases of IOCs

  3. Do NOT redistribute without permission
     - No sharing IOC lists directly
     - No selling access to processed data
     - No sublicensing the data

  4. Do NOT modify and claim as original
     - Must attribute source if republishing
     - Cannot remove attribution
     - Cannot misrepresent origin
```

## Practical Guidelines

### For Individual Users

```yaml
recommended:
  - Clone the repo
  - Run pipeline locally
  - Feed IOCs to your firewall/SIEM
  - Keep outputs private
  - Do not share raw IOC data publicly

allowed:
  - Sharing the code (MIT license)
  - Sharing your configuration
  - Sharing generic usage instructions
  - Publishing aggregate statistics (with attribution)
```

### For Organizations

```yaml
recommended:
  - Deploy on internal infrastructure
  - Process data for internal security
  - Integrate with existing security stack
  - Maintain audit trail of usage
  - Consult legal for redistribution questions

allowed:
  - Internal IOC databases
  - Integration with commercial security tools
  - Use in security operations center (SOC)
  - Automated threat response workflows
```

### For Open Source Projects

```yaml
recommended:
  - Link to the TC SGB API (not re-serve data)
  - Provide configuration for users to fetch themselves
  - Do not include IOC data in releases
  - Document the API terms in your README

allowed:
  - The code itself (MIT license)
  - Documentation about the API
  - Configuration files
  - Scripts that fetch from the API
```

## Legal Risk Assessment

### Low Risk Activities

- Running the pipeline for personal/internal use
- Feeding IOCs to your own security infrastructure
- Contributing code improvements to the project
- Sharing configuration and setup instructions

### Medium Risk Activities

- Publishing aggregate statistics (with proper attribution)
- Creating derivative tools that use the API
- Sharing processed IOCs with partners (check ToS)

### High Risk Activities

- Publicly redistributing IOC data
- Creating a public mirror of the data
- Selling access to processed data
- Removing attribution from data

## Compliance Recommendations

1. **Always attribute the source** — When sharing any derived work, credit TC SGB
2. **Keep data processing local** — Don't upload IOC data to public services
3. **Consult legal counsel** — For commercial or large-scale use cases
4. **Document your usage** — Maintain records of how data is consumed
5. **Respect rate limits** — Even though not documented, be a good citizen
6. **Monitor ToS changes** — Check siberguvenlik.gov.tr/yasal-uyarilar periodically

## Alternative Data Sources

If the TC SGB license is too restrictive for your use case, consider these alternative IOC sources with more permissive licenses:

| Source | License | Data Types | Notes |
|--------|---------|------------|-------|
| AlienVault OTX | Apache 2.0 | IOCs, pulses | Open community |
| Abuse.ch | CC0 | IOCs, malware | Public domain |
| PhishTank | Custom (free) | Phishing URLs | Registration required |
| CISA KEV | Public domain | Known exploits | US government |
| Spamhaus | Custom (free) | Blocklists | Non-commercial |
| URLhaus | CC0 | Malware URLs | abuse.ch project |
| MISP Galaxy | CC BY-SA | Threat intel | Open community |

## Summary

The TC SGB API is designed for integration with security systems. You can freely:

1. **Fetch and process data locally** for security purposes
2. **Integrate with your security infrastructure** (firewall, SIEM, etc.)
3. **Use the open-source code** (MIT licensed)

You must NOT:

1. **Republish raw IOC data publicly** (GitHub, websites, databases)
2. **Redistribute data commercially** without written permission
3. **Remove attribution** from any derived works

**Recommendation**: Use the API as intended — as an integration endpoint for security systems — and keep all data processing local to your environment.

---

<a id="-türkçe"></a>

# Lisans ve Yeniden Dağıtım Analizi

## Genel Bakış

Bu belge, TC-SGB-API-to-List projesini yöneten yasal ve lisans kısıtlamalarını analiz etmektedir; özellikle Türkiye Siber Güvenlik Başkanlığı (T.C. Siber Güvenlik Başkanlığı) API'sinden elde edilen verilerin kullanımını ve yeniden dağıtımını kapsamaktadır.

## Hukuki Çerçeve

### Hakim Kanun

TC SGB tarafından yayınlanan içerik şu kanunlara tabidir:

- **5846 Sayılı Fikir ve Sanat Eserleri Kanunu**
- https://siberguvenlik.gov.tr/yasal-uyarilar adresinde yayınlanan **Kullanım Koşulları**

### Telif Hakkı Sahibi

siberguvenlik.gov.tr adresinde yayınlanan içerik üzerindeki tüm fikri mülkiyet hakları, Ulaştırma ve Altyapı Bakanlığı bünyesinde faaliyet gösteren **Siber Güvenlik Dairesi Başkanlığı**na aittir.

## Yasal Uyarılar Özeti

TC SGB tarafından yayınlanan tüm içerik aşağıdaki kısıtlamalara tabidir:

### Yasaklanan Faaliyetler

| Faaliyet | Durum | Hukuki Dayanak |
|----------|-------|----------------|
| İçeriğin çoğaltılması | Yazılı izin olmadan **YASAKTIR** | Fikir ve Sanat Eserleri Kanunu 5846 |
| İçeriğin değiştirilmesi | Kaynak atıfı olmadan **YASAKTIR** | Fikir ve Sanat Eserleri Kanunu 5846 |
| İçeriğin yeniden yayınlanması | Yazılı izin olmadan **YASAKTIR** | Fikir ve Sanat Eserleri Kanunu 5846 |
| İçeriğin dağıtılması | Yazılı izin olmadan **YASAKTIR** | Fikir ve Sanat Eserleri Kanunu 5846 |
| Diğer web sitelerinde kullanılması | Yazılı izin olmadan **YASAKTIR** | Fikir ve Sanat Eserleri Kanunu 5846 |
| Programların tersine mühendisliği | **YASAKTIR** | Fikir ve Sanat Eserleri Kanunu 5846 |
| İzinsiz ticari kullanım | **YASAKTIR** | Fikir ve Sanat Eserleri Kanunu 5846 |

### İzin Verilen Faaliyetler

| Faaliyet | Durum | Koşullar |
|----------|-------|----------|
| API'ye erişim | **İZİN VERİLMİŞTİR** | Herkese açık uç nokta, kimlik doğrulama gerekmez |
| Güvenlik sistemleriyle entegrasyon | **İZİN VERİLMİŞTİR** | API açıklamasında açıkça belirtildiği şekilde |
| Güvenlik amaçlı yerel işleme | **İZİN VERİLMİŞTİR** | Güvenlik duvarları, SIEM vb. ile entegrasyon |
| TXT beslemesinin (url-list.txt) kullanılması | **İZİN VERİLMİŞTİR** | API ile birlikte hâlâ yayınlanmaktadır |

## API'ye Özel Lisans Koşulları

### Açık Entegrasyon İzni

TC SGB API dokümantasyonu, API'nin güvenlik sistemleriyle entegrasyon için tasarlandığını açıkça belirtmektedir:

> "otomatik olarak erişilerek güvenlik duvarı, SIEM, url filtreleme ve DNS gibi uygulama/sistemlerin entegre edilebilmesi"

**Çeviri**: "otomatik olarak erişilerek güvenlik duvarı, SIEM, URL filtreleme ve DNS gibi uygulama/sistemlerle entegre edilebilmesi"

Bu şunları ima etmektedir:

1. **Otomatik erişim amaçlanmıştır** — API programlı tüketim için tasarlanmıştır
2. **Güvenlik sistemi entegrasyonu amaçlanmıştır** — Güvenlik duvarları, SIEM, URL filtreleme, DNS açıkça adlandırılmıştır
3. **Verilerin kullanılması amaçlanmıştır** — Yalnızca görüntülenmek değil, güvenlik altyapısına entegre edilmek

### Kullanımdan Kaldırılmış Uç Noktalar

| Uç Nokta | Durum | Tarih | Notlar |
|----------|-------|-------|--------|
| `url-list.xml` | Kullanımdan kaldırıldı | Şubat 2024 | REST API ile değiştirildi |
| `url-list.txt` | Aktif | Devam ediyor | Hâlâ yayınlanıyor |
| REST API | Aktif | Güncel | Birincil arayüz |

## Proje Lisans Analizi

### Kodun Kendisi

| Bileşen | Lisans | Notlar |
|---------|--------|-------|
| TC-SGB-API-to-List kaynak kodu | MIT Lisansı | Serbestçe dağıtılabilir |
| Python bağımlılıkları | Çeşitli | İzin verici lisanslar (MIT, BSD, Apache) |
| Dokümantasyon | CC-BY-4.0 | Atıf gerekli |

### Veri

| Bileşen | Lisans | Yeniden Dağıtım |
|---------|--------|-----------------|
| API'den gelen IOC verisi | TC SGB Koşulları | **KISITLI** |
| İşlenmiş/türetilmiş veri | TC SGB Koşulları | **KISITLI** |
| Toplu istatistikler | Gri alan | **DİKKAT** |
| Ham API yanıtları | TC SGB Koşulları | **KISITLI** |

## Yeniden Dağıtım Önerileri

### Yapabilecekleriniz

```
+=====================================================================+
|  İZİN VERİLEN KULLANIMLAR                                          |
+=====================================================================+

  1. Hattı yerel olarak çalıştırın
     - TC SGB API'sinden veri çekme
     - IOC'leri işleme ve normalleştirme
     - Kendi güvenlik altyapınız için kullanma

  2. Güvenlik sistemleriyle entegre etme
     - IOC'leri güvenlik duvarlarına besleme
     - SIEM platformlarına aktarma
     - URL filtreleme yapılandırma
     - DNS sinkhole'larını güncelleme

  3. Açık kaynak kodu kullanma
     - Depoyu çoğaltma
     - Kendi kullanımınıza göre değiştirme
     - Ortamınızda dağıtma

  4. Verileri yerel olarak işleme
     - Doğrulama ve normalleştirme
     - Tekilleştirme
     - Özel raporlar üretme
```

### Yapamayacaklarınız

```
+=====================================================================+
|  YASAKLANAN KULLANIMLAR                                             |
+=====================================================================+

  1. Ham veriyi GitHub'da yeniden yayınlamayın
     - output/*.json提交 yok
     - README'de IOC değer listeleri yok
     - Sorun taleplerinde/çekme isteklerinde toplu veri dökümleri yok

  2. Herkese açık veri aynası oluşturmayın
     - Alternatif dağıtım siteleri yok
     - Herkese açık API yeniden sunumları yok
     - Herkese açık IOC veritabanları yok

  3. İzinsiz yeniden dağıtım yapmayın
     - IOC listelerini doğrudan paylaşmayın
     - İşlenmiş verilere erişimi satmayın
     - Verileri alt lisanslamayın

  4. Değiştirip orijinal olarak iddia etmeyin
     - Yeniden yayınlıyorsanız kaynağı belirtmeniz gerekir
     - Atıfı kaldıramazsınız
     - Kökeni yanlış gösteremezsiniz
```

## Pratik Yönergeler

### Bireysel Kullanıcılar İçin

```yaml
önerilen:
  - Depoyu çoğaltma
  - Hattı yerel olarak çalıştırma
  - IOC'leri güvenlik duvarınıza/SIEM'inize besleme
  - Çıktıları gizli tutma
  - Ham IOC verilerini herkese açık paylaşmama

izin_verilen:
  - Kodu paylaşma (MIT lisansı)
  - Yapılandırmanızı paylaşma
  - Genel kullanım talimatlarını paylaşma
  - Toplu istatistikleri yayınlama (atıfla)
```

### Kuruluşlar İçin

```yaml
önerilen:
  - İç altyapıda dağıtma
  - İç güvenlik için veri işleme
  - Mevcut güvenlik yığınıyla entegrasyon
  - Kullanım denetim izini koruma
  - Yeniden dağıtım soruları için hukuki danışmanlık alma

izin_verilen:
  - İç IOC veritabanları
  - Ticari güvenlik araçlarıyla entegrasyon
  - Güvenlik operasyonları merkezinde (SOC) kullanım
  - Otomatik tehdit yanıt iş akışları
```

### Açık Kaynak Projeler İçin

```yaml
önerilen:
  - TC SGB API'sine bağlantı verme (veriyi yeniden sunmama)
  - Kullanıcıların kendilerinin çekmesi için yapılandırma sağlama
  - Sürümlere IOC verisi dahil etmeme
  - README'de API koşullarını belgeleme

izin_verilen:
  - Kodun kendisi (MIT lisansı)
  - API hakkında dokümantasyon
  - Yapılandırma dosyaları
  - API'den çekme betikleri
```

## Hukuki Risk Değerlendirmesi

### Düşük Riskli Faaliyetler

- Kişisel/iç kullanım için hattı çalıştırma
- IOC'leri kendi güvenlik altyapınıza besleme
- Projeye kod iyileştirmelerine katkıda bulunma
- Yapılandırma ve kurulum talimatlarını paylaşma

### Orta Riskli Faaliyetler

- Toplu istatistikleri yayınlama (uygun atıfla)
- API'yi kullanan türetilmiş araçlar oluşturma
- İşlenmiş IOC'leri ortaklarla paylaşma (Kullanım Koşullarını kontrol edin)

### Yüksek Riskli Faaliyetler

- IOC verilerini herkese açık olarak yeniden dağıtma
- Verilerin herkese açık bir aynasını oluşturma
- İşlenmiş verilere erişimi satma
- Verilerden atıfı kaldırma

## Uyumluluk Önerileri

1. **Her zaman kaynağı atfedin** — Herhangi bir türetilmiş eseri paylaşırken TC SGB'ye kredi verin
2. **Veri işlemenizi yerel tutun** — IOC verilerini herkese açık hizmetlere yüklemeyin
3. **Hukuki danışmanlık alın** — Ticari veya büyük ölçekli kullanım durumları için
4. **Kullanımınızı belgeleyin** — Verilerin nasıl tüketildiğine ilişkin kayıtlar tutun
5. **Hız sınırlarına saygı gösterin** — Belgelenmemiş olsa bile iyi bir vatandaş olun
6. **Kullanım Koşulları değişikliklerini izleyin** — siberguvenlik.gov.tr/yasal-uyarilar adresini düzenli olarak kontrol edin

## Alternatif Veri Kaynakları

TC SGB lisansı kullanım durumunuz için çok kısıtlayıcıysa, daha izin verici lisanslara sahip bu alternatif IOC kaynaklarını değerlendirin:

| Kaynak | Lisans | Veri Türleri | Notlar |
|--------|--------|-------------|-------|
| AlienVault OTX | Apache 2.0 | IOC'ler, nabızlar | Açık topluluk |
| Abuse.ch | CC0 | IOC'ler, kötü amaçlı yazılım | Kamu malı |
| PhishTank | Özel (ücretsiz) | Oltalama URL'leri | Kayıt gerekli |
| CISA KEV | Kamu malı | Bilinen açıklar | ABD hükümeti |
| Spamhaus | Özel (ücretsiz) | Engelleme listeleri | Ticari olmayan |
| URLhaus | CC0 | Kötü amaçlı yazılım URL'leri | abuse.ch projesi |
| MISP Galaxy | CC BY-SA | Tehdit istihbaratı | Açık topluluk |

## Özet

TC SGB API'si güvenlik sistemleriyle entegrasyon için tasarlanmıştır. Şunları serbestçe yapabilirsiniz:

1. **Güvenlik amaçlı verileri yerel olarak çekme ve işleme**
2. **Güvenlik altyapınızla entegrasyon** (güvenlik duvarı, SIEM vb.)
3. **Açık kaynak kodu kullanma** (MIT lisanslı)

Şunları yapmamalısınız:

1. **Ham IOC verilerini herkese açık olarak yeniden yayınlama** (GitHub, web siteleri, veritabanları)
2. **Yazılı izin olmadan verileri ticari olarak dağıtma**
3. **Türetilmiş eserlerden atfı kaldırma**

**Öneri**: API'yi amaçlandığı şekilde kullanın — güvenlik sistemleri için bir entegrasyon uç noktası olarak — ve tüm veri işlemenizi ortamınızda yerel tutun.
