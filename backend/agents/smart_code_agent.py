
from backend.agents.base_agent import BaseAgent, AgentResponse

CODE_STUB = """```dart
// your Flutter code goes here
```"""

class Agent(BaseAgent):
    async def handle(self, message, context):
        # In reality you'd parse message and generate code
        return AgentResponse(content="Here's a starter code snippet:\n" + CODE_STUB)
