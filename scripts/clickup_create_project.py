#!/usr/bin/env python3
"""Create a ClickUp project (folder + list + tasks) from onboarding SOP."""

import argparse
import re
from pathlib import Path

import requests

from _common import REPO_ROOT, fail, ok, require_env

SOP_PATH = REPO_ROOT / "references" / "onboarding-sop.md"


def parse_sop_tasks(content: str) -> list[str]:
    tasks = []
    for line in content.splitlines():
        m = re.match(r"^\s*-\s*\[\s*\]\s+(.+)$", line)
        if m:
            tasks.append(m.group(1).strip())
    return tasks


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--client", required=True)
    parser.add_argument("--services", required=True)
    args = parser.parse_args()

    env = require_env("CLICKUP_API_TOKEN", "CLICKUP_TEAM_ID", "CLICKUP_SPACE_ID")
    if not SOP_PATH.exists():
        fail(f"Missing {SOP_PATH}")

    tasks = parse_sop_tasks(SOP_PATH.read_text(encoding="utf-8"))
    headers = {"Authorization": env["CLICKUP_API_TOKEN"], "Content-Type": "application/json"}
    team_id = env["CLICKUP_TEAM_ID"]
    space_id = env["CLICKUP_SPACE_ID"]

    folder_resp = requests.post(
        f"https://api.clickup.com/api/v2/space/{space_id}/folder",
        headers=headers,
        json={"name": f"{args.client} — Onboarding"},
        timeout=60,
    )
    if folder_resp.status_code >= 400:
        fail(f"ClickUp folder create failed: {folder_resp.text}")
    folder_id = folder_resp.json()["id"]

    list_resp = requests.post(
        f"https://api.clickup.com/api/v2/folder/{folder_id}/list",
        headers=headers,
        json={"name": "Onboarding checklist"},
        timeout=60,
    )
    if list_resp.status_code >= 400:
        fail(f"ClickUp list create failed: {list_resp.text}")
    list_id = list_resp.json()["id"]

    for task_name in tasks:
        task_resp = requests.post(
            f"https://api.clickup.com/api/v2/list/{list_id}/task",
            headers=headers,
            json={
                "name": task_name,
                "description": f"Services: {args.services}",
            },
            timeout=60,
        )
        if task_resp.status_code >= 400:
            fail(f"ClickUp task create failed: {task_resp.text}")

    url = f"https://app.clickup.com/{team_id}/v/li/{list_id}"
    ok(f"CLICKUP_PROJECT_URL={url}")


if __name__ == "__main__":
    main()
