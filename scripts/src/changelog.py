"""Persistent changelog for IoC fetch runs.

Compares the current deduplicated IoC list against the previous
``raw_records.json`` snapshot and writes a human-readable markdown
log to ``output/logs/fetch_<timestamp>.md``.

Usage from ``cmd_fetch``::

    from scripts.src.changelog import generate_changelog
    generate_changelog(output_dir=Path("output"), current_records=raw_data)
"""

from __future__ import annotations

import json
import logging
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


def generate_changelog(
    output_dir: Path,
    current_records: list[dict[str, Any]],
) -> Path | None:
    """Compare *current_records* against the previous snapshot and write a log.

    Parameters
    ----------
    output_dir:
        The ``output/`` directory where ``raw_records.json`` lives.
    current_records:
        The freshly-fetched list of IoC dicts (same structure as
        ``raw_records.json``).

    Returns
    -------
    The ``Path`` of the generated markdown file, or ``None`` if this
    is the very first run (no previous snapshot).
    """
    raw_path = output_dir / "raw_records.json"
    logs_dir = output_dir / "logs"
    logs_dir.mkdir(parents=True, exist_ok=True)

    # --- Load previous snapshot ------------------------------------------------
    previous = _load_previous(raw_path)
    if previous is None:
        logger.info("No previous snapshot found — skipping changelog generation.")
        _write_first_run_log(logs_dir, len(current_records))
        return None

    # --- Compute diff ----------------------------------------------------------
    prev_keys = {(r["type"], r["value"]) for r in previous}
    curr_keys = {(r["type"], r["value"]) for r in current_records}

    new_keys = curr_keys - prev_keys
    removed_keys = prev_keys - curr_keys

    new_records = [r for r in current_records if (r["type"], r["value"]) in new_keys]
    removed_records = [r for r in previous if (r["type"], r["value"]) in removed_keys]

    # --- Write markdown log ----------------------------------------------------
    now = datetime.now(UTC)
    ts_label = now.strftime("%Y-%m-%d %H:%M:%S UTC")
    file_label = now.strftime("%Y-%m-%d_%H%M%S")
    log_path = logs_dir / f"fetch_{file_label}.md"

    lines = _build_markdown(
        ts_label=ts_label,
        total_current=len(current_records),
        total_previous=len(previous),
        new_records=new_records,
        removed_records=removed_records,
    )
    log_path.write_text("\n".join(lines), encoding="utf-8")
    logger.info(
        "Changelog written: %s (+%d / -%d)",
        log_path,
        len(new_records),
        len(removed_records),
    )
    return log_path


# ---------------------------------------------------------------------------
# Internals
# ---------------------------------------------------------------------------


def _load_previous(raw_path: Path) -> list[dict[str, Any]] | None:
    """Return the list of IoC dicts from the previous snapshot, or ``None``."""
    if not raw_path.exists():
        return None
    try:
        data = json.loads(raw_path.read_text(encoding="utf-8"))
        if isinstance(data, list):
            return data
    except (json.JSONDecodeError, OSError) as exc:
        logger.warning("Could not read previous snapshot %s: %s", raw_path, exc)
    return None


def _write_first_run_log(logs_dir: Path, count: int) -> None:
    """Write a minimal log for the very first run (no diff possible)."""
    now = datetime.now(UTC)
    ts_label = now.strftime("%Y-%m-%d %H:%M:%S UTC")
    file_label = now.strftime("%Y-%m-%d_%H%M%S")
    log_path = logs_dir / f"fetch_{file_label}.md"
    lines = [
        f"# IoC Fetch Log — {ts_label}",
        "",
        "## Özet",
        "",
        f"- Toplam IoC: **{count:,}**",
        "- Yeni IoC: — (ilk çalışma, önceki veri yok)",  # noqa: RUF001
        "- Silinen IoC: —",
        "",
        "> Bu ilk çalıştırma olduğundan karşılaştırma yapılamadı.",  # noqa: RUF001
        "> Bir sonraki çalıştırmada yeni/silinen IoC'ler kaydedilecek.",  # noqa: RUF001
        "",
    ]
    log_path.write_text("\n".join(lines), encoding="utf-8")
    logger.info("First-run changelog written: %s", log_path)


def _build_markdown(
    *,
    ts_label: str,
    total_current: int,
    total_previous: int,
    new_records: list[dict[str, Any]],
    removed_records: list[dict[str, Any]],
) -> list[str]:
    """Return the full markdown content as a list of lines."""
    delta = total_current - total_previous
    delta_str = f"+{delta}" if delta >= 0 else str(delta)

    lines: list[str] = [
        f"# IoC Fetch Log — {ts_label}",
        "",
        "## Özet",
        "",
        f"- Toplam IoC (önceki): **{total_previous:,}**",
        f"- Toplam IoC (mevcut): **{total_current:,}**",
        f"- Net değişim: **{delta_str}**",
        f"- Yeni IoC: **{len(new_records):,}**",
        f"- Silinen IoC: **{len(removed_records):,}**",
        "",
    ]

    # --- New IoCs table --------------------------------------------------------
    lines.append("## Yeni IoC'ler")
    lines.append("")
    if new_records:
        lines.append(f"({len(new_records):,} yeni IoC)")
        lines.append("")
        lines.append("| # | Değer | Tip | Kaynak | Kritiklik | Güven Skoru | FP Riski |")
        lines.append("|---|-------|-----|--------|-----------|-------------|----------|")
        for i, r in enumerate(new_records, 1):
            value = r.get("value", "—")
            ioc_type = r.get("type", "—")
            source = r.get("source") or "—"
            crit = r.get("criticality_level") or "—"
            score = r.get("quality_score", "—")
            fp = r.get("false_positive_risk", "—")
            lines.append(f"| {i} | `{value}` | {ioc_type} | {source} | {crit} | {score} | {fp} |")
    else:
        lines.append("Yeni IoC yok.")
    lines.append("")

    # --- Removed IoCs table ----------------------------------------------------
    lines.append("## Silinen IoC'ler")
    lines.append("")
    if removed_records:
        lines.append(f"({len(removed_records):,} silinen IoC)")
        lines.append("")
        lines.append("| # | Değer | Tip | Kaynak | Kritiklik |")
        lines.append("|---|-------|-----|--------|-----------|")
        for i, r in enumerate(removed_records, 1):
            value = r.get("value", "—")
            ioc_type = r.get("type", "—")
            source = r.get("source") or "—"
            crit = r.get("criticality_level") or "—"
            lines.append(f"| {i} | `{value}` | {ioc_type} | {source} | {crit} |")
    else:
        lines.append("Silinen IoC yok.")
    lines.append("")

    return lines
