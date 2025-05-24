from fastapi import APIRouter, Body
from backend.utils.aiml_client import ask_aiml
from backend.utils.file_io import log_chat

router = APIRouter()

@router.post("/")
async def explain_code(code: str = Body(...)):
    prompt = f"Explain this code clearly and simply:\n\n{code}"
    response = ask_aiml(prompt)
    log_chat(prompt, response, source="explain")
    return {"explanation": response}
