import requests
from typing import List, Dict, Any

class OllamaClient:
    def __init__(self, base_url: str):
        self.base_url = base_url.rstrip("/")

    def chat(
        self,
        model: str,
        messages: List[Dict[str, str]],
        temperature: float = 0.2,
    ) -> str:
        """
        Ollama-compatible chat wrapper using /api/generate
        """
        url = f"{self.base_url}/api/generate"

        # Convert chat messages → single prompt
        prompt_parts = []
        for m in messages:
            role = m.get("role", "user")
            content = m.get("content", "")
            prompt_parts.append(f"{role.upper()}:\n{content}")

        prompt = "\n\n".join(prompt_parts) + "\n\nASSISTANT:\n"

        payload: Dict[str, Any] = {
            "model": model,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": temperature,
            },
        }

        r = requests.post(url, json=payload, timeout=300)
        r.raise_for_status()
        data = r.json()

        if "response" not in data:
            raise RuntimeError(f"Unexpected Ollama response: {data}")

        return data["response"]
