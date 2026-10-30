#!/usr/bin/env python3
"""Sync dependencies using pip-tools.

Usage:
    python sync_deps.py           # Sync to locked versions
    python sync_deps.py --upgrade # Upgrade to latest within constraints
"""

import argparse
import subprocess  # nosec B404
import sys
from pathlib import Path

ROOT = Path(__file__).parent.parent


def run(cmd: list[str]) -> int:
    print(f"$ {' '.join(cmd)}")
    return subprocess.call(cmd, cwd=ROOT, shell=False)  # nosec S603


def main() -> int:
    parser = argparse.ArgumentParser(description="Sync dependencies with pip-tools")
    parser.add_argument(
        "--upgrade", action="store_true", help="Upgrade to latest within constraints"
    )
    parser.add_argument("--compile-only", action="store_true", help="Only compile, don't install")
    args = parser.parse_args()

    # Compile requirements
    compile_cmd = [
        sys.executable,
        "-m",
        "piptools",
        "compile",
        "--allow-unsafe",
        "--output-file=requirements.txt",
        "requirements.in",
    ]
    if args.upgrade:
        compile_cmd.append("--upgrade")

    if run(compile_cmd) != 0:
        return 1

    compile_dev_cmd = [
        sys.executable,
        "-m",
        "piptools",
        "compile",
        "--allow-unsafe",
        "--output-file=requirements-dev.txt",
        "requirements-dev.in",
    ]
    if args.upgrade:
        compile_dev_cmd.append("--upgrade")

    if run(compile_dev_cmd) != 0:
        return 1

    if args.compile_only:
        print("Compiled requirements.txt and requirements-dev.txt")
        return 0

    # Sync (install exact versions)
    sync_cmd = [
        sys.executable,
        "-m",
        "piptools",
        "sync",
        "requirements-dev.txt",
    ]
    return run(sync_cmd)


if __name__ == "__main__":
    sys.exit(main())
