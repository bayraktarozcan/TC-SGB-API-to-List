[English](#-english) | [Türkçe](#-türkçe)

<a id="-english"></a>

# Contributing

Thank you for considering contributing to TC-SGB-API-to-List!

## Development Setup

### Prerequisites

- Python 3.11+
- Git
- pip

### Setup

```bash
git clone https://github.com/bayraktarozcan/TC-SGB-API-to-List.git
cd TC-SGB-API-to-List
pip install -e .
pip install -r requirements.txt
```

## Code Style

- **Formatter/Linter**: Ruff (`ruff format`, `ruff check`)
- **Type Checker**: mypy (`mypy scripts/src/`)
- **Line Length**: 100 characters max
- **Quotes**: Double quotes
- **Indentation**: 4 spaces (Python), 2 spaces (YAML/JSON)
- **Imports**: Sorted with `isort` (via Ruff)

## Testing

```bash
# Run all tests
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=scripts/src --cov-report=term-missing

# Run specific test
pytest tests/test_validator.py -v
```

## Commit Convention

We follow [Conventional Commits](https://www.conventionalcommits.org/):

```
<type>(<scope>): <description>

[optional body]

[optional footer]
```

### Types

| Type | Description |
|------|-------------|
| `feat` | New feature |
| `fix` | Bug fix |
| `docs` | Documentation |
| `style` | Formatting (no code change) |
| `refactor` | Code refactoring |
| `test` | Adding/updating tests |
| `ci` | CI/CD changes |
| `chore` | Maintenance tasks |
| `perf` | Performance improvement |

### Examples

```
feat(outputs): add Suricata rule format output
fix(validator): handle IPv6-mapped IPv4 addresses
docs(readme): update Turkish translation
test(client): add retry logic unit tests
```

## Pull Request Process

1. **Fork** the repository
2. **Create a branch** from `main`
   ```bash
   git checkout -b feat/my-feature
   ```
3. **Make changes** and commit
4. **Run quality checks**
   ```bash
   ruff check scripts/ tests/
   mypy scripts/src/
   pytest tests/ -v
   ```
5. **Push** and open a PR

### PR Checklist

- [ ] Tests pass (`pytest tests/ -v`)
- [ ] Linter passes (`ruff check scripts/ tests/`)
- [ ] Type checker passes (`mypy scripts/src/`)
- [ ] No hardcoded secrets or credentials
- [ ] Documentation updated (if applicable)
- [ ] CHANGELOG.md updated (if applicable)

## Reporting Issues

- Use [GitHub Issues](https://github.com/bayraktarozcan/TC-SGB-API-to-List/issues)
- Include Python version, OS, and error output
- For security issues, see [SECURITY.md](SECURITY.md)

## Code of Conduct

This project follows the [Contributor Covenant](CODE_OF_CONDUCT.md).
Please read it before contributing.

---

<a id="-türkçe"></a>

# Katkıda Bulunma

TC-SGB-API-to-List projesine katkıda bulunmayı düşünmeniz bizleri memnun etmektedir.

## Geliştirme Ortamı

### Ön Gereksinimler

- Python 3.11+
- Git
- pip

### Kurulum

```bash
git clone https://github.com/bayraktarozcan/TC-SGB-API-to-List.git
cd TC-SGB-API-to-List
pip install -e .
pip install -r requirements.txt
```

## Kod Stili

- **Biçimlendirici/Linter**: Ruff (`ruff format`, `ruff check`)
- **Tip Kontrolcü**: mypy (`mypy scripts/src/`)
- **Satır Uzunluğu**: Maksimum 100 karakter
- **Tırnak İşaretleri**: Çift tırnak
- **Girinti**: 4 boşluk (Python), 2 boşluk (YAML/JSON)
- **İçe Aktarımlar**: `isort` ile sıralanır (Ruff üzerinden)

## Testler

```bash
# Tüm testleri çalıştır
pytest tests/ -v

# Kapsama ile çalıştır
pytest tests/ --cov=scripts/src --cov-report=term-missing

# Belirli testi çalıştır
pytest tests/test_validator.py -v
```

## Commit Sözleşmesi

[Conventional Commits](https://www.conventionalcommits.org/) standardını takip ediyoruz:

```
<tip>(<kapsam>): <açıklama>

[isteğe bağlı gövde]

[isteğe bağlı alt bilgi]
```

### Türler

| Tür | Açıklama |
|-----|----------|
| `feat` | Yeni özellik |
| `fix` | Hata düzeltmesi |
| `docs` | Dokümantasyon |
| `style` | Biçimlendirme (kod değişikliği yok) |
| `refactor` | Kod yeniden yapılandırma |
| `test` | Test ekleme/güncelleme |
| `ci` | CI/CD değişiklikleri |
| `chore` | Bakım görevleri |
| `perf` | Performans iyileştirmesi |

### Örnekler

```
feat(outputs): Suricata kural formatı çıktısı ekle
fix(validator): IPv6'ya eşlenmiş IPv4 adreslerini işle
docs(readme): Türkçe çeviriyi güncelle
test(client): yeniden deneme mantığı birim testleri ekle
```

## Pull Request Süreci

1. Depoyu **çatallayın**
2. `main`'den **dal oluşturun**
   ```bash
   git checkout -b feat/my-feature
   ```
3. **Değişiklikler yapın** ve commit edin
4. **Kalite kontrollerini çalıştırın**
   ```bash
   ruff check scripts/ tests/
   mypy scripts/src/
   pytest tests/ -v
   ```
5. **Push edin** ve PR açın

### PR Kontrol Listesi

- [ ] Testler çalışıyor mu (`pytest tests/ -v`)
- [ ] Linter geçiyor mu (`ruff check scripts/ tests/`)
- [ ] Tip kontrolcü geçiyor mu (`mypy scripts/src/`)
- [ ] Sabit kodlanmış gizli anahtar veya kimlik bilgisi yok
- [ ] Dokümantasyon güncellendi (gerekirse)
- [ ] CHANGELOG.md güncellendi (gerekirse)

## Sorun Bildirme

- [GitHub Issues](https://github.com/bayraktarozcan/TC-SGB-API-to-List/issues) kullanın
- Python sürümü, işletim sistemi ve hata çıktısını ekleyin
- Güvenlik sorunları için [SECURITY.md](SECURITY.md) dosyasına bakın

## Davranış Kuralları

Bu proje [Contributor Covenant](CODE_OF_CONDUCT.md)standardını takip eder.
Katkıda bulunmadan önce lütfen okuyun.
