> **Language / Dil** &nbsp;
> [EN English](#-english) &nbsp;·&nbsp; [TR Türkçe](#-türkçe)

<a id="-english"></a>

# API Analysis

## TC SGB Threat Intelligence API

### Overview

The Turkish National Cyber Security Directorate (T.C. Siber Güvenlik Başkanlığı) provides a REST API for accessing threat intelligence IOC (Indicator of Compromise) data. This API replaced the deprecated XML feed (`url-list.xml`) as of February 2024.

### API Specification

| Property | Value |
|----------|-------|
| **Protocol** | HTTPS |
| **Format** | REST |
| **Spec** | OpenAPI 3.0 |
| **Response Format** | JSON |
| **Authentication** | None required |
| **Rate Limit** | Not documented (conservative: max 10 req/sec) |
| **API Version** | v1.1 (info field only, no versioning scheme) |
| **Base URL** | `https://siberguvenlik.gov.tr` |

### Endpoints

#### 1. IOC List

```
GET /ioc
```

Returns paginated list of IOC records.

**Parameters**:

| Name | Type | Required | Default | Description |
|------|------|----------|---------|-------------|
| `page` | integer | No | 1 | Page number (1-indexed) |
| `per_page` | integer | No | 500 | Records per page (max 9999) |

**Response**:

```json
{
  "data": [
    {
      "id": 12345,
      "type": "domain",
      "value": "malicious-example.com",
      "first_seen": "2025-01-15T10:30:00Z",
      "last_seen": "2025-01-20T14:22:00Z",
      "status": "active"
    }
  ],
  "meta": {
    "total": 483690,
    "page": 1,
    "per_page": 500
  }
}
```

#### 2. IOC Types

```
GET /ioc/types
```

Returns list of available IOC types.

**Response**:

```json
{
  "types": [
    "domain",
    "ip",
    "ip6",
    "ip6net",
    "url"
  ]
}
```

#### 3. IOC by Type

```
GET /ioc/{type}
```

Returns IOC records filtered by type.

**Parameters**:

| Name | Type | Required | Description |
|------|------|----------|-------------|
| `type` | string | Yes | IOC type (domain, ip, ip6, ip6net, url) |
| `page` | integer | No | Page number |
| `per_page` | integer | No | Records per page |

#### 4. Statistics

```
GET /stats
```

Returns aggregate statistics about the IOC dataset.

**Response**:

```json
{
  "total": 483690,
  "by_type": {
    "domain": 125000,
    "ip": 98000,
    "ip6": 45000,
    "ip6net": 15000,
    "url": 200690
  },
  "last_updated": "2025-01-20T14:22:00Z"
}
```

#### 5. Health Check

```
GET /health
```

Returns API health status.

**Response**:

```json
{
  "status": "ok",
  "version": "1.1"
}
```

### Pagination

The API uses offset-based pagination:

```
GET /ioc?page=1&per_page=500    # First page
GET /ioc?page=2&per_page=500    # Second page
GET /ioc?page=968&per_page=500  # Last page (483,690 records)
```

**Pagination Limits**:

| Parameter | Min | Max | Default |
|-----------|-----|-----|---------|
| `page` | 1 | 968 | 1 |
| `per_page` | 1 | 9999 | 500 |

**Total Pages Calculation**:

```
total_pages = ceil(total_records / per_page)
            = ceil(483,690 / 500)
            = 968 pages
```

### Data Volume

| Metric | Value |
|--------|-------|
| Total IOC records | ~483,690 |
| Average record size | ~200 bytes |
| Total dataset size | ~97 MB (raw JSON) |
| Pages at per_page=500 | ~968 |
| API calls for full fetch | ~968 |

### IOC Types Distribution (Estimated)

```
+---------------------------------------------------+
|  IOC Type Distribution                            |
+---------------------------------------------------+
|                                                   |
|  url     ████████████████████████████  41.5%      |
|  domain  ████████████████████          25.8%      |
|  ip      ████████████████              20.3%      |
|  ip6     ████████                       9.3%      |
|  ip6net  ███                            3.1%      |
|                                                   |
+---------------------------------------------------+
```

### HTTP Headers

**Request Headers** (sent by client):

```
User-Agent: tc-sgb/0.1.0.0
Accept: application/json
Connection: keep-alive
```

**Response Headers**:

```
Content-Type: application/json
X-RateLimit-Limit: (not present)
X-RateLimit-Remaining: (not present)
X-RateLimit-Reset: (not present)
Cache-Control: no-cache
```

### Caching Behavior

| Aspect | Status |
|--------|--------|
| ETag | Not supported |
| Last-Modified | Not supported |
| If-None-Match | Not supported |
| If-Modified-Since | Not supported |
| Cache-Control | no-cache |
| Incremental Sync | Not available |

**Implication**: Full fetch required on every run. No delta/incremental sync mechanism exists. The system must download the entire dataset each time.

### Error Responses

```json
// 400 Bad Request
{
  "error": "invalid_parameter",
  "message": "per_page must be between 1 and 9999"
}

// 404 Not Found
{
  "error": "not_found",
  "message": "Resource not found"
}

// 429 Too Many Requests (theoretical, not documented)
{
  "error": "rate_limited",
  "message": "Too many requests"
}

// 500 Internal Server Error
{
  "error": "internal_error",
  "message": "An unexpected error occurred"
}
```

### Rate Limiting Strategy

Since no rate limit is documented, we apply conservative defaults:

```python
RATE_LIMIT_CONFIG = {
    "max_concurrent_requests": 5,  # Simultaneous connections
    "min_request_interval": 0.1,  # 100ms between requests
    "max_requests_per_second": 10,  # Hard ceiling
    "backoff_base_delay": 0.5,  # Initial retry delay
    "backoff_max_delay": 30.0,  # Maximum retry delay
    "backoff_multiplier": 2.0,  # Exponential multiplier
    "max_retries": 3,  # Maximum retry attempts
}
```

### No Incremental Sync

```
Current Approach (Full Fetch):
+---------------------------------------------------+
|  Run 1: Fetch all 483,690 records                 |
|  Run 2: Fetch all 483,690 records (again)         |
|  Run 3: Fetch all 483,690 records (again)         |
+---------------------------------------------------+

Ideal Approach (Incremental - Not Available):
+---------------------------------------------------+
|  Run 1: Fetch all 483,690 records                 |
|  Run 2: Fetch new/changed since last_run          |
|  Run 3: Fetch new/changed since last_run          |
+---------------------------------------------------+
```

The absence of ETag, Last-Modified, or any change-tracking mechanism means:
- Every pipeline run downloads the full dataset
- Local deduplication against previous runs is essential
- Storage of previous hashes enables client-side incremental detection
- Network and processing costs scale linearly with dataset size

### Terms of Service

The API is governed by the legal warnings published at:
- **URL**: https://siberguvenlik.gov.tr/yasal-uyarilar
- **Content**: Protected under Turkish Copyright Law 5846
- **Redistribution**: Prohibited without written permission
- **Modification**: Prohibited without source attribution
- **Integration**: Explicitly permitted for security systems (firewall, SIEM, URL filtering, DNS)

See [License-Analysis](License-Analysis) and [Legal-Notices](Legal-Notices) for full details.

### Deprecated Endpoints

| Endpoint | Status | Replacement |
|----------|--------|-------------|
| `url-list.xml` | Deprecated Feb 2024 | REST API |
| `url-list.txt` | Still published | REST API (recommended) |

### Integration Compatibility

The API is explicitly designed for integration with:

- **Firewall systems** — Block malicious IPs and domains
- **SIEM platforms** — Correlate IOCs with log data
- **URL filtering** — Block malicious URLs
- **DNS systems** — Sinkhole malicious domains

Target platforms include:
- Palo Alto Networks
- Cisco Firepower
- Fortinet FortiGate
- Splunk Enterprise Security
- IBM QRadar
- Elastic Security
- Open-source tools (Suricata, Zeek, Security Onion)

<a id="-türkçe"></a>

# API Analizi

## TC SGB Tehdit İstihbaratı API'si

### Genel Bakış

Türk Siber Güvenlik Başkanlığı (T.C. Siber Güvenlik Başkanlığı), tehdit istihbaratı IOC (Tehdit Göstergesi) verilerine erişim sağlayan bir REST API sunmaktadır. Bu API, Şubat 2024'ten itibaren kullanımdan kaldırılan XML beslemesinin (`url-list.xml`) yerini almıştır.

### API Özellikleri

| Özellik | Değer |
|---------|-------|
| **Protokol** | HTTPS |
| **Format** | REST |
| **Özellikler** | OpenAPI 3.0 |
| **Yanıt Formatı** | JSON |
| **Kimlik Doğrulama** | Gerekmez |
| **Hız Sınırı** | Belgelenmemiş (muhafazakar: maks. 10 istek/sn) |
| **API Sürümü** | v1.1 (yalnızca bilgi alanı, sürümleme şeması yok) |
| **Temel URL** | `https://siberguvenlik.gov.tr` |

### Uç Noktalar

#### 1. IOC Listesi

```
GET /ioc
```

Sayfalanmış IOC kayıtları listesini döndürür.

**Parametreler**:

| Ad | Tür | Gerekli | Varsayılan | Açıklama |
|----|------|---------|------------|----------|
| `page` | tamsayı | Hayır | 1 | Sayfa numarası (1'den başlar) |
| `per_page` | tamsayı | Hayır | 500 | Sayfa başına kayıt (maks. 9999) |

**Yanıt**:

```json
{
  "data": [
    {
      "id": 12345,
      "type": "domain",
      "value": "malicious-example.com",
      "first_seen": "2025-01-15T10:30:00Z",
      "last_seen": "2025-01-20T14:22:00Z",
      "status": "active"
    }
  ],
  "meta": {
    "total": 483690,
    "page": 1,
    "per_page": 500
  }
}
```

#### 2. IOC Türleri

```
GET /ioc/types
```

Mevcut IOC türlerinin listesini döndürür.

**Yanıt**:

```json
{
  "types": [
    "domain",
    "ip",
    "ip6",
    "ip6net",
    "url"
  ]
}
```

#### 3. Türe Göre IOC

```
GET /ioc/{type}
```

Türe göre filtrelenmiş IOC kayıtlarını döndürür.

**Parametreler**:

| Ad | Tür | Gerekli | Açıklama |
|----|------|---------|----------|
| `type` | dize | Evet | IOC türü (domain, ip, ip6, ip6net, url) |
| `page` | tamsayı | Hayır | Sayfa numarası |
| `per_page` | tamsayı | Hayır | Sayfa başına kayıt |

#### 4. İstatistikler

```
GET /stats
```

IOC veri kümesi hakkında toplu istatistikleri döndürür.

**Yanıt**:

```json
{
  "total": 483690,
  "by_type": {
    "domain": 125000,
    "ip": 98000,
    "ip6": 45000,
    "ip6net": 15000,
    "url": 200690
  },
  "last_updated": "2025-01-20T14:22:00Z"
}
```

#### 5. Sağlık Kontrolü

```
GET /health
```

API sağlık durumunu döndürür.

**Yanıt**:

```json
{
  "status": "ok",
  "version": "1.1"
}
```

### Sayfalama

API, ofset tabanlı sayfalama kullanır:

```
GET /ioc?page=1&per_page=500    # İlk sayfa
GET /ioc?page=2&per_page=500    # İkinci sayfa
GET /ioc?page=968&per_page=500  # Son sayfa (483.690 kayıt)
```

**Sayfalama Sınırları**:

| Parametre | Min | Maks | Varsayılan |
|-----------|-----|------|------------|
| `page` | 1 | 968 | 1 |
| `per_page` | 1 | 9999 | 500 |

**Toplam Sayfa Hesaplaması**:

```
total_pages = ceil(toplam_kayit / sayfa_basi)
            = ceil(483.690 / 500)
            = 968 sayfa
```

### Veri Hacmi

| Metrik | Değer |
|--------|-------|
| Toplam IOC kaydı | ~483.690 |
| Ortalama kayıt boyutu | ~200 bayt |
| Toplam veri kümesi boyutu | ~97 MB (ham JSON) |
| per_page=500 ile sayfa sayısı | ~968 |
| Tam çekim için API çağrıları | ~968 |

### IOC Tür Dağılımı (Tahmini)

```
+---------------------------------------------------+
|  IOC Tür Dağılımı                                 |
+---------------------------------------------------+
|                                                   |
|  url     ████████████████████████████  41.5%      |
|  domain  ████████████████████          25.8%      |
|  ip      ████████████████              20.3%      |
|  ip6     ████████                       9.3%      |
|  ip6net  ███                            3.1%      |
|                                                   |
+---------------------------------------------------+
```

### HTTP Başlıkları

**İstek Başlıkları** (istemci tarafından gönderilir):

```
User-Agent: tc-sgb/0.1.0.0
Accept: application/json
Connection: keep-alive
```

**Yanıt Başlıkları**:

```
Content-Type: application/json
X-RateLimit-Limit: (mevcut değil)
X-RateLimit-Remaining: (mevcut değil)
X-RateLimit-Reset: (mevcut değil)
Cache-Control: no-cache
```

### Önbellekleme Davranışı

| Yön | Durum |
|-----|-------|
| ETag | Desteklenmiyor |
| Last-Modified | Desteklenmiyor |
| If-None-Match | Desteklenmiyor |
| If-Modified-Since | Desteklenmiyor |
| Cache-Control | no-cache |
| Artımlı Eşitleme | Mevcut değil |

**Sonuç**: Her çalıştırmada tam çekim gereklidir. Delta/artımlı eşitleme mekanizması yoktur. Sistem her seferinde tüm veri kümesini indirmelidir.

### Hata Yanıtları

```json
// 400 Hatalı İstek
{
  "error": "invalid_parameter",
  "message": "per_page must be between 1 and 9999"
}

// 404 Bulunamadı
{
  "error": "not_found",
  "message": "Resource not found"
}

// 429 Çok Fazla İstek (teorik, belgelenmemiş)
{
  "error": "rate_limited",
  "message": "Too many requests"
}

// 500 Sunucu İç Hatası
{
  "error": "internal_error",
  "message": "An unexpected error occurred"
}
```

### Hız Sınırı Stratejisi

Hız sınırı belgelenmediğinden, muhafazakar varsayılanlar uyguluyoruz:

```python
RATE_LIMIT_CONFIG = {
    "max_concurrent_requests": 5,  # Eşzamanlı bağlantılar
    "min_request_interval": 0.1,  # İstekler arası 100ms
    "max_requests_per_second": 10,  # Sert tavan
    "backoff_base_delay": 0.5,  # İlk yeniden deneme gecikmesi
    "backoff_max_delay": 30.0,  # Maksimum yeniden deneme gecikmesi
    "backoff_multiplier": 2.0,  # Üstel çarpan
    "max_retries": 3,  # Maksimum yeniden deneme sayısı
}
```

### Artımlı Eşitleme Yok

```
Mevcut Yaklaşım (Tam Çekim):
+---------------------------------------------------+
|  Çalıştırma 1: Tüm 483.690 kaydı çek              |
|  Çalıştırma 2: Tüm 483.690 kaydı çek (tekrar)     |
|  Çalıştırma 3: Tüm 483.690 kaydı çek (tekrar)     |
+---------------------------------------------------+

İdeal Yaklaşım (Artımlı - Mevcut Değil):
+---------------------------------------------------+
|  Çalıştırma 1: Tüm 483.690 kaydı çek              |
|  Çalıştırma 2: Son çalıştırma 이후 yeni/değişenleri çek |
|  Çalıştırma 3: Son çalıştırma 이후 yeni/değişenleri çek |
+---------------------------------------------------+
```

ETag, Last-Modified veya herhangi bir değişiklik izleme mekanizmasının olmaması şunları ima eder:
- Her boru hattı çalıştırması tam veri kümesini indirir
- Önceki çalıştırmalara karşı yerel tekilleştirme gereklidir
- Önceki özetlerin saklanması istemci tarafında artımlı tespiti sağlar
- Ağ ve işleme maliyetleri veri kümesi boyutuyla doğrusal olarak ölçeklenir

### Hizmet Şartları

API aşağıdaki adreste yayımlanan yasal uyarılar tarafından yönetilmektedir:
- **URL**: https://siberguvenlik.gov.tr/yasal-uyarilar
- **İçerik**: Türk Telif Hakkı Yasası 5846 kapsamında korunmaktadır
- **Yeniden dağıtma**: Yazılı izin olmadan yasaktır
- **Değiştirme**: Kaynak ataması olmadan yasaktır
- **Entegrasyon**: Güvenlik sistemleri için açıkça izin verilmiştir (güvenlik duvarı, SIEM, URL filtreleme, DNS)

Tam ayrıntılar için [License-Analysis](License-Analysis#-türkçe) ve [Legal-Notices](Legal-Notices#-türkçe) dosyalarına bakın.

### Kullanımdan Kaldırılan Uç Noktalar

| Uç Nokta | Durum | Yerine Geçen |
|----------|-------|-------------|
| `url-list.xml` | Şubat 2024'te kullanımdan kaldırıldı | REST API |
| `url-list.txt` | Hâlâ yayımlanıyor | REST API (önerilen) |

### Entegrasyon Uyumluluğu

API açıkça aşağıdaki entegrasyonlar için tasarlanmıştır:

- **Güvenlik duvarı sistemleri** — Kötü amaçlı IP'leri ve alan adlarını engeller
- **SIEM platformları** — IOC'leri günlük verileriyle korele eder
- **URL filtreleme** — Kötü amaçlı URL'leri engeller
- **DNS sistemleri** — Kötü amaçlı alan adlarını sinkhole'a yönlendirir

Hedef platformlar şunları içerir:
- Palo Alto Networks
- Cisco Firepower
- Fortinet FortiGate
- Splunk Enterprise Security
- IBM QRadar
- Elastic Security
- Açık kaynak araçlar (Suricata, Zeek, Security Onion)
