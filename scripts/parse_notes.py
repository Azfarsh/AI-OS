#!/usr/bin/env python3
"""
parse_notes.py — Bombay Media Notes Parser
Reads a clients/{slug}/notes.md file and extracts structured data
to be passed as arguments to generate_proposal.py.

Prints a shell-ready argument string.

Usage:
    python scripts/parse_notes.py --client "james-carter"
    
Output (stdout):
    PAIN_POINTS:Low ROAS on Meta, no retargeting, creatives not converting
    BUDGET:5000
    AD_SPEND_RANGE:3000-7000
    SERVICES:meta,content
    COMPANY_NICHE:Online fitness coaching for busy professionals
"""

import argparse
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).parent.parent
CLIENTS_DIR = REPO_ROOT / "clients"

# Services keyword map — if any of these words appear in notes, include that service
SERVICE_KEYWORDS = {
    "meta":    ["meta", "facebook", "instagram", "fb ads", "ig ads", "social ads"],
    "google":  ["google", "search ads", "ppc", "adwords", "youtube"],
    "content": ["content", "creative", "carousel", "email", "copy", "ugc"],
    "seo":     ["seo", "organic", "blog", "search engine", "ranking"],
}


def extract_budget(text: str) -> str:
    """Extract monthly retainer budget from notes. Returns number string."""
    patterns = [
        r"monthly retainer budget discussed[:\s\$]+(\d[\d,]+)",
        r"retainer[:\s\$]+(\d[\d,]+)",
        r"budget[:\s\$]+(\d[\d,]+)",
        r"\$(\d[\d,]+)\s*/?\s*mo",
        r"\$(\d[\d,]+)\s*per month",
        r"\$(\d[\d,]+)\s*monthly",
    ]
    for pat in patterns:
        m = re.search(pat, text, re.IGNORECASE)
        if m:
            return m.group(1).replace(",", "")
    return "3000"  # default


def extract_ad_spend(text: str) -> str:
    """Extract ad spend range from notes. Returns 'min-max' string."""
    # Look for range patterns like $3,000–$7,000 or $3k-$7k
    range_pat = r"\$(\d[\d,k]+)\s*[-–—to]+\s*\$(\d[\d,k]+)\s*/?\s*(?:mo|month|monthly)?"
    m = re.search(range_pat, text, re.IGNORECASE)
    if m:
        lo = m.group(1).replace(",", "").replace("k", "000")
        hi = m.group(2).replace(",", "").replace("k", "000")
        return f"{lo}-{hi}"

    # Single value
    single_pat = r"ad spend[^$\n]*\$(\d[\d,k]+)"
    m = re.search(single_pat, text, re.IGNORECASE)
    if m:
        val = m.group(1).replace(",", "").replace("k", "000")
        try:
            v = int(val)
            return f"{v}-{v * 2}"  # rough range
        except ValueError:
            pass

    return "3000-10000"


def extract_pain_points(text: str) -> str:
    """Extract bullet-pointed pain points from the Pain Points section."""
    section = re.search(
        r"##\s*Pain Points.*?\n(.*?)(?=##|\Z)",
        text, re.DOTALL | re.IGNORECASE
    )
    if not section:
        return ""

    lines = section.group(1).strip().splitlines()
    points = []
    for line in lines:
        line = line.strip().lstrip("-•*").strip()
        if line and len(line) > 5 and not line.startswith("#"):
            points.append(line)

    return "; ".join(points[:4]) if points else ""


def extract_services(text: str) -> str:
    """Infer which services to include based on keywords in notes."""
    text_lower = text.lower()
    found = []
    for service, keywords in SERVICE_KEYWORDS.items():
        if any(kw in text_lower for kw in keywords):
            found.append(service)

    # Always include meta for performance marketing agency
    if not found:
        found = ["meta", "content"]
    elif "meta" not in found:
        found.insert(0, "meta")  # meta is always primary

    return ",".join(found[:4])  # max 4 services (3 cards + standards fill rest)


def extract_niche(text: str) -> str:
    """Extract company niche / audience description."""
    section = re.search(
        r"##\s*Client Overview.*?\n(.*?)(?=##|\Z)",
        text, re.DOTALL | re.IGNORECASE
    )
    if not section:
        return ""

    for line in section.group(1).splitlines():
        if re.search(r"niche|audience|industry|serve|coach", line, re.IGNORECASE):
            val = re.sub(r"^[-•*\s]*[^:]+:\s*", "", line).strip()
            if val and len(val) > 3:
                return val
    return ""


def main():
    parser = argparse.ArgumentParser(description="Parse meeting notes for proposal generation")
    parser.add_argument("--client", required=True, help="Client slug, e.g. james-carter")
    args = parser.parse_args()

    notes_path = CLIENTS_DIR / args.client / "notes.md"

    if not notes_path.exists():
        print(f"ERROR: notes.md not found at {notes_path}")
        sys.exit(1)

    text = notes_path.read_text(encoding="utf-8")

    # Check it's not just the empty template
    filled_lines = [l for l in text.splitlines()
                    if l.strip() and not l.startswith("#") and not l.startswith(">")
                    and not l.startswith("_") and len(l.strip()) > 3
                    and l.strip() not in ["-", "•"]]

    if len(filled_lines) < 3:
        print(f"ERROR: notes.md at {notes_path} appears to be empty or unfilled.")
        print("  → Add meeting notes before running /proposal")
        sys.exit(1)

    pain   = extract_pain_points(text)
    budget = extract_budget(text)
    spend  = extract_ad_spend(text)
    svcs   = extract_services(text)
    niche  = extract_niche(text)

    # Print structured output for the calling skill
    print(f"PAIN_POINTS:{pain}")
    print(f"BUDGET:{budget}")
    print(f"AD_SPEND_RANGE:{spend}")
    print(f"SERVICES:{svcs}")
    print(f"NICHE:{niche}")


if __name__ == "__main__":
    main()
