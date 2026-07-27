> **Language / Dil** &nbsp;
> [EN English](#-english) &nbsp;·&nbsp; [TR Türkçe](#-türkçe)

<a id="-english"></a>

# TC-SGB-API-to-List — Home

## Overview

TC-SGB-API-to-List is an automated threat intelligence pipeline that ingests Indicator of Compromise (IOC) data from the Turkish National Cyber Security Directorate (TC SGB) public API, processes it through validation, normalization, deduplication, and quality control stages, and outputs structured threat intelligence in 16+ interoperable formats.

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
TC SGB API ──► Fetch ──► Validate ──► Normalize ──► Dedup ──► Score ──► Output (16+ formats)
```

---

## Key Features

- **Async HTTP fetching** with httpx, retry logic, and rate limiting
- **Pydantic data models** with strict validation
- **Cross-type deduplication** with metadata merging
- **Quality scoring** with false-positive risk detection
- **16+ output formats** including nftables, MikroTik, Suricata, Sigma, YARA, STIX 2.1, MISP
- **CI/CD** via GitHub Actions (lint, type check, test, security scan)
- **Dual-language** documentation (English / Turkish)

---

## Getting Started

```bash
git clone https://github.com/bayraktarozcan/TC-SGB-API-to-List.git
cd TC-SGB-API-to-List
python -m venv .venv
.venv\Scripts\activate          # Windows
# source .venv/bin/activate     # macOS/Linux
pip install -r requirements.txt

# Fetch all IOC data
python -m scripts.main fetch

# Generate all output formats
python -m scripts.main generate
```

---

## Wiki Pages

- [Architecture](Architecture) — System design and component overview
- [Data Flow](Data-Flow) — End-to-end data pipeline walkthrough
- [API Analysis](API-Analysis) — TC SGB API specification and behavior
- [Data Model](Data-Model) — Pydantic models and enums
- [Security Analysis](Security-Analysis) — Security posture and threat model
- [Test Strategy](Test-Strategy) — Test suite architecture and coverage
- [Roadmap](Roadmap) — Future plans and milestones

---

<a id="-türkçe"></a>

# TC-SGB-API-to-List — Ana Sayfa

## Genel Bakış

TC-SGB-API-to-List, T.C. Siber Güvenlik Başkanlığı (TC SGB) kamu API'sinden İhlal Göstergesi (IOC) verilerini otomatik olarak çekip doğrulama, normalleştirme, yineleme kaldırma ve kalite kontrol aşamalarından geçiren, 16'dan fazla uyumlu formatta yapılandırılmış tehdit istihbaratı üreten bir otomatik tehdit istihbaratı hattıdır.

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
TC SGB API ──► Çekme ──► Doğrulama ──► Normalleştirme ──► Yineleme Kaldırma ──► Puanlama ──► Çıktı (16+ format)
```

---

## Temel Özellikler

- **Asenkron HTTP çekme** httpx ile, yeniden deneme mantığı ve hız sınırlama ile
- **Pydantic veri modelleri** sıkı doğrulama ile
- **Çapraz tür yineleme kaldırma** meta veri birleştirme ile
- **Kalite puanlama** sahte pozitif risk tespiti ile
- **16+ çıktı formatı** nftables, MikroTik, Suricata, Sigma, YARA, STIX 2.1, MISP dahil
- **CI/CD** GitHub Actions üzerinden (lint, tip kontrolü, test, güvenlik taraması)
- **Çift dilli** dokümantasyon (İngilizce / Türkçe)

---

## Hızlı Başlangıç

```bash
git clone https://github.com/bayraktarozcan/TC-SGB-API-to-List.git
cd TC-SGB-API-to-List
python -m venv .venv
.venv\Scripts\activate          # Windows
# source .venv/bin/activate     # macOS/Linux
pip install -r requirements.txt

# Tüm IOC verilerini çek
python -m scripts.main fetch

# Tüm çıktı formatlarını üret
python -m scripts.main generate
```

---

## Wiki Sayfaları

- [Mimari](Architecture#-türkçe) — Sistem tasarımı ve bileşen genel bakışı
- [Veri Akışı](Data-Flow#-textContent) — Uçtan uca veri hattı yürüyüşü
- [API Analizi](API-Analysis#-türkçe) — TC SGB API spesifikasyonu ve davranışı
- [Veri Modeli](Data-Model#-textContent) — Pydantic modelleri ve numaralandırmalar
- [Güvenlik Analizi](Security-Analysis#-textContent) — Güvenlik duruşu ve tehdit modeli
- [Test Stratejisi](Test-Strategy#-textContent) — Test takımı mimarisi ve kapsamı
- [Yol Haritası](Roadmap#-textContent) — Gelecek planları ve dönüm noktaları
