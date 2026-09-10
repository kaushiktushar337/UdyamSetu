from __future__ import annotations
import re
from .config import settings
from .schemas import RetrievedDocument

def _column(cursor, table: str, candidates: tuple[str, ...]) -> str | None:
    cursor.execute("SELECT column_name FROM information_schema.columns WHERE table_schema='public' AND table_name=%s", (table,))
    cols = {r[0] for r in cursor.fetchall()}
    return next((c for c in candidates if c in cols), None)

def search_knowledge(query: str, limit: int | None = None) -> list[RetrievedDocument]:
    """Lightweight PostgreSQL full-text retrieval for Vercel.

    It deliberately avoids pgvector/numpy/transformer dependencies. Existing
    chunk-level embeddings remain intact in PostgreSQL and can still be used by
    the full ML deployment.
    """
    if not settings.database_url:
        return []
    import psycopg2
    conn = psycopg2.connect(settings.database_url)
    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT EXISTS (SELECT 1 FROM knowledge_documents WHERE is_active = true)")
            if not cursor.fetchone()[0]:
                return []
            lim = int(limit or settings.similarity_limit)
            cursor.execute(
                """SELECT kd.id, kd.title, kd.content,
                   ts_rank_cd(to_tsvector('simple', coalesce(kd.title,'') || ' ' || coalesce(kd.content,'')),
                              plainto_tsquery('simple', %s)) AS score
                   FROM knowledge_documents kd
                   WHERE kd.is_active = true
                     AND to_tsvector('simple', coalesce(kd.title,'') || ' ' || coalesce(kd.content,'')) @@ plainto_tsquery('simple', %s)
                   ORDER BY score DESC, kd.id DESC
                   LIMIT %s""",
                (query, query, lim),
            )
            rows = cursor.fetchall()
            if rows:
                return [RetrievedDocument(document_id=r[0], title=r[1] or '', content=r[2] or '', similarity=float(r[3] or 0)) for r in rows]
            # Small fallback for short queries/Indian terms that PostgreSQL's
            # simple parser may not tokenize usefully.
            tokens = [t for t in re.findall(r"\w+", query.lower(), re.UNICODE) if len(t) >= 3][:8]
            if not tokens:
                return []
            clauses = " OR ".join(["lower(coalesce(kd.title,'') || ' ' || coalesce(kd.content,'')) LIKE %s"] * len(tokens))
            params = [f"%{t}%" for t in tokens] + [lim]
            cursor.execute(f"""SELECT kd.id, kd.title, kd.content, 0.1 AS score
                               FROM knowledge_documents kd
                               WHERE kd.is_active = true AND ({clauses})
                               ORDER BY kd.id DESC LIMIT %s""", params)
            return [RetrievedDocument(document_id=r[0], title=r[1] or '', content=r[2] or '', similarity=float(r[3] or 0)) for r in cursor.fetchall()]
    finally:
        conn.close()
