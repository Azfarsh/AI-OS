from ais_os.agents.base import AgentResponse, BaseAgent
from ais_os.agents.shared import invoke_agent


class MemoryAgent(BaseAgent):
    agent_id = "memory_agent"
    display_name = "Memory"
    description = "Curate long-term memory, summarize sessions, organize notes."
    system_prompt = """You are the Memory Agent. Help the operator capture durable facts as concise
markdown notes. Suggest what belongs in vector memory vs context/ vs decisions/log.md.
Never store raw email/Slack dumps — interpreted facts only (per EXPANSIONS.md)."""

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
