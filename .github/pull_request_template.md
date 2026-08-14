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
