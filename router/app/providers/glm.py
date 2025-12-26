import requests
from typing import List, Dict, Any

class ZaiGLMClient:
    """
    This is intentionally minimal.
    You may need to adjust the endpoint/shape to match Z.AI's current API.
    The router is built so swapping this adapter is easy.
    """
    def __init__(self, base_url: str, api_key: str):
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key

    def chat(self, model: str, messages: List[Dict[str, str]], temperature: float = 0.2) -> str:
        url = f"{self.base_url}/chat/completions"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        payload: Dict[str, Any] = {
            "model": model,
            "messages": messages,
            "temperature": temperature,
            "stream": False,
        }
        r = requests.post(url, headers=headers, json=payload, timeout=300)
        r.raise_for_status()
        data = r.json()
        # common shape: choices[0].message.content
        return data["choices"][0]["message"]["content"]
