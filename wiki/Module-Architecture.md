> **Language / Dil** &nbsp;
> [EN English](#-english) &nbsp;·&nbsp; [TR Türkçe](#-türkçe)

<a id="-english"></a>

# Module Architecture

## Module Dependency Graph

```
+=====================================================================+
|                     Module Dependency Graph                          |
+=====================================================================+

                          +-----------+
                          | pipeline  |
                          |    .py    |
                          +-----+-----+
                                |
            +-------------------+-------------------+
            |                   |                   |
            v                   v                   v
     +-----------+       +-----------+       +-----------+
     |  client   |       | validator |       |  outputs  |
     |    .py    |       |    .py    |       |    .py    |
     +-----+-----+       +-----+-----+       +-----+-----+
           |                   |                   |
           v                   v                   v
     +-----------+       +-----------+       +-----------+
     |  models   |       | normalizer|       |  quality  |
     |    .py    |       |    .py    |       |    .py    |
     +-----------+       +-----+-----+       +-----------+
                                 |
                                 v
                          +-----------+
                          | deduplicator|
                          |    .py     |
                          +-----------+
```

## Module Specifications

### 1. `client.py` — API Client

**Responsibility**: HTTP communication with the TC SGB API.

```python
class SGBAPIClient:
    """Async HTTP client for TC SGB threat intelligence API."""

    def __init__(self, base_url: str, config: ClientConfig) -> None: ...

    async def fetch_page(self, page: int, per_page: int) -> APIResponse:
        """Fetch a single page of IOC records."""

    async def fetch_all(self) -> AsyncGenerator[list[IOCRecord], None]:
        """Fetch all pages with bounded concurrency."""

    async def get_total_count(self) -> int:
        """Query total record count for pagination calculation."""

    async def health_check(self) -> bool:
        """Verify API endpoint is reachable."""
```

**Key Behaviors**:
- Uses `httpx.AsyncClient` with connection pooling
- Bounded concurrency via `asyncio.Semaphore`
- Exponential backoff on rate limit (429) and server errors (503)
- Configurable timeout per request (default 30s)
- User-Agent header identifies the client
- No authentication required

**Configuration**:
```python
@dataclass
class ClientConfig:
    base_url: str = "https://threatintel.sgbsg.gov.tr/api/v1"
    max_concurrent: int = 5
    request_timeout: float = 30.0
    retry_max: int = 3
    retry_base_delay: float = 0.5
    per_page: int = 500
    user_agent: str = "tc-sgb-api-list/{version}"
```

---

### 2. `models.py` — Data Models

**Responsibility**: Pydantic models, enums, type definitions, serialization schemas.

```python
class IOCType(str, Enum):
    DOMAIN = "domain"
    IP = "ip"
    IP6 = "ip6"
    IP6NET = "ip6net"
    URL = "url"


class IOCStatus(str, Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    UNKNOWN = "unknown"


class IOCRecord(BaseModel):
    id: int
    type: IOCType
    value: str
    first_seen: datetime
    last_seen: datetime
    status: IOCStatus


class APIResponse(BaseModel):
    data: list[IOCRecord]
    meta: PaginationMeta


class PaginationMeta(BaseModel):
    total: int
    page: int
    per_page: int
```

**Key Behaviors**:
- Strict Pydantic v2 validation with `model_config = ConfigDict(strict=True)`
- Custom validators for IOC value formats
- Serialization aliases for API field names
- Frozen models (immutable after creation)
- Custom JSON encoders for datetime handling

---

### 3. `validator.py` — Data Validator

**Responsibility**: Schema validation, type checking, null detection, format verification.

```python
class IOCValidator:
    """Multi-stage IOC record validator."""

    def validate_record(self, record: IOCRecord) -> ValidationResult:
        """Run all validation checks on a single record."""

    def validate_batch(self, records: list[IOCRecord]) -> BatchValidationResult:
        """Validate a batch of records with aggregate statistics."""

    def _check_required_fields(self, record: IOCRecord) -> list[ValidationError]: ...
    def _check_type_enum(self, record: IOCRecord) -> list[ValidationError]: ...
    def _check_value_format(self, record: IOCRecord) -> list[ValidationError]: ...
    def _check_date_range(self, record: IOCRecord) -> list[ValidationError]: ...
    def _check_value_length(self, record: IOCRecord) -> list[ValidationError]: ...
    def _check_control_chars(self, record: IOCRecord) -> list[ValidationError]: ...
    def _check_encoding(self, record: IOCRecord) -> list[ValidationError]: ...
    def _check_self_reference(self, record: IOCRecord) -> list[ValidationError]: ...
```

**Validation Rules**:

| Rule ID | Check | Severity | Action |
|---------|-------|----------|--------|
| V001 | Required fields present | CRITICAL | Reject |
| V002 | ID is positive integer | CRITICAL | Reject |
| V003 | Type in enum set | CRITICAL | Reject |
| V004 | Value non-empty string | CRITICAL | Reject |
| V005 | Value length <= 2048 | HIGH | Reject |
| V006 | No null bytes | HIGH | Reject |
| V007 | No control chars | MEDIUM | Strip/Reject |
| V008 | Date format valid | HIGH | Reject |
| V009 | Date range logical | MEDIUM | Flag |
| V010 | Status in valid set | LOW | Map default |
| V011 | Value encoding valid | MEDIUM | Reject |
| V012 | Self-reference check | LOW | Flag |

---

### 4. `normalizer.py` — Data Normalizer

**Responsibility**: Format canonicalization, type-specific transformations, metadata standardization.

```python
class IOCNormalizer:
    """Type-aware IOC record normalizer."""

    def normalize(self, record: IOCRecord) -> NormalizedIOC:
        """Apply type-specific normalization."""

    def normalize_batch(self, records: list[IOCRecord]) -> list[NormalizedIOC]:
        """Normalize a batch of records."""

    def _normalize_domain(self, value: str) -> str: ...
    def _normalize_ip(self, value: str) -> str: ...
    def _normalize_ip6(self, value: str) -> str: ...
    def _normalize_ip6net(self, value: str) -> str: ...
    def _normalize_url(self, value: str) -> str: ...
    def _normalize_dates(self, record: IOCRecord) -> tuple[datetime, datetime]: ...
```

**Normalization Rules**:

| IOC Type | Transform | Example Input | Example Output |
|----------|-----------|---------------|----------------|
| domain | Lowercase, trim, punycode | `Evil.COM ` | `evil.com` |
| domain | Remove trailing dot | `evil.com.` | `evil.com` |
| ip | Validate, strip whitespace | ` 192.168.1.1 ` | `192.168.1.1` |
| ip6 | Compress to shortest form | `2001:0db8:...` | `2001:db8::1` |
| ip6net | Validate CIDR, normalize | `2001:db8::/32` | `2001:db8::/32` |
| url | Lowercase scheme/host | `HTTP://EVIL.COM/path` | `http://evil.com/path` |
| url | Remove default ports | `http://evil.com:80/` | `http://evil.com/` |
| url | Remove fragments | `http://evil.com/#track` | `http://evil.com/` |
| url | Remove tracking params | `http://evil.com/?utm_source=x` | `http://evil.com/` |
| all | ISO 8601 dates | `2025-01-15 10:30` | `2025-01-15T10:30:00Z` |

---

### 5. `deduplicator.py` — Deduplication Engine

**Responsibility**: Identify and merge duplicate IOC records across the dataset.

```python
class IOCDeduplicator:
    """Multi-strategy IOC deduplication engine."""

    def __init__(self, config: DedupConfig) -> None: ...

    def deduplicate(self, records: list[NormalizedIOC]) -> DedupResult:
        """Remove duplicates using configured strategies."""

    def _exact_hash(self, record: NormalizedIOC) -> str: ...
    def _semantic_key(self, record: NormalizedIOC) -> str: ...
    def _subdomain_key(self, record: NormalizedIOC) -> str: ...
    def _merge_records(self, records: list[NormalizedIOC]) -> NormalizedIOC: ...
```

**Deduplication Strategies**:

```python
@dataclass
class DedupConfig:
    exact_match: bool = True
    semantic_match: bool = True
    subdomain_dedup: bool = False
    subdomain_depth: int = 2
    case_sensitive: bool = False
```

**Merge Rules**:
- `first_seen`: Earliest across duplicates
- `last_seen`: Latest across duplicates
- `status`: Union of all statuses (if any active, result is active)
- `id`: Lowest id (primary record)
- `source_page`: All source pages recorded

---

### 6. `quality.py` — Quality Assurance Engine

**Responsibility**: Statistical analysis, false positive detection, quality scoring, reporting.

```python
class QualityEngine:
    """IOC dataset quality assessment and reporting."""

    def __init__(self, config: QualityConfig) -> None: ...

    def analyze(self, records: list[NormalizedIOC]) -> QualityReport:
        """Run full quality analysis on dataset."""

    def _compute_statistics(self, records: list) -> DatasetStatistics: ...
    def _check_false_positives(self, records: list) -> list[FPFlag]: ...
    def _score_records(self, records: list) -> list[ScoredIOC]: ...
    def _detect_anomalies(self, records: list) -> list[Anomaly]: ...
    def _generate_report(self, ...) -> QualityReport: ...
```

**Quality Metrics**:

| Metric | Description | Target |
|--------|-------------|--------|
| Schema Compliance | % records passing validation | 100% |
| Deduplication Rate | % duplicates removed | 5-20% |
| False Positive Rate | % flagged as likely benign | < 5% |
| Data Freshness | Avg age of last_seen | < 90 days |
| Field Completeness | % non-null optional fields | > 95% |
| Format Consistency | % conforming to type rules | 100% |
| Overall Quality Score | Weighted composite score | > 0.90 |

---

### 7. `outputs.py` — Output Engine

**Responsibility**: Format conversion, file generation, output packaging.

```python
class OutputEngine:
    """Multi-format IOC output generator."""

    def __init__(self, config: OutputConfig) -> None: ...

    def generate_all(self, records: list[NormalizedIOC], output_dir: Path) -> list[OutputFile]:
        """Generate all configured output formats."""

    def generate_json(self, records, path) -> OutputFile: ...
    def generate_stix(self, records, path) -> OutputFile: ...
    def generate_csv(self, records, path) -> OutputFile: ...
    def generate_misp(self, records, path) -> OutputFile: ...
    def generate_openioc(self, records, path) -> OutputFile: ...
    def generate_sigma(self, records, path) -> OutputFile: ...
    def generate_yara(self, records, path) -> OutputFile: ...
    def generate_cef(self, records, path) -> OutputFile: ...
    def generate_leef(self, records, path) -> OutputFile: ...
    def generate_syslog(self, records, path) -> OutputFile: ...
    def generate_html(self, records, path) -> OutputFile: ...
    def generate_markdown(self, records, path) -> OutputFile: ...
    def generate_pdf(self, records, path) -> OutputFile: ...
    def generate_splunk(self, records, path) -> OutputFile: ...
    def generate_qradar(self, records, path) -> OutputFile: ...
    def generate_elastic(self, records, path) -> OutputFile: ...
    def generate_grafana(self, records, path) -> OutputFile: ...
```

**Output Format Details**:

| Format | MIME Type | Encoding | Purpose |
|--------|-----------|----------|---------|
| JSON | application/json | UTF-8 | General interchange |
| STIX 2.1 | application/stix+json | UTF-8 | Standardized threat intel |
| CSV | text/csv | UTF-8 | Spreadsheet import |
| MISP | application/json | UTF-8 | MISP platform import |
| OpenIOC | application/xml | UTF-8 | FireEye/Trellix |
| Sigma | application/yaml | UTF-8 | SIEM detection rules |
| YARA | text/plain | UTF-8 | Malware detection |
| CEF | text/plain | UTF-8 | ArcSight/syslog |
| LEEF | text/plain | UTF-8 | IBM QRadar |
| Syslog | text/plain | UTF-8 | Generic SIEM |
| HTML | text/html | UTF-8 | Human-readable report |
| Markdown | text/markdown | UTF-8 | Documentation |
| PDF | application/pdf | binary | Formal reports |
| Splunk | application/splunk | UTF-8 | Splunk import |
| QRadar | application/json | UTF-8 | QRadar import |
| Elastic NDJSON | application/x-ndjson | UTF-8 | Elasticsearch bulk |
| Grafana | application/json | UTF-8 | Dashboard datasource |

---

### 8. `pipeline.py` — Pipeline Orchestrator

**Responsibility**: End-to-end orchestration, stage management, error handling, logging.

```python
class ThreatIntelPipeline:
    """End-to-end threat intelligence processing pipeline."""

    def __init__(self, config: PipelineConfig) -> None: ...

    async def run(self) -> PipelineResult:
        """Execute the full pipeline from fetch to publish."""

    async def _fetch_stage(self) -> list[RawIOC]: ...
    def _validate_stage(self, records) -> tuple[list, list]: ...
    def _normalize_stage(self, records) -> list[NormalizedIOC]: ...
    def _dedup_stage(self, records) -> DedupResult: ...
    def _quality_stage(self, records) -> QualityReport: ...
    def _output_stage(self, records) -> list[OutputFile]: ...
    def _publish_stage(self, outputs) -> PublishResult: ...

    def _log_stage(self, stage: str, result: Any) -> None: ...
    def _handle_error(self, stage: str, error: Exception) -> PipelineError: ...
```

**Pipeline Configuration**:

```python
@dataclass
class PipelineConfig:
    api: ClientConfig = field(default_factory=ClientConfig)
    validation: ValidationConfig = field(default_factory=ValidationConfig)
    normalization: NormalizationConfig = field(default_factory=NormalizationConfig)
    dedup: DedupConfig = field(default_factory=DedupConfig)
    quality: QualityConfig = field(default_factory=QualityConfig)
    output: OutputConfig = field(default_factory=OutputConfig)
    publish: PublishConfig = field(default_factory=PublishConfig)
    logging: LoggingConfig = field(default_factory=LoggingConfig)
```

## Module Interaction Sequence

```
+=====================================================================+
|                  Pipeline Execution Sequence                         |
+=====================================================================+

  pipeline.run()
      |
      +----> client.fetch_all()
      |        |
      |        +----> client.fetch_page(N)  [concurrent]
      |        |        |
      |        |        +----> httpx.AsyncClient.get()
      |        |        |
      |        |        +----> models.APIResponse(**response.json())
      |        |        |
      |        |        +----> validator.validate_record()
      |        |        |
      |        |        +----> Returns IOCRecord list
      |        |
      |        +----> Collects all pages
      |        +----> Returns raw records
      |
      +----> validator.validate_batch(records)
      |        |
      |        +----> For each record:
      |        |        _check_required_fields()
      |        |        _check_type_enum()
      |        |        _check_value_format()
      |        |        _check_date_range()
      |        |        _check_value_length()
      |        |        _check_control_chars()
      |        |        _check_encoding()
      |        |        _check_self_reference()
      |        |
      |        +----> Returns BatchValidationResult
      |
      +----> normalizer.normalize_batch(valid_records)
      |        |
      |        +----> For each record:
      |        |        _normalize_domain/ip/ip6/ip6net/url()
      |        |        _normalize_dates()
      |        |
      |        +----> Returns NormalizedIOC list
      |
      +----> deduplicator.deduplicate(normalized_records)
      |        |
      |        +----> _exact_hash() for each record
      |        +----> _semantic_key() for each record
      |        +----> _subdomain_key() if enabled
      |        +----> _merge_records() for duplicates
      |        +----> Returns DedupResult
      |
      +----> quality.analyze(unique_records)
      |        |
      |        +----> _compute_statistics()
      |        +----> _check_false_positives()
      |        +----> _score_records()
      |        +----> _detect_anomalies()
      |        +----> Returns QualityReport
      |
      +----> outputs.generate_all(verified_records)
      |        |
      |        +----> generate_json/stix/csv/misp/...
      |        +----> Returns list[OutputFile]
      |
      +----> Returns PipelineResult
```

## Error Propagation

```
+=====================================================================+
|                     Error Propagation Model                          |
+=====================================================================+

  Module Exception          Pipeline Handling
  +------------------+     +---------------------------+
  | APIError         | --> | Retry with backoff        |
  | ValidationError  | --> | Log + skip record         |
  | NormalizationErr | --> | Log + skip record         |
  | DedupError       | --> | Log + keep both records   |
  | QualityError     | --> | Log + advisory flag       |
  | OutputError      | --> | Retry + fallback format   |
  | PublishError     | --> | Log + local save only     |
  +------------------+     +---------------------------+
```

<a id="-türkçe"></a>

# Modül Mimarisi

## Modül Bağımlılık Grafiği

```
+=====================================================================+
|                     Module Dependency Graph                          |
+=====================================================================+

                          +-----------+
                          | pipeline  |
                          |    .py    |
                          +-----+-----+
                                |
            +-------------------+-------------------+
            |                   |                   |
            v                   v                   v
     +-----------+       +-----------+       +-----------+
     |  client   |       | validator |       |  outputs  |
     |    .py    |       |    .py    |       |    .py    |
     +-----+-----+       +-----+-----+       +-----+-----+
           |                   |                   |
           v                   v                   v
     +-----------+       +-----------+       +-----------+
     |  models   |       | normalizer|       |  quality  |
     |    .py    |       |    .py    |       |    .py    |
     +-----------+       +-----+-----+       +-----------+
                                 |
                                 v
                          +-----------+
                          | deduplicator|
                          |    .py     |
                          +-----------+
```

## Modül Özellikleri

### 1. `client.py` — API İstemcisi

**Sorumluluk**: TC SGB API'siyle HTTP iletişimi.

```python
class SGBAPIClient:
    """Async HTTP client for TC SGB threat intelligence API."""

    def __init__(self, base_url: str, config: ClientConfig) -> None: ...

    async def fetch_page(self, page: int, per_page: int) -> APIResponse:
        """Fetch a single page of IOC records."""

    async def fetch_all(self) -> AsyncGenerator[list[IOCRecord], None]:
        """Fetch all pages with bounded concurrency."""

    async def get_total_count(self) -> int:
        """Query total record count for pagination calculation."""

    async def health_check(self) -> bool:
        """Verify API endpoint is reachable."""
```

**Ana Davranışlar**:
- Bağlantı havuzlamalı `httpx.AsyncClient` kullanır
- `asyncio.Semaphore` ile sınırlı eşzamanlılık
- Hız sınırı (429) ve sunucu hatalarında (503) üstel geri çekilme
- İstek başına yapılandırılabilir zaman aşımı (varsayılan 30s)
- User-Agent başlığı istemciyi tanımlar
- Kimlik doğrulama gerektirmez

**Yapılandırma**:
```python
@dataclass
class ClientConfig:
    base_url: str = "https://threatintel.sgbsg.gov.tr/api/v1"
    max_concurrent: int = 5
    request_timeout: float = 30.0
    retry_max: int = 3
    retry_base_delay: float = 0.5
    per_page: int = 500
    user_agent: str = "tc-sgb-api-list/{version}"
```

---

### 2. `models.py` — Veri Modelleri

**Sorumluluk**: Pydantic modelleri, numaralandırmaları, tür tanımlamaları, serializasyon şemaları.

```python
class IOCType(str, Enum):
    DOMAIN = "domain"
    IP = "ip"
    IP6 = "ip6"
    IP6NET = "ip6net"
    URL = "url"


class IOCStatus(str, Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    UNKNOWN = "unknown"


class IOCRecord(BaseModel):
    id: int
    type: IOCType
    value: str
    first_seen: datetime
    last_seen: datetime
    status: IOCStatus


class APIResponse(BaseModel):
    data: list[IOCRecord]
    meta: PaginationMeta


class PaginationMeta(BaseModel):
    total: int
    page: int
    per_page: int
```

**Ana Davranışlar**:
- `model_config = ConfigDict(strict=True)` ile katı Pydantic v2 doğrulaması
- IOC değer formatları için özel doğrulayıcılar
- API alan adları için serializasyon takma adları
- Donmuş modeller (oluşturma sonrası değişmez)
- Tarih/saat işlemi için özel JSON kodlayıcıları

---

### 3. `validator.py` — Veri Doğrulayıcı

**Sorumluluk**: Şema doğrulama, tür kontrolü, boş değer algılama, format doğrulama.

```python
class IOCValidator:
    """Multi-stage IOC record validator."""

    def validate_record(self, record: IOCRecord) -> ValidationResult:
        """Run all validation checks on a single record."""

    def validate_batch(self, records: list[IOCRecord]) -> BatchValidationResult:
        """Validate a batch of records with aggregate statistics."""

    def _check_required_fields(self, record: IOCRecord) -> list[ValidationError]: ...
    def _check_type_enum(self, record: IOCRecord) -> list[ValidationError]: ...
    def _check_value_format(self, record: IOCRecord) -> list[ValidationError]: ...
    def _check_date_range(self, record: IOCRecord) -> list[ValidationError]: ...
    def _check_value_length(self, record: IOCRecord) -> list[ValidationError]: ...
    def _check_control_chars(self, record: IOCRecord) -> list[ValidationError]: ...
    def _check_encoding(self, record: IOCRecord) -> list[ValidationError]: ...
    def _check_self_reference(self, record: IOCRecord) -> list[ValidationError]: ...
```

**Doğrulama Kuralları**:

| Kural ID | Kontrol | Öncelik | Aksiyon |
|----------|---------|---------|---------|
| V001 | Zorunlu alanlar mevcut | KRİTİK | Reddet |
| V002 | ID pozitif tam sayı | KRİTİK | Reddet |
| V003 | Tür küme içinde | KRİTİK | Reddet |
| V004 | Değer boş olmayan dize | KRİTİK | Reddet |
| V005 | Değer uzunluğu <= 2048 | YÜKSEK | Reddet |
| V006 | Null baytı yok | YÜKSEK | Reddet |
| V007 | Kontrol karakteri yok | ORTA | Temizle/Reddet |
| V008 | Tarih formatı geçerli | YÜKSEK | Reddet |
| V009 | Tarih aralığı mantıklı | ORTA | İşaretle |
| V010 | Durum geçerli kümede | DÜŞÜK | Varsayılan eşle |
| V011 | Değer kodlaması geçerli | ORTA | Reddet |
| V012 | Kendine referans kontrolü | DÜŞÜK | İşaretle |

---

### 4. `normalizer.py` — Veri Normalleştirici

**Sorumluluk**: Format kanonikleştirme, türe özgü dönüştürmeler, meta veri standartlaştırma.

```python
class IOCNormalizer:
    """Type-aware IOC record normalizer."""

    def normalize(self, record: IOCRecord) -> NormalizedIOC:
        """Apply type-specific normalization."""

    def normalize_batch(self, records: list[IOCRecord]) -> list[NormalizedIOC]:
        """Normalize a batch of records."""

    def _normalize_domain(self, value: str) -> str: ...
    def _normalize_ip(self, value: str) -> str: ...
    def _normalize_ip6(self, value: str) -> str: ...
    def _normalize_ip6net(self, value: str) -> str: ...
    def _normalize_url(self, value: str) -> str: ...
    def _normalize_dates(self, record: IOCRecord) -> tuple[datetime, datetime]: ...
```

**Normalleştirme Kuralları**:

| IOC Türü | Dönüştürme | Örnek Girdi | Örnek Çıktı |
|----------|------------|-------------|-------------|
| domain | Küçük harf, kırp, punycode | `Evil.COM ` | `evil.com` |
| domain | Sondaki noktayı kaldır | `evil.com.` | `evil.com` |
| ip | Doğrula, boşlukları temizle | ` 192.168.1.1 ` | `192.168.1.1` |
| ip6 | En kısa forma sıkıştır | `2001:0db8:...` | `2001:db8::1` |
| ip6net | CIDR doğrula, normalleştir | `2001:db8::/32` | `2001:db8::/32` |
| url | Şema/ana bilgisayarı küçük harfe çevir | `HTTP://EVIL.COM/path` | `http://evil.com/path` |
| url | Varsayılan portları kaldır | `http://evil.com:80/` | `http://evil.com/` |
| url | Parçacıkları kaldır | `http://evil.com/#track` | `http://evil.com/` |
| url | İzleme parametrelerini kaldır | `http://evil.com/?utm_source=x` | `http://evil.com/` |
| all | ISO 8601 tarihleri | `2025-01-15 10:30` | `2025-01-15T10:30:00Z` |

---

### 5. `deduplicator.py` — Tekilleştirme Motoru

**Sorumluluk**: Veri kümesi genelinde yinelenen IOC kayıtlarını belirleme ve birleştirme.

```python
class IOCDeduplicator:
    """Multi-strategy IOC deduplication engine."""

    def __init__(self, config: DedupConfig) -> None: ...

    def deduplicate(self, records: list[NormalizedIOC]) -> DedupResult:
        """Remove duplicates using configured strategies."""

    def _exact_hash(self, record: NormalizedIOC) -> str: ...
    def _semantic_key(self, record: NormalizedIOC) -> str: ...
    def _subdomain_key(self, record: NormalizedIOC) -> str: ...
    def _merge_records(self, records: list[NormalizedIOC]) -> NormalizedIOC: ...
```

**Tekilleştirme Stratejileri**:

```python
@dataclass
class DedupConfig:
    exact_match: bool = True
    semantic_match: bool = True
    subdomain_dedup: bool = False
    subdomain_depth: int = 2
    case_sensitive: bool = False
```

**Birleştirme Kuralları**:
- `first_seen`: Yinelenenler arasında en erken
- `last_seen`: Yinelenenler arasında en geç
- `status`: Tüm durumların birleşimi (herhangi biri aktifse sonuç aktif)
- `id`: En düşük id (birincil kayıt)
- `source_page`: Tüm kaynak sayfalar kaydedilir

---

### 6. `quality.py` — Kalite Güvence Motoru

**Sorumluluk**: İstatistiksel analiz, yanlış pozitif algılama, kalite puanlama, raporlama.

```python
class QualityEngine:
    """IOC dataset quality assessment and reporting."""

    def __init__(self, config: QualityConfig) -> None: ...

    def analyze(self, records: list[NormalizedIOC]) -> QualityReport:
        """Run full quality analysis on dataset."""

    def _compute_statistics(self, records: list) -> DatasetStatistics: ...
    def _check_false_positives(self, records: list) -> list[FPFlag]: ...
    def _score_records(self, records: list) -> list[ScoredIOC]: ...
    def _detect_anomalies(self, records: list) -> list[Anomaly]: ...
    def _generate_report(self, ...) -> QualityReport: ...
```

**Kalite Metrikleri**:

| Metrik | Açıklama | Hedef |
|--------|----------|-------|
| Şema Uyumu | Doğrulamadan geçen kayıt yüzdesi | %100 |
| Tekilleştirme Oranı | Kaldırılan yinelenen yüzdesi | %5-20 |
| Yanlış Pozitif Oranı | Muhtemelen masum olarak işaretlenen yüzdesi | < %5 |
| Veri Tazeliği | Son görülme yaşı ortalaması | < 90 gün |
| Alan Bütünlüğü | Boş olmayan isteğe bağlı alan yüzdesi | > %95 |
| Format Tutarlılığı | Tür kurallarına uyan yüzdesi | %100 |
| Genel Kalite Puanı | Ağırlıklı bileşik puan | > 0.90 |

---

### 7. `outputs.py` — Çıktı Motoru

**Sorumluluk**: Format dönüştürme, dosya oluşturma, çıktı paketleme.

```python
class OutputEngine:
    """Multi-format IOC output generator."""

    def __init__(self, config: OutputConfig) -> None: ...

    def generate_all(self, records: list[NormalizedIOC], output_dir: Path) -> list[OutputFile]:
        """Generate all configured output formats."""

    def generate_json(self, records, path) -> OutputFile: ...
    def generate_stix(self, records, path) -> OutputFile: ...
    def generate_csv(self, records, path) -> OutputFile: ...
    def generate_misp(self, records, path) -> OutputFile: ...
    def generate_openioc(self, records, path) -> OutputFile: ...
    def generate_sigma(self, records, path) -> OutputFile: ...
    def generate_yara(self, records, path) -> OutputFile: ...
    def generate_cef(self, records, path) -> OutputFile: ...
    def generate_leef(self, records, path) -> OutputFile: ...
    def generate_syslog(self, records, path) -> OutputFile: ...
    def generate_html(self, records, path) -> OutputFile: ...
    def generate_markdown(self, records, path) -> OutputFile: ...
    def generate_pdf(self, records, path) -> OutputFile: ...
    def generate_splunk(self, records, path) -> OutputFile: ...
    def generate_qradar(self, records, path) -> OutputFile: ...
    def generate_elastic(self, records, path) -> OutputFile: ...
    def generate_grafana(self, records, path) -> OutputFile: ...
```

**Çıktı Format Detayları**:

| Format | MIME Türü | Kodlama | Amaç |
|--------|-----------|---------|------|
| JSON | application/json | UTF-8 | Genel değişim |
| STIX 2.1 | application/stix+json | UTF-8 | Standartlaştırılmış tehdit istihbaratı |
| CSV | text/csv | UTF-8 | Tablo programı aktarımı |
| MISP | application/json | UTF-8 | MISP platformu aktarımı |
| OpenIOC | application/xml | UTF-8 | FireEye/Trellix |
| Sigma | application/yaml | UTF-8 | SIEM algılama kuralları |
| YARA | text/plain | UTF-8 | Kötü amaçlı yazılım algılama |
| CEF | text/plain | UTF-8 | ArcSight/syslog |
| LEEF | text/plain | UTF-8 | IBM QRadar |
| Syslog | text/plain | UTF-8 | Genel SIEM |
| HTML | text/html | UTF-8 | İnsan tarafından okunabilir rapor |
| Markdown | text/markdown | UTF-8 | Dokümantasyon |
| PDF | application/pdf | ikili | Resmi raporlar |
| Splunk | application/splunk | UTF-8 | Splunk aktarımı |
| QRadar | application/json | UTF-8 | QRadar aktarımı |
| Elastic NDJSON | application/x-ndjson | UTF-8 | Elasticsearch toplu |
| Grafana | application/json | UTF-8 | Panel veri kaynağı |

---

### 8. `pipeline.py` — Hat Orkestratörü

**Sorumluluk**: Uçtan uca orkestrasyon, aşama yönetimi, hata işleme, günlük kaydı.

```python
class ThreatIntelPipeline:
    """End-to-end threat intelligence processing pipeline."""

    def __init__(self, config: PipelineConfig) -> None: ...

    async def run(self) -> PipelineResult:
        """Execute the full pipeline from fetch to publish."""

    async def _fetch_stage(self) -> list[RawIOC]: ...
    def _validate_stage(self, records) -> tuple[list, list]: ...
    def _normalize_stage(self, records) -> list[NormalizedIOC]: ...
    def _dedup_stage(self, records) -> DedupResult: ...
    def _quality_stage(self, records) -> QualityReport: ...
    def _output_stage(self, records) -> list[OutputFile]: ...
    def _publish_stage(self, outputs) -> PublishResult: ...

    def _log_stage(self, stage: str, result: Any) -> None: ...
    def _handle_error(self, stage: str, error: Exception) -> PipelineError: ...
```

**Hat Yapılandırması**:

```python
@dataclass
class PipelineConfig:
    api: ClientConfig = field(default_factory=ClientConfig)
    validation: ValidationConfig = field(default_factory=ValidationConfig)
    normalization: NormalizationConfig = field(default_factory=NormalizationConfig)
    dedup: DedupConfig = field(default_factory=DedupConfig)
    quality: QualityConfig = field(default_factory=QualityConfig)
    output: OutputConfig = field(default_factory=OutputConfig)
    publish: PublishConfig = field(default_factory=PublishConfig)
    logging: LoggingConfig = field(default_factory=LoggingConfig)
```

## Modül Etkileşim Sırası

```
+=====================================================================+
|                  Pipeline Execution Sequence                         |
+=====================================================================+

  pipeline.run()
      |
      +----> client.fetch_all()
      |        |
      |        +----> client.fetch_page(N)  [concurrent]
      |        |        |
      |        |        +----> httpx.AsyncClient.get()
      |        |        |
      |        |        +----> models.APIResponse(**response.json())
      |        |        |
      |        |        +----> validator.validate_record()
      |        |        |
      |        |        +----> Returns IOCRecord list
      |        |
      |        +----> Collects all pages
      |        +----> Returns raw records
      |
      +----> validator.validate_batch(records)
      |        |
      |        +----> For each record:
      |        |        _check_required_fields()
      |        |        _check_type_enum()
      |        |        _check_value_format()
      |        |        _check_date_range()
      |        |        _check_value_length()
      |        |        _check_control_chars()
      |        |        _check_encoding()
      |        |        _check_self_reference()
      |        |
      |        +----> Returns BatchValidationResult
      |
      +----> normalizer.normalize_batch(valid_records)
      |        |
      |        +----> For each record:
      |        |        _normalize_domain/ip/ip6/ip6net/url()
      |        |        _normalize_dates()
      |        |
      |        +----> Returns NormalizedIOC list
      |
      +----> deduplicator.deduplicate(normalized_records)
      |        |
      |        +----> _exact_hash() for each record
      |        +----> _semantic_key() for each record
      |        +----> _subdomain_key() if enabled
      |        +----> _merge_records() for duplicates
      |        +----> Returns DedupResult
      |
      +----> quality.analyze(unique_records)
      |        |
      |        +----> _compute_statistics()
      |        +----> _check_false_positives()
      |        +----> _score_records()
      |        +----> _detect_anomalies()
      |        +----> Returns QualityReport
      |
      +----> outputs.generate_all(verified_records)
      |        |
      |        +----> generate_json/stix/csv/misp/...
      |        +----> Returns list[OutputFile]
      |
      +----> Returns PipelineResult
```

## Hata Yayılımı

```
+=====================================================================+
|                     Error Propagation Model                          |
+=====================================================================+

  Module Exception          Pipeline Handling
  +------------------+     +---------------------------+
  | APIError         | --> | Retry with backoff        |
  | ValidationError  | --> | Log + skip record         |
  | NormalizationErr | --> | Log + skip record         |
  | DedupError       | --> | Log + keep both records   |
  | QualityError     | --> | Log + advisory flag       |
  | OutputError      | --> | Retry + fallback format   |
  | PublishError     | --> | Log + local save only     |
  +------------------+     +---------------------------+
```
