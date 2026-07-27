> **Language / Dil** &nbsp;
> [EN English](#-english) &nbsp;·&nbsp; [TR Türkçe](#-türkçe)

<a id="-english"></a>

# Data Flow

## Overview

This document describes the complete data flow through the TC-SGB-API-to-List threat intelligence pipeline, from API ingestion to final output publication.

## End-to-End Data Flow

```
+=====================================================================+
|                    TC-SGB-API-to-List Data Flow                         |
+=====================================================================+

 [1]              [2]              [3]              [4]
+------+      +----------+     +---------+     +----------+
|      |      |          |     |         |     |          |
| API  |----->| Raw Data |---->|Validate |---->|Normalize |
| Call |      | Store    |     |         |     |          |
|      |      |          |     | Schema  |     | Canonical|
| GET  |      | JSON     |     | Check   |     | Format   |
| /v1  |      | Response |     | Type Map|     |          |
|      |      |          |     | Null Chk|     |          |
+------+      +----------+     +---------+     +----------+
                                    |               |
                                    | errors        | transformed
                                    v               v
                              +---------+     +----------+
                              | Error   |     |Transform |
                              | Log     |     | Records  |
                              +---------+     +----------+
                                                  |
                                                  v
 [5]              [6]              [7]              [8]
+----------+   +----------+   +----------+     +----------+
|          |   |          |   |          |     |          |
| Dedup    |-->| False    |-->| Output   |---->| Quality  |
|          |   | Positive |   | Generate |     | Tests    |
| Hash     |   | Control  |   |          |     |          |
| Content  |   |          |   | 16+ Fmt  |     | Valid    |
| Seen Map |   | Benign   |   |          |     | Schema   |
|          |   | Whitelist|   |          |     | Stats    |
+----------+   +----------+   +----------+     +----------+
                                    |               |
                                    | files         | report
                                    v               v
                              +----------+     +----------+
                              |          |     |          |
                              | Publish  |     | Quality  |
                              |          |     | Report   |
                              | GitHub   |     |          |
                              | Release  |     | Metrics  |
                              | PyPI     |     | Dashboard|
                              |          |     |          |
                              +----------+     +----------+
```

## Stage 1: API Download

```
+---------------------------------------------------+
|  STAGE 1: API Download                            |
+---------------------------------------------------+
|                                                   |
|  Input:  API endpoint configuration               |
|  Output: Raw JSON response per page               |
|                                                   |
|  Process:                                         |
|  1. Resolve API base URL                          |
|  2. Query total record count                      |
|  3. Calculate pagination (ceil(total/per_page))   |
|  4. Fetch all pages concurrently (semaphore=5)    |
|  5. Store raw responses                           |
|                                                   |
|  Rate Limiting:                                   |
|  - Max 5 concurrent requests                      |
|  - Min 100ms between sequential requests          |
|  - Exponential backoff on 429/503                 |
|                                                   |
|  Data Volume:                                     |
|  - ~483,690 records (as of 2025)                  |
|  - 500 records per page                           |
|  - ~968 API calls for full fetch                  |
|                                                   |
+---------------------------------------------------+
```

## Stage 2: Raw Data Store

```
+---------------------------------------------------+
|  STAGE 2: Raw Data Store                          |
+---------------------------------------------------+
|                                                   |
|  Input:  Raw JSON API responses                   |
|  Output: Parsed record list (unvalidated)         |
|                                                   |
|  Schema:                                          |
|  {                                                |
|    "data": [                                      |
|      {                                            |
|        "id": int,                                 |
|        "type": str,                               |
|        "value": str,                              |
|        "first_seen": str,                         |
|        "last_seen": str,                          |
|        "status": str                              |
|      }                                            |
|    ],                                             |
|    "meta": {                                      |
|      "total": int,                                |
|      "page": int,                                 |
|      "per_page": int                              |
|    }                                              |
|  }                                                |
|                                                   |
|  Retention: In-memory during processing           |
|  Persistence: Optional local cache (JSON)         |
|                                                   |
+---------------------------------------------------+
```

## Stage 3: Validation

```
+---------------------------------------------------+
|  STAGE 3: Validation                              |
+---------------------------------------------------+
|                                                   |
|  Input:  Raw parsed records                       |
|  Output: Validated records + error report         |
|                                                   |
|  Checks:                                          |
|  +------------------------------------------------+
|  | Rule                    | Action               |
|  +------------------------------------------------+
|  | Required fields present | Reject if missing    |
|  | ID is integer > 0      | Reject if invalid     |
|  | Type in enum set       | Reject if unknown     |
|  | Value non-empty string | Reject if empty       |
|  | Value length <= 2048   | Reject if too long    |
|  | No null bytes          | Reject if contains    |
|  | No control characters  | Strip or reject       |
|  | Date format valid      | Reject if malformed   |
|  | Status in valid set    | Map unknown to default|
|  +------------------------------------------------+
|                                                   |
|  Output:                                          |
|  - valid_records: List[IOCRecord]                 |
|  - invalid_records: List[ValidationError]         |
|  - validation_stats: ValidationReport             |
|                                                   |
+---------------------------------------------------+
```

## Stage 4: Normalization

```
+---------------------------------------------------+
|  STAGE 4: Normalization                           |
+---------------------------------------------------+
|                                                   |
|  Input:  Validated records                        |
|  Output: Normalized records (canonical form)      |
|                                                   |
|  Transformations by type:                         |
|                                                   |
|  domain:                                         |
|  - Lowercase                                      |
|  - Trim whitespace                               |
|  - Punycode encode (IDN)                         |
|  - Remove trailing dots                           |
|  - Validate against RFC 1035/1123                |
|                                                   |
|  ip:                                             |
|  - Strip whitespace                              |
|  - Validate against ipaddress module             |
|  - Expand compressed IPv6                        |
|  - Remove zone IDs                               |
|                                                   |
|  ip6:                                            |
|  - Compress to shortest form                     |
|  - Lowercase hex                                 |
|  - Validate full expansion                       |
|                                                   |
|  ip6net:                                         |
|  - Normalize prefix length                       |
|  - Validate CIDR notation                        |
|  - Expand network address                        |
|                                                   |
|  url:                                            |
|  - Percent-encode special chars                  |
|  - Normalize scheme to lowercase                 |
|  - Remove default ports (80/443)                 |
|  - Decode unnecessary percent-encoding           |
|  - Sort query parameters                         |
|  - Remove fragment identifiers                   |
|  - Remove tracking parameters (utm_*)            |
|                                                   |
|  Metadata:                                        |
|  - Standardize date format to ISO 8601           |
|  - Normalize status enum                          |
|  - Add processing timestamp                      |
|                                                   |
+---------------------------------------------------+
```

## Stage 5: Deduplication

```
+---------------------------------------------------+
|  STAGE 5: Deduplication                           |
+---------------------------------------------------+
|                                                   |
|  Input:  Normalized records                       |
|  Output: Unique records + dedup report            |
|                                                   |
|  Strategy:                                        |
|  +------------------------------------------------+
|  | Level 1: Exact Match                          |
|  | - Hash(type + normalized_value)               |
|  | - O(1) lookup in seen set                     |
|  +------------------------------------------------+
|  | Level 2: Semantic Match                       |
|  | - URL: ignore query params, fragments         |
|  | - IP: equivalent notations                    |
|  | - Domain: www prefix equivalence              |
|  +------------------------------------------------+
|  | Level 3: Subdomain Dedup                      |
|  | - *.evil.com deduped to evil.com              |
|  | - Configurable depth                          |
|  +------------------------------------------------+
|                                                   |
|  Merge Policy:                                    |
|  - Keep earliest first_seen                      |
|  - Keep latest last_seen                         |
|  - Union of status flags                         |
|  - Preserve source attribution                   |
|                                                   |
|  Statistics:                                      |
|  - Total input records                           |
|  - Duplicates removed                            |
|  - Dedup ratio                                   |
|  - Per-type breakdown                            |
|                                                   |
+---------------------------------------------------+
```

## Stage 6: False Positive Control

```
+---------------------------------------------------+
|  STAGE 6: False Positive Control                  |
+---------------------------------------------------+
|                                                   |
|  Input:  Deduplicated records                     |
|  Output: Verified records + FP report             |
|                                                   |
|  Whitelist Checks:                                |
|  +------------------------------------------------+
|  | Check                        | Action         |
|  +------------------------------------------------+
|  | Known benign domains         | Flag/Exclude   |
|  | CDN infrastructure           | Flag           |
|  | Major cloud providers        | Flag           |
|  | Government domains           | Flag           |
|  | Popular websites             | Flag           |
|  +------------------------------------------------+
|                                                   |
|  Heuristics:                                      |
|  - Newly registered domains (< 30 days)          |
|  - High-entropy subdomains (DGA detection)       |
|  - IP address in private ranges                   |
|  - Reserved TLD (.local, .test, .example)        |
|  - Self-referencing values                        |
|                                                   |
|  Configuration:                                   |
|  - Whitelist file: config/whitelist.txt           |
|  - Strict mode: reject all flagged                |
|  - Advisory mode: flag but include                |
|                                                   |
+---------------------------------------------------+
```

## Stage 7: Output Generation

```
+---------------------------------------------------+
|  STAGE 7: Output Generation                      |
+---------------------------------------------------+
|                                                   |
|  Input:  Verified records                         |
|  Output: 16+ formatted output files               |
|                                                   |
|  Output Formats:                                  |
|  +------------------------------------------------+
|  | Format         | Extension  | Use Case        |
|  +------------------------------------------------+
|  | JSON           | .json      | General         |
|  | STIX 2.1       | .stix.json | Interop         |
|  | CSV            | .csv       | Spreadsheet     |
|  | MISP           | .misp.json | MISP platform   |
|  | OpenIOC        | .ioc       | FireEye/Trellix |
|  | Sigma          | .yml       | SIEM rules      |
|  | YARA           | .yar       | Malware detect  |
|  | CEF            | .cef       | Syslog/CEF      |
|  | LEEF           | .leef      | IBM QRadar      |
|  | Syslog         | .log       | Generic SIEM    |
|  | HTML           | .html      | Human report    |
|  | Markdown       | .md        | Documentation   |
|  | PDF            | .pdf       | Formal report   |
|  | Splunk         | .spl       | Splunk import   |
|  | QRadar         | .json      | QRadar import   |
|  | Elastic NDJSON | .ndjson    | Elasticsearch   |
|  | Grafana        | .json      | Dashboard       |
|  +------------------------------------------------+
|                                                   |
|  Each format includes:                            |
|  - Header with metadata                           |
|  - Processing timestamp                           |
|  - Source attribution                              |
|  - Record count                                    |
|                                                   |
+---------------------------------------------------+
```

## Stage 8: Quality Tests

```
+---------------------------------------------------+
|  STAGE 8: Quality Tests                           |
+---------------------------------------------------+
|                                                   |
|  Input:  All output files                         |
|  Output: Quality report + pass/fail               |
|                                                   |
|  Test Categories:                                 |
|  +------------------------------------------------+
|  | Test                     | Threshold          |
|  +------------------------------------------------+
|  | Schema validity          | 100% pass          |
|  | Format conformance       | 100% pass          |
|  | Round-trip consistency   | JSON=JSON          |
|  | Record count match       | input == output    |
|  | No duplicate IOCs        | 0 duplicates       |
|  | Field completeness       | >99% non-null      |
|  | Date range validity      | All dates parse    |
|  | Type distribution        | Matches expected   |
|  | Output file sizes        | >0 bytes           |
|  | Encoding (UTF-8)         | Valid UTF-8        |
|  +------------------------------------------------+
|                                                   |
|  Report:                                          |
|  - Total tests run                                |
|  - Tests passed / failed                          |
|  - Coverage percentage                            |
|  - Performance metrics                            |
|  - Anomaly detection results                      |
|                                                   |
+---------------------------------------------------+
```

## Stage 9: Publication

```
+---------------------------------------------------+
|  STAGE 9: Publication                             |
+---------------------------------------------------+
|                                                   |
|  Input:  Quality-assured output files             |
|  Output: Published artifacts                      |
|                                                   |
|  Channels:                                        |
|  +------------------------------------------------+
|  | Channel          | Trigger      | Format      |
|  +------------------------------------------------+
|  | GitHub Release   | Tag push     | All formats |
|  | GitHub Actions   | On success   | Artifacts   |
|  | PyPI             | Tag push     | Package     |
|  | Local filesystem | Always       | All formats |
|  +------------------------------------------------+
|                                                   |
|  Release Artifacts:                               |
|  - tc-sgb-{version}.tar.gz                       |
|  - tc_sgb-{version}-py3-none-any.whl             |
|  - output/*.json                                  |
|  - output/*.csv                                   |
|  - output/*.stix.json                             |
|  - output/report.html                             |
|                                                   |
+---------------------------------------------------+
```

## Error Handling Flow

```
                    +----------+
                    |  Error   |
                    | Detected |
                    +----------+
                         |
              +----------+----------+
              |                     |
              v                     v
        +----------+          +----------+
        | Recoverable|        | Fatal     |
        |            |        |           |
        +----------+          +----------+
              |                     |
              v                     v
        +----------+          +----------+
        | Retry with|        | Abort     |
        | backoff   |        | Pipeline  |
        | (max 3)   |        |           |
        +----------+          +----------+
              |                     |
              v                     v
        +----------+          +----------+
        | Success?  |        | Error     |
        |           |        | Report    |
        +----------+          +----------+
           |      |              |
           v      v              v
       +------+ +------+   +----------+
       | Continue| Abort|   | Exit     |
       |         |      |   | Code 1   |
       +------+ +------+   +----------+
```

## Data Lineage

Every record carries provenance metadata through the pipeline:

```json
{
  "lineage": {
    "source": "tc-sgb-api",
    "fetch_time": "2025-01-15T10:30:00Z",
    "page": 42,
    "raw_hash": "sha256:abc123...",
    "validation": {
      "passed": true,
      "checks": 8,
      "timestamp": "2025-01-15T10:30:01Z"
    },
    "normalization": {
      "transforms": ["lowercase", "trim", "punycode"],
      "timestamp": "2025-01-15T10:30:01Z"
    },
    "dedup": {
      "is_unique": true,
      "hash": "sha256:def456...",
      "timestamp": "2025-01-15T10:30:02Z"
    },
    "quality": {
      "score": 0.98,
      "flags": [],
      "timestamp": "2025-01-15T10:30:02Z"
    }
  }
}
```

<a id="-türkçe"></a>

# Veri Akışı

## Genel Bakış

Bu belge, TC-SGB-API-to-List tehdit istihbaratı hattındaki API alımından nihai çıktı yayımına kadar olan tam veri akışını tanımlamaktadır.

## Uçtan Uca Veri Akışı

```
+=====================================================================+
|                    TC-SGB-API-to-List Data Flow                         |
+=====================================================================+

 [1]              [2]              [3]              [4]
+------+      +----------+     +---------+     +----------+
|      |      |          |     |         |     |          |
| API  |----->| Raw Data |---->|Validate |---->|Normalize |
| Call |      | Store    |     |         |     |          |
|      |      |          |     | Schema  |     | Canonical|
| GET  |      | JSON     |     | Check   |     | Format   |
| /v1  |      | Response |     | Type Map|     |          |
|      |      |          |     | Null Chk|     |          |
+------+      +----------+     +---------+     +----------+
                                    |               |
                                    | errors        | transformed
                                    v               v
                              +---------+     +----------+
                              | Error   |     |Transform |
                              | Log     |     | Records  |
                              +---------+     +----------+
                                                  |
                                                  v
 [5]              [6]              [7]              [8]
+----------+   +----------+   +----------+     +----------+
|          |   |          |   |          |     |          |
| Dedup    |-->| False    |-->| Output   |---->| Quality  |
|          |   | Positive |   | Generate |     | Tests    |
| Hash     |   | Control  |   |          |     |          |
| Content  |   |          |   | 16+ Fmt  |     | Valid    |
| Seen Map |   | Benign   |   |          |     | Schema   |
|          |   | Whitelist|   |          |     | Stats    |
+----------+   +----------+   +----------+     +----------+
                                    |               |
                                    | files         | report
                                    v               v
                              +----------+     +----------+
                              |          |     |          |
                              | Publish  |     | Quality  |
                              |          |     | Report   |
                              | GitHub   |     |          |
                              | Release  |     | Metrics  |
                              | PyPI     |     | Dashboard|
                              |          |     |          |
                              +----------+     +----------+
```

## Aşama 1: API İndirme

```
+---------------------------------------------------+
|  STAGE 1: API Download                            |
+---------------------------------------------------+
|                                                   |
|  Input:  API endpoint configuration               |
|  Output: Raw JSON response per page               |
|                                                   |
|  Process:                                         |
|  1. Resolve API base URL                          |
|  2. Query total record count                      |
|  3. Calculate pagination (ceil(total/per_page))   |
|  4. Fetch all pages concurrently (semaphore=5)    |
|  5. Store raw responses                           |
|                                                   |
|  Rate Limiting:                                   |
|  - Max 5 concurrent requests                      |
|  - Min 100ms between sequential requests          |
|  - Exponential backoff on 429/503                 |
|                                                   |
|  Data Volume:                                     |
|  - ~483,690 records (as of 2025)                  |
|  - 500 records per page                           |
|  - ~968 API calls for full fetch                  |
|                                                   |
+---------------------------------------------------+
```

## Aşama 2: Ham Veri Deposu

```
+---------------------------------------------------+
|  STAGE 2: Raw Data Store                          |
+---------------------------------------------------+
|                                                   |
|  Input:  Raw JSON API responses                   |
|  Output: Parsed record list (unvalidated)         |
|                                                   |
|  Schema:                                          |
|  {                                                |
|    "data": [                                      |
|      {                                            |
|        "id": int,                                 |
|        "type": str,                               |
|        "value": str,                              |
|        "first_seen": str,                         |
|        "last_seen": str,                          |
|        "status": str                              |
|      }                                            |
|    ],                                             |
|    "meta": {                                      |
|      "total": int,                                |
|      "page": int,                                 |
|      "per_page": int                              |
|    }                                              |
|  }                                                |
|                                                   |
|  Retention: In-memory during processing           |
|  Persistence: Optional local cache (JSON)         |
|                                                   |
+---------------------------------------------------+
```

## Aşama 3: Doğrulama

```
+---------------------------------------------------+
|  STAGE 3: Validation                              |
+---------------------------------------------------+
|                                                   |
|  Input:  Raw parsed records                       |
|  Output: Validated records + error report         |
|                                                   |
|  Checks:                                          |
|  +------------------------------------------------+
|  | Rule                    | Action               |
|  +------------------------------------------------+
|  | Required fields present | Reject if missing    |
|  | ID is integer > 0      | Reject if invalid     |
|  | Type in enum set       | Reject if unknown     |
|  | Value non-empty string | Reject if empty       |
|  | Value length <= 2048   | Reject if too long    |
|  | No null bytes          | Reject if contains    |
|  | No control characters  | Strip or reject       |
|  | Date format valid      | Reject if malformed   |
|  | Status in valid set    | Map unknown to default|
|  +------------------------------------------------+
|                                                   |
|  Output:                                          |
|  - valid_records: List[IOCRecord]                 |
|  - invalid_records: List[ValidationError]         |
|  - validation_stats: ValidationReport             |
|                                                   |
+---------------------------------------------------+
```

## Aşama 4: Normalleştirme

```
+---------------------------------------------------+
|  STAGE 4: Normalization                           |
+---------------------------------------------------+
|                                                   |
|  Input:  Validated records                        |
|  Output: Normalized records (canonical form)      |
|                                                   |
|  Transformations by type:                         |
|                                                   |
|  domain:                                         |
|  - Lowercase                                      |
|  - Trim whitespace                               |
|  - Punycode encode (IDN)                         |
|  - Remove trailing dots                           |
|  - Validate against RFC 1035/1123                |
|                                                   |
|  ip:                                             |
|  - Strip whitespace                              |
|  - Validate against ipaddress module             |
|  - Expand compressed IPv6                        |
|  - Remove zone IDs                               |
|                                                   |
|  ip6:                                            |
|  - Compress to shortest form                     |
|  - Lowercase hex                                 |
|  - Validate full expansion                       |
|                                                   |
|  ip6net:                                         |
|  - Normalize prefix length                       |
|  - Validate CIDR notation                        |
|  - Expand network address                        |
|                                                   |
|  url:                                            |
|  - Percent-encode special chars                  |
|  - Normalize scheme to lowercase                 |
|  - Remove default ports (80/443)                 |
|  - Decode unnecessary percent-encoding           |
|  - Sort query parameters                         |
|  - Remove fragment identifiers                   |
|  - Remove tracking parameters (utm_*)            |
|                                                   |
|  Metadata:                                        |
|  - Standardize date format to ISO 8601           |
|  - Normalize status enum                          |
|  - Add processing timestamp                      |
|                                                   |
+---------------------------------------------------+
```

## Aşama 5: Tekilleştirme

```
+---------------------------------------------------+
|  STAGE 5: Deduplication                           |
+---------------------------------------------------+
|                                                   |
|  Input:  Normalized records                       |
|  Output: Unique records + dedup report            |
|                                                   |
|  Strategy:                                        |
|  +------------------------------------------------+
|  | Level 1: Exact Match                          |
|  | - Hash(type + normalized_value)               |
|  | - O(1) lookup in seen set                     |
|  +------------------------------------------------+
|  | Level 2: Semantic Match                       |
|  | - URL: ignore query params, fragments         |
|  | - IP: equivalent notations                    |
|  | - Domain: www prefix equivalence              |
|  +------------------------------------------------+
|  | Level 3: Subdomain Dedup                      |
|  | - *.evil.com deduped to evil.com              |
|  | - Configurable depth                          |
|  +------------------------------------------------+
|                                                   |
|  Merge Policy:                                    |
|  - Keep earliest first_seen                      |
|  - Keep latest last_seen                         |
|  - Union of status flags                         |
|  - Preserve source attribution                   |
|                                                   |
|  Statistics:                                      |
|  - Total input records                           |
|  - Duplicates removed                            |
|  - Dedup ratio                                   |
|  - Per-type breakdown                            |
|                                                   |
+---------------------------------------------------+
```

## Aşama 6: Yanlış Pozitif Kontrolü

```
+---------------------------------------------------+
|  STAGE 6: False Positive Control                  |
+---------------------------------------------------+
|                                                   |
|  Input:  Deduplicated records                     |
|  Output: Verified records + FP report             |
|                                                   |
|  Whitelist Checks:                                |
|  +------------------------------------------------+
|  | Check                        | Action         |
|  +------------------------------------------------+
|  | Known benign domains         | Flag/Exclude   |
|  | CDN infrastructure           | Flag           |
|  | Major cloud providers        | Flag           |
|  | Government domains           | Flag           |
|  | Popular websites             | Flag           |
|  +------------------------------------------------+
|                                                   |
|  Heuristics:                                      |
|  - Newly registered domains (< 30 days)          |
|  - High-entropy subdomains (DGA detection)       |
|  - IP address in private ranges                   |
|  - Reserved TLD (.local, .test, .example)        |
|  - Self-referencing values                        |
|                                                   |
|  Configuration:                                   |
|  - Whitelist file: config/whitelist.txt           |
|  - Strict mode: reject all flagged                |
|  - Advisory mode: flag but include                |
|                                                   |
+---------------------------------------------------+
```

## Aşama 7: Çıktı Üretimi

```
+---------------------------------------------------+
|  STAGE 7: Output Generation                      |
+---------------------------------------------------+
|                                                   |
|  Input:  Verified records                         |
|  Output: 16+ formatted output files               |
|                                                   |
|  Output Formats:                                  |
|  +------------------------------------------------+
|  | Format         | Extension  | Use Case        |
|  +------------------------------------------------+
|  | JSON           | .json      | General         |
|  | STIX 2.1       | .stix.json | Interop         |
|  | CSV            | .csv       | Spreadsheet     |
|  | MISP           | .misp.json | MISP platform   |
|  | OpenIOC        | .ioc       | FireEye/Trellix |
|  | Sigma          | .yml       | SIEM rules      |
|  | YARA           | .yar       | Malware detect  |
|  | CEF            | .cef       | Syslog/CEF      |
|  | LEEF           | .leef      | IBM QRadar      |
|  | Syslog         | .log       | Generic SIEM    |
|  | HTML           | .html      | Human report    |
|  | Markdown       | .md        | Documentation   |
|  | PDF            | .pdf       | Formal report   |
|  | Splunk         | .spl       | Splunk import   |
|  | QRadar         | .json      | QRadar import   |
|  | Elastic NDJSON | .ndjson    | Elasticsearch   |
|  | Grafana        | .json      | Dashboard       |
|  +------------------------------------------------+
|                                                   |
|  Each format includes:                            |
|  - Header with metadata                           |
|  - Processing timestamp                           |
|  - Source attribution                              |
|  - Record count                                    |
|                                                   |
+---------------------------------------------------+
```

## Aşama 8: Kalite Testleri

```
+---------------------------------------------------+
|  STAGE 8: Quality Tests                           |
+---------------------------------------------------+
|                                                   |
|  Input:  All output files                         |
|  Output: Quality report + pass/fail               |
|                                                   |
|  Test Categories:                                 |
|  +------------------------------------------------+
|  | Test                     | Threshold          |
|  +------------------------------------------------+
|  | Schema validity          | 100% pass          |
|  | Format conformance       | 100% pass          |
|  | Round-trip consistency   | JSON=JSON          |
|  | Record count match       | input == output    |
|  | No duplicate IOCs        | 0 duplicates       |
|  | Field completeness       | >99% non-null      |
|  | Date range validity      | All dates parse    |
|  | Type distribution        | Matches expected   |
|  | Output file sizes        | >0 bytes           |
|  | Encoding (UTF-8)         | Valid UTF-8        |
|  +------------------------------------------------+
|                                                   |
|  Report:                                          |
|  - Total tests run                                |
|  - Tests passed / failed                          |
|  - Coverage percentage                            |
|  - Performance metrics                            |
|  - Anomaly detection results                      |
|                                                   |
+---------------------------------------------------+
```

## Aşama 9: Yayınlama

```
+---------------------------------------------------+
|  STAGE 9: Publication                             |
+---------------------------------------------------+
|                                                   |
|  Input:  Quality-assured output files             |
|  Output: Published artifacts                      |
|                                                   |
|  Channels:                                        |
|  +------------------------------------------------+
|  | Channel          | Trigger      | Format      |
|  +------------------------------------------------+
|  | GitHub Release   | Tag push     | All formats |
|  | GitHub Actions   | On success   | Artifacts   |
|  | PyPI             | Tag push     | Package     |
|  | Local filesystem | Always       | All formats |
|  +------------------------------------------------+
|                                                   |
|  Release Artifacts:                               |
|  - tc-sgb-{version}.tar.gz                       |
|  - tc_sgb-{version}-py3-none-any.whl             |
|  - output/*.json                                  |
|  - output/*.csv                                   |
|  - output/*.stix.json                             |
|  - output/report.html                             |
|                                                   |
+---------------------------------------------------+
```

## Hata İşleme Akışı

```
                    +----------+
                    |  Error   |
                    | Detected |
                    +----------+
                         |
              +----------+----------+
              |                     |
              v                     v
        +----------+          +----------+
        | Recoverable|        | Fatal     |
        |            |        |           |
        +----------+          +----------+
              |                     |
              v                     v
        +----------+          +----------+
        | Retry with|        | Abort     |
        | backoff   |        | Pipeline  |
        | (max 3)   |        |           |
        +----------+          +----------+
              |                     |
              v                     v
        +----------+          +----------+
        | Success?  |        | Error     |
        |           |        | Report    |
        +----------+          +----------+
           |      |              |
           v      v              v
       +------+ +------+   +----------+
       | Continue| Abort|   | Exit     |
       |         |      |   | Code 1   |
       +------+ +------+   +----------+
```

## Veri Kökeni

Her kayıt, hat boyunca köken meta verilerini taşır:

```json
{
  "lineage": {
    "source": "tc-sgb-api",
    "fetch_time": "2025-01-15T10:30:00Z",
    "page": 42,
    "raw_hash": "sha256:abc123...",
    "validation": {
      "passed": true,
      "checks": 8,
      "timestamp": "2025-01-15T10:30:01Z"
    },
    "normalization": {
      "transforms": ["lowercase", "trim", "punycode"],
      "timestamp": "2025-01-15T10:30:01Z"
    },
    "dedup": {
      "is_unique": true,
      "hash": "sha256:def456...",
      "timestamp": "2025-01-15T10:30:02Z"
    },
    "quality": {
      "score": 0.98,
      "flags": [],
      "timestamp": "2025-01-15T10:30:02Z"
    }
  }
}
```
