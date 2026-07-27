> **Language / Dil** &nbsp;
> [EN English](#-english) &nbsp;·&nbsp; [TR Türkçe](#-türkçe)

<a id="-english"></a>

# Security Analysis

## Overview

This document provides a comprehensive security analysis of the TC-SGB-API-to-List system, covering supply chain security, dependency management, GitHub Actions CI/CD security, and runtime security considerations.

## Supply Chain Security

### Dependency Inventory

#### Direct Dependencies

| Package | Version | Purpose | Risk Level |
|---------|---------|---------|------------|
| httpx | 0.27+ | Async HTTP client | LOW |
| pydantic | 2.9+ | Data validation | LOW |
| rich | 13.0+ | Terminal formatting | LOW |

#### Development Dependencies

| Package | Version | Purpose | Risk Level |
|---------|---------|---------|------------|
| pytest | 8.x | Testing | LOW |
| pytest-asyncio | 0.23+ | Async tests | LOW |
| pytest-cov | 5.x | Coverage | LOW |
| mypy | 1.10+ | Type checking | LOW |
| ruff | 0.5+ | Linting | LOW |
| bandit | 1.7+ | Security linting | LOW |
| pip-audit | 2.7+ | Dependency auditing | LOW |
| hypothesis | 6.100+ | Property testing | LOW |

### Dependency Risks

```
+=====================================================================+
|  Supply Chain Risk Assessment                                        |
+=====================================================================+

  Risk Factor              Assessment
  +------------------+     +------------------------------------------+
  | Dependency Count |     | LOW  (~3 direct, ~20 transitive)         |
  +------------------+     +------------------------------------------+
  | Known Vulns       |     | LOW  ( Dependabot monitors)             |
  +------------------+     +------------------------------------------+
  | Maintainer Trust  |     | HIGH (well-known packages)              |
  +------------------+     +------------------------------------------+
  | Pinning Strategy  |     | MEDIUM (version ranges in pyproject)    |
  +------------------+     +------------------------------------------+
  | Update Frequency  |     | LOW  (automated via Dependabot)         |
  +------------------+     +------------------------------------------+
  | Attack Surface    |     | LOW  (minimal dependency set)           |
  +------------------+     +------------------------------------------+
```

### Mitigation: Dependency Pinning

```toml
# pyproject.toml - Recommended pinning strategy
[project]
dependencies = [
    "httpx>=0.27,<1",
    "pydantic>=2.0,<3",
    "rich>=13.0,<14",
]

[project.optional-dependencies]
dev = [
    "pytest>=8.0,<9",
    "pytest-asyncio>=0.23,<1",
    "pytest-cov>=5.0,<6",
    "ruff>=0.5,<1",
    "mypy>=1.10,<2",
    "bandit>=1.7,<2",
    "pip-audit>=2.7,<3",
    "hypothesis>=6.100,<7",
]
```

### Mitigation: Lock File

```bash
# Generate lock file
pip-compile pyproject.toml --output-file=requirements.lock

# Install from lock
pip install -r requirements.lock
```

### Mitigation: Dependency Scanning

```yaml
# .github/workflows/security.yml
- name: Run Safety Check
  run: pip-audit

- name: Run Snyk
  uses: snyk/actions/python@master

- name: Check for known vulnerabilities
  run: safety check --full-report
```

---

## GitHub Actions Security

### Workflow Permissions

```yaml
# Recommended minimal permissions
permissions:
  contents: read          # Read repository
  contents: write         # Create releases (release.yaml only)
  packages: write         # Publish to PyPI (release.yaml only)
  security-events: write  # Upload SARIF results
```

### Workflow Security Matrix

| Workflow | Trigger | Permissions | Risk |
|----------|---------|-------------|------|
| `ci.yml` | push, PR | contents: read | LOW |
| `release.yaml` | tag push | contents: write, packages: write | MEDIUM |
| `scheduled.yml` | cron | contents: read, write | MEDIUM |

### Potential Attack Vectors

#### 1. Pull Request Attacks

```
+---------------------------------------------------+
|  ATTACK: Malicious PR modifies CI workflow         |
+---------------------------------------------------+
|                                                   |
|  1. Attacker forks repository                     |
|  2. Modifies .github/workflows/ci.yml            |
|  3. Adds malicious step (e.g., reverse shell)     |
|  4. Opens PR to upstream                          |
|  5. If merged, attacker gains CI access           |
|                                                   |
|  MITIGATION:                                      |
|  - Require PR approval from maintainers           |
|  - Lock workflow files (require approval)         |
|  - Use pinned action versions                     |
|  - Run untrusted code in sandbox                  |
+---------------------------------------------------+
```

#### 2. Action Version Pinning

```yaml
# BAD: Floating tag (vulnerable to tag hijacking)
- uses: actions/checkout@v4
- uses: actions/setup-python@v5

# GOOD: Pinned to commit SHA
- uses: actions/checkout@b4ffde65f46336ab88eb53be808477a3936bae11  # v4.1.1
- uses: actions/setup-python@0a5c61591de30f1073f4f3e1d665f48f8f78f701  # v5.0.0
```

#### 3. Secrets Management

```
+---------------------------------------------------+
|  SECRETS IN GITHUB ACTIONS                        |
+---------------------------------------------------+
|                                                   |
|  Required Secrets:                                |
|  - PYPI_API_TOKEN          (release.yaml)          |
|  - (No other secrets required)                    |
|                                                   |
|  Best Practices:                                  |
|  - Use GitHub Environments for deployment         |
|  - Limit secret access to specific workflows      |
|  - Rotate tokens periodically                     |
|  - Never echo secrets to logs                     |
|  - Use OIDC for PyPI publishing when available    |
+---------------------------------------------------+
```

#### 4. Workflow Hardening

```yaml
# Hardened workflow example
name: CI
on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

permissions:
  contents: read

jobs:
  test:
    runs-on: ubuntu-latest
    timeout-minutes: 15

    steps:
      - name: Checkout
        uses: actions/checkout@b4ffde65f46336ab88eb53be808477a3936bae11

      - name: Setup Python
        uses: actions/setup-python@0a5c61591de30f1073f4f3e1d665f48f8f78f701
        with:
          python-version: "3.11"

      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install -r requirements.lock

      - name: Lint
        run: ruff check scripts/ tests/

      - name: Type check
        run: mypy scripts/

      - name: Test
        run: pytest tests/ --cov=scripts --cov-report=xml

      - name: Upload coverage
        uses: codecov/codecov-action@v3
```

---

## Runtime Security

### Process Isolation

```
+---------------------------------------------------+
|  RECOMMENDED DEPLOYMENT MODEL                     |
+---------------------------------------------------+
|                                                   |
|  Option 1: Local Execution (Recommended)          |
|  - Run on dedicated workstation/server            |
|  - No container required                          |
|  - Direct filesystem access                       |
|                                                   |
|  Option 2: Container Execution                    |
|  - Docker/Podman container                        |
|  - Read-only filesystem where possible            |
|  - Dropped capabilities                           |
|  - Non-root user                                  |
|                                                   |
|  Option 3: Serverless (GitHub Actions)            |
|  - Ephemeral environment                          |
|  - No persistent state                            |
|  - Network access only to API                     |
+---------------------------------------------------+
```

### Filesystem Security

```bash
# Recommended permissions
chmod 700 ~/.config/tc-sgb/           # Config directory
chmod 600 ~/.config/tc-sgb/config.yaml  # Config file
chmod 755 output/                      # Output directory
chmod 644 output/*                     # Output files

# Run as non-root user
useradd -r -s /bin/false tc-sgb
chown -R tc-sgb:tc-sgb /opt/tc-sgb/
```

### Network Security

```
+---------------------------------------------------+
|  NETWORK SECURITY CONTROLS                        |
+---------------------------------------------------+
|                                                   |
|  Outbound:                                        |
|  - HTTPS only (port 443)                          |
|  - To threatintel.sgbsg.gov.tr only              |
|  - No other network access required               |
|                                                   |
|  Inbound:                                         |
|  - None required                                  |
|  - Pipeline is pull-only (no server mode)         |
|                                                   |
|  DNS:                                             |
|  - Use system resolver                            |
|  - Consider DNS-over-HTTPS for integrity          |
+---------------------------------------------------+
```

### Memory Safety

| Concern | Mitigation |
|---------|------------|
| Large dataset OOM | Stream processing, chunked reads |
| Unbounded growth | Memory limits on batch sizes |
| String duplication | Intern common strings |
| Circular references | Pydantic frozen models prevent |
| Memory leaks | Generators instead of lists where possible |

### Logging Security

```python
# SAFE: Structured logging without sensitive data
logger.info("fetched_page", page=page_num, records=len(records))

# UNSAFE: Logging raw IOC data
logger.debug(f"IOC data: {record}")  # NEVER DO THIS

# UNSAFE: Logging with f-string interpolation
logger.info(f"Processing {len(records)} records from {url}")  # Prefer structured
```

### Input Validation Security

```python
# All input validation happens through Pydantic
from pydantic import BaseModel, Field, field_validator


class IOCRecord(BaseModel):
    @field_validator("value")
    @classmethod
    def validate_value(cls, v: str) -> str:
        # Reject null bytes
        if "\x00" in v:
            raise ValueError("Value contains null bytes")
        # Reject control characters (except tab/newline)
        if any(ord(c) < 32 and c not in "\t\n\r" for c in v):
            raise ValueError("Value contains control characters")
        # Enforce length limit
        if len(v) > 2048:
            raise ValueError("Value exceeds maximum length")
        return v
```

---

## Security Checklist

### Pre-Deployment

- [ ] All dependencies pinned and locked
- [ ] No known vulnerabilities in dependencies (`pip-audit`)
- [ ] All GitHub Actions pinned to commit SHAs
- [ ] Workflow permissions set to minimum required
- [ ] Secrets stored in GitHub Secrets (not in code)
- [ ] Branch protection enabled on main branch
- [ ] PR reviews required before merge
- [ ] Type checking passes (`mypy --strict`)
- [ ] Linting passes (`ruff check`)
- [ ] All tests pass (`pytest`)
- [ ] Security scan passes (CodeQL/Snyk)

### Runtime

- [ ] Running as non-root user
- [ ] Filesystem permissions correctly set
- [ ] No sensitive data in logs
- [ ] TLS verification enabled
- [ ] Rate limiting configured
- [ ] Error handling doesn't leak information
- [ ] Output files have appropriate permissions

### Post-Deployment

- [ ] Monitoring configured
- [ ] Alerting for security events
- [ ] Incident response plan documented
- [ ] Regular dependency updates via Dependabot
- [ ] Periodic security audits scheduled

---

## Security Recommendations

### Priority 1: Critical

1. **Enable TLS verification** — Never disable certificate validation
2. **Input validation** — All API data validated before processing
3. **No code execution** — Never eval/exec on input data
4. **Dependency pinning** — Lock all dependency versions

### Priority 2: High

5. **GitHub Actions hardening** — Pin actions to SHAs, minimal permissions
6. **Secret management** — Use GitHub Secrets, rotate regularly
7. **Audit logging** — Track all pipeline operations
8. **Output integrity** — Generate checksums for all outputs

### Priority 3: Medium

9. **Container hardening** — If using containers, drop capabilities
10. **Network restrictions** — Limit outbound to API endpoint only
11. **Memory limits** — Set ulimits for processing
12. **Regular scanning** — Automated vulnerability scanning

### Priority 4: Low

13. **Security headers** — If serving output via web server
14. **Encryption at rest** — For sensitive output files
15. **Backup security** — Encrypted backups of configurations
16. **Incident response drills** — Regular security exercises

---

<a id="-türkçe"></a>

# Güvenlik Analizi

## Genel Bakış

Bu belge, TC-SGB-API-to-List sisteminin kapsamlı bir güvenlik analizini sunmakta olup tedarik zinciri güvenliği, bağımlılık yönetimi, GitHub Actions CI/CD güvenliği ve çalışma zamanı güvenlik değerlendirmelerini kapsamaktadır.

## Tedarik Zinciri Güvenliği

### Bağımlılık Envanteri

#### Doğrudan Bağımlılıklar

| Paket | Sürüm | Amaç | Risk Seviyesi |
|-------|-------|------|---------------|
| httpx | 0.27+ | Eşzamansız HTTP istemcisi | DÜŞÜK |
| pydantic | 2.9+ | Veri doğrulama | DÜŞÜK |
| rich | 13.0+ | Terminal biçimlendirme | DÜŞÜK |

#### Geliştirme Bağımlılıkları

| Paket | Sürüm | Amaç | Risk Seviyesi |
|-------|-------|------|---------------|
| pytest | 8.x | Test | DÜŞÜK |
| pytest-asyncio | 0.23+ | Eşzamansız testler | DÜŞÜK |
| pytest-cov | 5.x | Kod kapsama | DÜŞÜK |
| mypy | 1.10+ | Tür kontrolü | DÜŞÜK |
| ruff | 0.5+ | Kod denetleme | DÜŞÜK |
| bandit | 1.7+ | Güvenlik denetimi | DÜŞÜK |
| pip-audit | 2.7+ | Bağımlılık denetimi | DÜŞÜK |
| hypothesis | 6.100+ | Özellik testi | DÜŞÜK |

### Bağımlılık Riskleri

```
+=====================================================================+
|  Tedarik Zinciri Risk Değerlendirmesi                                |
+=====================================================================+

  Risk Faktörü             Değerlendirme
  +------------------+     +------------------------------------------+
  | Bağımlılık Sayısı|     | DÜŞÜK  (~3 doğrudan, ~20 geçişli)       |
  +------------------+     +------------------------------------------+
  | Bilinen Zafiyetler|    | DÜŞÜK  ( Dependabot izler)             |
  +------------------+     +------------------------------------------+
  | Bakıcı Güveni     |    | YÜKSEK (bilinen paketler)              |
  +------------------+     +------------------------------------------+
  | Sabitleme Stratejisi|  | ORTA   (pyproject'te sürüm aralıkları) |
  +------------------+     +------------------------------------------+
  | Güncelleme Sıklığı |   | DÜŞÜK  (Dependabot ile otomatik)       |
  +------------------+     +------------------------------------------+
  | Saldırı Yüzeyi    |    | DÜŞÜK  (minimal bağımlılık kümesi)     |
  +------------------+     +------------------------------------------+
```

### Azaltma: Bağımlılık Sabitleme

```toml
# pyproject.toml - Önerilen sabitleme stratejisi
[project]
dependencies = [
    "httpx>=0.27,<1",
    "pydantic>=2.0,<3",
    "rich>=13.0,<14",
]

[project.optional-dependencies]
dev = [
    "pytest>=8.0,<9",
    "pytest-asyncio>=0.23,<1",
    "pytest-cov>=5.0,<6",
    "ruff>=0.5,<1",
    "mypy>=1.10,<2",
    "bandit>=1.7,<2",
    "pip-audit>=2.7,<3",
    "hypothesis>=6.100,<7",
]
```

### Azaltma: Kilitleme Dosyası

```bash
# Kilitleme dosyası oluşturma
pip-compile pyproject.toml --output-file=requirements.lock

# Kilitten yükleme
pip install -r requirements.lock
```

### Azaltma: Bağımlılık Taraması

```yaml
# .github/workflows/security.yml
- name: Run Safety Check
  run: pip-audit

- name: Run Snyk
  uses: snyk/actions/python@master

- name: Check for known vulnerabilities
  run: safety check --full-report
```

---

## GitHub Actions Güvenliği

### İş Akışı İzinleri

```yaml
# Önerilen minimum izinler
permissions:
  contents: read          # Depoyu oku
  contents: write         # Sürüm oluştur (yalnızca release.yaml)
  packages: write         # PyPI'ya yayınla (yalnızca release.yaml)
  security-events: write  # SARIF sonuçlarını yükle
```

### İş Akışı Güvenlik Matrisi

| İş Akışı | Tetikleyici | İzinler | Risk |
|----------|-------------|---------|------|
| `ci.yml` | push, PR | contents: read | DÜŞÜK |
| `release.yaml` | etiket push | contents: write, packages: write | ORTA |
| `scheduled.yml` | cron | contents: read, write | ORTA |

### Olası Saldırı Vektörleri

#### 1. Çekme İsteği Saldırıları

```
+---------------------------------------------------+
|  SALDIRI: Kötü amaçlı PR iş akışını değiştirir    |
+---------------------------------------------------+
|                                                   |
|  1. Saldıran depoyu çatalandırır                  |
|  2. .github/workflows/ci.yml dosyasını değiştirir |
|  3. Kötü amaçlı adım ekler (ör. ters kabuk)       |
|  4. Üst akıma PR açar                             |
|  5. Birleştirilirse saldırgan CI erişimi kazanır  |
|                                                   |
|  AZALTMA:                                         |
|  - Bakıcılardan PR onayı zorunlu kılma           |
|  - İş akışı dosyalarını kilitleme (onay gerektir) |
|  - Sabitlenmiş eylem sürümleri kullanma            |
|  - Güvenilmez kodu sandıkta çalıştırma            |
+---------------------------------------------------+
```

#### 2. Eylem Sürümü Sabitleme

```yaml
# KÖTÜ: Yüzen etiket (etiket ele geçirmeye karşı savunmasız)
- uses: actions/checkout@v4
- uses: actions/setup-python@v5

# İYİ: Commit SHA'sına sabitlenmiş
- uses: actions/checkout@b4ffde65f46336ab88eb53be808477a3936bae11  # v4.1.1
- uses: actions/setup-python@0a5c61591de30f1073f4f3e1d665f48f8f78f701  # v5.0.0
```

#### 3. Gizli Anahtar Yönetimi

```
+---------------------------------------------------+
|  GITHUB ACTIONS'TA GİZLİ ANAHTARLAR              |
+---------------------------------------------------+
|                                                   |
|  Gerekli Gizli Anahtarlar:                        |
|  - PYPI_API_TOKEN          (release.yaml)          |
|  - (Diğer gizli anahtar gerekmez)                |
|                                                   |
|  En İyi Uygulamalar:                              |
|  - Dağıtım için GitHub Ortamları kullanma         |
|  - Gizli anahtar erişimini belirli iş akışlarıyla |
|    kısıtlama                                      |
|  - Jetonları düzenli olarak değiştirme            |
|  - Gizli anahtarları asla günlüklerde göstermeme  |
|  - Mevcut olduğunda PyPI yayını için OIDC kullanma|
+---------------------------------------------------+
```

#### 4. İş Akışı Güçlendirme

```yaml
# Güçlendirilmiş iş akışı örneği
name: CI
on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

permissions:
  contents: read

jobs:
  test:
    runs-on: ubuntu-latest
    timeout-minutes: 15

    steps:
      - name: Checkout
        uses: actions/checkout@b4ffde65f46336ab88eb53be808477a3936bae11

      - name: Setup Python
        uses: actions/setup-python@0a5c61591de30f1073f4f3e1d665f48f8f78f701
        with:
          python-version: "3.11"

      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install -r requirements.lock

      - name: Lint
        run: ruff check scripts/ tests/

      - name: Type check
        run: mypy scripts/

      - name: Test
        run: pytest tests/ --cov=scripts --cov-report=xml

      - name: Upload coverage
        uses: codecov/codecov-action@v3
```

---

## Çalışma Zamanı Güvenliği

### Süreç İzolasyonu

```
+---------------------------------------------------+
|  ÖNERİLEN DAĞITIM MODELİ                         |
+---------------------------------------------------+
|                                                   |
|  Seçenek 1: Yerel Çalıştırma (Önerilen)           |
|  - Adanmış iş istasyonunda/sunucuda çalıştırma    |
|  - Konteynere gerek yok                           |
|  - Doğrudan dosya sistemi erişimi                 |
|                                                   |
|  Seçenek 2: Konteyner Çalıştırması                |
|  - Docker/Podman konteyneri                       |
|  - Mümkün olduğunda salt okunur dosya sistemi     |
|  - Düşürülmüş yetenekler                          |
|  - Kök kullanıcı olmayan hesap                    |
|                                                   |
|  Seçenek 3: Sunucusuz (GitHub Actions)            |
|  - Geçici ortam                                   |
|  - Kalıcı durum yok                               |
|  - Yalnızca API'ye ağ erişimi                     |
+---------------------------------------------------+
```

### Dosya Sistemi Güvenliği

```bash
# Önerilen izinler
chmod 700 ~/.config/tc-sgb/           # Yapılandırma dizini
chmod 600 ~/.config/tc-sgb/config.yaml  # Yapılandırma dosyası
chmod 755 output/                      # Çıktı dizini
chmod 644 output/*                     # Çıktı dosyaları

# Kök olmayan kullanıcı olarak çalıştırma
useradd -r -s /bin/false tc-sgb
chown -R tc-sgb:tc-sgb /opt/tc-sgb/
```

### Ağ Güvenliği

```
+---------------------------------------------------+
|  AĞ GÜVENLİĞİ KONTROLLERİ                       |
+---------------------------------------------------+
|                                                   |
|  Dışa Giden:                                      |
|  - Yalnızca HTTPS (443. port)                     |
|  - Yalnızca threatintel.sgbsg.gov.tr adresine     |
|  - Başka ağ erişimi gerekmez                      |
|                                                   |
|  İçeri Gelen:                                     |
|  - Gerekmez                                       |
|  - Hat yalnızca çekme modundadır (sunucu modu yok)|
|                                                   |
|  DNS:                                             |
|  - Sistem çözümleyicisi kullanma                  |
|  - Bütünlük için DNS-over-HTTPS'i değerlendirin   |
+---------------------------------------------------+
```

### Bellek Güvenliği

| Endişe | Azaltma |
|--------|---------|
| Büyük veri seti OOM | Akış işleme, parçalı okumalar |
| Sınırsız büyüme | Toplu iş boyutlarında bellek sınırları |
| Dize tekrarı | Ortak dizeleri dahil etme |
| Döngüsel referanslar | Pydantic donmuş modelleri önler |
| Bellek sızıntıları | Mümkün olduğunda listeler yerine üreteçler |

### Kayıt Güvenliği

```python
# GÜVENLİ: Hassas veri olmayan yapılandırılmış kayıt
logger.info("fetched_page", page=page_num, records=len(records))

# GÜVENLİSİZ: Ham IOC verisini kaydetme
logger.debug(f"IOC data: {record}")  # BUNU ASLA YAPMAYIN

# GÜVENLİSİZ: f-string ile kayıt
logger.info(f"Processing {len(records)} records from {url}")  # Yapılandırılmış tercih edin
```

### Giriş Doğrulama Güvenliği

```python
# Tüm giriş doğrulaması Pydantic aracılığıyla yapılır
from pydantic import BaseModel, Field, field_validator


class IOCRecord(BaseModel):
    @field_validator("value")
    @classmethod
    def validate_value(cls, v: str) -> str:
        # Null byte'ları reddetme
        if "\x00" in v:
            raise ValueError("Value contains null bytes")
        # Kontrol karakterlerini reddetme (tab/newline hariç)
        if any(ord(c) < 32 and c not in "\t\n\r" for c in v):
            raise ValueError("Value contains control characters")
        # Uzunluk sınırını zorunlu kılma
        if len(v) > 2048:
            raise ValueError("Value exceeds maximum length")
        return v
```

---

## Güvenlik Kontrol Listesi

### Dağıtım Öncesi

- [ ] Tüm bağımlılıklar sabitlenmiş ve kilitlenmiş
- [ ] Bağımlılıklarda bilinen zafiyet yok (`pip-audit`)
- [ ] Tüm GitHub Actions commit SHA'larına sabitlenmiş
- [ ] İş akışı izinleri gerekli asgari düzeye ayarlanmış
- [ ] Gizli anahtarlar GitHub Secrets'ta saklanıyor (kodda değil)
- [ ] Ana dalda dal koruması etkinleştirilmiş
- [ ] Birleştirmeden önce PR incelemeleri gerekli
- [ ] Tür kontrolü geçiyor (`mypy --strict`)
- [ ] Kod denetleme geçiyor (`ruff check`)
- [ ] Tüm testler geçiyor (`pytest`)
- [ ] Güvenlik taraması geçiyor (CodeQL/Snyk)

### Çalışma Zamanı

- [ ] Kök olmayan kullanıcı olarak çalışıyor
- [ ] Dosya sistemi izinleri doğru ayarlanmış
- [ ] Günlüklerde hassas veri yok
- [ ] TLS doğrulaması etkinleştirilmiş
- [ ] Hız sınırı yapılandırılmış
- [ ] Hata işleme bilgi sızdırmıyor
- [ ] Çıktı dosyaları uygun izinlere sahip

### Dağıtım Sonrası

- [ ] İzleme yapılandırılmış
- [ ] Güvenlik olayları için uyarı
- [ ] Olay müdahale planı belgelenmiş
- [ ] Dependabot aracılığıyla düzenli bağımlılık güncellemeleri
- [ ] Periyodik güvenlik denetimleri planlanmış

---

## Güvenlik Önerileri

### Öncelik 1: Kritik

1. **TLS doğrulamasını etkinleştirme** — Sertifika doğrulamasını asla devre dışı bırakma
2. **Giriş doğrulaması** — Tüm API verileri işlenmeden önce doğrulanır
3. **Kod çalıştırma yok** — Giriş verileri üzerinde asla eval/exec çalıştırma
4. **Bağımlılık sabitleme** — Tüm bağımlılık sürümlerini kilitle

### Öncelik 2: Yüksek

5. **GitHub Actions güçlendirme** — Eylemleri SHA'lara sabitleme, minimum izinler
6. **Gizli anahtar yönetimi** — GitHub Secrets kullanma, düzenli olarak değiştirme
7. **Denetim kaydı** — Tüm hat işlemlerini izleme
8. **Çıktı bütünlüğü** — Tüm çıktılar için kontrol toplamları üretme

### Öncelik 3: Orta

9. **Konteyner güçlendirme** — Konteyner kullanıyorsanız yetenekleri düşürme
10. **Ağ kısıtlamaları** — Dışa giden trafiği yalnızca API uç noktasına kısıtlama
11. **Bellek sınırları** - İşleme için ulimit'leri ayarlama
12. **Düzenli tarama** — Otomatik zafiyet taraması

### Öncelik 4: Düşük

13. **Güvenlik başlıkları** — Çıktıyı web sunucusuyla sunuyorsanız
14. **Depolamada şifreleme** — Hassas çıktı dosyaları için
15. **Yedekleme güvenliği** — Yapılandırmaların şifreli yedekleri
16. **Olay müdahale tatbikatları** — Düzenli güvenlik tatbikatları
