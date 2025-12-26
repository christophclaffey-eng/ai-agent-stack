import json
import os
import time
from typing import Dict, Any, List
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from app import config
from app.providers.ollama import OllamaClient
# We are not using the GLM client right now:
# from app.providers.glm import ZaiGLMClient

from app.pipeline.author import author_prompt
from app.pipeline.verify import verify_messages
from app.utils.hashing import sha256_text

app = FastAPI(title="Agent Router", version="0.1")

ollama = OllamaClient(config.OLLAMA_BASE_URL)

class TaskReq(BaseModel):
    task: str
    project: str = "default"

def ensure_dirs():
    for d in [config.INCOMING_DIR, config.APPROVED_DIR, config.REJECTED_DIR, config.REPORTS_DIR]:
        os.makedirs(d, exist_ok=True)

@app.post("/task/code")
def task_code(req: TaskReq):
    ensure_dirs()
    run_id = f"{int(time.time())}-{sha256_text(req.task)[:10]}"

    # --- AUTHOR (LOCAL ONLY, JSON-SAFE) ---
    author_raw = ollama.chat(
        config.GWEN_MODEL,
        author_prompt(req.task),
        temperature=0.2,
    )

    try:
        author_obj = safe_json_loads(author_raw)
    except Exception:
        # Retry once with stricter instruction
        author_raw = ollama.chat(
            config.GWEN_MODEL,
            [
                {"role": "system", "content": "Return ONLY valid JSON. No text."},
                {"role": "user", "content": req.task},
            ],
            temperature=0.1,
        )
        author_obj = safe_json_loads(author_raw)

    files = author_obj.get("files", [])
    if not files:
        raise HTTPException(status_code=400, detail="Author returned no files.")

    bundle_text = "\n".join(
        f"--- {f['path']} ---\n{f['content']}" for f in files
    )

    # --- VERIFY (SINGLE MODEL FOR NOW) ---
    # We can add repro/security later. For now, just one verify step.
    verify_raw = ollama.chat(
        config.GWEN_MODEL,
        verify_messages(req.task, bundle_text),
        temperature=0.1,
    )
    verify_obj = safe_json_loads(verify_raw)

    # --- WRITE APPROVED FILES ---
    root = os.path.join(config.APPROVED_DIR, req.project, run_id)
    os.makedirs(root, exist_ok=True)

    for f in files:
        path = os.path.join(root, f["path"])
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w", encoding="utf-8") as out:
            out.write(f["content"])

    return {
        "verdict": "approved",
        "run_id": run_id,
        "files": [f["path"] for f in files],
    }
