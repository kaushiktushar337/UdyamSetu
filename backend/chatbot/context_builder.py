from __future__ import annotations
from typing import Iterable
from .config import settings
from .schemas import RetrievedDocument

class ContextBuilder:
    def __init__(self, threshold: float | None = None, max_chars: int | None = None):
        self.threshold = settings.similarity_threshold if threshold is None else threshold
        self.max_chars = settings.max_context_chars if max_chars is None else max_chars

    def build(self, documents: Iterable[RetrievedDocument]) -> tuple[str, list[RetrievedDocument]]:
        accepted = [d for d in documents if d.similarity >= self.threshold]
        accepted.sort(key=lambda d: d.similarity, reverse=True)

        parts = []
        used = []
        used_chars = 0
        for doc in accepted:
            block = f"[Source {doc.document_id}: {doc.title}]\n{doc.content.strip()}\n"
            remaining = self.max_chars - used_chars
            if remaining <= 0:
                break
            if len(block) > remaining:
                block = block[:remaining]
            parts.append(block)
            used.append(doc)
            used_chars += len(block)

        return "\n\n".join(parts), used
