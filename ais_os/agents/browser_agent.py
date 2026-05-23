from ais_os.agents.base import AgentResponse, BaseAgent
from ais_os.agents.shared import invoke_agent
from ais_os.config import get_config


class BrowserAgent(BaseAgent):
    agent_id = "browser_agent"
    display_name = "Browser"
    description = "Playwright browser tasks (Phase 3). Plans automation steps today."
    system_prompt = """You are the Browser Agent. Phase 3 adds Playwright execution.
For now: produce step-by-step browser playbooks (selectors, URLs, login notes).
Flag when agents.permissions.browser is enabled for live runs."""

    async def run(self, user_message: str, *, context: str, memory_block: str, model: str, tools_enabled: bool = True) -> AgentResponse:
        cfg = get_config()
        extra = ""
        if not cfg.agent_permissions.get("browser"):
            extra = "\n\nNote: browser automation is disabled in config. Output a playbook only."
        return await invoke_agent(
            agent_id=self.agent_id,
            display_name=self.display_name,
            system_prompt=self.system_prompt + extra,
            user_message=user_message,
            context=context,
            memory_block=memory_block,
            model=model,
            tools_enabled=False,
        )
