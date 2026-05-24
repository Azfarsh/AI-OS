"""Typer CLI entry point."""

from __future__ import annotations

import typer
from rich.console import Console

from ais_os.cli_lead import lead_app
from ais_os.config import get_config
from ais_os.logging_setup import setup_logging

app = typer.Typer(
    name="ais",
    help="AIS-OS — Terminal-first AI Operating System",
    no_args_is_help=False,
)
console = Console()

app.add_typer(lead_app, name="lead")


@app.callback(invoke_without_command=True)
def main(ctx: typer.Context) -> None:
    """Launch interactive terminal when no subcommand given."""
    if ctx.invoked_subcommand is None:
        from ais_os.terminal.repl import TerminalREPL

        TerminalREPL().run()


@app.command("chat")
def chat(
    message: str = typer.Argument(..., help="Message to send"),
    agent: str | None = typer.Option(None, "--agent", "-a", help="Force agent id"),
    model: str | None = typer.Option(None, "--model", "-m", help="Model override"),
) -> None:
    """Single-shot chat (non-interactive)."""
    import asyncio

    setup_logging()
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
            agent_id=agent,
            model_override=model,
        )
        ui.print_agent_feed(result["agent_id"], result["model"])
        ui.print_markdown(result["response"])

    asyncio.run(_run())


@app.command("agents")
def agents_list() -> None:
    """List registered agents."""
    from ais_os.agents.registry import get_agent_registry
    from ais_os.terminal import ui

    ui.agents_table(get_agent_registry().list_agents())


@app.command("memory")
def memory_search(
    query: str = typer.Argument(..., help="Search query"),
    top_k: int = typer.Option(6, "--top-k", "-k"),
) -> None:
    """Search long-term vector memory."""
    import asyncio

    from ais_os.memory.manager import MemoryManager

    async def _run() -> None:
        mem = MemoryManager()
        hits = await mem.recall(query, top_k=top_k)
        if not hits:
            console.print("[dim]No results.[/]")
            return
        for h in hits:
            console.print(f"• ({h.get('distance', 0):.3f}) {h['text'][:500]}")

    asyncio.run(_run())


@app.command("memory-save")
def memory_save(text: str = typer.Argument(..., help="Text to store in vector memory")) -> None:
    """Save text to long-term vector memory."""
    import asyncio

    from ais_os.memory.manager import MemoryManager

    async def _run() -> None:
        mem = MemoryManager()
        doc_id = await mem.remember(text, source="cli")
        console.print(f"[green]Stored[/] memory id: {doc_id}")

    asyncio.run(_run())


@app.command("sessions")
def sessions_list() -> None:
    """List saved chat sessions."""
    from ais_os.memory.manager import MemoryManager
    from ais_os.terminal import ui

    mem = MemoryManager()
    ui.sessions_table(mem.sessions.list_sessions())


@app.command("config")
def show_config() -> None:
    """Print effective configuration."""
    cfg = get_config()
    console.print(f"Profile: {cfg.config_profile}")
    console.print(f"Free models: {cfg.use_free_models}")
    console.print(f"Workspace: {cfg.workspace}")
    console.print(f"Default model: {cfg.default_model}")
    console.print(f"Embeddings: {cfg.embed_provider}")
    console.print(f"OpenRouter: {cfg.openrouter_base_url}")
    console.print(f"API key: {'set' if cfg.openrouter_api_key else 'MISSING'}")


if __name__ == "__main__":
    app()
