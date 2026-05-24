"""CLI: Agency lead pipeline commands."""

from __future__ import annotations

import json
from pathlib import Path

import typer
from rich.console import Console
from rich.table import Table

from ais_os.skills.deduplicate_lead import leads_dir
from ais_os.skills.lead_schema import LeadInput
from ais_os.skills.qualify_lead import get_threshold
from ais_os.workflows.lead_pipeline import run_lead_pipeline

lead_app = typer.Typer(help="Agency OS — Loop 1 lead acquisition pipeline")
console = Console()


@lead_app.command("run")
def lead_run(
    file: Path = typer.Option(
        Path("fixtures/sample_leads.json"),
        "--file",
        "-f",
        help="JSON array of leads",
    ),
    threshold: int | None = typer.Option(None, "--threshold", "-t", help="Qualification threshold"),
) -> None:
    """Score, qualify, and write leads to memory/leads/ (Loop 1)."""
    import asyncio

    if not file.exists():
        raise typer.BadParameter(f"File not found: {file}")

    raw = json.loads(file.read_text(encoding="utf-8"))
    if not isinstance(raw, list):
        raw = [raw]

    async def _process() -> None:
        table = Table(title="Lead pipeline results")
        table.add_column("Lead")
        table.add_column("Status")
        table.add_column("Fit")
        table.add_column("Intent")
        table.add_column("Message")

        for item in raw:
            lead = LeadInput.model_validate(item)
            result = await run_lead_pipeline(lead, threshold=threshold)
            fit = str(result.scores.fit_score) if result.scores else "—"
            intent = str(result.scores.intent_score) if result.scores else "—"
            table.add_row(lead.slug(), result.status, fit, intent, result.message[:80])
        console.print(table)
        console.print(f"\nThreshold: {threshold or get_threshold()}")
        console.print("Lead files: memory/leads/")
        console.print("Pipeline board: memory/context/active_pipeline.md")

    asyncio.run(_process())


@lead_app.command("list")
def lead_list() -> None:
    """List lead memory files."""
    directory = leads_dir()
    if not directory.is_dir():
        console.print("[dim]No leads yet. Run: ais lead run[/]")
        return
    table = Table(title="Leads in memory/leads/")
    table.add_column("File")
    for path in sorted(directory.glob("*.md")):
        table.add_row(path.name)
    console.print(table)


@lead_app.command("show")
def lead_show(slug: str = typer.Argument(..., help="Lead file slug without .md")) -> None:
    """Print a lead memory file."""
    path = leads_dir() / (slug if slug.endswith(".md") else f"{slug}.md")
    if not path.exists():
        raise typer.BadParameter(f"Not found: {path}")
    console.print(path.read_text(encoding="utf-8"))


@lead_app.command("chat")
def lead_chat(
    message: str = typer.Argument(..., help="Ask about leads / pipeline"),
) -> None:
    """Chat with executive agent using lead memory context."""
    import asyncio

    from ais_os.memory.manager import MemoryManager
    from ais_os.orchestrator.graph import Orchestrator
    from ais_os.terminal import ui

    async def _run() -> None:
        mem = MemoryManager()
        orch = Orchestrator()
        context = mem.build_system_context()
        memory_block = await mem.build_retrieval_block(message)
        result = await orch.run(
            message,
            context=context,
            memory_block=memory_block,
            agent_id="executive_agent",
        )
        ui.print_agent_feed(result["agent_id"], result["model"])
        ui.print_markdown(result["response"])

    asyncio.run(_run())
