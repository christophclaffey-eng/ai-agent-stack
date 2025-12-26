from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import requests
import os
import json

app = FastAPI()

OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://ollama:11434")

MODELS = {
    "fast": os.getenv("MODEL_FAST", "llama3.1:8b-instruct"),
    "reasoning": os.getenv("MODEL_REASONING", "qwen2.5:14b-instruct"),
}

class Query(BaseModel):
    message: str

class CodeTask(BaseModel):
    task: str
    author: str = None

def safe_json_loads(json_string):
    """Safely parse JSON string, returning None if invalid"""
    try:
        if json_string is None or json_string == "":
            return None
        return json.loads(json_string)
    except (json.JSONDecodeError, TypeError, ValueError) as e:
        print(f"Error parsing JSON: {e}")
        return None

def route(message: str) -> str:
    m = message.lower()
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

@app.post("/task/code")
def task_code(task: CodeTask):
    """Handle code generation tasks"""
    try:
        author_raw = task.author
        author_obj = safe_json_loads(author_raw) if author_raw else None
        
        model = MODELS["reasoning"]
        
        prompt = f"Generate code for: {task.task}"
        if author_obj:
            prompt = f"[Author: {author_obj}] {prompt}"
        
        r = requests.post(
            f"{OLLAMA_BASE_URL}/api/generate",
            json={"model": model, "prompt": prompt, "stream": False},
            timeout=180,
        )
        r.raise_for_status()
        j = r.json()
        
        return {
            "task": task.task,
            "author": author_obj,
            "model": model,
            "code": j.get("response", "").strip(),
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
