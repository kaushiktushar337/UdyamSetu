"""
Conversation memory.

The original chatbot package already implies an `embeddings.message_id` relationship,
but the exact conversation/message schema was not included in the supplied backend.
This manager therefore:
1. Uses PostgreSQL persistence when compatible conversation/message tables exist.
2. Detects table/column names through information_schema rather than hard-coding an
   unsupported schema.
3. Falls back to in-memory memory for development/testing.

This keeps the chatbot runnable now while allowing exact database persistence after
the database team's final conversation tables are confirmed.
"""
from __future__ import annotations
from collections import defaultdict
from datetime import datetime, timezone
from uuid import uuid4
from .config import settings
from .schemas import ChatMessage

class ConversationManager:
    def __init__(self, database_url: str | None = None, max_history: int | None = None):
        self.database_url = database_url if database_url is not None else settings.database_url
        self.max_history = max_history or settings.max_history_messages
        self._memory = defaultdict(list)

    def new_conversation_id(self) -> str:
        return str(uuid4())

    def _connect(self):
        if not self.database_url:
            return None
        import psycopg2
        return psycopg2.connect(self.database_url)

    def _table_columns(self, cursor, table: str) -> set[str]:
        cursor.execute("""
            SELECT column_name
            FROM information_schema.columns
            WHERE table_schema = 'public' AND table_name = %s
        """, (table,))
        return {r[0] for r in cursor.fetchall()}

    def _resolve_message_schema(self, cursor):
        for table in ("messages", "chat_messages", "conversation_messages"):
            cols = self._table_columns(cursor, table)
            if not cols:
                continue
            content = next((c for c in ("content", "message_text", "message") if c in cols), None)
            role = next((c for c in ("role", "sender_role") if c in cols), None)
            conversation = next((c for c in ("conversation_id", "session_id") if c in cols), None)
            created = next((c for c in ("created_at", "timestamp") if c in cols), None)
            if content and role and conversation:
                return table, content, role, conversation, created
        return None

    def get_history(self, conversation_id: str) -> list[dict]:
        if not self.database_url:
            return [{"role": m.role, "content": m.content} for m in self._memory[conversation_id][-self.max_history:]]

        try:
            conn = self._connect()
            cursor = conn.cursor()
            schema = self._resolve_message_schema(cursor)
            if not schema:
                cursor.close(); conn.close()
                return [{"role": m.role, "content": m.content} for m in self._memory[conversation_id][-self.max_history:]]

            table, content, role, conversation, created = schema
            order = f"{created} DESC" if created else "id DESC"
            cursor.execute(
                f"SELECT {role}, {content} FROM {table} WHERE {conversation} = %s ORDER BY {order} LIMIT %s",
                (conversation_id, self.max_history),
            )
            rows = list(reversed(cursor.fetchall()))
            cursor.close(); conn.close()
            return [{"role": str(r[0]), "content": str(r[1])} for r in rows]
        except Exception:
            return [{"role": m.role, "content": m.content} for m in self._memory[conversation_id][-self.max_history:]]

    def add_message(self, conversation_id: str, role: str, content: str) -> None:
        msg = ChatMessage(role=role, content=content, created_at=datetime.now(timezone.utc).isoformat())
        self._memory[conversation_id].append(msg)

        if not self.database_url:
            return

        try:
            conn = self._connect()
            cursor = conn.cursor()
            schema = self._resolve_message_schema(cursor)
            if not schema:
                cursor.close(); conn.close()
                return

            table, content_col, role_col, conversation_col, _ = schema
            cursor.execute(
                f"INSERT INTO {table} ({conversation_col}, {role_col}, {content_col}) VALUES (%s, %s, %s)",
                (conversation_id, role, content),
            )
            conn.commit()
            cursor.close(); conn.close()
        except Exception:
            # The in-memory copy remains available so a temporary DB issue does not
            # break the chat response itself.
            pass
