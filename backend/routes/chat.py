from fastapi import APIRouter, Body
from backend.utils.aiml_client import ask_aiml
from backend.utils.file_io import log_chat

router = APIRouter()

@router.post("/")
async def chat_with_agent(payload: dict = Body(...)):
    prompt = payload.get("prompt", "")
    response = ask_aiml(prompt)
    log_chat(prompt, response)
    return {"prompt": prompt, "response": response}
