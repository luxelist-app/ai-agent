"""
LLMSelector – auto-picks the highest-ranked model (Chatbot Arena leaderboard)
that you have credentials for.

Usage:
    from services.llm_selector import get_llm
    llm = get_llm()
    reply = await llm.acomplete(prompt="Hello")

Supported providers so far:
    • OpenAI      – env: OPENAI_API_KEY
    • Anthropic   – env: ANTHROPIC_API_KEY
    • Google Gemini – env: GOOGLE_API_KEY
    • Mistral     – env: MISTRAL_API_KEY
    • TogetherAI  – env: TOGETHER_API_KEY   (fallback for many OSS models)
"""
from __future__ import annotations

import csv
import os
import re
from functools import lru_cache
from typing import Optional
import httpx
from backend.utils.aiml_client import ask_aiml

HF_CSV_URL = (
    "https://huggingface.co/spaces/"
    "lmarena-ai/chatbot-arena-leaderboard/raw/main/"
    "arena_hard_auto_leaderboard_v0.1.csv"
)

# --------------------------------------------------------------------- #
# Mapping leaderboard model names → provider + model identifier
# Feel free to extend as you get more keys.
# --------------------------------------------------------------------- #
MODEL_MAP = {
    # OpenAI
    "gpt-4o":               ("openai", "gpt-4o-mini"),
    "gpt-4o-2024-05-13":     ("openai", "gpt-4o-mini"),
    "gpt-4-turbo":          ("openai", "gpt-4o-mini"),
    "gpt-4-turbo-2024-04-09":("openai", "gpt-4o-mini"),
    "gpt-4-0125-preview":   ("openai", "gpt-4o-mini"),
    # Anthropic
    "claude-3-5-sonnet":    ("anthropic", "claude-3.5-sonnet-20240620"),
    "claude-3-opus":        ("anthropic", "claude-3-opus-20240229"),
    "claude-3-sonnet":      ("anthropic", "claude-3-sonnet-20240229"),
    "claude-3-haiku":       ("anthropic", "claude-3-haiku-20240307"),
    # Google
    "gemini-1.5-pro":       ("google",   "models/gemini-1.5-pro-latest"),
    "gemini-1.5-flash":     ("google",   "models/gemini-1.5-flash"),
    # Mistral
    "mistral-large":        ("mistral",  "mistral-large-latest"),
    # Together (open-weights)
    "mixtral-8x22b":        ("together", "mistralai/Mixtral-8x22B-Instruct-v0.1"),
    "yi-large":             ("together", "01-ai/Yi-34B-Chat"),
    "deepseek-coder-v2":    ("together", "deepseek-ai/deepseek-coder-33b-instruct"),
}

# env → SDK import path and factory
CLIENTS = {
    "openai":   ("OPENAI_API_KEY",   lambda: __import__("openai").OpenAI()),
    "anthropic":("ANTHROPIC_API_KEY",lambda: __import__("anthropic").Anthropic()),
    "google":   ("GOOGLE_API_KEY",   lambda: __import__("google.generativeai").generativeai),
    "mistral":  ("MISTRAL_API_KEY",  lambda: __import__("mistralai.client").client.MistralClient()),
    "together": ("TOGETHER_API_KEY", lambda: __import__("together").Together()),
    "aiml":    ("AIML_API_KEY", lambda: ask_aiml),
}

@lru_cache(maxsize=1)
def _fetch_leaderboard() -> list[tuple[str, float]]:
    """Return list[(model_name, score)] sorted descending."""
    with httpx.Client(timeout=10) as client:
        csv_bytes = client.get(HF_CSV_URL).content.decode()
    reader = csv.DictReader(csv_bytes.splitlines())
    rows = sorted(reader, key=lambda r: float(r["score"]), reverse=True)
    return [(r["model"].strip(), float(r["score"])) for r in rows]

def _first_available_model() -> Optional[tuple[str, str, str]]:
    """Return (provider, model_name, raw_leaderboard_name) or None."""
    leaderboard = _fetch_leaderboard()
    for raw_name, _ in leaderboard:
        # normalise for mapping keys
        key = re.sub(r"[ _]+", "-", raw_name.lower())
        for known, (prov, mdl) in MODEL_MAP.items():
            if key.startswith(known):
                env_name, _ = CLIENTS[prov]
                if os.getenv(env_name):
                    return prov, mdl, raw_name
    return None

def get_llm():
    """
    Instantiate the highest-ranked model you have credentials for.
    Falls back to OpenAI GPT-3.5 if nothing matches.
    """
    choice = _first_available_model()
    if choice:
        provider, model, raw = choice
        env_name, factory = CLIENTS[provider]
        client = factory()
        print(f"[LLMSelector] Using '{raw}' via {provider} (from leaderboard)")
        if provider == "openai":
            client.model = model   # OpenAI python SDK
            return client
        # Expand per SDK; all must implement .acomplete or adapter.
        # For brevity we wrap everything in a tiny adapter here:
        class Adapter:
            async def acomplete(self, prompt: str):
                if provider == "anthropic":
                    resp = await client.messages.create(
                        model=model, max_tokens=2048, messages=[{"role":"user","content":prompt}]
                    )
                    return resp.content[0].text
                if provider == "google":
                    resp = await client.chat.completions.create(model=model, prompt=prompt)
                    return resp.text
                if provider == "mistral":
                    resp = await client.chat(model=model, prompt=prompt)
                    return resp["choices"][0]["message"]["content"]
                if provider == "together":
                    resp = await client.chat.completions.create(
                        model=model, messages=[{"role":"user","content":prompt}]
                    )
                    return resp.choices[0].message.content
        return Adapter()
    
    # ---------- fallback ----------
    aiml_key = os.getenv("AIML_API_KEY")
    if aiml_key:
        # 1️⃣  Use ask_aiml from backend.utils.aiml_client
        class AIMLAdapter:
            async def acomplete(self, prompt: str):
                # ask_aiml is synchronous, so run in thread executor
                import asyncio
                loop = asyncio.get_event_loop()
                return await loop.run_in_executor(None, ask_aiml, prompt)
        print("[LLMSelector] Using AIML provider (fallback)")
        return AIMLAdapter()

    # If we get here, nothing is configured:
    raise RuntimeError("No usable LLM credentials found.")