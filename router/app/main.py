import html
import json
import os
import time
from typing import Dict, Any, List
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from fastapi.responses import HTMLResponse

from app import config
from app.providers.ollama import OllamaClient
# We are not using the GLM client right now:
# from app.providers.glm import ZaiGLMClient

from app.pipeline.author import author_prompt
from app.pipeline.verify import verify_messages
from app.utils.hashing import sha256_text

app = FastAPI(title="Agent Router", version="0.1")

ollama = OllamaClient(config.OLLAMA_BASE_URL)


DEFAULT_PROJECT = os.environ.get("DEFAULT_PROJECT", "system-34")

STATUS_DIRS = {
    "incoming": config.INCOMING_DIR,
    "approved": config.APPROVED_DIR,
    "rejected": config.REJECTED_DIR,
    "reports": config.REPORTS_DIR,
}

class TaskReq(BaseModel):
    task: str
    project: str = "default"

def safe_json_loads(json_string: str) -> Any:
    try:
        if json_string is None or json_string == "":
            raise ValueError("Empty JSON payload")
        return json.loads(json_string)
    except (json.JSONDecodeError, TypeError, ValueError):
        raise HTTPException(status_code=502, detail="Upstream model returned invalid JSON")

def ensure_dirs():
    for d in [config.INCOMING_DIR, config.APPROVED_DIR, config.REJECTED_DIR, config.REPORTS_DIR]:
        os.makedirs(d, exist_ok=True)

def preview_file(path: str, limit: int = 400) -> str:
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = f.read(limit + 1)
    except UnicodeDecodeError:
        return "<binary>"
    except FileNotFoundError:
        return ""

    if len(data) > limit:
        data = f"{data[:limit]}…"
    return data

def gather_run_files(run_path: str) -> List[Dict[str, Any]]:
    collected: List[Dict[str, Any]] = []
    for dirpath, _, filenames in os.walk(run_path):
        for filename in filenames:
            full = os.path.join(dirpath, filename)
            rel = os.path.relpath(full, run_path)
            collected.append(
                {
                    "path": rel,
                    "size": os.path.getsize(full),
                    "preview": preview_file(full),
                }
            )
    collected.sort(key=lambda f: f["path"])
    return collected

def list_runs(status_dir: str, project: str) -> List[Dict[str, Any]]:
    project_root = os.path.join(status_dir, project)
    if not os.path.isdir(project_root):
        return []

    runs: List[Dict[str, Any]] = []
    for run_id in os.listdir(project_root):
        run_path = os.path.join(project_root, run_id)
        if not os.path.isdir(run_path):
            continue
        files = gather_run_files(run_path)
        runs.append(
            {
                "run_id": run_id,
                "last_updated": int(os.path.getmtime(run_path)),
                "file_count": len(files),
                "files": files,
            }
        )

    runs.sort(key=lambda r: r["last_updated"], reverse=True)
    return runs

def dashboard_summary(project: str, limit: int) -> Dict[str, Any]:
    ensure_dirs()
    limit = max(1, min(limit, 50))

    snapshot: Dict[str, Any] = {
        "project": project,
        "workspace": config.WORKSPACE_DIR,
        "default_models": {
            "author": config.GWEN_MODEL,
            "reproduce": config.REPRO_MODEL,
            "security": config.SECURITY_MODEL,
        },
        "status": {},
        "timestamp": int(time.time()),
    }

    for status, path in STATUS_DIRS.items():
        runs = list_runs(path, project)
        snapshot["status"][status] = {
            "root": os.path.join(path, project),
            "total_runs": len(runs),
            "latest": runs[:limit],
        }

    return snapshot

def dashboard_run_detail(status: str, project: str, run_id: str) -> Dict[str, Any]:
    if status not in STATUS_DIRS:
        raise HTTPException(status_code=404, detail=f"Unknown status '{status}'")

    run_path = os.path.join(STATUS_DIRS[status], project, run_id)
    if not os.path.isdir(run_path):
        raise HTTPException(status_code=404, detail=f"Run '{run_id}' not found")

    files = gather_run_files(run_path)
    return {
        "status": status,
        "project": project,
        "run_id": run_id,
        "path": run_path,
        "file_count": len(files),
        "files": files,
        "last_updated": int(os.path.getmtime(run_path)),
    }

def format_timestamp(ts: int) -> str:
    return time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(ts))

def render_dashboard_html(summary: Dict[str, Any]) -> HTMLResponse:
    lines: List[str] = [
        "<html>",
        "<head>",
        "<title>System 34 Command Center</title>",
        "<style>body{font-family:Arial,sans-serif;margin:24px;}h1{color:#0f172a;}",
        "section{margin-bottom:24px;}ul{padding-left:18px;}code{background:#f1f5f9;padding:2px 4px;}",
        "small{color:#475569;}</style>",
        "</head>",
        "<body>",
        f"<h1>System 34 Command Center</h1>",
        f"<p><strong>Project:</strong> {html.escape(summary['project'])} | "
        f"<strong>Workspace:</strong> {html.escape(summary['workspace'])}</p>",
        "<section>",
        "<h2>Model Configuration</h2>",
        "<ul>",
    ]

    for name, model in summary["default_models"].items():
        lines.append(f"<li><strong>{html.escape(name.title())}</strong>: <code>{html.escape(model)}</code></li>")

    lines.extend(["</ul>", "</section>"])

    for status, info in summary["status"].items():
        lines.append("<section>")
        lines.append(f"<h2>{html.escape(status.title())} runs</h2>")
        lines.append(
            f"<p><small>Root: {html.escape(info['root'])} | Total runs: {info['total_runs']}</small></p>"
        )
        if not info["latest"]:
            lines.append("<p>No runs recorded yet.</p>")
            lines.append("</section>")
            continue

        lines.append("<ul>")
        for run in info["latest"]:
            lines.append(
                f"<li><strong>{html.escape(run['run_id'])}</strong> — {run['file_count']} file(s) • "
                f"updated {format_timestamp(run['last_updated'])}"
            )
            if run["files"]:
                lines.append("<ul>")
                for file_info in run["files"][:3]:
                    lines.append(
                        "<li>"
                        f"<code>{html.escape(file_info['path'])}</code>"
                        f" ({file_info['size']} bytes)"
                        f"<br/><small>{html.escape(file_info['preview'])}</small>"
                        "</li>"
                    )
                if len(run["files"]) > 3:
                    lines.append(
                        f"<li><small>… {len(run['files']) - 3} more file(s) in this run</small></li>"
                    )
                lines.append("</ul>")
            lines.append("</li>")
        lines.append("</ul>")
        lines.append("</section>")

    lines.extend(["</body>", "</html>"])
    return HTMLResponse("\n".join(lines))

@app.get("/dashboard")
def dashboard(project: str = DEFAULT_PROJECT, limit: int = 5):
    return dashboard_summary(project, limit)

@app.get("/dashboard/run/{status}/{project}/{run_id}")
def dashboard_run(status: str, project: str, run_id: str):
    return dashboard_run_detail(status, project, run_id)

@app.get("/dashboard/html", response_class=HTMLResponse)
def dashboard_html(project: str = DEFAULT_PROJECT, limit: int = 5):
    summary = dashboard_summary(project, limit)
    return render_dashboard_html(summary)

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
