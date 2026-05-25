#!/usr/bin/env python3
"""Pull Google Ads campaign metrics; writes JSON under client reports/."""

import argparse
import json
from datetime import datetime
from pathlib import Path

from google.ads.googleads.client import GoogleAdsClient

from _common import REPO_ROOT, fail, ok, require_env


def period_bounds(period: str) -> tuple[str, str]:
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
    parser.add_argument("--customer-id", required=True)
    parser.add_argument("--period", required=True)
    parser.add_argument("--client-slug", required=True)
    args = parser.parse_args()

    require_env(
        "GOOGLE_ADS_DEVELOPER_TOKEN",
        "GOOGLE_ADS_CLIENT_ID",
        "GOOGLE_ADS_CLIENT_SECRET",
        "GOOGLE_ADS_REFRESH_TOKEN",
    )
    since, until = period_bounds(args.period)
    customer_id = args.customer_id.replace("-", "")

    config_path = REPO_ROOT / "scripts" / ".google-ads.yaml"
    if not config_path.exists():
        fail("Missing scripts/.google-ads.yaml — see references/google-ads-api.md")

    client = GoogleAdsClient.load_from_storage(str(config_path))
    ga_service = client.get_service("GoogleAdsService")
    query = f"""
        SELECT
          campaign.name,
          metrics.impressions,
          metrics.clicks,
          metrics.ctr,
          metrics.average_cpc,
          metrics.cost_micros,
          metrics.conversions,
          metrics.conversions_value
        FROM campaign
        WHERE segments.date BETWEEN '{since}' AND '{until}'
    """
    response = ga_service.search(customer_id=customer_id, query=query)
    rows = []
    for row in response:
        rows.append(
            {
                "campaign": row.campaign.name,
                "impressions": row.metrics.impressions,
                "clicks": row.metrics.clicks,
                "ctr": row.metrics.ctr,
                "average_cpc": row.metrics.average_cpc,
                "cost_micros": row.metrics.cost_micros,
                "conversions": row.metrics.conversions,
                "conversions_value": row.metrics.conversions_value,
            }
        )

    out_dir = REPO_ROOT / "clients" / args.client_slug / "reports"
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / f".tmp-google-{args.period}.json"
    out_path.write_text(json.dumps({"platform": "google", "period": args.period, "rows": rows}, indent=2), encoding="utf-8")
    ok(f"GOOGLE_JSON_PATH={out_path}")


if __name__ == "__main__":
    main()
