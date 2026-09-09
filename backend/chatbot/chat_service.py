from __future__ import annotations
from .schemas import ChatRequest, ChatResponse
from .similarity_search import search_knowledge
from .context_builder import ContextBuilder
from .conversation_manager import ConversationManager
from .response_generator import OpenRouterResponseGenerator

class ChatService:
    def __init__(self, retriever=None, context_builder=None, memory=None, generator=None, funding_provider=None):
        self.retriever = retriever or search_knowledge
        self.context_builder = context_builder or ContextBuilder()
        self.memory = memory or ConversationManager()
        self.generator = generator or OpenRouterResponseGenerator()
        self.funding_provider = funding_provider

    def chat(self, request: ChatRequest) -> ChatResponse:
        message = request.message.strip()
        if not message:
            raise ValueError("Message cannot be empty")

        conversation_id = request.conversation_id or self.memory.new_conversation_id()
        history = self.memory.get_history(conversation_id)

        documents = self.retriever(message)
        context, used_documents = self.context_builder.build(documents)
        if self.funding_provider:
            try:
                is_funding_query = getattr(self.funding_provider, "is_funding_query", lambda _text: True)
                if is_funding_query(message):
                    funding_context = self.funding_provider.chat_context(message, request.location_text)
                    if funding_context:
                        context = (context + "\n\n" + funding_context).strip()
            except Exception:
                # Funding tables are optional; general RAG chat must continue if they are unavailable.
                pass

        try:
            answer = self.generator.generate(
                user_message=message, context=context, history=history, location_text=request.location_text
            )
        except TypeError as exc:
            # Keep compatibility with lightweight test/custom generators that use the original signature.
            if "location_text" not in str(exc):
                raise
            answer = self.generator.generate(user_message=message, context=context, history=history)

        self.memory.add_message(conversation_id, "user", message, user_id=request.user_id)
        self.memory.add_message(conversation_id, "assistant", answer, user_id=request.user_id, metadata={"sources": [{"document_id": d.document_id, "title": d.title, "similarity": round(d.similarity, 4)} for d in used_documents], "model": getattr(self.generator, "model", None)})

        return ChatResponse(
            conversation_id=conversation_id,
            answer=answer,
            sources=[
                {
                    "document_id": d.document_id,
                    "title": d.title,
                    "similarity": round(d.similarity, 4),
                }
                for d in used_documents
            ],
            used_context=bool(used_documents),
            model=getattr(self.generator, "model", None),
        )
