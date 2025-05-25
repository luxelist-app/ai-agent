import os, asyncio, httpx, datetime as dt
from typing import List, Dict

PAT = os.getenv("GH_PAT")
REPO = os.getenv("GH_REPO")  # e.g. luxelist-app/luxelist

HEADERS = {"Authorization": f"Bearer {PAT}", "Accept": "application/vnd.github+json"}
BASE = "https://api.github.com"

async def _call(method, url, **kw):
    kw.setdefault("headers", {}).update(HEADERS)
    async with httpx.AsyncClient(timeout=15) as c:
        r = await c.request(method, f"{BASE}{url}", **kw)
        r.raise_for_status()
        return r.json()

# ---------- public helpers ------------------------------------------- #
async def fetch_issues() -> List[Dict]:
    return await _call("GET", f"/repos/{REPO}/issues?state=all&per_page=100")

async def create_issue(title: str, body: str, labels=None) -> Dict:
    data = {"title": title, "body": body, "labels": labels or []}
    return await _call("POST", f"/repos/{REPO}/issues", json=data)

async def close_issue(issue_number: int):
    return await _call("PATCH", f"/repos/{REPO}/issues/{issue_number}", json={"state": "closed"})
