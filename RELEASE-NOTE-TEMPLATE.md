# Release Note Template

Copy the template below and fill in placeholders when creating new releases.

---

```markdown
## v{VERSION} — {TITLE}

**{ONE_LINE_SUMMARY}**

### Summary

{BRIEF_DESCRIPTION}

| Metric | Before | After |
|--------|--------|-------|
| Total IOCs fetched | {BEFORE} | **{AFTER}** ({DIFF}) |
| Validated IOCs | {V_BEFORE} | **{V_AFTER}** |
| Output formats | {F_BEFORE} | **{F_AFTER}** |

### Added

{FEATURE_NAME} — {DESCRIPTION}

### Changed

- {CHANGE_DESCRIPTION}

### Removed

{FEATURE_NAME} — {REASON}

### Files

- `scripts/main.py` — CLI entry point
- `scripts/src/*.py` — Core modules

### Documentation

- [Changelog](https://github.com/bayraktarozcan/TC-SGB-API-to-List/blob/main/CHANGELOG.md)
```

---

## Example: v1.1.0

```markdown
## v1.1.0 — New Output Formats & IPv6 Support

**Added Suricata and CrowdSec output formats with full IPv6 support.**

### Summary

Expands output format coverage to 16+ formats with proper IPv6 address-list
handling for nftables and MikroTik outputs.

| Metric | Before (v1.0.0) | After (v1.1.0) |
|--------|-----------------|----------------|
| Total IOCs fetched | 480,000 | 489,951 |
| Validated IOCs | 479,000 | 479,134 |
| Output formats | 14 | **16** (+2) |

### Added

- **Suricata rules** — IDS/IPS compatible output format
- **CrowdSec decisions** — Community threat intelligence format
- **IPv6 address-lists** — Separate nftables and MikroTik outputs

### Changed

- Script version → `v1.1.0`
- Documentation updated (README, CHANGELOG)

### Files

- `scripts/main.py` — CLI entry point
- `scripts/src/outputs.py` — Output format generators

### Documentation

- [Changelog](https://github.com/bayraktarozcan/TC-SGB-API-to-List/blob/main/CHANGELOG.md)
```
