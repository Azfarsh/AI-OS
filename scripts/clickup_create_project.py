#!/usr/bin/env python3
"""
clickup_create_project.py — Bombay Media ClickUp Project Creator
Creates a ClickUp project (list structure) for a new client based on onboarding-sop.md

Usage:
    python scripts/clickup_create_project.py \
        --client "Acme Coaching" \
        --services "meta,content"
"""

import argparse
import json
import os
import sys
from pathlib import Path

try:
    import requests
    from dotenv import load_dotenv
except ImportError:
    print("ERROR: Missing packages. Run: pip install requests python-dotenv")
    sys.exit(1)

REPO_ROOT = Path(__file__).resolve().parent.parent
load_dotenv(REPO_ROOT / ".env")

CLICKUP_API_TOKEN = os.getenv("CLICKUP_API_TOKEN")
CLICKUP_SPACE_ID  = os.getenv("CLICKUP_SPACE_ID")
BASE_URL = "https://api.clickup.com/api/v2"
HEADERS = {
    "Authorization": CLICKUP_API_TOKEN,
    "Content-Type": "application/json"
}

# Tasks to create per list, from onboarding-sop.md
ONBOARDING_TASKS = [
    "Create client folder in repo",
    "Write client-brief.md",
    "Create Google Drive folder structure",
    "Send contract via DocuSeal / email",
    "Schedule kickoff call with Farhan",
    "Gather brand assets from client",
    "Audit existing Meta Ads account",
    "Set up reporting access",
]

META_ADS_TASKS = [
    "Campaign Setup",
    "Audience Research & Targeting",
    "Creative Testing — Week 1",
    "Weekly ROAS Dashboard Setup",
    "Weekly Reporting — Ongoing",
]

CONTENT_TASKS = [
    "Monthly Content Calendar — Month 1",
    "Ad Creative Production — Batch 1",
    "Copy Review & Approval",
]

STRATEGY_TASKS = [
    "Initial Funnel Audit",
    "A/B Test Plan",
    "Monthly Performance Review — Month 1",
]


def find_folder(space_id: str, client_name: str) -> str | None:
    """Return existing folder ID if the client folder already exists."""
    url = f"{BASE_URL}/space/{space_id}/folder"
    r = requests.get(url, headers=HEADERS)
    r.raise_for_status()
    for folder in r.json().get("folders", []):
        if folder.get("name") == client_name:
            return folder["id"]
    return None


def create_folder(space_id: str, client_name: str) -> str:
    """Create a folder (project) for the client inside the space."""
    existing = find_folder(space_id, client_name)
    if existing:
        print(f"✓ ClickUp folder already exists: {client_name} (ID: {existing})")
        return existing

    url = f"{BASE_URL}/space/{space_id}/folder"
    payload = {"name": client_name}
    r = requests.post(url, headers=HEADERS, json=payload)
    r.raise_for_status()
    folder_id = r.json()["id"]
    print(f"✓ ClickUp folder created: {client_name} (ID: {folder_id})")
    return folder_id


def create_list(folder_id: str, list_name: str) -> str:
    """Create a list inside a folder."""
    url = f"{BASE_URL}/folder/{folder_id}/list"
    payload = {"name": list_name}
    r = requests.post(url, headers=HEADERS, json=payload)
    r.raise_for_status()
    list_id = r.json()["id"]
    print(f"  ✓ List created: {list_name} (ID: {list_id})")
    return list_id


def create_task(list_id: str, task_name: str) -> str:
    """Create a task inside a list."""
    url = f"{BASE_URL}/list/{list_id}/task"
    payload = {"name": task_name, "status": "Open"}
    r = requests.post(url, headers=HEADERS, json=payload)
    r.raise_for_status()
    task_id = r.json()["id"]
    return task_id


def main():
    parser = argparse.ArgumentParser(description="Bombay Media — ClickUp Project Creator")
    parser.add_argument("--client",   required=True, help="Client name, e.g. 'Acme Coaching'")
    parser.add_argument("--services", required=True, help="Comma-separated: meta,content,google,seo")
    args = parser.parse_args()

    if not CLICKUP_API_TOKEN or not CLICKUP_SPACE_ID:
        print("ERROR: CLICKUP_API_TOKEN and CLICKUP_SPACE_ID must be set in .env")
        sys.exit(1)

    services = [s.strip() for s in args.services.split(",")]

    # Create folder for the client
    folder_id = create_folder(CLICKUP_SPACE_ID, args.client)

    # Always create Onboarding list
    onboarding_list_id = create_list(folder_id, "Onboarding")
    for task in ONBOARDING_TASKS:
        create_task(onboarding_list_id, task)
    print(f"    ✓ {len(ONBOARDING_TASKS)} onboarding tasks created")

    # Meta Ads list
    if "meta" in services or "google" in services:
        meta_list_id = create_list(folder_id, "Meta Ads")
        for task in META_ADS_TASKS:
            create_task(meta_list_id, task)
        print(f"    ✓ {len(META_ADS_TASKS)} Meta Ads tasks created")

    # Content Marketing list
    if "content" in services:
        content_list_id = create_list(folder_id, "Content Marketing")
        for task in CONTENT_TASKS:
            create_task(content_list_id, task)
        print(f"    ✓ {len(CONTENT_TASKS)} content tasks created")

    # Strategy list (always)
    strategy_list_id = create_list(folder_id, "Strategy")
    for task in STRATEGY_TASKS:
        create_task(strategy_list_id, task)
    print(f"    ✓ {len(STRATEGY_TASKS)} strategy tasks created")

    project_url = f"https://app.clickup.com/{os.getenv('CLICKUP_TEAM_ID')}/v/f/{folder_id}"
    print(f"\n✓ ClickUp project ready: {args.client}")
    print(f"CLICKUP_URL:{project_url}")


if __name__ == "__main__":
    main()
