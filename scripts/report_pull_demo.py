#!/usr/bin/env python3
"""Copy demo fixture JSON into client reports/ as .tmp-* files for dry runs."""

from __future__ import annotations

import argparse
import shutil
from pathlib import Path

from _common import REPO_ROOT, fail, ok


def main() -> None:
    parser = argparse.ArgumentParser(description="Load demo metrics fixtures for report workflow")
    parser.add_argument("--client-slug", required=True)
    parser.add_argument("--period", required=True)
    args = parser.parse_args()

    client_fixtures = REPO_ROOT / "clients" / args.client_slug / "fixtures"
    fallback = REPO_ROOT / "clients" / "demo-corp" / "fixtures"

    def _copy_from(source: Path) -> list[str]:
        copied_paths: list[str] = []
        for platform in ("meta", "google"):
            src = source / f"{platform}-{args.period}.json"
            if not src.exists():
                continue
            dest = out_dir / f".tmp-{platform}-{args.period}.json"
            shutil.copy2(src, dest)
            copied_paths.append(str(dest))
        return copied_paths

    out_dir = REPO_ROOT / "clients" / args.client_slug / "reports"
    out_dir.mkdir(parents=True, exist_ok=True)

    copied: list[str] = []
    if client_fixtures.exists():
        copied = _copy_from(client_fixtures)

    if not copied and fallback.exists() and fallback != client_fixtures:
        copied = _copy_from(fallback)

    if not copied:
        if not client_fixtures.exists() and not fallback.exists():
            fail(f"No fixtures folder: {client_fixtures}")
        fail(f"No fixtures for period {args.period} in {client_fixtures} or {fallback}")

    ok(f"DEMO_JSON={','.join(copied)}")


if __name__ == "__main__":
    main()
