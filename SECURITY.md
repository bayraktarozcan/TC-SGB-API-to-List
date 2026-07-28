[English](#-english) | [Türkçe](#-türkçe)

<a id="-english"></a>

# Security Policy

## Supported Versions

| Version | Supported |
|---------|-----------|
| 0.2.x   | Yes       |
| 0.1.x   | No        |

## Reporting a Vulnerability

> **DO NOT** report security vulnerabilities through public GitHub issues.

### Preferred: Private Vulnerability Reporting

Use GitHub's built-in **Private vulnerability reporting** feature:
[Report a vulnerability →](https://github.com/bayraktarozcan/TC-SGB-API-to-List/security/advisories/new)

### Alternative

If the above is unavailable, open a **private** issue describing the vulnerability.

### What to Include

- Type of issue (e.g., injection, path traversal, etc.)
- Full paths of source file(s) related to the issue
- The location of the affected source code (tag/branch/commit or direct URL)
- Any special configuration required to reproduce the issue
- Step-by-step instructions to reproduce the issue
- Proof-of-concept or exploit code (if possible)
- Impact of the issue, including how an attacker might exploit it

### Response Timeline

| Phase | Timeframe |
|-------|-----------|
| Acknowledgment | Within 48 hours |
| Initial assessment | Within 1 week |
| Resolution | Depends on severity |
| Disclosure | Coordinated disclosure after fix is available |

## Security Best Practices

When using this tool:

- Never commit `.env` files or API keys
- Use environment variables for sensitive configuration
- Run the pipeline in isolated environments
- Validate all IOC data before applying to production systems
- Keep dependencies updated (`pip-audit`, `dependabot`)

## Dependency Security

- Automated dependency updates via [Dependabot](https://github.com/bayraktarozcan/TC-SGB-API-to-List/blob/main/.github/dependabot.yml)
- Regular security audits with `pip-audit`
- Secret scanning with push protection enabled
- Dependabot security updates and automated fixes enabled

## Security Features

| Feature | Status |
|---------|--------|
| Secret scanning | Enabled |
| Push protection | Enabled |
| Validity checks | Requires Advanced Security |
| Dependabot alerts | Enabled |
| Dependabot security updates | Enabled |
| Dependabot automated fixes | Enabled |
| Branch protection | Enabled |
| CODEOWNERS | Enforced |

---

<a id="-türkçe"></a>

# Güvenlik Politikası

## Desteklenen Sürüm

| Sürüm | Destekleniyor |
|-------|---------------|
| 0.2.x | Evet       |
| 0.1.x | Hayır      |

## Güvenlik Açığı Bildirme

> **Güvenlik açıklarını** herkese açık GitHub sorunları üzerinden **bildirmeyin**.

### Tercih Edilen: Özel Güvenlik Açığı Bildirimi

GitHub'un yerleşik **Özel güvenlik açığı bildirimi** özelliğini kullanın:
[Bir güvenlik açığı bildirin →](https://github.com/bayraktarozcan/TC-SGB-API-to-List/security/advisories/new)

### Alternatif

Yukarıdaki seçenek kullanılamıyorsa, sorunu özel bir sorun olarak açıklayın.

### Neler Dahil Edilmeli

- Sorunun türü (ör. enjeksiyon, yol gezintisi, vb.)
- Sorunla ilgili kaynak dosya(lar)ın tam yolları
- Etkilenen kaynak kodunun konumu (etiket/dal/commit veya doğrudan URL)
- Sorunu yeniden üretmek için gereken özel yapılandırma
- Sorunu yeniden üretme adımları
- Kanıt kodu veya exploit kodu (mümkünse)
- Saldırganın sorunu nasıl istismar edebileceğini de içeren etki

### Yanıt Zaman Çizelgesi

| Aşama | Süre |
|-------|------|
| Bildirim | 48 saat içinde |
| İlk değerlendirme | 1 hafta içinde |
| Çözüm | Önceliğe bağlı |
| Açıklama | Düzeltme mevcut olduktan sonra koordineli açıklama |

## Güvenlik En İyi Uygulamaları

Bu aracı kullanırken:

- `.env` dosyalarını veya API anahtarlarını asla commit etmeyin
- Hassas yapılandırma için ortam değişkenlerini kullanın
- Hattı izole ortamlarda çalıştırın
- Tüm IOC verilerini üretim sistemlerine uygulamadan önce doğrulayın
- Bağımlılıkları güncel tutun (`pip-audit`, `dependabot`)

## Bağımlılık Güvenliği

- [Dependabot](https://github.com/bayraktarozcan/TC-SGB-API-to-List/blob/main/.github/dependabot.yml) aracılığıyla otomatik bağımlılık güncellemeleri
- `pip-audit` ile düzenli güvenlik denetimleri
- Push korumalı gizli tarama etkin
- Dependabot güvenlik güncellemeleri ve otomatik düzeltmeler etkin

## Güvenlik Özellikleri

| Özellik | Durum |
|---------|-------|
| Gizli tarama | Etkin |
| Push koruması | Etkin |
| Geçerlilik denetimi | İleri Güvenlik gerektirir |
| Dependabot uyarıları | Etkin |
| Dependabot güvenlik güncellemeleri | Etkin |
| Dependabot otomatik düzeltmeleri | Etkin |
| Dal koruması | Etkin |
| CODEOWNERS | Zorunlu |
