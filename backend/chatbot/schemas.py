from __future__ import annotations
from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any

@dataclass
class RetrievedDocument:
    document_id: int
    title: str
    content: str
    similarity: float

@dataclass
class ChatMessage:
    role: str
    content: str
    message_id: Optional[int] = None
    created_at: Optional[str] = None

@dataclass
class ChatRequest:
    message: str
    conversation_id: Optional[str] = None
    user_id: Optional[str] = None

@dataclass
class ChatResponse:
    conversation_id: str
    answer: str
    sources: List[Dict[str, Any]] = field(default_factory=list)
    used_context: bool = False
    model: Optional[str] = None
