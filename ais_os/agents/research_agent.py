from ais_os.agents.base import AgentResponse, BaseAgent
from ais_os.agents.shared import invoke_agent


class ResearchAgent(BaseAgent):
    agent_id = "research_agent"
    display_name = "Research"
    description = "Deep research, synthesis, competitive analysis, and reports."
    system_prompt = """You are the Research Agent for AIS-OS. You produce structured,
source-aware analysis. Cite assumptions. Use filesystem tools to read project docs when useful.
Output: executive summary, findings, recommendations."""

    async def run(
        self,
        user_message: str,
        *,
        context: str,
        memory_block: str,
        model: str,
        tools_enabled: bool = True,
    ) -> AgentResponse:
        return await invoke_agent(
            agent_id=self.agent_id,
            display_name=self.display_name,
            system_prompt=self.system_prompt,
            user_message=user_message,
            context=context,
            memory_block=memory_block,
            model=model,
            tools_enabled=tools_enabled,
        )
