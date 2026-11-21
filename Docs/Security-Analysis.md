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
| httpx | latest | Async HTTP client | LOW |
| pydantic | latest | Data validation | LOW |


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
  | Version Policy   |     | LOW  (unpinned, resolve latest)         |
  +------------------+     +------------------------------------------+
  | Update Frequency  |     | LOW  (automated via deps-update)        |
  +------------------+     +------------------------------------------+
  | Attack Surface    |     | LOW  (minimal dependency set)           |
  +------------------+     +------------------------------------------+
```

### Mitigation: Always-Latest Dependencies

Editors (`requirements.in`, `requirements-dev.in`) and `pyproject.toml` are
unpinned; the latest compatible versions resolve at install time. Compiled
snapshots (`requirements.txt`, `requirements-dev.txt`) are regenerated weekly
by `deps-update.yml`, so they never rot silently.

```toml
# pyproject.toml - always-latest policy (no version pins)
[project]
dependencies = [
    "httpx",
    "pydantic",
    "python-dotenv",
    "pyyaml",
]
```

### Mitigation: Regenerated Lock Snapshots

```bash
# Regenerate compiled snapshots to latest (weekly automation)
python Scripts/sync_deps.py --upgrade --compile-only

# Install latest into the local environment
pip install -e ".[dev]"
```

### Mitigation: Dependency Scanning

```yaml
# .github/workflows/ci.yml + .gitlab-ci.yml (security job)
- name: pip-audit
  run: pip-audit

- name: Bandit security scan
  run: bandit -r Scripts/
```

---

## GitHub Actions Security

### Workflow Permissions

```yaml
# Recommended minimal permissions
permissions:
  contents: read          # Read repository
  contents: write         # Push branches / create releases (schedule.yml, auto-merge.yml)
  pull-requests: write    # Open and update PRs (schedule.yml, auto-merge.yml)
  pages: write            # Deploy to GitHub Pages (deploy.yml)
  id-token: write         # OIDC token for Pages deploy (deploy.yml)
  security-events: write  # Upload SARIF results (codeql.yml)
```

### Workflow Security Matrix

| Workflow | Trigger | Permissions | Risk |
|----------|---------|-------------|------|
| `ci.yml` | push, PR | contents: read | LOW |
| `codeql.yml` | push, PR, schedule | contents: read, security-events: write | LOW |
| `hygiene.yml` | schedule, manual | contents: read | LOW |
| `link-check.yml` | schedule, manual | contents: read | LOW |
| `deploy.yml` | push to main | contents: read, pages: write, id-token: write | LOW |
| `schedule.yml` | schedule (daily), manual | contents: write, pull-requests: write | MEDIUM |
| `auto-merge.yml` | PR | contents: write, pull-requests: write | MEDIUM |

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
|  - Use branch-based action refs (@main/@master)   |
|  - Run untrusted code in sandbox                  |
+---------------------------------------------------+
```

#### 2. Action Version Policy

```yaml
# Current policy: branch-based refs self-update from upstream
- uses: actions/checkout@main
- uses: actions/setup-python@main

# Floating major tags where the upstream has no branch ref
- uses: lycheeverse/lychee-action@master
```

With `sha_pinning_required=false` these refs pass workflow validation;
branch refs always resolve to the current upstream default-branch commit.

#### 3. Secrets Management

```
+---------------------------------------------------+
|  SECRETS IN GITHUB ACTIONS                        |
+---------------------------------------------------+
|                                                   |
|  Required Secrets:                                |
|  - AUTO_MERGE_TOKEN        (schedule.yml)          |
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
        uses: actions/checkout@main

      - name: Setup Python
        uses: actions/setup-python@main
        with:
          python-version: "3.x"

      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install -e ".[dev]"

      - name: Lint
        run: ruff check Scripts/ Tests/

      - name: Type check
        run: mypy Scripts/

      - name: Test
        run: pytest Tests/ --cov=Scripts --cov-report=xml

      - name: Upload coverage
        uses: codecov/codecov-action@main
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
chmod 755 Output/                      # Output directory
chmod 644 Output/*                     # Output files

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
|  - To siberguvenlik.gov.tr only                  |
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

# UNSAFE: Logging raw IoC data
logger.debug(f"IoC data: {record}")  # NEVER DO THIS

# UNSAFE: Logging with f-string interpolation
logger.info(f"Processing {len(records)} records from {url}")  # Prefer structured
```

### Input Validation Security

```python
# All input validation happens through Pydantic
from pydantic import BaseModel, Field, field_validator


class IoCRecord(BaseModel):
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

- [ ] Unpinned editable manifests (always-latest policy)
- [ ] No known vulnerabilities in dependencies (`pip-audit`)
- [ ] Actions use branch refs (@main/@master), sha_pinning_required=false
- [ ] Workflow permissions set to minimum required
- [ ] Secrets stored in GitHub Secrets (not in code)
- [ ] Branch protection enabled on main branch
- [ ] PR reviews required before merge
- [ ] Type checking passes (`mypy --strict`)
- [ ] Linting passes (`ruff check`)
- [ ] All tests pass (`pytest`)
- [ ] Security scan passes (CodeQL/bandit/pip-audit)

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
4. **Always-latest dependencies** — unpinned editors + regenerated lock snapshots

### Priority 2: High

5. **GitHub Actions hardening** — branch refs + minimal permissions
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
| httpx | latest | Eşzamansız HTTP istemcisi | DÜŞÜK |
| pydantic | latest | Veri doğrulama | DÜŞÜK |


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
  | Sürüm Politikası    |     | DÜŞÜK  (pin'siz, en güncel çözülür)         |
  +------------------+     +------------------------------------------+
  | Güncelleme Sıklığı |   | DÜŞÜK  (deps-update ile otomatik)      |
  +------------------+     +------------------------------------------+
  | Saldırı Yüzeyi    |    | DÜŞÜK  (minimal bağımlılık kümesi)     |
  +------------------+     +------------------------------------------+
```

### Azaltma: Her Daim Güncel Bağımlılıklar

Düzenlenebilir bildirimler (`requirements.in`, `requirements-dev.in`) ve
`pyproject.toml` pin'sizdir; en güncel uyumlu sürümler kurulum anında çözülür.
Derlenmiş anlık görüntüler (`requirements.txt`, `requirements-dev.txt`) haftalık
olarak `deps-update.yml` ile yenilenir, böylece sessizce çürümez.

```toml
# pyproject.toml - her daim en güncel politikası (sürüm pin'i yok)
[project]
dependencies = [
    "httpx",
    "pydantic",
    "python-dotenv",
    "pyyaml",
]
```

### Azaltma: Yenilenen Kilit Anlık Görüntüleri

```bash
# Derlenmiş anlık görüntüleri en güncel sürüme yenile (haftalık otomasyon)
python Scripts/sync_deps.py --upgrade --compile-only

# En güncel sürümleri yerel ortama kur
pip install -e ".[dev]"
```

### Azaltma: Bağımlılık Taraması

```yaml
# .github/workflows/ci.yml + .gitlab-ci.yml (security işi)
- name: pip-audit
  run: pip-audit

- name: Bandit güvenlik denetimi
  run: bandit -r Scripts/
```

---

## GitHub Actions Güvenliği

### İş Akışı İzinleri

```yaml
# Önerilen minimum izinler
permissions:
  contents: read          # Depoyu oku
  contents: write         # Dal it / sürüm oluştur (schedule.yml, auto-merge.yml)
  pull-requests: write    # PR aç ve güncelle (schedule.yml, auto-merge.yml)
  pages: write            # GitHub Pages'e dağıt (deploy.yml)
  id-token: write         # Pages dağıtımı için OIDC jetonu (deploy.yml)
  security-events: write  # SARIF sonuçlarını yükle (codeql.yml)
```

### İş Akışı Güvenlik Matrisi

| İş Akışı | Tetikleyici | İzinler | Risk |
|----------|-------------|---------|------|
| `ci.yml` | push, PR | contents: read | DÜŞÜK |
| `codeql.yml` | push, PR, zamanlama | contents: read, security-events: write | DÜŞÜK |
| `hygiene.yml` | zamanlama, manuel | contents: read | DÜŞÜK |
| `link-check.yml` | zamanlama, manuel | contents: read | DÜŞÜK |
| `deploy.yml` | main'e push | contents: read, pages: write, id-token: write | DÜŞÜK |
| `schedule.yml` | zamanlama (günlük), manuel | contents: write, pull-requests: write | ORTA |
| `auto-merge.yml` | PR | contents: write, pull-requests: write | ORTA |

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
|  - Dal tabanlı eylem ref'leri (@main/@master)     |
|  - Güvenilmez kodu sandıkta çalıştırma            |
+---------------------------------------------------+
```

#### 2. Eylem Sürümü Politikası

```yaml
# Mevcut politika: dal tabanlı ref'ler yukarı akıştan kendiliğinden güncellenir
- uses: actions/checkout@main
- uses: actions/setup-python@main

# Yukarı akışta dal ref'i yoksa kayan büyük sürüm etiketi
- uses: lycheeverse/lychee-action@master
```

`sha_pinning_required=false` ile bu ref'ler iş akışı doğrulamasından geçer;
dal ref'leri her zaman yukarı akışın güncel varsayılan dal commit'ini çözer.

#### 3. Gizli Anahtar Yönetimi

```
+---------------------------------------------------+
|  GITHUB ACTIONS'TA GİZLİ ANAHTARLAR              |
+---------------------------------------------------+
|                                                   |
|  Gerekli Gizli Anahtarlar:                        |
|  - AUTO_MERGE_TOKEN        (schedule.yml)          |
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
        uses: actions/checkout@main

      - name: Setup Python
        uses: actions/setup-python@main
        with:
          python-version: "3.x"

      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install -e ".[dev]"

      - name: Lint
        run: ruff check Scripts/ Tests/

      - name: Type check
        run: mypy Scripts/

      - name: Test
        run: pytest Tests/ --cov=Scripts --cov-report=xml

      - name: Upload coverage
        uses: codecov/codecov-action@main
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
chmod 755 Output/                      # Çıktı dizini
chmod 644 Output/*                     # Çıktı dosyaları

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
|  - Yalnızca siberguvenlik.gov.tr adresine         |
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

# GÜVENLİSİZ: Ham IoC verisini kaydetme
logger.debug(f"IoC data: {record}")  # BUNU ASLA YAPMAYIN

# GÜVENLİSİZ: f-string ile kayıt
logger.info(f"Processing {len(records)} records from {url}")  # Yapılandırılmış tercih edin
```

### Giriş Doğrulama Güvenliği

```python
# Tüm giriş doğrulaması Pydantic aracılığıyla yapılır
from pydantic import BaseModel, Field, field_validator


class IoCRecord(BaseModel):
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

- [ ] Pin'siz düzenlenebilir bildirimler (her daim en güncel politikası)
- [ ] Bağımlılıklarda bilinen zafiyet yok (`pip-audit`)
- [ ] Eylemler dal ref'leri kullanıyor (@main/@master), sha_pinning_required=false
- [ ] İş akışı izinleri gerekli asgari düzeye ayarlanmış
- [ ] Gizli anahtarlar GitHub Secrets'ta saklanıyor (kodda değil)
- [ ] Ana dalda dal koruması etkinleştirilmiş
- [ ] Birleştirmeden önce PR incelemeleri gerekli
- [ ] Tür kontrolü geçiyor (`mypy --strict`)
- [ ] Kod denetleme geçiyor (`ruff check`)
- [ ] Tüm testler geçiyor (`pytest`)
- [ ] Güvenlik taraması geçiyor (CodeQL/bandit/pip-audit)

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
4. **Her daim en güncel bağımlılıklar** — pin'siz düzenleyiciler + yenilenen kilit anlık görüntüleri

### Öncelik 2: Yüksek

5. **GitHub Actions güçlendirme** — dal ref'leri + minimum izinler
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
