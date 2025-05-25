from backend.agents.feature_strategist_agent import Agent as Strategist
from backend.services import github_sync as gh, task_db as db
from backend.services.llm_selector import get_llm
from backend.agents.base_agent import AgentResponse
from backend.services.vault_editor import append_to_note
import datetime as dt

LLM = get_llm()

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
            # batch LLM call to split each backlog idea into tasks
            ideas = [i["text"] for i in self._idea_store.list() if i["status"]=="active"]
            prompt = "Turn each idea into 3 small dev tasks, JSON list please:\n"+"\n".join(ideas)
            tasks_json = await LLM.acomplete(prompt=prompt)
            # ...parse & insert...
            return AgentResponse(content="📝 Tasks generated.")
        
        if msg.startswith("/brainstorm "):
            idea = msg[len("/brainstorm "):]
            append_to_note(ctx.get("feature_title", "unsorted-ideas"),
                        f"### Brainstorm {dt.datetime.now():%Y-%m-%d %H:%M}\n{idea}")
            return AgentResponse(content="📝 Added brainstorm block to Obsidian.")

        return await super().handle(msg, ctx)
