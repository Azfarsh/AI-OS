#!/usr/bin/env python3
"""Synthesize a performance report from platform JSON files."""

from __future__ import annotations

import argparse
import json
import os
import re
from datetime import date
from pathlib import Path

from _common import REPO_ROOT, fail, ok, slugify


def _num(value: object, default: float = 0.0) -> float:
    if value is None:
        return default
    if isinstance(value, (int, float)):
        return float(value)
    try:
        return float(str(value).replace(",", ""))
    except ValueError:
        return default


def _fmt_money(value: float) -> str:
    return f"${value:,.2f}"


def _fmt_int(value: float) -> str:
    return f"{int(round(value)):,}"


def _fmt_pct(value: float) -> str:
    return f"{value:.2f}%"


def _change(current: float, previous: float) -> str:
    if previous <= 0:
        return "—"
    delta = ((current - previous) / previous) * 100
    sign = "+" if delta >= 0 else ""
    return f"{sign}{delta:.1f}%"


def _parse_meta_row(row: dict) -> dict[str, float]:
    spend = _num(row.get("spend"))
    impressions = _num(row.get("impressions"))
    clicks = _num(row.get("clicks"))
    ctr = _num(row.get("ctr"))
    cpc = _num(row.get("cpc"))
    conversions = 0.0
    for action in row.get("actions") or []:
        if action.get("action_type") in ("lead", "purchase", "offsite_conversion.fb_pixel_lead"):
            conversions += _num(action.get("value"))
    roas_raw = row.get("purchase_roas")
    if isinstance(roas_raw, list) and roas_raw:
        roas = _num(roas_raw[0].get("value"))
    else:
        roas = _num(roas_raw)
    if ctr <= 1 and impressions > 0 and clicks > 0:
        ctr = (clicks / impressions) * 100
    if cpc <= 0 and clicks > 0:
        cpc = spend / clicks
    return {
        "spend": spend,
        "impressions": impressions,
        "clicks": clicks,
        "ctr": ctr,
        "cpc": cpc,
        "conversions": conversions,
        "roas": roas,
    }


def _parse_google_rows(rows: list[dict]) -> dict[str, float]:
    spend = sum(_num(r.get("cost_micros")) / 1_000_000 for r in rows)
    impressions = sum(_num(r.get("impressions")) for r in rows)
    clicks = sum(_num(r.get("clicks")) for r in rows)
    conversions = sum(_num(r.get("conversions")) for r in rows)
    conv_value = sum(_num(r.get("conversions_value")) for r in rows)
    ctr = (clicks / impressions * 100) if impressions else 0.0
    cpc = (spend / clicks) if clicks else 0.0
    roas = (conv_value / spend) if spend else 0.0
    return {
        "spend": spend,
        "impressions": impressions,
        "clicks": clicks,
        "ctr": ctr,
        "cpc": cpc,
        "conversions": conversions,
        "roas": roas,
    }


def _load_json(path: Path) -> dict | None:
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def _metric_table(label: str, current: dict[str, float], previous: dict[str, float] | None) -> str:
    prev = previous or {}
    lines = [
        f"### {label}",
        "",
        "| Metric | This Period | Last Period | Change |",
        "|--------|-------------|-------------|--------|",
        f"| Spend | {_fmt_money(current['spend'])} | {_fmt_money(prev.get('spend', 0)) if prev else '—'} | {_change(current['spend'], prev.get('spend', 0)) if prev else '—'} |",
        f"| Impressions | {_fmt_int(current['impressions'])} | {_fmt_int(prev.get('impressions', 0)) if prev else '—'} | {_change(current['impressions'], prev.get('impressions', 0)) if prev else '—'} |",
        f"| Clicks | {_fmt_int(current['clicks'])} | {_fmt_int(prev.get('clicks', 0)) if prev else '—'} | {_change(current['clicks'], prev.get('clicks', 0)) if prev else '—'} |",
        f"| CTR | {_fmt_pct(current['ctr'])} | {_fmt_pct(prev.get('ctr', 0)) if prev else '—'} | {_change(current['ctr'], prev.get('ctr', 0)) if prev else '—'} |",
        f"| CPC | {_fmt_money(current['cpc'])} | {_fmt_money(prev.get('cpc', 0)) if prev else '—'} | {_change(current['cpc'], prev.get('cpc', 0)) if prev else '—'} |",
        f"| Conversions | {_fmt_int(current['conversions'])} | {_fmt_int(prev.get('conversions', 0)) if prev else '—'} | {_change(current['conversions'], prev.get('conversions', 0)) if prev else '—'} |",
        (
            f"| ROAS | {current['roas']:.2f}x | {prev.get('roas', 0):.2f}x | {_change(current['roas'], prev.get('roas', 0))} |"
            if prev
            else f"| ROAS | {current['roas']:.2f}x | — | — |"
        ),
    ]
    return "\n".join(lines)


def _executive_summary(client: str, period: str, meta: dict | None, google: dict | None) -> str:
    parts: list[str] = []
    if meta:
        parts.append(f"Meta delivered {meta['roas']:.2f}x ROAS on {_fmt_money(meta['spend'])} spend")
    if google:
        parts.append(f"Google Ads returned {google['roas']:.2f}x ROAS on {_fmt_money(google['spend'])} spend")
    if not parts:
        return f"No platform data available for {client} in {period}."
    headline = " and ".join(parts) + "."
    win = "Lead volume and efficiency held steady across active channels."
    concern = "Prior-period comparison data was not available for this run."
    return f"{headline} {win} {concern}"


def _insights(meta: dict | None, google: dict | None) -> list[str]:
    insights: list[str] = []
    if meta:
        insights.append(
            f"Meta generated {_fmt_int(meta['conversions'])} conversions at {_fmt_money(meta['cpc'])} CPC "
            f"with {_fmt_pct(meta['ctr'])} CTR."
        )
    if google:
        insights.append(
            f"Google Ads consolidated {_fmt_int(google['clicks'])} clicks at {_fmt_money(google['cpc'])} CPC "
            f"across all campaigns."
        )
    if meta and google:
        total_spend = meta["spend"] + google["spend"]
        insights.append(
            f"Combined ad spend was {_fmt_money(total_spend)}; Meta accounted for "
            f"{(meta['spend'] / total_spend * 100):.0f}% of total."
        )
    return insights or ["Insufficient data to generate insights."]


def _recommendations(meta: dict | None, google: dict | None) -> list[str]:
    recs: list[str] = []
    if meta and meta["roas"] < 3:
        recs.append("Test new Meta creative angles to lift ROAS toward the 3× guarantee target.")
    if google and google["ctr"] < 2:
        recs.append("Refresh Google ad copy and tighten keyword match types to improve CTR.")
    if meta and meta["roas"] >= 3:
        recs.append("Scale top-performing Meta ad sets by 15–20% while holding CPA steady.")
    recs.append("Schedule a 30-minute review call to align on next-period budget allocation.")
    return recs[:3]


def _prior_period(period: str) -> str:
    year, month = map(int, period.split("-"))
    if month == 1:
        return f"{year - 1}-12"
    return f"{year}-{month - 1:02d}"


def _resolve_client_slug(client_name: str) -> str:
    registry = REPO_ROOT / "context" / "clients.md"
    if registry.exists():
        text = registry.read_text(encoding="utf-8")
        slug = slugify(client_name)
        if slug in text:
            return slug
        for line in text.splitlines():
            if client_name.lower() in line.lower():
                match = re.search(r"\|\s*[\d-]+\s*\|\s*[^|]+\s*\|\s*([a-z0-9-]+)\s*\|", line)
                if match:
                    return match.group(1)
    return slugify(client_name)


def synthesize(
    client_name: str,
    period: str,
    client_slug: str | None = None,
    reports_dir: Path | None = None,
) -> Path:
    slug = client_slug or _resolve_client_slug(client_name)
    reports = reports_dir or (REPO_ROOT / "clients" / slug / "reports")
    reports.mkdir(parents=True, exist_ok=True)

    meta_current = _load_json(reports / f".tmp-meta-{period}.json")
    google_current = _load_json(reports / f".tmp-google-{period}.json")
    if not meta_current and not google_current:
        fail(f"No platform JSON in {reports}. Run pull scripts or --demo first.")

    prior = _prior_period(period)
    meta_prev_data = _load_json(reports / f".tmp-meta-{prior}.json")
    google_prev_data = _load_json(reports / f".tmp-google-{prior}.json")

    meta_metrics = _parse_meta_row(meta_current["rows"][0]) if meta_current and meta_current.get("rows") else None
    google_metrics = (
        _parse_google_rows(google_current["rows"]) if google_current and google_current.get("rows") else None
    )
    meta_prev = _parse_meta_row(meta_prev_data["rows"][0]) if meta_prev_data and meta_prev_data.get("rows") else None
    google_prev = (
        _parse_google_rows(google_prev_data["rows"]) if google_prev_data and google_prev_data.get("rows") else None
    )

    body_parts = [
        f"# Performance Report — {client_name} — {period}",
        "",
        "## Executive Summary",
        "",
        _executive_summary(client_name, period, meta_metrics, google_metrics),
        "",
        "## Platform Breakdown",
        "",
    ]
    if meta_metrics:
        body_parts.append(_metric_table("Meta Ads", meta_metrics, meta_prev))
        body_parts.append("")
    if google_metrics:
        body_parts.append(_metric_table("Google Ads", google_metrics, google_prev))
        body_parts.append("")

    body_parts.extend(["## Key Insights", ""])
    for item in _insights(meta_metrics, google_metrics):
        body_parts.append(f"- {item}")
    body_parts.extend(["", "## Recommendations", ""])
    for item in _recommendations(meta_metrics, google_metrics):
        body_parts.append(f"- {item}")
    body_parts.extend(
        [
            "",
            "## Next Steps",
            "",
            "- Account manager: share report with client and confirm budget for next period (within 3 business days)",
            "- Creative team: brief new ad variants based on top performers (within 1 week)",
        ]
    )

    report_body = "\n".join(body_parts)
    wrapper_path = REPO_ROOT / "templates" / "report-template.md"
    agency = os.getenv("AGENCY_NAME", "Bombay Media")
    if wrapper_path.exists():
        wrapper = wrapper_path.read_text(encoding="utf-8")
        report = (
            wrapper.replace("{{CLIENT_NAME}}", client_name)
            .replace("{{PERIOD}}", period)
            .replace("{{AGENCY_NAME}}", agency)
            .replace("{{DATE}}", date.today().isoformat())
            .replace("{{REPORT_BODY}}", report_body)
        )
    else:
        report = report_body

    out_path = reports / f"report-{period}.md"
    out_path.write_text(report, encoding="utf-8")
    return out_path


def main() -> None:
    parser = argparse.ArgumentParser(description="Synthesize report from .tmp-*.json files")
    parser.add_argument("--client-name", required=True)
    parser.add_argument("--client-slug", default=None)
    parser.add_argument("--period", required=True)
    args = parser.parse_args()

    path = synthesize(args.client_name, args.period, args.client_slug)
    ok(f"REPORT_PATH={path}")


if __name__ == "__main__":
    main()
