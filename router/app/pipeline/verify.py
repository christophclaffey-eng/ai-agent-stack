from typing import List, Dict

VERIFY_SYSTEM = """You are a CODE VERIFIER.
You will receive proposed source code files.
Return a JSON object only:
{
  "pass": true/false,
  "issues": [{"severity":"low|med|high","file":"...","line":"?","message":"..."}],
  "suggested_fixes": [{"file":"...","patch":"..."}]
}
Be strict. Prefer correctness and safety.
No markdown. JSON only.
"""

def verify_messages(task: str, bundle_text: str) -> List[Dict[str, str]]:
    return [
        {"role": "system", "content": VERIFY_SYSTEM},
        {"role": "user", "content": f"Task:\n{task}\n\nProposed files:\n{bundle_text}"},
    ]
