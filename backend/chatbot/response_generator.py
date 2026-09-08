from __future__ import annotations
import requests
from .config import settings

SYSTEM_PROMPT = """You are UdyamSetu's business assistance chatbot.
Answer helpfully and clearly. Use the supplied knowledge context when it is relevant.
Do not invent facts that are not supported by the context. If the context does not contain
enough information, say so and offer the most useful next step. You may still handle normal
conversation naturally. Keep recommendations practical for Indian entrepreneurs and small businesses.
"""

class OpenRouterResponseGenerator:
    def __init__(self, api_key: str | None = None, model: str | None = None, endpoint: str | None = None):
        self.api_key = api_key or settings.openrouter_api_key
        self.model = model or settings.openrouter_model
        self.endpoint = endpoint or settings.openrouter_base_url

    def generate(self, user_message: str, context: str = "", history: list[dict] | None = None) -> str:
        if not self.api_key:
            raise ValueError("OPENROUTER_API_KEY is missing from .env")

        messages = [{"role": "system", "content": SYSTEM_PROMPT}]
        if context:
            messages.append({
                "role": "system",
                "content": "Knowledge context for this answer:\n" + context
            })
        for item in history or []:
            role = item.get("role", "user")
            if role not in {"user", "assistant"}:
                continue
            content = str(item.get("content", "")).strip()
            if content:
                messages.append({"role": role, "content": content})
        messages.append({"role": "user", "content": user_message})

        response = requests.post(
            self.endpoint,
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
                "HTTP-Referer": "https://udyamsetu.local",
                "X-Title": "UdyamSetu",
            },
            json={"model": self.model, "messages": messages},
            timeout=settings.request_timeout,
        )

        if response.status_code >= 400:
            raise RuntimeError(f"OpenRouter request failed ({response.status_code}): {response.text[:500]}")

        data = response.json()
        try:
            content = data["choices"][0]["message"]["content"]
        except (KeyError, IndexError, TypeError) as exc:
            raise RuntimeError(f"Unexpected OpenRouter response format: {data}") from exc

        if isinstance(content, list):
            content = "".join(
                part.get("text", "") if isinstance(part, dict) else str(part)
                for part in content
            )

        answer = str(content).strip()
        if not answer:
            raise RuntimeError("OpenRouter returned an empty response")
        return answer
