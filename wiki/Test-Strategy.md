> **Language / Dil** &nbsp;
> [EN English](#-english) &nbsp;·&nbsp; [TR Türkçe](#-türkçe)

<a id="-english"></a>

# Test Strategy

## Overview

This document defines the comprehensive testing strategy for the TC-SGB-API-to-List project, covering unit tests, integration tests, regression tests, snapshot tests, property-based tests, fuzz tests, and performance benchmarks.

## Test Pyramid

```
+=====================================================================+
|                        Test Pyramid                                  |
+=====================================================================+

                          /\
                         /  \
                        / E2E\
                       /  5%  \
                      /--------\
                     / Integration\
                    /     15%      \
                   /----------------\
                  /   Unit Tests     \
                 /       60%         \
                /--------------------\
               /   Property/Fuzz      \
              /        10%            \
             /------------------------\
            /   Performance/Load       \
           /          10%              \
          /----------------------------\
```

## Test Categories

### 1. Unit Tests (60%)

**Location**: `tests/` (flat structure, no subdirectories)

**Purpose**: Test individual modules in isolation with mocked dependencies.

| Module | File | Test Count | Focus |
|--------|------|------------|-------|
| client.py | test_client.py | ~30 | HTTP calls, retry, rate limiting |
| models.py | test_models.py | ~35 | Validation, serialization, enums |
| validator.py | test_validator.py | ~50 | All 12 validation rules |
| normalizer.py | test_normalizer.py | ~32 | Type-specific normalization |
| deduplicator.py | test_deduplicator.py | ~32 | Exact, semantic, subdomain dedup |
| quality.py | test_quality.py | ~49 | Statistics, FP detection, scoring |
| outputs.py | test_outputs.py | ~70 | All 16 output formats |
| pipeline.py | test_pipeline.py | ~37 | Orchestration, error handling |
| regression.py | test_regression.py | ~31 | Output stability |
| fuzz.py | test_fuzz.py | ~23 | Property-based & fuzz testing |
| performance.py | test_performance.py | ~18 | Throughput benchmarks |
| models.py | test_models.py | ~35 | Pydantic model validation |

**Example Unit Test**:

```python
import pytest
from scripts.src.validator import validate_ioc
from scripts.src.models import AddressRecord, IOCType


def test_valid_record_passes():
    record = AddressRecord(
        id="1",
        type=IOCType.DOMAIN,
        value="evil.com",
        first_seen="2025-01-15T10:00:00Z",
        last_seen="2025-01-20T10:00:00Z",
        status="active",
    )
    result = validate_ioc(record)
    assert result.is_valid is True
    assert len(result.errors) == 0


def test_empty_value_rejected():
    with pytest.raises(ValidationError, match="min_length"):
        AddressRecord(
            id="1",
            type=IOCType.DOMAIN,
            value="",
            first_seen="2025-01-15T10:00:00Z",
            last_seen="2025-01-20T10:00:00Z",
        )
```

---

### 2. Integration Tests (15%)

**Purpose**: Test module interactions and end-to-end flows via the pipeline orchestrator.

Integration coverage is achieved through `test_pipeline.py` which exercises the full fetch → validate → normalize → score → dedup → generate flow using mocked API responses.

---

## Test Configuration

### pytest Configuration

```toml
# pyproject.toml
[tool.pytest.ini_options]
testpaths = ["tests"]
markers = [
    "unit: Unit tests",
    "integration: Integration tests",
    "regression: Regression tests",
    "property: Property-based tests",
    "fuzz: Fuzz tests",
    "performance: Performance benchmarks",
    "slow: Slow tests (skip in CI)",
]
addopts = [
    "-ra",          # Show extra summary for all except passed
    "--strict-markers",
    "--strict-config",
    "-v",
]
```

### Coverage Configuration

```toml
# pyproject.toml
[tool.coverage.run]
source = ["scripts"]
branch = true
omit = ["tests/*"]

[tool.coverage.report]
fail_under = 90
show_missing = true
exclude_lines = [
    "pragma: no cover",
    "if TYPE_CHECKING:",
    "if __name__ == .__main__.",
]
```

### Test Fixtures

```python
# tests/conftest.py
import pytest
from scripts.src.models import IOCRecord, IOCType, IOCStatus


@pytest.fixture
def sample_ioc_record():
    """Create a valid IoC record for testing."""
    return IOCRecord(
        id=1,
        type=IOCType.DOMAIN,
        value="evil-example.com",
        first_seen="2025-01-15T10:00:00Z",
        last_seen="2025-01-20T14:30:00Z",
        status=IOCStatus.ACTIVE,
    )


@pytest.fixture
def sample_ioc_batch():
    """Create a batch of IoC records for testing."""
    return [
        IOCRecord(
            id=i,
            type=IOCType.DOMAIN,
            value=f"evil{i}.com",
            first_seen="2025-01-15T10:00:00Z",
            last_seen="2025-01-20T14:30:00Z",
            status=IOCStatus.ACTIVE,
        )
        for i in range(1, 101)
    ]


@pytest.fixture
def sample_api_response():
    """Sample API response for testing."""
    return {
        "data": [
            {
                "id": 1,
                "type": "domain",
                "value": "malicious.com",
                "first_seen": "2025-01-15T10:00:00Z",
                "last_seen": "2025-01-20T14:30:00Z",
                "status": "active",
            }
        ],
        "meta": {"total": 1, "page": 1, "per_page": 500},
    }
```

## Test Execution

### Local Development

```bash
# Run all tests
pytest

# Run unit tests only
pytest -m unit

# Run with coverage
pytest --cov=scripts --cov-report=html

# Run specific test file
pytest tests/unit/test_validator.py

# Run specific test
pytest tests/test_validator.py::test_valid_record_passes

# Run property tests with more examples
pytest -m property --hypothesis-seed=0

# Run performance benchmarks
pytest -m performance --benchmark-only
```

### CI Pipeline

```yaml
# .github/workflows/ci.yml
- name: Run unit tests
  run: pytest -m unit --cov=scripts --cov-report=xml

- name: Run integration tests
  run: pytest -m integration

- name: Run regression tests
  run: pytest -m regression

- name: Run property tests
  run: pytest -m property --hypothesis-seed=0

- name: Run performance tests
  run: pytest -m performance --benchmark-compare=0.001
```

## Quality Gates

### Minimum Requirements

| Metric | Threshold | Enforcement |
|--------|-----------|-------------|
| Code Coverage | >= 90% | CI blocks merge |
| Unit Tests | 100% pass | CI blocks merge |
| Integration Tests | 100% pass | CI blocks merge |
| Type Checking | 0 errors | CI blocks merge |
| Linting | 0 errors | CI blocks merge |
| Performance | < 10% regression | Warning only |

### Test Reporting

```
+=====================================================================+
|  Test Report Format                                                  |
+=====================================================================+
|                                                                     |
|  Unit Tests:        45 passed, 0 failed                             |
|  Integration:        8 passed, 0 failed                             |
|  Regression:        12 passed, 0 failed                             |
|  Property:          20 passed, 0 failed (1000 examples each)        |
|  Fuzz:               5 passed, 0 crashes                            |
|  Performance:        6 passed, 0 regressions                        |
|                                                                     |
|  Coverage: 94.2% (branch)                                           |
|                                                                     |
|  Duration: 45.2s                                                    |
+=====================================================================+
```

## Mock Strategy

### API Mocking

```python
# Use pytest-httpserver for API mocking
@pytest.fixture
def api_mock(httpserver):
    httpserver.expect_request("/api/v1/ioc").respond_with_json({...})
    return httpserver
```

### File System Mocking

```python
# Use pytest tmp_path for file system isolation
def test_output_generation(tmp_path):
    files = generate_all(records, tmp_path)
    assert len(files) > 0
```

### Time Mocking

```python
# Use freezegun for deterministic timestamps
from freezegun import freeze_time


@freeze_time("2025-01-20T12:00:00Z")
def test_processing_timestamp():
    pipeline = Pipeline()
    result = pipeline.run()
    assert result.end_time == datetime(2025, 1, 20, 12, 0, 0)
```

<a id="-türkçe"></a>

# Test Stratejisi

## Genel Bakış

Bu belge, TC-SGB-API-to-List projesi için kapsamlı test stratejisini tanımlar; birim testleri, entegrasyon testleri, regresyon testleri, anlık görüntü testleri, özellik tabanlı testler, fuzz testleri ve performans karşılaştırmalarını kapsar.

## Test Piramidi

```
+=====================================================================+
|                        Test Piramidi                                  |
+=====================================================================+

                          /\
                         /  \
                        / E2E\
                       /  5%  \
                      /--------\
                     / Entegrasyon\
                    /     15%      \
                   /----------------\
                  /   Birim Testler  \
                 /       60%         \
                /--------------------\
               /   Özellik/Fuzz       \
              /        10%            \
             /------------------------\
            /   Performans/Yük         \
           /          10%              \
          /----------------------------\
```

## Test Kategorileri

### 1. Birim Testleri (%60)

**Konum**: `tests/` (düz yapı, alt dizin yok)

**Amaç**: Bağımlılıkları taklit ederek bireysel modülleri izole olarak test etmek.

| Modül | Dosya | Test Sayısı | Odak |
|--------|------|------------|-------|
| client.py | test_client.py | ~30 | HTTP çağrıları, yeniden deneme, hız sınırlama |
| models.py | test_models.py | ~35 | Doğrulama, serileştirme, enum'lar |
| validator.py | test_validator.py | ~50 | Tüm 12 doğrulama kuralı |
| normalizer.py | test_normalizer.py | ~32 | Türe özgü normalizasyon |
| deduplicator.py | test_deduplicator.py | ~32 | Kesin, anlamsal, alt alan adı tekrar kontrolü |
| quality.py | test_quality.py | ~49 | İstatistikler, yanlış pozitif algılama, puanlama |
| outputs.py | test_outputs.py | ~70 | Tüm 16 çıkış biçimi |
| pipeline.py | test_pipeline.py | ~37 | Orkestrasyon, hata işleme |
| changelog.py | test_changelog.py | ~15 | IoC farkı ve değişiklik günlüğü |

**Örnek Birim Testi**:

```python
import pytest
from scripts.src.validator import validate_ioc
from scripts.src.models import AddressRecord, IOCType


def test_valid_record_passes():
    record = AddressRecord(
        id="1",
        type=IOCType.DOMAIN,
        value="evil.com",
        first_seen="2025-01-15T10:00:00Z",
        last_seen="2025-01-20T10:00:00Z",
        status="active",
    )
    result = validate_ioc(record)
    assert result.is_valid is True
    assert len(result.errors) == 0


def test_empty_value_rejected():
    with pytest.raises(ValidationError, match="min_length"):
        AddressRecord(
            id="1",
            type=IOCType.DOMAIN,
            value="",
            first_seen="2025-01-15T10:00:00Z",
            last_seen="2025-01-20T10:00:00Z",
        )
```

---

### 2. Entegrasyon Testleri (%15)

**Amaç**: Gerçek veya kaydedilmiş API yanıtlarıyla modül etkileşimlerini ve uçtan uca akışları test etmek.

Entegrasyon kapsamı `test_pipeline.py` aracılığıyla sağlanır; bu dosya sahte API yanıtlarıyla tam çekme → doğrulama → normalleştirme → puanlama → tekrar kaldırma → üretme akışını test eder.

---

## Test Yapılandırması

### pytest Yapılandırması

```toml
# pyproject.toml
[tool.pytest.ini_options]
testpaths = ["tests"]
markers = [
    "unit: Unit tests",
    "integration: Integration tests",
    "regression: Regression tests",
    "property: Property-based tests",
    "fuzz: Fuzz tests",
    "performance: Performance benchmarks",
    "slow: Slow tests (skip in CI)",
]
addopts = [
    "-ra",          # Show extra summary for all except passed
    "--strict-markers",
    "--strict-config",
    "-v",
]
```

### Kapsam Yapılandırması

```toml
# pyproject.toml
[tool.coverage.run]
source = ["scripts"]
branch = true
omit = ["tests/*"]

[tool.coverage.report]
fail_under = 90
show_missing = true
exclude_lines = [
    "pragma: no cover",
    "if TYPE_CHECKING:",
    "if __name__ == .__main__.",
]
```

### Test Fixture'ları

```python
# tests/conftest.py
import pytest
from scripts.src.models import IOCRecord, IOCType, IOCStatus


@pytest.fixture
def sample_ioc_record():
    """Create a valid IoC record for testing."""
    return IOCRecord(
        id=1,
        type=IOCType.DOMAIN,
        value="evil-example.com",
        first_seen="2025-01-15T10:00:00Z",
        last_seen="2025-01-20T14:30:00Z",
        status=IOCStatus.ACTIVE,
    )


@pytest.fixture
def sample_ioc_batch():
    """Create a batch of IoC records for testing."""
    return [
        IOCRecord(
            id=i,
            type=IOCType.DOMAIN,
            value=f"evil{i}.com",
            first_seen="2025-01-15T10:00:00Z",
            last_seen="2025-01-20T14:30:00Z",
            status=IOCStatus.ACTIVE,
        )
        for i in range(1, 101)
    ]


@pytest.fixture
def sample_api_response():
    """Sample API response for testing."""
    return {
        "data": [
            {
                "id": 1,
                "type": "domain",
                "value": "malicious.com",
                "first_seen": "2025-01-15T10:00:00Z",
                "last_seen": "2025-01-20T14:30:00Z",
                "status": "active",
            }
        ],
        "meta": {"total": 1, "page": 1, "per_page": 500},
    }
```

## Test Çalıştırma

### Yerel Geliştirme

```bash
# Tüm testleri çalıştır
pytest

# Kapsam ile çalıştır
pytest --cov=scripts --cov-report=html

# Belirli test dosyası
pytest tests/test_validator.py

# Belirli test
pytest tests/test_validator.py::test_valid_record_passes
```

### CI Pipeline

```yaml
# .github/workflows/ci.yml
- name: Run tests
  run: pytest tests/ -v --tb=short
```

## Kalite Kapıları

### Minimum Gereksinimler

| Metrik | Eşik | Uygulama |
|--------|-----------|-------------|
| Kod Kapsamı | >= %100 | CI birleştirmeyi engeller (testlerin kodun her satırını çalıştırıp çalıştırmadığını ölçer) |
| Birim Testleri | %100 geçiş | CI birleştirmeyi engeller |
| Entegrasyon Testleri | %100 geçiş | CI birleştirmeyi engeller |
| Tip Denetimi | 0 hata | CI birleştirmeyi engeller |
| Linting | 0 hata | CI birleştirmeyi engeller |
| Performans | < %10 regresyon | Yalnızca uyarı |

### Test Raporlama

```
+=====================================================================+
|  Test Raporu Biçimi                                                  |
+=====================================================================+
|                                                                     |
|  Toplam: 452 test, 0 başarısız                                     |
|                                                                     |
|  Kapsam: %99 (testlerin kodun her satırını çalıştırıp               |
|  çalıştırmadığını ölçer)                                           |
|                                                                     |
|  Süre: 45.2s                                                        |
+=====================================================================+
```

## Taklit Stratejisi

### API Taklidi

```python
# Use pytest-httpserver for API mocking
@pytest.fixture
def api_mock(httpserver):
    httpserver.expect_request("/api/v1/ioc").respond_with_json({...})
    return httpserver
```

### Dosya Sistemi Taklidi

```python
# Use pytest tmp_path for file system isolation
def test_output_generation(tmp_path):
    files = generate_all(records, tmp_path)
    assert len(files) > 0
```

### Zaman Taklidi

```python
# Use freezegun for deterministic timestamps
from freezegun import freeze_time


@freeze_time("2025-01-20T12:00:00Z")
def test_processing_timestamp():
    pipeline = Pipeline()
    result = pipeline.run()
    assert result.end_time == datetime(2025, 1, 20, 12, 0, 0)
```
