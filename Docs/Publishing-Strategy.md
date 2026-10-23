> **Language / Dil** &nbsp;
> [EN English](#-english) &nbsp;·&nbsp; [TR Türkçe](#-türkçe)

<a id="-english"></a>

# Publishing Strategy

## Overview

This document defines the distribution and publishing strategy for the TC-SGB-API-to-List project, including GitHub releases, PyPI distribution, and output file management.

## Distribution Channels

```
+=====================================================================+
|                     Distribution Channels                            |
+=====================================================================+

  +-------------------+     +-------------------+     +---------------+
  |                   |     |                   |     |               |
  |   GitHub          |     |   PyPI            |     |   Local       |
  |   Releases        |     |   Package         |     |   Filesystem  |
  |                   |     |                   |     |               |
  | - Source code     |     | - pip install     |     | - Output      |
  | - Wheel           |     | - Package deps    |     |   files       |
  | - Tarball         |     | - CLI entry point |     | - Reports     |
  | - Release notes   |     | - Version mgmt    |     | - Configs     |
  | - Artifacts       |     |                   |     |               |
  +-------------------+     +-------------------+     +---------------+
          |                         |                         |
          v                         v                         v
  +-------------------+     +-------------------+     +---------------+
  |                   |     |                   |     |               |
  |  Source Dist      |     |  Wheel            |     |  Output Files |
  |  .tar.gz          |     |  .whl             |     |  .json        |
  |  (all files)      |     |  (Python only)    |     |  .csv         |
  |                   |     |                   |     |  .stix.json   |
  +-------------------+     +-------------------+     |  .html        |
                                                       |  .md          |
                                                       |  ...16       |
                                                       +---------------+
```

---

## GitHub Releases

### Release Artifacts

Each GitHub release includes:

| Artifact | Description | Size (est.) |
|----------|-------------|-------------|
| Source code (tar.gz) | Full repository source | ~500 KB |
| Source code (zip) | Full repository source | ~600 KB |
| Wheel (.whl) | Built Python package | ~200 KB |
| Output samples | Example output files | ~1 MB |
| Checksums | SHA-256 for all artifacts | ~1 KB |
| Release notes | Auto-generated from PRs | ~10 KB |

### Brave / AdGuard filter list

Release-asset links are served as file downloads, which Brave rejects as custom
filter lists. The AdGuard output is therefore also mirrored as plain text on the
rolling single-commit `filter-lists` branch (no history kept, never needs Git LFS),
refreshed daily by the Scheduled Fetch workflow. Two third-party feeds
(Poland, Slovenia) ship on the same branch as separate lists; files
are numbered so Brave (which sorts subscriptions by URL) shows them in country
order (`04` is reserved for Lithuania, whose source sits behind a Cloudflare
challenge and cannot be fetched yet):

- Türkiye: <https://raw.githubusercontent.com/bayraktarozcan/TC-SGB-API-to-List/filter-lists/01-turkiye-sgb_adguard.txt>
- Polonya: <https://raw.githubusercontent.com/bayraktarozcan/TC-SGB-API-to-List/filter-lists/02-polonya-certpl_adguard.txt>
- Slovenya: <https://raw.githubusercontent.com/bayraktarozcan/TC-SGB-API-to-List/filter-lists/03-slovenya-certsi_adguard.txt>
- Subscribe in Brave via `brave://adblock` → Add filter list via URL.

The Azerbaijani `blacklist.gov.az` list is out of scope: its contents proved
unreliable and unsuitable for a curated blocklist, so it is no longer fetched,
validated, or published, and its file has been dropped from the branch.

### External safety gate

Every external feed passes the publication safety policy (`Scripts/src/safety.py`)
before rendering: exact high-impact hosts are rejected, shared user-content
apexes go to review, and each held indicator is recorded with its reason in a
per-feed audit file (`<feed>_audit.json` under `Output/External/`) next to a raw
source snapshot (`<feed>_source.txt`). The list header carries both timestamps:
`! Last updated` (generation time) and, when the source declares one,
`! Source updated` (feed time).

Before publishing, the workflow runs `tc-sgb validate-external` (usable locally
too) and copies only gate-passing files to the branch. A feed that fails the
gate keeps serving its last good snapshot; a file that never passed is never
treated as safe. The main pipeline applies the same policy to domain indicators
at its quality stage (`safety_rejected` in the run summary), independent of the
quality score. URL indicators remain URLs, and a host-wide generator applies the
same policy before promoting one, so a held host never becomes a wholesale rule.

### Release Process

```
1. Developer pushes tag
   git tag -a v1.1.0 -m "Release v1.1.0"
   git push origin v1.1.0

2. GitHub Actions triggers release.yaml
   ├── Run full test suite
   ├── Build package (sdist + wheel)
   ├── Generate release notes
   ├── Create GitHub Release
   ├── Upload artifacts
   └── Publish to PyPI

3. Release is live
   ├── GitHub: github.com/bayraktarozcan/TC-SGB-API-to-List/releases/tag/v0.1.0.0
   ├── PyPI: pypi.org/project/tc-sgb/1.1.0/
   └── Artifacts: Downloadable from release page
```

### Release Page Template

```markdown
# Release v1.1.0

## What's New
- Added Sigma rule output format
- 30% faster deduplication
- Memory optimization for large datasets

## Installation

### From PyPI
pip install tc-sgb==1.1.0

### From Source
git clone https://github.com/bayraktarozcan/TC-SGB-API-to-List.git
cd tc-sgb
git checkout v1.1.0
pip install -e .

## Artifacts
| File | Checksum (SHA-256) |
|------|-------------------|
| tc-sgb-1.1.0.tar.gz | abc123... |
| tc_sgb-1.1.0-py3-none-any.whl | def456... |

## Migration Notes
- Config files now require `version: 2` key
- See Docs/Migration.md for details

## Full Changelog
https://github.com/bayraktarozcan/TC-SGB-API-to-List/compare/v0.1.0.0...v0.1.1.0
```

---

## PyPI Distribution

### Package Configuration

```toml
# pyproject.toml
[build-system]
requires = ["setuptools>=68.0"]
build-backend = "setuptools.build_meta"

[project]
name = "tc-sgb"
version = "1.1.0"
description = "T.C. Siber Güvenlik Başkanlığı IoC processor"
readme = "README.md"
license = "MIT"
requires-python = ">=3.11"
authors = [
    { name = "Author Name", email = "author@example.com" }
]
keywords = ["threat-intelligence", "ioc", "cybersecurity", "tc-sgb"]
classifiers = [
    "Development Status :: 5 - Production/Stable",
    "Intended Audience :: Information Technology",
    "License :: OSI Approved :: MIT License",
    "Programming Language :: Python :: 3.11",
    "Programming Language :: Python :: 3.12",
    "Topic :: Security",
]
dependencies = [
    "httpx>=0.27,<1",
    "pydantic>=2.0,<3",
    "rich>=13.0,<14",
]

[project.scripts]
tc-sgb = "Scripts.main:main"

[project.urls]
Homepage = "https://github.com/bayraktarozcan/TC-SGB-API-to-List"
Documentation = "https://github.com/bayraktarozcan/TC-SGB-API-to-List/tree/main/Docs"
Repository = "https://github.com/bayraktarozcan/TC-SGB-API-to-List"
Issues = "https://github.com/bayraktarozcan/TC-SGB-API-to-List/issues"
Changelog = "https://github.com/bayraktarozcan/TC-SGB-API-to-List/blob/main/CHANGELOG.md"
```

### Build & Publish Commands

```bash
# Build package
python -m build

# Verify package
twine check dist/*

# Upload to TestPyPI (testing)
twine upload --repository testpypi dist/*

# Upload to PyPI (production)
twine upload dist/*

# Or use GitHub Actions (recommended)
git tag -a v1.1.0 -m "Release v1.1.0"
git push origin v1.1.0
```

### Installation Methods

```bash
# Method 1: pip install from PyPI
pip install tc-sgb

# Method 2: pip install specific version
pip install tc-sgb==1.1.0

# Method 3: pip install from GitHub
pip install git+https://github.com/bayraktarozcan/TC-SGB-API-to-List.git@v0.1.0.0

# Method 4: pip install from source
git clone https://github.com/bayraktarozcan/TC-SGB-API-to-List.git
cd tc-sgb
pip install -e .

# Method 5: pipx (for CLI usage)
pipx install tc-sgb
```

---

## Output File Distribution

### Output Directory Structure

```
Output/
├── json/
│   └── tc-sgb-iocs-2025-01-20.json
├── csv/
│   └── tc-sgb-iocs-2025-01-20.csv
├── stix/
│   └── tc-sgb-iocs-2025-01-20.stix.json
├── misp/
│   └── tc-sgb-iocs-2025-01-20.misp.json
├── sigma/
│   └── tc-sgb-iocs-2025-01-20.yml
├── yara/
│   └── tc-sgb-iocs-2025-01-20.yar
├── html/
│   └── tc-sgb-report-2025-01-20.html
├── markdown/
│   └── tc-sgb-report-2025-01-20.md
├── checksums/
│   └── SHA256SUMS.txt
└── metadata/
    └── generation-info.json
```

### Checksum Generation

```python
import hashlib
from pathlib import Path


def generate_checksums(output_dir: Path) -> Path:
    """Generate SHA-256 checksums for all output files."""
    checksum_file = output_dir / "checksums" / "SHA256SUMS.txt"

    with open(checksum_file, "w") as f:
        for file_path in sorted(output_dir.rglob("*")):
            if file_path.is_file() and file_path.suffix != ".txt":
                sha256 = hashlib.sha256(file_path.read_bytes()).hexdigest()
                relative = file_path.relative_to(output_dir)
                f.write(f"{sha256}  {relative}\n")

    return checksum_file
```

### Metadata File

```json
{
  "generation": {
    "timestamp": "2025-01-20T12:00:00Z",
    "version": "1.1.0",
    "pipeline_version": "1.1.0",
    "python_version": "3.11.7",
    "duration_seconds": 28.5
  },
  "source": {
    "api_url": "https://siberguvenlik.gov.tr",
    "fetch_time": "2025-01-20T11:58:00Z",
    "total_records": 483690
  },
  "output": {
    "formats": ["json", "csv", "stix", "misp", "sigma", "yara", "html"],
    "total_files": 7,
    "total_size_bytes": 1048576,
    "checksums": "SHA256SUMS.txt"
  },
  "quality": {
    "overall_score": 0.94,
    "records_passed": 478500,
    "records_failed": 5190,
    "duplicates_removed": 8400
  }
}
```

---

## Publication Schedule

### Automated Schedule

```
+=====================================================================+
|  Publication Schedule                                                |
+=====================================================================+

  Event                Frequency           Channel
  +------------------+-------------------+------------------+
  | Full pipeline run | Daily (scheduled) | GitHub Actions   |
  | Output update     | Daily             | Local filesystem |
  | Bug fix release   | As needed         | PyPI + GitHub    |
  | Feature release   | Monthly           | PyPI + GitHub    |
  | Security patch    | ASAP              | PyPI + GitHub    |
  +------------------+-------------------+------------------+
```

### Scheduled Pipeline

```yaml
# .github/workflows/scheduled.yml
name: Weekly Pipeline
on:
  schedule:
    - cron: "0 19 * * *"  # Daily at 19:00 UTC

jobs:
  fetch-and-process:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Run pipeline
        run: tc-sgb fetch
      - name: Upload outputs
        uses: actions/upload-artifact@v3
        with:
          name: daily-outputs
          path: Output/
          retention-days: 30
```

---

## Version Distribution Matrix

| Version | PyPI | GitHub Release | Docker | Homebrew |
|---------|------|----------------|--------|----------|
| v1.0.x | Yes | Yes | No | No |
| v1.1.x | Yes | Yes | Yes | Yes |
| v2.0.x | Yes | Yes | Yes | Yes |

---

## Rollback Strategy

### PyPI Rollback

```bash
# Cannot delete from PyPI, but can yank
# Yanking makes version unavailable for install but keeps it visible

# Yank a release
pip install tc-sgb==1.1.0  # Still works
# But `pip install tc-sgb` won't pick it up

# Users can still install yanked version explicitly
pip install tc-sgb==1.1.0  # Works even if yanked
```

### GitHub Release Rollback

```bash
# Delete and recreate tag
git tag -d v1.1.0
git push origin :refs/tags/v1.1.0

# Create hotfix release
git tag -a v1.1.1 -m "Hotfix: critical bug fix"
git push origin v1.1.1
```

---

## Documentation Distribution

### Documentation Hosting

| Resource | Location | Update |
|----------|----------|--------|
| README | GitHub repo | Per release |
| API docs | GitHub Pages | Per release |
| Changelog | GitHub repo | Per release |
| Migration guides | GitHub repo | Per major release |
| Configuration reference | GitHub repo | Per release |

### Documentation Versioning

```
Docs/
├── v1.0/
│   ├── Architecture.md
│   └── ...
├── v1.1/
│   ├── Architecture.md
│   └── ...
├── latest -> v1.1/    # Symlink to latest
└── index.html          # Redirect to latest
```

<a id="-türkçe"></a>

# Yayın Stratejisi

## Genel Bakış

Bu belge, TC-SGB-API-to-List projesi için dağıtım ve yayın stratejisini, GitHub sürümleri, PyPI dağıtımı ve çıkış dosyası yönetimini tanımlar.

## Dağıtım Kanalları

```
+=====================================================================+
|                     Dağıtım Kanalları                                 |
+=====================================================================+

  +-------------------+     +-------------------+     +---------------+
  |                   |     |                   |     |               |
  |   GitHub          |     |   PyPI            |     |   Yerel       |
  |   Sürümleri       |     |   Paketi          |     |   Dosya Sistemi|
  |                   |     |                   |     |               |
  | - Kaynak kodu     |     | - pip install     |     | - Çıkış       |
  | - Wheel           |     | - Paket bağımlılıkları|  |   dosyaları   |
  | - Tarball         |     | - CLI giriş noktası|    | - Raporlar    |
  | - Sürüm notları   |     | - Sürüm yönetimi  |     | - Yapılandırmalar|
  | - Artifactlar     |     |                   |     |               |
  +-------------------+     +-------------------+     +---------------+
          |                         |                         |
          v                         v                         v
  +-------------------+     +-------------------+     +---------------+
  |                   |     |                   |     |               |
  |  Kaynak Dist      |     |  Wheel            |     |  Çıkış Dosyaları|
  |  .tar.gz          |     |  .whl             |     |  .json        |
  |  (tüm dosyalar)   |     |  (sadece Python)  |     |  .csv         |
  |                   |     |                   |     |  .stix.json   |
  +-------------------+     +-------------------+     |  .html        |
                                                       |  .md          |
                                                       |  ...16       |
                                                       +---------------+
```

---

## GitHub Sürümleri

### Sürüm Artifactları

Her GitHub sürümü şunları içerir:

| Artifact | Açıklama | Boyut (tahmini) |
|----------|----------|-----------------|
| Kaynak kodu (tar.gz) | Tam depo kaynağı | ~500 KB |
| Kaynak kodu (zip) | Tam depo kaynağı | ~600 KB |
| Wheel (.whl) | Oluşturulmuş Python paketi | ~200 KB |
| Çıkış örnekleri | Örnek çıkış dosyaları | ~1 MB |
| Doğrulama toplamları | Tüm artifactlar için SHA-256 | ~1 KB |
| Sürüm notları | PR'lardan otomatik oluşturulmuş | ~10 KB |

### Brave / AdGuard filtre listesi

Release bağlantıları dosya indirme olarak sunulur ve Brave bunları özel filtre listesi
olarak kabul etmez. Bu yüzden AdGuard çıktısı, yuvarlanan tek-commit'lik `filter-lists`
dalında düz metin olarak da aynalanır (tarih tutulmaz, Git LFS gerekmez); Scheduled Fetch
workflow'u ile her gün güncellenir. İki üçüncü taraf akış (Polonya, Slovenya)
aynı dalda ayrı listeler olarak yayınlanır; dosyalar numaralıdır, böylece Brave (abonelikleri
URL'ye göre sıralar) onları ülke sırasıyla gösterir (`04` Litvanya için ayrılmıştır;
kaynağı bir Cloudflare doğrulamasının arkasında olduğu için henüz çekilemiyor):

- Türkiye: <https://raw.githubusercontent.com/bayraktarozcan/TC-SGB-API-to-List/filter-lists/01-turkiye-sgb_adguard.txt>
- Polonya: <https://raw.githubusercontent.com/bayraktarozcan/TC-SGB-API-to-List/filter-lists/02-polonya-certpl_adguard.txt>
- Slovenya: <https://raw.githubusercontent.com/bayraktarozcan/TC-SGB-API-to-List/filter-lists/03-slovenya-certsi_adguard.txt>
- Brave'de `brave://adblock` → Add filter list via URL ile abone olun.

Azerbaycan `blacklist.gov.az` listesi kapsam dışıdır: içeriği güvenilir olmadığı ve
seçkin bir engel listesi için uygun düşmediği için artık çekilmiyor, doğrulanmıyor
veya yayımlanmıyor; dosyası daldan çıkarıldı.

### Harici güvenlik kapısı

Her harici akış, oluşturulmadan önce yayımlama güvenlik politikasından
(`Scripts/src/safety.py`) geçer: tam yüksek etkili makineler reddedilir, ortak
kullanıcı içerik uçları incelemeye ayrılır ve tutulan her gösterge gerekçesiyle
birlikte akış başına denetim dosyasına (`Output/External/` altında
`<feed>_audit.json`) ve ham kaynak anlık görüntüsünün yanına
(`<feed>_source.txt`) kaydedilir. Liste başlığı iki zaman damgasını da taşır:
`! Last updated` (üretim zamanı) ve kaynak bildirmişse `! Source updated`
(akış zamanı).

Yayımlamadan önce iş akışı `tc-sgb validate-external` çalıştırır (yerelde de
kullanılabilir) ve dala yalnızca kapıdan geçen dosyaları kopyalar. Kapıdan
geçemeyen akış son iyi anlık görüntüyü sunmaya devam eder; hiç geçmemiş bir
dosya asla güvenli kabul edilmez. Ana hat aynı politikayı alan adı göstergeleri
için kalite aşamasında uygular (koşu özetinde `safety_rejected`), kalite puanından
bağımsızdır. URL göstergeleri URL olarak kalır ve ana makineyi toptan engelleyen
bir üretici yükseltmeden önce aynı politikayı uygular; böylece tutulan bir ana
makine toptan kurala dönüşmez.

### Yayın Süreci

```
1. Geliştirici etiketi push eder
   git tag -a v1.1.0 -m "Release v1.1.0"
   git push origin v1.1.0

2. GitHub Actions release.yaml'yi tetikler
   ├── Tüm test paketini çalıştırır
   ├── Paketi oluşturur (sdist + wheel)
   ├── Sürüm notlarını oluşturur
   ├── GitHub Release oluşturur
   ├── Artifactları yükler
   └── PyPI'ya yayınlar

3. Yayın canlıya geçer
   ├── GitHub: github.com/bayraktarozcan/TC-SGB-API-to-List/releases/tag/v0.1.0.0
   ├── PyPI: pypi.org/project/tc-sgb/1.1.0/
   └── Artifactlar: Yayın sayfasından indirilebilir
```

### Yayın Sayfası Şablonu

```markdown
# Release v1.1.0

## What's New
- Added Sigma rule output format
- 30% faster deduplication
- Memory optimization for large datasets

## Installation

### From PyPI
pip install tc-sgb==1.1.0

### From Source
git clone https://github.com/bayraktarozcan/TC-SGB-API-to-List.git
cd tc-sgb
git checkout v1.1.0
pip install -e .

## Artifacts
| File | Checksum (SHA-256) |
|------|-------------------|
| tc-sgb-1.1.0.tar.gz | abc123... |
| tc_sgb-1.1.0-py3-none-any.whl | def456... |

## Migration Notes
- Config files now require `version: 2` key
- See Docs/Migration.md for details

## Full Changelog
https://github.com/bayraktarozcan/TC-SGB-API-to-List/compare/v0.1.0.0...v0.1.1.0
```

---

## PyPI Dağıtımı

### Paket Yapılandırması

```toml
# pyproject.toml
[build-system]
requires = ["setuptools>=68.0"]
build-backend = "setuptools.build_meta"

[project]
name = "tc-sgb"
version = "1.1.0"
description = "T.C. Siber Güvenlik Başkanlığı IoC processor"
readme = "README.md"
license = "MIT"
requires-python = ">=3.11"
authors = [
    { name = "Author Name", email = "author@example.com" }
]
keywords = ["threat-intelligence", "ioc", "cybersecurity", "tc-sgb"]
classifiers = [
    "Development Status :: 5 - Production/Stable",
    "Intended Audience :: Information Technology",
    "License :: OSI Approved :: MIT License",
    "Programming Language :: Python :: 3.11",
    "Programming Language :: Python :: 3.12",
    "Topic :: Security",
]
dependencies = [
    "httpx>=0.27,<1",
    "pydantic>=2.0,<3",
    "rich>=13.0,<14",
]

[project.scripts]
tc-sgb = "Scripts.main:main"

[project.urls]
Homepage = "https://github.com/bayraktarozcan/TC-SGB-API-to-List"
Documentation = "https://github.com/bayraktarozcan/TC-SGB-API-to-List/tree/main/Docs"
Repository = "https://github.com/bayraktarozcan/TC-SGB-API-to-List"
Issues = "https://github.com/bayraktarozcan/TC-SGB-API-to-List/issues"
Changelog = "https://github.com/bayraktarozcan/TC-SGB-API-to-List/blob/main/CHANGELOG.md"
```

### Derleme ve Yayın Komutları

```bash
# Paketi derle
python -m build

# Paketi doğrula
twine check dist/*

# TestPyPI'ya yükle (test)
twine upload --repository testpypi dist/*

# PyPI'ya yükle (üretim)
twine upload dist/*

# Veya GitHub Actions kullanın (önerilen)
git tag -a v1.1.0 -m "Release v1.1.0"
git push origin v1.1.0
```

### Yükleme Yöntemleri

```bash
# Yöntem 1: PyPI'dan pip install
pip install tc-sgb

# Yöntem 2: Belirli sürüme pip install
pip install tc-sgb==1.1.0

# Yöntem 3: GitHub'dan pip install
pip install git+https://github.com/bayraktarozcan/TC-SGB-API-to-List.git@v0.1.0.0

# Yöntem 4: Kaynaktan pip install
git clone https://github.com/bayraktarozcan/TC-SGB-API-to-List.git
cd tc-sgb
pip install -e .

# Yöntem 5: pipx (CLI kullanımı için)
pipx install tc-sgb
```

---

## Çıkış Dosyası Dağıtımı

### Çıkış Dizin Yapısı

```
Output/
├── json/
│   └── tc-sgb-iocs-2025-01-20.json
├── csv/
│   └── tc-sgb-iocs-2025-01-20.csv
├── stix/
│   └── tc-sgb-iocs-2025-01-20.stix.json
├── misp/
│   └── tc-sgb-iocs-2025-01-20.misp.json
├── sigma/
│   └── tc-sgb-iocs-2025-01-20.yml
├── yara/
│   └── tc-sgb-iocs-2025-01-20.yar
├── html/
│   └── tc-sgb-report-2025-01-20.html
├── markdown/
│   └── tc-sgb-report-2025-01-20.md
├── checksums/
│   └── SHA256SUMS.txt
└── metadata/
    └── generation-info.json
```

### Doğrulama Toplamı Oluşturma

```python
import hashlib
from pathlib import Path


def generate_checksums(output_dir: Path) -> Path:
    """Generate SHA-256 checksums for all output files."""
    checksum_file = output_dir / "checksums" / "SHA256SUMS.txt"

    with open(checksum_file, "w") as f:
        for file_path in sorted(output_dir.rglob("*")):
            if file_path.is_file() and file_path.suffix != ".txt":
                sha256 = hashlib.sha256(file_path.read_bytes()).hexdigest()
                relative = file_path.relative_to(output_dir)
                f.write(f"{sha256}  {relative}\n")

    return checksum_file
```

### Metadata Dosyası

```json
{
  "generation": {
    "timestamp": "2025-01-20T12:00:00Z",
    "version": "1.1.0",
    "pipeline_version": "1.1.0",
    "python_version": "3.11.7",
    "duration_seconds": 28.5
  },
  "source": {
    "api_url": "https://siberguvenlik.gov.tr",
    "fetch_time": "2025-01-20T11:58:00Z",
    "total_records": 483690
  },
  "output": {
    "formats": ["json", "csv", "stix", "misp", "sigma", "yara", "html"],
    "total_files": 7,
    "total_size_bytes": 1048576,
    "checksums": "SHA256SUMS.txt"
  },
  "quality": {
    "overall_score": 0.94,
    "records_passed": 478500,
    "records_failed": 5190,
    "duplicates_removed": 8400
  }
}
```

---

## Yayın Takvimi

### Otomatik Takvim

```
+=====================================================================+
|  Yayın Takvimi                                                       |
+=====================================================================+

  Olay                  Sıklık               Kanal
  +------------------+-------------------+------------------+
  | Tam hat çalışması | Günlük (planlanmış)| GitHub Actions   |
  | Çıkış güncellemesi| Günlük            | Yerel dosya sistemi|
  | Hata düzeltme yayını| İhtiyaça göre    | PyPI + GitHub    |
  | Özellik yayını    | Aylık             | PyPI + GitHub    |
  | Güvenlik yaması   | Mümkün olduğunca  | PyPI + GitHub    |
  +------------------+-------------------+------------------+
```

### Planlanmış Hat

```yaml
# .github/workflows/scheduled.yml
name: Weekly Pipeline
on:
  schedule:
    - cron: "0 19 * * *"  # Daily at 19:00 UTC

jobs:
  fetch-and-process:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Run pipeline
        run: tc-sgb fetch
      - name: Upload outputs
        uses: actions/upload-artifact@v3
        with:
          name: daily-outputs
          path: Output/
          retention-days: 30
```

---

## Sürüm Dağıtım Matrisi

| Sürüm | PyPI | GitHub Release | Docker | Homebrew |
|-------|------|----------------|--------|----------|
| v1.0.x | Evet | Evet | Hayır | Hayır |
| v1.1.x | Evet | Evet | Evet | Evet |
| v2.0.x | Evet | Evet | Evet | Evet |

---

## Geri Alma Stratejisi

### PyPI Geri Alma

```bash
# PyPI'dan silinemez, ancak geri çekilebilir (yank)
# Geri çekme, sürümün yüklenemez hale gelmesini sağlar ancak görünür kalır

# Bir yayını geri çek
pip install tc-sgb==1.1.0  # Hala çalışıyor
# Ancak `pip install tc-sgb` onu seçmez

# Kullanıcılar geri çekilmiş sürümü hala açıkça yükleyebilir
pip install tc-sgb==1.1.0  # Geri çekilmiş olsa bile çalışır
```

### GitHub Release Geri Alma

```bash
# Etiketi sil ve yeniden oluştur
git tag -d v1.1.0
git push origin :refs/tags/v1.1.0

# Acil düzeltme yayın oluştur
git tag -a v1.1.1 -m "Hotfix: critical bug fix"
git push origin v1.1.1
```

---

## Belgeleme Dağıtımı

### Belgeleme Barındırma

| Kaynak | Konum | Güncelleme |
|--------|-------|------------|
| README | GitHub deposu | Her yayında |
| API belgeleri | GitHub Pages | Her yayında |
| Değişiklik günlüğü | GitHub deposu | Her yayında |
| Geçiş kılavuzları | GitHub deposu | Her major yayında |
| Yapılandırma referansı | GitHub deposu | Her yayında |

### Belgeleme Sürümleme

```
Docs/
├── v1.0/
│   ├── Architecture.md
│   └── ...
├── v1.1/
│   ├── Architecture.md
│   └── ...
├── latest -> v1.1/    # En son sürüme sembolik bağ
└── index.html          # En son sürüme yönlendirme
```
