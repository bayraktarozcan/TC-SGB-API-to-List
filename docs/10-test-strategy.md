[English](#english) | [Türkçe](#turkish)

<a id="english"></a>

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

**Location**: `tests/unit/`

**Purpose**: Test individual modules in isolation with mocked dependencies.

| Module | File | Test Count | Focus |
|--------|------|------------|-------|
| client.py | test_client.py | ~8 | HTTP calls, retry, rate limiting |
| models.py | test_models.py | ~10 | Validation, serialization, enums |
| validator.py | test_validator.py | ~15 | All 12 validation rules |
| normalizer.py | test_normalizer.py | ~12 | Type-specific normalization |
| deduplicator.py | test_deduplicator.py | ~10 | Exact, semantic, subdomain dedup |
| quality.py | test_quality.py | ~8 | Statistics, FP detection, scoring |
| outputs.py | test_outputs.py | ~20 | All 16+ output formats |
| pipeline.py | test_pipeline.py | ~5 | Orchestration, error handling |

**Example Unit Test**:

```python
import pytest
from tc_sgb.validator import IOCValidator
from tc_sgb.models import IOCRecord, IOCType, IOCStatus

class TestIOCValidator:
    def setup_method(self):
        self.validator = IOCValidator()

    def test_valid_record_passes(self):
        record = IOCRecord(
            id=1,
            type=IOCType.DOMAIN,
            value="evil.com",
            first_seen="2025-01-15T10:00:00Z",
            last_seen="2025-01-20T10:00:00Z",
            status=IOCStatus.ACTIVE,
        )
        result = self.validator.validate_record(record)
        assert result.is_valid is True
        assert len(result.errors) == 0

    def test_empty_value_rejected(self):
        with pytest.raises(ValidationError, match="min_length"):
            IOCRecord(
                id=1,
                type=IOCType.DOMAIN,
                value="",
                first_seen="2025-01-15T10:00:00Z",
                last_seen="2025-01-20T10:00:00Z",
            )

    def test_invalid_type_rejected(self):
        with pytest.raises(ValidationError):
            IOCRecord(
                id=1,
                type="malware",
                value="evil.com",
                first_seen="2025-01-15T10:00:00Z",
                last_seen="2025-01-20T10:00:00Z",
            )

    def test_null_bytes_rejected(self):
        record = IOCRecord(
            id=1,
            type=IOCType.DOMAIN,
            value="evil\x00.com",
            first_seen="2025-01-15T10:00:00Z",
            last_seen="2025-01-20T10:00:00Z",
        )
        result = self.validator.validate_record(record)
        assert result.is_valid is False
```

---

### 2. Integration Tests (15%)

**Location**: `tests/integration/`

**Purpose**: Test module interactions and end-to-end flows with real or recorded API responses.

| Test | File | Focus |
|------|------|-------|
| API Integration | test_api_integration.py | Live API connection (optional) |
| End-to-End | test_end_to_end.py | Full pipeline execution |
| Format Roundtrip | test_format_roundtrip.py | JSON → Process → Output → Parse |

**Example Integration Test**:

```python
import pytest
from tc_sgb.pipeline import ThreatIntelPipeline
from tc_sgb.config import load_config

@pytest.mark.integration
class TestEndToEnd:
    @pytest.fixture
    def config(self):
        return load_config("config/default.yaml")

    @pytest.fixture
    def mock_api_response(self, httpserver):
        """Mock API server for testing."""
        httpserver.expect_request("/api/v1/ioc").respond_with_json({
            "data": [
                {
                    "id": 1,
                    "type": "domain",
                    "value": "evil.com",
                    "first_seen": "2025-01-15T10:00:00Z",
                    "last_seen": "2025-01-20T10:00:00Z",
                    "status": "active",
                }
            ],
            "meta": {"total": 1, "page": 1, "per_page": 500},
        })
        return httpserver

    @pytest.mark.asyncio
    async def test_full_pipeline(self, config, mock_api_response):
        config.api.base_url = mock_api_response.url_for("/api/v1")
        pipeline = ThreatIntelPipeline(config)
        result = await pipeline.run()

        assert result.success is True
        assert result.output_record_count == 1
        assert len(result.output_files) > 0
```

---

### 3. Regression Tests (10%)

**Location**: `tests/regression/`

**Purpose**: Ensure output stability across versions using snapshot testing.

| Test | Focus |
|------|-------|
| Output Snapshot | JSON output matches expected structure |
| STIX Format | STIX 2.1 output conformance |
| CSV Format | CSV output matches expected |
| Performance Baseline | No performance regression |

See [11-regression-strategy.md](11-regression-strategy.md) for details.

---

### 4. Property-Based Tests (10%)

**Location**: `tests/property/`

**Purpose**: Verify invariants hold for any input using Hypothesis.

| Test | Property |
|------|----------|
| Normalization | `normalize(normalize(x)) == normalize(x)` (idempotency) |
| Deduplication | `len(dedup(records)) <= len(records)` |
| Validation | Valid records pass all checks |
| Output | All formats produce valid output |

**Example Property Test**:

```python
from hypothesis import given, strategies as st
from tc_sgb.normalizer import IOCNormalizer

class TestNormalizationProperties:
    @given(st.text(min_size=1, max_size=2048))
    def test_idempotency(self, value):
        """Normalizing twice should produce same result."""
        normalizer = IOCNormalizer()
        first = normalizer._normalize_domain(value)
        second = normalizer._normalize_domain(first)
        assert first == second

    @given(st.text(min_size=1, max_size=2048))
    def test_output_always_lowercase(self, value):
        """Domain normalization always produces lowercase."""
        normalizer = IOCNormalizer()
        result = normalizer._normalize_domain(value)
        assert result == result.lower()
```

---

### 5. Fuzz Tests (10%)

**Location**: `tests/fuzz/`

**Purpose**: Discover crashes and edge cases with random/malformed inputs.

| Test | Target | Strategy |
|------|--------|----------|
| fuzz_validator.py | IOCValidator | Random strings, malformed records |
| fuzz_normalizer.py | IOCNormalizer | Edge cases, Unicode, huge inputs |
| fuzz_client.py | SGBAPIClient | Malformed responses, timeouts |

**Example Fuzz Test**:

```python
from hypothesis import given, strategies as st, settings
from tc_sgb.validator import IOCValidator

class TestValidatorFuzz:
    @given(st.binary(min_size=0, max_size=10000))
    @settings(max_examples=1000)
    def test_validator_never_crashes(self, data):
        """Validator should handle any input without crashing."""
        validator = IOCValidator()
        try:
            # Attempt to parse as IOCRecord
            record = IOCRecord.model_validate_json(data)
            result = validator.validate_record(record)
            # Should always produce a valid result
            assert hasattr(result, 'is_valid')
        except (ValidationError, JSONDecodeError):
            # Expected for invalid input - should not crash
            pass
```

---

### 6. Performance Tests (10%)

**Location**: `tests/performance/`

**Purpose**: Ensure performance meets requirements and detect regressions.

| Benchmark | Target | Threshold |
|-----------|--------|-----------|
| 100 IOCs | Full pipeline | < 1s |
| 1K IOCs | Full pipeline | < 5s |
| 10K IOCs | Full pipeline | < 30s |
| 100K IOCs | Full pipeline | < 5min |
| 1M IOCs | Full pipeline | < 30min |

See [12-performance-strategy.md](12-performance-strategy.md) for details.

---

## Test Configuration

### pytest Configuration

```toml
# pyproject.toml
[tool.pytest.ini_options]
testpaths = ["tests"]
asyncio_mode = "auto"
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
    "--tb=short",   # Short traceback format
]
```

### Coverage Configuration

```toml
# pyproject.toml
[tool.coverage.run]
source = ["tc_sgb"]
branch = true
omit = ["tests/*", "scripts/*"]

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
from tc_sgb.models import IOCRecord, IOCType, IOCStatus

@pytest.fixture
def sample_ioc_record():
    """Create a valid IOC record for testing."""
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
    """Create a batch of IOC records for testing."""
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
pytest --cov=tc_sgb --cov-report=html

# Run specific test file
pytest tests/unit/test_validator.py

# Run specific test
pytest tests/unit/test_validator.py::TestIOCValidator::test_valid_record_passes

# Run property tests with more examples
pytest -m property --hypothesis-seed=0

# Run performance benchmarks
pytest -m performance --benchmark-only
```

### CI Pipeline

```yaml
# .github/workflows/ci.yml
- name: Run unit tests
  run: pytest -m unit --cov=tc_sgb --cov-report=xml

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
    engine = OutputEngine(config)
    files = engine.generate_all(records, tmp_path)
    assert all(f.path.exists() for f in files)
```

### Time Mocking

```python
# Use freezegun for deterministic timestamps
from freezegun import freeze_time

@freeze_time("2025-01-20T12:00:00Z")
def test_processing_timestamp():
    pipeline = ThreatIntelPipeline(config)
    result = pipeline.run()
    assert result.end_time == datetime(2025, 1, 20, 12, 0, 0)
```

<a id="turkish"></a>

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

**Konum**: `tests/unit/`

**Amaç**: Bağımlılıkları taklit ederek bireysel modülleri izole olarak test etmek.

| Modül | Dosya | Test Sayısı | Odak |
|--------|------|------------|-------|
| client.py | test_client.py | ~8 | HTTP çağrıları, yeniden deneme, hız sınırlama |
| models.py | test_models.py | ~10 | Doğrulama, serileştirme, enum'lar |
| validator.py | test_validator.py | ~15 | Tüm 12 doğrulama kuralı |
| normalizer.py | test_normalizer.py | ~12 | Türe özgü normalizasyon |
| deduplicator.py | test_deduplicator.py | ~10 | Kesin, anlamsal, alt alan adı tekrar kontrolü |
| quality.py | test_quality.py | ~8 | İstatistikler, yanlış pozitif algılama, puanlama |
| outputs.py | test_outputs.py | ~20 | Tüm 16+ çıkış biçimi |
| pipeline.py | test_pipeline.py | ~5 | Orkestrasyon, hata işleme |

**Örnek Birim Testi**:

```python
import pytest
from tc_sgb.validator import IOCValidator
from tc_sgb.models import IOCRecord, IOCType, IOCStatus

class TestIOCValidator:
    def setup_method(self):
        self.validator = IOCValidator()

    def test_valid_record_passes(self):
        record = IOCRecord(
            id=1,
            type=IOCType.DOMAIN,
            value="evil.com",
            first_seen="2025-01-15T10:00:00Z",
            last_seen="2025-01-20T10:00:00Z",
            status=IOCStatus.ACTIVE,
        )
        result = self.validator.validate_record(record)
        assert result.is_valid is True
        assert len(result.errors) == 0

    def test_empty_value_rejected(self):
        with pytest.raises(ValidationError, match="min_length"):
            IOCRecord(
                id=1,
                type=IOCType.DOMAIN,
                value="",
                first_seen="2025-01-15T10:00:00Z",
                last_seen="2025-01-20T10:00:00Z",
            )

    def test_invalid_type_rejected(self):
        with pytest.raises(ValidationError):
            IOCRecord(
                id=1,
                type="malware",
                value="evil.com",
                first_seen="2025-01-15T10:00:00Z",
                last_seen="2025-01-20T10:00:00Z",
            )

    def test_null_bytes_rejected(self):
        record = IOCRecord(
            id=1,
            type=IOCType.DOMAIN,
            value="evil\x00.com",
            first_seen="2025-01-15T10:00:00Z",
            last_seen="2025-01-20T10:00:00Z",
        )
        result = self.validator.validate_record(record)
        assert result.is_valid is False
```

---

### 2. Entegrasyon Testleri (%15)

**Konum**: `tests/integration/`

**Amaç**: Gerçek veya kaydedilmiş API yanıtlarıyla modül etkileşimlerini ve uçtan uca akışları test etmek.

| Test | Dosya | Odak |
|------|------|-------|
| API Entegrasyonu | test_api_integration.py | Canlı API bağlantısı (isteğe bağlı) |
| Uçtan Uca | test_end_to_end.py | Tam pipeline çalıştırma |
| Biçim Turu | test_format_roundtrip.py | JSON → İşle → Çıktı → Ayrıştır |

**Örnek Entegrasyon Testi**:

```python
import pytest
from tc_sgb.pipeline import ThreatIntelPipeline
from tc_sgb.config import load_config

@pytest.mark.integration
class TestEndToEnd:
    @pytest.fixture
    def config(self):
        return load_config("config/default.yaml")

    @pytest.fixture
    def mock_api_response(self, httpserver):
        """Mock API server for testing."""
        httpserver.expect_request("/api/v1/ioc").respond_with_json({
            "data": [
                {
                    "id": 1,
                    "type": "domain",
                    "value": "evil.com",
                    "first_seen": "2025-01-15T10:00:00Z",
                    "last_seen": "2025-01-20T10:00:00Z",
                    "status": "active",
                }
            ],
            "meta": {"total": 1, "page": 1, "per_page": 500},
        })
        return httpserver

    @pytest.mark.asyncio
    async def test_full_pipeline(self, config, mock_api_response):
        config.api.base_url = mock_api_response.url_for("/api/v1")
        pipeline = ThreatIntelPipeline(config)
        result = await pipeline.run()

        assert result.success is True
        assert result.output_record_count == 1
        assert len(result.output_files) > 0
```

---

### 3. Regresyon Testleri (%10)

**Konum**: `tests/regression/`

**Amaç**: Anlık görüntü testi kullanarak sürümler arası çıkış kararlılığını sağlamak.

| Test | Odak |
|------|-------|
| Çıktı Anlık Görüntüsü | JSON çıktısının beklenen yapıyla eşleşmesi |
| STIX Biçimi | STIX 2.1 çıktı uyumluluğu |
| CSV Biçimi | CSV çıktısının beklenen değerlerle eşleşmesi |
| Performans Temel Çizgisi | Performans regresyonu olmaması |

Ayrıntılar için [11-regression-strategy.md](11-regression-strategy.md) belgesine bakın.

---

### 4. Özellik Tabanlı Testler (%10)

**Konum**: `tests/property/`

**Amaç**: Hypothesis kullanarak herhangi bir giriş için değişmezlerin doğruluğunu sağlamak.

| Test | Özellik |
|------|----------|
| Normalizasyon | `normalize(normalize(x)) == normalize(x)` (idempotency) |
| Tekrar Kaldırma | `len(dedup(records)) <= len(records)` |
| Doğrulama | Geçerli kayıtlar tüm kontrolden geçer |
| Çıktı | Tüm biçimler geçerli çıktı üretir |

**Örnek Özellik Testi**:

```python
from hypothesis import given, strategies as st
from tc_sgb.normalizer import IOCNormalizer

class TestNormalizationProperties:
    @given(st.text(min_size=1, max_size=2048))
    def test_idempotency(self, value):
        """Normalizing twice should produce same result."""
        normalizer = IOCNormalizer()
        first = normalizer._normalize_domain(value)
        second = normalizer._normalize_domain(first)
        assert first == second

    @given(st.text(min_size=1, max_size=2048))
    def test_output_always_lowercase(self, value):
        """Domain normalization always produces lowercase."""
        normalizer = IOCNormalizer()
        result = normalizer._normalize_domain(value)
        assert result == result.lower()
```

---

### 5. Fuzz Testleri (%10)

**Konum**: `tests/fuzz/`

**Amaç**: Rastgele/hatalı girişlerle çökme ve kenar durumlarını keşfetmek.

| Test | Hedef | Strateji |
|------|--------|----------|
| fuzz_validator.py | IOCValidator | Rastgele dizgeler, hatalı kayıtlar |
| fuzz_normalizer.py | IOCNormalizer | Kenar durumları, Unicode, devasa girişler |
| fuzz_client.py | SGBAPIClient | Hatalı yanıtlar, zaman aşımaları |

**Örnek Fuzz Testi**:

```python
from hypothesis import given, strategies as st, settings
from tc_sgb.validator import IOCValidator

class TestValidatorFuzz:
    @given(st.binary(min_size=0, max_size=10000))
    @settings(max_examples=1000)
    def test_validator_never_crashes(self, data):
        """Validator should handle any input without crashing."""
        validator = IOCValidator()
        try:
            # Attempt to parse as IOCRecord
            record = IOCRecord.model_validate_json(data)
            result = validator.validate_record(record)
            # Should always produce a valid result
            assert hasattr(result, 'is_valid')
        except (ValidationError, JSONDecodeError):
            # Expected for invalid input - should not crash
            pass
```

---

### 6. Performans Testleri (%10)

**Konum**: `tests/performance/`

**Amaç**: Performansın gereksinimleri karşılamasını sağlamak ve regresyonları tespit etmek.

| Karşılaştırma | Hedef | Eşik |
|-----------|--------|-----------|
| 100 IOC | Tam pipeline | < 1s |
| 1B IOC | Tam pipeline | < 5s |
| 10B IOC | Tam pipeline | < 30s |
| 100B IOC | Tam pipeline | < 5dk |
| 1M IOC | Tam pipeline | < 30dk |

Ayrıntılar için [12-performance-strategy.md](12-performance-strategy.md) belgesine bakın.

---

## Test Yapılandırması

### pytest Yapılandırması

```toml
# pyproject.toml
[tool.pytest.ini_options]
testpaths = ["tests"]
asyncio_mode = "auto"
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
    "--tb=short",   # Short traceback format
]
```

### Kapsam Yapılandırması

```toml
# pyproject.toml
[tool.coverage.run]
source = ["tc_sgb"]
branch = true
omit = ["tests/*", "scripts/*"]

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
from tc_sgb.models import IOCRecord, IOCType, IOCStatus

@pytest.fixture
def sample_ioc_record():
    """Create a valid IOC record for testing."""
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
    """Create a batch of IOC records for testing."""
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
# Run all tests
pytest

# Run unit tests only
pytest -m unit

# Run with coverage
pytest --cov=tc_sgb --cov-report=html

# Run specific test file
pytest tests/unit/test_validator.py

# Run specific test
pytest tests/unit/test_validator.py::TestIOCValidator::test_valid_record_passes

# Run property tests with more examples
pytest -m property --hypothesis-seed=0

# Run performance benchmarks
pytest -m performance --benchmark-only
```

### CI Pipeline

```yaml
# .github/workflows/ci.yml
- name: Run unit tests
  run: pytest -m unit --cov=tc_sgb --cov-report=xml

- name: Run integration tests
  run: pytest -m integration

- name: Run regression tests
  run: pytest -m regression

- name: Run property tests
  run: pytest -m property --hypothesis-seed=0

- name: Run performance tests
  run: pytest -m performance --benchmark-compare=0.001
```

## Kalite Kapıları

### Minimum Gereksinimler

| Metrik | Eşik | Uygulama |
|--------|-----------|-------------|
| Kod Kapsamı | >= %90 | CI birleştirmeyi engeller |
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
|  Birim Testleri:      45 geçti, 0 başarısız                        |
|  Entegrasyon:          8 geçti, 0 başarısız                        |
|  Regresyon:           12 geçti, 0 başarısız                        |
|  Özellik:             20 geçti, 0 başarısız (her biri 1000 örnek)   |
|  Fuzz:                 5 geçti, 0 çökme                             |
|  Performans:           6 geçti, 0 regresyon                         |
|                                                                     |
|  Kapsam: %94.2 (dal)                                                |
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
    engine = OutputEngine(config)
    files = engine.generate_all(records, tmp_path)
    assert all(f.path.exists() for f in files)
```

### Zaman Taklidi

```python
# Use freezegun for deterministic timestamps
from freezegun import freeze_time

@freeze_time("2025-01-20T12:00:00Z")
def test_processing_timestamp():
    pipeline = ThreatIntelPipeline(config)
    result = pipeline.run()
    assert result.end_time == datetime(2025, 1, 20, 12, 0, 0)
```
