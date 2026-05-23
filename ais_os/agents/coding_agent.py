from ais_os.agents.base import AgentResponse, BaseAgent
from ais_os.agents.shared import invoke_agent


class CodingAgent(BaseAgent):
    agent_id = "coding_agent"
    display_name = "Coding"
    description = "Software engineering, debugging, refactors, and repo changes."
    system_prompt = """You are the Coding Agent for AIS-OS. You write production-quality code,
run terminal commands via tools when needed, and respect the existing repo structure.
Prefer minimal diffs. Match project conventions. Never leave placeholder implementations."""

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
