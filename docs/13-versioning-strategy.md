[English](#english) | [Türkçe](#turkish)

<a id="english"></a>

# Versioning Strategy

## Overview

This document defines the versioning strategy for the TC-SGB-API-to-List project using Semantic Versioning (SemVer) and the associated release note conventions.

## Semantic Versioning

### Format

```
MAJOR.MINOR.PATCH
```

| Component | Increment When | Example |
|-----------|----------------|---------|
| MAJOR | Breaking changes to public API, config format, or output schema | 2.0.0 |
| MINOR | New features, new output formats, backward-compatible | 1.1.0 |
| PATCH | Bug fixes, security patches, documentation updates | 1.0.1 |

### Pre-Release Versions

```
MAJOR.MINOR.PATCH-alpha.N    # Alpha testing
MAJOR.MINOR.PATCH-beta.N     # Beta testing
MAJOR.MINOR.PATCH-rc.N       # Release candidate
```

### Version Examples

| Version | Description |
|---------|-------------|
| 1.0.0 | Initial stable release |
| 1.0.1 | Bug fix release |
| 1.1.0 | Added Sigma output format |
| 1.2.0 | Added MISP output format |
| 2.0.0 | Breaking: New config format, dropped Python 3.10 |
| 2.0.0-rc.1 | Release candidate for v2 |

---

## Version Lifecycle

```
+=====================================================================+
|  Version Lifecycle                                                   |
+=====================================================================+

  Development          Pre-Release           Stable            Deprecated
  +----------+        +----------+         +----------+       +----------+
  |          |        |          |         |          |       |          |
  | 0.1.0    |------->| 1.0.0    |-------->| 1.0.x    |------>| 1.0.x    |
  | (dev)    |        | -alpha.N |  stable  | (patch)  | EOL  | (archived)|
  |          |        | -beta.N  |         |          |       |          |
  |          |        | -rc.N    |         |          |       |          |
  +----------+        +----------+         +----------+       +----------+

  Timeline:
  - Development: Active feature work
  - Pre-Release: Testing and stabilization
  - Stable: Production use, security patches
  - Deprecated: No longer maintained
```

---

## Release Process

### 1. Version Bump Decision

```
Does the change break backward compatibility?
├── YES → MAJOR version bump
└── NO
    ├── Does it add new functionality?
    │   ├── YES → MINOR version bump
    │   └── NO
    │       └── Is it a bug fix or security patch?
    │           └── YES → PATCH version bump
```

### 2. Release Workflow

```bash
# 1. Ensure all tests pass
pytest

# 2. Update version in pyproject.toml
# [project]
# version = "1.1.0"

# 3. Update CHANGELOG.md
# Add release notes for v1.1.0

# 4. Commit changes
git add -A
git commit -m "chore: bump version to 1.1.0"

# 5. Create and push tag
git tag -a v1.1.0 -m "Release v1.1.0: Add Sigma output format"
git push origin v1.1.0

# 6. GitHub Actions automatically:
#    - Runs full test suite
#    - Builds package
#    - Publishes to PyPI
#    - Creates GitHub Release
#    - Uploads artifacts
```

### 3. Automated Release Pipeline

```yaml
# .github/workflows/release.yml
name: Release
on:
  push:
    tags:
      - "v*.*.*"

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Run full test suite
        run: pytest

  build:
    needs: test
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Build package
        run: python -m build
      - name: Upload artifacts
        uses: actions/upload-artifact@v3
        with:
          name: dist
          path: dist/

  publish:
    needs: build
    runs-on: ubuntu-latest
    environment: release
    permissions:
      contents: write
    steps:
      - name: Download artifacts
        uses: actions/download-artifact@v3
        with:
          name: dist
          path: dist/

      - name: Publish to PyPI
        uses: pypa/gh-action-pypi-publish@release/v1
        with:
          password: ${{ secrets.PYPI_API_TOKEN }}

      - name: Create GitHub Release
        uses: softprops/action-gh-release@v1
        with:
          files: dist/*
          generate_release_notes: true
```

---

## Release Notes Convention

### Format

```markdown
# Release v1.1.0

**Release Date**: 2025-01-20

## What's New

### Features
- Added Sigma rule output format (`outputs.py`)
- Added YARA rule generation
- New `--format` CLI option for selective output

### Improvements
- 30% faster deduplication with Bloom filter
- Better error messages for validation failures
- Improved URL normalization (handles international domains)

### Bug Fixes
- Fixed CSV output missing header row (#42)
- Fixed timezone handling for API dates (#38)
- Fixed memory leak in large dataset processing (#45)

### Security
- Updated PyYAML to fix CVE-2024-XXXXX
- Pinned all GitHub Actions to commit SHAs

### Breaking Changes
- Removed deprecated `--legacy` CLI option
- Config file now requires `version: 2` key
- Output format names changed: `stix21` → `stix`

### Migration Guide
- Update config files to include `version: 2`
- Replace `--format stix21` with `--format stix`
- See MIGRATION.md for full details

## Performance
- Full pipeline: 28s → 19s for 10K records
- Memory usage: 120MB → 85MB for 100K records

## Dependencies
- Added: pybloom-live 1.2.0
- Updated: httpx 0.27.0 → 0.27.1
- Updated: pydantic 2.9.0 → 2.9.2

## Contributors
- @contributor1 - Sigma output implementation
- @contributor2 - Memory optimization
```

### Categories

| Category | Description | SemVer |
|----------|-------------|--------|
| **Features** | New functionality | MINOR |
| **Improvements** | Enhancements to existing features | MINOR |
| **Bug Fixes** | Error corrections | PATCH |
| **Security** | Vulnerability patches | PATCH |
| **Breaking Changes** | Backward-incompatible changes | MAJOR |
| **Deprecations** | Features marked for removal | MINOR |
| **Performance** | Speed/memory improvements | PATCH |
| **Dependencies** | Library updates | PATCH |
| **Documentation** | Doc improvements | PATCH |

---

## Backward Compatibility

### What Constitutes a Breaking Change

| Change | Breaking? | Version Bump |
|--------|-----------|--------------|
| Remove CLI option | YES | MAJOR |
| Rename CLI option | YES | MAJOR |
| Change config file format | YES | MAJOR |
| Change output JSON schema | YES | MAJOR |
| Remove output format | YES | MAJOR |
| Add required config key | YES | MAJOR |
| Change default values | MAYBE | MINOR or MAJOR |
| Add optional config key | NO | MINOR |
| Add new output format | NO | MINOR |
| Change internal API | NO | MINOR |
| Fix bug in output | NO | PATCH |
| Update dependencies | NO | PATCH |

### Compatibility Guarantees

```
+=====================================================================+
|  Compatibility Matrix                                                |
+=====================================================================+

  Version N.x.y guarantees:
  +---------------------------------------------------+
  | ✓ Same CLI interface                              |
  | ✓ Same config file format                         |
  | ✓ Same output JSON schema                         |
  | ✓ Same exit codes                                 |
  | ✓ Same environment variables                      |
  | ✓ Same Python version support                     |
  |                                                   |
  | ✗ No guarantee on internal module APIs            |
  | ✗ No guarantee on log format                      |
  | ✗ No guarantee on error message text              |
  +---------------------------------------------------+
```

---

## Changelog Management

### Changelog Format

```markdown
# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- ...

### Changed
- ...

### Fixed
- ...

## [1.1.0] - 2025-01-20

### Added
- Sigma output format
- YARA output format

### Fixed
- CSV header issue

## [1.0.0] - 2025-01-15

### Added
- Initial release
- 16 output formats
- Async API client
- Full test suite
```

### Automated Changelog

```yaml
# GitHub Release auto-generates release notes from:
# - PR titles since last release
# - Commit messages since last release
# - Contributors list
```

---

## Version Tagging

### Tag Format

```bash
# Semantic version tag
git tag -a v1.1.0 -m "Release v1.1.0"

# Pre-release tag
git tag -a v1.2.0-beta.1 -m "Beta release v1.2.0-beta.1"

# Release candidate
git tag -a v1.2.0-rc.1 -m "Release candidate v1.2.0-rc.1"
```

### Tag Verification

```bash
# List all tags
git tag -l

# Show tag details
git show v1.1.0

# Verify tag signature (if using GPG)
git tag -v v1.1.0
```

---

## Deprecation Policy

### Process

1. **Announce deprecation** in MINOR version release notes
2. **Add deprecation warning** in code (with removal version)
3. **Maintain for 2 MINOR versions** before removal
4. **Remove in MAJOR version** with migration guide

### Deprecation Warning

```python
import warnings

def deprecated_option():
    warnings.warn(
        "The '--legacy' option is deprecated since v1.1.0 "
        "and will be removed in v2.0.0. "
        "Use '--format new' instead.",
        DeprecationWarning,
        stacklevel=2,
    )
```

### Timeline Example

```
v1.0.0  Feature introduced
v1.1.0  Feature deprecated (warning added)
v1.2.0  Feature still deprecated (warning persists)
v2.0.0  Feature removed
```

<a id="turkish"></a>

# Sürüm Numaralandırma Stratejisi

## Genel Bakış

Bu belge, TC-SGB-API-to-List projesi için Anlamsal Sürüm Numaralandırması (SemVer) ve ilişkili sürüm notu kurallarını kullanan sürüm numaralandırma stratejisini tanımlar.

## Anlamsal Sürüm Numaralandırması

### Format

```
MAJOR.MINOR.PATCH
```

| Bileşen | Artırma Durumu | Örnek |
|---------|----------------|-------|
| MAJOR | Genel API, yapılandırma formatı veya çıkış şemasında geriye dönük uyumsuz değişiklikler | 2.0.0 |
| MINOR | Yeni özellikler, yeni çıkış formatları, geriye dönük uyumlu | 1.1.0 |
| PATCH | Hata düzeltmeleri, güvenlik yamaları, belgeleme güncellemeleri | 1.0.1 |

### Ön Yayın Sürümleri

```
MAJOR.MINOR.PATCH-alpha.N    # Alpha testi
MAJOR.MINOR.PATCH-beta.N     # Beta testi
MAJOR.MINOR.PATCH-rc.N       # Aday yayın
```

### Sürüm Örnekleri

| Sürüm | Açıklama |
|-------|----------|
| 1.0.0 | İlk kararlı yayın |
| 1.0.1 | Hata düzeltme yayını |
| 1.1.0 | Sigma çıkış formatı eklendi |
| 1.2.0 | MISP çıkış formatı eklendi |
| 2.0.0 | Kırıcı: Yeni yapılandırma formatı, Python 3.10 desteği kaldırıldı |
| 2.0.0-rc.1 | v2 için aday yayın |

---

## Sürüm Yaşam Döngüsü

```
+=====================================================================+
|  Sürüm Yaşam Döngüsü                                                 |
+=====================================================================+

  Geliştirme            Ön Yayın              Kararlı            Kullanımdan Kaldırılmış
  +----------+        +----------+         +----------+       +----------+
  |          |        |          |         |          |       |          |
  | 0.1.0    |------->| 1.0.0    |-------->| 1.0.x    |------>| 1.0.x    |
  | (dev)    |        | -alpha.N |  kararlı | (yama)  | EOL  | (arşivlenmis)|
  |          |        | -beta.N  |         |          |       |          |
  |          |        | -rc.N    |         |          |       |          |
  +----------+        +----------+         +----------+       +----------+

  Zaman Çizelgesi:
  - Geliştirme: Aktif özellik çalışması
  - Ön Yayın: Test ve kararlılaştırma
  - Kararlı: Üretim kullanımı, güvenlik yamaları
  - Kullanımdan Kaldırılmış: Artık desteklenmiyor
```

---

## Yayın Süreci

### 1. Sürüm Artırma Kararı

```
Değişiklik geriye dönük uyumluluğu kırıyor mu?
├── EVET → MAJOR sürüm artırımı
└── HAYIR
    ├── Yeni işlevsellik ekliyor mu?
    │   ├── EVET → MINOR sürüm artırımı
    │   └── HAYIR
    │       └── Bir hata düzeltmesi veya güvenlik yaması mı?
    │           └── EVET → PATCH sürüm artırımı
```

### 2. Yayın İş Akışı

```bash
# 1. Tüm testlerin geçtiğinden emin olun
pytest

# 2. pyproject.toml'da sürümü güncelleyin
# [project]
# version = "1.1.0"

# 3. CHANGELOG.md'yi güncelleyin
# v1.1.0 için sürüm notlarını ekleyin

# 4. Değişiklikleri commit edin
git add -A
git commit -m "chore: bump version to 1.1.0"

# 5. Etiket oluşturun ve push edin
git tag -a v1.1.0 -m "Release v1.1.0: Add Sigma output format"
git push origin v1.1.0

# 6. GitHub Actions otomatik olarak:
#    - Tüm test paketini çalıştırır
#    - Paketi oluşturur
#    - PyPI'ya yayınlar
#    - GitHub Release oluşturur
#    -Artifactları yükler
```

### 3. Otomatik Yayın Hattı

```yaml
# .github/workflows/release.yml
name: Release
on:
  push:
    tags:
      - "v*.*.*"

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Run full test suite
        run: pytest

  build:
    needs: test
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Build package
        run: python -m build
      - name: Upload artifacts
        uses: actions/upload-artifact@v3
        with:
          name: dist
          path: dist/

  publish:
    needs: build
    runs-on: ubuntu-latest
    environment: release
    permissions:
      contents: write
    steps:
      - name: Download artifacts
        uses: actions/download-artifact@v3
        with:
          name: dist
          path: dist/

      - name: Publish to PyPI
        uses: pypa/gh-action-pypi-publish@release/v1
        with:
          password: ${{ secrets.PYPI_API_TOKEN }}

      - name: Create GitHub Release
        uses: softprops/action-gh-release@v1
        with:
          files: dist/*
          generate_release_notes: true
```

---

## Sürüm Notu Kuralları

### Format

```markdown
# Release v1.1.0

**Release Date**: 2025-01-20

## What's New

### Features
- Added Sigma rule output format (`outputs.py`)
- Added YARA rule generation
- New `--format` CLI option for selective output

### Improvements
- 30% faster deduplication with Bloom filter
- Better error messages for validation failures
- Improved URL normalization (handles international domains)

### Bug Fixes
- Fixed CSV output missing header row (#42)
- Fixed timezone handling for API dates (#38)
- Fixed memory leak in large dataset processing (#45)

### Security
- Updated PyYAML to fix CVE-2024-XXXXX
- Pinned all GitHub Actions to commit SHAs

### Breaking Changes
- Removed deprecated `--legacy` CLI option
- Config file now requires `version: 2` key
- Output format names changed: `stix21` → `stix`

### Migration Guide
- Update config files to include `version: 2`
- Replace `--format stix21` with `--format stix`
- See MIGRATION.md for full details

## Performance
- Full pipeline: 28s → 19s for 10K records
- Memory usage: 120MB → 85MB for 100K records

## Dependencies
- Added: pybloom-live 1.2.0
- Updated: httpx 0.27.0 → 0.27.1
- Updated: pydantic 2.9.0 → 2.9.2

## Contributors
- @contributor1 - Sigma output implementation
- @contributor2 - Memory optimization
```

### Kategoriler

| Kategori | Açıklama | SemVer |
|----------|----------|--------|
| **Özellikler** | Yeni işlevsellik | MINOR |
| **İyileştirmeler** | Mevcut özelliklerde geliştirmeler | MINOR |
| **Hata Düzeltmeleri** | Hata düzeltmeleri | PATCH |
| **Güvenlik** | Güvenlik açığı yamaları | PATCH |
| **Kırıcı Değişiklikler** | Geriye dönük uyumsuz değişiklikler | MAJOR |
| **Kullanımdan Kaldırmalar** | Kaldırılmak üzere işaretlenen özellikler | MINOR |
| **Performans** | Hız/bellek iyileştirmeleri | PATCH |
| **Bağımlılıklar** | Kütüphane güncellemeleri | PATCH |
| **Belgeleme** | Belgeleme iyileştirmeleri | PATCH |

---

## Geriye Dönük Uyumluluk

### Kırıcı Değişiklik Oluşturan Durumlar

| Değişiklik | Kırıcı mı? | Sürüm Artırımı |
|------------|------------|-----------------|
| CLI seçeneği kaldırma | EVET | MAJOR |
| CLI seçeneği yeniden adlandırma | EVET | MAJOR |
| Yapılandırma dosyası formatını değiştirme | EVET | MAJOR |
| Çıkış JSON şemasını değiştirme | EVET | MAJOR |
| Çıkış formatını kaldırma | EVET | MAJOR |
| Gerekli yapılandırma anahtarı ekleme | EVET | MAJOR |
| Varsayılan değerleri değiştirme | BELKİ | MINOR veya MAJOR |
| Opsiyonel yapılandırma anahtarı ekleme | HAYIR | MINOR |
| Yeni çıkış formatı ekleme | HAYIR | MINOR |
| Dahili API'yi değiştirme | HAYIR | MINOR |
| Çıkışta hata düzeltme | HAYIR | PATCH |
| Bağımlılıkları güncelleme | HAYIR | PATCH |

### Uyumluluk Garantileri

```
+=====================================================================+
|  Uyumluluk Matrisi                                                   |
+=====================================================================+

  N.x.y sürümü garantileri:
  +---------------------------------------------------+
  | ✓ Aynı CLI arayüzü                                 |
  | ✓ Aynı yapılandırma dosyası formatı                |
  | ✓ Aynı çıkış JSON şeması                           |
  | ✓ Aynı çıkış kodları                                |
  | ✓ Aynı ortam değişkenleri                           |
  | ✓ Aynı Python sürüm desteği                         |
  |                                                    |
  | ✗ Dahili modül API'leri garanti edilmez             |
  | ✗ Günlük formatı garanti edilmez                    |
  | ✗ Hata mesajı metni garanti edilmez                 |
  +---------------------------------------------------+
```

---

## Değişiklik Günlüğü Yönetimi

### Değişiklik Günlüğü Formatı

```markdown
# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- ...

### Changed
- ...

### Fixed
- ...

## [1.1.0] - 2025-01-20

### Added
- Sigma output format
- YARA output format

### Fixed
- CSV header issue

## [1.0.0] - 2025-01-15

### Added
- Initial release
- 16 output formats
- Async API client
- Full test suite
```

### Otomatik Değişiklik Günlüğü

```yaml
# GitHub Release, son yayından bu yana otomatik olarak sürüm notları oluşturur:
# - Son yayından bu yana PR başlıkları
# - Son yayından bu yana commit mesajları
# - Katılımcı listesi
```

---

## Sürüm Etiketleme

### Etiket Formatı

```bash
# Anlamsal sürüm etiketi
git tag -a v1.1.0 -m "Release v1.1.0"

# Ön yayın etiketi
git tag -a v1.2.0-beta.1 -m "Beta release v1.2.0-beta.1"

# Aday yayın
git tag -a v1.2.0-rc.1 -m "Release candidate v1.2.0-rc.1"
```

### Etiket Doğrulama

```bash
# Tüm etiketleri listele
git tag -l

# Etiket ayrıntılarını göster
git show v1.1.0

# Etiket imzasını doğrula (GPG kullanıyorsanız)
git tag -v v1.1.0
```

---

## Kullanımdan Kaldırma Politikası

### Süreç

1. **Kullanımdan kaldırmayı duyurun** MINOR sürüm yayın notlarında
2. **Kullanımdan kaldırma uyarısı ekleyin** kodda (kaldırma sürümü ile birlikte)
3. **Kaldırmadan önce 2 MINOR sürüm boyunca koruyun**
4. **MAJOR sürümde kaldırın** geçiş kılavuzu ile birlikte

### Kullanımdan Kaldırma Uyarısı

```python
import warnings

def deprecated_option():
    warnings.warn(
        "The '--legacy' option is deprecated since v1.1.0 "
        "and will be removed in v2.0.0. "
        "Use '--format new' instead.",
        DeprecationWarning,
        stacklevel=2,
    )
```

### Zaman Çizelgesi Örneği

```
v1.0.0  Özellik tanıtıldı
v1.1.0  Özellik kullanımdan kaldırıldı (uyarı eklendi)
v1.2.0  Özellik hala kullanımdan kaldırılmış (uyarı devam ediyor)
v2.0.0  Özellik kaldırıldı
```
