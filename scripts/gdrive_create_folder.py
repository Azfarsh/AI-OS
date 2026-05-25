#!/usr/bin/env python3
"""Create Google Drive client folder tree under agency root."""

import argparse
from pathlib import Path

from google.oauth2 import service_account
from googleapiclient.discovery import build

from _common import fail, ok, require_env

SUBFOLDERS = ("Reports", "Assets", "Contracts", "Creative")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--client", required=True, help="Client slug")
    parser.add_argument("--display-name", default=None, help="Human-readable client name")
    args = parser.parse_args()

    env = require_env(
        "GOOGLE_SERVICE_ACCOUNT_JSON_PATH",
        "GOOGLE_DRIVE_ROOT_FOLDER_ID",
        "AGENCY_NAME",
    )
    sa_path = Path(env["GOOGLE_SERVICE_ACCOUNT_JSON_PATH"])
    if not sa_path.exists():
        fail(f"Service account file not found: {sa_path}")

    display = args.display_name or args.client.replace("-", " ").title()
    creds = service_account.Credentials.from_service_account_file(
        str(sa_path),
        scopes=["https://www.googleapis.com/auth/drive"],
    )
    drive = build("drive", "v3", credentials=creds, cache_discovery=False)
    root_id = env["GOOGLE_DRIVE_ROOT_FOLDER_ID"]

    def mkdir(name: str, parent: str) -> str:
        meta = {"name": name, "mimeType": "application/vnd.google-apps.folder", "parents": [parent]}
        created = drive.files().create(body=meta, fields="id, webViewLink").execute()
        return created["id"]

    agency = env["AGENCY_NAME"]
    agency_parent = mkdir(agency, root_id)
    clients_parent = mkdir("Clients", agency_parent)
    client_root = mkdir(display, clients_parent)
    for sub in SUBFOLDERS:
        mkdir(sub, client_root)

    folder = drive.files().get(fileId=client_root, fields="webViewLink").execute()
    ok(f"GDRIVE_FOLDER_URL={folder.get('webViewLink', client_root)}")


if __name__ == "__main__":
    main()
