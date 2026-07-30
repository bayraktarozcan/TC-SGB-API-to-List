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
                          |deduplicator|
                          |    .py     |
                          +-----------+
```

## Module Specifications

### 1. `client.py` — API Client

**Responsibility**: HTTP communication with the T.C. Siber Guvenlik Baskanligi API.

```python
class AsyncAPIClient:
    """Async HTTP client for the T.C. Siber Guvenlik Baskanligi API."""

    def __init__(
        self,
        base_url: str = "https://siberguvenlik.gov.tr",
        max_retries: int = 3,
        rate_limit: float = 10.0,
        timeout: float = 60.0,
    ) -> None: ...

    async def _get_client(self) -> httpx.AsyncClient: ...
    async def close(self) -> None: ...
    async def __aenter__(self) -> AsyncAPIClient: ...
    async def __aexit__(self, *args) -> None: ...
    async def _rate_limit_wait(self) -> None: ...
    async def _request(self, endpoint: str, params: dict | None = None) -> dict: ...
    async def _fetch_paginated(self, endpoint: str, model_class: type, per_page: int = 9999, max_pages: int = 0) -> list: ...

    async def fetch_addresses(self, per_page: int = 9999, max_pages: int = 0) -> list[AddressRecord]: ...
    async def fetch_descriptions(self) -> list[DescriptionRecord]: ...
    async def fetch_connection_types(self) -> list[ConnectionTypeRecord]: ...
    async def fetch_sources(self) -> list[SourceRecord]: ...
    async def fetch_incidents(self) -> list[IncidentRecord]: ...
    async def fetch_announcements(self) -> list[AnnouncementRecord]: ...
    async def fetch_metadata(self) -> dict[str, Any]: ...
    async def health_check(self) -> bool: ...

    @property
    def stats(self) -> dict[str, Any]: ...
```

**Key Behaviors**:
- Uses `httpx.AsyncClient` with `follow_redirects=True`
- Rate limiting via `asyncio.sleep()` with configurable requests/second (default 10)
- Exponential backoff on 429 (rate limit) and 5xx (server errors)
- `httpx.TransportError` catch for network-level failures (DNS, connection refused, etc.)
- No authentication required (public API)
- Context manager support (`async with AsyncAPIClient() as client:`)

**Default Configuration**:
```python
base_url = "https://siberguvenlik.gov.tr"
max_retries = 3
rate_limit = 10.0    # requests per second
timeout = 60.0       # seconds
per_page = 9999      # max records per page
max_pages = 0        # 0 = fetch all pages
```

---

### 2. `models.py` — Data Models

**Responsibility**: Pydantic models, enums, type definitions for API responses and pipeline stages.

#### Enums

```python
class IOCType(str, Enum):
    DOMAIN = "domain"
    URL = "url"
    IP = "ip"
    IP6 = "ip6"
    IP6NET = "ip6net"

class DescriptionCategory(str, Enum):
    PHISHING = "PH"
    FINANCIAL_PHISHING = "BP"
    MALWARE_DIST_DOMAIN = "MD"
    MALWARE_DIST_IP = "MI"
    MALWARE_DIST_URL = "MU"
    MALWARE_CMD_CENTER = "MC"
    CYBER_ATTACK = "CA"

class Source(str, Enum):
    USOM = "US"
    SOME = "SO"
    RSA = "RS"
    IHBAR = "IH"
    SGB = "SB"

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

#### API Response Models

```python
class PaginatedResponse(BaseModel, Generic[T]):
    models: list[T] = Field(default_factory=list)
    totalCount: int = 0
    count: int = 0
    page: int = 0
    pageCount: int = 0

class AddressRecord(BaseModel):
    id: int
    url: str = ""
    type: str = ""
    desc: str = ""
    source: str = ""
    date: str = ""
    criticality_level: int = Field(default=10)
    connectiontype: str = ""

class DescriptionRecord(BaseModel):
    id: str
    tr_title: str = ""
    en_title: str = ""
    tr_desc: str = ""
    en_desc: str = ""

class ConnectionTypeRecord(BaseModel):
    id: str
    tr_title: str = ""
    en_title: str = ""

class SourceRecord(BaseModel):
    id: str
    tr_title: str = ""
    en_title: str = ""

class IncidentRecord(BaseModel):
    id: int
    title: str = ""
    desc: str = ""
    date: str = ""
    active: bool = True
    slug: str = ""
    language: str = ""

class AnnouncementRecord(BaseModel):
    id: int
    title: str = ""
    desc: str = ""
    date: str = ""
    active: bool = True
    slug: str = ""
    language: str = ""
```

#### Pipeline Models

```python
class ValidatedIOC(BaseModel):
    raw_url: str
    ioc_type: IOCType
    desc: DescriptionCategory | None = None
    source: Source | None = None
    date: datetime | None = None
    criticality_level: int = 10
    connectiontype: ConnectionType | None = None
    original_id: int = 0
    validation_errors: list[str] = Field(default_factory=list)

class NormalizedIOC(BaseModel):
    value: str
    ioc_type: IOCType
    desc: DescriptionCategory | None = None
    source: Source | None = None
    date: datetime | None = None
    criticality_level: int = 10
    connectiontype: ConnectionType | None = None
    original_id: int = 0
    normalization_notes: list[str] = Field(default_factory=list)

class ScoredIOC(BaseModel):
    value: str
    ioc_type: IOCType
    desc: DescriptionCategory | None = None
    source: Source | None = None
    date: datetime | None = None
    criticality_level: int = 10
    connectiontype: ConnectionType | None = None
    original_id: int = 0
    quality_score: float = 0.0
    false_positive_risk: str = "low"
    flags: list[str] = Field(default_factory=list)

class PipelineStats(BaseModel):
    total_fetched: int = 0
    after_validation: int = 0
    after_normalization: int = 0
    after_dedup: int = 0
    after_quality: int = 0
    by_type: dict[str, int] = Field(default_factory=dict)
    by_source: dict[str, int] = Field(default_factory=dict)
    by_desc: dict[str, int] = Field(default_factory=dict)
    by_criticality: dict[int, int] = Field(default_factory=dict)
    validation_rejected: int = 0
    quality_rejected: int = 0
    duplicates_removed: int = 0
    fetch_duration_seconds: float = 0.0
    pipeline_duration_seconds: float = 0.0
    errors: list[str] = Field(default_factory=list)
```

---

### 3. `validator.py` — Data Validator

**Responsibility**: IoC validation, type checking, RFC6761 compliance, format verification.

```python
def validate_ioc(record: AddressRecord) -> ValidatedIOC | None:
    """Validate a single AddressRecord. Returns None if invalid."""

def validate_records_batch(records: list[AddressRecord]) -> tuple[list[ValidatedIOC], list[tuple[AddressRecord, list[str]]]]:
    """Validate a batch. Returns (valid, rejected)."""

def _infer_ioc_type(value: str) -> IOCType | None:
    """Infer IoC type from value when API type field is unavailable."""

def _is_valid_domain(domain: str) -> list[str]:
    """Validate domain format. Returns list of error strings."""

def _is_rfc6761(domain: str) -> bool:
    """Check if domain is RFC6761 reserved."""

def _has_private_suffix(domain: str) -> bool:
    """Check if domain uses a private/internal TLD."""

def _is_reserved_domain(domain: str) -> bool:
    """Check if domain is in the reserved/well-known list."""
```

**Validation Rules**:

| Rule | Check | Action |
|------|-------|--------|
| Empty value | URL field is non-empty | Reject |
| Invalid type | API type matches IOCType enum or can be inferred | Reject |
| Domain format | RFC952/1035 compliant, max 253 chars, max 63 per label | Reject |
| RFC6761 | Not localhost, example.com, test.com, etc. | Reject |
| Private TLD | Not .local, .lan, .home, .internal, etc. | Reject |
| Reserved domain | Not schemas.microsoft.com, w3.org, etc. | Reject |
| IP validity | Valid IPv4/IPv6 address | Reject |
| Date parsing | ISO8601 format | Leave as None on failure |

---

### 4. `normalizer.py` — Data Normalizer

**Responsibility**: Format canonicalization, type-specific transformations, metadata standardization.

```python
def normalize_ioc(validated: ValidatedIOC) -> NormalizedIOC | None:
    """Normalize a ValidatedIOC. Returns None if normalization is impossible."""

def normalize_batch(validated_list: list[ValidatedIOC]) -> list[NormalizedIOC]:
    """Normalize a batch, filtering out invalid results."""

def _normalize_domain(value: str) -> tuple[str, list[str]]:
    """Lowercase, trim, remove trailing dot, IDN→punycode."""

def _normalize_url(value: str) -> tuple[str, list[str]]:
    """Lowercase scheme/host, remove default ports."""

def _normalize_ip(value: str) -> tuple[str, list[str]]:
    """Strip whitespace, lowercase."""
```

**Normalization Rules**:

| IoC Type | Transform | Example Input | Example Output |
|----------|-----------|---------------|----------------|
| domain | Lowercase, trim, punycode | `Evil.COM ` | `evil.com` |
| domain | Remove trailing dot | `evil.com.` | `evil.com` |
| ip | Validate, strip whitespace | ` 192.168.1.1 ` | `192.168.1.1` |
| url | Lowercase scheme/host | `HTTP://EVIL.COM/path` | `http://evil.com/path` |
| url | Remove default ports | `http://evil.com:80/` | `http://evil.com/` |
| all | Reject empty/invalid | `"."` | `None` |

---

### 5. `deduplicator.py` — Deduplication Engine

**Responsibility**: Cross-type IoC deduplication using quality scores.

```python
class DeduplicationResult:
    kept: list[ScoredIOC]
    removed_count: int
    merge_log: list[str]

def deduplicate(scored_iocs: list[ScoredIOC], *, merge_metadata: bool = True) -> DeduplicationResult:
    """Deduplicate IoCs. Keeps the one with the highest quality_score."""

def get_dedup_stats(before: int, after: int) -> dict[str, int]:
    """Return simple dedup stats: {before, after, removed}."""
```

**Deduplication Strategy**:
1. Primary dedup: `(value, ioc_type)` exact match
2. Cross-type dedup: domain extracted from URL matches an existing domain IoC
3. When duplicates found, keep the one with the highest `quality_score`
4. Metadata from removed duplicates logged to `merge_log`

---

### 6. `quality.py` — Quality Scoring Engine

**Responsibility**: Confidence scoring, false-positive risk detection, benign domain/IP filtering.

```python
def score_ioc(ioc: NormalizedIOC) -> ScoredIOC:
    """Compute quality score (0-100) and false-positive risk."""

def score_iocs(iocs: list[NormalizedIOC], threshold: float = 20.0) -> list[ScoredIOC]:
    """Score a batch, filtering out those below threshold."""

def filter_false_positives(scored: list[ScoredIOC], min_score: float = 20.0) -> tuple[list[ScoredIOC], int]:
    """Filter IoCs below the quality threshold."""

def _extract_domain(value: str) -> str | None:
    """Extract domain from IoC value (handles URLs)."""

def _is_benign_domain(domain: str) -> bool:
    """Check against 50+ known-good domains (google, github, microsoft, etc.)."""

def _is_benign_ip(ip_str: str) -> bool:
    """Check against known-good IPs (1.1.1.1, 8.8.8.8, etc.)."""

def _is_private_ip(ip_str: str) -> bool:
    """Check if IP is private, loopback, reserved, or link-local."""

def _has_suspicious_patterns(domain: str) -> list[str]:
    """Detect suspicious patterns: IP in domain, long domain, many hyphens, etc."""
```

**Scoring Algorithm**:
```
base_score = 100
-80 if benign domain/IP
-70 if private IP
-5 per suspicious pattern (ip_in_domain, long_domain, many_hyphens, very_short_domain, numeric_subdomain)
+5 if source is set, -10 if not
+5 if description category is set
+10 if criticality <= 3, -5 if >= 8
+3 if date is set
clamp to [0, 100]
risk: score < 20 → "high", score < 50 → "medium" (unless pattern checks already set "high")
```

---

### 7. `outputs.py` — Output Engine

**Responsibility**: Multi-format IoC output generation (17 formats).

```python
FORMAT_REGISTRY: dict[str, Callable | None]

def generate_nextdns(scored: list[ScoredIOC], path: Path) -> str: ...
def generate_adguard(scored: list[ScoredIOC], path: Path) -> str: ...
def generate_pihole(scored: list[ScoredIOC], path: Path) -> str: ...
def generate_dnsmasq(scored: list[ScoredIOC], path: Path) -> str: ...
def generate_unbound(scored: list[ScoredIOC], path: Path) -> str: ...
def generate_rpz(scored: list[ScoredIOC], path: Path) -> str: ...
def generate_technitium(scored: list[ScoredIOC], path: Path) -> str: ...
def generate_mikrotik(scored: list[ScoredIOC], path: Path) -> str: ...
def generate_nftables(scored: list[ScoredIOC], path: Path) -> str: ...
def generate_ipset(scored: list[ScoredIOC], path: Path) -> str: ...
def generate_suricata(scored: list[ScoredIOC], path: Path) -> str: ...
def generate_crowdsec(scored: list[ScoredIOC], path: Path) -> str: ...
def generate_csv(scored: list[ScoredIOC], path: Path) -> str: ...
def generate_json(scored: list[ScoredIOC], path: Path) -> str: ...
def generate_yaml(scored: list[ScoredIOC], path: Path) -> str: ...
def generate_sqlite(scored: list[ScoredIOC], path: Path) -> str: ...

def generate_all(scored: list[ScoredIOC], output_dir: Path, formats: list[str] | None = None) -> dict[str, str]:
    """Generate all (or selected) output formats. Returns {format: filepath}."""
```

**Output Formats**:

| Format | File | Description |
|--------|------|-------------|
| NextDNS | `nextdns.txt` | NextDNS blocklist |
| AdGuard | `adguard.txt` | AdGuard Home blocklist |
| Pi-hole | `pihole.txt` | Pi-hole blocklist |
| dnsmasq | `dnsmasq.conf` | dnsmasq address records |
| Unbound | `unbound.conf` | Unbound blocklist |
| RPZ | `rpz.zone` | Response Policy Zone |
| Technitium | `technitium.txt` | Technitium DNS blocklist |
| MikroTik | `mikrotik.rsc` | MikroTik RouterOS script (IP + IPv6) |
| nftables | `nftables.nft` | nftables rules (IPv4 + IPv6) |
| ipset | `ipset.sh` | ipset/ip6set shell script |
| Suricata | `suricata.rules` | Suricata IDS rules |
| CrowdSec | `crowdsec.yaml` | CrowdSec scenario YAML |
| CSV | `ioc_data.csv` | Comma-separated values |
| JSON | `ioc_data.json` | Structured JSON |
| YAML | `ioc_data.yaml` | YAML format |
| SQLite | `ioc_database.sqlite` | SQLite database |

---

### 8. `pipeline.py` — Pipeline Orchestrator

**Responsibility**: End-to-end orchestration of fetch → validate → normalize → quality → dedup.

```python
class Pipeline:
    """Main pipeline orchestrator."""

    def __init__(
        self,
        client: AsyncAPIClient | None = None,
        min_quality_score: float = 0.0,
        max_criticality: int = 10,
        per_page: int = 9999,
        max_pages: int = 0,
        skip_validation: bool = False,
        skip_dedup: bool = False,
    ) -> None: ...

    async def run(self) -> tuple[list[ScoredIOC], PipelineStats]:
        """Execute the full 5-stage pipeline."""

    async def __aenter__(self) -> Pipeline: ...
    async def __aexit__(self, *args) -> None: ...

    async def _stage_fetch(self) -> tuple[list[AddressRecord], float]: ...
    def _stage_validate(self, records: list[AddressRecord]) -> tuple[list[ValidatedIOC], int]: ...
    def _stage_normalize(self, validated: list[ValidatedIOC]) -> list[NormalizedIOC]: ...
    def _stage_quality(self, normalized: list[NormalizedIOC]) -> tuple[list[ScoredIOC], int]: ...
    def _stage_dedup(self, scored: list[ScoredIOC]) -> tuple[list[ScoredIOC], int]: ...
    def _compute_stats(self, scored: list[ScoredIOC]) -> None: ...

def run_pipeline_sync(client: AsyncAPIClient | None = None, **kwargs) -> tuple[list[ScoredIOC], PipelineStats]:
    """Synchronous wrapper using asyncio.run()."""
```

## Pipeline Execution Sequence

```
Pipeline.run()
    |
    +----> _stage_fetch()
    |        |
    |        +----> client.fetch_addresses()
    |        |        |
    |        |        +----> client._fetch_paginated() → client._request()
    |        |
    |        +----> Returns list[AddressRecord]
    |
    +----> _stage_validate()
    |        |
    |        +----> For each record:
    |        |        validate_ioc(record)
    |        |        → ValidatedIOC or None
    |        |
    |        +----> Returns (valid, rejected_count)
    |
    +----> _stage_normalize()
    |        |
    |        +----> For each validated:
    |        |        normalize_ioc(validated)
    |        |        → NormalizedIOC or None
    |        |
    |        +----> Returns list[NormalizedIOC]
    |
    +----> _stage_quality()
    |        |
    |        +----> For each normalized:
    |        |        score_ioc(normalized)
    |        |        → ScoredIOC
    |        |        Filter by min_quality_score
    |        |
    |        +----> Returns (scored, rejected_count)
    |
    +----> _stage_dedup()
    |        |
    |        +----> deduplicate(scored)
    |        |        → DeduplicationResult
    |        |
    |        +----> Returns (kept, removed_count)
    |
    +----> _compute_stats()
    |        |
    |        +----> Aggregate by type, source, desc, criticality
    |
    +----> Returns (deduped, PipelineStats)
```

## Error Propagation

```
Stage              Exception              Handling
+------------------+----------------------+---------------------------+
| Fetch            | APIError             | Retry with backoff       |
| Fetch            | TransportError       | Retry, then raise        |
| Fetch            | TimeoutException     | Retry with backoff       |
| Validate         | Exception            | Log + skip record        |
| Normalize        | Exception            | Log + skip record        |
| Quality          | Exception            | Log + skip record        |
| Dedup            | Exception            | Log + keep both records  |
+------------------+----------------------+---------------------------+
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
                          |deduplicator|
                          |    .py     |
                          +-----------+
```

## Modül Özellikleri

### 1. `client.py` — API İstemcisi

**Sorumluluk**: T.C. Siber Güvenlik Başkanlığı API'siyle HTTP iletişimi.

```python
class AsyncAPIClient:
    """T.C. Siber Güvenlik Başkanlığı API'si için asenkron HTTP istemcisi."""

    def __init__(
        self,
        base_url: str = "https://siberguvenlik.gov.tr",
        max_retries: int = 3,
        rate_limit: float = 10.0,
        timeout: float = 60.0,
    ) -> None: ...

    async def _get_client(self) -> httpx.AsyncClient: ...
    async def close(self) -> None: ...
    async def __aenter__(self) -> AsyncAPIClient: ...
    async def __aexit__(self, *args) -> None: ...
    async def _rate_limit_wait(self) -> None: ...
    async def _request(self, endpoint: str, params: dict | None = None) -> dict: ...
    async def _fetch_paginated(self, endpoint: str, model_class: type, per_page: int = 9999, max_pages: int = 0) -> list: ...

    async def fetch_addresses(self, per_page: int = 9999, max_pages: int = 0) -> list[AddressRecord]: ...
    async def fetch_descriptions(self) -> list[DescriptionRecord]: ...
    async def fetch_connection_types(self) -> list[ConnectionTypeRecord]: ...
    async def fetch_sources(self) -> list[SourceRecord]: ...
    async def fetch_incidents(self) -> list[IncidentRecord]: ...
    async def fetch_announcements(self) -> list[AnnouncementRecord]: ...
    async def fetch_metadata(self) -> dict[str, Any]: ...
    async def health_check(self) -> bool: ...

    @property
    def stats(self) -> dict[str, Any]: ...
```

**Ana Davranışlar**:
- `follow_redirects=True` ile `httpx.AsyncClient` kullanır
- Kalibrasyonlu `asyncio.sleep()` ile hız sınırlama (varsayılan 10 istek/saniye)
- 429 (hız sınırı) ve 5xx (sunucu hataları) durumunda üstel geri çekilme
- `httpx.TransportError` yakalama (DNS, bağlantı reddi, vb.)
- Kimlik doğrulama gerektirmez (kamu API'si)
- Bağlam yöneticisi desteği (`async with AsyncAPIClient() as client:`)

**Varsayılan Yapılandırma**:
```python
base_url = "https://siberguvenlik.gov.tr"
max_retries = 3
rate_limit = 10.0    # istek/saniye
timeout = 60.0       # saniye
per_page = 9999      # sayfa basina maksimum kayit
max_pages = 0        # 0 = tum sayfalari cek
```

---

### 2. `models.py` — Veri Modelleri

**Sorumluluk**: API yanıtları ve pipeline aşamaları için Pydantic modelleri, numaralandırmaları, tür tanımları.

#### Numaralandırmalar

```python
class IOCType(str, Enum):
    DOMAIN = "domain"
    URL = "url"
    IP = "ip"
    IP6 = "ip6"
    IP6NET = "ip6net"

class DescriptionCategory(str, Enum):
    PHISHING = "PH"
    FINANCIAL_PHISHING = "BP"
    MALWARE_DIST_DOMAIN = "MD"
    MALWARE_DIST_IP = "MI"
    MALWARE_DIST_URL = "MU"
    MALWARE_CMD_CENTER = "MC"
    CYBER_ATTACK = "CA"

class Source(str, Enum):
    USOM = "US"
    SOME = "SO"
    RSA = "RS"
    IHBAR = "IH"
    SGB = "SB"

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

#### API Yanit Modelleri

```python
class PaginatedResponse(BaseModel, Generic[T]):
    models: list[T] = Field(default_factory=list)
    totalCount: int = 0
    count: int = 0
    page: int = 0
    pageCount: int = 0

class AddressRecord(BaseModel):
    id: int
    url: str = ""
    type: str = ""
    desc: str = ""
    source: str = ""
    date: str = ""
    criticality_level: int = Field(default=10)
    connectiontype: str = ""

class DescriptionRecord(BaseModel):
    id: str
    tr_title: str = ""
    en_title: str = ""
    tr_desc: str = ""
    en_desc: str = ""

class ConnectionTypeRecord(BaseModel):
    id: str
    tr_title: str = ""
    en_title: str = ""

class SourceRecord(BaseModel):
    id: str
    tr_title: str = ""
    en_title: str = ""

class IncidentRecord(BaseModel):
    id: int
    title: str = ""
    desc: str = ""
    date: str = ""
    active: bool = True
    slug: str = ""
    language: str = ""

class AnnouncementRecord(BaseModel):
    id: int
    title: str = ""
    desc: str = ""
    date: str = ""
    active: bool = True
    slug: str = ""
    language: str = ""
```

#### Pipeline Modelleri

```python
class ValidatedIOC(BaseModel):
    raw_url: str
    ioc_type: IOCType
    desc: DescriptionCategory | None = None
    source: Source | None = None
    date: datetime | None = None
    criticality_level: int = 10
    connectiontype: ConnectionType | None = None
    original_id: int = 0
    validation_errors: list[str] = Field(default_factory=list)

class NormalizedIOC(BaseModel):
    value: str
    ioc_type: IOCType
    desc: DescriptionCategory | None = None
    source: Source | None = None
    date: datetime | None = None
    criticality_level: int = 10
    connectiontype: ConnectionType | None = None
    original_id: int = 0
    normalization_notes: list[str] = Field(default_factory=list)

class ScoredIOC(BaseModel):
    value: str
    ioc_type: IOCType
    desc: DescriptionCategory | None = None
    source: Source | None = None
    date: datetime | None = None
    criticality_level: int = 10
    connectiontype: ConnectionType | None = None
    original_id: int = 0
    quality_score: float = 0.0
    false_positive_risk: str = "low"
    flags: list[str] = Field(default_factory=list)

class PipelineStats(BaseModel):
    total_fetched: int = 0
    after_validation: int = 0
    after_normalization: int = 0
    after_dedup: int = 0
    after_quality: int = 0
    by_type: dict[str, int] = Field(default_factory=dict)
    by_source: dict[str, int] = Field(default_factory=dict)
    by_desc: dict[str, int] = Field(default_factory=dict)
    by_criticality: dict[int, int] = Field(default_factory=dict)
    validation_rejected: int = 0
    quality_rejected: int = 0
    duplicates_removed: int = 0
    fetch_duration_seconds: float = 0.0
    pipeline_duration_seconds: float = 0.0
    errors: list[str] = Field(default_factory=list)
```

---

### 3. `validator.py` — Veri Doğrulayıcı

**Sorumluluk**: IoC doğrulama, RFC6761 uyumluluğu, biçim doğrulama.

```python
def validate_ioc(record: AddressRecord) -> ValidatedIOC | None:
    """Tekil AddressRecord doğrulaması. Geçersizse None döndürür."""

def validate_records_batch(records: list[AddressRecord]) -> tuple[list[ValidatedIOC], list[tuple[AddressRecord, list[str]]]]:
    """Toplu doğrulama. (geçerli, reddedilen) döndürür."""

def _infer_ioc_type(value: str) -> IOCType | None:
    """API tür alanı boşken değerden IoC türü çıkarır."""

def _is_valid_domain(domain: str) -> list[str]:
    """Domain biçimini doğrular. Hata listesi döndürür."""

def _is_rfc6761(domain: str) -> bool:
    """Domain'in RFC6761 ayırt edici olup olmadığını kontrol eder."""

def _has_private_suffix(domain: str) -> bool:
    """Domain'in özel/iç TLD kullanıp kullanmadığını kontrol eder."""

def _is_reserved_domain(domain: str) -> bool:
    """Domain'in rezerve/iyi bilinen domain listesinde olup olmadığını kontrol eder."""
```

**Dogrulama Kuralları**:

| Kural | Kontrol | Aksiyon |
|-------|---------|---------|
| Bos deger | URL alani dolu olmali | Reddet |
| Gecersiz tur | API turu IOCType enum ile eslesmeli veya cikarilabilmeli | Reddet |
| Domain biçimi | RFC952/1035 uyumlu, maks 253 karakter, etiket basina maks 63 | Reddet |
| RFC6761 | localhost, example.com, test.com degil | Reddet |
| Ozel TLD | .local, .lan, .home, .internal degil | Reddet |
| Rezerve domain | schemas.microsoft.com, w3.org degil | Reddet |
| IP gecerliligi | Gecerli IPv4/IPv6 adresi | Reddet |
| Tarih ayristirma | ISO8601 biçimi | Basarisizsa None birak |

---

### 4. `normalizer.py` — Veri Normalizatörü

**Sorumluluk**: Biçim kanonikleştirme, türe dönüşüm, meta veri standartlaştırma.

```python
def normalize_ioc(validated: ValidatedIOC) -> NormalizedIOC | None:
    """ValidatedIOC normalizasyonu. Mümkün değilse None döndürür."""

def normalize_batch(validated_list: list[ValidatedIOC]) -> list[NormalizedIOC]:
    """Toplu normalizasyon, geçersiz sonuçları filtreler."""

def _normalize_domain(value: str) -> tuple[str, list[str]]:
    """Küçük harf, kırpma, sondaki noktayı kaldırma, IDN→punycode."""

def _normalize_url(value: str) -> tuple[str, list[str]]:
    """Şema/ana bilgisayarı küçük harfe çevirme, varsayılan portları kaldırma."""

def _normalize_ip(value: str) -> tuple[str, list[str]]:
    """Boşluk temizleme, küçük harf dönüşümü."""
```

**Normalleştirme Kuralları**:

| IoC Turu | Donusum | Ornek Girdi | Ornek Cikti |
|----------|---------|-------------|-------------|
| domain | Kucuk harf, kirpma, punycode | `Evil.COM ` | `evil.com` |
| domain | Sondaki noktayi kaldir | `evil.com.` | `evil.com` |
| ip | Dogrula, bosluklari temizle | ` 192.168.1.1 ` | `192.168.1.1` |
| url | Sema/ana bilgisayari kucuk harfe cevir | `HTTP://EVIL.COM/path` | `http://evil.com/path` |
| url | Varsayilan portlari kaldir | `http://evil.com:80/` | `http://evil.com/` |
| tumu | Bos/gecersiz reddet | `"."` | `None` |

---

### 5. `deduplicator.py` — Tekilleştirme Motoru

**Sorumluluk**: Kalite puanlari kullanan cruz tur IoC tekrar kaldirma.

```python
class DeduplicationResult:
    kept: list[ScoredIOC]
    removed_count: int
    merge_log: list[str]

def deduplicate(scored_iocs: list[ScoredIOC], *, merge_metadata: bool = True) -> DeduplicationResult:
    """IoC'leri tekrar kaldırır. En yüksek kalite puanı olanı korur."""

def get_dedup_stats(before: int, after: int) -> dict[str, int]:
    """Basit tekrar kaldırma istatistikleri döndürür: {before, after, removed}."""
```

**Tekilleştirme Stratejisi**:
1. Birincil tekrar kaldirma: `(value, ioc_type)` tam eslesme
2. Cruz tur tekrar kaldirma: URL'den cikarilan domain mevcut bir domain IoC ile eslesir
3. Tekrarlananlar bulundugunda en yuksek `quality_score` olani korunur
4. Kaldirilan tekrarlardan gelen meta veri `merge_log`'a kaydedilir

---

### 6. `quality.py` — Kalite Puanlama Motoru

**Sorumluluk**: Guven puanlama, yanlis pozitif risk tespiti, masum domain/IP filtreleme.

```python
def score_ioc(ioc: NormalizedIOC) -> ScoredIOC:
    """Kalite puanı (0-100) ve yanlış pozitif riski hesaplar."""

def score_iocs(iocs: list[NormalizedIOC], threshold: float = 20.0) -> list[ScoredIOC]:
    """Toplu puanlama, eşik altındakileri filtreler."""

def filter_false_positives(scored: list[ScoredIOC], min_score: float = 20.0) -> tuple[list[ScoredIOC], int]:
    """Kalite eşiği altındaki IoC'leri filtreler."""

def _extract_domain(value: str) -> str | None:
    """IoC değerinden domain çıkarır (URL'leri işler)."""

def _is_benign_domain(domain: str) -> bool:
    """50+ bilinen iyi domain'e karşı kontrol eder (google, github, microsoft, vb.)."""

def _is_benign_ip(ip_str: str) -> bool:
    """Bilinen iyi IP'lere karşı kontrol eder (1.1.1.1, 8.8.8.8, vb.)."""

def _is_private_ip(ip_str: str) -> bool:
    """IP'nin özel, döngü, rezerve veya bağlantı yerel olup olmadığını kontrol eder."""

def _has_suspicious_patterns(domain: str) -> list[str]:
    """Şüpheli kalıpları algılar: domain içinde IP, uzun domain, çok tire, vb."""
```

**Puanlama Algoritması**:
```
base_puan = 100
-80 ise masum domain/IP
-70 ise ozel IP
-5 supheli kaliplar basina (ip_in_domain, long_domain, many_hyphens, very_short_domain, numeric_subdomain)
+5 ise kaynak belirlenmis, -10 degilse
+5 ise aciklama kategorisi belirlenmis
+10 ise kritiklik <= 3, -5 ise >= 8
+3 ise tarih belirlenmis
[0, 100] arasinda sinirla
risk: puan < 20 → "high", puan < 50 → "medium" (kalip kontrolleri "high" belirlemedikce)
```

---

### 7. `outputs.py` — Çıktı Motoru

**Sorumluluk**: Coklu biçimli IoC cikti uretimi (17 biçim).

```python
FORMAT_REGISTRY: dict[str, Callable | None]

def generate_nextdns(scored: list[ScoredIOC], path: Path) -> str: ...
def generate_adguard(scored: list[ScoredIOC], path: Path) -> str: ...
def generate_pihole(scored: list[ScoredIOC], path: Path) -> str: ...
def generate_dnsmasq(scored: list[ScoredIOC], path: Path) -> str: ...
def generate_unbound(scored: list[ScoredIOC], path: Path) -> str: ...
def generate_rpz(scored: list[ScoredIOC], path: Path) -> str: ...
def generate_technitium(scored: list[ScoredIOC], path: Path) -> str: ...
def generate_mikrotik(scored: list[ScoredIOC], path: Path) -> str: ...
def generate_nftables(scored: list[ScoredIOC], path: Path) -> str: ...
def generate_ipset(scored: list[ScoredIOC], path: Path) -> str: ...
def generate_suricata(scored: list[ScoredIOC], path: Path) -> str: ...
def generate_crowdsec(scored: list[ScoredIOC], path: Path) -> str: ...
def generate_csv(scored: list[ScoredIOC], path: Path) -> str: ...
def generate_json(scored: list[ScoredIOC], path: Path) -> str: ...
def generate_yaml(scored: list[ScoredIOC], path: Path) -> str: ...
def generate_sqlite(scored: list[ScoredIOC], path: Path) -> str: ...

def generate_all(scored: list[ScoredIOC], output_dir: Path, formats: list[str] | None = None) -> dict[str, str]:
    """Tüm (veya seçili) çıktı formatlarını üretir. {format: dosya_yolu} döndürür."""
```

**Cikti Formatlari**:

| Biçim | Dosya | Aciklama |
|--------|-------|----------|
| NextDNS | `nextdns.txt` | NextDNS engelleme listesi |
| AdGuard | `adguard.txt` | AdGuard Home engelleme listesi |
| Pi-hole | `pihole.txt` | Pi-hole engelleme listesi |
| dnsmasq | `dnsmasq.conf` | dnsmasq adres kayitlari |
| Unbound | `unbound.conf` | Unbound engelleme listesi |
| RPZ | `rpz.zone` | Response Policy Zone |
| Technitium | `technitium.txt` | Technitium DNS engelleme listesi |
| MikroTik | `mikrotik.rsc` | MikroTik RouterOS betigi (IP + IPv6) |
| nftables | `nftables.nft` | nftables kuralları (IPv4 + IPv6) |
| ipset | `ipset.sh` | ipset/ip6set shell betigi |
| Suricata | `suricata.rules` | Suricata IDS kuralları |
| CrowdSec | `crowdsec.yaml` | CrowdSec senaryo YAML'i |
| CSV | `ioc_data.csv` |virgulle ayrılmış degerler |
| JSON | `ioc_data.json` | Yapilandirilmis JSON |
| YAML | `ioc_data.yaml` | YAML biçimi |
| SQLite | `ioc_database.sqlite` | SQLite veritabani |

---

### 8. `pipeline.py` — Hat Orkestratörü

**Sorumluluk**: Cekme → dogrulama → normalleştirme → kalite → tekrar kaldirma uclu orkestrasyon.

```python
class Pipeline:
    """Ana hat orkestratoru."""

    def __init__(
        self,
        client: AsyncAPIClient | None = None,
        min_quality_score: float = 0.0,
        max_criticality: int = 10,
        per_page: int = 9999,
        max_pages: int = 0,
        skip_validation: bool = False,
        skip_dedup: bool = False,
    ) -> None: ...

    async def run(self) -> tuple[list[ScoredIOC], PipelineStats]:
        """Tam 5 aşamalı hattı çalıştırır."""

    async def __aenter__(self) -> Pipeline: ...
    async def __aexit__(self, *args) -> None: ...

    async def _stage_fetch(self) -> tuple[list[AddressRecord], float]: ...
    def _stage_validate(self, records: list[AddressRecord]) -> tuple[list[ValidatedIOC], int]: ...
    def _stage_normalize(self, validated: list[ValidatedIOC]) -> list[NormalizedIOC]: ...
    def _stage_quality(self, normalized: list[NormalizedIOC]) -> tuple[list[ScoredIOC], int]: ...
    def _stage_dedup(self, scored: list[ScoredIOC]) -> tuple[list[ScoredIOC], int]: ...
    def _compute_stats(self, scored: list[ScoredIOC]) -> None: ...

def run_pipeline_sync(client: AsyncAPIClient | None = None, **kwargs) -> tuple[list[ScoredIOC], PipelineStats]:
    """asyncio.run() ile senkron sarmalayıcı."""
```

## Hat Çalışma Sırası

```
Pipeline.run()
    |
    +----> _stage_fetch()
    |        |
    |        +----> client.fetch_addresses()
    |        |        |
    |        |        +----> client._fetch_paginated() → client._request()
    |        |
    |        +----> list[AddressRecord] dondurur
    |
    +----> _stage_validate()
    |        |
    |        +----> Her kayit icin:
    |        |        validate_ioc(record)
    |        |        → ValidatedIOC veya None
    |        |
    |        +----> (gecerli, reddedilen_sayisi) dondurur
    |
    +----> _stage_normalize()
    |        |
    |        +----> Her dogrulanmis icin:
    |        |        normalize_ioc(validated)
    |        |        → NormalizedIOC veya None
    |        |
    |        +----> list[NormalizedIOC] dondurur
    |
    +----> _stage_quality()
    |        |
    |        +----> Her normallestirilmis icin:
    |        |        score_ioc(normalized)
    |        |        → ScoredIOC
    |        |        min_quality_score ile filtreleme
    |        |
    |        +----> (puanlanmis, reddedilen_sayisi) dondurur
    |
    +----> _stage_dedup()
    |        |
    |        +----> deduplicate(puanlanmis)
    |        |        → DeduplicationResult
    |        |
    |        +----> (korunan, kaldirilan_sayisi) dondurur
    |
    +----> _compute_stats()
    |        |
    |        +----> Turlere, kaynaklara gore toplula
    |
    +----> (tekrarsiz, PipelineStats) dondurur
```

## Hata Yayılımı

```
Asama              Istisna                  Islem
+------------------+------------------------+---------------------------+
| Cekme            | APIError               | Ustel geri cekilme       |
| Cekme            | TransportError         | Yeniden dene, sonra kaldir |
| Cekme            | TimeoutException       | Ustel geri cekilme       |
| Dogrulama        | Istisna                | Log + kaydi atla         |
| Normallestirme   | Istisna                | Log + kaydi atla         |
| Kalite           | Istisna                | Log + kaydi atla         |
| Tekrar           | Istisna                | Log + her iki kaydi koru |
+------------------+------------------------+---------------------------+
```
