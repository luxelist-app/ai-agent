from fastapi import APIRouter
from datetime import datetime, timedelta
from backend.utils.file_io import load_json

router = APIRouter()

@router.get("/")
async def weekly_summary():
    now = datetime.utcnow()
    week_ago = now - timedelta(days=7)

    def within_week(item):
        ts = item.get("timestamp")
        if not ts:
            return False
        return datetime.fromisoformat(ts) > week_ago

    tasks = [t for t in load_json("tasks.json") if within_week(t)]
    ideas = [i for i in load_json("ideas.json") if within_week(i)]

    summary = {
        "done": [t for t in tasks if t.get("status") == "done"],
        "todo": [t for t in tasks if t.get("status") == "todo"],
        "ideas": ideas
    }

    return {
        "summary": {
            "done": [t["title"] for t in summary["done"]],
            "next": [t["title"] for t in summary["todo"]],
            "ideas": [i["description"] for i in summary["ideas"]],
            "insight": f"{len(summary['done'])} tasks completed, {len(summary['ideas'])} ideas added"
        }
    }
