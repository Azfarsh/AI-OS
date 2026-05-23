"""Agent registry — all modular agents."""

from __future__ import annotations

from functools import lru_cache
from typing import TYPE_CHECKING

from ais_os.agents.automation_agent import AutomationAgent
from ais_os.agents.base import BaseAgent
from ais_os.agents.browser_agent import BrowserAgent
from ais_os.agents.coding_agent import CodingAgent
from ais_os.agents.deployment_agent import DeploymentAgent
from ais_os.agents.executive_agent import ExecutiveAgent
from ais_os.agents.meeting_agent import MeetingAgent
from ais_os.agents.memory_agent import MemoryAgent
from ais_os.agents.outreach_agent import OutreachAgent
from ais_os.agents.research_agent import ResearchAgent

if TYPE_CHECKING:
    pass


class AgentRegistry:
    def __init__(self) -> None:
        self._agents: dict[str, BaseAgent] = {}
        for agent_cls in (
            ExecutiveAgent,
            CodingAgent,
            ResearchAgent,
            OutreachAgent,
            AutomationAgent,
            BrowserAgent,
            MemoryAgent,
            MeetingAgent,
            DeploymentAgent,
        ):
            inst = agent_cls()
            self._agents[inst.agent_id] = inst

    def get(self, agent_id: str) -> BaseAgent | None:
        return self._agents.get(agent_id)

    def list_agents(self) -> list[dict[str, str]]:
        return [
            {
                "id": a.agent_id,
                "name": a.display_name,
                "description": a.description,
            }
            for a in self._agents.values()
        ]


@lru_cache
def get_agent_registry() -> AgentRegistry:
    return AgentRegistry()
