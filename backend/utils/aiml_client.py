import os
import requests
from dotenv import load_dotenv

load_dotenv()
AIML_API_KEY = os.getenv("AIML_API_KEY")
AIML_URL = "https://api.aimlapi.com/v1/chat/completions"  # Confirm this is correct

def ask_aiml(prompt: str) -> str:
    headers = {
        "Authorization": f"Bearer {AIML_API_KEY}",
        "Content-Type": "application/json"
    }
    body = {
        "model": "gpt-3.5-turbo",  # or whatever model AIMLapi supports
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.7
    }

    res = requests.post(AIML_URL, headers=headers, json=body)
    
    try:
        data = res.json()
        # Debugging output (write to log or terminal)
        print("AIMLapi response:", data)
        
        # Update this based on what AIMLapi actually returns
        return data["choices"][0]["message"]["content"]
    except Exception as e:
        return f"[Error parsing response: {e} | Raw response: {res.text}]"
