# backend/agents/feature_strategist_agent.py
from __future__ import annotations

import json
import re
import time
from datetime import date
from pathlib import Path
from typing import Dict, List, Tuple

from backend.agents.base_agent import AgentResponse, BaseAgent

DATA_DIR = Path(__file__).resolve().parent.parent / "data"
DATA_DIR.mkdir(exist_ok=True)
IDEA_FILE = DATA_DIR / "ideas.json"


class IdeaStore:
    """Lightweight JSON tracker for ideas & statuses."""
    def __init__(self, path: Path = IDEA_FILE):
        self.path = path
        if not self.path.exists():
            self._write([])
        self.ideas: List[Dict] = self._read()

    # -------------- public helpers ----------------- #
    def add(self, text: str) -> Dict:
        entry = {
            "id": int(time.time() * 1000),
            "text": text.strip(),
            "status": "active",
            "created": date.today().isoformat(),
        }
        self.ideas.append(entry)
        self._write(self.ideas)
        return entry

    def list(self) -> List[Dict]:
        return self.ideas

    # ---------------- file i/o ---------------------- #
    def _read(self) -> List[Dict]:
        return json.loads(self.path.read_text())

    def _write(self, obj):
        self.path.write_text(json.dumps(obj, indent=2))


class Agent(BaseAgent):
    """
    Feature Strategist Agent
    • add idea: <text>
    • list ideas
    • roadmap
    • retrospective
    • estimate feature: <text>
    """

    _idea_store = IdeaStore()

    async def handle(self, message: str, context: Dict) -> AgentResponse:
        msg = message.lower().strip()

        # ---------- add idea ---------- #
        if msg.startswith("add idea:"):
            idea_text = message.split(":", 1)[1]
            entry = self._idea_store.add(idea_text)
            return AgentResponse(content=f"💡 Idea saved (id={entry['id']}).")

        # ---------- list ideas -------- #
        if msg.startswith("list ideas"):
            items = self._idea_store.list()
            if not items:
                return AgentResponse(content="(No ideas yet)")
            bullets = "\n".join(f"* {i['text']} – _{i['status']}_" for i in items)
            return AgentResponse(content=f"### Idea backlog\n{bullets}")

        # ---------- roadmap ----------- #
        if msg.startswith("roadmap"):
            mvp, v1, v2 = self._bucketize(self._idea_store.list())
            roadmap_md = self._format_roadmap(mvp, v1, v2)
            return AgentResponse(content=roadmap_md)

        # ---------- retrospective ----- #
        if msg.startswith("retrospective"):
            md = (
                "## 🗓 Weekly Retrospective\n\n"
                "**Done**:\n- \n\n"
                "**Next**:\n- \n\n"
                "**Insights**:\n- "
            )
            return AgentResponse(content=md)

        # ---------- estimate ---------- #
        if msg.startswith("estimate feature:"):
            feat = message.split(":", 1)[1].strip()
            days = self._estimate_days(feat)
            return AgentResponse(content=f"📏 Rough estimate for _{feat}_ ⇒ **~{days} days**")

        # fallback
        return AgentResponse(
            content="🧭 Strategist options: `add idea:`, `list ideas`, `roadmap`, "
                    "`retrospective`, `estimate feature:`"
        )

    # ====================================================== #
    # private helpers
    # ====================================================== #
    def _bucketize(self, ideas: List[Dict]) -> Tuple[List[str], List[str], List[str]]:
        """Trivial bucketing by index just for demo."""
        mvp, v1, v2 = [], [], []
        for idx, it in enumerate(ideas):
            if idx < 3:
                mvp.append(it["text"])
            elif idx < 6:
                v1.append(it["text"])
            else:
                v2.append(it["text"])
        return mvp, v1, v2

    @staticmethod
    def _format_roadmap(mvp: List[str], v1: List[str], v2: List[str]) -> str:
        def section(title, items):
            if not items:
                return ""
            lines = "\n".join(f"- {x}" for x in items)
            return f"### {title}\n{lines}\n"
        return section("🚀 MVP (0.1)", mvp) + section("v1.0", v1) + section("v2.0+", v2)

    @staticmethod
    def _estimate_days(text: str) -> int:
        words = len(text.split())
        if words < 5:
            return 2
        if words < 15:
            return 5
        return 10
