from typing import List, Dict

REPRO_SYSTEM = """You are a REPRODUCER.
Recreate the solution from scratch based ONLY on the task description.
Return a JSON object only:
{
  "files": [{"path":"relative/path.ext","content":"..."}],
  "notes":"..."
}
No markdown. JSON only.
"""

def reproduce_messages(task: str) -> List[Dict[str, str]]:
    return [
        {"role": "system", "content": REPRO_SYSTEM},
        {"role": "user", "content": task.strip()},
    ]
