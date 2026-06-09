#!/usr/bin/env python3
"""
fetch_notes.py — Bombay Media Meeting Notes Fetcher
Searches Google Drive for the prospect's meeting notes file and saves to clients/{slug}/notes.md

The script searches for any of these filename patterns in the agency's Drive notes folder:
  - "{Company Name} - Meeting Notes"
  - "{Company Name} Meeting Notes"
  - "Meeting Notes - {Company Name}"
  - "{slug}" (fuzzy match fallback)

Setup requirement:
  GOOGLE_SERVICE_ACCOUNT_JSON_PATH and GOOGLE_DRIVE_NOTES_FOLDER_ID in .env

Usage:
    python scripts/fetch_notes.py --client "james-carter" --company "FitCoach Pro"
"""

import argparse
import os
import sys
from pathlib import Path

try:
    from dotenv import load_dotenv
except ImportError:
    print("ERROR: python-dotenv not installed. Run: pip install python-dotenv")
    sys.exit(1)

# ── Load env ────────────────────────────────────────────────────────
REPO_ROOT = Path(__file__).parent.parent
load_dotenv(REPO_ROOT / ".env")

SERVICE_ACCOUNT_PATH = os.getenv("GOOGLE_SERVICE_ACCOUNT_JSON_PATH", "")
NOTES_FOLDER_ID      = os.getenv("GOOGLE_DRIVE_NOTES_FOLDER_ID", "")
CLIENTS_DIR          = REPO_ROOT / "clients"

# ── Optional Google Drive deps ──────────────────────────────────────
try:
    from googleapiclient.discovery import build
    from googleapiclient.http import MediaIoBaseDownload
    from google.oauth2 import service_account
    import io
    GDRIVE_AVAILABLE = True
except ImportError:
    GDRIVE_AVAILABLE = False


def get_drive_service():
    if not SERVICE_ACCOUNT_PATH:
        print("ERROR: GOOGLE_SERVICE_ACCOUNT_JSON_PATH not set in .env")
        sys.exit(1)
    credentials = service_account.Credentials.from_service_account_file(
        SERVICE_ACCOUNT_PATH,
        scopes=["https://www.googleapis.com/auth/drive.readonly"]
    )
    return build("drive", "v3", credentials=credentials)


def search_for_notes(service, company: str, slug: str) -> dict | None:
    """Search Drive for the meeting notes file. Returns file metadata or None."""
    search_terms = [
        f"{company} - Meeting Notes",
        f"{company} Meeting Notes",
        f"Meeting Notes - {company}",
        company,
        slug,
    ]

    for term in search_terms:
        query = f"name contains '{term}' and trashed = false"
        if NOTES_FOLDER_ID:
            query += f" and '{NOTES_FOLDER_ID}' in parents"

        result = service.files().list(
            q=query,
            fields="files(id, name, mimeType)",
            pageSize=5
        ).execute()

        files = result.get("files", [])
        if files:
            print(f"  ✓ Found: '{files[0]['name']}' (matched on: '{term}')")
            return files[0]

    return None


def download_file(service, file_meta: dict, out_path: Path):
    """Download file content. Handles Google Docs (export as text) and plain files."""
    mime = file_meta.get("mimeType", "")
    fid  = file_meta["id"]

    if mime == "application/vnd.google-apps.document":
        # Export Google Doc as plain text
        request = service.files().export_media(
            fileId=fid, mimeType="text/plain"
        )
    else:
        request = service.files().get_media(fileId=fid)

    fh = io.BytesIO()
    downloader = MediaIoBaseDownload(fh, request)
    done = False
    while not done:
        _, done = downloader.next_chunk()

    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_bytes(fh.getvalue())
    print(f"  ✓ Saved to: {out_path}")


def create_notes_template(slug: str, company: str, out_path: Path):
    """Create an empty notes.md template when Drive is not connected."""
    template = f"""# Meeting Notes — {company}

> Fill this file before running /proposal.
> Captured after the first discovery call with the prospect.

## Client Overview
- Company: {company}
- Contact name + role:
- Website:
- Industry / niche:
- Audience (who they coach / serve):

## Current Situation
- Platforms they're currently advertising on:
- Monthly ad spend currently:
- What's not working / biggest frustration:
- Any agencies they've worked with before:

## Pain Points (what they said, verbatim if possible)
-
-
-

## Goals
- Primary goal (e.g. "increase ROAS", "scale to $X/month"):
- Timeline they mentioned:
- Success metric in their words:

## Budget
- Monthly retainer budget discussed: $
- Ad spend they're comfortable with: $___/month
- Any hesitation around pricing:

## Objections / Concerns
-

## Competitor Context
- Who else are they talking to:
- What made them reach out to Bombay Media:

## Notes / Other
-

---
_Last updated: [add date]_
"""
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(template)


def main():
    parser = argparse.ArgumentParser(description="Fetch meeting notes from Google Drive")
    parser.add_argument("--client",  required=True, help="Client slug, e.g. james-carter")
    parser.add_argument("--company", required=True, help="Company name, e.g. FitCoach Pro")
    args = parser.parse_args()

    notes_path = CLIENTS_DIR / args.client / "notes.md"

    # ── Check if already exists ─────────────────────────────────────
    if notes_path.exists() and notes_path.stat().st_size > 200:
        print(f"✓ notes.md already exists and has content: {notes_path}")
        print(f"NOTES_PATH:{notes_path}")
        sys.exit(0)

    # ── Try Google Drive ────────────────────────────────────────────
    if not GDRIVE_AVAILABLE:
        print("⚠ google-api-python-client not installed.")
        print("  Run: pip install google-api-python-client google-auth")
        print("  Falling back to empty template.")
        create_notes_template(args.client, args.company, notes_path)
        print(f"\n📝 Empty notes.md created at: {notes_path}")
        print("  → Fill it with meeting notes, then re-run /proposal")
        sys.exit(1)

    if not SERVICE_ACCOUNT_PATH or not os.path.exists(SERVICE_ACCOUNT_PATH):
        print("⚠ GOOGLE_SERVICE_ACCOUNT_JSON_PATH not set or file missing.")
        print("  Falling back to empty template.")
        create_notes_template(args.client, args.company, notes_path)
        print(f"\n📝 Empty notes.md created at: {notes_path}")
        print("  → Fill it with meeting notes, then re-run /proposal")
        sys.exit(1)

    # ── Search and download ─────────────────────────────────────────
    print(f"🔍 Searching Google Drive for {args.company} meeting notes...")
    service = get_drive_service()
    file_meta = search_for_notes(service, args.company, args.client)

    if not file_meta:
        print(f"⚠ No meeting notes found in Drive for '{args.company}'.")
        print(f"  Searched folder: {NOTES_FOLDER_ID or '(all folders)'}")
        create_notes_template(args.client, args.company, notes_path)
        print(f"\n📝 Empty notes.md created at: {notes_path}")
        print("  → Fill it with meeting notes, then re-run /proposal")
        sys.exit(1)

    download_file(service, file_meta, notes_path)
    print(f"NOTES_PATH:{notes_path}")
    sys.exit(0)


if __name__ == "__main__":
    main()
