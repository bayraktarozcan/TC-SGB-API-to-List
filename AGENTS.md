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

- GitLab CI/CD is intentionally disabled (`jobs_enabled=false`); `.gitlab-ci.yml`
  stays defined but must NOT be re-enabled via pipeline runs — it does not run.
- GitHub Actions is the active CI; the `origin` remote pushes to both GitHub and
  GitLab, so a single `git push origin main` updates both.
- GitLab-native pipeline/coverage badges were removed; do not re-add them.
- `TC_SGB_LOG_LEVEL` and `TC_SGB_OUTPUT_DIR` are honored by the CLI; `.env`
  files are read via `load_dotenv`.