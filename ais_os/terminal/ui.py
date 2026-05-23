"""Rich terminal UI components."""

from __future__ import annotations

from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

console = Console()


def print_banner() -> None:
    console.print(
        Panel.fit(
            "[bold cyan]AIS-OS[/] — Terminal AI Operating System\n"
            "[dim]Context · Connections · Capabilities · Cadence[/]\n"
            "Type [bold]/help[/] for commands · [bold]/chat[/] to talk · [bold]exit[/] to quit",
            border_style="cyan",
        )
    )


def print_agent_feed(agent_id: str, model: str) -> None:
    console.print(f"[dim]agent[/] [yellow]{agent_id}[/]  [dim]model[/] [magenta]{model}[/]")


def stream_markdown_start() -> None:
    console.print("[bold green]Assistant[/]")


def print_markdown(content: str) -> None:
    console.print(Markdown(content))


def print_error(message: str) -> None:
    console.print(f"[bold red]Error:[/] {message}")


def print_success(message: str) -> None:
    console.print(f"[bold green]✓[/] {message}")


def agents_table(rows: list[dict[str, str]]) -> None:
    table = Table(title="AIS-OS Agents", show_header=True, header_style="bold cyan")
    table.add_column("ID", style="yellow")
    table.add_column("Name")
    table.add_column("Description", max_width=60)
    for r in rows:
        table.add_row(r["id"], r["name"], r["description"])
    console.print(table)


def sessions_table(rows: list[dict[str, str]]) -> None:
    table = Table(title="Chat Sessions")
    table.add_column("ID", style="cyan")
    table.add_column("Title")
    table.add_column("Updated")
    for r in rows:
        table.add_row(r["id"], r["title"], r.get("updated_at", ""))
    console.print(table)


def settings_panel(cfg_text: str) -> None:
    console.print(Panel(cfg_text, title="Settings", border_style="blue"))


def help_text() -> Text:
    lines = [
        "/chat [message]     — conversational assistant (default)",
        "/agents             — list all agents",
        "/memory [query]     — search vector memory",
        "/memory save <text> — store in long-term memory",
        "/browser <task>     — browser agent (playbook; Phase 3 live)",
        "/research <query>   — research agent",
        "/code <task>        — coding agent",
        "/outreach <task>    — outreach agent",
        "/deploy <task>      — deployment agent",
        "/settings           — show configuration",
        "/voice              — voice mode (Phase 2)",
        "/help               — this help",
        "",
        "Prefix with agent:  @coding_agent fix the login bug",
        "Model override:     /model anthropic/claude-3.5-sonnet",
        "Plain text (no /)  — same as /chat",
    ]
    return Text("\n".join(lines))
