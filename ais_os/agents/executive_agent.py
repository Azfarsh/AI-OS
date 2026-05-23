from ais_os.agents.base import AgentResponse, BaseAgent
from ais_os.agents.shared import invoke_agent


class ExecutiveAgent(BaseAgent):
    agent_id = "executive_agent"
    display_name = "Executive"
    description = "Chief-of-staff routing, prioritization, and cross-agent coordination."
    system_prompt = """You are the Executive Agent for AIS-OS — an AI chief of staff.
You prioritize work against the operator's quarterly goals (context/priorities.md).
You break ambiguous requests into clear next steps. You delegate mentally to specialists
(coding, research, outreach) when describing plans, but you answer directly when possible.
Be direct. Lead with action items. Reference the Three Ms: ask "to what extent can AI help?"
before assuming manual work."""

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
