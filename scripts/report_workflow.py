#!/usr/bin/env python3
"""
End-to-end report workflow: pull data → synthesize → optional email → optional TTS.

Usage:
  python scripts/report_workflow.py --client-name "Demo Corp" --period 2025-01 --demo
  python scripts/report_workflow.py --client-name "Demo Corp" --period 2025-01 --demo --audio
"""

from __future__ import annotations

import argparse
import re
import subprocess
import sys
from datetime import datetime
from pathlib import Path

from _common import REPO_ROOT, fail, load_env, ok, slugify


def _run(cmd: list[str]) -> None:
    result = subprocess.run(cmd, cwd=REPO_ROOT, capture_output=True, text=True)
    if result.returncode != 0:
        fail(result.stderr.strip() or result.stdout.strip() or f"Command failed: {' '.join(cmd)}")
    if result.stdout.strip():
        print(result.stdout.strip())


def _resolve_slug(client_name: str) -> str:
    registry = REPO_ROOT / "context" / "clients.md"
    text = registry.read_text(encoding="utf-8") if registry.exists() else ""
    slug = slugify(client_name)
    if slug in text:
        return slug
    for line in text.splitlines():
        if client_name.lower() in line.lower():
            match = re.search(r"\|\s*[\d-]+\s*\|\s*[^|]+\s*\|\s*([a-z0-9-]+)\s*\|", line)
            if match:
                return match.group(1)
    fail(f"Client not found in context/clients.md: {client_name}")


def _parse_brief_platforms(slug: str) -> dict[str, str]:
    brief = REPO_ROOT / "clients" / slug / "client-brief.md"
    if not brief.exists():
        fail(f"Missing client brief: {brief}")
    text = brief.read_text(encoding="utf-8")
    platforms: dict[str, str] = {}
    for line in text.splitlines():
        if "| Meta" in line or "| meta" in line.lower():
            parts = [p.strip() for p in line.split("|") if p.strip()]
            if len(parts) >= 2:
                platforms["meta"] = parts[-1]
        if "| Google" in line or "| google" in line.lower():
            parts = [p.strip() for p in line.split("|") if p.strip()]
            if len(parts) >= 2:
                platforms["google"] = parts[-1]
    if "meta" not in platforms and "google" not in platforms:
        if "meta" in text.lower():
            platforms["meta"] = ""
        if "google" in text.lower():
            platforms["google"] = ""
    return platforms


def _connections_status() -> dict[str, str]:
    path = REPO_ROOT / "connections.md"
    text = path.read_text(encoding="utf-8")
    status: dict[str, str] = {}
    for line in text.splitlines():
        if not line.startswith("|") or "---" in line or "Key" in line:
            continue
        parts = [p.strip() for p in line.split("|")]
        if len(parts) < 8:
            continue
        key_match = re.search(r"`([^`]+)`", parts[3])
        status_match = re.search(r"`([^`]+)`", parts[6])
        if key_match and status_match:
            status[key_match.group(1)] = status_match.group(1)
    return status


def _cleanup_tmp(reports_dir: Path) -> None:
    for path in reports_dir.glob(".tmp-*.json"):
        path.unlink(missing_ok=True)


def _append_log(client: str, period: str, slug: str, platforms: list[str], report_path: Path) -> None:
    log = REPO_ROOT / "decisions" / "log.md"
    ts = datetime.now().isoformat(timespec="seconds")
    pptx_name = report_path.with_suffix(".pptx").name
    line = (
        f"{ts} | /report | {client} {period} | platforms: {', '.join(platforms) or 'demo'} "
        f"| path: clients/{slug}/reports/{report_path.name}, {pptx_name}\n"
    )
    with log.open("a", encoding="utf-8") as f:
        f.write(line)


def main() -> None:
    load_env()
    parser = argparse.ArgumentParser(description="Agency OS report workflow")
    parser.add_argument("--client-name", required=True)
    parser.add_argument("--period", required=True, help="YYYY-MM")
    parser.add_argument("--demo", action="store_true", help="Use fixture JSON instead of live APIs")
    parser.add_argument("--send-email", action="store_true")
    parser.add_argument("--audio", action="store_true", help="Generate executive summary MP3 via ElevenLabs")
    args = parser.parse_args()

    slug = _resolve_slug(args.client_name)
    reports_dir = REPO_ROOT / "clients" / slug / "reports"
    reports_dir.mkdir(parents=True, exist_ok=True)
    connections = _connections_status()
    platforms_used: list[str] = []

    if args.demo:
        _run(
            [
                sys.executable,
                "scripts/report_pull_demo.py",
                "--client-slug",
                slug,
                "--period",
                args.period,
            ]
        )
        if (reports_dir / f".tmp-meta-{args.period}.json").exists():
            platforms_used.append("meta")
        if (reports_dir / f".tmp-google-{args.period}.json").exists():
            platforms_used.append("google")
    else:
        brief_platforms = _parse_brief_platforms(slug)
        if "meta" in brief_platforms and connections.get("meta-ads") == "connected":
            account = brief_platforms["meta"] or ""
            _run(
                [
                    sys.executable,
                    "scripts/meta_ads_pull.py",
                    "--account-id",
                    account,
                    "--period",
                    args.period,
                    "--client-slug",
                    slug,
                ]
            )
            platforms_used.append("meta")
        if "google" in brief_platforms and connections.get("google-ads") == "connected":
            customer = brief_platforms["google"] or ""
            _run(
                [
                    sys.executable,
                    "scripts/google_ads_pull.py",
                    "--customer-id",
                    customer,
                    "--period",
                    args.period,
                    "--client-slug",
                    slug,
                ]
            )
            platforms_used.append("google")

    if not platforms_used:
        fail("No platform data pulled. Use --demo or connect meta-ads/google-ads in connections.md")

    _run(
        [
            sys.executable,
            "scripts/synthesize_report.py",
            "--client-name",
            args.client_name,
            "--client-slug",
            slug,
            "--period",
            args.period,
        ]
    )
    report_path = reports_dir / f"report-{args.period}.md"

    _run(
        [
            sys.executable,
            "scripts/generate_report_pptx.py",
            "--client-name",
            args.client_name,
            "--client-slug",
            slug,
            "--period",
            args.period,
        ]
    )
    report_pptx_path = reports_dir / f"report-{args.period}.pptx"

    if args.audio and connections.get("elevenlabs") == "connected":
        _run(
            [
                sys.executable,
                "scripts/elevenlabs_tts.py",
                "--report-path",
                str(report_path),
                "--output",
                str(reports_dir / f"report-{args.period}.mp3"),
            ]
        )

    if args.send_email:
        if connections.get("smtp") != "connected":
            fail("SMTP not connected — cannot send email")
        brief = (REPO_ROOT / "clients" / slug / "client-brief.md").read_text(encoding="utf-8")
        email_match = re.search(r"[\w.+-]+@[\w-]+\.[\w.-]+", brief)
        if not email_match:
            fail("No client email found in client-brief.md")
        _run(
            [
                sys.executable,
                "scripts/send_email.py",
                "--to",
                email_match.group(0),
                "--subject",
                f"Performance Report — {args.client_name} — {args.period}",
                "--template",
                "report",
                "--client-name",
                args.client_name,
                "--company",
                args.client_name,
                "--period",
                args.period,
                "--attachment",
                str(report_path),
            ]
        )

    _cleanup_tmp(reports_dir)
    _append_log(args.client_name, args.period, slug, platforms_used, report_path)
    ok(f"REPORT_COMPLETE={report_path}|REPORT_PPTX={report_pptx_path}")


if __name__ == "__main__":
    main()
