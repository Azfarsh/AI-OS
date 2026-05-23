"""Base agent interface."""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any


@dataclass
class AgentResponse:
    content: str
    agent_id: str
    model: str
    metadata: dict[str, Any] = field(default_factory=dict)


class BaseAgent(ABC):
    agent_id: str
    display_name: str
    description: str
    system_prompt: str

    @abstractmethod
    async def run(
        self,
        user_message: str,
        *,
        context: str,
        memory_block: str,
        model: str,
        tools_enabled: bool = True,
    ) -> AgentResponse:
        ...
