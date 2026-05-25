#!/usr/bin/env python3
"""Lightweight company enrichment stub — extend with real APIs as needed."""

import argparse
import json

import requests

from _common import fail, ok


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--company", required=True)
    parser.add_argument("--website", default="")
    args = parser.parse_args()

    hints = {"company": args.company, "website": args.website, "sources": []}
    if args.website:
        try:
            resp = requests.get(args.website, timeout=15, headers={"User-Agent": "AgencyOS/1.0"})
            if resp.ok:
                title = ""
                for line in resp.text.splitlines()[:80]:
                    if "<title>" in line.lower():
                        title = line.strip()
                        break
                hints["sources"].append({"type": "website", "title": title[:200]})
        except requests.RequestException as exc:
            fail(f"Website fetch failed: {exc}")

    ok(json.dumps(hints))


if __name__ == "__main__":
    main()
