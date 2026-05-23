"""Slash command handlers."""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Awaitable, Callable

from ais_os.agents.registry import get_agent_registry
from ais_os.config import get_config
from ais_os.memory.manager import MemoryManager
from ais_os.orchestrator.graph import Orchestrator
from ais_os.terminal import ui

CommandHandler = Callable[[str, "CommandContext"], Awaitable[str | None]]


@dataclass
class CommandContext:
    memory: MemoryManager
    orchestrator: Orchestrator
    session_id: str
    model_override: str | None = None
    last_agent: str = ""
    last_model: str = ""


class CommandRouter:
    def __init__(self) -> None:
        self._handlers: dict[str, CommandHandler] = {
            "help": self._help,
            "chat": self._chat,
            "agents": self._agents,
            "memory": self._memory,
            "browser": self._agent_cmd("browser_agent"),
            "research": self._agent_cmd("research_agent"),
            "code": self._agent_cmd("coding_agent"),
            "outreach": self._agent_cmd("outreach_agent"),
            "deploy": self._agent_cmd("deployment_agent"),
            "settings": self._settings,
            "voice": self._voice,
            "model": self._model,
        }

    async def dispatch(self, line: str, ctx: CommandContext) -> tuple[bool, str | None]:
        """Returns (handled, response). response None means use default chat."""
        line = line.strip()
        if not line.startswith("/"):
            return False, None

        parts = line[1:].split(maxsplit=1)
        cmd = parts[0].lower()
        arg = parts[1] if len(parts) > 1 else ""

        handler = self._handlers.get(cmd)
        if not handler:
            ui.print_error(f"Unknown command: /{cmd}. Try /help")
            return True, None

        if cmd == "model":
            result = await handler(arg, ctx)
            return True, result

        if callable(handler) and cmd in ("browser", "research", "code", "outreach", "deploy"):
            return True, await handler(arg, ctx)

        return True, await handler(arg, ctx)

    async def _help(self, _arg: str, _ctx: CommandContext) -> str | None:
        ui.console.print(ui.help_text())
        return None

    async def _agents(self, _arg: str, _ctx: CommandContext) -> str | None:
        ui.agents_table(get_agent_registry().list_agents())
        return None

    async def _settings(self, _arg: str, ctx: CommandContext) -> str | None:
        cfg = get_config()
        text = (
            f"Workspace: {cfg.workspace}\n"
            f"Default model: {cfg.default_model}\n"
            f"OpenRouter key: {'set' if cfg.openrouter_api_key else 'MISSING'}\n"
            f"Session: {ctx.session_id}\n"
            f"Chroma vectors: {ctx.memory.vectors.count()}\n"
            f"Permissions: {cfg.agent_permissions}"
        )
        ui.settings_panel(text)
        return None

    async def _voice(self, _arg: str, _ctx: CommandContext) -> str | None:
        ui.print_error(
            "Voice Jarvis mode ships in Phase 2 (ElevenLabs + Whisper). "
            "Set voice.enabled in configs/default.yaml when ready."
        )
        return None

    async def _model(self, arg: str, ctx: CommandContext) -> str | None:
        if arg.strip():
            ctx.model_override = arg.strip()
            ui.print_success(f"Model override: {ctx.model_override}")
        else:
            ctx.model_override = None
            ui.print_success("Model override cleared")
        return None

    async def _memory(self, arg: str, ctx: CommandContext) -> str | None:
        if arg.lower().startswith("save "):
            text = arg[5:].strip()
            if not text:
                ui.print_error("Usage: /memory save <text>")
                return None
            doc_id = await ctx.memory.remember(text, source="slash_command")
            ui.print_success(f"Stored memory: {doc_id}")
            return None
        query = arg or "recent priorities"
        hits = await ctx.memory.recall(query)
        if not hits:
            ui.console.print("[dim]No matching memories.[/]")
            return None
        for h in hits:
            ui.console.print(f"• {h['text'][:400]}")
        return None

    async def _chat(self, arg: str, ctx: CommandContext) -> str | None:
        if not arg:
            ui.print_error("Usage: /chat <message>")
            return None
        return await self._run_orchestrator(arg, ctx, agent_id=None)

    def _agent_cmd(self, agent_id: str) -> CommandHandler:
        async def handler(arg: str, ctx: CommandContext) -> str | None:
            if not arg:
                ui.print_error(f"Provide a task for {agent_id}")
                return None
            return await self._run_orchestrator(arg, ctx, agent_id=agent_id)

        return handler

    async def _run_orchestrator(
        self,
        message: str,
        ctx: CommandContext,
        *,
        agent_id: str | None,
    ) -> str:
        context = ctx.memory.build_system_context()
        memory_block = await ctx.memory.build_retrieval_block(message)
        result = await ctx.orchestrator.run(
            message,
            context=context,
            memory_block=memory_block,
            agent_id=agent_id,
            model_override=ctx.model_override,
        )
        ctx.last_agent = result.get("agent_id", "")
        ctx.last_model = result.get("model", "")
        ui.print_agent_feed(ctx.last_agent, ctx.last_model)
        response = result.get("response", "")
        ctx.memory.short_term.add("user", message)
        ctx.memory.short_term.add("assistant", response)
        await ctx.memory.remember(f"Q: {message}\nA: {response[:500]}", source="session")
        return response


_AGENT_MENTION = re.compile(r"^@(\w+)\s+", re.I)


class MessageParser:
    @staticmethod
    def parse(line: str) -> tuple[str | None, str]:
        m = _AGENT_MENTION.match(line)
        if m:
            return m.group(1).lower(), line[m.end() :].strip()
        return None, line
