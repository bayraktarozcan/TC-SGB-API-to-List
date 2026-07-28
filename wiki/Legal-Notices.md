> **Language / Dil** &nbsp;
> [EN English](#-english) &nbsp;·&nbsp; [TR Türkçe](#-türkçe)

<a id="-english"></a>

# Legal Notices

## Turkish National Cyber Security Directorate — Legal Warnings

**Source**: https://siberguvenlik.gov.tr/yasal-uyarilar
**Original Language**: Turkish
**Translated**: English (for reference only — consult the original for authoritative text)

---

## Original Legal Warnings (Yasal Uyarılar)

### Copyright Notice

> **T.C. Ulaştırma ve Altyapı Bakanlığı Siber Güvenlik Dairesi Başkanlığı**
>
> All intellectual property rights, including but not limited to copyright, related to the content, design, and all materials published on the website https://siberguvenlik.gov.tr belong exclusively to the Directorate of Cyber Security (Siber Güvenlik Dairesi Başkanlığı) of the Republic of Türkiye Ministry of Transport and Infrastructure.

### Content Protection

> The content published on this website is protected under the **Turkish Law No. 5846 on Intellectual and Artistic Works** (Fikir ve Sanat Eserleri Kanunu). All rights reserved.

### Prohibited Activities

> **Without obtaining prior written permission** from the Directorate of Cyber Security, the following activities are **strictly prohibited**:
>
> 1. **Reproduction** of any content published on this website in any form or by any means (printing, photocopying, digital copying, etc.)
>
> 2. **Modification** of any content, including but not limited to changing, adding to, or removing from the original content, without proper source attribution
>
> 3. **Republishing** or **redistribution** of content on other websites, platforms, or media
>
> 4. **Commercial use** of content without explicit written authorization
>
> 5. **Reverse engineering** of any programs, software, or systems used on or provided through this website
>
> 6. **Use of content on other websites** without prior written permission from the Directorate

### Website Content Usage

> The content of this website cannot be used on other websites without permission. This includes, but is not limited to:
>
> - Text content
> - Images and graphics
> - Logos and trademarks
> - Software and code
> - Databases and data structures
> - Design elements and layout

### Intellectual Property

> All intellectual property rights related to the content and services provided through this website are reserved by the Directorate of Cyber Security. These rights are protected under applicable Turkish and international laws and treaties.

---

## API-Specific Terms

### API Purpose and Integration

The TC SGB Threat Intelligence API is specifically designed and provided for the purpose of integration with security systems. The API description states:

> **Original (Turkish)**: "otomatik olarak erişilerek güvenlik duvarı, SIEM, url filtreleme ve DNS gibi uygulama/sistemlerin entegre edilebilmesi"
>
> **English Translation**: "to be automatically accessed and integrated with applications/systems such as firewalls, SIEM, URL filtering, and DNS"

This implies:

1. **Automated programmatic access is intended** — The API is designed for machine-to-machine communication
2. **Security system integration is the primary purpose** — Firewalls, SIEM, URL filtering, and DNS are explicitly named as target systems
3. **The data is meant to be consumed programmatically** — Not just viewed in a browser, but integrated into security infrastructure

### Data Feeds

| Feed | Status | Terms |
|------|--------|-------|
| REST API | Active | Per API terms above |
| url-list.txt | Active | Publicly published |
| url-list.xml | Deprecated (Feb 2024) | No longer available |

---

## Compliance Analysis for This Project

### What This Project Does

The TC-SGB-API-to-List project:

1. **Fetches IOC data** from the TC SGB public API using automated means
2. **Processes and normalizes** the data locally (validation, normalization, deduplication)
3. **Generates output files** in multiple formats for local use
4. **Does NOT redistribute** raw IOC data publicly

### Compliance Assessment

| Activity | Assessment | Notes |
|----------|------------|-------|
| Fetching from API | ✅ PERMITTED | API is public, designed for automated access |
| Local processing | ✅ PERMITTED | No redistribution involved |
| Integration with security systems | ✅ PERMITTED | Explicitly stated purpose in API docs |
| Generating local reports | ✅ PERMITTED | For internal use only |
| Publishing code | ✅ PERMITTED | Code is MIT licensed, not TC SGB content |
| Redistributing IOC data | ❌ PROHIBITED | Cannot republish without written permission |
| Hosting IOC data publicly | ❌ PROHIBITED | GitHub repos, websites, databases |
| Commercial redistribution | ❌ PROHIBITED | No commercial use without permission |

### Recommendations

#### For Users of This Project

1. **Run locally**: Execute the pipeline on your own infrastructure
2. **Feed to security systems**: Use outputs with your firewall, SIEM, URL filtering, DNS
3. **Keep data private**: Do not share raw IOC data publicly
4. **Do not host publicly**: Do not create public mirrors or databases of IOC data
5. **Consult legal counsel**: For commercial or large-scale use cases

#### For Contributors

1. **Code contributions**: Welcome and encouraged (MIT license)
2. **No IOC data in PRs**: Do not include IOC data in pull requests or issues
3. **Documentation**: May reference the API but not reproduce its content
4. **Examples**: Use fictional examples, not real IOC data

#### For Organizations

1. **Internal use**: Deploy and use freely within your organization
2. **Security integration**: Feed IOCs into your security stack
3. **No external sharing**: Do not share IOC data with external parties without permission
4. **Audit trail**: Maintain records of data processing for compliance
5. **Legal review**: Consult legal for specific use cases

---

## Alternative Data Sources (More Permissive)

If the TC SGB license restrictions are too limiting for your use case, consider these alternative IOC sources:

| Source | License | Redistribution | Notes |
|--------|---------|----------------|-------|
| AlienVault OTX | Apache 2.0 | ✅ Yes | Open community, permissive |
| abuse.ch (URLhaus, MalwareBazaar) | CC0 | ✅ Yes | Public domain |
| CISA KEV | Public Domain | ✅ Yes | US Government data |
| PhishTank | CC BY | ✅ With attribution | Registration required |
| Spamhaus DROP | Non-commercial free | ⚠️ Non-commercial | Free for non-commercial |
| Emerging Threats Open | Open | ✅ Yes | Community ruleset |
| MISP Galaxy | CC BY-SA | ✅ With attribution | Open community |
| OpenPhish | Proprietary | ❌ No | Commercial license |

---

## Disclaimer

> **DISCLAIMER**: This document provides a summary of the legal warnings published by the Turkish National Cyber Security Directorate for reference purposes only. It does not constitute legal advice. The original Turkish text at https://siberguvenlik.gov.tr/yasal-uyarilar is the authoritative source. For legal questions regarding the use of TC SGB data, consult qualified legal counsel familiar with Turkish intellectual property law.

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | 2025-01-20 | Initial legal notices document |
| 1.1 | 2025-01-20 | Added API-specific terms and compliance analysis |

---

## Contact

For questions about the legal terms of the TC SGB API:

- **Website**: https://siberguvenlik.gov.tr
- **Legal Warnings**: https://siberguvenlik.gov.tr/yasal-uyarilar
- **API Documentation**: https://siberguvenlik.gov.tr

For questions about the TC-SGB-API-to-List project:

- **GitHub Issues**: https://github.com/bayraktarozcan/TC-SGB-API-to-List/issues
- **Email**: [project email]

<a id="-türkçe"></a>

# Yasal Bildirimler

## Türkiye Ulusal Siber Güvenlik Müdürlüğü — Yasal Uyarılar

**Kaynak**: https://siberguvenlik.gov.tr/yasal-uyarilar
**Orijinal Dil**: Türkçe
**Çeviri**: İngilizce (yalnızca referans amaçlı — yetkili metin için orijinaline başvurunuz)

---

## Orijinal Yasal Uyarılar (Yasal Uyarılar)

### Telif Hakkı Bildirimi

> **T.C. Ulaştırma ve Altyapı Bakanlığı Siber Güvenlik Dairesi Başkanlığı**
>
> https://siberguvenlik.gov.tr adresinde yayımlanan içerik, tasarım ve tüm materyallerle ilgili telif hakkı da dahil olmak üzere tüm fikri mülkiyet hakları münhasıran Türkiye Cumhuriyeti Ulaştırma ve Altyapı Bakanlığı Siber Güvenlik Dairesi Başkanlığı'na aittir.

### İçerik Koruması

> Bu web sitesinde yayımlanan içerik, **Fikir ve Sanat Eserleri Kanunu** (5846 sayılı Kanun) kapsamında korunmaktadır. Tüm hakları saklıdır.

### Yasak Faaliyetler

> Siber Güvenlik Dairesi Başkanlığı'ndan **önceden yazılı izin almadan** aşağıdaki faaliyetler **kesinlikle yasaktır**:
>
> 1. Bu web sitesinde yayımlanan herhangi bir içeriğin herhangi bir biçimde veya yolla çoğaltılması (basım, fotokopi, dijital kopyalama vb.)
>
> 2. Kaynak gösterilmeksizin orijinal içerikte değişiklik, ekleme veya çıkarma da dahil olmak üzere herhangi bir içeriğin değiştirilmesi
>
> 3. İçeriğin diğer web sitelerinde, platformlarda veya medyada **yeniden yayımlanması** veya **yeniden dağıtılması**
>
> 4. Açıkça yazılı izin olmaksızın içeriğin **ticari amaçla kullanılması**
>
> 5. Bu web sitesinde kullanılan veya sağlanan herhangi bir programın, yazılımın veya sistemin **ters mühendisliği**
>
> 6. Dairenin önceden yazılı izni olmaksızın içeriğin **diğer web sitelerinde kullanılması**

### Web Sitesi İçerik Kullanımı

> Bu web sitesinin içeriği izin alınmadan diğer web sitelerinde kullanılamaz. Bu, aşağıdakilerle sınırlı değildir:
>
> - Metin içeriği
> - Görseller ve grafikler
> - Logolar ve ticari markalar
> - Yazılım ve kod
> - Veritabanları ve veri yapıları
> - Tasarım öğeleri ve yerleşim

### Fikri Mülkiyet

> Bu web sitesi aracılığıyla sağlanan içerik ve hizmetlerle ilgili tüm fikri mülkiyet hakları Siber Güvenlik Dairesi Başkanlığı tarafından saklıdır. Bu haklar, yürürlükteki Türk ve uluslararası yasalar ve anlaşmalar kapsamında korunmaktadır.

---

## API'ye Özel Şartlar

### API Amacı ve Entegrasyonu

TC SGB Tehdit İstihbaratı API'si, güvenlik sistemleriyle entegrasyon amacıyla özel olarak tasarlanmış ve sağlanmıştır. API açıklaması şunu belirtmektedir:

> **Orijinal (Türkçe)**: "otomatik olarak erişilerek güvenlik duvarı, SIEM, url filtreleme ve DNS gibi uygulama/sistemlerin entegre edilebilmesi"
>
> **İngilizce Çeviri**: "to be automatically accessed and integrated with applications/systems such as firewalls, SIEM, URL filtering, and DNS"

Bu şunları ifade etmektedir:

1. **Otomatik programlı erişim öngörülmektedir** — API makine-makine iletişimi için tasarlanmıştır
2. **Güvenlik sistemi entegrasyonu temel amaçtır** — Güvenlik duvarları, SIEM, URL filtreleme ve DNS açıkça hedef sistemler olarak belirtilmiştir
3. **Veriler programlı olarak tüketilmek içindir** — Yalnızca tarayıcıda görüntülenmek için değil, güvenlik altyapısına entegre edilmek içindir

### Veri Beslemeleri

| Besleme | Durum | Şartlar |
|---------|-------|---------|
| REST API | Aktif | Yukarıdaki API şartlarına göre |
| url-list.txt | Aktif | Kamuya yayımlanmış |
| url-list.xml | Kullanımdan kaldırıldı (Şubat 2024) | Artık mevcut değil |

---

## Bu Proje İçin Uyumluluk Analizi

### Bu Projenin Yaptığı

TC-SGB-API-to-List projesi:

1. TC SGB kamu API'sinden otomatik yollarla **IOC verisi çeker**
2. Verileri yerel olarak **işler ve normalleştirir** (doğrulama, normalleştirme, tekilleştirme)
3. Yerel kullanım için çoklu biçimlerde **çıktı dosyaları üretir**
4. Ham IOC verisini kamuya **yeniden dağıtmaz**

### Uyumluluk Değerlendirmesi

| Faaliyet | Değerlendirme | Notlar |
|----------|---------------|--------|
| API'den çekme | ✅ İZİN VERİLMİŞ | API kamuya açıktır, otomatik erişim için tasarlanmıştır |
| Yerel işleme | ✅ İZİN VERİLMİŞ | Yeniden dağıtım içermez |
| Güvenlik sistemleriyle entegrasyon | ✅ İZİN VERİLMİŞ | API dokümantasyonunda açıkça belirtilmiştir |
| Yerel rapor oluşturma | ✅ İZİN VERİLMİŞ | Yalnızca dahili kullanım içindir |
| Kod yayımlama | ✅ İZİN VERİLMİŞ | Kod MIT lisanslıdır, TC SGB içeriği değildir |
| IOC verisinin yeniden dağıtımı | ❌ YASAKTIR | Yazılı izin olmadan yeniden yayımlanamaz |
| IOC verisinin kamuya barındırılması | ❌ YASAKTIR | GitHub depoları, web siteleri, veritabanları |
| Ticari yeniden dağıtım | ❌ YASAKTIR | İzinsiz ticari kullanım yasaktır |

### Öneriler

#### Bu Projenin Kullanıcıları İçin

1. **Yerel olarak çalıştırın**: Hattı kendi altyapınızda çalıştırın
2. **Güvenlik sistemlerine besleyin**: Çıktıları güvenlik duvarınız, SIEM, URL filtreleme, DNS ile kullanın
3. **Verileri gizli tutun**: Ham IOC verisini kamuya paylaşmayın
4. **Kamuya barındırmayın**: IOC verisinin kamuya açık aynalarını veya veritabanlarını oluşturmayın
5. **Hukuki danışmana başvurun**: Ticari veya büyük ölçekli kullanım durumları için

#### Katkıda Bulunanlar İçin

1. **Katkılar**: Hoş geldiniz ve teşvik edilmektedir (MIT lisansı)
2. **PR'larda IOC verisi olmasın**: Pull request'lere veya sorunlara IOC verisi eklemeyin
3. **Dokümantasyon**: API'ye referans verilebilir ancak içeriği çoğaltılamaz
4. **Örnekler**: Gerçek IOC verisi değil, kurgusal örnekler kullanın

#### Kuruluşlar İçin

1. **Dahili kullanım**: Kuruluşunuz içinde özgürce dağıtın ve kullanın
2. **Güvenlik entegrasyonu**: IOC'leri güvenlik yığınınıza besleyin
3. **Harici Paylaşım Yasak**: İzinsiz IOC verisini harici taraflarla paylaşmayın
4. **Denetim izi**: Uyumluluk için veri işleme kayıtlarını tutun
5. **Hukuki inceleme**: Belirli kullanım durumları için hukuki danışmana başvurun

---

## Alternatif Veri Kaynakları (Daha İzni Geniş)

TC SGB lisans kısıtlamaları kullanım senaryonuz için çok kısıtlayıcıysa, şu alternatif IOC kaynaklarını değerlendirin:

| Kaynak | Lisans | Yeniden Dağıtım | Notlar |
|--------|--------|-----------------|--------|
| AlienVault OTX | Apache 2.0 | ✅ Evet | Açık topluluk, geniş izin |
| abuse.ch (URLhaus, MalwareBazaar) | CC0 | ✅ Evet | Kamu malı |
| CISA KEV | Kamu Malı | ✅ Evet | ABD Hükümeti verisi |
| PhishTank | CC BY | ✅ Atıf ile | Kayıt gereklidir |
| Spamhaus DROP | Ticari olmayan ücretsiz | ⚠️ Ticari olmayan | Ticari olmayan kullanım için ücretsiz |
| Emerging Threats Open | Açık | ✅ Evet | Topluluk kural seti |
| MISP Galaxy | CC BY-SA | ✅ Atıf ile | Açık topluluk |
| OpenPhish | Telifli | ❌ Hayır | Ticari lisans |

---

## Sorumluluk Reddi

> **SORUMLULUK REDDİ**: Bu belge, yalnızca referans amaçlı olarak Türkiye Ulusal Siber Güvenlik Müdürlüğü tarafından yayımlanan yasal uyarıların bir özetini sunmaktadır. Hukuki tavsiye niteliği taşımamaktadır. https://siberguvenlik.gov.tr/yasal-uyarilar adresindeki orijinal Türkçe metin yetkili kaynaktır. TC SGB verilerinin kullanımıyla ilgili hukuki sorularınız için Türk fikri mülkiyet hukumuna hakim nitelikli hukuki danışmana başvurunuz.

---

## Sürüm Geçmişi

| Sürüm | Tarih | Değişiklikler |
|-------|-------|---------------|
| 1.0 | 2025-01-20 | İlk yasal bildirimler belgesi |
| 1.1 | 2025-01-20 | API'ye özel şartlar ve uyumluluk analizi eklendi |

---

## İletişim

TC SGB API'nin yasal şartlarıyla ilgili sorularınız için:

- **Web Sitesi**: https://siberguvenlik.gov.tr
- **Yasal Uyarılar**: https://siberguvenlik.gov.tr/yasal-uyarilar
- **API Dokümantasyonu**: https://siberguvenlik.gov.tr

TC-SGB-API-to-List projesiyle ilgili sorularınız için:

- **GitHub Sorunları**: https://github.com/bayraktarozcan/TC-SGB-API-to-List/issues
- **E-posta**: [proje e-postası]
