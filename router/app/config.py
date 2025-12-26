import os

def env(name: str, default: str = "") -> str:
    return os.environ.get(name, default)

ROUTER_PORT = int(env("ROUTER_PORT", "8010"))

OLLAMA_BASE_URL = env("OLLAMA_BASE_URL", "http://ollama:11434")
GWEN_MODEL = env("GWEN_MODEL", "qwen2.5-coder:7b-instruct")
REPRO_MODEL = env("REPRO_MODEL", "qwen2.5:7b-instruct")
SECURITY_MODEL = env("SECURITY_MODEL", "qwen2.5:7b-instruct")

ZAI_BASE_URL = env("ZAI_BASE_URL", "https://api.z.ai/v1")
ZAI_API_KEY = env("ZAI_API_KEY", "")
GLM_MODEL = env("GLM_MODEL", "glm-4.6")

AUTHOR_IS_REMOTE = env("AUTHOR_IS_REMOTE", "true").lower() == "true"
FINAL_OUTPUT_LOCAL_ONLY = env("FINAL_OUTPUT_LOCAL_ONLY", "true").lower() == "true"

WORKSPACE_DIR = "/app/workspace"
INCOMING_DIR = f"{WORKSPACE_DIR}/incoming"
APPROVED_DIR = f"{WORKSPACE_DIR}/approved"
REJECTED_DIR = f"{WORKSPACE_DIR}/rejected"
REPORTS_DIR = f"{WORKSPACE_DIR}/reports"
