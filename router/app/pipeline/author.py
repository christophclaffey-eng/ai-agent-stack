from typing import Dict, List

AUTHOR_SYSTEM = """You are the PRIMARY CODE AUTHOR.

YOU MUST FOLLOW THESE RULES EXACTLY:
- Output ONLY valid JSON
- Do NOT include markdown
- Do NOT include explanations
- Do NOT include commentary
- Do NOT include backticks
- Do NOT include anything outside the JSON object

Return EXACTLY this schema:
{
  "files": [
    {"path":"relative/path.ext","content":"..."}
  ],
  "notes": "short build/run notes"
}

If you violate the format, the output will be discarded.
"""

def author_prompt(task: str) -> List[Dict[str, str]]:
    return [
        {"role": "system", "content": AUTHOR_SYSTEM},
        {
            "role": "user",
            "content": (
                "TASK:\n"
                f"{task}\n\n"
                "IMPORTANT:\n"
                "- Respond with JSON only\n"
                "- No markdown\n"
                "- No text outside JSON\n"
            ),
        },
    ]
