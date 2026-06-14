#!/usr/bin/env python3
"""
generate_report_pptx.py — Bombay Media Report PPTX Generator
Clones the branded report template and fills metrics from platform JSON.

Usage:
    python scripts/generate_report_pptx.py \
        --client-name "Demo Corp" \
        --client-slug demo-corp \
        --period 2025-01
"""

from __future__ import annotations

import argparse
import sys
from datetime import date
from pathlib import Path

try:
    from pptx import Presentation
except ImportError:
    print("ERROR: python-pptx not installed. Run: pip install python-pptx")
    sys.exit(1)

from _common import REPO_ROOT, fail, ok
from synthesize_report import (
    _executive_summary,
    _insights,
    _load_json,
    _parse_google_rows,
    _parse_meta_row,
    _prior_period,
    _recommendations,
)


TEMPLATE_PPTX = REPO_ROOT / "references" / "Bombay_Media_Dummy_Report.pptx"


def period_label(period: str) -> str:
    year, month = map(int, period.split("-"))
    return date(year, month, 1).strftime("%B %Y")


def replace_text_in_shape(shape, replacements: dict) -> None:
    if not shape.has_text_frame:
        return
    for para in shape.text_frame.paragraphs:
        for run in para.runs:
            for placeholder, value in replacements.items():
                if placeholder in run.text:
                    run.text = run.text.replace(placeholder, value)


def set_shape_text(shape, text: str) -> None:
    if not shape.has_text_frame:
        return
    tf = shape.text_frame
    para = tf.paragraphs[0]
    if para.runs:
        para.runs[0].text = text
        for run in para.runs[1:]:
            run.text = ""
    else:
        para.text = text


def set_cell_text(cell, text: str) -> None:
    if cell.text_frame.paragraphs and cell.text_frame.paragraphs[0].runs:
        cell.text_frame.paragraphs[0].runs[0].text = text
        for run in cell.text_frame.paragraphs[0].runs[1:]:
            run.text = ""
    else:
        cell.text = text


def _pct_change(current: float, previous: float) -> str:
    if previous <= 0:
        return "—"
    delta = ((current - previous) / previous) * 100
    sign = "+" if delta >= 0 else ""
    return f"{sign}{delta:.0f}%"


def _roas_change(current: float, previous: float) -> str:
    if previous <= 0:
        return "—"
    delta = current - previous
    sign = "+" if delta >= 0 else ""
    return f"{sign}{delta:.1f}x vs last month"


def _money_change(current: float, previous: float) -> str:
    if previous <= 0:
        return "—"
    delta = current - previous
    sign = "+" if delta >= 0 else ""
    return f"{sign}${abs(delta):,.0f} vs last month"


def _count_change(current: float, previous: float) -> str:
    if previous <= 0:
        return "—"
    return f"{_pct_change(current, previous)} vs last month"


def _build_campaign_rows(
    meta_metrics: dict | None,
    google_rows: list[dict] | None,
) -> list[tuple[str, float, float, float, float, str]]:
    rows: list[tuple[str, float, float, float, float, str]] = []
    if meta_metrics:
        spend = meta_metrics["spend"]
        revenue = spend * meta_metrics["roas"]
        conversions = meta_metrics["conversions"]
        cpl = spend / conversions if conversions else 0.0
        rows.append(
            (
                "Meta Ads — All Campaigns",
                spend,
                revenue,
                meta_metrics["roas"],
                cpl,
                "Active",
            )
        )
    if google_rows:
        for row in google_rows:
            spend = float(row.get("cost_micros", 0)) / 1_000_000
            conversions = float(row.get("conversions", 0))
            revenue = float(row.get("conversions_value", 0))
            roas = revenue / spend if spend else 0.0
            cpl = spend / conversions if conversions else 0.0
            name = str(row.get("campaign", "Google Ads Campaign"))
            rows.append((name, spend, revenue, roas, cpl, "Active"))
    return rows


def _format_table_money(value: float) -> str:
    return f"${value:,.0f}"


def _format_table_roas(value: float) -> str:
    return f"{value:.1f}x"


def _format_table_cpl(value: float) -> str:
    return f"${value:,.2f}"


def fill_report_pptx(client_name: str, client_slug: str, period: str) -> Path:
    reports_dir = REPO_ROOT / "clients" / client_slug / "reports"
    meta_current = _load_json(reports_dir / f".tmp-meta-{period}.json")
    google_current = _load_json(reports_dir / f".tmp-google-{period}.json")
    if not meta_current and not google_current:
        fail(f"No platform JSON in {reports_dir}. Run pull scripts or --demo first.")

    prior = _prior_period(period)
    meta_prev_data = _load_json(reports_dir / f".tmp-meta-{prior}.json")
    google_prev_data = _load_json(reports_dir / f".tmp-google-{prior}.json")

    meta_metrics = _parse_meta_row(meta_current["rows"][0]) if meta_current and meta_current.get("rows") else None
    google_metrics = (
        _parse_google_rows(google_current["rows"]) if google_current and google_current.get("rows") else None
    )
    meta_prev = _parse_meta_row(meta_prev_data["rows"][0]) if meta_prev_data and meta_prev_data.get("rows") else None
    google_prev = (
        _parse_google_rows(google_prev_data["rows"]) if google_prev_data and google_prev_data.get("rows") else None
    )

    total_spend = (meta_metrics or {}).get("spend", 0.0) + (google_metrics or {}).get("spend", 0.0)
    total_conversions = (meta_metrics or {}).get("conversions", 0.0) + (google_metrics or {}).get("conversions", 0.0)
    total_revenue = 0.0
    if meta_metrics:
        total_revenue += meta_metrics["spend"] * meta_metrics["roas"]
    if google_metrics:
        total_revenue += google_metrics["spend"] * google_metrics["roas"]
    combined_roas = total_revenue / total_spend if total_spend else 0.0
    combined_cpl = total_spend / total_conversions if total_conversions else 0.0

    prev_spend = (meta_prev or {}).get("spend", 0.0) + (google_prev or {}).get("spend", 0.0)
    prev_conversions = (meta_prev or {}).get("conversions", 0.0) + (google_prev or {}).get("conversions", 0.0)
    prev_revenue = 0.0
    if meta_prev:
        prev_revenue += meta_prev["spend"] * meta_prev["roas"]
    if google_prev:
        prev_revenue += google_prev["spend"] * google_prev["roas"]
    prev_roas = prev_revenue / prev_spend if prev_spend else 0.0
    prev_cpl = prev_spend / prev_conversions if prev_conversions else 0.0

    month_label = period_label(period)
    summary = _executive_summary(client_name, period, meta_metrics, google_metrics)
    insight_lines = _insights(meta_metrics, google_metrics)
    recommendation_lines = _recommendations(meta_metrics, google_metrics)

    guarantee_delta = max(combined_roas - 3.0, 0.0)
    highlights = [
        f"ROAS at {combined_roas:.1f}x — {'above' if combined_roas >= 3 else 'tracking toward'} the 3x guarantee target",
        insight_lines[0] if insight_lines else summary,
        insight_lines[1] if len(insight_lines) > 1 else recommendation_lines[0],
        recommendation_lines[0] if recommendation_lines else "Continue optimising top-performing campaigns.",
        recommendation_lines[1] if len(recommendation_lines) > 1 else "Schedule monthly review with client.",
    ]
    highlight_markers = [
        "ROAS exceeded",
        "Cold audience CPL",
        "Top ad creative",
        "Retargeting audiences",
        "No underperforming ad sets",
    ]
    note_markers = [
        "Lookalike audiences outperforming",
        "Creative fatigue detected",
        "Hot retargeting underweight",
    ]

    replacements = {
        "[CLIENT NAME]": client_name,
        "[MONTH YYYY]": month_label,
        "[Month YYYY]": month_label,
        "8.4×": f"{combined_roas:.1f}×",
        "+1.2× vs last month": _roas_change(combined_roas, prev_roas),
        "$52,340": _format_table_money(total_revenue),
        "+18% vs last month": _count_change(total_revenue, prev_revenue),
        "$6,230": _format_table_money(total_spend),
        "-4% (efficient)": _pct_change(total_spend, prev_spend) + " vs last month",
        "312": str(int(round(total_conversions))),
        "+24% vs last month": _count_change(total_conversions, prev_conversions),
        "$19.97": _format_table_cpl(combined_cpl),
        "-$4.20 vs last month": _money_change(combined_cpl, prev_cpl),
        "9.0×": f"{max(combined_roas * 1.05, 3.0):.1f}×",
        "$60,000+": f"{_format_table_money(total_revenue * 1.15)}+",
        "$6,600": _format_table_money(total_spend * 1.05),
        "<$18.00": f"<{_format_table_cpl(combined_cpl * 0.95)}",
        "360+": f"{int(round(total_conversions * 1.15))}+",
    }

    if not TEMPLATE_PPTX.exists():
        fail(f"Report template not found: {TEMPLATE_PPTX}")

    prs = Presentation(str(TEMPLATE_PPTX))
    campaign_rows = _build_campaign_rows(
        meta_metrics,
        google_current.get("rows") if google_current else None,
    )

    for slide in prs.slides:
        for shape in slide.shapes:
            replace_text_in_shape(shape, replacements)
            if shape.has_text_frame:
                text = shape.text_frame.text
                for idx, marker in enumerate(highlight_markers):
                    if marker in text:
                        set_shape_text(shape, f"▸  {highlights[idx]}")
                        break
                for idx, marker in enumerate(note_markers):
                    if marker in text:
                        note = recommendation_lines[idx] if idx < len(recommendation_lines) else highlights[-1]
                        set_shape_text(shape, note)
                        break
            if shape.has_table:
                table = shape.table
                for row_idx in range(1, 6):
                    if row_idx - 1 < len(campaign_rows):
                        name, spend, revenue, roas, cpl, status = campaign_rows[row_idx - 1]
                        values = [
                            name,
                            _format_table_money(spend),
                            _format_table_money(revenue),
                            _format_table_roas(roas),
                            _format_table_cpl(cpl),
                            status,
                        ]
                    else:
                        values = ["—", "—", "—", "—", "—", "—"]
                    for col_idx, value in enumerate(values):
                        set_cell_text(table.cell(row_idx, col_idx), value)
                totals = [
                    "TOTAL",
                    _format_table_money(total_spend),
                    _format_table_money(total_revenue),
                    _format_table_roas(combined_roas),
                    _format_table_cpl(combined_cpl),
                    "—",
                ]
                for col_idx, value in enumerate(totals):
                    set_cell_text(table.cell(6, col_idx), value)

    out_path = reports_dir / f"report-{period}.pptx"
    prs.save(str(out_path))
    return out_path


def main() -> None:
    parser = argparse.ArgumentParser(description="Bombay Media — Report PPTX Generator")
    parser.add_argument("--client-name", required=True)
    parser.add_argument("--client-slug", required=True)
    parser.add_argument("--period", required=True, help="YYYY-MM")
    args = parser.parse_args()

    path = fill_report_pptx(args.client_name, args.client_slug, args.period)
    print(f"OK Report PPTX saved: {path}")
    print(f"REPORT_PPTX_PATH:{path}")
    ok(f"REPORT_PPTX={path}")


if __name__ == "__main__":
    main()
