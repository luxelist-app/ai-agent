from fastapi import APIRouter, Body
from backend.services.auditors import run_all, diff_to_tasks

router = APIRouter()

@router.post("/")
async def audit_site(payload: dict = Body(...)):
    url = payload.get("url")
    objective = payload.get("objective", "Prepare for website launch")
    results = await run_all(url, objective)
    tasks = diff_to_tasks(results, objective)
    return {"results": results, "tasks": tasks}