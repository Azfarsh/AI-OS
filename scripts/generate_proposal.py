#!/usr/bin/env python3
"""
generate_proposal.py — Bombay Media Proposal Generator
Builds a pixel-perfect branded 4-slide PPTX proposal from meeting notes data.

Usage:
    python scripts/generate_proposal.py \
        --client-name "James Carter" \
        --company "FitCoach Pro" \
        --client-email "james@fitcoachpro.com" \
        --slug "james-carter" \
        --pain-points "Low ROAS on Meta, no retargeting, creatives not converting" \
        --budget "5000" \
        --services "meta,content" \
        --ad-spend-range "3000-7000"
"""

import argparse
import sys
from datetime import datetime
from pathlib import Path

try:
    from pptx import Presentation
    from pptx.util import Inches, Pt, Emu
    from pptx.dml.color import RGBColor
    from pptx.enum.text import PP_ALIGN
    from pptx.oxml.ns import qn
    from lxml import etree
except ImportError:
    print("ERROR: python-pptx not installed. Run: pip install python-pptx")
    sys.exit(1)

# ── Repo paths ─────────────────────────────────────────────────────
REPO_ROOT = Path(__file__).parent.parent
CLIENTS_DIR = REPO_ROOT / "clients"

# ── Brand constants ────────────────────────────────────────────────
C_PURPLE      = RGBColor(0x32, 0x07, 0x53)   # #320753 — primary
C_PURPLE2     = RGBColor(0x37, 0x24, 0x5C)   # #37245C — variant
C_YELLOW      = RGBColor(0xFF, 0xDE, 0x00)   # #FFDE00 — accent
C_BLACK       = RGBColor(0x11, 0x11, 0x11)   # #111111 — body
C_LAVENDER    = RGBColor(0xF8, 0xF5, 0xFF)   # #F8F5FF — card bg
C_WHITE       = RGBColor(0xFF, 0xFF, 0xFF)   # #FFFFFF
C_GREY        = RGBColor(0x6B, 0x72, 0x80)   # #6B7280 — subtext
C_PURPLE_LITE = RGBColor(0x9F, 0x86, 0xC0)   # #9F86C0 — muted purple
C_DIVIDER     = RGBColor(0xE5, 0xD9, 0xF2)   # #E5D9F2

# Slide dimensions (10" × 5.625")
W = Inches(10)
H = Inches(5.625)


# ── Helpers ────────────────────────────────────────────────────────

def add_rect(slide, left, top, width, height, fill_rgb):
    shape = slide.shapes.add_shape(1, Inches(left), Inches(top), Inches(width), Inches(height))
    shape.line.fill.background()
    shape.fill.solid()
    shape.fill.fore_color.rgb = fill_rgb
    return shape


def add_text(slide, text, left, top, width, height,
             font_name="Calibri", font_size=10, bold=False,
             color=C_BLACK, align=PP_ALIGN.LEFT, wrap=True):
    txBox = slide.shapes.add_textbox(Inches(left), Inches(top), Inches(width), Inches(height))
    tf = txBox.text_frame
    tf.word_wrap = wrap
    p = tf.paragraphs[0]
    p.alignment = align
    run = p.add_run()
    run.text = text
    run.font.name = font_name
    run.font.size = Pt(font_size)
    run.font.bold = bold
    run.font.color.rgb = color
    return txBox


def add_footer(slide, left_text="bmmediagrowth.com  |  Bombay Media  |  Dubai & Mumbai",
               bg=C_YELLOW, fg=C_PURPLE):
    add_rect(slide, 0, 5.300, 10, 0.325, bg)
    add_text(slide, left_text, 0.4, 5.300, 9, 0.325,
             font_size=9, color=fg)


def add_purple_header(slide, title_text):
    """Standard purple header bar used on slides 2-4."""
    add_rect(slide, 0, 0, 10, 0.700, C_PURPLE)
    add_text(slide, title_text, 0.4, 0.0, 9, 0.700,
             font_name="Arial Black", font_size=12, bold=True,
             color=C_YELLOW)


def set_slide_bg(slide, color_rgb):
    bg = slide.background
    fill = bg.fill
    fill.solid()
    fill.fore_color.rgb = color_rgb


def slugify(name: str) -> str:
    return name.lower().strip().replace(" ", "-").replace("'", "").replace(",", "")


def services_label(services_str: str) -> str:
    mapping = {
        "meta":    "Meta Ads Management",
        "google":  "Google Ads Management",
        "content": "Content Marketing",
        "seo":     "SEO & Content",
    }
    parts = [mapping.get(s.strip(), s.strip().title()) for s in services_str.split(",")]
    if len(parts) == 1:
        return parts[0]
    return ", ".join(parts[:-1]) + " and " + parts[-1]


def parse_services(services_str: str) -> list:
    """Return list of (title, description) tuples for slide 3 service cards."""
    all_services = {
        "meta": (
            "AI-Powered Meta Ads",
            "Full funnel campaign architecture — cold, warm, and retargeting. "
            "Creative testing at scale. Weekly optimisation with ROAS accountability."
        ),
        "content": (
            "Content Marketing System",
            "AI-generated ad creatives, carousel content, and email sequences "
            "tailored to your program audience. All done-for-you."
        ),
        "google": (
            "Google Ads Management",
            "Search and Performance Max campaigns built around high-intent buyers. "
            "Keyword architecture, bid strategy, and weekly optimisation."
        ),
        "seo": (
            "SEO & Content Engine",
            "Long-form content, keyword strategy, and authority building for "
            "organic discovery alongside your paid campaigns."
        ),
    }
    # Always include guaranteed standards
    standards = [
        (
            "Funnel Diagnostic (Free First)",
            "Before we begin, you receive a personalised Funnel Leaks diagnostic "
            "report — revealing exactly where revenue is escaping your funnel today."
        ),
        (
            "Weekly Reporting & Direct Access",
            "Live ROAS dashboard and a weekly summary directly from Farhan — "
            "not an account manager. Full transparency at all times."
        ),
        (
            "90-Day Guarantee",
            "If we don't hit 3× ROAS within 90 days, we continue working for free "
            "until we do. No asterisks. No exceptions."
        ),
        (
            "Strategy Calls",
            "Monthly performance review call with your dedicated strategist. "
            "You always know what's running, why, and what's next."
        ),
    ]

    selected = []
    for s in services_str.split(","):
        s = s.strip()
        if s in all_services:
            selected.append(all_services[s])

    # Fill up to 6 cards (3×2 grid)
    combined = selected + standards
    return combined[:6]


# ── Slide builders ─────────────────────────────────────────────────

def build_slide1_cover(prs, client_name, company, date_str, budget_monthly):
    """Cover slide — dark purple background."""
    slide = prs.slides.add_slide(prs.slide_layouts[6])  # blank
    set_slide_bg(slide, C_PURPLE)

    # Yellow left accent stripe
    add_rect(slide, 0, 0, 0.18, 5.625, C_YELLOW)

    # Right dark panel
    add_rect(slide, 7.5, 0, 2.5, 5.625, C_PURPLE2)

    # BM monogram badge (yellow circle + dark text)
    add_rect(slide, 0.5, 1.0, 0.9, 0.9, C_YELLOW)
    add_text(slide, "BM", 0.5, 1.0, 0.9, 0.9,
             font_name="Arial Black", font_size=24, bold=True,
             color=C_PURPLE, align=PP_ALIGN.CENTER)

    # Agency name + tagline
    add_text(slide, "BOMBAY MEDIA", 1.55, 1.10, 5.0, 0.35,
             font_name="Arial Black", font_size=14, bold=True,
             color=C_WHITE)
    add_text(slide, "AI-Powered Performance Marketing", 1.55, 1.50, 5.0, 0.30,
             font_size=10, color=C_YELLOW)

    # Main title block — two-line heading, placed lower to avoid logo overlap
    add_text(slide, "GROWTH", 0.5, 2.15, 6.5, 0.75,
             font_name="Arial Black", font_size=44, bold=True,
             color=C_WHITE)
    add_text(slide, "PROPOSAL", 0.5, 2.85, 6.5, 0.75,
             font_name="Arial Black", font_size=44, bold=True,
             color=C_WHITE)
    add_text(slide, "3× ROAS in 90 Days — Guaranteed", 0.5, 3.65, 6.5, 0.40,
             font_size=16, color=C_YELLOW)

    # Client name block
    add_text(slide, "Prepared for:", 0.5, 4.15, 6.0, 0.28,
             font_size=10, color=C_PURPLE_LITE)
    add_text(slide, client_name, 0.5, 4.42, 6.0, 0.35,
             font_name="Arial Black", font_size=15, bold=True,
             color=C_WHITE)
    add_text(slide, f"{date_str}  |  Prepared by Farhan Rakhangi", 0.5, 4.80, 6.0, 0.28,
             font_size=9, color=C_PURPLE_LITE)

    # Right panel — best case study stat (separate text boxes per line)
    add_text(slide, "25.6×", 7.6, 1.10, 2.2, 0.55,
             font_name="Arial Black", font_size=30, bold=True,
             color=C_YELLOW, align=PP_ALIGN.CENTER)
    add_text(slide, "ROAS", 7.6, 1.62, 2.2, 0.40,
             font_name="Arial Black", font_size=18, bold=True,
             color=C_YELLOW, align=PP_ALIGN.CENTER)
    add_text(slide, "Best 90-Day Case Study", 7.6, 2.10, 2.2, 0.55,
             font_size=9, color=C_WHITE, align=PP_ALIGN.CENTER)
    add_text(slide, "$179,850", 7.6, 2.80, 2.2, 0.55,
             font_name="Arial Black", font_size=22, bold=True,
             color=C_WHITE, align=PP_ALIGN.CENTER)
    add_text(slide, "revenue", 7.6, 3.32, 2.2, 0.35,
             font_name="Arial Black", font_size=14, bold=True,
             color=C_WHITE, align=PP_ALIGN.CENTER)
    add_text(slide, "from $7,017", 7.6, 3.80, 2.2, 0.30,
             font_size=10, color=C_PURPLE_LITE, align=PP_ALIGN.CENTER)
    add_text(slide, "ad spend", 7.6, 4.08, 2.2, 0.30,
             font_size=10, color=C_PURPLE_LITE, align=PP_ALIGN.CENTER)

    # Footer
    add_rect(slide, 0, 5.30, 10, 0.325, C_YELLOW)
    add_text(slide, f"CONFIDENTIAL  |  bmmediagrowth.com", 0.4, 5.30, 9, 0.325,
             font_size=9, color=C_PURPLE)


def build_slide2_proof(prs, company, pain_summary):
    """Proof slide — real numbers, always static (verified case study)."""
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    set_slide_bg(slide, C_WHITE)

    add_purple_header(slide, "THE PROOF — REAL CLIENT, REAL NUMBERS")

    add_text(slide, "US Investment & Trading Coach  |  Jan–Mar 2026  |  90-Day Campaign",
             0.4, 0.82, 9.0, 0.30, font_size=10, color=C_GREY)

    # 4 stat cards
    cards = [
        (0.40,  "REVENUE GENERATED", "$179,850",  "in 90 days",      C_LAVENDER, C_PURPLE, C_GREY),
        (2.70,  "AD SPEND",          "$7,017",     "total invested",  C_LAVENDER, C_PURPLE, C_GREY),
        (5.00,  "ROAS ACHIEVED",     "25.6×",      "vs 3× guarantee", C_PURPLE,  C_WHITE,  C_PURPLE_LITE),
        (7.30,  "BEST CAMPAIGN",     "131×",       "single campaign ROAS", C_LAVENDER, C_PURPLE, C_GREY),
    ]

    for left, label, number, sub, card_bg, num_color, sub_color in cards:
        add_rect(slide, left, 1.25, 2.1, 2.5, card_bg)
        add_text(slide, label, left + 0.1, 1.35, 1.9, 0.45,
                 font_name="Arial Black", font_size=8, bold=True, color=C_GREY)
        # Use smaller font for long numbers like $179,850
        num_size = 22 if len(number) >= 8 else (26 if len(number) > 5 else 32)
        add_text(slide, number, left + 0.1, 1.80, 1.9, 0.90,
                 font_name="Arial Black", font_size=num_size, bold=True, color=num_color)
        add_text(slide, sub, left + 0.1, 2.80, 1.9, 0.35,
                 font_size=10, color=sub_color)

    # Divider + context section
    add_rect(slide, 0.4, 3.95, 9.2, 0.06, C_DIVIDER)
    add_text(slide, "18-Month Authority Context", 0.4, 4.10, 9.0, 0.35,
             font_name="Arial Black", font_size=12, bold=True, color=C_PURPLE)
    add_text(slide,
             "Same client — $263,646 total revenue from $26,493 ad spend over 18 months = "
             "9.95× blended ROAS. The 90-day sprint above is our standard onboarding performance, not an outlier.",
             0.4, 4.50, 9.2, 0.65, font_size=10, color=C_BLACK)

    add_footer(slide, "Metrics verified. Identity anonymised by client request.")


def build_slide3_services(prs, services_str, pain_points):
    """What we deliver — 6 service cards in a 3×2 grid."""
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    set_slide_bg(slide, C_WHITE)

    add_purple_header(slide, "WHAT WE DELIVER FOR YOU")

    service_cards = parse_services(services_str)

    positions = [
        (0.40, 0.85),   # 01
        (3.55, 0.85),   # 02
        (6.70, 0.85),   # 03
        (0.40, 2.95),   # 04
        (3.55, 2.95),   # 05
        (6.70, 2.95),   # 06
    ]

    for i, ((left, top), (title, desc)) in enumerate(zip(positions, service_cards), 1):
        # Card background
        add_rect(slide, left, top, 2.95, 1.90, C_LAVENDER)
        # Number badge
        add_rect(slide, left, top, 0.55, 0.55, C_YELLOW)
        add_text(slide, f"0{i}", left, top, 0.55, 0.55,
                 font_name="Arial Black", font_size=12, bold=True,
                 color=C_PURPLE, align=PP_ALIGN.CENTER)
        # Title
        add_text(slide, title, left + 0.65, top + 0.08, 2.2, 0.40,
                 font_name="Arial Black", font_size=10, bold=True, color=C_PURPLE)
        # Description
        add_text(slide, desc, left + 0.10, top + 0.65, 2.75, 1.10,
                 font_size=9, color=C_BLACK, wrap=True)

    add_footer(slide)


def build_slide4_investment(prs, budget_monthly, ad_spend_range, services_str):
    """Investment & Next Steps — pricing table + 3 CTA steps."""
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    set_slide_bg(slide, C_WHITE)

    add_purple_header(slide, "INVESTMENT & NEXT STEPS")

    # --- Left: Pricing ---
    add_text(slide, "Your Investment", 0.4, 0.85, 4.5, 0.38,
             font_name="Arial Black", font_size=16, bold=True, color=C_PURPLE)

    # Parse budget
    try:
        retainer = int(budget_monthly)
    except (ValueError, TypeError):
        retainer = 3000

    try:
        ad_min, ad_max = [int(x.strip()) for x in ad_spend_range.split("-")]
    except Exception:
        ad_min, ad_max = 3000, 10000

    all_in = retainer + 1500 // 12  # approx
    market_rate = 8000

    pricing_rows = [
        ("Setup Fee",         "One-time",    "$1,500",                     C_LAVENDER),
        ("Monthly Retainer",  "Ongoing",     f"${retainer:,}/mo",          C_WHITE),
        ("Ad Spend",          "Client-direct", f"${ad_min:,}–${ad_max:,}/mo", C_LAVENDER),
    ]

    for i, (label, term, amount, row_bg) in enumerate(pricing_rows):
        top = 1.35 + i * 0.70
        add_rect(slide, 0.4, top, 4.5, 0.60, row_bg)
        add_text(slide, label, 0.55, top, 2.0, 0.60,
                 font_name="Arial Black", font_size=10, bold=True, color=C_PURPLE)
        add_text(slide, term, 2.55, top, 1.3, 0.60,
                 font_size=10, color=C_GREY)
        add_text(slide, amount, 3.85, top, 1.05, 0.60,
                 font_name="Arial Black", font_size=11, bold=True, color=C_PURPLE)

    # Value callout bar
    add_rect(slide, 0.4, 3.50, 4.5, 0.55, C_PURPLE)
    add_text(slide,
             f"Market Rate: ~${market_rate:,}/mo.  Your exclusive client price: ${retainer + 1500 // 12:,}/mo all-in",
             0.5, 3.50, 4.3, 0.55,
             font_size=9, color=C_YELLOW)

    # --- Right: Next Steps ---
    add_text(slide, "Your Next 3 Steps", 5.4, 0.85, 4.2, 0.38,
             font_name="Arial Black", font_size=16, bold=True, color=C_PURPLE)

    steps = [
        (1.35,  "1", "Get your free Funnel Leaks report",
                "Visit bmmediagrowth.com — takes 2 minutes and shows you exactly where you're leaking revenue today."),
        (2.55,  "2", "Book a strategy call",
                "30 minutes with Farhan directly. We'll review your funnel diagnostic and map out your 90-day growth plan."),
        (3.75,  "3", "We launch in 14 days",
                "Upon signing, your campaign is live within two weeks. Day 1, your audience starts seeing your offer at scale."),
    ]

    for top, num, step_title, step_body in steps:
        add_rect(slide, 5.4, top, 0.50, 0.50, C_YELLOW)
        add_text(slide, num, 5.4, top, 0.50, 0.50,
                 font_name="Arial Black", font_size=16, bold=True,
                 color=C_PURPLE, align=PP_ALIGN.CENTER)
        add_text(slide, step_title, 6.05, top + 0.02, 3.5, 0.35,
                 font_name="Arial Black", font_size=10, bold=True, color=C_PURPLE)
        add_text(slide, step_body, 6.05, top + 0.40, 3.5, 0.70,
                 font_size=9, color=C_BLACK, wrap=True)

    # Calendly CTA bar
    add_rect(slide, 5.4, 4.80, 4.2, 0.38, C_YELLOW)
    add_text(slide, "calendly.com/bombay_media/complimentary-business-success-call",
             5.5, 4.80, 4.0, 0.38,
             font_size=8, bold=True, color=C_PURPLE)

    add_footer(slide)


# ── Main ──────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="Bombay Media — Proposal Generator")
    parser.add_argument("--client-name",    required=True,  help="Prospect full name")
    parser.add_argument("--company",        required=True,  help="Company / business name")
    parser.add_argument("--client-email",   required=True,  help="Prospect email")
    parser.add_argument("--slug",           required=True,  help="clients/ folder slug")
    parser.add_argument("--pain-points",    default="",     help="Comma-separated pain points from notes")
    parser.add_argument("--budget",         default="3000", help="Monthly retainer budget (USD, number only)")
    parser.add_argument("--services",       default="meta,content", help="Comma-separated: meta,content,google,seo")
    parser.add_argument("--ad-spend-range", default="3000-10000",   help="e.g. 3000-7000")
    args = parser.parse_args()

    # ── Build presentation ─────────────────────────────────────────
    prs = Presentation()
    prs.slide_width  = Inches(10)
    prs.slide_height = Inches(5.625)

    today = datetime.today()
    date_str = f"{today.day} {today.strftime('%B %Y')}"
    date_tag = today.strftime("%Y-%m-%d")

    build_slide1_cover(prs, args.client_name, args.company, date_str, args.budget)
    build_slide2_proof(prs, args.company, args.pain_points)
    build_slide3_services(prs, args.services, args.pain_points)
    build_slide4_investment(prs, args.budget, args.ad_spend_range, args.services)

    # ── Save ───────────────────────────────────────────────────────
    out_dir = CLIENTS_DIR / args.slug / "proposals"
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / f"proposal-{date_tag}.pptx"
    prs.save(str(out_path))

    print(f"✓ Proposal PPTX saved: {out_path}")
    print(f"PROPOSAL_PATH:{out_path}")


if __name__ == "__main__":
    main()
