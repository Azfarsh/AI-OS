from ais_os.agents.base import AgentResponse, BaseAgent
from ais_os.agents.shared import invoke_agent


class DeploymentAgent(BaseAgent):
    agent_id = "deployment_agent"
    display_name = "Deployment"
    description = "Deploy, CI/CD, infrastructure, and release checklists."
    system_prompt = """You are the Deployment Agent. Produce safe deploy runbooks: preflight checks,
rollback steps, env vars, and commands. Use run_terminal when the operator confirms execution."""

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
