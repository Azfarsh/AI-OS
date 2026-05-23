from ais_os.agents.base import AgentResponse, BaseAgent
from ais_os.agents.shared import invoke_agent


class MeetingAgent(BaseAgent):
    agent_id = "meeting_agent"
    display_name = "Meeting"
    description = "Meeting prep, agendas, follow-ups, and action items."
    system_prompt = """You are the Meeting Agent. Produce agendas, pre-reads, and follow-up emails
with clear owners and deadlines. Pull from context when meeting systems are in connections.md."""

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
