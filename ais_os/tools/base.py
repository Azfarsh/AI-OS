"""Tool protocol for AIS-OS."""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any


@dataclass
class ToolResult:
    success: bool
    output: str
    data: dict[str, Any] | None = None


class BaseTool(ABC):
    name: str
    description: str

    @abstractmethod
    async def run(self, **kwargs: Any) -> ToolResult:
        ...

    def schema(self) -> dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": self.name,
                "description": self.description,
                "parameters": self.parameters_schema(),
            },
        }

    def parameters_schema(self) -> dict[str, Any]:
        return {"type": "object", "properties": {}, "required": []}
