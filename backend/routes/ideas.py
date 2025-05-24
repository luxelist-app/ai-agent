import json
from fastapi import APIRouter, Body
from backend.utils.file_io import log_item

router = APIRouter()

@router.post("/")
async def add_idea(idea: dict = Body(...)):
    return log_item(idea, "ideas.json")

@router.get("/")
async def get_ideas():
    with open("data/ideas.json", "r") as f:
        return json.load(f)
