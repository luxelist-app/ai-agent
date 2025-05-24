from fastapi import APIRouter, Body
from datetime import datetime
from backend.utils.file_io import log_item, load_json

router = APIRouter()

@router.post("/")
async def log_mood(data: dict = Body(...)):
    entry = {
        "timestamp": datetime.utcnow().isoformat(),
        "mood": data.get("mood"),
        "energy": data.get("energy"),
        "focus": data.get("focus"),
        "notes": data.get("notes", "")
    }
    return log_item(entry, "mood.json")

@router.get("/")
async def get_mood():
    return load_json("mood.json")[-7:]  # return last 7 entries
