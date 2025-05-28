# backend/agents/gap_finder_agent.py
from backend.agents.base_agent import BaseAgent, AgentResponse
from backend.services import auditors, project_db as pdb
import re, asyncio, uuid

class Agent(BaseAgent):
    async def handle(self, msg: str, ctx):
        m = re.match(r"/audit\s+(?P<target>\S+)(\s+objective=(?P<obj>\S+))?", msg)
        if not m:
            return AgentResponse(content="Usage: /audit <url|path|repo> objective=<goal>")

        target, objective = m.group("target"), m.group("obj") or "release"
        proj_id = uuid.uuid4().hex[:8]

        # 1️⃣  Run analyzers concurrently
        results = await auditors.run_all(target, objective)

        # 2️⃣  Diff against rubric
        tasks = auditors.diff_to_tasks(results, objective)

        # 3️⃣  Persist project + tasks
        pdb.create_project(proj_id, target, objective, results["score"])
        for t in tasks:
            pdb.add_task(title=t, project_id=proj_id, status="backlog")

        return AgentResponse(content=f"📋 Project *{proj_id}* created with {len(tasks)} tasks.")
