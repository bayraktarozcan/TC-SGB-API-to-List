[English](#-english) | [Türkçe](#-türkçe)

<a id="-english"></a>

# AGENTS.md

Guidance for AI coding agents working in this repository.

## Project overview

TC-SGB threat-intelligence pipeline: fetches IoCs from the
[T.C. Siber Güvenlik Başkanlığı](https://siberguvenlik.gov.tr) API, validates,
normalizes, scores, and deduplicates them, then exports to 16 formats.

- Python `>=3.11`, packages in `pyproject.toml`; runtime deps are `httpx`,
  `pydantic`, `python-dotenv`, `pyyaml`.
- Source lives in `scripts/src/`; the CLI entry point is `scripts/main.py`.
- Tests live in `tests/` (pytest, `asyncio_mode = auto`).

## Quality gate (always run before claiming work complete)

Use the project virtualenv at `.venv`:

```powershell
& .venv\Scripts\python.exe -m ruff check scripts/ tests/
& .venv\Scripts\python.exe -m ruff format --check scripts/ tests/
& .venv\Scripts\python.exe -m mypy scripts/
& .venv\Scripts\python.exe -m bandit -r scripts/
& .venv\Scripts\python.exe -m pytest --cov=scripts --cov-report=term-missing -q
```

Baseline at last check: 480+ tests passing, ~99% coverage, zero ruff/mypy/bandit
findings. Do not drop below it.

## Conventions

- Conventional Commits for commit messages (see `CONTRIBUTING.md`).
- No f-string logging: `logger.*` calls use lazy `%`-style args, enforced by
  ruff rule `G004`.
- Test falsy-capable constructor flags with `is not None`, never `or` (a falsy
  `rate_limit=0`, `timeout=0`, or `max_retries=0` is meaningful).
- International domain names are IDNA-encoded to punycode before validation and
  normalization; `xn--` TLDs are valid.
- Prefer Path APIs over `os.path`; keep line length ≤ 100; follow existing
  module structure (models → client → validator → normalizer → quality → dedup).
- Do not add comments unless asked.

## Repository facts

- GitLab CI/CD and GitHub Actions are both active. GitLab pipelines run on GitLab
  shared runners (project-level CI is enabled); the `origin` remote pushes to
  both GitHub and GitLab, so a single `git push origin main` updates both and
  triggers both pipelines.
- GitLab-native pipeline/coverage badges are configured at the project level and
  mirrored in the README; GitHub Actions hosts the scheduled IoC update pipeline.
- `TC_SGB_LOG_LEVEL` and `TC_SGB_OUTPUT_DIR` are honored by the CLI; `.env`
  files are read via `load_dotenv`.

<a id="-türkçe"></a>

# AGENTS.md (Türkçe)

Bu depoda çalışan yapay zekâ kodlama aracıları için rehber.

## Proje genel bakışı

TC-SGB tehdit istihbaratı hattı: [T.C. Siber Güvenlik Başkanlığı](https://siberguvenlik.gov.tr)
API'sinden IoC'leri (İhlal Göstergesi) çeker, doğrular, normalleştirir,
puanlar ve tekilleştirir; ardından 16 biçime dışa aktarır.

- Python `>=3.11`, paketler `pyproject.toml` içinde; çalışma bağımlılıkları
  `httpx`, `pydantic`, `python-dotenv`, `pyyaml`.
- Kaynak kod `scripts/src/` altındadır; CLI giriş noktası `scripts/main.py`.
- Testler `tests/` içindedir (pytest, `asyncio_mode = auto`).

## Kalite çıtası (iş tamamlandı denmeden önce her zaman çalıştırın)

Projenin `.venv` sanal ortamını kullanın:

```powershell
& .venv\Scripts\python.exe -m ruff check scripts/ tests/
& .venv\Scripts\python.exe -m ruff format --check scripts/ tests/
& .venv\Scripts\python.exe -m mypy scripts/
& .venv\Scripts\python.exe -m bandit -r scripts/
& .venv\Scripts\python.exe -m pytest --cov=scripts --cov-report=term-missing -q
```

Son kontrol itibarıyla taban: 480+ test geçiyor, ~%99 kapsam, sıfır
ruff/mypy/bandit bulgusu. Bu seviyenin altına düşülmez.

## Kurallar

- Commit mesajları için Conventional Commits (bkz. `CONTRIBUTING.md`).
- f-string ile loglama yok: `logger.*` çağrıları tembel `%`-stili argüman kullanır;
  ruff kuralı `G004` ile zorunlu kılınır.
- Falsy olabilen yapıcı (constructor) bayraklarını `or` ile değil, `is not None`
  ile test edin (`rate_limit=0`, `timeout=0` veya `max_retries=0` anlamlıdır).
- Uluslararası alan adları doğrulama ve normalleştirmeden önce IDNA ile punycode
  biçimine kodlanır; `xn--` TLD'leri geçerlidir.
- `os.path` yerine Path API'lerini tercih edin; satır uzunluğu ≤ 100 tutun;
  mevcut modül yapısını izleyin (models → client → validator → normalizer →
  quality → dedup).
- İstenmedikçe yorum eklemeyin.

## Depo gerçekleri

- GitLab CI/CD ve GitHub Actions'ın ikisi de aktiftir. GitLab pipeline'ları
  GitLab paylaşımlı runner'larında çalışır (proje seviyesi CI etkin); `origin`
  uzak kaynağı hem GitHub'a hem GitLab'a iter; bu yüzden tek bir
  `git push origin main` ikisini de günceller ve iki pipeline'ı da tetikler.
- GitLab yerel pipeline/coverage rozetleri proje seviyesinde yapılandırılmıştır ve
  README'ye yansıtılmıştır; GitHub Actions zamanlanmış IoC güncelleme
  pipeline'ına ev sahipliği yapar.
- CLI tarafında `TC_SGB_LOG_LEVEL` ve `TC_SGB_OUTPUT_DIR` desteklenir; `.env`
  dosyaları `load_dotenv` üzerinden okunur.