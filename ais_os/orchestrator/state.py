"""LangGraph state for multi-agent orchestration."""

from __future__ import annotations

from typing import TypedDict


class OrchestratorState(TypedDict):
    user_input: str
    route: str
    agent_id: str
    model: str
    context: str
    memory_block: str
    response: str
    retries: int
    error: str
