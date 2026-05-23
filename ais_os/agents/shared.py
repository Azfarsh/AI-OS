"""Shared agent LLM invocation with optional tools."""

from __future__ import annotations

import json
import logging
from typing import Any

from ais_os.agents.base import AgentResponse
from ais_os.models.openrouter import OpenRouterClient
from ais_os.tools.registry import get_tool_registry

logger = logging.getLogger("ais_os.agents.shared")
MAX_TOOL_ROUNDS = 3


async def invoke_agent(
    *,
    agent_id: str,
    display_name: str,
    system_prompt: str,
    user_message: str,
    context: str,
    memory_block: str,
    model: str,
    tools_enabled: bool = True,
) -> AgentResponse:
    llm = OpenRouterClient()
    tools = get_tool_registry()
    messages: list[dict[str, str]] = [
        {
            "role": "system",
            "content": f"{system_prompt}\n\n## Operator context (AIS-OS Context layer)\n{context}\n\n{memory_block}".strip(),
        },
        {"role": "user", "content": user_message},
    ]
    tool_schemas = tools.schemas() if tools_enabled else None

    for round_i in range(MAX_TOOL_ROUNDS):
        raw = await llm.chat(messages, model=model, tools=tool_schemas)
        if not raw.strip().startswith("["):
            return AgentResponse(content=raw, agent_id=agent_id, model=model)

        try:
            calls = json.loads(raw)
        except json.JSONDecodeError:
            return AgentResponse(content=raw, agent_id=agent_id, model=model)

        if not isinstance(calls, list):
            return AgentResponse(content=raw, agent_id=agent_id, model=model)

        messages.append({"role": "assistant", "content": raw})
        for call in calls:
            name = call.get("name", "")
            args = call.get("arguments", "{}")
            result = await tools.execute(name, args)
            messages.append(
                {
                    "role": "user",
                    "content": f"Tool `{name}` result (success={result.success}):\n{result.output}",
                }
            )
        logger.debug("Agent %s tool round %d", agent_id, round_i + 1)

    return AgentResponse(
        content="Tool loop limit reached. Summarize from partial results above.",
        agent_id=agent_id,
        model=model,
        metadata={"tool_rounds": MAX_TOOL_ROUNDS},
    )
