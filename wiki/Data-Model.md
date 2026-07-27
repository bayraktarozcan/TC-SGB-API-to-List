> **Language / Dil** &nbsp;
> [EN English](#-english) &nbsp;·&nbsp; [TR Türkçe](#-türkçe)

<a id="-english"></a>

# Data Model

## Overview

This document defines all data models, schemas, field definitions, and enumerations used in the TC-SGB-API-to-List system. All models use Pydantic v2 for validation and serialization.

## Core Models

### IOCRecord

The primary data model representing a single Indicator of Compromise.

```python
class IOCRecord(BaseModel):
    """A single IOC record from the TC SGB API."""

    model_config = ConfigDict(
        frozen=True,
        str_strip_whitespace=True,
        validate_assignment=True,
    )

    id: int = Field(
        ...,
        description="Unique identifier for the IOC record",
        gt=0,
    )
    type: IOCType = Field(
        ...,
        description="Type of indicator (domain, ip, ip6, ip6net, url)",
    )
    value: str = Field(
        ...,
        description="The IOC value (domain, IP, URL, etc.)",
        min_length=1,
        max_length=2048,
    )
    first_seen: datetime = Field(
        ...,
        description="Timestamp when the IOC was first observed",
    )
    last_seen: datetime = Field(
        ...,
        description="Timestamp when the IOC was last observed",
    )
    status: IOCStatus = Field(
        default=IOCStatus.ACTIVE,
        description="Current status of the IOC",
    )
```

**Field Constraints**:

| Field | Type | Required | Constraints |
|-------|------|----------|-------------|
| `id` | int | Yes | gt=0 |
| `type` | IOCType | Yes | Enum |
| `value` | str | Yes | 1-2048 chars, non-empty |
| `first_seen` | datetime | Yes | ISO 8601 |
| `last_seen` | datetime | Yes | ISO 8601, >= first_seen |
| `status` | IOCStatus | No | Default: ACTIVE |

---

### NormalizedIOC

Extended model after normalization and enrichment.

```python
class NormalizedIOC(BaseModel):
    """IOC record after normalization and enrichment."""

    model_config = ConfigDict(frozen=True)

    # Core fields (from IOCRecord)
    id: int
    type: IOCType
    value: str
    first_seen: datetime
    last_seen: datetime
    status: IOCStatus

    # Normalized fields
    normalized_value: str = Field(
        ...,
        description="Canonical form of the IOC value",
    )
    normalized_type: str = Field(
        ...,
        description="Standardized type string",
    )

    # Quality fields
    quality_score: float = Field(
        default=1.0,
        ge=0.0,
        le=1.0,
        description="Quality score 0.0-1.0",
    )
    quality_flags: list[str] = Field(
        default_factory=list,
        description="Quality issue flags",
    )

    # Provenance
    source_page: int = Field(
        ...,
        description="API page where this record was found",
    )
    processing_timestamp: datetime = Field(
        ...,
        description="When this record was processed",
    )

    # Dedup
    content_hash: str = Field(
        ...,
        description="SHA-256 hash of type+normalized_value",
    )
    is_unique: bool = Field(
        default=True,
        description="Whether this record is unique",
    )
```

---

### ScoredIOC

IOC record with computed risk score.

```python
class ScoredIOC(BaseModel):
    """IOC record with computed risk assessment."""

    record: NormalizedIOC
    risk_score: float = Field(ge=0.0, le=10.0)
    risk_factors: list[RiskFactor]
    confidence: float = Field(ge=0.0, le=1.0)
    recommended_action: str
```

---

## API Response Models

### APIResponse

```python
class APIResponse(BaseModel):
    """Response from the TC SGB API."""

    data: list[IOCRecord]
    meta: PaginationMeta
```

### PaginationMeta

```python
class PaginationMeta(BaseModel):
    """Pagination metadata from API response."""

    total: int = Field(
        ...,
        description="Total number of records",
        ge=0,
    )
    page: int = Field(
        ...,
        description="Current page number",
        ge=1,
    )
    per_page: int = Field(
        ...,
        description="Records per page",
        ge=1,
        le=9999,
    )
```

### APIErrorResponse

```python
class APIErrorResponse(BaseModel):
    """Error response from the API."""

    error: str = Field(..., description="Error code")
    message: str = Field(..., description="Human-readable error message")
```

---

## Enumerations

### IOCType

```python
class IOCType(str, Enum):
    """Types of Indicators of Compromise."""

    DOMAIN = "domain"
    """Malicious domain name"""

    IP = "ip"
    """IPv4 address"""

    IP6 = "ip6"
    """IPv6 address"""

    IP6NET = "ip6net"
    """IPv6 network (CIDR notation)"""

    URL = "url"
    """Malicious URL"""
```

### IOCStatus

```python
class IOCStatus(str, Enum):
    """Status of an IOC record."""

    ACTIVE = "active"
    """IOC is currently active/threatening"""

    INACTIVE = "inactive"
    """IOC is no longer active"""

    UNKNOWN = "unknown"
    """Status cannot be determined"""
```

### RiskLevel

```python
class RiskLevel(str, Enum):
    """Risk classification levels."""

    CRITICAL = "critical"
    """Immediate threat, requires urgent action"""

    HIGH = "high"
    """Significant threat, prioritize remediation"""

    MEDIUM = "medium"
    """Moderate threat, schedule remediation"""

    LOW = "low"
    """Minor threat, monitor"""

    INFO = "info"
    """Informational, no immediate action needed"""
```

### OutputFormat

```python
class OutputFormat(str, Enum):
    """Supported output formats."""

    JSON = "json"
    STIX = "stix"
    CSV = "csv"
    MISP = "misp"
    OPENIOC = "openioc"
    SIGMA = "sigma"
    YARA = "yara"
    CEF = "cef"
    LEEF = "leef"
    SYSLOG = "syslog"
    HTML = "html"
    MARKDOWN = "markdown"
    PDF = "pdf"
    SPLUNK = "splunk"
    QRADAR = "qradar"
    ELASTIC = "elastic"
    GRAFANA = "grafana"
```

### ValidationSeverity

```python
class ValidationSeverity(str, Enum):
    """Severity levels for validation errors."""

    CRITICAL = "critical"
    """Record must be rejected"""

    HIGH = "high"
    """Record should be rejected"""

    MEDIUM = "medium"
    """Record should be flagged"""

    LOW = "low"
    """Informational flag only"""
```

---

## Result Models

### ValidationResult

```python
class ValidationResult(BaseModel):
    """Result of validating a single IOC record."""

    record_id: int
    is_valid: bool
    errors: list[ValidationError]
    warnings: list[ValidationWarning]
    processing_time_ms: float
```

### BatchValidationResult

```python
class BatchValidationResult(BaseModel):
    """Result of validating a batch of records."""

    total_records: int
    valid_records: int
    invalid_records: int
    warnings_count: int
    validation_errors: list[ValidationReport]
    processing_time_ms: float
    pass_rate: float = Field(ge=0.0, le=1.0)
```

### ValidationError

```python
class ValidationError(BaseModel):
    """A single validation error."""

    rule_id: str = Field(
        ...,
        description="Unique rule identifier (e.g., V001)",
    )
    field: str = Field(
        ...,
        description="Field that failed validation",
    )
    severity: ValidationSeverity
    message: str = Field(
        ...,
        description="Human-readable error description",
    )
    value: Any = Field(
        ...,
        description="The invalid value",
    )
```

### ValidationWarning

```python
class ValidationWarning(BaseModel):
    """A validation warning (non-fatal)."""

    rule_id: str
    field: str
    message: str
    value: Any
```

### ValidationReport

```python
class ValidationReport(BaseModel):
    """Detailed validation report for a record."""

    record_id: int
    passed: bool
    checks_run: int
    checks_passed: int
    checks_failed: int
    checks_warned: int
    errors: list[ValidationError]
    warnings: list[ValidationWarning]
```

---

## Normalization Models

### NormalizationTransform

```python
class NormalizationTransform(BaseModel):
    """Record of a normalization transformation applied."""

    field: str = Field(..., description="Field that was transformed")
    original: str = Field(..., description="Original value")
    normalized: str = Field(..., description="Normalized value")
    transforms_applied: list[str] = Field(
        ...,
        description="List of transform names applied",
    )
```

### NormalizationResult

```python
class NormalizationResult(BaseModel):
    """Result of normalizing a batch of records."""

    total_input: int
    total_output: int
    transforms_applied: int
    unique_transforms: list[str]
    processing_time_ms: float
```

---

## Deduplication Models

### DedupConfig

```python
class DedupConfig(BaseModel):
    """Configuration for deduplication engine."""

    exact_match: bool = Field(
        default=True,
        description="Enable exact hash matching",
    )
    semantic_match: bool = Field(
        default=True,
        description="Enable semantic matching (URL path, etc.)",
    )
    subdomain_dedup: bool = Field(
        default=False,
        description="Enable subdomain deduplication",
    )
    subdomain_depth: int = Field(
        default=2,
        description="Number of domain levels for subdomain dedup",
        ge=1,
        le=5,
    )
    case_sensitive: bool = Field(
        default=False,
        description="Case-sensitive comparison",
    )
```

### DedupResult

```python
class DedupResult(BaseModel):
    """Result of deduplication."""

    total_input: int
    total_output: int
    duplicates_removed: int
    dedup_ratio: float = Field(ge=0.0, le=1.0)
    by_type: dict[str, DedupStats]
    processing_time_ms: float
    merge_log: list[DedupMergeEvent]
```

### DedupStats

```python
class DedupStats(BaseModel):
    """Deduplication statistics per IOC type."""

    input_count: int
    output_count: int
    duplicates_removed: int
    dedup_ratio: float
```

### DedupMergeEvent

```python
class DedupMergeEvent(BaseModel):
    """Record of a deduplication merge event."""

    primary_id: int
    merged_ids: list[int]
    merge_reason: str
    original_values: list[str]
```

---

## Quality Models

### QualityReport

```python
class QualityReport(BaseModel):
    """Comprehensive quality analysis report."""

    overall_score: float = Field(ge=0.0, le=1.0)
    statistics: DatasetStatistics
    false_positives: list[FPFlag]
    anomalies: list[Anomaly]
    per_type_scores: dict[str, float]
    recommendations: list[str]
    processing_time_ms: float
```

### DatasetStatistics

```python
class DatasetStatistics(BaseModel):
    """Statistical summary of the IOC dataset."""

    total_records: int
    records_by_type: dict[str, int]
    records_by_status: dict[str, int]
    date_range: DateRange
    avg_value_length: float
    median_value_length: float
    unique_values: int
    duplicate_count: int
```

### FPFlag

```python
class FPFlag(BaseModel):
    """A potential false positive flag."""

    record_id: int
    value: str
    flag_type: str
    confidence: float = Field(ge=0.0, le=1.0)
    reason: str
    recommendation: str
```

### Anomaly

```python
class Anomaly(BaseModel):
    """A detected anomaly in the dataset."""

    anomaly_type: str
    description: str
    affected_records: list[int]
    severity: RiskLevel
    recommendation: str
```

---

## Output Models

### OutputFile

```python
class OutputFile(BaseModel):
    """Metadata about a generated output file."""

    format: OutputFormat
    path: Path
    size_bytes: int
    record_count: int
    checksum_sha256: str
    encoding: str = "utf-8"
    mime_type: str
    generation_time_ms: float
```

### OutputConfig

```python
class OutputConfig(BaseModel):
    """Configuration for output generation."""

    enabled_formats: list[OutputFormat] = Field(
        default_factory=lambda: list(OutputFormat),
        description="Formats to generate",
    )
    output_dir: Path = Field(
        default=Path("output"),
        description="Output directory",
    )
    compress: bool = Field(
        default=False,
        description="Compress output files (gzip)",
    )
    include_metadata: bool = Field(
        default=True,
        description="Include metadata headers",
    )
    include_lineage: bool = Field(
        default=False,
        description="Include data lineage info",
    )
```

---

## Pipeline Models

### PipelineConfig

```python
class PipelineConfig(BaseModel):
    """Complete pipeline configuration."""

    api: ClientConfig = Field(default_factory=ClientConfig)
    validation: ValidationConfig = Field(default_factory=ValidationConfig)
    normalization: NormalizationConfig = Field(default_factory=NormalizationConfig)
    dedup: DedupConfig = Field(default_factory=DedupConfig)
    quality: QualityConfig = Field(default_factory=QualityConfig)
    output: OutputConfig = Field(default_factory=OutputConfig)
    publish: PublishConfig = Field(default_factory=PublishConfig)
    logging: LoggingConfig = Field(default_factory=LoggingConfig)
```

### PipelineResult

```python
class PipelineResult(BaseModel):
    """Final result of pipeline execution."""

    success: bool
    version: str
    start_time: datetime
    end_time: datetime
    duration_seconds: float
    stages: list[StageResult]
    input_record_count: int
    output_record_count: int
    output_files: list[OutputFile]
    quality_report: QualityReport
    errors: list[PipelineError]
```

### StageResult

```python
class StageResult(BaseModel):
    """Result of a single pipeline stage."""

    stage_name: str
    status: str  # "success", "partial", "failed"
    input_count: int
    output_count: int
    duration_ms: float
    details: dict[str, Any]
```

### PipelineError

```python
class PipelineError(BaseModel):
    """An error that occurred during pipeline execution."""

    stage: str
    error_type: str
    message: str
    record_id: Optional[int]
    timestamp: datetime
    recoverable: bool
```

---

## Configuration Models

### ClientConfig

```python
class ClientConfig(BaseModel):
    """HTTP client configuration."""

    base_url: str = "https://threatintel.sgbsg.gov.tr/api/v1"
    max_concurrent: int = Field(default=5, ge=1, le=20)
    request_timeout: float = Field(default=30.0, gt=0)
    retry_max: int = Field(default=3, ge=0)
    retry_base_delay: float = Field(default=0.5, gt=0)
    per_page: int = Field(default=500, ge=1, le=9999)
    user_agent: str = "tc-sgb-api-list/{version}"
```

### ValidationConfig

```python
class ValidationConfig(BaseModel):
    """Validation configuration."""

    strict_mode: bool = Field(default=False)
    max_value_length: int = Field(default=2048, gt=0)
    allow_control_chars: bool = Field(default=False)
    check_encoding: bool = Field(default=True)
    check_self_reference: bool = Field(default=True)
```

### NormalizationConfig

```python
class NormalizationConfig(BaseModel):
    """Normalization configuration."""

    lowercase_values: bool = True
    strip_whitespace: bool = True
    normalize_urls: bool = True
    remove_fragments: bool = True
    remove_tracking_params: bool = True
    normalize_dates: bool = True
    target_date_format: str = "iso8601"
```

### QualityConfig

```python
class QualityConfig(BaseModel):
    """Quality analysis configuration."""

    enable_fp_detection: bool = True
    enable_anomaly_detection: bool = True
    min_quality_score: float = Field(default=0.5, ge=0.0, le=1.0)
    whitelist_file: Optional[Path] = None
    strict_whitelist: bool = False
```

### LoggingConfig

```python
class LoggingConfig(BaseModel):
    """Logging configuration."""

    level: str = "INFO"
    format: str = "json"  # "json" or "text"
    file: Optional[Path] = None
    max_bytes: int = 10 * 1024 * 1024  # 10MB
    backup_count: int = 5
```

<a id="-türkçe"></a>

# Veri Modeli

## Genel Bakış

Bu belge, TC-SGB-API-to-List sisteminde kullanılan tüm veri modellerini, şemaları, alan tanımlamalarını ve numaralandırmaları tanımlar. Tüm modeller doğrulama ve serializasyon için Pydantic v2 kullanır.

## Temel Modeller

### IOCRecord

Tek bir Tehdit Göstergesini temsil eden birincil veri modeli.

```python
class IOCRecord(BaseModel):
    """A single IOC record from the TC SGB API."""

    model_config = ConfigDict(
        frozen=True,
        str_strip_whitespace=True,
        validate_assignment=True,
    )

    id: int = Field(
        ...,
        description="Unique identifier for the IOC record",
        gt=0,
    )
    type: IOCType = Field(
        ...,
        description="Type of indicator (domain, ip, ip6, ip6net, url)",
    )
    value: str = Field(
        ...,
        description="The IOC value (domain, IP, URL, etc.)",
        min_length=1,
        max_length=2048,
    )
    first_seen: datetime = Field(
        ...,
        description="Timestamp when the IOC was first observed",
    )
    last_seen: datetime = Field(
        ...,
        description="Timestamp when the IOC was last observed",
    )
    status: IOCStatus = Field(
        default=IOCStatus.ACTIVE,
        description="Current status of the IOC",
    )
```

**Alan Kısıtlamaları**:

| Alan | Tür | Gerekli | Kısıtlamalar |
|------|------|---------|-------------|
| `id` | int | Evet | gt=0 |
| `type` | IOCType | Evet | Enum |
| `value` | str | Evet | 1-2048 karakter, boş olmayan |
| `first_seen` | datetime | Evet | ISO 8601 |
| `last_seen` | datetime | Evet | ISO 8601, >= first_seen |
| `status` | IOCStatus | Hayır | Varsayılan: ACTIVE |

---

### NormalizedIOC

Normalizasyon ve zenginleştirme sonrası genişletilmiş model.

```python
class NormalizedIOC(BaseModel):
    """IOC record after normalization and enrichment."""

    model_config = ConfigDict(frozen=True)

    # Core fields (from IOCRecord)
    id: int
    type: IOCType
    value: str
    first_seen: datetime
    last_seen: datetime
    status: IOCStatus

    # Normalized fields
    normalized_value: str = Field(
        ...,
        description="Canonical form of the IOC value",
    )
    normalized_type: str = Field(
        ...,
        description="Standardized type string",
    )

    # Quality fields
    quality_score: float = Field(
        default=1.0,
        ge=0.0,
        le=1.0,
        description="Quality score 0.0-1.0",
    )
    quality_flags: list[str] = Field(
        default_factory=list,
        description="Quality issue flags",
    )

    # Provenance
    source_page: int = Field(
        ...,
        description="API page where this record was found",
    )
    processing_timestamp: datetime = Field(
        ...,
        description="When this record was processed",
    )

    # Dedup
    content_hash: str = Field(
        ...,
        description="SHA-256 hash of type+normalized_value",
    )
    is_unique: bool = Field(
        default=True,
        description="Whether this record is unique",
    )
```

---

### ScoredIOC

Hesaplanmış risk puanına sahip IOC kaydı.

```python
class ScoredIOC(BaseModel):
    """IOC record with computed risk assessment."""

    record: NormalizedIOC
    risk_score: float = Field(ge=0.0, le=10.0)
    risk_factors: list[RiskFactor]
    confidence: float = Field(ge=0.0, le=1.0)
    recommended_action: str
```

---

## API Yanıt Modelleri

### APIResponse

```python
class APIResponse(BaseModel):
    """Response from the TC SGB API."""

    data: list[IOCRecord]
    meta: PaginationMeta
```

### PaginationMeta

```python
class PaginationMeta(BaseModel):
    """Pagination metadata from API response."""

    total: int = Field(
        ...,
        description="Total number of records",
        ge=0,
    )
    page: int = Field(
        ...,
        description="Current page number",
        ge=1,
    )
    per_page: int = Field(
        ...,
        description="Records per page",
        ge=1,
        le=9999,
    )
```

### APIErrorResponse

```python
class APIErrorResponse(BaseModel):
    """Error response from the API."""

    error: str = Field(..., description="Error code")
    message: str = Field(..., description="Human-readable error message")
```

---

## Numaralandırmalar

### IOCType

```python
class IOCType(str, Enum):
    """Types of Indicators of Compromise."""

    DOMAIN = "domain"
    """Malicious domain name"""

    IP = "ip"
    """IPv4 address"""

    IP6 = "ip6"
    """IPv6 address"""

    IP6NET = "ip6net"
    """IPv6 network (CIDR notation)"""

    URL = "url"
    """Malicious URL"""
```

### IOCStatus

```python
class IOCStatus(str, Enum):
    """Status of an IOC record."""

    ACTIVE = "active"
    """IOC is currently active/threatening"""

    INACTIVE = "inactive"
    """IOC is no longer active"""

    UNKNOWN = "unknown"
    """Status cannot be determined"""
```

### RiskLevel

```python
class RiskLevel(str, Enum):
    """Risk classification levels."""

    CRITICAL = "critical"
    """Immediate threat, requires urgent action"""

    HIGH = "high"
    """Significant threat, prioritize remediation"""

    MEDIUM = "medium"
    """Moderate threat, schedule remediation"""

    LOW = "low"
    """Minor threat, monitor"""

    INFO = "info"
    """Informational, no immediate action needed"""
```

### OutputFormat

```python
class OutputFormat(str, Enum):
    """Supported output formats."""

    JSON = "json"
    STIX = "stix"
    CSV = "csv"
    MISP = "misp"
    OPENIOC = "openioc"
    SIGMA = "sigma"
    YARA = "yara"
    CEF = "cef"
    LEEF = "leef"
    SYSLOG = "syslog"
    HTML = "html"
    MARKDOWN = "markdown"
    PDF = "pdf"
    SPLUNK = "splunk"
    QRADAR = "qradar"
    ELASTIC = "elastic"
    GRAFANA = "grafana"
```

### ValidationSeverity

```python
class ValidationSeverity(str, Enum):
    """Severity levels for validation errors."""

    CRITICAL = "critical"
    """Record must be rejected"""

    HIGH = "high"
    """Record should be rejected"""

    MEDIUM = "medium"
    """Record should be flagged"""

    LOW = "low"
    """Informational flag only"""
```

---

## Sonuç Modelleri

### ValidationResult

```python
class ValidationResult(BaseModel):
    """Result of validating a single IOC record."""

    record_id: int
    is_valid: bool
    errors: list[ValidationError]
    warnings: list[ValidationWarning]
    processing_time_ms: float
```

### BatchValidationResult

```python
class BatchValidationResult(BaseModel):
    """Result of validating a batch of records."""

    total_records: int
    valid_records: int
    invalid_records: int
    warnings_count: int
    validation_errors: list[ValidationReport]
    processing_time_ms: float
    pass_rate: float = Field(ge=0.0, le=1.0)
```

### ValidationError

```python
class ValidationError(BaseModel):
    """A single validation error."""

    rule_id: str = Field(
        ...,
        description="Unique rule identifier (e.g., V001)",
    )
    field: str = Field(
        ...,
        description="Field that failed validation",
    )
    severity: ValidationSeverity
    message: str = Field(
        ...,
        description="Human-readable error description",
    )
    value: Any = Field(
        ...,
        description="The invalid value",
    )
```

### ValidationWarning

```python
class ValidationWarning(BaseModel):
    """A validation warning (non-fatal)."""

    rule_id: str
    field: str
    message: str
    value: Any
```

### ValidationReport

```python
class ValidationReport(BaseModel):
    """Detailed validation report for a record."""

    record_id: int
    passed: bool
    checks_run: int
    checks_passed: int
    checks_failed: int
    checks_warned: int
    errors: list[ValidationError]
    warnings: list[ValidationWarning]
```

---

## Normalizasyon Modelleri

### NormalizationTransform

```python
class NormalizationTransform(BaseModel):
    """Record of a normalization transformation applied."""

    field: str = Field(..., description="Field that was transformed")
    original: str = Field(..., description="Original value")
    normalized: str = Field(..., description="Normalized value")
    transforms_applied: list[str] = Field(
        ...,
        description="List of transform names applied",
    )
```

### NormalizationResult

```python
class NormalizationResult(BaseModel):
    """Result of normalizing a batch of records."""

    total_input: int
    total_output: int
    transforms_applied: int
    unique_transforms: list[str]
    processing_time_ms: float
```

---

## Tekilleştirme Modelleri

### DedupConfig

```python
class DedupConfig(BaseModel):
    """Configuration for deduplication engine."""

    exact_match: bool = Field(
        default=True,
        description="Enable exact hash matching",
    )
    semantic_match: bool = Field(
        default=True,
        description="Enable semantic matching (URL path, etc.)",
    )
    subdomain_dedup: bool = Field(
        default=False,
        description="Enable subdomain deduplication",
    )
    subdomain_depth: int = Field(
        default=2,
        description="Number of domain levels for subdomain dedup",
        ge=1,
        le=5,
    )
    case_sensitive: bool = Field(
        default=False,
        description="Case-sensitive comparison",
    )
```

### DedupResult

```python
class DedupResult(BaseModel):
    """Result of deduplication."""

    total_input: int
    total_output: int
    duplicates_removed: int
    dedup_ratio: float = Field(ge=0.0, le=1.0)
    by_type: dict[str, DedupStats]
    processing_time_ms: float
    merge_log: list[DedupMergeEvent]
```

### DedupStats

```python
class DedupStats(BaseModel):
    """Deduplication statistics per IOC type."""

    input_count: int
    output_count: int
    duplicates_removed: int
    dedup_ratio: float
```

### DedupMergeEvent

```python
class DedupMergeEvent(BaseModel):
    """Record of a deduplication merge event."""

    primary_id: int
    merged_ids: list[int]
    merge_reason: str
    original_values: list[str]
```

---

## Kalite Modelleri

### QualityReport

```python
class QualityReport(BaseModel):
    """Comprehensive quality analysis report."""

    overall_score: float = Field(ge=0.0, le=1.0)
    statistics: DatasetStatistics
    false_positives: list[FPFlag]
    anomalies: list[Anomaly]
    per_type_scores: dict[str, float]
    recommendations: list[str]
    processing_time_ms: float
```

### DatasetStatistics

```python
class DatasetStatistics(BaseModel):
    """Statistical summary of the IOC dataset."""

    total_records: int
    records_by_type: dict[str, int]
    records_by_status: dict[str, int]
    date_range: DateRange
    avg_value_length: float
    median_value_length: float
    unique_values: int
    duplicate_count: int
```

### FPFlag

```python
class FPFlag(BaseModel):
    """A potential false positive flag."""

    record_id: int
    value: str
    flag_type: str
    confidence: float = Field(ge=0.0, le=1.0)
    reason: str
    recommendation: str
```

### Anomaly

```python
class Anomaly(BaseModel):
    """A detected anomaly in the dataset."""

    anomaly_type: str
    description: str
    affected_records: list[int]
    severity: RiskLevel
    recommendation: str
```

---

## Çıktı Modelleri

### OutputFile

```python
class OutputFile(BaseModel):
    """Metadata about a generated output file."""

    format: OutputFormat
    path: Path
    size_bytes: int
    record_count: int
    checksum_sha256: str
    encoding: str = "utf-8"
    mime_type: str
    generation_time_ms: float
```

### OutputConfig

```python
class OutputConfig(BaseModel):
    """Configuration for output generation."""

    enabled_formats: list[OutputFormat] = Field(
        default_factory=lambda: list(OutputFormat),
        description="Formats to generate",
    )
    output_dir: Path = Field(
        default=Path("output"),
        description="Output directory",
    )
    compress: bool = Field(
        default=False,
        description="Compress output files (gzip)",
    )
    include_metadata: bool = Field(
        default=True,
        description="Include metadata headers",
    )
    include_lineage: bool = Field(
        default=False,
        description="Include data lineage info",
    )
```

---

## Boru Hattı Modelleri

### PipelineConfig

```python
class PipelineConfig(BaseModel):
    """Complete pipeline configuration."""

    api: ClientConfig = Field(default_factory=ClientConfig)
    validation: ValidationConfig = Field(default_factory=ValidationConfig)
    normalization: NormalizationConfig = Field(default_factory=NormalizationConfig)
    dedup: DedupConfig = Field(default_factory=DedupConfig)
    quality: QualityConfig = Field(default_factory=QualityConfig)
    output: OutputConfig = Field(default_factory=OutputConfig)
    publish: PublishConfig = Field(default_factory=PublishConfig)
    logging: LoggingConfig = Field(default_factory=LoggingConfig)
```

### PipelineResult

```python
class PipelineResult(BaseModel):
    """Final result of pipeline execution."""

    success: bool
    version: str
    start_time: datetime
    end_time: datetime
    duration_seconds: float
    stages: list[StageResult]
    input_record_count: int
    output_record_count: int
    output_files: list[OutputFile]
    quality_report: QualityReport
    errors: list[PipelineError]
```

### StageResult

```python
class StageResult(BaseModel):
    """Result of a single pipeline stage."""

    stage_name: str
    status: str  # "success", "partial", "failed"
    input_count: int
    output_count: int
    duration_ms: float
    details: dict[str, Any]
```

### PipelineError

```python
class PipelineError(BaseModel):
    """An error that occurred during pipeline execution."""

    stage: str
    error_type: str
    message: str
    record_id: Optional[int]
    timestamp: datetime
    recoverable: bool
```

---

## Yapılandırma Modelleri

### ClientConfig

```python
class ClientConfig(BaseModel):
    """HTTP client configuration."""

    base_url: str = "https://threatintel.sgbsg.gov.tr/api/v1"
    max_concurrent: int = Field(default=5, ge=1, le=20)
    request_timeout: float = Field(default=30.0, gt=0)
    retry_max: int = Field(default=3, ge=0)
    retry_base_delay: float = Field(default=0.5, gt=0)
    per_page: int = Field(default=500, ge=1, le=9999)
    user_agent: str = "tc-sgb-api-list/{version}"
```

### ValidationConfig

```python
class ValidationConfig(BaseModel):
    """Validation configuration."""

    strict_mode: bool = Field(default=False)
    max_value_length: int = Field(default=2048, gt=0)
    allow_control_chars: bool = Field(default=False)
    check_encoding: bool = Field(default=True)
    check_self_reference: bool = Field(default=True)
```

### NormalizationConfig

```python
class NormalizationConfig(BaseModel):
    """Normalization configuration."""

    lowercase_values: bool = True
    strip_whitespace: bool = True
    normalize_urls: bool = True
    remove_fragments: bool = True
    remove_tracking_params: bool = True
    normalize_dates: bool = True
    target_date_format: str = "iso8601"
```

### QualityConfig

```python
class QualityConfig(BaseModel):
    """Quality analysis configuration."""

    enable_fp_detection: bool = True
    enable_anomaly_detection: bool = True
    min_quality_score: float = Field(default=0.5, ge=0.0, le=1.0)
    whitelist_file: Optional[Path] = None
    strict_whitelist: bool = False
```

### LoggingConfig

```python
class LoggingConfig(BaseModel):
    """Logging configuration."""

    level: str = "INFO"
    format: str = "json"  # "json" or "text"
    file: Optional[Path] = None
    max_bytes: int = 10 * 1024 * 1024  # 10MB
    backup_count: int = 5
```
