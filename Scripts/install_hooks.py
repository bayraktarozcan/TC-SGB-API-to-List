"""Install the tracked pre-push hook without clobbering an existing hook.

The hook is copied to the active hooks directory reported by Git. When a hook
already exists it is backed up beside itself with a timestamp before replace-
ment, and the backup path is printed so the change is reversible.
"""

from __future__ import annotations

import argparse
import shutil
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "Scripts" / "pre-push"


def hooks_directory() -> Path:
    configured = ""
    section = ""
    for raw in (ROOT / ".git" / "config").read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if line.startswith("["):
            section = line.strip("[]")
            continue
        if section != "core" or "=" not in line:
            continue
        key, value = (part.strip() for part in line.split("=", 1))
        if key == "hooksPath":
            configured = value.strip('"')
            break
    path = Path(configured) if configured else ROOT / ".git" / "hooks"
    return path if path.is_absolute() else ROOT / path


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--uninstall", action="store_true")
    args = parser.parse_args()
    target = hooks_directory() / "pre-push"
    target.parent.mkdir(parents=True, exist_ok=True)
    if args.uninstall:
        if target.exists():
            target.unlink()
            print(f"removed {target}")
        return
    if not SOURCE.is_file():
        raise SystemExit(f"missing tracked hook: {SOURCE}")
    if target.exists():
        stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
        backup = target.with_name(f"{target.name}.{stamp}.bak")
        shutil.copyfile(target, backup)
        print(f"backed up existing hook to {backup}")
    shutil.copyfile(SOURCE, target)
    target.chmod(0o755)
    print(f"installed {target}")


if __name__ == "__main__":
    main()
