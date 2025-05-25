# backend/agents/base_agent.py
from abc import ABC, abstractmethod
from typing import Any, Dict
from pydantic import BaseModel

class AgentResponse(BaseModel):
    content: str
    metadata: Dict[str, Any] = {}

class BaseAgent(ABC):
    def __init__(self, llm, tools=None):
        self.llm = llm
        self.tools = tools or []

    @abstractmethod
    async def handle(self, message: str, context: Dict) -> AgentResponse:
        ...

    # Shared helpers ↓
    async def chat(self, prompt: str) -> str:
        # Thin async wrapper around your chosen LLM SDK
        return await self.llm.acomplete(prompt)
