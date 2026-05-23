"""Interactive terminal REPL."""

from __future__ import annotations

import asyncio
import logging

from ais_os.config import get_config
from ais_os.logging_setup import setup_logging
from ais_os.memory.manager import MemoryManager
from ais_os.models.openrouter import OpenRouterClient
from ais_os.models.router import ModelRouter
from ais_os.orchestrator.graph import Orchestrator
from ais_os.terminal import ui
from ais_os.terminal.commands import CommandContext, CommandRouter, MessageParser

logger = logging.getLogger("ais_os.terminal.repl")


class TerminalREPL:
    def __init__(self) -> None:
        setup_logging()
        self.cfg = get_config()
        self.memory = MemoryManager()
        self.orchestrator = Orchestrator()
        self.commands = CommandRouter()
        self.llm = OpenRouterClient()
        self.model_router = ModelRouter()
        self.session_id = self.memory.sessions.create_session("Terminal session")
        self.ctx = CommandContext(
            memory=self.memory,
            orchestrator=self.orchestrator,
            session_id=self.session_id,
        )

    async def run_async(self) -> None:
        if not self.cfg.openrouter_api_key:
            ui.print_error(
                "OPENROUTER_API_KEY not set. Copy .env.example to .env and add your key."
            )

        ui.print_banner()
        ui.print_success(f"Session {self.session_id} started")

        while True:
            try:
                line = await asyncio.to_thread(input, "ais> ")
            except (EOFError, KeyboardInterrupt):
                ui.console.print("\n[dim]Goodbye.[/]")
                break

            line = line.strip()
            if not line:
                continue
            if line.lower() in ("exit", "quit", "/exit", "/quit"):
                ui.console.print("[dim]Goodbye.[/]")
                break

            try:
                await self._handle_line(line)
            except Exception as exc:
                logger.exception("REPL error")
                ui.print_error(str(exc))

    async def _handle_line(self, line: str) -> None:
        handled, response = await self.commands.dispatch(line, self.ctx)
        if handled:
            if response:
                ui.print_markdown(response)
            return

        agent_override, message = MessageParser.parse(line)
        if not message:
            return

        if line.startswith("/"):
            return

        # Default: chat with optional @agent
        result = await self.commands._run_orchestrator(
            message,
            self.ctx,
            agent_id=agent_override,
        )
        ui.print_markdown(result)

    def run(self) -> None:
        asyncio.run(self.run_async())
