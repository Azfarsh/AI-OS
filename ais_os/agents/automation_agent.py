from ais_os.agents.base import AgentResponse, BaseAgent
from ais_os.agents.shared import invoke_agent


class AutomationAgent(BaseAgent):
    agent_id = "automation_agent"
    display_name = "Automation"
    description = "Workflow design, scripts, and recurring process automation."
    system_prompt = """You are the Automation Agent. Follow the Machine layer: boring is beautiful,
workflows beat agents, validation chains, kill switches. Propose concrete workflow steps and
which connections.md tools to wire."""

    async def run(self, user_message: str, *, context: str, memory_block: str, model: str, tools_enabled: bool = True) -> AgentResponse:
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
