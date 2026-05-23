from ais_os.agents.base import AgentResponse, BaseAgent
from ais_os.agents.shared import invoke_agent


class OutreachAgent(BaseAgent):
    agent_id = "outreach_agent"
    display_name = "Outreach"
    description = "Campaigns, LinkedIn/email drafts, lead messaging (Phase 3: browser automation)."
    system_prompt = """You are the Outreach Agent. Draft messages matching references/voice.md when available.
Never send external messages without operator approval. Propose sequences, subject lines, and CTAs."""

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
