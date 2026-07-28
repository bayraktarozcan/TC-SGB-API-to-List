> **Language / Dil** &nbsp;
> [EN English](#-english) &nbsp;·&nbsp; [TR Türkçe](#-türkçe)

<a id="-english"></a>

# Data Model

## Overview

This document defines all data models, schemas, field definitions, and enumerations used in the TC-SGB-API-to-List system. All models use Pydantic v2 for validation and serialization.

## Enums

### IOCType

Indicator of Compromise type classification.

```python
class IOCType(str, Enum):
    DOMAIN = "domain"
    URL = "url"
    IP = "ip"
    IP6 = "ip6"
    IP6NET = "ip6net"
```

### DescriptionCategory

Category of threat description from the SGB API.

```python
class DescriptionCategory(str, Enum):
    PHISHING = "PH"
    FINANCIAL_PHISHING = "BP"
    MALWARE_DIST_DOMAIN = "MD"
    MALWARE_DIST_IP = "MI"
    MALWARE_DIST_URL = "MU"
    MALWARE_CMD_CENTER = "MC"
    CYBER_ATTACK = "CA"
```

### Source

Originating source of the IOC report.

```python
class Source(str, Enum):
    USOM = "US"   # Ulusal Siber Olay Müdahale
    SOME = "SO"   # Siber Olayları Müdahale Ekipleri
    RSA = "RS"    # Regional Security Assessment
    IHBAR = "IH"  # İhbar
    SGB = "SB"    # Siber Güvenlik Başkanlığı
```

### ConnectionType

Network connection type classification.

```python
class ConnectionType(str, Enum):
    APT_CNC = "AC"
    BOTNET_CNC = "BC"
    EXPLOIT_KIT = "EK"
    MOBILE_CNC = "MC"
    MALWARE_DOWNLOAD = "MF"
    MINING_MALWARE = "MM"
    OTHER = "OT"
    PHISHING = "PH"
```

## API Response Models

### PaginatedResponse

Generic paginated response wrapper matching the real SGB API field names.

```python
class PaginatedResponse(BaseModel, Generic[T]):
    models: list[T] = Field(default_factory=list)
    totalCount: int = 0
    count: int = 0
    page: int = 0
    pageCount: int = 0
```

### AddressRecord

Single IOC record from `/api/address/index`.

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `id` | `int` | — | Unique identifier |
| `url` | `str` | `""` | IOC value (domain, IP, URL) |
| `type` | `str` | `""` | IOC type code |
| `desc` | `str` | `""` | Description category code |
| `source` | `str` | `""` | Source code |
| `date` | `str` | `""` | Observation date |
| `criticality_level` | `int` | `10` | Criticality level (1=highest) |
| `connectiontype` | `str` | `""` | Connection type code |

### DescriptionRecord

Reference record from `/api/address-description/index`.

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `id` | `str` | — | Description category code |
| `tr_title` | `str` | `""` | Turkish title |
| `en_title` | `str` | `""` | English title |
| `tr_desc` | `str` | `""` | Turkish description |
| `en_desc` | `str` | `""` | English description |

### ConnectionTypeRecord

Reference record from `/api/address-connection-type/index`.

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `id` | `str` | — | Connection type code |
| `tr_title` | `str` | `""` | Turkish title |
| `en_title` | `str` | `""` | English title |

### SourceRecord

Reference record from `/api/address-source/index`.

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `id` | `str` | — | Source code |
| `tr_title` | `str` | `""` | Turkish title |
| `en_title` | `str` | `""` | English title |

### IncidentRecord

Record from `/api/incident/index`.

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `id` | `int` | — | Incident ID |
| `title` | `str` | `""` | Title |
| `desc` | `str` | `""` | Description |
| `date` | `str` | `""` | Date |
| `active` | `bool` | `True` | Active status |
| `slug` | `str` | `""` | URL slug |
| `language` | `str` | `""` | Language code |

### AnnouncementRecord

Record from `/api/announcement/index`.

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `id` | `int` | — | Announcement ID |
| `title` | `str` | `""` | Title |
| `desc` | `str` | `""` | Description |
| `date` | `str` | `""` | Date |
| `active` | `bool` | `True` | Active status |
| `slug` | `str` | `""` | URL slug |
| `language` | `str` | `""` | Language code |

## Pipeline Models

### ValidatedIOC

An IOC that has passed validation.

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `raw_url` | `str` | — | Original IOC value |
| `ioc_type` | `IOCType` | — | Classified IOC type |
| `desc` | `DescriptionCategory \| None` | `None` | Description category |
| `source` | `Source \| None` | `None` | Originating source |
| `date` | `datetime \| None` | `None` | Observation date |
| `criticality_level` | `int` | `10` | Criticality (1=highest) |
| `connectiontype` | `ConnectionType \| None` | `None` | Connection type |
| `original_id` | `int` | `0` | Original API record ID |
| `validation_errors` | `list[str]` | `[]` | Non-fatal validation notes |

### NormalizedIOC

An IOC that has been normalised (lowercase, trimmed, IDN resolved, standard port extracted).

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `value` | `str` | — | Normalised IOC value |
| `ioc_type` | `IOCType` | — | Classified IOC type |
| `desc` | `DescriptionCategory \| None` | `None` | Description category |
| `source` | `Source \| None` | `None` | Originating source |
| `date` | `datetime \| None` | `None` | Observation date |
| `criticality_level` | `int` | `10` | Criticality (1=highest) |
| `connectiontype` | `ConnectionType \| None` | `None` | Connection type |
| `original_id` | `int` | `0` | Original API record ID |
| `normalization_notes` | `list[str]` | `[]` | Normalisation log |

### ScoredIOC

An IOC with a quality / confidence score.

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `value` | `str` | — | Normalised IOC value |
| `ioc_type` | `IOCType` | — | Classified IOC type |
| `desc` | `DescriptionCategory \| None` | `None` | Description category |
| `source` | `Source \| None` | `None` | Originating source |
| `date` | `datetime \| None` | `None` | Observation date |
| `criticality_level` | `int` | `10` | Criticality (1=highest) |
| `connectiontype` | `ConnectionType \| None` | `None` | Connection type |
| `original_id` | `int` | `0` | Original API record ID |
| `quality_score` | `float` | `0.0` | Confidence score (0–100) |
| `false_positive_risk` | `str` | `"low"` | FP risk level: low / medium / high |
| `flags` | `list[str]` | `[]` | Dedup metadata and quality flags |

### PipelineStats

Statistics collected during a pipeline run.

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `total_fetched` | `int` | `0` | Records fetched from API |
| `after_validation` | `int` | `0` | Records passing validation |
| `after_normalization` | `int` | `0` | Records after normalisation |
| `after_dedup` | `int` | `0` | Records after deduplication |
| `after_quality` | `int` | `0` | Records after quality filtering |
| `by_type` | `dict[str, int]` | `{}` | Count by IOC type |
| `by_source` | `dict[str, int]` | `{}` | Count by source |
| `by_desc` | `dict[str, int]` | `{}` | Count by description category |
| `by_criticality` | `dict[int, int]` | `{}` | Count by criticality level |
| `validation_rejected` | `int` | `0` | Records rejected by validation |
| `quality_rejected` | `int` | `0` | Records rejected by quality |
| `duplicates_removed` | `int` | `0` | Duplicates removed |
| `fetch_duration_seconds` | `float` | `0.0` | Time spent fetching |
| `pipeline_duration_seconds` | `float` | `0.0` | Total pipeline time |
| `errors` | `list[str]` | `[]` | Error messages |

## Client Models

### APIError

Exception raised when the SGB API returns a non-2xx response.

```python
class APIError(Exception):
    status_code: int   # HTTP status code
    detail: str        # Error message
    url: str           # Request URL
```

### AsyncAPIClient

Async HTTP client for the SGB API. No authentication required.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `base_url` | `str` | `https://siberguvenlik.gov.tr` | API base URL |
| `max_retries` | `int` | `3` | Max retry attempts |
| `rate_limit` | `float` | `10.0` | Requests per second |
| `timeout` | `float` | `60.0` | HTTP timeout (seconds) |

## Deduplicator Models

### DeduplicationResult

Result of deduplicating a list of scored IOCs.

| Field | Type | Description |
|-------|------|-------------|
| `kept` | `list[ScoredIOC]` | Deduplicated IOC list |
| `removed_count` | `int` | Number of duplicates removed |
| `merge_log` | `list[str]` | Log of merge decisions |

## Data Flow

The pipeline transforms data through these model stages:

```
API Response (PaginatedResponse[AddressRecord])
    → ValidatedIOC[]
    → NormalizedIOC[]
    → ScoredIOC[]
    → DeduplicationResult
    → ScoredIOC[] (final, written to output files)
```

---

<a id="-türkçe"></a>

# Veri Modeli

## Genel Bakış

Bu belge, TC-SGB-API-to-List sisteminde kullanılan tüm veri modellerini, şemaları, alan tanımlarını ve numaralandırmaları tanımlar. Tüm modeller doğrulama ve seri hale getirme için Pydantic v2 kullanır.

## Numaralandırmalar

### IOCType

Tehdit göstergesi tipi sınıflandırması.

```python
class IOCType(str, Enum):
    DOMAIN = "domain"
    URL = "url"
    IP = "ip"
    IP6 = "ip6"
    IP6NET = "ip6net"
```

### DescriptionCategory

SGB API'sinden gelen tehdit açıklama kategorisi.

```python
class DescriptionCategory(str, Enum):
    PHISHING = "PH"
    FINANCIAL_PHISHING = "BP"
    MALWARE_DIST_DOMAIN = "MD"
    MALWARE_DIST_IP = "MI"
    MALWARE_DIST_URL = "MU"
    MALWARE_CMD_CENTER = "MC"
    CYBER_ATTACK = "CA"
```

### Source

IOC raporunun geldiği kaynak.

```python
class Source(str, Enum):
    USOM = "US"   # Ulusal Siber Olay Müdahale
    SOME = "SO"   # Siber Olayları Müdahale Ekipleri
    RSA = "RS"    # Regional Security Assessment
    IHBAR = "IH"  # İhbar
    SGB = "SB"    # Siber Güvenlik Başkanlığı
```

### ConnectionType

Ağ bağlantısı tipi sınıflandırması.

```python
class ConnectionType(str, Enum):
    APT_CNC = "AC"
    BOTNET_CNC = "BC"
    EXPLOIT_KIT = "EK"
    MOBILE_CNC = "MC"
    MALWARE_DOWNLOAD = "MF"
    MINING_MALWARE = "MM"
    OTHER = "OT"
    PHISHING = "PH"
```

## API Yanıt Modelleri

### PaginatedResponse

Gerçek SGB API alan adlarıyla eşleşen genel sayfalı yanıt sarmalayıcısı.

```python
class PaginatedResponse(BaseModel, Generic[T]):
    models: list[T] = Field(default_factory=list)
    totalCount: int = 0
    count: int = 0
    page: int = 0
    pageCount: int = 0
```

### AddressRecord

`/api/address/index` endpoint'inden gelen tek IOC kaydı.

| Alan | Tip | Varsayılan | Açıklama |
|------|-----|-----------|----------|
| `id` | `int` | — | Benzersiz tanımlayıcı |
| `url` | `str` | `""` | IOC değeri (alan adı, IP, URL) |
| `type` | `str` | `""` | IOC tipi kodu |
| `desc` | `str` | `""` | Açıklama kategori kodu |
| `source` | `str` | `""` | Kaynak kodu |
| `date` | `str` | `""` | Gözlem tarihi |
| `criticality_level` | `int` | `10` | Kritiklik düzeyi (1=en yüksek) |
| `connectiontype` | `str` | `""` | Bağlantı tipi kodu |

### DescriptionRecord

`/api/address-description/index` referans kaydı.

| Alan | Tip | Varsayılan | Açıklama |
|------|-----|-----------|----------|
| `id` | `str` | — | Açıklama kategori kodu |
| `tr_title` | `str` | `""` | Türkçe başlık |
| `en_title` | `str` | `""` | İngilizce başlık |
| `tr_desc` | `str` | `""` | Türkçe açıklama |
| `en_desc` | `str` | `""` | İngilizce açıklama |

### ConnectionTypeRecord

`/api/address-connection-type/index` referans kaydı.

| Alan | Tip | Varsayılan | Açıklama |
|------|-----|-----------|----------|
| `id` | `str` | — | Bağlantı tipi kodu |
| `tr_title` | `str` | `""` | Türkçe başlık |
| `en_title` | `str` | `""` | İngilizce başlık |

### SourceRecord

`/api/address-source/index` referans kaydı.

| Alan | Tip | Varsayılan | Açıklama |
|------|-----|-----------|----------|
| `id` | `str` | — | Kaynak kodu |
| `tr_title` | `str` | `""` | Türkçe başlık |
| `en_title` | `str` | `""` | İngilizce başlık |

### IncidentRecord

`/api/incident/index` kaydı.

| Alan | Tip | Varsayılan | Açıklama |
|------|-----|-----------|----------|
| `id` | `int` | — | Olay ID'si |
| `title` | `str` | `""` | Başlık |
| `desc` | `str` | `""` | Açıklama |
| `date` | `str` | `""` | Tarih |
| `active` | `bool` | `True` | Aktif durum |
| `slug` | `str` | `""` | URL slug |
| `language` | `str` | `""` | Dil kodu |

### AnnouncementRecord

`/api/announcement/index` kaydı.

| Alan | Tip | Varsayılan | Açıklama |
|------|-----|-----------|----------|
| `id` | `int` | — | Duyuru ID'si |
| `title` | `str` | `""` | Başlık |
| `desc` | `str` | `""` | Açıklama |
| `date` | `str` | `""` | Tarih |
| `active` | `bool` | `True` | Aktif durum |
| `slug` | `str` | `""` | URL slug |
| `language` | `str` | `""` | Dil kodu |

## Hattın Veri Modelleri

### ValidatedIOC

Doğrulamayı geçmiş bir IOC.

| Alan | Tip | Varsayılan | Açıklama |
|------|-----|-----------|----------|
| `raw_url` | `str` | — | Orijinal IOC değeri |
| `ioc_type` | `IOCType` | — | Sınıflandırılmış IOC tipi |
| `desc` | `DescriptionCategory \| None` | `None` | Açıklama kategorisi |
| `source` | `Source \| None` | `None` | Geldiği kaynak |
| `date` | `datetime \| None` | `None` | Gözlem tarihi |
| `criticality_level` | `int` | `10` | Kritiklik (1=en yüksek) |
| `connectiontype` | `ConnectionType \| None` | `None` | Bağlantı tipi |
| `original_id` | `int` | `0` | Orijinal API kayıt ID'si |
| `validation_errors` | `list[str]` | `[]` | Ölümcül olmayan doğrulama notları |

### NormalizedIOC

Küçük harfe dönüştürülmüş, kırpılmış, IDN çözümlenmiş, standart port çıkarılmış bir IOC.

| Alan | Tip | Varsayılan | Açıklama |
|------|-----|-----------|----------|
| `value` | `str` | — | Normalize edilmiş IOC değeri |
| `ioc_type` | `IOCType` | — | Sınıflandırılmış IOC tipi |
| `desc` | `DescriptionCategory \| None` | `None` | Açıklama kategorisi |
| `source` | `Source \| None` | `None` | Geldiği kaynak |
| `date` | `datetime \| None` | `None` | Gözlem tarihi |
| `criticality_level` | `int` | `10` | Kritiklik (1=en yüksek) |
| `connectiontype` | `ConnectionType \| None` | `None` | Bağlantı tipi |
| `original_id` | `int` | `0` | Orijinal API kayıt ID'si |
| `normalization_notes` | `list[str]` | `[]` | Normalizasyon günlüğü |

### ScoredIOC

Kalite / güven puanı eklenmiş bir IOC.

| Alan | Tip | Varsayılan | Açıklama |
|------|-----|-----------|----------|
| `value` | `str` | — | Normalize edilmiş IOC değeri |
| `ioc_type` | `IOCType` | — | Sınıflandırılmış IOC tipi |
| `desc` | `DescriptionCategory \| None` | `None` | Açıklama kategorisi |
| `source` | `Source \| None` | `None` | Geldiği kaynak |
| `date` | `datetime \| None` | `None` | Gözlem tarihi |
| `criticality_level` | `int` | `10` | Kritiklik (1=en yüksek) |
| `connectiontype` | `ConnectionType \| None` | `None` | Bağlantı tipi |
| `original_id` | `int` | `0` | Orijinal API kayıt ID'si |
| `quality_score` | `float` | `0.0` | Güven puanı (0–100) |
| `false_positive_risk` | `str` | `"low"` | Yanlış pozitif risk düzeyi |
| `flags` | `list[str]` | `[]` | Tekilleştirme meta verisi ve kalite imleri |

### PipelineStats

Bir hattı çalıştırma sırasında toplanan istatistikler.

| Alan | Tip | Varsayılan | Açıklama |
|------|-----|-----------|----------|
| `total_fetched` | `int` | `0` | API'den çekilen kayıt sayısı |
| `after_validation` | `int` | `0` | Doğrulamayı geçen kayıt sayısı |
| `after_normalization` | `int` | `0` | Normalizasyon sonrası kayıt sayısı |
| `after_dedup` | `int` | `0` | Tekilleştirme sonrası kayıt sayısı |
| `after_quality` | `int` | `0` | Kalite filtresi sonrası kayıt sayısı |
| `by_type` | `dict[str, int]` | `{}` | IOC tipine göre sayım |
| `by_source` | `dict[str, int]` | `{}` | Kaynağa göre sayım |
| `by_desc` | `dict[str, int]` | `{}` | Açıklama kategorisine göre sayım |
| `by_criticality` | `dict[int, int]` | `{}` | Kritiklik düzeyine göre sayım |
| `validation_rejected` | `int` | `0` | Doğrulama tarafından reddedilen |
| `quality_rejected` | `int` | `0` | Kalite tarafından reddedilen |
| `duplicates_removed` | `int` | `0` | Kaldırılan mükerrer kayıt |
| `fetch_duration_seconds` | `float` | `0.0` | Çekme süresi |
| `pipeline_duration_seconds` | `float` | `0.0` | Toplam hattı süresi |
| `errors` | `list[str]` | `[]` | Hata mesajları |

## İstemci Modelleri

### APIError

SGB API'si 2xx dışı bir yanıt döndürdüğünde oluşan istisna.

```python
class APIError(Exception):
    status_code: int   # HTTP durum kodu
    detail: str        # Hata mesajı
    url: str           # İstek URL'si
```

### AsyncAPIClient

SGB API'si için asenkron HTTP istemcisi. Kimlik doğrulama gerekmez.

| Parametre | Tip | Varsayılan | Açıklama |
|-----------|-----|-----------|----------|
| `base_url` | `str` | `https://siberguvenlik.gov.tr` | API temel URL'si |
| `max_retries` | `int` | `3` | Maksimum yeniden deneme |
| `rate_limit` | `float` | `10.0` | Saniye başına istek |
| `timeout` | `float` | `60.0` | HTTP zaman aşımı (saniye) |

## Tekilleştirici Modelleri

### DeduplicationResult

Skorlanmış IOC listesinin tekilleştirilmesinin sonucu.

| Alan | Tip | Açıklama |
|------|-----|----------|
| `kept` | `list[ScoredIOC]` | Tekilleştirilmiş IOC listesi |
| `removed_count` | `int` | Kaldırılan mükerrer kayıt sayısı |
| `merge_log` | `list[str]` | Birleştirme karar günlüğü |

## Veri Akışı

Hatt veriyi şu model aşamalarından geçirerek dönüştürür:

```
API Yanıtı (PaginatedResponse[AddressRecord])
    → ValidatedIOC[]
    → NormalizedIOC[]
    → ScoredIOC[]
    → DeduplicationResult
    → ScoredIOC[] (nihai, çıktı dosyalarına yazılır)
```
