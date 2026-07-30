> **Language / Dil** &nbsp;
> [EN English](#-english) &nbsp;·&nbsp; [TR Türkçe](#-türkçe)

<a id="-english"></a>

# Roadmap

## Overview

This document outlines the phased development roadmap for the TC-SGB-API-to-List project, including current phase, planned features, and future data source integrations.

## Phased Roadmap

```
+=====================================================================+
|                     Development Roadmap                              |
+=====================================================================+

  Phase 1            Phase 2            Phase 3            Phase 4
  Foundation         Expansion          Ecosystem          Scale
  (v1.0 - v1.2)     (v1.3 - v1.5)     (v2.0 - v2.2)     (v3.0+)
  +-----------+      +-----------+      +-----------+      +-----------+
  |           |      |           |      |           |      |           |
  | Core      |----->| Multi-    |----->| Multi-    |----->| Enterprise|
  | Pipeline  |      | Source    |      | Platform  |      | Features  |
  |           |      |           |      |           |      |           |
  | 17 Output |      | CISA KEV  |      | REST API  |      | Dashboard |
  | Formats   |      | Spamhaus  |      | Web UI    |      | Real-time |
  |           |      | URLhaus   |      | Plugin    |      | Alerting  |
  | CLI Tool  |      | OTX       |      | System    |      | HA/DR     |
  |           |      | PhishTank |      |           |      |           |
  +-----------+      +-----------+      +-----------+      +-----------+

  Status: ACTIVE     Status: PLANNED    Status: FUTURE    Status: VISION
```

---

## Phase 1: Foundation (Current)

**Version**: v1.0 - v1.2
**Status**: Active Development
**Timeline**: Q1-Q2 2025

### Completed

- [x] Core pipeline (fetch → validate → normalize → dedup → output)
- [x] Async API client with retry logic
- [x] Pydantic v2 data models
- [x] 17 output formats (NextDNS, AdGuard, Pi-hole, dnsmasq, Unbound, RPZ, Technitium, MikroTik, nftables, ipset, Suricata, CrowdSec, CSV, JSON, YAML, SQLite)
- [x] Unit test suite (100% coverage)
- [x] CI/CD pipeline (GitHub Actions)
- [x] PyPI packaging
- [x] CLI interface

### In Progress

- [ ] Performance optimization for 500K+ records
- [ ] Memory-efficient streaming processing
- [ ] Comprehensive documentation
- [ ] Property-based testing
- [ ] Fuzz testing

### Planned (v1.1 - v1.2)

- [ ] Sigma rule output format
- [ ] YARA rule generation
- [ ] Bloom filter for faster deduplication
- [ ] Configurable quality thresholds
- [ ] HTML report templates
- [ ] PDF report generation
- [ ] Incremental fetch (local hash comparison)
- [ ] Docker container support

---

## Phase 2: Multi-Source Expansion

**Version**: v1.3 - v1.5
**Status**: Planned
**Timeline**: Q3-Q4 2025

### Data Source Integrations

#### CISA Known Exploited Vulnerabilities (KEV)

```
Source: https://www.cisa.gov/known-exploited-vulnerabilities-catalog
Format: JSON (REST API)
License: Public Domain (US Government)
Update: Daily

Data Available:
- CVE IDs
- Vendor/product names
- Vulnerability names
- Dates added/required remediation
- Short descriptions

Integration:
- Fetch KEV catalog
- Extract CVE-based IoCs
- Cross-reference with TC SGB data
- Generate CVE-focused reports
```

#### Spamhaus Blocklists

```
Source: https://www.spamhaus.org/
Format: DROP/eDROP lists (text)
License: Non-commercial use free
Update: Daily

Data Available:
- IP ranges (DROP list)
- Extended IP ranges (eDROP)
- BGP Prefixes
- ASN data

Integration:
- Fetch DROP/eDROP lists
- Parse IP ranges
- Generate firewall rules (iptables, pf, etc.)
- Cross-reference with TC SGB IPs
```

#### URLhaus (abuse.ch)

```
Source: https://urlhaus.abuse.ch/
Format: CSV, JSON, text
License: CC0 (Public Domain)
Update: Hourly

Data Available:
- Malicious URLs
- URL status (online/offline)
- Tags (malware, phishing, etc.)
- Target information
- Payload delivery details

Integration:
- Fetch URL feeds
- Filter by tag/status
- Generate URL blocklists
- Cross-reference with TC SGB URLs
```

#### AlienVault OTX

```
Source: https://otx.alienvault.com/
Format: JSON (REST API)
License: Apache 2.0
Update: Community-driven

Data Available:
- IoC pulses
- Domain/IP/URL/Hash IoCs
- Threat actor profiles
- Malware samples
- Geolocation data

Integration:
- Fetch relevant pulses
- Extract IoCs by type
- Enrich with threat context
- Cross-reference with TC SGB data
```

#### PhishTank

```
Source: https://www.phishtank.com/
Format: JSON, CSV
License: Creative Commons
Update: Hourly

Data Available:
- Phishing URLs
- Target brands
- Verification status
- Screenshot URLs
- Submission details

Integration:
- Fetch verified phishing URLs
- Filter by target brand
- Generate phishing blocklists
- Cross-reference with TC SGB URLs
```

#### Emerging Threats (ET) Open Ruleset

```
Source: https://rules.emergingthreats.net/
Format: Snort/Suricata rules
License: Open (ETPro: Commercial)
Update: Daily

Data Available:
- Network signatures
- IoC-based rules
- Protocol detection
- Malware command channels

Integration:
- Parse ET Open rules
- Extract IoC-based signatures
- Generate Suricata rules
- Cross-reference with TC SGB data
```

### Phase 2 Features

- [ ] Multi-source pipeline architecture
- [ ] Source plugin system
- [ ] Cross-source deduplication
- [ ] Threat intelligence correlation
- [ ] Source priority/weighting
- [ ] Unified data model for all sources
- [ ] Source-specific output formats

---

## Phase 3: Platform Features

**Version**: v2.0 - v2.2
**Status**: Future
**Timeline**: 2026

### REST API Server

```
+---------------------------------------------------+
|  REST API Server Architecture                     |
+---------------------------------------------------+

  +-----------+       +-----------+       +-----------+
  |           |       |           |       |           |
  |  FastAPI  |------>| Pipeline  |------>| Database  |
  |  Server   |       | Engine    |       | (SQLite)  |
  |           |       |           |       |           |
  +-----------+       +-----------+       +-----------+
        |                                       |
        v                                       v
  +-----------+       +-----------+       +-----------+
  |           |       |           |       |           |
  |  Auth     |       | Caching   |       | Output    |
  |  (API Key)|       | (Redis)   |       | Storage   |
  |           |       |           |       |           |
  +-----------+       +-----------+       +-----------+

  Endpoints:
  GET  /api/v1/iocs           - List IoCs
  GET  /api/v1/iocs/{id}      - Get single IoC
  GET  /api/v1/iocs/search    - Search IoCs
  GET  /api/v1/stats          - Dataset statistics
  POST /api/v1/refresh        - Trigger refresh
  GET  /api/v1/health         - Health check
```

### Web Dashboard

```
+---------------------------------------------------+
|  Web Dashboard                                    |
+---------------------------------------------------+

  +-----------------------------------------------+
  |  TC-SGB-API-to-List Dashboard                     |
  +-----------------------------------------------+
  |  +----------+  +----------+  +----------+     |
  |  | Total    |  | Active   |  | Quality  |     |
  |  | IoCs     |  | IoCs     |  | Score    |     |
  |  | 483,690  |  | 412,300  |  | 0.94     |     |
  |  +----------+  +----------+  +----------+     |
  |                                               |
  |  +------------------------------------------+ |
  |  |  IoC Type Distribution (Chart)           | |
  |  |  ████ 35% | ████ 25% | ████ 20% | ...  | |
  |  +------------------------------------------+ |
  |                                               |
  |  +------------------------------------------+ |
  |  |  Recent Pipeline Runs                    | |
  |  |  ✓ 2025-01-20 06:00  28s  483K records  | |
  |  |  ✓ 2025-01-19 06:00  26s  481K records  | |
  |  |  ✓ 2025-01-18 06:00  27s  479K records  | |
  |  +------------------------------------------+ |
  +-----------------------------------------------+
```

### Plugin System

```python
# Plugin architecture
class SourcePlugin:
    """Base class for data source plugins."""

    def fetch(self) -> AsyncGenerator[IOCRecord, None]:
        """Fetch IoCs from the source."""
        ...

    def validate(self, record: IOCRecord) -> bool:
        """Validate record from this source."""
        ...

    def get_metadata(self) -> SourceMetadata:
        """Get source metadata."""
        ...


# Example plugins
class TCSGBPlugin(SourcePlugin):
    """TC SGB API plugin."""

    ...


class CISAKeVPlugin(SourcePlugin):
    """CISA KEV catalog plugin."""

    ...


class URLhausPlugin(SourcePlugin):
    """URLhaus feed plugin."""

    ...
```

### Phase 3 Features

- [ ] FastAPI REST server
- [ ] SQLite/PostgreSQL storage
- [ ] Redis caching layer
- [ ] Web dashboard (React/Vue)
- [ ] Plugin architecture
- [ ] API authentication (API keys)
- [ ] Rate limiting per client
- [ ] WebSocket for real-time updates
- [ ] Export to STIX/TAXII server
- [ ] Webhook notifications

---

## Phase 4: Enterprise Features

**Version**: v3.0+
**Status**: Vision
**Timeline**: 2027+

### Features

- [ ] High availability (HA) deployment
- [ ] Disaster recovery (DR) procedures
- [ ] Multi-tenant support
- [ ] Role-based access control (RBAC)
- [ ] Audit logging and compliance
- [ ] Real-time alerting (email, Slack, PagerDuty)
- [ ] Integration with SOAR platforms
- [ ] Threat intelligence sharing (TAXII 2.1)
- [ ] Machine learning anomaly detection
- [ ] Automated threat response
- [ ] Custom correlation rules
- [ ] Geographic threat mapping
- [ ] Executive reporting dashboards
- [ ] SSO/SAML authentication
- [ ] On-premise deployment option

---

## Data Source Roadmap

```
+=====================================================================+
|  Data Source Integration Timeline                                    |
+=====================================================================+

  2025 Q1    2025 Q2    2025 Q3    2025 Q4    2026 Q1    2026 Q2
  +--------+ +--------+ +--------+ +--------+ +--------+ +--------+
  |        | |        | |        | |        | |        | |        |
  | TC SGB | | TC SGB | | CISA   | | URLhaus| | OTX    | | ET Open|
  | (Done) | | v1.2   | | KEV    | |        | |        | |        |
  |        | |        | |        | |        | |        | |        |
  |        | |        | | Spamhaus| | Phish- | | MISP   | | Custom |
  |        | |        | |        | | Tank   | | Galaxy | | Feeds  |
  |        | |        | |        | |        | |        | |        |
  +--------+ +--------+ +--------+ +--------+ +--------+ +--------+

  Priority: HIGH     HIGH      HIGH      MEDIUM    MEDIUM    LOW
```

### Source Evaluation Criteria

| Criterion | Weight | Description |
|-----------|--------|-------------|
| Data Quality | 25% | Accuracy, completeness, freshness |
| License | 20% | Permissiveness for integration |
| Reliability | 20% | Uptime, consistency, maintenance |
| Update Frequency | 15% | How often data is refreshed |
| Data Volume | 10% | Amount of data available |
| Integration Effort | 10% | Technical complexity |

---

## Technology Evolution

| Component | Current | Planned | Future |
|-----------|---------|---------|--------|
| Python | 3.11+ | 3.12+ | 3.13+ |
| HTTP | httpx 0.27 | httpx 0.28+ | HTTP/3 |
| Validation | Pydantic v2 | Pydantic v2.1+ | Pydantic v3 |
| Database | None | SQLite | PostgreSQL |
| Cache | None | Redis | Redis Cluster |
| Web Framework | None | FastAPI | FastAPI + WebSocket |
| Frontend | None | HTML | React/Next.js |
| Container | None | Docker | Kubernetes |
| CI/CD | GitHub Actions | GitHub Actions | GitHub Actions + ArgoCD |

---

## Community Features

### v1.x Community

- [ ] Contributing guidelines
- [ ] Issue templates
- [ ] PR templates
- [ ] Code of conduct
- [ ] Discussion forum
- [ ] Example configurations
- [ ] Use case documentation

### v2.x Community

- [ ] Plugin marketplace
- [ ] Community plugins
- [ ] Shared configurations
- [ ] Integration guides
- [ ] Video tutorials
- [ ] Certification program

---

## Success Metrics

| Metric | Phase 1 | Phase 2 | Phase 3 | Phase 4 |
|--------|---------|---------|---------|---------|
| Downloads/month | 100 | 500 | 2,000 | 10,000 |
| GitHub stars | 50 | 200 | 500 | 1,000 |
| Contributors | 3 | 10 | 25 | 50 |
| Data sources | 1 | 6 | 10+ | 20+ |
| Output formats | 17 | 20 | 25+ | 30+ |
| Test coverage | 100% | 100% | 100% | 100% |
| Response time | <20min | <15min | <5min | <1min |

<a id="-türkçe"></a>

# Yol Haritası

## Genel Bakış

Bu belge, TC-SGB-API-to-List projesinin aşamalı geliştirme yol haritasını çizmekte; mevcut aşamayı, planlanan özellikleri ve gelecekteki veri kaynağı entegrasyonlarını içermektedir.

## Aşamalı Yol Haritası

```
+=====================================================================+
|                     Geliştirme Yol Haritası                           |
+=====================================================================+

  1. Aşama            2. Aşama            3. Aşama            4. Aşama
  Temel               Genişleme           Ekosistem           Ölçek
  (v1.0 - v1.2)     (v1.3 - v1.5)     (v2.0 - v2.2)     (v3.0+)
  +-----------+      +-----------+      +-----------+      +-----------+
  |           |      |           |      |           |      |           |
  | Çekirdek |----->| Çoklu     |----->| Çoklu     |----->| Kurumsal  |
  | Hattı    |      | Kaynak    |      | Platform  |      | Özellikler|
  |           |      |           |      |           |      |           |
  | 17 Çıktı |      | CISA KEV  |      | REST API  |      | Kontrol   |
  | Biçimi   |      | Spamhaus  |      | Web UI    |      | Paneli    |
  |           |      | URLhaus   |      | Eklenti   |      | Gerçek    |
  | CLI       |      | OTX       |      | Sistemi   |      | Zamanlı   |
  | Aracı    |      | PhishTank |      |           |      | Uyarılar  |
  |           |      |           |      |           |      | HA/DR     |
  +-----------+      +-----------+      +-----------+      +-----------+

  Durum: AKTİF       Durum: PLANLANAN    Durum: GELECEK     Durum: VİZYON
```

---

## 1. Aşama: Temel (Mevcut)

**Sürüm**: v1.0 - v1.2
**Durum**: Aktif Geliştirme
**Zaman Çizelgesi**: 2025 1. Çeyrek - 2. Çeyrek

### Tamamlanan

- [x] Çekirdek hattı (çekme → doğrulama → normalleştirme → tekilleştirme → çıktı)
- [x] Yeniden deneme mantığı ile asenkron API istemcisi
- [x] Pydantic v2 veri modelleri
- [x] 17 çıktı biçimi (NextDNS, AdGuard, Pi-hole, dnsmasq, Unbound, RPZ, Technitium, MikroTik, nftables, ipset, Suricata, CrowdSec, CSV, JSON, YAML, SQLite)
- [x] Birim test paketi (%100 kapsama)
- [x] CI/CD hattı (GitHub Actions)
- [x] PyPI paketleme
- [x] CLI arayüzü

### Devam Eden

- [ ] 500K+ kayıt için performans optimizasyonu
- [ ] Bellek verimli akış işleme
- [ ] Kapsamlı dokümantasyon
- [ ] Özellik tabanlı test
- [ ] Belirsizlik testi

### Planlanan (v1.1 - v1.2)

- [ ] Sigma kuralı çıktı biçimi
- [ ] YARA kuralı oluşturma
- [ ] Daha hızlı tekilleştirme için Bloom filtresi
- [ ] Yapılandırılabilir kalite eşikleri
- [ ] HTML rapor şablonları
- [ ] PDF rapor oluşturma
- [ ] Artımlı çekme (yerel karma karşılaştırma)
- [ ] Docker konteyner desteği

---

## 2. Aşama: Çoklu Kaynak Genişlemesi

**Sürüm**: v1.3 - v1.5
**Durum**: Planlanan
**Zaman Çizelgesi**: 2025 3. Çeyrek - 4. Çeyrek

### Veri Kaynağı Entegrasyonları

#### CISA Bilinen İstismar Edilen Zafiyetleri (KEV)

```
Kaynak: https://www.cisa.gov/known-exploited-vulnerabilities-catalog
Biçim: JSON (REST API)
Lisans: Kamu Malı (ABD Hükümeti)
Güncelleme: Günlük

Mevcut Veriler:
- CVE Kimlikleri
- Satıcı/ürün adları
- Zafiyet adları
- Eklenecek/gerekli düzeltme tarihleri
- Kısa açıklamalar

Entegrasyon:
- KEEV kataloğunu çekme
- CVE tabanlı IoC'leri çıkarma
- TC SGB verisiyle çapraz referans
- CVE odaklı raporlar oluşturma
```

#### Spamhaus Engelleme Listeleri

```
Kaynak: https://www.spamhaus.org/
Biçim: DROP/eDROP listeleri (metin)
Lisans: Ticari olmayan kullanım ücretsiz
Güncelleme: Günlük

Mevcut Veriler:
- IP aralıkları (DROP listesi)
- Genişletilmiş IP aralıkları (eDROP)
- BGP Ön ekleri
- ASN verileri

Entegrasyon:
- DROP/eDROP listelerini çekme
- IP aralıklarını ayrıştırma
- Güvenlik duvarı kuralları oluşturma (iptables, vb.)
- TC SGB IP'leriyle çapraz referans
```

#### URLhaus (abuse.ch)

```
Kaynak: https://urlhaus.abuse.ch/
Biçim: CSV, JSON, metin
Lisans: CC0 (Kamu Malı)
Güncelleme: Saatlik

Mevcut Veriler:
- Kötü amaçlı URL'ler
- URL durumu (çevrimiçi/çevrimdışı)
- Etiketler (kötü amaçlı yazılım, kimlik avı, vb.)
- Hedef bilgileri
- Yük dağıtma ayrıntıları

Entegrasyon:
- URL beslemelerini çekme
- Etiket/duruma göre filtreleme
- URL engelleme listeleri oluşturma
- TC SGB URL'leriyle çapraz referans
```

#### AlienVault OTX

```
Kaynak: https://otx.alienvault.com/
Biçim: JSON (REST API)
Lisans: Apache 2.0
Güncelleme: Topluluk tarafından

Mevcut Veriler:
- IoC nabızları
- Domain/IP/URL/Hash IoC'leri
- Tehdit aktörü profilleri
- Kötü amaçlı yazılım örnekleri
- Coğrafi konum verileri

Entegrasyon:
- İlgili nabızları çekme
- Türe göre IoC'leri çıkarma
- Tehdit bağlamıyla zenginleştirme
- TC SGB verisiyle çapraz referans
```

#### PhishTank

```
Kaynak: https://www.phishtank.com/
Biçim: JSON, CSV
Lisans: Creative Commons
Güncelleme: Saatlik

Mevcut Veriler:
- Kimlik avı URL'leri
- Hedef markalar
- Doğrulama durumu
- Ekran görüntüsü URL'leri
- Gönderim ayrıntıları

Entegrasyon:
- Doğrulanmış kimlik avı URL'lerini çekme
- Hedef markaya göre filtreleme
- Kimlik avı engelleme listeleri oluşturma
- TC SGB URL'leriyle çapraz referans
```

#### Emerging Threats (ET) Açık Kural Seti

```
Kaynak: https://rules.emergingthreats.net/
Biçim: Snort/Suricata kuralları
Lisans: Açık (ETPro: Ticari)
Güncelleme: Günlük

Mevcut Veriler:
- Ağ imzaları
- IoC tabanlı kurallar
- Protokol tespiti
- Kötü amaçlı yazılım komut kanalları

Entegrasyon:
- ET Open kurallarını ayrıştırma
- IoC tabanlı imzaları çıkarma
- Suricata kuralları oluşturma
- TC SGB verisiyle çapraz referans
```

### 2. Aşama Özellikleri

- [ ] Çoklu kaynak hattı mimarisi
- [ ] Kaynak eklenti sistemi
- [ ] Çapraz kaynak tekilleştirme
- [ ] Tehdit istihbaratı korelasyonu
- [ ] Kaynak önceliği/ağırlıklandırma
- [ ] Tüm kaynaklar için birleşik veri modeli
- [ ] Kaynağa özgü çıktı biçimleri

---

## 3. Aşama: Platform Özellikleri

**Sürüm**: v2.0 - v2.2
**Durum**: Gelecek
**Zaman Çizelgesi**: 2026

### REST API Sunucusu

```
+---------------------------------------------------+
|  REST API Sunucusu Mimarisi                        |
+---------------------------------------------------+

  +-----------+       +-----------+       +-----------+
  |           |       |           |       |           |
  |  FastAPI  |------>| Hat       |------>| Veritabanı|
  |  Sunucusu |       | Motoru    |       | (SQLite)  |
  |           |       |           |       |           |
  +-----------+       +-----------+       +-----------+
        |                                       |
        v                                       v
  +-----------+       +-----------+       +-----------+
  |           |       |           |       |           |
  |  Kimlik   |       | Önbellek  |       | Çıktı     |
  |  Doğrulama|       | (Redis)   |       | Depolama  |
  |  (API Anahtarı)|  |           |       |           |
  +-----------+       +-----------+       +-----------+

  Uç Noktaları:
  GET  /api/v1/iocs           - IoC'leri listeleme
  GET  /api/v1/iocs/{id}      - Tek IoC getirme
  GET  /api/v1/iocs/search    - IoC arama
  GET  /api/v1/stats          - Veri seti istatistikleri
  POST /api/v1/refresh        - Yenileme tetikleme
  GET  /api/v1/health         - Sağlık kontrolü
```

### Web Kontrol Paneli

```
+---------------------------------------------------+
|  Web Kontrol Paneli                               |
+---------------------------------------------------+

  +-----------------------------------------------+
  |  TC-SGB-API-to-List Kontrol Paneli               |
  +-----------------------------------------------+
  |  +----------+  +----------+  +----------+     |
  |  | Toplam   |  | Aktif    |  | Kalite   |     |
  |  | IoC      |  | IoC      |  | Puanı    |     |
  |  | 483.690  |  | 412.300  |  | 0,94     |     |
  |  +----------+  +----------+  +----------+     |
  |                                               |
  |  +------------------------------------------+ |
  |  |  IoC Türü Dağılımı (Grafik)              | |
  |  |  ████ %35 | ████ %25 | ████ %20 | ...  | |
  |  +------------------------------------------+ |
  |                                               |
  |  +------------------------------------------+ |
  |  |  Son Hat Çalıştırmaları                  | |
  |  |  ✓ 2025-01-20 06:00  28sn  483B kayıt   | |
  |  |  ✓ 2025-01-19 06:00  26sn  481B kayıt   | |
  |  |  ✓ 2025-01-18 06:00  27sn  479B kayıt   | |
  |  +------------------------------------------+ |
  +-----------------------------------------------+
```

### Eklenti Sistemi

```python
# Plugin architecture
class SourcePlugin:
    """Base class for data source plugins."""

    def fetch(self) -> AsyncGenerator[IOCRecord, None]:
        """Fetch IoCs from the source."""
        ...

    def validate(self, record: IOCRecord) -> bool:
        """Validate record from this source."""
        ...

    def get_metadata(self) -> SourceMetadata:
        """Get source metadata."""
        ...


# Example plugins
class TCSGBPlugin(SourcePlugin):
    """TC SGB API plugin."""

    ...


class CISAKeVPlugin(SourcePlugin):
    """CISA KEV catalog plugin."""

    ...


class URLhausPlugin(SourcePlugin):
    """URLhaus feed plugin."""

    ...
```

### 3. Aşama Özellikleri

- [ ] FastAPI REST sunucusu
- [ ] SQLite/PostgreSQL depolama
- [ ] Redis önbellek katmanı
- [ ] Web kontrol paneli (React/Vue)
- [ ] Eklenti mimarisi
- [ ] API kimlik doğrulaması (API anahtarları)
- [ ] İstemci başına hız kısıtlaması
- [ ] Gerçek zamanlı güncellemeler için WebSocket
- [ ] STIX/TAXII sunucusuna dışa aktarım
- [ ] Webhook bildirimleri

---

## 4. Aşama: Kurumsal Özellikler

**Sürüm**: v3.0+
**Durum**: Vizyon
**Zaman Çizelgesi**: 2027+

### Özellikler

- [ ] Yüksek erişilebilirlik (HA) dağıtımı
- [ ] Felaket kurtarma (DR) prosedürleri
- [ ] Çoklu kiracı desteği
- [ ] Rol tabanlı erişim kontrolü (RBAC)
- [ ] Denetim günlüğü ve uyumluluk
- [ ] Gerçek zamanlı uyarılar (e-posta, Slack, PagerDuty)
- [ ] SOAR platformlarıyla entegrasyon
- [ ] Tehdit istihbaratı paylaşımı (TAXII 2.1)
- [ ] Makine öğrenmesi anomalisi tespiti
- [ ] Otomatik tehdit yanıtı
- [ ] Özel korelasyon kuralları
- [ ] Coğrafi tehdit haritalama
- [ ] Yönetici raporlama panelleri
- [ ] SSO/SAML kimlik doğrulaması
- [ ] Yerinde kurulum seçeneği

---

## Veri Kaynağı Yol Haritası

```
+=====================================================================+
|  Veri Kaynağı Entegrasyon Zaman Çizelgesi                           |
+=====================================================================+

  2025 Q1    2025 Q2    2025 Q3    2025 Q4    2026 Q1    2026 Q2
  +--------+ +--------+ +--------+ +--------+ +--------+ +--------+
  |        | |        | |        | |        | |        | |        |
  | TC SGB | | TC SGB | | CISA   | | URLhaus| | OTX    | | ET Open|
  | (Tamam)| | v1.2   | | KEV    | |        | |        | |        |
  |        | |        | |        | |        | |        | |        |
  |        | |        | | Spamhaus| | Phish- | | MISP   | | Özel   |
  |        | |        | |        | | Tank   | | Galaxy | | Beslemeler|
  |        | |        | |        | |        | |        | |        |
  +--------+ +--------+ +--------+ +--------+ +--------+ +--------+

  Öncelik: YÜKSEK    YÜKSEK    YÜKSEK    ORTA      ORTA      DÜŞÜK
```

### Kaynak Değerlendirme Kriterleri

| Kriter | Ağırlık | Açıklama |
|--------|---------|----------|
| Veri Kalitesi | %25 | Doğruluk, eksiksizlik, tazelik |
| Lisans | %20 | Entegrasyon için izin vericilik |
| Güvenilirlik | %20 | Çalışma süresi, tutarlılık, bakım |
| Güncelleme Sıklığı | %15 | Verinin ne sıklıkla yenilendiği |
| Veri Hacmi | %10 | Mevcut veri miktarı |
| Entegrasyon Çabası | %10 | Teknik karmaşıklık |

---

## Teknoloji Evrimi

| Bileşen | Mevcut | Planlanan | Gelecek |
|---------|--------|-----------|---------|
| Python | 3.11+ | 3.12+ | 3.13+ |
| HTTP | httpx 0.27 | httpx 0.28+ | HTTP/3 |
| Doğrulama | Pydantic v2 | Pydantic v2.1+ | Pydantic v3 |
| Veritabanı | Yok | SQLite | PostgreSQL |
| Önbellek | Yok | Redis | Redis Cluster |
| Web Çerçevesi | Yok | FastAPI | FastAPI + WebSocket |
| Ön Yüz | Yok | HTML | React/Next.js |
| Konteyner | Yok | Docker | Kubernetes |
| CI/CD | GitHub Actions | GitHub Actions | GitHub Actions + ArgoCD |

---

## Topluluk Özellikleri

### v1.x Topluluk

- [ ] Katılım yönergeleri
- [ ] Sorun şablonları
- [ ] PR şablonları
- [ ] Davranış kuralları
- [ ] Tartışma forumu
- [ ] Örnek yapılandırmalar
- [ ] Kullanım senaryosu dokümantasyonu

### v2.x Topluluk

- [ ] Eklenti pazar yeri
- [ ] Topluluk eklentileri
- [ ] Paylaşılan yapılandırmalar
- [ ] Entegrasyon rehberleri
- [ ] Video eğitimi
- [ ] Sertifika programı

---

## Başarı Metrikleri

| Metrik | 1. Aşama | 2. Aşama | 3. Aşama | 4. Aşama |
|--------|----------|----------|----------|----------|
| Aylık indirme | 100 | 500 | 2.000 | 10.000 |
| GitHub yıldızları | 50 | 200 | 500 | 1.000 |
| Katkıda bulunanlar | 3 | 10 | 25 | 50 |
| Veri kaynakları | 1 | 6 | 10+ | 20+ |
| Çıktı biçimleri | 17 | 20 | 25+ | 30+ |
| Test kapsaması | %100 | %100 | %100 | %100 |
| Yanıt süresi | <20dk | <15dk | <5dk | <1dk |
