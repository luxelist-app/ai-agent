from fastapi import FastAPI
from .routes import chat, explain, tasks, ideas, summary, mood

app = FastAPI(title="AI Dev Agent API")

# Include routes
app.include_router(chat.router, prefix="/chat")
app.include_router(explain.router, prefix="/explain")
app.include_router(tasks.router, prefix="/tasks")
app.include_router(ideas.router, prefix="/ideas")
app.include_router(summary.router, prefix="/summary")
app.include_router(mood.router, prefix="/mood")