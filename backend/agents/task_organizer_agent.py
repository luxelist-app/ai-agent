import json
import textwrap
from backend.agents.feature_strategist_agent import Agent as Strategist
from backend.services import github_sync as gh, task_db as db
from backend.services.llm_selector import get_llm
from backend.agents.base_agent import AgentResponse
from backend.services.vault_editor import append_to_note
import datetime as dt

LLM = get_llm()

def _safe_parse_tasks(raw: str) -> list[str]:
    """
    Expects raw to be JSON or JSON inside markdown fences.
    Returns a flat list of task strings.
    """
    trimmed = raw.strip()
    if trimmed.startswith("```"):
        trimmed = trimmed.split("\n", 1)[1].rsplit("```", 1)[0]
    try:
        data = json.loads(trimmed)
        # data can be [{'idea': 'foo', 'tasks': ['a', 'b']} , …] OR a flat list
        if isinstance(data, list) and all(isinstance(x, str) for x in data):
            return data
        tasks = []
        for block in data:
            tasks.extend(block.get("tasks", []))
        return tasks
    except Exception as e:
        print("[plan] JSON parse failed:", e)
        return []

class Agent(Strategist):
    async def handle(self, msg: str, ctx):
        if msg.startswith("/sync"):
            issues = await gh.fetch_issues()
            db.sync_from_github(issues)
            return AgentResponse(content=f"🔄 Synced {len(issues)} GitHub issues.")

        if msg.startswith("/add "):
            text = msg[5:].strip()
            idea = self._idea_store.add(text)
            iss = await gh.create_issue(idea["text"], "Added via chat", labels=["backlog"])
            db.add_task(title=idea["text"], gh_number=iss["number"])
            return AgentResponse(content=f"✅ Idea saved and issue #{iss['number']} created.")

        if msg.startswith("/plan"):
            ideas = [i["text"] for i in self._idea_store.list() if i["status"]=="active"]
            if not ideas:
                return AgentResponse(content="📭 No active ideas.")
            prompt = textwrap.dedent(f"""
                Split each idea into 3 bullet-point dev tasks (10 words max each).
                Return raw JSON list (no markdown).
                Ideas:
                {json.dumps(ideas, indent=2)}
            """)
            raw = await LLM.acomplete(prompt=prompt)
            tasks = _safe_parse_tasks(raw)
            if not tasks:
                return AgentResponse(content="⚠️ LLM response un-parsable.")
            for t in tasks:
                issue = await gh.create_issue(t, "Generated via /plan", labels=["backlog"])
                db.add_task(title=t, gh_number=issue["number"])
            return AgentResponse(content=f"📝 Added {len(tasks)} tasks to backlog.")

        if msg.startswith("/brainstorm "):
            idea = msg[len("/brainstorm "):]
            append_to_note(ctx.get("feature_title", "unsorted-ideas"),
                        f"### Brainstorm {dt.datetime.now():%Y-%m-%d %H:%M}\n{idea}")
            return AgentResponse(content="📝 Added brainstorm block to Obsidian.")

        return await super().handle(msg, ctx)
