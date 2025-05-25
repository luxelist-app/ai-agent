import asyncio, json, yaml, time
import os
from pathlib import Path
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import frontmatter
from backend.services import task_db as db, github_sync as gh

VAULT = Path(os.getenv("VAULT_PATH", "~/Documents/Obsidian/luxelist")).expanduser()
FEATURES_DIR = VAULT / "LUXELIST" / "FEATURES"

class FeatureHandler(FileSystemEventHandler):
    def on_modified(self, event):
        if event.is_directory or not event.src_path.endswith(".md"):
            return
        asyncio.create_task(process_note(Path(event.src_path)))

async def process_note(path: Path):
    note = frontmatter.load(path)
    meta, body = note.metadata, note.content
    title = meta.get("title") or path.stem
    gh_no = meta.get("github_issue")
    # ----- create GH issue if missing -----
    if not gh_no:
        iss = await gh.create_issue(title, body, labels=meta.get("labels", []))
        meta["github_issue"] = iss["number"]
        note.metadata = meta
        frontmatter.dump(note, path.open("w", encoding="utf-8"))
        db.add_task(title=title, gh_number=iss["number"],
                    labels=",".join(meta.get("labels", [])),
                    status=meta.get("status","backlog"),
                    estimate_days=meta.get("estimate_days",0))

def start_watch():
    ob = Observer()
    ob.schedule(FeatureHandler(), str(FEATURES_DIR), recursive=False)
    ob.start()
    print(f"[VaultWatcher] watching {FEATURES_DIR}")
