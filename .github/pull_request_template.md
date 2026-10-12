[English](#-english) | [Türkçe](#-türkçe)

<a id="-english"></a>

## Summary

_Describe the change and what problem it solves._

- Closes #_ (if applicable)

---

## Type of Change

- [ ] New output format
- [ ] New IoC source integration
- [ ] Pipeline enhancement
- [ ] Bug fix
- [ ] Documentation (README, CHANGELOG, Docs/)
- [ ] Translation / i18n
- [ ] CI/CD or automation
- [ ] Security
- [ ] Chore / refactor

---

## Checklist

- [ ] Tests pass (`pytest Tests/ -v`)
- [ ] Ruff linter passes (`ruff check Scripts/ Tests/`)
- [ ] mypy type checker passes (`mypy Scripts/`)
- [ ] No hardcoded secrets or credentials
- [ ] CHANGELOG.md updated (if applicable)
- [ ] README.md updated (if applicable)

---

## Testing

_Steps to verify:_

```bash
pytest Tests/ -v
tc-sgb fetch --max-records 100
```

<a id="-türkçe"></a>

## Özet

_Değişikliği ve çözdüğü sorunu açıklayın._

- Closes #_ (uygunsa)

---

## Değişiklik Türü

- [ ] Yeni çıktı biçimi
- [ ] Yeni IoC kaynağı entegrasyonu
- [ ] Hat iyileştirmesi
- [ ] Hata düzeltmesi
- [ ] Dokümantasyon (README, CHANGELOG, Docs/)
- [ ] Çeviri / i18n
- [ ] CI/CD veya otomasyon
- [ ] Güvenlik
- [ ] Alt yapı / yeniden düzenleme

---

## Kontrol Listesi

- [ ] Testler geçiyor (`pytest Tests/ -v`)
- [ ] Ruff linter geçiyor (`ruff check Scripts/ Tests/`)
- [ ] mypy tip kontrolü geçiyor (`mypy Scripts/`)
- [ ] Sabit kodlanmış gizli bilgi veya kimlik bilgisi yok
- [ ] CHANGELOG.md güncellendi (uygunsa)
- [ ] README.md güncellendi (uygunsa)

---

## Test Etme

_Doğrulama adımları:_

```bash
pytest Tests/ -v
tc-sgb fetch --max-records 100
```