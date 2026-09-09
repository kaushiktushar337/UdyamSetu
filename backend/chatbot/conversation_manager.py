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
        if not self.database_url: return None
        import psycopg2
        return psycopg2.connect(self.database_url)

    def _ensure_conversation(self, conn, conversation_id: str, user_id: str | None):
        from psycopg2 import sql
        with conn.cursor() as cur:
            cur.execute("SELECT 1 FROM conversations WHERE conversation_id=%s", (conversation_id,))
            if cur.fetchone(): return
            # If user_id is absent, this is only safe when the DB permits NULL; the agreed schema requires a user.
            if not user_id: return
            cur.execute("""INSERT INTO conversations (conversation_id,user_id,title,created_at,updated_at,is_active)
                           VALUES (%s,%s,%s,CURRENT_TIMESTAMP,CURRENT_TIMESTAMP,TRUE)""", (conversation_id,user_id,"UdyamSetu Chat"))

    def get_history(self, conversation_id: str) -> list[dict]:
        if not self.database_url:
            return [{"role": m.role, "content": m.content} for m in self._memory[conversation_id][-self.max_history:]]
        try:
            conn=self._connect()
            from psycopg2.extras import Json
            with conn.cursor() as cur:
                cur.execute("""SELECT role,content FROM messages WHERE conversation_id=%s ORDER BY message_index ASC LIMIT %s""", (conversation_id,self.max_history))
                rows=cur.fetchall()
            conn.close()
            if rows: return [{"role": str(r[0]), "content": str(r[1])} for r in rows]
        except Exception:
            pass
        return [{"role": m.role, "content": m.content} for m in self._memory[conversation_id][-self.max_history:]]

    def add_message(self, conversation_id: str, role: str, content: str, user_id: str | None = None, metadata: dict | None = None) -> None:
        msg=ChatMessage(role=role,content=content,created_at=datetime.now(timezone.utc).isoformat())
        self._memory[conversation_id].append(msg)
        if not self.database_url: return
        try:
            conn=self._connect()
            from psycopg2.extras import Json
            with conn.cursor() as cur:
                self._ensure_conversation(conn, conversation_id, user_id)
                cur.execute("SELECT COALESCE(MAX(message_index), -1)+1 FROM messages WHERE conversation_id=%s", (conversation_id,))
                idx=cur.fetchone()[0]
                cur.execute("""INSERT INTO messages (conversation_id,role,content,message_index,created_at,metadata)
                               VALUES (%s,%s,%s,%s,CURRENT_TIMESTAMP,%s)""", (conversation_id,role,content,idx,Json(metadata or {})))
                cur.execute("UPDATE conversations SET updated_at=CURRENT_TIMESTAMP WHERE conversation_id=%s", (conversation_id,))
            conn.commit(); conn.close()
        except Exception:
            try: conn.rollback(); conn.close()
            except Exception: pass
