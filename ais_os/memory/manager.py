"""Unified memory facade: short-term, sessions, vectors, markdown, project context."""

from __future__ import annotations

import logging
from typing import Any

from ais_os.config import get_config
from ais_os.memory.markdown_store import MarkdownMemoryStore
from ais_os.memory.session_store import SessionStore
from ais_os.memory.short_term import ShortTermMemory
from ais_os.memory.vector_store import VectorMemoryStore

logger = logging.getLogger("ais_os.memory.manager")


class MemoryManager:
    def __init__(self) -> None:
        cfg = get_config()
        mem = cfg.memory_settings
        self.short_term = ShortTermMemory(
            max_messages=int(mem.get("short_term_max_messages", 40))
        )
        self.sessions = SessionStore()
        self.markdown = MarkdownMemoryStore()
        self.vectors = VectorMemoryStore()
        self._top_k = int(mem.get("retrieval_top_k", 6))

    async def remember(self, text: str, *, source: str = "conversation") -> str:
        doc_id = await self.vectors.add(text, metadata={"source": source})
        logger.debug("Stored vector memory %s", doc_id)
        return doc_id

    async def recall(self, query: str, top_k: int | None = None) -> list[dict[str, Any]]:
        return await self.vectors.search(query, top_k=top_k or self._top_k)

    def build_system_context(self) -> str:
        """Assemble AIS-OS Context layer (Four Cs) for prompts."""
        parts: list[str] = []
        for path, content in self.markdown.load_context_files():
            parts.append(f"### {path}\n{content.strip()}")
        notes = self.markdown.list_notes()[:12]
        mem_root = self.markdown.notes_dir.parent
        for note in notes:
            try:
                path = mem_root / note
                if path.is_file():
                    body = path.read_text(encoding="utf-8")
                else:
                    body = self.markdown.read_note(note)
                parts.append(f"### memory/{note}\n{body.strip()[:2000]}")
            except (OSError, FileNotFoundError, ValueError):
                continue
        return "\n\n".join(parts) if parts else "(No context files yet — run /onboard in Claude Code or fill context/)"

    async def build_retrieval_block(self, user_message: str) -> str:
        hits = await self.recall(user_message)
        if not hits:
            return ""
        lines = ["## Retrieved memory"]
        for h in hits:
            lines.append(f"- {h['text'][:500]}")
        return "\n".join(lines)
