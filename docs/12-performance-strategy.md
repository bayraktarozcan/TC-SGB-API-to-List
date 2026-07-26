[English](#english) | [Türkçe](#turkish)

<a id="english"></a>

# Performance Strategy

## Overview

This document defines performance benchmarks, measurement methodology, and optimization targets for the TC-SGB-API-to-List system across various data volumes.

## Performance Targets

### Pipeline Latency

| Dataset Size | Records | Target Latency | Throughput |
|--------------|---------|----------------|------------|
| Small | 100 | < 1s | 100 rec/s |
| Medium | 1,000 | < 5s | 200 rec/s |
| Large | 10,000 | < 30s | 333 rec/s |
| XL | 100,000 | < 5min | 333 rec/s |
| Full | 483,690 | < 20min | 400 rec/s |
| Stress | 1,000,000 | < 45min | 370 rec/s |

### API Fetch Performance

| Metric | Target | Measurement |
|--------|--------|-------------|
| Single Page Fetch | < 500ms | p95 latency |
| Full Dataset Fetch | < 10min | 483K records |
| Concurrent Requests | 5 max | Semaphore limit |
| Retry Recovery | < 30s | Backoff + retry |
| Connection Reuse | > 80% | Pool hit rate |

### Memory Usage

| Dataset Size | Records | Max Memory | Notes |
|--------------|---------|------------|-------|
| Small | 100 | 50 MB | Minimal footprint |
| Medium | 1,000 | 100 MB | Comfortable |
| Large | 10,000 | 200 MB | Streaming recommended |
| XL | 100,000 | 500 MB | Chunked processing |
| Full | 483,690 | 1 GB | Full pipeline |
| Stress | 1,000,000 | 2 GB | Maximum expected |

### Disk Usage

| Dataset Size | Records | Output Size | Notes |
|--------------|---------|-------------|-------|
| Small | 100 | 50 KB | All formats |
| Medium | 1,000 | 500 KB | All formats |
| Large | 10,000 | 5 MB | All formats |
| XL | 100,000 | 50 MB | All formats |
| Full | 483,690 | 250 MB | All formats |
| Stress | 1,000,000 | 500 MB | All formats |

---

## Benchmark Suite

### Benchmark Categories

```
+=====================================================================+
|  Performance Benchmark Matrix                                        |
+=====================================================================+

  Category              Tool              Frequency
  +--------------------+-----------------+-------------------+
  | API Fetch           | pytest-bench    | Every PR           |
  | Validation          | pytest-bench    | Every PR           |
  | Normalization       | pytest-bench    | Every PR           |
  | Deduplication       | pytest-bench    | Weekly             |
  | Quality Analysis    | pytest-bench    | Weekly             |
  | Output Generation   | pytest-bench    | Every PR           |
  | Full Pipeline       | pytest-bench    | On release         |
  | Memory Profiling    | memory_profiler | Weekly             |
  | Concurrency         | Custom          | Monthly            |
  +--------------------+-----------------+-------------------+
```

### Benchmark Implementation

```python
import pytest
from tc_sgb.client import SGBAPIClient
from tc_sgb.validator import IOCValidator
from tc_sgb.normalizer import IOCNormalizer
from tc_sgb.deduplicator import IOCDeduplicator
from tc_sgb.outputs import OutputEngine
from tc_sgb.pipeline import ThreatIntelPipeline

@pytest.mark.performance
class TestBenchmarks:
    """Performance benchmarks for all pipeline stages."""

    @pytest.fixture
    def small_dataset(self):
        return generate_records(100)

    @pytest.fixture
    def medium_dataset(self):
        return generate_records(1_000)

    @pytest.fixture
    def large_dataset(self):
        return generate_records(10_000)

    @pytest.fixture
    def xl_dataset(self):
        return generate_records(100_000)

    def test_fetch_100_records(self, benchmark, small_dataset):
        """Benchmark: Fetch 100 records."""
        client = SGBAPIClient(config)
        benchmark(client.fetch_all_sync, small_dataset)

    def test_validate_100_records(self, benchmark, small_dataset):
        """Benchmark: Validate 100 records."""
        validator = IOCValidator()
        benchmark(validator.validate_batch, small_dataset)

    def test_normalize_100_records(self, benchmark, small_dataset):
        """Benchmark: Normalize 100 records."""
        normalizer = IOCNormalizer()
        benchmark(normalizer.normalize_batch, small_dataset)

    def test_dedup_1000_records(self, benchmark, medium_dataset):
        """Benchmark: Dedup 1000 records."""
        deduplicator = IOCDeduplicator(config)
        benchmark(deduplicator.deduplicate, medium_dataset)

    def test_output_100_records(self, benchmark, small_dataset, tmp_path):
        """Benchmark: Generate all outputs for 100 records."""
        engine = OutputEngine(config)
        benchmark(engine.generate_all, small_dataset, tmp_path)

    def test_full_pipeline_100(self, benchmark, small_dataset):
        """Benchmark: Full pipeline with 100 records."""
        pipeline = ThreatIntelPipeline(config)
        benchmark(pipeline.run_sync, small_dataset)

    def test_full_pipeline_1000(self, benchmark, medium_dataset):
        """Benchmark: Full pipeline with 1000 records."""
        pipeline = ThreatIntelPipeline(config)
        benchmark(pipeline.run_sync, medium_dataset)

    def test_full_pipeline_10000(self, benchmark, large_dataset):
        """Benchmark: Full pipeline with 10000 records."""
        pipeline = ThreatIntelPipeline(config)
        benchmark(pipeline.run_sync, large_dataset)
```

---

## Performance Profiling

### Memory Profiling

```python
from memory_profiler import profile

@profile
def benchmark_memory_usage():
    """Profile memory usage during pipeline execution."""
    records = generate_records(100_000)
    pipeline = ThreatIntelPipeline(config)
    result = pipeline.run_sync(records)
    return result
```

### CPU Profiling

```python
import cProfile
import pstats

def benchmark_cpu_usage():
    """Profile CPU usage during pipeline execution."""
    profiler = cProfile.Profile()
    profiler.enable()

    records = generate_records(100_000)
    pipeline = ThreatIntelPipeline(config)
    result = pipeline.run_sync(records)

    profiler.disable()
    stats = pstats.Stats(profiler)
    stats.sort_stats('cumulative')
    stats.print_stats(20)
    return result
```

### Async Performance

```python
import asyncio
from tc_sgb.client import SGBAPIClient

async def benchmark_concurrent_fetch():
    """Benchmark concurrent API fetch performance."""
    client = SGBAPIClient(config)

    # Sequential fetch
    start = time.time()
    for page in range(10):
        await client.fetch_page(page, 500)
    sequential_time = time.time() - start

    # Concurrent fetch
    start = time.time()
    tasks = [client.fetch_page(page, 500) for page in range(10)]
    await asyncio.gather(*tasks)
    concurrent_time = time.time() - start

    speedup = sequential_time / concurrent_time
    print(f"Sequential: {sequential_time:.2f}s")
    print(f"Concurrent: {concurrent_time:.2f}s")
    print(f"Speedup: {speedup:.1f}x")
```

---

## Performance Test Results Template

### Benchmark Report

```
+=====================================================================+
|  Performance Benchmark Report                                        |
+=====================================================================+
|  Date: 2025-01-20                                                   |
|  Python: 3.11.7                                                     |
|  Platform: Linux x86_64                                             |
+=====================================================================+

  API Fetch
  +---------------------------------------------------+
  | 100 records:   0.45s (222 rec/s)     [PASS]      |
  | 1K records:    2.10s (476 rec/s)     [PASS]      |
  | 10K records:   18.5s (540 rec/s)     [PASS]      |
  | 100K records:  185s (540 rec/s)      [PASS]      |
  +---------------------------------------------------+

  Validation
  +---------------------------------------------------+
  | 100 records:   0.02s (5000 rec/s)    [PASS]      |
  | 1K records:    0.15s (6666 rec/s)    [PASS]      |
  | 10K records:   1.4s (7142 rec/s)     [PASS]      |
  | 100K records:  14s (7142 rec/s)      [PASS]      |
  +---------------------------------------------------+

  Normalization
  +---------------------------------------------------+
  | 100 records:   0.03s (3333 rec/s)    [PASS]      |
  | 1K records:    0.25s (4000 rec/s)    [PASS]      |
  | 10K records:   2.3s (4347 rec/s)     [PASS]      |
  | 100K records:  23s (4347 rec/s)      [PASS]      |
  +---------------------------------------------------+

  Deduplication
  +---------------------------------------------------+
  | 100 records:   0.01s (10000 rec/s)   [PASS]      |
  | 1K records:    0.08s (12500 rec/s)   [PASS]      |
  | 10K records:   0.7s (14285 rec/s)    [PASS]      |
  | 100K records:  6.5s (15384 rec/s)    [PASS]      |
  +---------------------------------------------------+

  Output Generation
  +---------------------------------------------------+
  | 100 records:   0.08s (1250 rec/s)    [PASS]      |
  | 1K records:    0.65s (1538 rec/s)    [PASS]      |
  | 10K records:   5.8s (1724 rec/s)     [PASS]      |
  | 100K records:  58s (1724 rec/s)      [PASS]      |
  +---------------------------------------------------+

  Full Pipeline
  +---------------------------------------------------+
  | 100 records:   0.6s (166 rec/s)      [PASS]      |
  | 1K records:    3.2s (312 rec/s)      [PASS]      |
  | 10K records:   28s (357 rec/s)       [PASS]      |
  | 100K records:  285s (350 rec/s)      [PASS]      |
  +---------------------------------------------------+

  Memory Usage
  +---------------------------------------------------+
  | 100 records:   45 MB                  [PASS]      |
  | 1K records:    62 MB                  [PASS]      |
  | 10K records:   95 MB                  [PASS]      |
  | 100K records:  285 MB                 [PASS]      |
  +---------------------------------------------------+

  Summary: All benchmarks PASS
+=====================================================================+
```

---

## Performance Optimization Strategies

### 1. API Fetch Optimization

```python
# Use connection pooling
client = httpx.AsyncClient(
    http2=True,                    # HTTP/2 multiplexing
    limits=httpx.Limits(
        max_connections=10,
        max_keepalive_connections=5,
        keepalive_expiry=30,
    ),
)

# Use bounded concurrency
semaphore = asyncio.Semaphore(5)

async def fetch_with_semaphore(page):
    async with semaphore:
        return await client.fetch_page(page)
```

### 2. Memory Optimization

```python
# Use generators for streaming processing
async def process_records_streaming(records):
    """Process records one at a time to minimize memory."""
    async for record in records:
        validated = validator.validate_record(record)
        if validated.is_valid:
            normalized = normalizer.normalize(validated.record)
            yield normalized

# Use chunked processing for large datasets
def process_in_chunks(records, chunk_size=1000):
    """Process records in chunks."""
    for i in range(0, len(records), chunk_size):
        chunk = records[i:i + chunk_size]
        yield process_chunk(chunk)
```

### 3. Deduplication Optimization

```python
# Use Bloom filter for probabilistic dedup
from pybloom_live import BloomFilter

class OptimizedDeduplicator:
    def __init__(self, expected_items=500_000, error_rate=0.001):
        self.bloom = BloomFilter(capacity=expected_items, error_rate=error_rate)
        self.exact_set = set()  # For exact matching

    def is_duplicate(self, record_hash: str) -> bool:
        """Check if record is duplicate using Bloom filter first."""
        if record_hash in self.bloom:
            # Bloom filter says maybe - check exact set
            return record_hash in self.exact_set
        # Bloom filter says definitely not duplicate
        self.bloom.add(record_hash)
        self.exact_set.add(record_hash)
        return False
```

### 4. Output Optimization

```python
# Use orjson for fast JSON serialization
import orjson

def generate_json_fast(records):
    """Generate JSON using orjson for speed."""
    data = {
        "data": [r.model_dump() for r in records],
        "meta": {"count": len(records)},
    }
    return orjson.dumps(data).decode("utf-8")

# Use buffered writing
def write_output_buffered(path, data, buffer_size=8192):
    """Write output in buffered chunks."""
    with open(path, "w", buffering=buffer_size) as f:
        for chunk in data:
            f.write(chunk)
```

### 5. Parallel Output Generation

```python
import asyncio

async def generate_outputs_parallel(records, output_dir):
    """Generate all output formats in parallel."""
    formats = [OutputFormat.JSON, OutputFormat.STIX, OutputFormat.CSV, ...]

    async def generate_one(fmt):
        engine = OutputEngine(config)
        return await engine.generate_async(fmt, records, output_dir)

    tasks = [generate_one(fmt) for fmt in formats]
    results = await asyncio.gather(*tasks)
    return results
```

---

## Performance Monitoring

### Metrics to Track

| Metric | Tool | Alert Threshold |
|--------|------|-----------------|
| Pipeline Duration | pytest-bench | > 20min |
| API Response Time | httpx metrics | > 2s p95 |
| Memory Peak | memory_profiler | > 2GB |
| CPU Usage | psutil | > 90% sustained |
| Disk I/O | iostat | > 100MB/s |
| Network I/O | ifstat | > 10MB/s |

### Continuous Performance Testing

```yaml
# .github/workflows/performance.yml
name: Performance Tests
on:
  schedule:
    - cron: "0 2 * * *"  # Daily at 2 AM

jobs:
  benchmark:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v4
        with:
          python-version: "3.11"

      - name: Install dependencies
        run: pip install -r requirements.lock

      - name: Run benchmarks
        run: pytest -m performance --benchmark-json=benchmark.json

      - name: Upload results
        uses: actions/upload-artifact@v3
        with:
          name: benchmark-results
          path: benchmark.json
```

<a id="turkish"></a>

# Performans Stratejisi

## Genel Bakış

Bu belge, TC-SGB-API-to-List sistemi için çeşitli veri hacimlerinde performans karşılaştırmalarını, ölçüm yöntemlerini ve optimizasyon hedeflerini tanımlar.

## Performans Hedefleri

### Pipeline Gecikmesi

| Veri Seti Boyutu | Kayıtlar | Hedef Gecikme | Verimlilik |
|--------------|---------|----------------|------------|
| Küçük | 100 | < 1s | 100 kayıt/sn |
| Orta | 1.000 | < 5s | 200 kayıt/sn |
| Büyük | 10.000 | < 30s | 333 kayıt/sn |
| XL | 100.000 | < 5dk | 333 kayıt/sn |
| Tam | 483.690 | < 20dk | 400 kayıt/sn |
| Stres | 1.000.000 | < 45dk | 370 kayıt/sn |

### API Çekme Performansı

| Metrik | Hedef | Ölçüm |
|--------|--------|-------------|
| Tek Sayfa Çekme | < 500ms | p95 gecikmesi |
| Tam Veri Seti Çekme | < 10dk | 483B kayıt |
| Eş Zamanlı İstekler | 5 maks | Semafor limiti |
| Yeniden Deneme Kurtarma | < 30s | Geri çekilme + yeniden deneme |
| Bağlantı Yeniden Kullanım | > %80 | Havuz isabet oranı |

### Bellek Kullanımı

| Veri Seti Boyutu | Kayıtlar | Maks Bellek | Notlar |
|--------------|---------|------------|-------|
| Küçük | 100 | 50 MB | Minimal ayak izi |
| Orta | 1.000 | 100 MB | Konforlu |
| Büyük | 10.000 | 200 MB | Akış önerilir |
| XL | 100.000 | 500 MB | Parçalı işleme |
| Tam | 483.690 | 1 GB | Tam pipeline |
| Stres | 1.000.000 | 2 GB | Beklenen maksimum |

### Disk Kullanımı

| Veri Seti Boyutu | Kayıtlar | Çıktı Boyutu | Notlar |
|--------------|---------|-------------|-------|
| Küçük | 100 | 50 KB | Tüm biçimler |
| Orta | 1.000 | 500 KB | Tüm biçimler |
| Büyük | 10.000 | 5 MB | Tüm biçimler |
| XL | 100.000 | 50 MB | Tüm biçimler |
| Tam | 483.690 | 250 MB | Tüm biçimler |
| Stres | 1.000.000 | 500 MB | Tüm biçimler |

---

## Karşılaştırma Paketi

### Karşılaştırma Kategorileri

```
+=====================================================================+
|  Performans Karşılaştırma Matrisi                                    |
+=====================================================================+

  Kategori                Araç               Sıklık
  +--------------------+-----------------+-------------------+
  | API Çekme            | pytest-bench    | Her PR'da          |
  | Doğrulama            | pytest-bench    | Her PR'da          |
  | Normalizasyon        | pytest-bench    | Her PR'da          |
  | Tekrar Kaldırma      | pytest-bench    | Haftalık           |
  | Kalite Analizi       | pytest-bench    | Haftalık           |
  | Çıktı Üretimi        | pytest-bench    | Her PR'da          |
  | Tam Pipeline         | pytest-bench    | Yayımlandığında     |
  | Bellek Profillendirme| memory_profiler | Haftalık           |
  | Eş Zamanlılık        | Özel            | Aylık              |
  +--------------------+-----------------+-------------------+
```

### Karşılaştırma Uygulaması

```python
import pytest
from tc_sgb.client import SGBAPIClient
from tc_sgb.validator import IOCValidator
from tc_sgb.normalizer import IOCNormalizer
from tc_sgb.deduplicator import IOCDeduplicator
from tc_sgb.outputs import OutputEngine
from tc_sgb.pipeline import ThreatIntelPipeline

@pytest.mark.performance
class TestBenchmarks:
    """Performance benchmarks for all pipeline stages."""

    @pytest.fixture
    def small_dataset(self):
        return generate_records(100)

    @pytest.fixture
    def medium_dataset(self):
        return generate_records(1_000)

    @pytest.fixture
    def large_dataset(self):
        return generate_records(10_000)

    @pytest.fixture
    def xl_dataset(self):
        return generate_records(100_000)

    def test_fetch_100_records(self, benchmark, small_dataset):
        """Benchmark: Fetch 100 records."""
        client = SGBAPIClient(config)
        benchmark(client.fetch_all_sync, small_dataset)

    def test_validate_100_records(self, benchmark, small_dataset):
        """Benchmark: Validate 100 records."""
        validator = IOCValidator()
        benchmark(validator.validate_batch, small_dataset)

    def test_normalize_100_records(self, benchmark, small_dataset):
        """Benchmark: Normalize 100 records."""
        normalizer = IOCNormalizer()
        benchmark(normalizer.normalize_batch, small_dataset)

    def test_dedup_1000_records(self, benchmark, medium_dataset):
        """Benchmark: Dedup 1000 records."""
        deduplicator = IOCDeduplicator(config)
        benchmark(deduplicator.deduplicate, medium_dataset)

    def test_output_100_records(self, benchmark, small_dataset, tmp_path):
        """Benchmark: Generate all outputs for 100 records."""
        engine = OutputEngine(config)
        benchmark(engine.generate_all, small_dataset, tmp_path)

    def test_full_pipeline_100(self, benchmark, small_dataset):
        """Benchmark: Full pipeline with 100 records."""
        pipeline = ThreatIntelPipeline(config)
        benchmark(pipeline.run_sync, small_dataset)

    def test_full_pipeline_1000(self, benchmark, medium_dataset):
        """Benchmark: Full pipeline with 1000 records."""
        pipeline = ThreatIntelPipeline(config)
        benchmark(pipeline.run_sync, medium_dataset)

    def test_full_pipeline_10000(self, benchmark, large_dataset):
        """Benchmark: Full pipeline with 10000 records."""
        pipeline = ThreatIntelPipeline(config)
        benchmark(pipeline.run_sync, large_dataset)
```

---

## Performans Profilendirme

### Bellek Profilendirme

```python
from memory_profiler import profile

@profile
def benchmark_memory_usage():
    """Profile memory usage during pipeline execution."""
    records = generate_records(100_000)
    pipeline = ThreatIntelPipeline(config)
    result = pipeline.run_sync(records)
    return result
```

### CPU Profilendirme

```python
import cProfile
import pstats

def benchmark_cpu_usage():
    """Profile CPU usage during pipeline execution."""
    profiler = cProfile.Profile()
    profiler.enable()

    records = generate_records(100_000)
    pipeline = ThreatIntelPipeline(config)
    result = pipeline.run_sync(records)

    profiler.disable()
    stats = pstats.Stats(profiler)
    stats.sort_stats('cumulative')
    stats.print_stats(20)
    return result
```

### Asenkron Performans

```python
import asyncio
from tc_sgb.client import SGBAPIClient

async def benchmark_concurrent_fetch():
    """Benchmark concurrent API fetch performance."""
    client = SGBAPIClient(config)

    # Sequential fetch
    start = time.time()
    for page in range(10):
        await client.fetch_page(page, 500)
    sequential_time = time.time() - start

    # Concurrent fetch
    start = time.time()
    tasks = [client.fetch_page(page, 500) for page in range(10)]
    await asyncio.gather(*tasks)
    concurrent_time = time.time() - start

    speedup = sequential_time / concurrent_time
    print(f"Sequential: {sequential_time:.2f}s")
    print(f"Concurrent: {concurrent_time:.2f}s")
    print(f"Speedup: {speedup:.1f}x")
```

---

## Performans Test Sonuçları Şablonu

### Karşılaştırma Raporu

```
+=====================================================================+
|  Performans Karşılaştırma Raporu                                    |
+=====================================================================+
|  Tarih: 2025-01-20                                                  |
|  Python: 3.11.7                                                     |
|  Platform: Linux x86_64                                             |
+=====================================================================+

  API Çekme
  +---------------------------------------------------+
  | 100 kayıt:    0.45s (222 kayıt/sn)     [GEÇTİ]    |
  | 1B kayıt:     2.10s (476 kayıt/sn)     [GEÇTİ]    |
  | 10B kayıt:    18.5s (540 kayıt/sn)     [GEÇTİ]    |
  | 100B kayıt:   185s (540 kayıt/sn)      [GEÇTİ]    |
  +---------------------------------------------------+

  Doğrulama
  +---------------------------------------------------+
  | 100 kayıt:    0.02s (5000 kayıt/sn)    [GEÇTİ]    |
  | 1B kayıt:     0.15s (6666 kayıt/sn)    [GEÇTİ]    |
  | 10B kayıt:    1.4s (7142 kayıt/sn)     [GEÇTİ]    |
  | 100B kayıt:   14s (7142 kayıt/sn)      [GEÇTİ]    |
  +---------------------------------------------------+

  Normalizasyon
  +---------------------------------------------------+
  | 100 kayıt:    0.03s (3333 kayıt/sn)    [GEÇTİ]    |
  | 1B kayıt:     0.25s (4000 kayıt/sn)    [GEÇTİ]    |
  | 10B kayıt:    2.3s (4347 kayıt/sn)     [GEÇTİ]    |
  | 100B kayıt:   23s (4347 kayıt/sn)      [GEÇTİ]    |
  +---------------------------------------------------+

  Tekrar Kaldırma
  +---------------------------------------------------+
  | 100 kayıt:    0.01s (10000 kayıt/sn)   [GEÇTİ]    |
  | 1B kayıt:     0.08s (12500 kayıt/sn)   [GEÇTİ]    |
  | 10B kayıt:    0.7s (14285 kayıt/sn)    [GEÇTİ]    |
  | 100B kayıt:   6.5s (15384 kayıt/sn)    [GEÇTİ]    |
  +---------------------------------------------------+

  Çıktı Üretimi
  +---------------------------------------------------+
  | 100 kayıt:    0.08s (1250 kayıt/sn)     [GEÇTİ]    |
  | 1B kayıt:     0.65s (1538 kayıt/sn)    [GEÇTİ]    |
  | 10B kayıt:    5.8s (1724 kayıt/sn)     [GEÇTİ]    |
  | 100B kayıt:   58s (1724 kayıt/sn)      [GEÇTİ]    |
  +---------------------------------------------------+

  Tam Pipeline
  +---------------------------------------------------+
  | 100 kayıt:    0.6s (166 kayıt/sn)       [GEÇTİ]    |
  | 1B kayıt:     3.2s (312 kayıt/sn)       [GEÇTİ]    |
  | 10B kayıt:    28s (357 kayıt/sn)        [GEÇTİ]    |
  | 100B kayıt:   285s (350 kayıt/sn)       [GEÇTİ]    |
  +---------------------------------------------------+

  Bellek Kullanımı
  +---------------------------------------------------+
  | 100 kayıt:    45 MB                    [GEÇTİ]    |
  | 1B kayıt:     62 MB                    [GEÇTİ]    |
  | 10B kayıt:    95 MB                    [GEÇTİ]    |
  | 100B kayıt:   285 MB                   [GEÇTİ]    |
  +---------------------------------------------------+

  Özet: Tüm karşılaştırmalar GEÇTİ
+=====================================================================+
```

---

## Performans Optimizasyon Stratejileri

### 1. API Çekme Optimizasyonu

```python
# Use connection pooling
client = httpx.AsyncClient(
    http2=True,                    # HTTP/2 multiplexing
    limits=httpx.Limits(
        max_connections=10,
        max_keepalive_connections=5,
        keepalive_expiry=30,
    ),
)

# Use bounded concurrency
semaphore = asyncio.Semaphore(5)

async def fetch_with_semaphore(page):
    async with semaphore:
        return await client.fetch_page(page)
```

### 2. Bellek Optimizasyonu

```python
# Use generators for streaming processing
async def process_records_streaming(records):
    """Process records one at a time to minimize memory."""
    async for record in records:
        validated = validator.validate_record(record)
        if validated.is_valid:
            normalized = normalizer.normalize(validated.record)
            yield normalized

# Use chunked processing for large datasets
def process_in_chunks(records, chunk_size=1000):
    """Process records in chunks."""
    for i in range(0, len(records), chunk_size):
        chunk = records[i:i + chunk_size]
        yield process_chunk(chunk)
```

### 3. Tekrar Kaldırma Optimizasyonu

```python
# Use Bloom filter for probabilistic dedup
from pybloom_live import BloomFilter

class OptimizedDeduplicator:
    def __init__(self, expected_items=500_000, error_rate=0.001):
        self.bloom = BloomFilter(capacity=expected_items, error_rate=error_rate)
        self.exact_set = set()  # For exact matching

    def is_duplicate(self, record_hash: str) -> bool:
        """Check if record is duplicate using Bloom filter first."""
        if record_hash in self.bloom:
            # Bloom filter says maybe - check exact set
            return record_hash in self.exact_set
        # Bloom filter says definitely not duplicate
        self.bloom.add(record_hash)
        self.exact_set.add(record_hash)
        return False
```

### 4. Çıktı Optimizasyonu

```python
# Use orjson for fast JSON serialization
import orjson

def generate_json_fast(records):
    """Generate JSON using orjson for speed."""
    data = {
        "data": [r.model_dump() for r in records],
        "meta": {"count": len(records)},
    }
    return orjson.dumps(data).decode("utf-8")

# Use buffered writing
def write_output_buffered(path, data, buffer_size=8192):
    """Write output in buffered chunks."""
    with open(path, "w", buffering=buffer_size) as f:
        for chunk in data:
            f.write(chunk)
```

### 5. Paralel Çıktı Üretimi

```python
import asyncio

async def generate_outputs_parallel(records, output_dir):
    """Generate all output formats in parallel."""
    formats = [OutputFormat.JSON, OutputFormat.STIX, OutputFormat.CSV, ...]

    async def generate_one(fmt):
        engine = OutputEngine(config)
        return await engine.generate_async(fmt, records, output_dir)

    tasks = [generate_one(fmt) for fmt in formats]
    results = await asyncio.gather(*tasks)
    return results
```

---

## Performans İzleme

### Takip Edilecek Metrikler

| Metrik | Araç | Uyarı Eşiği |
|--------|------|-----------------|
| Pipeline Süresi | pytest-bench | > 20dk |
| API Yanıt Süresi | httpx metrikleri | > 2s p95 |
| Bellek Tepe Değeri | memory_profiler | > 2GB |
| CPU Kullanımı | psutil | > %90 sürekli |
| Disk G/Ç | iostat | > 100MB/sn |
| Ağ G/Ç | ifstat | > 10MB/sn |

### Sürekli Performans Testi

```yaml
# .github/workflows/performance.yml
name: Performance Tests
on:
  schedule:
    - cron: "0 2 * * *"  # Daily at 2 AM

jobs:
  benchmark:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v4
        with:
          python-version: "3.11"

      - name: Install dependencies
        run: pip install -r requirements.lock

      - name: Run benchmarks
        run: pytest -m performance --benchmark-json=benchmark.json

      - name: Upload results
        uses: actions/upload-artifact@v3
        with:
          name: benchmark-results
          path: benchmark.json
```
