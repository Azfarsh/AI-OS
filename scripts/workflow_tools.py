"""Workflow execution helpers for the voice agent client tools."""

from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

from _common import REPO_ROOT, slugify


def _run_capture(cmd: list[str]) -> tuple[int, str]:
    result = subprocess.run(cmd, cwd=REPO_ROOT, capture_output=True, text=True)
    output = (result.stdout or "") + (result.stderr or "")
    return result.returncode, output.strip()


def _tool_result(**payload: object) -> dict:
    return payload  # type: ignore[return-value]


def list_clients(_params: dict) -> dict:
    path = REPO_ROOT / "context" / "clients.md"
    if not path.exists():
        return _tool_result(status="error", message="context/clients.md not found", spoken_receipt="Client registry not found.")
    lines = [
        line.strip()
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.startswith("|") and "Slug" not in line and "---" not in line
    ]
    count = len(lines)
    return _tool_result(
        status="ok",
        clients=lines,
        spoken_receipt=f"You have {count} client{'s' if count != 1 else ''} in the registry.",
    )


def get_connections(_params: dict) -> dict:
    path = REPO_ROOT / "connections.md"
    rows = []
    connected = 0
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.startswith("|") and "`" in line:
            rows.append(line.strip())
            if "`connected`" in line:
                connected += 1
    return _tool_result(
        status="ok",
        connections=rows,
        spoken_receipt=f"{connected} integration{'s' if connected != 1 else ''} connected and ready.",
    )


def run_report(params: dict) -> dict:
    client_name = params.get("client_name") or params.get("client")
    period = params.get("period")
    if not client_name or not period:
        return _tool_result(status="error", message="Need client_name and period (YYYY-MM)", spoken_receipt="I need a client name and period in YYYY-MM format.")

    cmd = [
        sys.executable,
        "scripts/report_workflow.py",
        "--client-name",
        str(client_name),
        "--period",
        str(period),
    ]
    if params.get("demo", True):
        cmd.append("--demo")
    if params.get("send_email"):
        cmd.append("--send-email")
    if params.get("audio"):
        cmd.append("--audio")

    send_email = bool(params.get("send_email"))
    code, output = _run_capture(cmd)
    if code != 0:
        return _tool_result(status="error", message=output, spoken_receipt="Report failed. Check the logs and try again.")
    md_match = re.search(r"REPORT_COMPLETE=(.+?)(?:\|REPORT_PPTX=|$)", output)
    pptx_match = re.search(r"REPORT_PPTX=(.+)", output)
    receipt = f"Report complete for {client_name}, period {period}. Branded PPTX is ready."
    if send_email:
        receipt += " Email sent to the client."
    if params.get("audio"):
        receipt += " Audio summary generated."
    return _tool_result(
        status="ok",
        message=f"Report generated for {client_name}, period {period}.",
        report_path=md_match.group(1).strip() if md_match else output,
        report_pptx_path=pptx_match.group(1).strip() if pptx_match else None,
        spoken_receipt=receipt,
    )


def run_onboard_client(params: dict) -> dict:
    required = ["client_name", "email", "services", "budget"]
    missing = [k for k in required if not params.get(k)]
    if missing:
        return {"status": "error", "message": f"Missing: {', '.join(missing)}"}

    slug = slugify(str(params["client_name"]))
    client_dir = REPO_ROOT / "clients" / slug
    client_dir.mkdir(parents=True, exist_ok=True)
    (client_dir / "proposals").mkdir(exist_ok=True)
    (client_dir / "reports").mkdir(exist_ok=True)
    (client_dir / "contracts").mkdir(exist_ok=True)
    (client_dir / "fixtures").mkdir(exist_ok=True)

    brief_path = client_dir / "client-brief.md"
    if not brief_path.exists():
        brief = f"""# {params['client_name']} — client brief

**Primary contact:** {params['email']}
**Services:** {params['services']}
**Monthly budget:** ${params['budget']}

## Platforms

| Platform | Account ID |
|----------|------------|
"""
        services = str(params["services"]).lower()
        if "meta" in services:
            brief += "| Meta Ads | TBD |\n"
        if "google" in services:
            brief += "| Google Ads | TBD |\n"
        brief_path.write_text(brief, encoding="utf-8")

    if not (client_dir / "notes.md").exists():
        (client_dir / "notes.md").write_text(f"# {params['client_name']} — notes\n", encoding="utf-8")

    registry = REPO_ROOT / "context" / "clients.md"
    text = registry.read_text(encoding="utf-8")
    if slug not in text:
        from datetime import date

        row = (
            f"| {date.today().isoformat()} | {params['client_name']} | {slug} | "
            f"{params['services']} | ${params['budget']} | active |\n"
        )
        registry.write_text(text.rstrip() + "\n" + row, encoding="utf-8")

    contract_cmd = [
        sys.executable,
        "scripts/generate_contract.py",
        "--client-name",
        str(params["client_name"]),
        "--client-email",
        str(params["email"]),
        "--client-city",
        str(params.get("city", "Dubai")),
        "--client-country",
        str(params.get("country", "UAE")),
        "--client-contact",
        str(params.get("contact", params["client_name"])),
        "--services",
        str(params["services"]),
        "--monthly-retainer",
        str(params["budget"]),
    ]
    code, output = _run_capture(contract_cmd)
    if code != 0:
        return _tool_result(
            status="error",
            message=f"Contract generation failed: {output}",
            slug=slug,
            spoken_receipt=f"Onboarding failed for {params['client_name']}. Contract step did not complete.",
        )

    contract_match = re.search(r"CONTRACT_PATH:(.+)", output)
    name = params["client_name"]
    return _tool_result(
        status="ok",
        message=f"Client {name} ready at clients/{slug}/",
        slug=slug,
        contract_path=contract_match.group(1).strip() if contract_match else None,
        spoken_receipt=(
            f"Onboarding complete for {name}. Client folder, brief, registry entry, and contract PPTX are ready."
        ),
    )


def run_proposal(params: dict) -> dict:
    client_name = params.get("client_name") or params.get("name")
    company = params.get("company") or client_name
    email = params.get("email")
    if not client_name or not company or not email:
        return {"status": "error", "message": "Need client_name, company, and email"}

    slug = slugify(str(company))
    cmd = [
        sys.executable,
        "scripts/generate_proposal.py",
        "--client-name",
        str(client_name),
        "--company",
        str(company),
        "--client-email",
        str(email),
        "--slug",
        slug,
    ]
    if params.get("budget"):
        cmd.extend(["--budget", str(params["budget"])])
    if params.get("services"):
        cmd.extend(["--services", str(params["services"])])
    if params.get("pain_points"):
        cmd.extend(["--pain-points", str(params["pain_points"])])
    code, output = _run_capture(cmd)
    if code != 0:
        return _tool_result(status="error", message=output, spoken_receipt=f"Proposal failed for {company}.")
    proposal_match = re.search(r"PROPOSAL_PATH:(.+)", output)
    return _tool_result(
        status="ok",
        message=f"Proposal generated for {company}.",
        proposal_path=proposal_match.group(1).strip() if proposal_match else None,
        output=output,
        spoken_receipt=f"Proposal ready for {company}. Branded PPTX saved to the client folder.",
    )


TOOL_REGISTRY = {
    "run_report": run_report,
    "run_onboard_client": run_onboard_client,
    "run_proposal": run_proposal,
    "list_clients": list_clients,
    "get_connections": get_connections,
}


def execute_tool(name: str, params: dict | None = None) -> dict:
    if name not in TOOL_REGISTRY:
        return _tool_result(status="error", message=f"Unknown tool: {name}", spoken_receipt="That workflow is not available.")
    return TOOL_REGISTRY[name](params or {})
