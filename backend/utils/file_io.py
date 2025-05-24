import json
import os
from datetime import datetime

LOG_FILE = "data/chats.json"

def log_chat(prompt: str, response: str, source: str = "chat"):
    entry = {
        "timestamp": datetime.utcnow().isoformat(),
        "source": source,
        "prompt": prompt,
        "response": response
    }

    if not os.path.exists(LOG_FILE):
        with open(LOG_FILE, "w") as f:
            json.dump([], f)

    with open(LOG_FILE, "r+") as f:
        data = json.load(f)
        data.append(entry)
        f.seek(0)
        json.dump(data, f, indent=2)

def log_item(item: dict, filename: str):
    item["timestamp"] = datetime.utcnow().isoformat()

    path = os.path.join("data", filename)
    if not os.path.exists(path):
        with open(path, "w") as f:
            json.dump([], f)

    with open(path, "r+") as f:
        data = json.load(f)
        data.append(item)
        f.seek(0)
        json.dump(data, f, indent=2)

    return {"status": "logged", "item": item}

def load_json(filename: str):
    path = os.path.join("data", filename)
    if not os.path.exists(path):
        return []
    with open(path, "r") as f:
        return json.load(f)
