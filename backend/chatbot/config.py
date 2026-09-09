from __future__ import annotations
import os
from dataclasses import dataclass
from dotenv import load_dotenv
load_dotenv()

@dataclass(frozen=True)
class ChatbotSettings:
    database_url: str | None = os.getenv("DATABASE_URL")
    embedding_model: str = os.getenv("MODEL_NAME", "paraphrase-multilingual-MiniLM-L12-v2")
    openrouter_api_key: str | None = os.getenv("OPENROUTER_API_KEY")
    openrouter_model: str = os.getenv("OPENROUTER_MODEL", "openrouter/free")
    openrouter_base_url: str = os.getenv("OPENROUTER_BASE_URL", "https://openrouter.ai/api/v1/chat/completions")
    similarity_limit: int = int(os.getenv("CHATBOT_SIMILARITY_LIMIT", "3"))
    similarity_threshold: float = float(os.getenv("CHATBOT_SIMILARITY_THRESHOLD", "0.35"))
    max_context_chars: int = int(os.getenv("CHATBOT_MAX_CONTEXT_CHARS", "6500"))
    max_history_messages: int = int(os.getenv("CHATBOT_MAX_HISTORY_MESSAGES", "8"))
    request_timeout: int = int(os.getenv("OPENROUTER_TIMEOUT", "45"))
    max_output_tokens: int = int(os.getenv("OPENROUTER_MAX_TOKENS", "600"))
settings = ChatbotSettings()
