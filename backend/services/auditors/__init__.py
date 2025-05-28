# backend/services/auditors/__init__.py
import asyncio
from .lighthouse import run_lighthouse
from .zap import run_zap

async def run_all(target, objective):
    lh, zap = await asyncio.gather(run_lighthouse(target), run_zap(target))
    return {"lighthouse": lh, "zap": zap}

def diff_to_tasks(results, objective):
    tasks = []
    if results["lighthouse"]["perf"] < 90:
        tasks.append("Improve Lighthouse performance score to 90+")
    if results["zap"]["alerts"]:
        tasks.append("Fix security alerts reported by ZAP")
    return tasks
