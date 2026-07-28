> **Language / Dil** &nbsp;
> [EN English](#-english) &nbsp;·&nbsp; [TR Türkçe](#-türkçe)

<a id="-english"></a>

# System Architecture

## Overview

The TC-SGB-API-to-List system is an automated threat intelligence pipeline that ingests Indicator of Compromise (IOC) data from the Turkish National Cyber Security Directorate (TC SGB) public API, processes it through validation, normalization, deduplication, and quality control stages, and outputs structured threat intelligence in 17 interoperable formats.

## High-Level Architecture

```
+=====================================================================+
|                        TC-SGB-API-to-List                              |
|                  Threat Intelligence Pipeline                       |
+=====================================================================+

  EXTERNAL                  INTERNAL PIPELINE                    OUTPUT
+-----------+        +---------------------------+        +---------------+
|           |        |                           |        |               |
|  TC SGB   |  HTTPS |  +-------+   +--------+  |  File  |  JSON         |
|  API      |------->|  | Fetch |-->|Validate|  |  I/O   |  STIX 2.1     |
|  Endpoint |        |  +-------+   +--------+  |------->|  CSV          |
|           |        |                |          |        |  MISP         |
|           |        |                v          |        |  OpenIOC      |
|           |        |  +-----------+ +--------+ |        |  PDF Report   |
|           |        |  |Normalize  |<-| Dedup  | |        |  Markdown     |
|           |        |  +-----------+ +--------+ |        |  CEF          |
|           |        |       |                   |        |  LEEF         |
|           |        |       v                   |        |  Syslog       |
|           |        |  +--------+  +---------+  |        |  Sigma Rules  |
|           |        |  |Quality |->| Output  |  |        |  YARA Rules   |
|           |        |  |Check   |  |Engine   |  |        |  HTML         |
|           |        |  +--------+  +---------+  |        |  Splunk       |
|           |        |                |          |        |  QRadar       |
|           |        |                v          |        |  Elastic      |
+-----------+        |          +---------+      |        |  Grafana      |
                     |          | Publish |      |        +---------------+
                     |          +---------+      |
                     +---------------------------+
                                |
                                v
                     +---------------------------+
                     |      CI/CD Pipeline        |
                     |   GitHub Actions Runner    |
                     +---------------------------+
```

## Component Architecture

```
+------------------------------------------------------------------+
|                        ORCHESTRATOR (pipeline.py)                 |
+------------------------------------------------------------------+
         |          |          |          |          |
         v          v          v          v          v
+----------+ +----------+ +---------+ +---------+ +---------+
| API      | | Data     | | Process | | Quality | | Output  |
| Client   | | Models   | | Engine  | | Engine  | | Engine  |
|          | |          | |         | |         | |         |
| client.py| | models.py| |pipeline | |quality.py| |outputs.py|
|          | |          | |  .py    | |         | |         |
| - httpx  | | - Pydantic| |         | | - Tests | | - 17   |
| - Async  | | - Enums  | | - valid | | - Stats | |   formats|
| - Retry  | | - Schema | | - norm  | | - Score | | - File  |
| - Rate   | | - Types  | | - dedup | | - Report| |   I/O   |
|   Limit  | |          | |         | |         | |         |
+----------+ +----------+ +---------+ +---------+ +---------+
```

## Data Flow

```
 1. FETCH               2. VALIDATE            3. NORMALIZE
+----------+          +----------+          +-----------+
| API Call |          | Schema   |          | Canonical |
| GET /v1  | -------> | Check    | -------> | Format    |
| page=N   |          | Type Map |          | Lowercase |
+----------+          | Null Chk |          | Trim      |
                      +----------+          +-----------+
                          |                       |
                          v                       v
 4. DEDUP              5. QUALITY            6. OUTPUT
+----------+          +----------+          +-----------+
| Hash     |          | FP Check |          | JSON      |
| Content  | -------> | Benign   | -------> | STIX      |
| Seen Map |          | Whitelist|          | CSV       |
+----------+          | Stats    |          | MISP      |
                      +----------+          | ...17    |
                                            +-----------+
```

## Technology Stack

### Core Runtime

| Component        | Technology     | Version  | Purpose                        |
|------------------|----------------|----------|--------------------------------|
| Language         | Python         | 3.11+    | Primary language               |
| HTTP Client      | httpx          | 0.27+    | Async HTTP with connection pool |
| Data Validation  | Pydantic       | 2.9+     | Schema validation & serialization |
| Async Runtime    | asyncio        | stdlib   | Concurrent I/O operations      |
| CLI Output       | rich           | 13.0+    | Terminal formatting & spinners  |

### Development & Testing

| Component        | Technology     | Purpose                        |
|------------------|----------------|--------------------------------|
| Test Framework   | pytest         | Unit and integration tests     |
| Async Testing    | pytest-asyncio | Async test support             |
| Coverage         | coverage.py    | Code coverage measurement      |
| Type Checking    | mypy           | Static type analysis           |
| Linting          | ruff           | Code style and quality         |
| Formatting       | ruff format    | Code formatting                |
| Property Testing | Hypothesis     | Fuzz and property-based tests  |
| Benchmarking     | pytest-benchmark | Performance benchmarks       |

### CI/CD & Deployment

| Component        | Technology     | Purpose                        |
|------------------|----------------|--------------------------------|
| CI/CD            | GitHub Actions | Automated pipeline             |
| Versioning       | SemVer         | Release management             |
| Packaging        | setuptools     | Package building               |
| Registry         | PyPI           | Package distribution           |

## Deployment Model

```
+=====================================================================+
|                      GitHub Actions CI/CD                            |
+=====================================================================+

  TRIGGER                         PIPELINE
+-----------+               +------------------+
|           |               |                  |
|  Push to  |    -------->  |  1. Checkout     |
|  main     |               |  2. Setup Python |
|           |               |  3. Install Deps |
|  PR       |    -------->  |  4. Lint (ruff)  |
|           |               |  5. Type Check   |
|  Tag      |    -------->  |  6. Test (pytest)|
|  v*.*.*   |               |  7. Build        |
|           |               |  8. Publish      |
+-----------+               +------------------+
                                     |
                                     v
                            +------------------+
                            |                  |
                            |  PyPI Registry   |
                            |  GitHub Release  |
                            |  Artifact Upload |
                            |                  |
                            +------------------+
```

### Release Flow

```
  Developer               GitHub                  PyPI
     |                      |                       |
     |  git push --tags     |                       |
     |  v1.2.0              |                       |
     |--------------------->|                       |
     |                      |  Trigger Actions      |
     |                      |  Run Test Suite       |
     |                      |  Build Package        |
     |                      |---------------------->|
     |                      |  twine upload         |
     |                      |  pip install tc-sgb   |
     |                      |                       |
     |  Create Release      |                       |
     |  Upload Artifacts    |                       |
     |  Generate Notes      |                       |
     |<---------------------|                       |
```

## Design Principles

1. **Immutable Data**: IOC records are validated once and never mutated after normalization
2. **Fail-Safe Defaults**: Invalid data is rejected with detailed error reporting
3. **Defense in Depth**: Multiple validation layers prevent malformed data propagation
4. **Auditability**: Every transformation is logged with before/after snapshots
5. **Idempotency**: Re-running the pipeline produces identical output for identical input
6. **Separation of Concerns**: Each module has a single, well-defined responsibility
7. **Zero-Trust Input**: All API responses are treated as untrusted until validated

## Concurrency Model

```
+=====================================================================+
|                     Async Pipeline Execution                         |
+=====================================================================+

  Event Loop (asyncio)
  +---------------------------------------------------------+
  |                                                         |
  |  Task 1: Fetch Page 1     [=====]                      |
  |  Task 2: Fetch Page 2     [=====]                      |
  |  Task 3: Fetch Page 3     [=====]                      |
  |  ...                                                    |
  |  Task N: Fetch Page N     [=====]                      |
  |                                                         |
  |  Semaphore(max_concurrent=5)                            |
  |                                                         |
  +---------------------------------------------------------+
                          |
                          v
  +---------------------------------------------------------+
  |  Sequential Processing Pipeline                         |
  |  Fetch -> Validate -> Normalize -> Dedup -> Output      |
  +---------------------------------------------------------+
```

The system uses asyncio with bounded concurrency to respect rate limits while maximizing throughput. Pages are fetched concurrently with a semaphore limiting in-flight requests, then processed sequentially to maintain data integrity.

<a id="-türkçe"></a>

# Sistem Mimarisi

## Genel Bakış

TC-SGB-API-to-List sistemi, Türkiye Ulusal Siber Güvenlik Direktörlüğü (TC SGB) kamu API'sinden Tehdit Göstergesi (IOC) verilerini alan, doğrulama, normalleştirme, tekilleştirme ve kalite kontrol aşamalarından geçirerek yapılandırılmış tehdit istihbaratını 17 birlikte çalışabilir formatta çıktı olarak üreten otomatik bir tehdit istihbaratı hattıdır.

## Üst Düzey Mimari

```
+=====================================================================+
|                        TC-SGB-API-to-List                              |
|                  Threat Intelligence Pipeline                       |
+=====================================================================+

  EXTERNAL                  INTERNAL PIPELINE                    OUTPUT
+-----------+        +---------------------------+        +---------------+
|           |        |                           |        |               |
|  TC SGB   |  HTTPS |  +-------+   +--------+  |  File  |  JSON         |
|  API      |------->|  | Fetch |-->|Validate|  |  I/O   |  STIX 2.1     |
|  Endpoint |        |  +-------+   +--------+  |------->|  CSV          |
|           |        |                |          |        |  MISP         |
|           |        |                v          |        |  OpenIOC      |
|           |        |  +-----------+ +--------+ |        |  PDF Report   |
|           |        |  |Normalize  |<-| Dedup  | |        |  Markdown     |
|           |        |  +-----------+ +--------+ |        |  CEF          |
|           |        |       |                   |        |  LEEF         |
|           |        |       v                   |        |  Syslog       |
|           |        |  +--------+  +---------+  |        |  Sigma Rules  |
|           |        |  |Quality |->| Output  |  |        |  YARA Rules   |
|           |        |  |Check   |  |Engine   |  |        |  HTML         |
|           |        |  +--------+  +---------+  |        |  Splunk       |
|           |        |                |          |        |  QRadar       |
|           |        |                v          |        |  Elastic      |
+-----------+        |          +---------+      |        |  Grafana      |
                     |          | Publish |      |        +---------------+
                     |          +---------+      |
                     +---------------------------+
                                |
                                v
                     +---------------------------+
                     |      CI/CD Pipeline        |
                     |   GitHub Actions Runner    |
                     +---------------------------+
```

## Bileşen Mimarisi

```
+------------------------------------------------------------------+
|                        ORCHESTRATOR (pipeline.py)                 |
+------------------------------------------------------------------+
         |          |          |          |          |
         v          v          v          v          v
+----------+ +----------+ +---------+ +---------+ +---------+
| API      | | Data     | | Process | | Quality | | Output  |
| Client   | | Models   | | Engine  | | Engine  | | Engine  |
|          | |          | |         | |         | |         |
| client.py| | models.py| |pipeline | |quality.py| |outputs.py|
|          | |          | |  .py    | |         | |         |
| - httpx  | | - Pydantic| |         | | - Tests | | - 17   |
| - Async  | | - Enums  | | - valid | | - Stats | |   formats|
| - Retry  | | - Schema | | - norm  | | - Score | | - File  |
| - Rate   | | - Types  | | - dedup | | - Report| |   I/O   |
|   Limit  | |          | |         | |         | |         |
+----------+ +----------+ +---------+ +---------+ +---------+
```

## Veri Akışı

```
 1. FETCH               2. VALIDATE            3. NORMALIZE
+----------+          +----------+          +-----------+
| API Call |          | Schema   |          | Canonical |
| GET /v1  | -------> | Check    | -------> | Format    |
| page=N   |          | Type Map |          | Lowercase |
+----------+          | Null Chk |          | Trim      |
                      +----------+          +-----------+
                          |                       |
                          v                       v
 4. DEDUP              5. QUALITY            6. OUTPUT
+----------+          +----------+          +-----------+
| Hash     |          | FP Check |          | JSON      |
| Content  | -------> | Benign   | -------> | STIX      |
| Seen Map |          | Whitelist|          | CSV       |
+----------+          | Stats    |          | MISP      |
                      +----------+          | ...17    |
                                            +-----------+
```

## Teknoloji Yığını

### Çalışma Zamanı Temeli

| Bileşen          | Teknoloji      | Sürüm    | Amaç                            |
|------------------|----------------|----------|----------------------------------|
| Dil              | Python         | 3.11+    | Ana programlama dili             |
| HTTP İstemcisi   | httpx          | 0.27+    | Bağlantı havuzlu asenkron HTTP   |
| Veri Doğrulama   | Pydantic       | 2.9+     | Şema doğrulama ve serializasyon  |
| Asenkron Çalışma | asyncio        | stdlib   | Eşzamanlı I/O işlemleri          |
| CLI Çıktısı      | rich           | 13.0+    | Terminal biçimlendirme ve döndürme |

### Geliştirme ve Test

| Bileşen          | Teknoloji      | Amaç                            |
|------------------|----------------|----------------------------------|
| Test Çerçevesi   | pytest         | Birim ve entegrasyon testleri    |
| Asenkron Test    | pytest-asyncio | Asenkron test desteği            |
| Kod Kapsaması    | coverage.py    | Testlerin kodun hangi satırlarını çalıştırdığını ölçer (testlerin kodu ne kadar kapsadığını gösterir) |
| Tür Denetimi     | mypy           | Statik tür analizi               |
| Kod Denetimi     | ruff           | Kod stili ve kalitesi            |
| Biçimlendirme    | ruff format    | Kod biçimlendirme                |
| Özellik Testi    | Hypothesis     | Bulanık ve özellik tabanlı testler |
| Ölçüm           | pytest-benchmark | Performans karşılaştırmaları   |

### CI/CD ve Dağıtım

| Bileşen          | Teknoloji      | Amaç                            |
|------------------|----------------|----------------------------------|
| CI/CD            | GitHub Actions | Otomatik hattı                   |
| Sürümleme        | SemVer         | Yayın yönetimi                   |
| Paketleme        | setuptools     | Paket oluşturma                  |
| Kayıt Defteri    | PyPI           | Paket dağıtımı                   |

## Dağıtım Modeli

```
+=====================================================================+
|                      GitHub Actions CI/CD                            |
+=====================================================================+

  TRIGGER                         PIPELINE
+-----------+               +------------------+
|           |               |                  |
|  Push to  |    -------->  |  1. Checkout     |
|  main     |               |  2. Setup Python |
|           |               |  3. Install Deps |
|  PR       |    -------->  |  4. Lint (ruff)  |
|           |               |  5. Type Check   |
|  Tag      |    -------->  |  6. Test (pytest)|
|  v*.*.*   |               |  7. Build        |
|           |               |  8. Publish      |
+-----------+               +------------------+
                                     |
                                     v
                            +------------------+
                            |                  |
                            |  PyPI Registry   |
                            |  GitHub Release  |
                            |  Artifact Upload |
                            |                  |
                            +------------------+
```

### Yayın Akışı

```
  Developer               GitHub                  PyPI
     |                      |                       |
     |  git push --tags     |                       |
     |  v1.2.0              |                       |
     |--------------------->|                       |
     |                      |  Trigger Actions      |
     |                      |  Run Test Suite       |
     |                      |  Build Package        |
     |                      |---------------------->|
     |                      |  twine upload         |
     |                      |  pip install tc-sgb   |
     |                      |                       |
     |  Create Release      |                       |
     |  Upload Artifacts    |                       |
     |  Generate Notes      |                       |
     |<---------------------|                       |
```

## Tasarım İlkeleri

1. **Değişmez Veri**: IOC kayıtları bir kez doğrulanır ve normalleştirmeden sonra asla değiştirilmez
2. **Güvenli Varsayılanlar**: Geçersiz veriler ayrıntılı hata raporlamasıyla reddedilir
3. **Derinlemesine Savunma**: Çoklu doğrulama katmanları hatalı verilerin yayılmasını engeller
4. **Denetlenebilirlik**: Her dönüştürme, öncesi/sonrası anlık görüntüleriyle kaydedilir
5. **İdempotentlik**: Hattın tekrar çalıştırılması aynı girdi için aynı çıktıyı üretir
6. **Sorumluluk Ayrımı**: Her modülün tek, iyi tanımlanmış bir sorumluluğu vardır
7. **Sıfır Güven Girdisi**: Tüm API yanıtları doğrulanana kadar güvensiz olarak değerlendirilir

## Eşzamanlılık Modeli

```
+=====================================================================+
|                     Async Pipeline Execution                         |
+=====================================================================+

  Event Loop (asyncio)
  +---------------------------------------------------------+
  |                                                         |
  |  Task 1: Fetch Page 1     [=====]                      |
  |  Task 2: Fetch Page 2     [=====]                      |
  |  Task 3: Fetch Page 3     [=====]                      |
  |  ...                                                    |
  |  Task N: Fetch Page N     [=====]                      |
  |                                                         |
  |  Semaphore(max_concurrent=5)                            |
  |                                                         |
  +---------------------------------------------------------+
                          |
                          v
  +---------------------------------------------------------+
  |  Sequential Processing Pipeline                         |
  |  Fetch -> Validate -> Normalize -> Dedup -> Output      |
  +---------------------------------------------------------+
```

Sistem, verimliliği en üst düzeye çıkarırken hız sınırlamalarına uymak için sınırlı eşzamanlılık ile asyncio kullanır. Sayfalar, eşzamanlı istekleri sınırlayan bir semafor ile eşzamanlı olarak getirilir, ardından veri bütünlüğünü korumak için sıralı olarak işlenir.
