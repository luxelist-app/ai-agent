
from backend.agents.base_agent import BaseAgent, AgentResponse

class Agent(BaseAgent):
    async def handle(self, message, context):
        return AgentResponse(content=f"GeneralAgent ➜ Echo: {message}")
