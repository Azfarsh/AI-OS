#!/usr/bin/env python3
"""Pull Meta Ads metrics for a date range; writes JSON under client reports/."""

import argparse
import json
from datetime import datetime
from pathlib import Path

from facebook_business.adobjects.adaccount import AdAccount
from facebook_business.api import FacebookAdsApi

from _common import REPO_ROOT, fail, ok, require_env


def period_bounds(period: str) -> tuple[str, str]:
    """period format: YYYY-MM"""
    try:
        start = datetime.strptime(period + "-01", "%Y-%m-%d")
    except ValueError:
        fail(f"Invalid period {period}; use YYYY-MM")
    if start.month == 12:
        end = start.replace(year=start.year + 1, month=1, day=1)
    else:
        end = start.replace(month=start.month + 1, day=1)
    from datetime import timedelta

    last = end - timedelta(days=1)
    return start.strftime("%Y-%m-%d"), last.strftime("%Y-%m-%d")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--account-id", required=True)
    parser.add_argument("--period", required=True)
    parser.add_argument("--client-slug", required=True)
    args = parser.parse_args()

    env = require_env("META_ACCESS_TOKEN", "META_APP_ID", "META_APP_SECRET")
    since, until = period_bounds(args.period)

    FacebookAdsApi.init(env["META_APP_ID"], env["META_APP_SECRET"], env["META_ACCESS_TOKEN"])
    account = AdAccount(f"act_{args.account_id}")
    insights = account.get_insights(
        fields=[
            "spend",
            "impressions",
            "clicks",
            "ctr",
            "cpc",
            "actions",
            "purchase_roas",
        ],
        params={"time_range": {"since": since, "until": until}, "level": "account"},
    )
    rows = [dict(i) for i in insights]

    out_dir = REPO_ROOT / "clients" / args.client_slug / "reports"
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / f".tmp-meta-{args.period}.json"
    out_path.write_text(json.dumps({"platform": "meta", "period": args.period, "rows": rows}, indent=2), encoding="utf-8")
    ok(f"META_JSON_PATH={out_path}")


if __name__ == "__main__":
    main()
