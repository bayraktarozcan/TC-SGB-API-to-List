> **Language / Dil** &nbsp;
> [EN English](#-english) &nbsp;·&nbsp; [TR Türkçe](#-türkçe)

<a id="-english"></a>

# Troubleshooting

Solutions for failures observed while installing, running, and developing this project. Each entry states the symptom, the verified cause, and the fix.

## PyYAML fails to build on Windows (Python 3.15, no MSVC)

`pip install` stops with `error: Microsoft Visual C++ 14.0 or greater is required` while building `pyyaml`.

Cause: PyYAML publishes no prebuilt wheel for CPython 3.15 on Windows, so pip falls back to compiling C sources, which needs MSVC Build Tools.

Fix, pick one:

- Use Python 3.11–3.14 (prebuilt wheels exist through cp314).
- Install Microsoft C++ Build Tools, then reinstall.
- Install the pure-Python build: `PYYAML_FORCE_LIBYAML=0 pip install --no-build-isolation pyyaml==6.0.3` from the sdist. Parsing works identically; only large YAML dumps run slower.

## PyCharm console fails with "did not find executable"

The Python console exits with code 103 and reports the base interpreter path as missing.

Cause: the project `.venv` was created from a Python installation that was later deleted; the venv cannot resolve its base executable anymore.

Fix: delete `.venv` and recreate it from the installed Python (`python -m venv .venv`), then reinstall with `pip install -e ".[dev]"` and `pip install -r requirements.txt`. The PyCharm project SDK path (`.venv\Scripts\python.exe`) stays the same, so no IDE reconfiguration is needed.

## `tc-sgb generate` reports "Input file not found"

Cause: the `--input` path does not exist.

Fix: run `tc-sgb fetch` first to produce `Output/raw_records.json`, or pass the correct `-i` path.

## API requests time out or fail

Cause: slow network, rate limiting, or API downtime.

Fix: run `tc-sgb health` to check connectivity, then retry with explicit `--timeout`, `--retries`, or a lower `--rps` value.

## Quality gate failures

Cause: usually a lint, format, type, or test regression in changed files.

Fix: run the gate step that failed (`ruff check`, `ruff format --check`, `mypy`, `bandit`, `pytest`) on `Scripts/` and `Tests/`, fix the reported lines, and re-run the full gate before committing.

## Stale local data

Cause: `Output/` holds artifacts from an older fetch.

Fix: re-run `tc-sgb fetch`, or download a fresh `raw_records.json` from the rolling `ioc-data` release and regenerate with `tc-sgb generate`.

---

<a id="-türkçe"></a>

# Sorun Giderme

Bu projeyi kurarken, çalıştırırken ve geliştirirken gözlenen arızaların çözümleri. Her girdi belirtiyi, doğrulanmış nedeni ve düzeltmeyi belirtir.

## Windows'ta PyYAML derlenemiyor (Python 3.15, MSVC yok)

`pip install`, C kaynaklarını derlerken `error: Microsoft Visual C++ 14.0 or greater is required` hatasıyla durur.

Neden: PyYAML'in Windows'ta CPython 3.15 için önceden derlenmiş wheel'i yoktur; pip C kaynaklarına düşer ve MSVC ister.

Düzeltme, birini seçin:

- Python 3.11–3.14 kullanın (cp314'e kadar wheel mevcuttur).
- Microsoft C++ Build Tools kurup yeniden yükleyin.
- Saf-Python derlemeyi kurun: sdist üzerinden `PYYAML_FORCE_LIBYAML=0 pip install --no-build-isolation pyyaml==6.0.3`. Çözümleme aynı çalışır; yalnızca büyük YAML dökümleri yavaşlar.

## PyCharm konsolu "did not find executable" hatası veriyor

Python konsolu 103 koduyla çıkar ve taban yorumlayıcı yolunun eksik olduğunu bildirir.

Neden: proje `.venv`'i sonradan silinen bir Python kurulumundan üretilmiştir; venv taban çalıştırılabilir dosyayı artık çözemez.

Düzeltme: `.venv`'yi silip kurulu Python ile yeniden oluşturun (`python -m venv .venv`), sonra `pip install -e ".[dev]"` ve `pip install -r requirements.txt` ile kurun. PyCharm proje SDK yolu (`.venv\Scripts\python.exe`) aynı kalır; IDE'yi yeniden yapılandırmak gerekmez.

## `tc-sgb generate` "Input file not found" diyor

Neden: `--input` yolu yoktur.

Düzeltme: önce `tc-sgb fetch` çalıştırıp `Output/raw_records.json` üretin ya da doğru `-i` yolunu verin.

## API istekleri zaman aşımına uğruyor ya da başarısız oluyor

Neden: yavaş ağ, hız sınırlama ya da API kesintisi.

Düzeltme: bağlantıyı `tc-sgb health` ile denetleyin, sonra açık `--timeout`, `--retries` ya da daha düşük `--rps` değeriyle yeniden deneyin.

## Kalite kapısı arızaları

Neden: genelde değişen dosyalarda lint, biçim, tip ya da test gerilemesi.

Düzeltme: çöken kapı adımını (`ruff check`, `ruff format --check`, `mypy`, `bandit`, `pytest`) `Scripts/` ve `Tests/` üzerinde çalıştırın, bildirilen satırları düzeltin ve commit'ten önce tüm kapıyı yeniden koşturun.

## Bayat yerel veri

Neden: `Output/` eski çekişten kalma eserler tutar.

Düzeltme: `tc-sgb fetch`'i yeniden çalıştırın ya da yuvarlanan `ioc-data` sürümünden taze `raw_records.json` indirip `tc-sgb generate` ile üretin.
