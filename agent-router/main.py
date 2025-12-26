from fastapi import FastAPI
from pydantic import BaseModel
import requests
import os

app = FastAPI()

OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://ollama:11434")

# Pick models you actually have pulled (we can change later)
MODELS = {
    "fast": os.getenv("MODEL_FAST", "llama3.1:8b-instruct"),
    "reasoning": os.getenv("MODEL_REASONING", "qwen2.5:14b-instruct"),
}

class Query(BaseModel):
    message: str

def route(message: str) -> str:
    m = message.lower()
    # simple router — tweak later
    if any(k in m for k in ["why", "analyze", "plan", "design", "architecture", "debug"]):
        return "reasoning"
    return "fast"

@app.get("/health")
def health():
    return {"status": "ok", "ollama": OLLAMA_BASE_URL, "models": MODELS}

@app.post("/query")
def query(q: Query):
    agent = route(q.message)
    model = MODELS[agent]

    r = requests.post(
        f"{OLLAMA_BASE_URL}/api/generate",
        json={"model": model, "prompt": q.message, "stream": False},
        timeout=180,
    )
    r.raise_for_status()
    j = r.json()

    return {
        "agent": agent,
        "model": model,
        "response": j.get("response", "").strip(),
    }
