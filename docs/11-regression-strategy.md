[English](#english) | [Türkçe](#turkish)

<a id="english"></a>

# Regression Testing Strategy

## Overview

This document defines the regression testing approach for the TC-SGB-API-to-List project, ensuring that changes do not break existing functionality and that output remains stable across versions.

## Regression Test Types

### 1. Snapshot Testing

**Purpose**: Verify that output structure and content remain consistent across code changes.

```
+=====================================================================+
|  Snapshot Testing Flow                                               |
+=====================================================================+

  Code Change                Test Execution              Result
  +----------+             +---------------+          +----------+
  |          |             |               |          |          |
  | Modify   | ----------> | Generate      | -------->| Compare  |
  | Module   |             | New Output    |          | with     |
  |          |             |               |          | Snapshot |
  +----------+             +---------------+          +----------+
                                                           |
                                               +----------+----------+
                                               |                     |
                                               v                     v
                                         +----------+          +----------+
                                         | Match    |          | Mismatch |
                                         | PASS     |          | FAIL     |
                                         +----------+          +----------+
```

**Snapshot Files**:

```
tests/regression/snapshots/
├── expected_output.json       # Full JSON output
├── expected_stix.json         # STIX 2.1 output
├── expected_csv.csv           # CSV output
├── expected_misp.json         # MISP format
├── expected_sigma.yml         # Sigma rules
├── expected_html.html         # HTML report
├── expected_markdown.md       # Markdown report
└── metadata.json              # Snapshot metadata
```

**Snapshot Metadata**:

```json
{
  "version": "1.0.0",
  "created": "2025-01-20T12:00:00Z",
  "input_hash": "sha256:abc123...",
  "record_count": 100,
  "source": "test_fixture",
  "python_version": "3.11.7"
}
```

### 2. Output Stability Testing

**Purpose**: Ensure that the same input always produces the same output.

```python
import pytest
from tc_sgb.pipeline import ThreatIntelPipeline

@pytest.mark.regression
class TestOutputStability:
    """Verify output stability across runs."""

    @pytest.fixture
    def stable_input(self):
        """Deterministic test input."""
        return [
            {"id": 1, "type": "domain", "value": "evil.com", ...},
            {"id": 2, "type": "ip", "value": "10.0.0.1", ...},
            # ... 100 deterministic records
        ]

    def test_json_output_stable(self, stable_input, snapshot):
        """JSON output should match snapshot."""
        pipeline = ThreatIntelPipeline(config)
        result = pipeline.run_sync(stable_input)
        snapshot.assert_match(result.json_output, "expected_output.json")

    def test_stix_output_stable(self, stable_input, snapshot):
        """STIX output should match snapshot."""
        pipeline = ThreatIntelPipeline(config)
        result = pipeline.run_sync(stable_input)
        snapshot.assert_match(result.stix_output, "expected_stix.json")

    def test_csv_output_stable(self, stable_input, snapshot):
        """CSV output should match snapshot."""
        pipeline = ThreatIntelPipeline(config)
        result = pipeline.run_sync(stable_input)
        snapshot.assert_match(result.csv_output, "expected_csv.csv")
```

### 3. Behavioral Regression Testing

**Purpose**: Verify that specific behaviors are preserved after changes.

```python
@pytest.mark.regression
class TestBehavioralRegression:
    """Verify behavioral invariants."""

    def test_dedup_ratio_stable(self):
        """Deduplication ratio should remain within expected range."""
        records = load_test_dataset("dedup_test_data.json")
        result = deduplicator.deduplicate(records)
        # Should remove 5-15% duplicates
        assert 0.05 <= result.dedup_ratio <= 0.15

    def test_validation_reject_rate_stable(self):
        """Validation rejection rate should be predictable."""
        records = load_test_dataset("validation_test_data.json")
        result = validator.validate_batch(records)
        # Should reject 2-5% of records
        assert 0.02 <= result.invalid_records / result.total_records <= 0.05

    def test_output_file_count_stable(self):
        """Should always generate 16+ output files."""
        records = load_test_dataset("output_test_data.json")
        files = output_engine.generate_all(records, tmp_path)
        assert len(files) >= 16

    def test_processing_order_deterministic(self):
        """Processing order should be deterministic."""
        records = load_test_dataset("order_test_data.json")
        result1 = pipeline.run_sync(records)
        result2 = pipeline.run_sync(records)
        assert result1.output_hashes == result2.output_hashes
```

### 4. API Contract Testing

**Purpose**: Ensure the client handles API responses correctly as defined.

```python
@pytest.mark.regression
class TestAPIContract:
    """Verify API response handling contract."""

    def test_response_schema_contract(self):
        """API response must conform to expected schema."""
        response = load_test_response("api_response_sample.json")
        parsed = APIResponse(**response)
        assert parsed.meta.total > 0
        assert len(parsed.data) > 0
        assert all(r.id > 0 for r in parsed.data)

    def test_pagination_contract(self):
        """Pagination metadata must be consistent."""
        response = load_test_response("api_response_page2.json")
        parsed = APIResponse(**response)
        assert parsed.meta.page == 2
        assert parsed.meta.per_page == 500

    def test_empty_response_contract(self):
        """Empty API response must be handled gracefully."""
        response = {"data": [], "meta": {"total": 0, "page": 1, "per_page": 500}}
        parsed = APIResponse(**response)
        assert len(parsed.data) == 0
```

### 5. Format Compatibility Testing

**Purpose**: Verify that output formats are compatible with target systems.

```python
@pytest.mark.regression
class TestFormatCompatibility:
    """Verify format compatibility with target systems."""

    def test_stix_validates_against_schema(self):
        """STIX output must validate against STIX 2.1 schema."""
        import stix2
        output = generate_stix_output()
        bundle = stix2.parse(output)
        assert bundle.type == "bundle"

    def test_csv_opens_in_excel(self):
        """CSV output must be valid and Excel-compatible."""
        output = generate_csv_output()
        import csv
        reader = csv.reader(io.StringIO(output))
        rows = list(reader)
        assert len(rows) > 1  # Header + data
        assert rows[0] == ["id", "type", "value", "first_seen", "last_seen", "status"]

    def test_json_parseable(self):
        """JSON output must be valid JSON."""
        output = generate_json_output()
        import json
        parsed = json.loads(output)
        assert "data" in parsed
        assert "meta" in parsed

    def test_elastic_ndjson_format(self):
        """Elasticsearch NDJSON must have correct format."""
        output = generate_elastic_output()
        lines = output.strip().split("\n")
        for line in lines:
            action = json.loads(line.split("\t")[0])
            assert "index" in action
```

## Regression Test Data Management

### Test Dataset Versions

```
tests/regression/data/
├── v1.0.0/
│   ├── input_records.json
│   ├── expected_output.json
│   └── metadata.json
├── v1.1.0/
│   ├── input_records.json
│   ├── expected_output.json
│   └── metadata.json
└── current/
    ├── input_records.json
    └── metadata.json
```

### Dataset Creation

```python
@pytest.fixture
def regression_dataset():
    """Create deterministic regression test dataset."""
    return [
        IOCRecord(
            id=i,
            type=list(IOCType)[i % 5],
            value=f"test{i}.example.com",
            first_seen=f"2025-01-{i:02d}T10:00:00Z",
            last_seen=f"2025-01-{i:02d}T14:00:00Z",
            status=IOCStatus.ACTIVE,
        )
        for i in range(1, 101)
    ]
```

## Regression Test Execution

### Full Regression Suite

```bash
# Run all regression tests
pytest -m regression

# Run with snapshot update
pytest -m regression --snapshot-update

# Run specific regression test
pytest tests/regression/test_regression.py::TestOutputStability::test_json_output_stable

# Compare performance baseline
pytest -m performance --benchmark-compare=0.001
```

### CI Integration

```yaml
# .github/workflows/ci.yml
- name: Run regression tests
  run: |
    pytest -m regression --tb=long
    if [ $? -ne 0 ]; then
      echo "Regression tests failed!"
      echo "If intentional, update snapshots with:"
      echo "  pytest -m regression --snapshot-update"
      exit 1
    fi
```

## Snapshot Update Process

When output changes intentionally:

```bash
# 1. Review the changes
git diff tests/regression/snapshots/

# 2. Update snapshots
pytest -m regression --snapshot-update

# 3. Verify the update
pytest -m regression

# 4. Commit updated snapshots
git add tests/regression/snapshots/
git commit -m "chore: update regression snapshots for v1.1.0"
```

## Regression Test Metrics

| Metric | Target | Measurement |
|--------|--------|-------------|
| Snapshot Coverage | 100% | All output formats have snapshots |
| Behavioral Coverage | 100% | All critical behaviors tested |
| Execution Time | < 60s | Full regression suite |
| Flakiness | 0% | No intermittent failures |
| Update Frequency | Per release | Snapshots updated on version bump |

## Regression Prevention

### Pre-Merge Checks

1. **All regression tests pass** — No snapshot mismatches
2. **No behavioral changes** — Output format preserved
3. **No performance regression** — Benchmarks within threshold
4. **Code review** — Changes to core modules reviewed

### Post-Merge Monitoring

1. **Daily regression run** — Scheduled CI job
2. **Performance tracking** — Benchmark trend analysis
3. **Output monitoring** — Alert on unexpected changes
4. **Version comparison** — Diff reports between versions

<a id="turkish"></a>

# Regresyon Test Stratejisi

## Genel Bakış

Bu belge, TC-SGB-API-to-List projesi için regresyon testi yaklaşımını tanımlar; değişikliklerin mevcut işlevselliği bozmasını engeller ve sürümler arası çıktının kararlı kalmasını sağlar.

## Regresyon Test Türleri

### 1. Anlık Görüntü Testi

**Amaç**: Çıktı yapısının ve içeriğinin kod değişiklikleri boyunca tutarlı kaldığını doğrulamak.

```
+=====================================================================+
|  Anlık Görüntü Testi Akışı                                          |
+=====================================================================+

  Kod Değişikliği             Test Çalıştırma              Sonuç
  +----------+             +---------------+          +----------+
  |          |             |               |          |          |
  | Değiştir | ----------> | Yeni Çıktı    | -------->| Karşılaştır|
  | Modül    |             | Üret          |          | Anlık     |
  |          |             |               |          | Görüntü   |
  +----------+             +---------------+          +----------+
                                                           |
                                               +----------+----------+
                                               |                     |
                                               v                     v
                                         +----------+          +----------+
                                         | Eşleşme  |          | Eşleşmeme|
                                         | GEÇTİ    |          | BAŞARISIZ|
                                         +----------+          +----------+
```

**Anlık Görüntü Dosyaları**:

```
tests/regression/snapshots/
├── expected_output.json       # Tam JSON çıktısı
├── expected_stix.json         # STIX 2.1 çıktısı
├── expected_csv.csv           # CSV çıktısı
├── expected_misp.json         MISP biçimi
├── expected_sigma.yml         # Sigma kuralları
├── expected_html.html         # HTML raporu
├── expected_markdown.md       # Markdown raporu
└── metadata.json              # Anlık görüntü meta verisi
```

**Anlık Görüntü Meta Verisi**:

```json
{
  "version": "1.0.0",
  "created": "2025-01-20T12:00:00Z",
  "input_hash": "sha256:abc123...",
  "record_count": 100,
  "source": "test_fixture",
  "python_version": "3.11.7"
}
```

### 2. Çıktı Kararlılığı Testi

**Amaç**: Aynı girişin her zaman aynı çıktıyı ürettiğini sağlamak.

```python
import pytest
from tc_sgb.pipeline import ThreatIntelPipeline

@pytest.mark.regression
class TestOutputStability:
    """Verify output stability across runs."""

    @pytest.fixture
    def stable_input(self):
        """Deterministic test input."""
        return [
            {"id": 1, "type": "domain", "value": "evil.com", ...},
            {"id": 2, "type": "ip", "value": "10.0.0.1", ...},
            # ... 100 deterministic records
        ]

    def test_json_output_stable(self, stable_input, snapshot):
        """JSON output should match snapshot."""
        pipeline = ThreatIntelPipeline(config)
        result = pipeline.run_sync(stable_input)
        snapshot.assert_match(result.json_output, "expected_output.json")

    def test_stix_output_stable(self, stable_input, snapshot):
        """STIX output should match snapshot."""
        pipeline = ThreatIntelPipeline(config)
        result = pipeline.run_sync(stable_input)
        snapshot.assert_match(result.stix_output, "expected_stix.json")

    def test_csv_output_stable(self, stable_input, snapshot):
        """CSV output should match snapshot."""
        pipeline = ThreatIntelPipeline(config)
        result = pipeline.run_sync(stable_input)
        snapshot.assert_match(result.csv_output, "expected_csv.csv")
```

### 3. Davranışsal Regresyon Testi

**Amaç**: Belirli davranışların değişikliklerden sonra korunduğunu doğrulamak.

```python
@pytest.mark.regression
class TestBehavioralRegression:
    """Verify behavioral invariants."""

    def test_dedup_ratio_stable(self):
        """Deduplication ratio should remain within expected range."""
        records = load_test_dataset("dedup_test_data.json")
        result = deduplicator.deduplicate(records)
        # Should remove 5-15% duplicates
        assert 0.05 <= result.dedup_ratio <= 0.15

    def test_validation_reject_rate_stable(self):
        """Validation rejection rate should be predictable."""
        records = load_test_dataset("validation_test_data.json")
        result = validator.validate_batch(records)
        # Should reject 2-5% of records
        assert 0.02 <= result.invalid_records / result.total_records <= 0.05

    def test_output_file_count_stable(self):
        """Should always generate 16+ output files."""
        records = load_test_dataset("output_test_data.json")
        files = output_engine.generate_all(records, tmp_path)
        assert len(files) >= 16

    def test_processing_order_deterministic(self):
        """Processing order should be deterministic."""
        records = load_test_dataset("order_test_data.json")
        result1 = pipeline.run_sync(records)
        result2 = pipeline.run_sync(records)
        assert result1.output_hashes == result2.output_hashes
```

### 4. API Sözleşme Testi

**Amaç**: İstemcinin API yanıtlarını tanımlandığı şekilde doğru işlediğini sağlamak.

```python
@pytest.mark.regression
class TestAPIContract:
    """Verify API response handling contract."""

    def test_response_schema_contract(self):
        """API response must conform to expected schema."""
        response = load_test_response("api_response_sample.json")
        parsed = APIResponse(**response)
        assert parsed.meta.total > 0
        assert len(parsed.data) > 0
        assert all(r.id > 0 for r in parsed.data)

    def test_pagination_contract(self):
        """Pagination metadata must be consistent."""
        response = load_test_response("api_response_page2.json")
        parsed = APIResponse(**response)
        assert parsed.meta.page == 2
        assert parsed.meta.per_page == 500

    def test_empty_response_contract(self):
        """Empty API response must be handled gracefully."""
        response = {"data": [], "meta": {"total": 0, "page": 1, "per_page": 500}}
        parsed = APIResponse(**response)
        assert len(parsed.data) == 0
```

### 5. Biçim Uyumluluk Testi

**Amaç**: Çıktı biçimlerinin hedef sistemlerle uyumlu olduğunu doğrulamak.

```python
@pytest.mark.regression
class TestFormatCompatibility:
    """Verify format compatibility with target systems."""

    def test_stix_validates_against_schema(self):
        """STIX output must validate against STIX 2.1 schema."""
        import stix2
        output = generate_stix_output()
        bundle = stix2.parse(output)
        assert bundle.type == "bundle"

    def test_csv_opens_in_excel(self):
        """CSV output must be valid and Excel-compatible."""
        output = generate_csv_output()
        import csv
        reader = csv.reader(io.StringIO(output))
        rows = list(reader)
        assert len(rows) > 1  # Header + data
        assert rows[0] == ["id", "type", "value", "first_seen", "last_seen", "status"]

    def test_json_parseable(self):
        """JSON output must be valid JSON."""
        output = generate_json_output()
        import json
        parsed = json.loads(output)
        assert "data" in parsed
        assert "meta" in parsed

    def test_elastic_ndjson_format(self):
        """Elasticsearch NDJSON must have correct format."""
        output = generate_elastic_output()
        lines = output.strip().split("\n")
        for line in lines:
            action = json.loads(line.split("\t")[0])
            assert "index" in action
```

## Regresyon Test Verisi Yönetimi

### Test Veri Seti Sürümleri

```
tests/regression/data/
├── v1.0.0/
│   ├── input_records.json
│   ├── expected_output.json
│   └── metadata.json
├── v1.1.0/
│   ├── input_records.json
│   ├── expected_output.json
│   └── metadata.json
└── current/
    ├── input_records.json
    └── metadata.json
```

### Veri Seti Oluşturma

```python
@pytest.fixture
def regression_dataset():
    """Create deterministic regression test dataset."""
    return [
        IOCRecord(
            id=i,
            type=list(IOCType)[i % 5],
            value=f"test{i}.example.com",
            first_seen=f"2025-01-{i:02d}T10:00:00Z",
            last_seen=f"2025-01-{i:02d}T14:00:00Z",
            status=IOCStatus.ACTIVE,
        )
        for i in range(1, 101)
    ]
```

## Regresyon Test Çalıştırma

### Tam Regresyon Paketi

```bash
# Run all regression tests
pytest -m regression

# Run with snapshot update
pytest -m regression --snapshot-update

# Run specific regression test
pytest tests/regression/test_regression.py::TestOutputStability::test_json_output_stable

# Compare performance baseline
pytest -m performance --benchmark-compare=0.001
```

### CI Entegrasyonu

```yaml
# .github/workflows/ci.yml
- name: Run regression tests
  run: |
    pytest -m regression --tb=long
    if [ $? -ne 0 ]; then
      echo "Regression tests failed!"
      echo "If intentional, update snapshots with:"
      echo "  pytest -m regression --snapshot-update"
      exit 1
    fi
```

## Anlık Görüntü Güncelleme Süreci

Çıktı kasıtlı olarak değiştiğinde:

```bash
# 1. Review the changes
git diff tests/regression/snapshots/

# 2. Update snapshots
pytest -m regression --snapshot-update

# 3. Verify the update
pytest -m regression

# 4. Commit updated snapshots
git add tests/regression/snapshots/
git commit -m "chore: update regression snapshots for v1.1.0"
```

## Regresyon Test Metrikleri

| Metrik | Hedef | Ölçüm |
|--------|--------|-------------|
| Anlık Görüntü Kapsamı | %100 | Tüm çıkış biçimlerinin anlık görüntüleri var |
| Davranışsal Kapsam | %100 | Tüm kritik davranışlar test edilmiş |
| Çalıştırma Süresi | < 60sn | Tam regresyon paketi |
| Tutarsızlık | %0 | Ara sıra oluşan hatalar yok |
| Güncelleme Sıklığı | Her sürümde | Sürüm artışında anlık görüntüler güncellenir |

## Regresyon Önleme

### Birleştirme Öncesi Kontroller

1. **Tüm regresyon testleri geçer** — Anlık görüntü eşleşmemesi yok
2. **Davranış değişikliği yok** — Çıktı biçimi korunmuş
3. **Performans regresyonu yok** — Karşılaştırmalar eşik içinde
4. **Kod incelemesi** — Çekirdek modüllere yapılan değişiklikler gözden geçirilmiş

### Birleştirme Sonrası İzleme

1. **Günlük regresyon çalıştırması** — Zamanlanmış CI görevi
2. **Performans takibi** — Karşılaştırma trend analizi
3. **Çıktı izleme** — Beklenmedik değişikliklerde uyarı
4. **Sürüm karşılaştırması** — Sürüm arasındaki fark raporları
