"""In-process short-term conversation buffer."""

from __future__ import annotations

from collections import deque
from dataclasses import dataclass, field
from typing import Any


@dataclass
class ShortTermMemory:
    max_messages: int = 40
    _messages: deque[dict[str, str]] = field(default_factory=deque)

    def add(self, role: str, content: str) -> None:
        self._messages.append({"role": role, "content": content})
        while len(self._messages) > self.max_messages:
            self._messages.popleft()

    def get_messages(self) -> list[dict[str, str]]:
        return list(self._messages)

    def clear(self) -> None:
        self._messages.clear()

    def to_dict(self) -> dict[str, Any]:
        return {"max_messages": self.max_messages, "messages": self.get_messages()}

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> ShortTermMemory:
        stm = cls(max_messages=int(data.get("max_messages", 40)))
        for m in data.get("messages", []):
            stm.add(m["role"], m["content"])
        return stm
