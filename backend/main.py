from fastapi import FastAPI
from pathlib import Path
from pydantic import BaseModel
from backend.routes import chat as chat_mod, explain, tasks, ideas, summary, mood
from backend.agents.loader import AgentRouter

MANIFEST = Path(__file__).parent / "agents" / "manifest.yaml"

app = FastAPI(title="AI Agent API")
router = AgentRouter(str(MANIFEST))

# Include routes
app.include_router(chat_mod.router, prefix="/chat")
app.include_router(explain.router, prefix="/explain")
app.include_router(ideas.router, prefix="/ideas")
app.include_router(summary.router, prefix="/summary")
app.include_router(mood.router, prefix="/mood")
app.include_router(tasks.router, prefix="/tasks", tags=["Tasks"])

class ChatReq(BaseModel):
    message: str
    context: dict | None = None

@app.post("/agent/chat")
async def agent_chat(req: ChatReq):
    reply = await router.chat(req.message, req.context or {})
    return reply.dict()