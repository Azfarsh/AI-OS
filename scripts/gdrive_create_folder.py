#!/usr/bin/env python3
"""
gdrive_create_folder.py — Bombay Media Google Drive Folder Creator
Creates the standard folder structure for a new client.

FREE TIER: Works with any Google account + Google Cloud free tier.
Setup:
  1. Go to console.cloud.google.com
  2. Create project → Enable "Google Drive API"
  3. Create Service Account → Download JSON key
  4. Share your root Drive folder with the service account email
  5. Set GOOGLE_SERVICE_ACCOUNT_JSON_PATH in .env

Usage:
    python scripts/gdrive_create_folder.py --client "acme-coaching"
"""

import argparse
import json
import os
import sys
from pathlib import Path

try:
    from dotenv import load_dotenv
    from googleapiclient.discovery import build
    from google.oauth2.service_account import Credentials
except ImportError:
    print("ERROR: Missing packages. Run: pip install google-api-python-client google-auth python-dotenv")
    sys.exit(1)

REPO_ROOT = Path(__file__).resolve().parent.parent
load_dotenv(REPO_ROOT / ".env")

SERVICE_ACCOUNT_PATH = os.getenv("GOOGLE_SERVICE_ACCOUNT_JSON_PATH")
ROOT_FOLDER_ID       = os.getenv("GOOGLE_DRIVE_ROOT_FOLDER_ID")
AGENCY_NAME          = os.getenv("AGENCY_NAME", "Bombay Media")

SCOPES = ["https://www.googleapis.com/auth/drive"]

# Folder structure per onboarding-sop.md
SUBFOLDERS = ["Reports", "Assets", "Contracts", "Creative"]
ASSET_SUBFOLDERS = ["Brand Assets", "Ad Creatives"]


def get_drive_service():
    if not SERVICE_ACCOUNT_PATH:
        print("ERROR: GOOGLE_SERVICE_ACCOUNT_JSON_PATH not set in .env")
        sys.exit(1)
    creds = Credentials.from_service_account_file(SERVICE_ACCOUNT_PATH, scopes=SCOPES)
    return build("drive", "v3", credentials=creds)


def create_folder(service, name: str, parent_id: str) -> str:
    """Create a folder and return its ID."""
    metadata = {
        "name": name,
        "mimeType": "application/vnd.google-apps.folder",
        "parents": [parent_id],
    }
    folder = service.files().create(body=metadata, fields="id, webViewLink").execute()
    folder_id = folder["id"]
    link = folder.get("webViewLink", "")
    print(f"  ✓ Created: {name} → {link}")
    return folder_id


def client_display_name(slug: str) -> str:
    """Convert 'acme-coaching' → 'Acme Coaching'"""
    return " ".join(word.capitalize() for word in slug.split("-"))


def main():
    parser = argparse.ArgumentParser(description="Bombay Media — Google Drive Folder Creator")
    parser.add_argument("--client", required=True, help="Client slug, e.g. 'acme-coaching'")
    args = parser.parse_args()

    if not ROOT_FOLDER_ID:
        print("ERROR: GOOGLE_DRIVE_ROOT_FOLDER_ID not set in .env")
        print("  → Share your 'Bombay Media' root Drive folder with the service account,")
        print("    then paste its folder ID here.")
        sys.exit(1)

    client_name = client_display_name(args.client)
    service = get_drive_service()

    print(f"Creating Drive structure for: {client_name}")

    # Create top-level client folder under root
    client_folder_id = create_folder(service, client_name, ROOT_FOLDER_ID)

    # Create standard subfolders
    assets_folder_id = None
    for subfolder in SUBFOLDERS:
        fid = create_folder(service, subfolder, client_folder_id)
        if subfolder == "Assets":
            assets_folder_id = fid

    # Create sub-subfolders inside Assets
    if assets_folder_id:
        for sub in ASSET_SUBFOLDERS:
            create_folder(service, sub, assets_folder_id)

    # Get shareable link for the client folder
    file_meta = service.files().get(fileId=client_folder_id, fields="webViewLink").execute()
    drive_url = file_meta.get("webViewLink", "")

    print(f"\n✓ Google Drive structure ready for: {client_name}")
    print(f"DRIVE_URL:{drive_url}")


if __name__ == "__main__":
    main()
