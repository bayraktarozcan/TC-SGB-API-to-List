> **Language / Dil** &nbsp;
> [EN English](#-english) &nbsp;·&nbsp; [TR Türkçe](#-türkçe)

<a id="-english"></a>

# Maintenance Plan

## Overview

This document defines the ongoing maintenance procedures for the TC-SGB-API-to-List project, including regular tasks, monitoring, dependency management, and incident response.

## Maintenance Categories

```
+=====================================================================+
|  Maintenance Categories                                              |
+=====================================================================+

  +------------------+    +------------------+    +------------------+
  |                  |    |                  |    |                  |
  |   Routine        |    |   Preventive     |    |   Corrective     |
  |   Maintenance    |    |   Maintenance    |    |   Maintenance    |
  |                  |    |                  |    |                  |
  | - Daily runs     |    | - Dependency     |    | - Bug fixes      |
  | - Log review     |    |   updates        |    | - Security       |
  | - Output checks  |    | - Security       |    |   patches        |
  | - Performance    |    |   audits         |    | - Incident       |
  |   monitoring     |    | - Performance    |    |   response       |
  |                  |    |   tuning         |    |                  |
  +------------------+    +------------------+    +------------------+
          |                       |                       |
          v                       v                       v
  +------------------+    +------------------+    +------------------+
  | Frequency:       |    | Frequency:       |    | Frequency:       |
  | Daily/Weekly     |    | Monthly/Quarterly|    | As needed        |
  +------------------+    +------------------+    +------------------+
```

---

## Daily Tasks

### Automated (GitHub Actions)

```yaml
# Daily maintenance tasks (automated)
+=====================================================================+
|  Daily Automated Tasks                                               |
+=====================================================================+

  Task                      Schedule         Action
  +------------------------+----------------+------------------------+
  | Pipeline execution      | Daily 06:00 UTC| Fetch & process IOCs   |
  | Dependency check        | Daily 00:00 UTC| Dependabot scan        |
  | Test suite              | On every push  | CI pipeline            |
  | Output validation       | After pipeline | Quality checks         |
  +------------------------+----------------+------------------------+
```

### Manual (Operator)

| Task | Frequency | Duration | Procedure |
|------|-----------|----------|-----------|
| Review pipeline logs | Daily | 5 min | Check GitHub Actions logs |
| Verify output files | Daily | 2 min | Check output directory |
| Check disk space | Daily | 1 min | `df -h` |
| Review error alerts | Daily | 5 min | Check monitoring |

---

## Weekly Tasks

### Dependency Updates

```bash
# Check for dependency updates
pip list --outdated

# Update dependencies (one at a time)
pip install --upgrade httpx
pip install --upgrade pydantic

# Run tests after each update
pytest

# Commit updated requirements
pip freeze > requirements.lock
git add requirements.lock
git commit -m "chore: update dependencies"
```

### Performance Review

```bash
# Run performance benchmarks
pytest -m performance --benchmark-compare=0.001

# Check for regressions
pytest -m performance --benchmark-only --benchmark-max-time=10

# Review memory usage
python -m memory_profiler scripts/fetch_iocs.py
```

### Log Review

```bash
# Review recent pipeline runs
gh run list --limit 10

# Check for failed runs
gh run list --status failure --limit 5

# Download and review logs
gh run view <run-id> --log
```

---

## Monthly Tasks

### Security Audit

```bash
# Run security scan
pip-audit

# Check for vulnerable dependencies
safety check

# Review GitHub security advisories
gh api repos/{owner}/{repo}/security-advisories

# Update security policy if needed
cat SECURITY.md
```

### Performance Profiling

```bash
# Full performance profile
python -m cProfile -o profile.stats -m tc_sgb

# Analyze results
python -m pstats profile.stats

# Memory profile
python -m memory_profiler scripts/full_pipeline.py

# Generate performance report
pytest -m performance --benchmark-json=monthly-benchmark.json
```

### Documentation Review

| Document | Review Focus | Update If Needed |
|----------|--------------|------------------|
| README.md | Installation instructions, usage examples | Feature changes |
| CHANGELOG.md | Release notes completeness | Per release |
| wiki/ | API analysis, data models | API changes |
| SECURITY.md | Security policy, vulnerability reporting | Quarterly |
| CONTRIBUTING.md | Contribution guidelines | Process changes |

---

## Quarterly Tasks

### Major Dependency Updates

```bash
# Update all dependencies
pip install --upgrade pip
pip install --upgrade -r requirements.txt

# Update dev dependencies
pip install --upgrade pytest mypy ruff

# Full test suite
pytest

# Type check
mypy src/

# Lint
ruff check src/ tests/
```

### Security Hardening Review

```yaml
Security Checklist:
  - [ ] Review GitHub Actions workflows
  - [ ] Verify dependency pinning
  - [ ] Check for new CVEs in dependencies
  - [ ] Review access controls
  - [ ] Update security policy
  - [ ] Test incident response plan
  - [ ] Review logging for sensitive data
```

### Performance Optimization Review

```yaml
Performance Checklist:
  - [ ] Benchmark current performance
  - [ ] Compare with baseline
  - [ ] Identify bottlenecks
  - [ ] Profile hot paths
  - [ ] Optimize critical code
  - [ ] Update performance targets
```

---

## Annual Tasks

### Major Version Planning

```yaml
Annual Review:
  - [ ] Review all breaking changes needed
  - [ ] Plan deprecation timeline
  - [ ] Update Python version support
  - [ ] Review API compatibility
  - [ ] Plan new features
  - [ ] Update roadmap
```

### License Review

```yaml
License Checklist:
  - [ ] Review TC SGB terms of service
  - [ ] Check for license changes
  - [ ] Update Legal-Notices.md
  - [ ] Review dependency licenses
  - [ ] Update copyright notices
```

---

## Monitoring & Alerting

### Key Metrics

| Metric | Threshold | Alert |
|--------|-----------|-------|
| Pipeline success rate | < 95% | Email |
| Pipeline duration | > 20 min | Email |
| API error rate | > 5% | Email |
| Disk usage | > 80% | Email |
| Memory usage | > 80% | Email |
| Failed tests | > 0 | Email |
| Security vulnerabilities | > 0 | Email |

### Monitoring Setup

```python
# Simple monitoring script
import logging
from datetime import datetime

logger = logging.getLogger("tc_sgb.monitor")


def check_pipeline_health():
    """Check pipeline health and alert if issues detected."""
    checks = {
        "api_reachable": check_api_health(),
        "disk_space": check_disk_space(),
        "recent_success": check_recent_runs(),
        "output_freshness": check_output_age(),
    }

    failures = [k for k, v in checks.items() if not v]

    if failures:
        logger.critical(f"Health check failures: {failures}")
        send_alert(failures)
    else:
        logger.info("All health checks passed")
```

### Log Management

```
+=====================================================================+
|  Log Retention Policy                                                |
+=====================================================================+

  Log Type              Retention        Storage
  +--------------------+----------------+---------------------------+
  | Pipeline logs       | 30 days        | GitHub Actions            |
  | Error logs          | 90 days        | GitHub Actions            |
  | Performance logs    | 365 days       | Local + GitHub Artifacts  |
  | Security audit logs | 1 year         | Local                     |
  | Access logs         | 30 days        | GitHub Actions            |
  +--------------------+----------------+---------------------------+
```

---

## Incident Response

### Incident Severity Levels

| Level | Description | Response Time | Example |
|-------|-------------|---------------|---------|
| P1 | Critical | < 1 hour | API compromised, data breach |
| P2 | High | < 4 hours | Pipeline broken, security vuln |
| P3 | Medium | < 24 hours | Performance degradation |
| P4 | Low | < 1 week | Minor bug, documentation issue |

### Incident Response Steps

```
1. DETECT
   ├── Monitor alerts
   ├── User reports
   └── Automated checks

2. TRIAGE
   ├── Assess severity
   ├── Determine impact
   └── Assign responder

3. CONTAIN
   ├── Stop the bleeding
   ├── Isolate affected systems
   └── Preserve evidence

4. REMEDIATE
   ├── Fix the root cause
   ├── Deploy fix
   └── Verify resolution

5. REVIEW
   ├── Post-mortem
   ├── Update documentation
   └── Improve monitoring
```

### Incident Templates

```markdown
# Incident Report: [Title]

**Date**: YYYY-MM-DD
**Severity**: P1/P2/P3/P4
**Duration**: X hours Y minutes
**Impact**: [Description]

## Summary
[One paragraph summary]

## Timeline
- HH:MM - Issue detected
- HH:MM - Investigation started
- HH:MM - Root cause identified
- HH:MM - Fix deployed
- HH:MM - Verified resolved

## Root Cause
[Technical description]

## Resolution
[What was done]

## Lessons Learned
- [Lesson 1]
- [Lesson 2]

## Action Items
- [ ] [Action 1] - Owner - Due date
- [ ] [Action 2] - Owner - Due date
```

---

## Backup & Recovery

### Backup Strategy

| Data | Backup Method | Frequency | Retention |
|------|--------------|-----------|-----------|
| Source code | Git repository | Every commit | Indefinite |
| Configuration | Git repository | Every change | Indefinite |
| Output files | GitHub Artifacts | Daily | 30 days |
| Pipeline state | N/A (stateless) | N/A | N/A |
| Logs | GitHub Actions | Per run | 30 days |

### Recovery Procedures

```bash
# Recover from corrupted output
git checkout output/  # Restore from last known good

# Recover from broken release
pip install tc-sgb-api-list==1.0.0  # Install previous version

# Recover from failed pipeline
gh run rerun <failed-run-id>  # Re-run failed pipeline

# Full recovery from scratch
git clone https://github.com/owner/tc-sgb-api-list.git
cd tc-sgb-api-list
pip install -e .
pytest  # Verify everything works
python -m tc_sgb  # Run pipeline
```

---

## Communication

### Status Updates

| Event | Channel | Audience |
|-------|---------|----------|
| Scheduled maintenance | GitHub Issues | Users |
| Security patches | GitHub Security Advisories | Users |
| Breaking changes | GitHub Discussions + Issues | Users |
| New releases | GitHub Releases + PyPI | Users |
| Incidents | GitHub Issues | Users |

### Release Communication

```markdown
## Release Notification Template

### v1.1.0 Released

**Date**: 2025-01-20
**Type**: Feature release
**Breaking**: No

**Highlights**:
- New Sigma output format
- 30% faster deduplication
- Memory optimization

**Upgrade**:
pip install --upgrade tc-sgb-api-list

**Full notes**: https://github.com/owner/tc-sgb-api-list/releases/tag/v1.1.0
```

<a id="-türkçe"></a>

# Bakım Planı

## Genel Bakış

Bu belge, TC-SGB-API-to-List projesi için devam eden bakım prosedürlerini, düzenli görevleri, izleme, bağımlılık yönetimi ve olay müdahalesini tanımlar.

## Bakım Kategorileri

```
+=====================================================================+
|  Bakım Kategorileri                                                  |
+=====================================================================+

  +------------------+    +------------------+    +------------------+
  |                  |    |                  |    |                  |
  |   Rutin          |    |   Önleyici       |    |   Düzeltici      |
  |   Bakım          |    |   Bakım          |    |   Bakım          |
  |                  |    |                  |    |                  |
  | - Günlük         |    | - Bağımlılık     |    | - Hata           |
  |   çalıştırmalar  |    |   güncellemeleri |    |   düzeltmeleri   |
  | - Günlük         |    | - Güvenlik       |    | - Güvenlik       |
  |   incelemesi     |    |   denetimleri    |    |   yamaları       |
  | - Çıkış          |    | - Performans     |    | - Olay           |
  |   kontrolleri    |    |   ayarlaması     |    |   müdahalesi     |
  | - Performans     |    |                  |    |                  |
  |   izleme         |    |                  |    |                  |
  +------------------+    +------------------+    +------------------+
          |                       |                       |
          v                       v                       v
  +------------------+    +------------------+    +------------------+
  | Sıklık:          |    | Sıklık:          |    | Sıklık:          |
  | Günlük/Haftalık  |    | Aylık/Üç Aylık  |    | İhtiyaça göre     |
  +------------------+    +------------------+    +------------------+
```

---

## Günlük Görevler

### Otomatik (GitHub Actions)

```yaml
# Günlük bakım görevleri (otomatik)
+=====================================================================+
|  Günlük Otomatik Görevler                                            |
+=====================================================================+

  Görev                    Zamanlama          Eylem
  +------------------------+----------------+------------------------+
  | Hat çalıştırması       | Günlük 06:00 UTC| IOC'leri çek ve işle  |
  | Bağımlılık kontrolü    | Günlük 00:00 UTC| Dependabot taraması   |
  | Test paketi            | Her push'ta     | CI hattı               |
  | Çıkış doğrulama        | Hat sonrasında   | Kalite kontrolleri     |
  +------------------------+----------------+------------------------+
```

### Manuel (Operatör)

| Görev | Sıklık | Süreç | Prosedür |
|-------|--------|-------|----------|
| Hat günlüklerini inceleme | Günlük | 5 dk | GitHub Actions günlüklerini kontrol et |
| Çıkış dosyalarını doğrulama | Günlük | 2 dk | Çıkış dizinini kontrol et |
| Disk alanını kontrol etme | Günlük | 1 dk | `df -h` |
| Hata uyarılarını inceleme | Günlük | 5 dk | İzlemeyi kontrol et |

---

## Haftalık Görevler

### Bağımlılık Güncellemeleri

```bash
# Bağımlılık güncellemelerini kontrol et
pip list --outdated

# Bağımlılıkları güncelle (birer birer)
pip install --upgrade httpx
pip install --upgrade pydantic

# Her güncellemeden sonra testleri çalıştır
pytest

# Güncellenmiş gereksinimleri commit et
pip freeze > requirements.lock
git add requirements.lock
git commit -m "chore: update dependencies"
```

### Performans İncelemesi

```bash
# Performans kıyaslama testlerini çalıştır
pytest -m performance --benchmark-compare=0.001

# Gerilemeleri kontrol et
pytest -m performance --benchmark-only --benchmark-max-time=10

# Bellek kullanımını incele
python -m memory_profiler scripts/fetch_iocs.py
```

### Günlük İncelemesi

```bash
# Son hat çalıştırmalarını incele
gh run list --limit 10

# Başarısız çalıştırmaları kontrol et
gh run list --status failure --limit 5

# Günlükleri indir ve incele
gh run view <run-id> --log
```

---

## Aylık Görevler

### Güvenlik Denetimi

```bash
# Güvenlik taraması çalıştır
pip-audit

# Güvenlik açığı olan bağımlılıkları kontrol et
safety check

# GitHub güvenlik uyarılarını incele
gh api repos/{owner}/{repo}/security-advisories

# Gerekirse güvenlik politikasını güncelle
cat SECURITY.md
```

### Performans Profilleme

```bash
# Tam performans profili
python -m cProfile -o profile.stats -m tc_sgb

# Sonuçları analiz et
python -m pstats profile.stats

# Bellek profili
python -m memory_profiler scripts/full_pipeline.py

# Performans raporu oluştur
pytest -m performance --benchmark-json=monthly-benchmark.json
```

### Belgeleme İncelemesi

| Belge | İnceleme Odağı | Gerekirse Güncelle |
|-------|----------------|---------------------|
| README.md | Yükleme talimatları, kullanım örnekleri | Özellik değişiklikleri |
| CHANGELOG.md | Sürüm notlarının eksiksizliği | Her yayında |
| wiki/ | API analizi, veri modelleri | API değişiklikleri |
| SECURITY.md | Güvenlik politikası, güvenlik açığı bildirimi | Üç Aylık |
| CONTRIBUTING.md | Katkı yönergeleri | Süreç değişiklikleri |

---

## Üç Aylık Görevler

### Büyük Bağımlılık Güncellemeleri

```bash
# Tüm bağımlılıkları güncelle
pip install --upgrade pip
pip install --upgrade -r requirements.txt

# Geliştirme bağımlılıklarını güncelle
pip install --upgrade pytest mypy ruff

# Tam test paketi
pytest

# Tip kontrolü
mypy src/

# Lint
ruff check src/ tests/
```

### Güvenlik Sertleştirmesi İncelemesi

```yaml
Güvenlik Kontrol Listesi:
  - [ ] GitHub Actions iş akışlarını incele
  - [ ] Bağımlılık sabitlemelerini doğrula
  - [ ] Bağımlılıklardaki yeni CVE'leri kontrol et
  - [ ] Erişim kontrollerini incele
  - [ ] Güvenlik politikasını güncelle
  - [ ] Olay müdahale planını test et
  - [ ] Hassas veriler için günlükleme incelemesi
```

### Performans Optimizasyonu İncelemesi

```yaml
Performans Kontrol Listesi:
  - [ ] Mevcut performansı kıyasla
  - [ ] Taban çizgi ile karşılaştır
  - [ ] Darboğazları belirle
  - [ ] Sıcak yolları profille
  - [ ] Kritik kodu optimize et
  - [ ] Performans hedeflerini güncelle
```

---

## Yıllık Görevler

### Büyük Sürüm Planlaması

```yaml
Yıllık İnceleme:
  - [ ] Gerekli tüm kırıcı değişiklikleri gözden geçir
  - [ ] Kullanımdan kaldırma zaman çizelgesini planla
  - [ ] Python sürüm desteğini güncelle
  - [ ] API uyumluluğunu gözden geçir
  - [ ] Yeni özellikleri planla
  - [ ] Yol haritasını güncelle
```

### Lisans İncelemesi

```yaml
Lisans Kontrol Listesi:
  - [ ] TC SGB hizmet şartlarını incele
  - [ ] Lisans değişikliklerini kontrol et
  - [ ] Legal-Notices.md'yi güncelle
  - [ ] Bağımlılık lisanslarını incele
  - [ ] Telif hakkı uyarılarını güncelle
```

---

## İzleme ve Uyarılar

### Anahtar Metrikler

| Metrik | Eşik Değeri | Uyarı |
|--------|-------------|-------|
| Hat başarı oranı | < %95 | E-posta |
| Hat süresi | > 20 dk | E-posta |
| API hata oranı | > %5 | E-posta |
| Disk kullanımı | > %80 | E-posta |
| Bellek kullanımı | > %80 | E-posta |
| Başarısız testler | > 0 | E-posta |
| Güvenlik açıkları | > 0 | E-posta |

### İzleme Kurulumu

```python
# Basit izleme betiği
import logging
from datetime import datetime

logger = logging.getLogger("tc_sgb.monitor")


def check_pipeline_health():
    """Check pipeline health and alert if issues detected."""
    checks = {
        "api_reachable": check_api_health(),
        "disk_space": check_disk_space(),
        "recent_success": check_recent_runs(),
        "output_freshness": check_output_age(),
    }

    failures = [k for k, v in checks.items() if not v]

    if failures:
        logger.critical(f"Health check failures: {failures}")
        send_alert(failures)
    else:
        logger.info("All health checks passed")
```

### Günlük Yönetimi

```
+=====================================================================+
|  Günlük Saklama Politikası                                          |
+=====================================================================+

  Günlük Türü             Saklama Süresi    Depolama
  +--------------------+----------------+---------------------------+
  | Hat günlükleri     | 30 gün         | GitHub Actions            |
  | Hata günlükleri    | 90 gün         | GitHub Actions            |
  | Performans günlükleri| 365 gün      | Yerel + GitHub Artifactlar|
  | Güvenlik denetimi   | 1 yıl          | Yerel                     |
  | günlükleri          |                |                           |
  | Erişim günlükleri   | 30 gün         | GitHub Actions            |
  +--------------------+----------------+---------------------------+
```

---

## Olay Müdahalesi

### Olay Şiddet Seviyeleri

| Seviye | Açıklama | Yanıt Süresi | Örnek |
|--------|----------|--------------|-------|
| P1 | Kritik | < 1 saat | API ele geçirildi, veri ihlali |
| P2 | Yüksek | < 4 saat | Hat bozuldu, güvenlik açığı |
| P3 | Orta | < 24 saat | Performans düşüşü |
| P4 | Düşük | < 1 hafta | Küçük hata, belgeleme sorunu |

### Olay Müdahale Adımları

```
1. TESPİT
   ├── Uyarıları izleme
   ├── Kullanıcı raporları
   └── Otomatik kontroller

2. SINIFLANDIRMA
   ├── Şiddeti değerlendirme
   ├── Etkiyi belirleme
   └── Müdahaleci atama

3. KONTROL ALTINA ALMA
   ├── Kanamayı durdurma
   ├── Etkilenen sistemleri izole etme
   └── Kanıtları koruma

4. DÜZELTME
   ├── Kök nedeni düzeltme
   ├── Düzeltmeyi dağıtma
   └── Çözümü doğrulama

5. İNCELEME
   ├── Olay sonrası analiz
   ├── Belgelemeyi güncelleme
   └── İzlemeyi iyileştirme
```

### Olay Şablonları

```markdown
# Incident Report: [Title]

**Date**: YYYY-MM-DD
**Severity**: P1/P2/P3/P4
**Duration**: X hours Y minutes
**Impact**: [Description]

## Summary
[One paragraph summary]

## Timeline
- HH:MM - Issue detected
- HH:MM - Investigation started
- HH:MM - Root cause identified
- HH:MM - Fix deployed
- HH:MM - Verified resolved

## Root Cause
[Technical description]

## Resolution
[What was done]

## Lessons Learned
- [Lesson 1]
- [Lesson 2]

## Action Items
- [ ] [Action 1] - Owner - Due date
- [ ] [Action 2] - Owner - Due date
```

---

## Yedekleme ve Kurtarma

### Yedekleme Stratejisi

| Veri | Yedekleme Yöntemi | Sıklık | Saklama Süresi |
|------|-------------------|--------|-----------------|
| Kaynak kodu | Git deposu | Her commit | Süresiz |
| Yapılandırma | Git deposu | Her değişiklik | Süresiz |
| Çıkış dosyaları | GitHub Artifactları | Günlük | 30 gün |
| Hat durumu | Yok (durumsuz) | Yok | Yok |
| Günlükler | GitHub Actions | Her çalıştırmada | 30 gün |

### Kurtarma Prosedürleri

```bash
# Bozulmuş çıkıştan kurtarma
git checkout output/  # Bilinen son iyi durumdan geri yükle

# Bozulmuş yayından kurtarma
pip install tc-sgb-api-list==1.0.0  # Önceki sürümü yükle

# Başarısız hattan kurtarma
gh run rerun <failed-run-id>  # Başarısız hattı yeniden çalıştır

# Sıfırdan tam kurtarma
git clone https://github.com/owner/tc-sgb-api-list.git
cd tc-sgb-api-list
pip install -e .
pytest  # Her şeyin çalıştığını doğrula
python -m tc_sgb  # Hattı çalıştır
```

---

## İletişim

### Durum Güncellemeleri

| Olay | Kanal | Hedef Kitle |
|------|-------|-------------|
| Planlı bakım | GitHub Issues | Kullanıcılar |
| Güvenlik yamaları | GitHub Security Advisories | Kullanıcılar |
| Kırıcı değişiklikler | GitHub Discussions + Issues | Kullanıcılar |
| Yeni sürümler | GitHub Releases + PyPI | Kullanıcılar |
| Olaylar | GitHub Issues | Kullanıcılar |

### Yayın İletişimi

```markdown
## Release Notification Template

### v1.1.0 Released

**Date**: 2025-01-20
**Type**: Feature release
**Breaking**: No

**Highlights**:
- New Sigma output format
- 30% faster deduplication
- Memory optimization

**Upgrade**:
pip install --upgrade tc-sgb-api-list

**Full notes**: https://github.com/owner/tc-sgb-api-list/releases/tag/v1.1.0
```
