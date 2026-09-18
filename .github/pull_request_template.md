[English](#-english) | [Türkçe](#-türkçe)

<a id="-english"></a>

## Summary

_Describe the change and what problem it solves._

- Closes #_ (if applicable)

---

## Type of Change

- [ ] New output format
- [ ] New IOC source integration
- [ ] Pipeline enhancement
- [ ] Bug fix
- [ ] Documentation (README, CHANGELOG, wiki/)
- [ ] Translation / i18n
- [ ] CI/CD or automation
- [ ] Security
- [ ] Chore / refactor

---

## Checklist

- [ ] Tests pass (`pytest tests/ -v`)
- [ ] Ruff linter passes (`ruff check scripts/ tests/`)
- [ ] mypy type checker passes (`mypy scripts/`)
- [ ] No hardcoded secrets or credentials
- [ ] CHANGELOG.md updated (if applicable)
- [ ] README.md updated (if applicable)

---

## Testing

_Steps to verify:_

```bash
pytest tests/ -v
tc-sgb fetch --max-records 100
```

<a id="-türkçe"></a>

## Özet

_Değişikliği ve çözdüğü sorunu açıklayın._

- Closes #_ (uygunsa)

---

## Değişiklik Türü

- [ ] Yeni çıktı biçimi
- [ ] Yeni IOC kaynağı entegrasyonu
- [ ] Hat iyileştirmesi
- [ ] Hata düzeltmesi
- [ ] Dokümantasyon (README, CHANGELOG, wiki/)
- [ ] Çeviri / i18n
- [ ] CI/CD veya otomasyon
- [ ] Güvenlik
- [ ] Alt yapı / yeniden düzenleme

---

## Kontrol Listesi

- [ ] Testler geçiyor (`pytest tests/ -v`)
- [ ] Ruff linter geçiyor (`ruff check scripts/ tests/`)
- [ ] mypy tip kontrolü geçiyor (`mypy scripts/`)
- [ ] Sabit kodlanmış gizli bilgi veya kimlik bilgisi yok
- [ ] CHANGELOG.md güncellendi (uygunsa)
- [ ] README.md güncellendi (uygunsa)

---

## Test Etme

_Doğrulama adımları:_

```bash
pytest tests/ -v
tc-sgb fetch --max-records 100
```