# Security Policy / Güvenlik Politikası

## Supported Versions / Desteklenen Sürüm

| Version / Sürüm | Supported / Destekleniyor |
|-----------------|---------------------------|
| 1.0.x           | Yes / Evet                |
| < 1.0           | No / Hayır                |

## Reporting a Vulnerability / Güvenlik Açığı Bildirme

> **DO NOT** report security vulnerabilities through public GitHub issues.
>
> **Halka açık GitHub sorunları** üzerinden güvenlik açığı **bildirmeyin**.

### Preferred: Private Vulnerability Reporting

Use GitHub's built-in **Private vulnerability reporting** feature:
[Report a vulnerability →](https://github.com/bayraktarozcan/TC-SGB-API-to-List/security/advisories/new)

### Alternative: Email

If the above is unavailable, email: **[INSERT YOUR EMAIL HERE]**

### What to Include / Neler Dahil Etmeli

- Type of issue (e.g., buffer overflow, SQL injection, etc.)
- Full paths of source file(s) related to the manifestation of the issue
- The location of the affected source code (tag/branch/commit or direct URL)
- Any special configuration required to reproduce the issue
- Step-by-step instructions to reproduce the issue
- Proof-of-concept or exploit code (if possible)
- Impact of the issue, including how an attacker might exploit it

### Response Timeline / Yanıt Zaman Çizelgesi

- **Acknowledgment**: Within 48 hours
- **Initial assessment**: Within 1 week
- **Resolution timeline**: Depends on severity
- **Disclosure**: Coordinated disclosure after fix is available

## Security Best Practices / Güvenlik En İyi Uygulamaları

When using this tool:

- Never commit `.env` files or API keys
- Use environment variables for sensitive configuration
- Run the pipeline in isolated environments
- Validate all IOC data before applying to production systems
- Keep dependencies updated (`pip-audit`, `dependabot`)

## Dependency Security / Bağımlılık Güvenliği

- Automated dependency updates via [Dependabot](.github/dependabot.yml)
- Regular security audits with `pip-audit`
- Secret scanning with push protection enabled
- Dependabot security updates and automated fixes enabled

## Security Features / Güvenlik Özellikleri

| Feature | Status |
|---|---|
| Secret scanning | Enabled |
| Push protection | Enabled |
| Validity checks | Requires Advanced Security |
| Dependabot alerts | Enabled |
| Dependabot security updates | Enabled |
| Dependabot automated fixes | Enabled |
| Branch protection | Enabled |
| CODEOWNERS | Enforced |
