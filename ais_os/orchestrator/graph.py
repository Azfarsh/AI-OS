"""LangGraph orchestrator — executive routes to specialist agents."""

from __future__ import annotations

import logging
import re

from langgraph.graph import END, StateGraph

from ais_os.agents.registry import get_agent_registry
from ais_os.config import get_config
from ais_os.models.router import ModelRouter, TaskType
from ais_os.orchestrator.state import OrchestratorState

logger = logging.getLogger("ais_os.orchestrator")

_ROUTE_PATTERNS: list[tuple[re.Pattern[str], str, TaskType]] = [
    (re.compile(r"\b(code|debug|implement|refactor|python|git)\b", re.I), "coding_agent", TaskType.CODE),
    (re.compile(r"\b(research|analyze|compare|report)\b", re.I), "research_agent", TaskType.RESEARCH),
    (re.compile(r"\b(email|linkedin|outreach|campaign|lead)\b", re.I), "outreach_agent", TaskType.CHAT),
    (re.compile(r"\b(deploy|release|ci|docker|kubernetes)\b", re.I), "deployment_agent", TaskType.CODE),
    (re.compile(r"\b(meeting|agenda|calendar|follow.?up)\b", re.I), "meeting_agent", TaskType.CHAT),
    (re.compile(r"\b(browser|scrape|playwright|login)\b", re.I), "browser_agent", TaskType.CHAT),
    (re.compile(r"\b(remember|memory|recall|note)\b", re.I), "memory_agent", TaskType.CHAT),
    (re.compile(r"\b(workflow|automate|n8n|zapier)\b", re.I), "automation_agent", TaskType.PLANNING),
]


def _pick_route(message: str, forced_agent: str | None) -> tuple[str, TaskType]:
    if forced_agent:
        tt = TaskType.CODE if "coding" in forced_agent else TaskType.CHAT
        return forced_agent, tt
    for pattern, agent_id, task_type in _ROUTE_PATTERNS:
        if pattern.search(message):
            return agent_id, task_type
    return "executive_agent", TaskType.CHAT


class Orchestrator:
    def __init__(self) -> None:
        self._agents = get_agent_registry()
        self._router = ModelRouter()
        self._cfg = get_config()
        self._graph = self._build_graph()

    def _build_graph(self):
        g = StateGraph(OrchestratorState)

        async def route_node(state: OrchestratorState) -> dict:
            forced = state.get("agent_id") or None
            if forced == "":
                forced = None
            agent_id, task_type = _pick_route(state["user_input"], forced)
            model = self._router.resolve(state["user_input"], task_type=task_type)
            logger.info("Routed to %s with model %s", agent_id, model)
            return {"route": agent_id, "agent_id": agent_id, "model": model, "retries": 0, "error": ""}

        async def execute_node(state: OrchestratorState) -> dict:
            agent = self._agents.get(state["agent_id"])
            if not agent:
                return {"response": f"Unknown agent: {state['agent_id']}", "error": "unknown_agent"}
            try:
                result = await agent.run(
                    state["user_input"],
                    context=state.get("context", ""),
                    memory_block=state.get("memory_block", ""),
                    model=state.get("model", self._cfg.default_model),
                )
                return {"response": result.content, "error": ""}
            except Exception as exc:
                logger.exception("Agent execution failed")
                retries = state.get("retries", 0) + 1
                if retries <= self._cfg.max_agent_retries:
                    return {"retries": retries, "error": str(exc)}
                return {"response": f"Agent failed after retries: {exc}", "error": str(exc)}

        async def retry_node(state: OrchestratorState) -> dict:
            if state.get("error") and state.get("retries", 0) <= self._cfg.max_agent_retries:
                return await execute_node(state)
            return {}

        g.add_node("route", route_node)
        g.add_node("execute", execute_node)
        g.set_entry_point("route")
        g.add_edge("route", "execute")
        g.add_edge("execute", END)
        return g.compile()

    async def run(
        self,
        user_input: str,
        *,
        context: str,
        memory_block: str,
        agent_id: str | None = None,
        model_override: str | None = None,
    ) -> dict:
        initial: OrchestratorState = {
            "user_input": user_input,
            "route": "",
            "agent_id": agent_id or "",
            "model": model_override or "",
            "context": context,
            "memory_block": memory_block,
            "response": "",
            "retries": 0,
            "error": "",
        }
        if model_override:
            initial["model"] = model_override
        final = await self._graph.ainvoke(initial)
        return {
            "response": final.get("response", ""),
            "agent_id": final.get("agent_id", "executive_agent"),
            "model": final.get("model", self._cfg.default_model),
            "error": final.get("error", ""),
        }
