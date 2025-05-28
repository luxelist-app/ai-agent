import asyncio, random

async def run_lighthouse(target: str):
    """
    Placeholder runner that returns fake scores.
    Replace with `subprocess.run(["npx","lhci","collect",...])` later.
    """
    await asyncio.sleep(0.1)
    return {
        "perf": random.randint(75, 95),
        "a11y": random.randint(80, 100),
        "seo":  random.randint(70, 100),
    }
