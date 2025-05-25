import json
from fastapi import APIRouter, Body
from backend.utils.file_io import load_json, log_item
from backend.services.task_db import all_tasks
from datetime import datetime

router = APIRouter()

@router.post("/")
async def add_task(task: dict = Body(...)):
    return log_item(task, "tasks.json")

@router.get("/")
async def get_tasks():
    with open("data/tasks.json", "r") as f:
        return json.load(f)

@router.get("/")
async def list_tasks():
    return all_tasks()

@router.post("/start")
async def start_task(data: dict = Body(...)):
    task_id = data.get("id")
    mood = data.get("mood")
    energy = data.get("energy")
    focus = data.get("focus")
    started = datetime.utcnow().isoformat()

    tasks = load_json("tasks.json")
    for t in tasks:
        if t.get("id") == task_id:
            t["status"] = "in_progress"
            t["started"] = started
            t["mood"] = mood
            t["energy"] = energy
            t["focus"] = focus
            break

    with open("data/tasks.json", "w") as f:
        json.dump(tasks, f, indent=2)

    return {"status": "started", "task": task_id}

@router.post("/complete")
async def complete_task(data: dict = Body(...)):
    task_id = data.get("id")
    completed = datetime.utcnow()
    tasks = load_json("tasks.json")

    for t in tasks:
        if t.get("id") == task_id and "started" in t:
            t["status"] = "done"
            start_time = datetime.fromisoformat(t["started"])
            duration = (completed - start_time).total_seconds() / 60  # minutes
            t["duration"] = duration
            t["completed"] = completed.isoformat()
            break

    with open("data/tasks.json", "w") as f:
        json.dump(tasks, f, indent=2)

    return {"status": "completed", "task": task_id, "duration_min": duration}

@router.get("/estimate")
async def estimate_task_time():
    from backend.utils.file_io import load_json

    tasks = load_json("tasks.json")

    durations = [
        t["duration"]
        for t in tasks
        if t.get("status") == "done" and t.get("duration") is not None
    ]

    if not durations:
        return {"estimated_minutes": 30}  # Default fallback time

    avg_time = sum(durations) / len(durations)
    return {"estimated_minutes": round(avg_time, 1)}
