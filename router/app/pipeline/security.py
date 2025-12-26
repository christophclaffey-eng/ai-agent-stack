from typing import List, Dict

SECURITY_SYSTEM = """You are a SECURITY REVIEWER.
Find risky patterns: command injection, path traversal, unsafe deserialization,
shell=True, eval, weak auth, exposed ports, secrets, etc.
Return JSON only:
{
  "pass": true/false,
  "risks": [{"severity":"low|med|high","message":"...","file":"..."}],
  "mitigations": ["...", "..."]
}
No markdown. JSON only.
"""

def security_messages(task: str, bundle_text: str) -> List[Dict[str, str]]:
    return [
        {"role": "system", "content": SECURITY_SYSTEM},
        {"role": "user", "content": f"Task:\n{task}\n\nFiles:\n{bundle_text}"},
    ]
