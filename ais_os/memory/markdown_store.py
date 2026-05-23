"""Markdown file memory — aligns with AIS-OS context/ and memory/notes."""

from __future__ import annotations

import logging
from pathlib import Path

from ais_os.config import get_config

logger = logging.getLogger("ais_os.memory.markdown")


class MarkdownMemoryStore:
    """Read and write interpreted facts as markdown (not raw dumps)."""

    def __init__(self, notes_dir: Path | None = None) -> None:
        cfg = get_config()
        self.notes_dir = notes_dir or cfg.markdown_memory_dir
        self.notes_dir.mkdir(parents=True, exist_ok=True)
        self.workspace = cfg.workspace

    def _safe_path(self, relative: str) -> Path:
        base = self.notes_dir.resolve()
        target = (self.notes_dir / relative).resolve()
        if not str(target).startswith(str(base)):
            raise ValueError("Path escapes memory notes directory")
        return target

    def list_notes(self) -> list[str]:
        return sorted(
            str(p.relative_to(self.notes_dir))
            for p in self.notes_dir.rglob("*.md")
            if p.is_file()
        )

    def read_note(self, name: str) -> str:
        path = self._safe_path(name if name.endswith(".md") else f"{name}.md")
        if not path.exists():
            raise FileNotFoundError(name)
        return path.read_text(encoding="utf-8")

    def write_note(self, name: str, content: str) -> Path:
        path = self._safe_path(name if name.endswith(".md") else f"{name}.md")
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
        logger.info("Wrote memory note: %s", path)
        return path

    def load_context_files(self) -> list[tuple[str, str]]:
        """Load AIS-OS kit context/ + key root files for prompt injection."""
        chunks: list[tuple[str, str]] = []
        context_dir = self.workspace / "context"
        if context_dir.is_dir():
            for md in sorted(context_dir.glob("*.md")):
                chunks.append((f"context/{md.name}", md.read_text(encoding="utf-8")[:8000]))

        for name in ("CLAUDE.md", "connections.md", "aios-intake.md"):
            p = self.workspace / name
            if p.exists():
                chunks.append((name, p.read_text(encoding="utf-8")[:6000]))
        return chunks
