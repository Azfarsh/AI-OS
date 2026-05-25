#!/usr/bin/env python3
"""Send contract for signature via DocuSeal."""

import argparse
from pathlib import Path

import requests

from _common import REPO_ROOT, fail, ok, require_env


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--client-email", required=True)
    parser.add_argument("--contract-path", required=True)
    args = parser.parse_args()

    env = require_env("DOCUSEAL_API_TOKEN", "DOCUSEAL_TEMPLATE_ID")
    contract_path = Path(args.contract_path)
    if not contract_path.is_absolute():
        contract_path = REPO_ROOT / contract_path
    if not contract_path.exists():
        fail(f"Contract not found: {contract_path}")

    body_text = contract_path.read_text(encoding="utf-8")
    payload = {
        "template_id": int(env["DOCUSEAL_TEMPLATE_ID"]),
        "send_email": True,
        "submitters": [{"email": args.client_email, "role": "Client"}],
        "fields": [{"name": "contract_body", "default_value": body_text}],
    }
    resp = requests.post(
        "https://api.docuseal.com/submissions",
        headers={
            "X-Auth-Token": env["DOCUSEAL_API_TOKEN"],
            "Content-Type": "application/json",
        },
        json=payload,
        timeout=60,
    )
    if resp.status_code >= 400:
        fail(f"DocuSeal submission failed: {resp.text}")

    data = resp.json()
    submission_id = data[0]["id"] if isinstance(data, list) else data.get("id", "unknown")
    ok(f"DOCUSEAL_SUBMISSION_ID={submission_id}")


if __name__ == "__main__":
    main()
