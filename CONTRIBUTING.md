# Contributing / Katkıda Bulunma

Thank you for considering contributing to TC-SGB-API-to-List!
Katkıda bulunmayı düşünmeniz teşekkür ederiz.

## Development Setup / Geliştirme Ortamı

### Prerequisites / Ön Gereksinimler

- Python 3.11+
- Git
- pip

### Setup / Kurulum

```bash
git clone https://github.com/bayraktarozcan/TC-SGB-API-to-List.git
cd TC-SGB-API-to-List
python -m venv .venv
.venv\Scripts\activate          # Windows
# source .venv/bin/activate     # macOS/Linux
pip install -r requirements.txt
```

## Code Style / Kod Stili

- **Formatter/Linter**: Ruff (`ruff format`, `ruff check`)
- **Type Checker**: mypy (`mypy scripts/src/`)
- **Line Length**: 100 characters max
- **Quotes**: Double quotes
- **Indentation**: 4 spaces (Python), 2 spaces (YAML/JSON)
- **Imports**: Sorted with `isort` (via Ruff)

## Testing / Testler

```bash
# Run all tests / Tüm testleri çalıştır
pytest tests/ -v

# Run with coverage / Kapsama ile çalıştır
pytest tests/ --cov=scripts/src --cov-report=term-missing

# Run specific test / Belirli testi çalıştır
pytest tests/test_validator.py -v
```

## Commit Convention / Sözleşme

We follow [Conventional Commits](https://www.conventionalcommits.org/):

```
<type>(<scope>): <description>

[optional body]

[optional footer]
```

### Types / Türler

| Type | Description |
|------|-------------|
| `feat` | New feature / Yeni özellik |
| `fix` | Bug fix / Hata düzeltmesi |
| `docs` | Documentation / Dokümantasyon |
| `style` | Formatting (no code change) |
| `refactor` | Code refactoring |
| `test` | Adding/updating tests |
| `ci` | CI/CD changes |
| `chore` | Maintenance tasks |
| `perf` | Performance improvement |

### Examples / Örnekler

```
feat(outputs): add Suricata rule format output
fix(validator): handle IPv6-mapped IPv4 addresses
docs(readme): update Turkish translation
test(client): add retry logic unit tests
```

## Pull Request Process / PR Süreci

1. **Fork** the repository / Depoyu çatallayın
2. **Create a branch** from `main` / `main`'den dal oluşturun
   ```bash
   git checkout -b feat/my-feature
   ```
3. **Make changes** and commit / Değişiklikler yapın ve commit edin
4. **Run quality checks** / Kalite kontrollerini çalıştırın
   ```bash
   ruff check scripts/ tests/
   mypy scripts/src/
   pytest tests/ -v
   ```
5. **Push** and open a PR / Push edin ve PR açın

### PR Checklist / PR Kontrol Listesi

- [ ] Tests pass (`pytest tests/ -v`)
- [ ] Linter passes (`ruff check scripts/ tests/`)
- [ ] Type checker passes (`mypy scripts/src/`)
- [ ] No hardcoded secrets or credentials
- [ ] Documentation updated (if applicable)
- [ ] CHANGELOG.md updated (if applicable)

## Reporting Issues / Sorun Bildirme

- Use [GitHub Issues](https://github.com/bayraktarozcan/TC-SGB-API-to-List/issues)
- Include Python version, OS, and error output
- For security issues, see [SECURITY.md](SECURITY.md)

## Code of Conduct / Davranış Kuralları

This project follows the [Contributor Covenant](CODE_OF_CONDUCT.md).
Please read it before contributing.
