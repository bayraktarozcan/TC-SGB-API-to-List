#!/usr/bin/env python3
"""CLI entry point for the TC-SGB threat-intelligence pipeline.

Usage:
    python scripts/main.py fetch [--max-records N] [--output DIR]
    python scripts/main.py generate [--input FILE] [--formats FMT,...] [--output DIR]
    python scripts/main.py stats [--max-records N]
    python scripts/main.py validate [--input FILE] [--max-records N]
    python scripts/main.py health
"""

from __future__ import annotations

import argparse
import asyncio
import json
import logging
import math
import sys
import time
from pathlib import Path

# Ensure the scripts package is importable.
_SCRIPTS_DIR = Path(__file__).resolve().parent
if str(_SCRIPTS_DIR.parent) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS_DIR.parent))

from scripts.src.client import AsyncAPIClient
from scripts.src.models import AddressRecord
from scripts.src.outputs import generate_all
from scripts.src.pipeline import Pipeline

# ---------------------------------------------------------------------------
# Logging setup
# ---------------------------------------------------------------------------

def _setup_logging(verbose: bool = False) -> None:
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format="%(asctime)s [%(levelname)-7s] %(name)s: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    # Quiet down noisy libraries.
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("httpcore").setLevel(logging.WARNING)


# ---------------------------------------------------------------------------
# Sub-commands
# ---------------------------------------------------------------------------

async def cmd_fetch(args: argparse.Namespace) -> None:
    """Fetch all IOCs from the SGB API and save raw data."""
    output_dir = Path(args.output)
    output_dir.mkdir(parents=True, exist_ok=True)

    client = AsyncAPIClient(
        rate_limit=args.rps,
        timeout=args.timeout,
        max_retries=args.retries,
    )

    pipeline = Pipeline(
        client=client,
        per_page=args.per_page,
        max_pages=math.ceil(args.max_records / args.per_page) if args.max_records else 0,
    )

    scored, stats = await pipeline.run()

    # Save raw records for offline use
    raw_path = output_dir / "raw_records.json"
    raw_data = [
        {
            "id": s.original_id,
            "value": s.value,
            "type": s.ioc_type.value if hasattr(s.ioc_type, "value") else str(s.ioc_type),
            "desc": s.desc.value if s.desc else None,
            "source": s.source.value if s.source else None,
            "date": s.date.isoformat() if s.date else None,
            "criticality_level": s.criticality_level,
            "connectiontype": s.connectiontype.value if s.connectiontype else None,
            "quality_score": s.quality_score,
            "false_positive_risk": s.false_positive_risk,
        }
        for s in scored
    ]
    raw_path.write_text(json.dumps(raw_data, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"\nSaved {len(raw_data)} records to {raw_path}")

    # Generate output files
    formats = args.formats.split(",") if hasattr(args, "formats") and args.formats else None
    results = generate_all(scored, str(output_dir), formats=formats)

    print("\n" + stats.summary())
    if results:
        print("\nOutput files:")
        for fmt, path in results.items():
            print(f"  {fmt:15s} -> {path}")


async def cmd_generate(args: argparse.Namespace) -> None:
    """Generate output files from previously fetched raw data."""
    input_path = Path(args.input)
    if not input_path.exists():
        print(f"Error: Input file not found: {input_path}", file=sys.stderr)
        sys.exit(1)

    # Load raw records.
    raw_data = json.loads(input_path.read_text(encoding="utf-8"))
    from datetime import datetime

    from scripts.src.models import ConnectionType, DescriptionCategory, IOCType, ScoredIOC, Source

    scored: list[ScoredIOC] = []
    for item in raw_data:
        try:
            ioc_type = IOCType(item["type"])
            desc = DescriptionCategory(item["desc"]) if item.get("desc") else None
            source = Source(item["source"]) if item.get("source") else None
            ct = ConnectionType(item["connectiontype"]) if item.get("connectiontype") else None
            date = datetime.fromisoformat(item["date"]) if item.get("date") else None

            scored.append(ScoredIOC(
                value=item["value"],
                ioc_type=ioc_type,
                desc=desc,
                source=source,
                date=date,
                criticality_level=item.get("criticality_level", 10),
                connectiontype=ct,
                original_id=item.get("id", 0),
                quality_score=item.get("quality_score", 0.0),
                false_positive_risk=item.get("false_positive_risk", "low"),
            ))
        except Exception as e:
            print(f"Warning: Skipping record: {e}", file=sys.stderr)
            continue

    print(f"Loaded {len(scored)} records from {input_path}")

    output_dir = Path(args.output)
    output_dir.mkdir(parents=True, exist_ok=True)

    formats = args.formats.split(",") if args.formats else None
    results = generate_all(scored, str(output_dir), formats=formats)

    print("\nGenerated files:")
    for fmt, path in results.items():
        print(f"  {fmt:15s} -> {path}")


async def cmd_stats(args: argparse.Namespace) -> None:
    """Fetch and display statistics without generating outputs."""
    client = AsyncAPIClient(
        rate_limit=args.rps,
        timeout=args.timeout,
        max_retries=args.retries,
    )

    # Fetch metadata
    meta = await client.fetch_metadata()

    print("\n=== API Metadata ===")
    print(f"\nDescription categories ({len(meta['descriptions'])}):")
    for rid, rec in meta["descriptions"].items():
        print(f"  {rid:3s}: {rec.en_title} ({rec.tr_title})")

    print(f"\nConnection types ({len(meta['connection_types'])}):")
    for rid, rec in meta["connection_types"].items():
        print(f"  {rid:2s}: {rec.en_title} ({rec.tr_title})")

    print(f"\nSources ({len(meta['sources'])}):")
    for rid, rec in meta["sources"].items():
        print(f"  {rid:2s}: {rec.en_title} ({rec.tr_title})")

    # Fetch address count
    data = await client._request("/api/address/index", {"page": 0, "per-page": 1})
    total = data.get("totalCount", 0)
    page_count = data.get("pageCount", 0)
    print(f"\nTotal IOCs: {total:,}")
    print(f"API pages (9999/page): {page_count:,}")


async def cmd_validate(args: argparse.Namespace) -> None:
    """Validate IOCs from raw data or fetch and validate only."""
    client = AsyncAPIClient(
        rate_limit=args.rps,
        timeout=args.timeout,
        max_retries=args.retries,
    )

    if args.input:
        input_path = Path(args.input)
        if not input_path.exists():
            print(f"Error: Input file not found: {input_path}", file=sys.stderr)
            sys.exit(1)
        raw_data = json.loads(input_path.read_text(encoding="utf-8"))
        records = [AddressRecord.model_validate(r) for r in raw_data]
    else:
        print("Fetching from API...")
        records = await client.fetch_addresses(
            per_page=args.per_page,
            max_pages=math.ceil(args.max_records / args.per_page) if args.max_records else 0,
        )

    print(f"Validating {len(records)} records...")

    from scripts.src.validator import validate_ioc
    valid_count = 0
    rejected: list[tuple[AddressRecord, list[str]]] = []
    type_counts: dict[str, int] = {}

    for record in records:
        result = validate_ioc(record)
        if result is None:
            rejected.append((record, ["empty or unparseable IOC value"]))
        elif result.validation_errors:
            rejected.append((record, result.validation_errors))
        else:
            valid_count += 1
            t = result.ioc_type.value
            type_counts[t] = type_counts.get(t, 0) + 1

    print(f"\nResults: {valid_count} valid, {len(rejected)} rejected")

    if rejected:
        print("\nRejected records (first 20):")
        for rec, errors in rejected[:20]:
            print(f"  ID={rec.id} URL={rec.url[:60]}")
            for err in errors:
                print(f"    -> {err}")

    # Show type distribution of valid records
    print("\nType distribution (valid):")
    for t, c in sorted(type_counts.items()):
        print(f"  {t:10s}: {c}")


async def cmd_health(args: argparse.Namespace) -> None:
    """Check API health and connectivity."""
    client = AsyncAPIClient(
        rate_limit=args.rps,
        timeout=args.timeout,
        max_retries=args.retries,
    )

    print("Checking API health...")
    is_healthy = await client.health_check()

    if is_healthy:
        print("[OK] API is healthy and reachable")
        print(f"  Base URL: {client.base_url}")
        print(f"  Stats: {client.stats}")
    else:
        print("[FAIL] API is not reachable")
        sys.exit(1)


# ---------------------------------------------------------------------------
# Argument parser
# ---------------------------------------------------------------------------

def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="tc-sgb-intel",
        description=(
            "TC-SGB Threat Intelligence Pipeline — "
            "Fetch, validate, and export IOCs from the "
            "Turkish Cyber Security Directorate API."
        ),
    )
    parser.add_argument("-v", "--verbose", action="store_true", help="Enable debug logging.")
    subparsers = parser.add_subparsers(dest="command", help="Available commands.")

    # --- Shared arguments ---
    def add_common_args(p: argparse.ArgumentParser) -> None:
        p.add_argument(
            "--output", "-o", default="output",
            help="Output directory (default: output).",
        )
        p.add_argument(
            "--per-page", type=int, default=9999,
            help="Records per API page (max 9999).",
        )
        p.add_argument(
            "--rps", type=float, default=5.0,
            help="Requests per second to the API.",
        )
        p.add_argument(
            "--timeout", type=float, default=60.0,
            help="HTTP request timeout in seconds.",
        )
        p.add_argument(
            "--retries", type=int, default=5,
            help="Max retries per request.",
        )
        p.add_argument(
            "--max-records", type=int, default=None,
            help="Limit number of records to fetch.",
        )

    # fetch
    p_fetch = subparsers.add_parser(
        "fetch", help="Fetch IOCs and generate all output formats."
    )
    add_common_args(p_fetch)
    p_fetch.add_argument(
        "--formats", default=None,
        help="Comma-separated format names (default: all).",
    )

    # generate
    p_gen = subparsers.add_parser(
        "generate", help="Generate outputs from previously saved raw data."
    )
    p_gen.add_argument(
        "--input", "-i", required=True,
        help="Path to raw JSON file from fetch.",
    )
    p_gen.add_argument(
        "--output", "-o", default="output", help="Output directory."
    )
    p_gen.add_argument(
        "--formats", default=None,
        help="Comma-separated format names (default: all).",
    )

    # stats
    p_stats = subparsers.add_parser("stats", help="Fetch and display API metadata and statistics.")
    add_common_args(p_stats)

    # validate
    p_val = subparsers.add_parser(
        "validate", help="Validate IOCs from file or API."
    )
    p_val.add_argument(
        "--input", "-i", default=None,
        help="Path to raw JSON file (omit to fetch from API).",
    )
    add_common_args(p_val)

    # health
    p_health = subparsers.add_parser("health", help="Check API health and connectivity.")
    p_health.add_argument("--rps", type=float, default=5.0, help="Requests per second.")
    p_health.add_argument("--timeout", type=float, default=60.0, help="HTTP timeout.")
    p_health.add_argument("--retries", type=int, default=3, help="Max retries.")

    return parser


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    _setup_logging(args.verbose)

    if args.command is None:
        parser.print_help()
        sys.exit(0)

    start = time.monotonic()
    cmd_map = {
        "fetch": cmd_fetch,
        "generate": cmd_generate,
        "stats": cmd_stats,
        "validate": cmd_validate,
        "health": cmd_health,
    }

    coro = cmd_map[args.command](args)
    asyncio.run(coro)

    elapsed = time.monotonic() - start
    print(f"\nCompleted in {elapsed:.1f}s")


if __name__ == "__main__":
    main()
