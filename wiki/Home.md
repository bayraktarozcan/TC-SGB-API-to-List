> **Language / Dil** &nbsp;
> [EN English](#-english) &nbsp;·&nbsp; [TR Türkçe](#-türkçe)

<a id="-english"></a>

# TC-SGB-API-to-List — Home

## Overview

TC-SGB-API-to-List is an automated threat intelligence pipeline that ingests Indicator of Compromise (IOC) data from the Turkish National Cyber Security Directorate (TC SGB) public API, processes it through validation, normalization, deduplication, and quality control stages, and outputs structured threat intelligence in 17 interoperable formats.

---

## Quick Facts

| Property | Value |
|----------|-------|
| **API Source** | TC SGB Threat Intelligence API (`https://threatintel.sgbsg.gov.tr/api/v1`) |
| **Auth Required** | None (public API) |
| **Pipeline Stages** | Fetch → Validate → Normalize → Dedup → Score → Output |
| **Output Formats** | 16+ (JSON, CSV, STIX 2.1, MISP, Sigma, YARA, nftables, MikroTik, Suricata, etc.) |
| **Python Version** | 3.11+ |
| **License** | MIT |
| **Test Suite** | 330 tests, 73% coverage |

---

## Architecture at a Glance

```
TC SGB API ──► Fetch ──► Validate ──► Normalize ──► Dedup ──► Score ──► Output (17 formats)
```

---

## Key Features

- **Async HTTP fetching** with httpx, retry logic, and rate limiting
- **Pydantic data models** with strict validation
- **Cross-type deduplication** with metadata merging
- **Quality scoring** with false-positive risk detection
- **17 output formats** including NextDNS, AdGuard, Pi-hole, dnsmasq, Unbound, RPZ, Technitium, MikroTik, nftables, ipset, Suricata, CrowdSec, CSV, JSON, YAML, SQLite
- **CI/CD** via GitHub Actions (lint, type check, test, security scan)
- **Dual-language** documentation (English / Turkish)

---

## Getting Started

```bash
git clone https://github.com/bayraktarozcan/TC-SGB-API-to-List.git
cd TC-SGB-API-to-List
pip install -e .

# Fetch all IOC data
tc-sgb fetch

# Generate all output formats
tc-sgb generate -i output/raw_records.json
```

---

## Wiki Pages

- [Architecture](Architecture) — System design and component overview
- [Data Flow](Data-Flow) — End-to-end data pipeline walkthrough
- [Module Architecture](Module-Architecture) — Module responsibilities and interfaces
- [Repository Structure](Repository-Structure) — Directory layout and file purposes
- [API Analysis](API-Analysis) — TC SGB API specification and behavior
- [Data Model](Data-Model) — Pydantic models and enums
- [Threat Model](Threat-Model) — STRIDE threat analysis
- [Security Analysis](Security-Analysis) — Security posture and hardening
- [License Analysis](License-Analysis) — Legal and licensing considerations
- [Test Strategy](Test-Strategy) — Test suite architecture and coverage
- [Regression Strategy](Regression-Strategy) — Regression testing methodology
- [Performance Strategy](Performance-Strategy) — Performance benchmarks and optimization
- [Versioning Strategy](Versioning-Strategy) — Semantic versioning approach
- [Publishing Strategy](Publishing-Strategy) — Distribution and publishing
- [Maintenance Plan](Maintenance-Plan) — Ongoing maintenance procedures
- [Risk Analysis](Risk-Analysis) — Risk assessment and mitigation
- [Roadmap](Roadmap) — Future plans and milestones
- [Legal Notices](Legal-Notices) — Legal and compliance notices
- [Audit Report](Audit-Report) — Documentation audit findings

---

<a id="-türkçe"></a>

# TC-SGB-API-to-List — Ana Sayfa

## Genel Bakış

TC-SGB-API-to-List, T.C. Siber Güvenlik Başkanlığı (TC SGB) kamu API'sinden İhlal Göstergesi (IOC) verilerini otomatik olarak çekip doğrulama, normalleştirme, tekilleştirme ve kalite kontrol aşamalarından geçiren, 17 uyumlu formatta yapılandırılmış tehdit istihbaratı üreten bir otomatik tehdit istihbaratı hattıdır.

---

## Temel Bilgiler

| Özellik | Değer |
|---------|-------|
| **API Kaynağı** | TC SGB Tehdit İstihbaratı API'si (`https://threatintel.sgbsg.gov.tr/api/v1`) |
| **Kimlik Doğrulama** | Gerekli değil (kamu API'si) |
| **Hat Aşamaları** | Çekme → Doğrulama → Normalleştirme → Yineleme Kaldırma → Puanlama → Çıktı |
| **Çıktı Formatları** | 16+ (JSON, CSV, STIX 2.1, MISP, Sigma, YARA, nftables, MikroTik, Suricata, vb.) |
| **Python Sürümü** | 3.11+ |
| **Lisans** | MIT |
| **Test Takımı** | 330 test, %73 kapsama |

---

## Mimari Özet

```
TC SGB API ──► Çekme ──► Doğrulama ──► Normalleştirme ──► Tekilleştirme ──► Puanlama ──► Çıktı (17 format)
```

---

## Temel Özellikler

- **Asenkron HTTP çekme** httpx ile, yeniden deneme mantığı ve hız sınırlama ile
- **Pydantic veri modelleri** sıkı doğrulama ile
- **Çapraz tür yineleme kaldırma** meta veri birleştirme ile
- **Kalite puanlama** sahte pozitif risk tespiti ile
- **17 çıktı formatı** NextDNS, AdGuard, Pi-hole, dnsmasq, Unbound, RPZ, Technitium, MikroTik, nftables, ipset, Suricata, CrowdSec, CSV, JSON, YAML, SQLite dahil
- **CI/CD** GitHub Actions üzerinden (lint, tip kontrolü, test, güvenlik taraması)
- **Çift dilli** dokümantasyon (İngilizce / Türkçe)

---

## Hızlı Başlangıç

```bash
git clone https://github.com/bayraktarozcan/TC-SGB-API-to-List.git
cd TC-SGB-API-to-List
pip install -e .

# Tüm IOC verilerini çek
tc-sgb fetch

# Tüm çıktı formatlarını üret
tc-sgb generate -i output/raw_records.json
```

---

## Wiki Sayfaları

- [Mimari](Architecture#-türkçe) — Sistem tasarımı ve bileşen genel bakışı
- [Veri Akışı](Data-Flow#-türkçe) — Uçtan uca veri hattı yürüyüşü
- [Modül Mimarisi](Module-Architecture#-türkçe) — Modül sorumlulukları ve arayüzleri
- [Depo Yapısı](Repository-Structure#-türkçe) — Dizin yerleşimi ve dosya amaçları
- [API Analizi](API-Analysis#-türkçe) — TC SGB API spesifikasyonu ve davranışı
- [Veri Modeli](Data-Model#-türkçe) — Pydantic modelleri ve numaralandırmalar
- [Tehdit Modeli](Threat-Model#-türkçe) — STRIDE tehdit analizi
- [Güvenlik Analizi](Security-Analysis#-türkçe) — Güvenlik duruşu ve sertleştirme
- [Lisans Analizi](License-Analysis#-türkçe) — Hukuki ve lisanslama hususları
- [Test Stratejisi](Test-Strategy#-türkçe) — Test takımı mimarisi ve kapsamı
- [Regresyon Stratejisi](Regression-Strategy#-türkçe) — Regresyon test metodolojisi
- [Performans Stratejisi](Performance-Strategy#-türkçe) — Performans karşılaştırmaları ve optimizasyon
- [Sürüm Stratejisi](Versioning-Strategy#-türkçe) — Semantik sürümleme yaklaşımı
- [Yayın Stratejisi](Publishing-Strategy#-türkçe) — Dağıtım ve yayınlanma
- [Bakım Planı](Maintenance-Plan#-türkçe) — Sürekli bakım prosedürleri
- [Risk Analizi](Risk-Analysis#-türkçe) — Risk değerlendirmesi ve azaltma
- [Yol Haritası](Roadmap#-türkçe) — Gelecek planları ve dönüm noktaları
- [Yasal Bildirimler](Legal-Notices#-türkçe) — Hukuki ve uyum bildirimleri
- [Denetim Raporu](Audit-Report#-türkçe) — Dokümantasyon denetim bulguları
