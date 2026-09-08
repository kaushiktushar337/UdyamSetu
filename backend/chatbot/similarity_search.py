"""Knowledge retrieval using the actual UdyamSetu embeddings schema."""
from __future__ import annotations
import numpy as np
from .config import settings
from .schemas import RetrievedDocument
from .db_schema import resolve_embedding_column, resolve_model_column

_model = None

def _get_model():
    global _model
    if _model is None:
        from sentence_transformers import SentenceTransformer
        _model = SentenceTransformer(settings.embedding_model)
    return _model

def search_knowledge(query: str, limit: int | None = None) -> list[RetrievedDocument]:
    if not settings.database_url:
        raise ValueError("DATABASE_URL is missing from .env")

    import psycopg2
    from pgvector.psycopg2 import register_vector

    vector = np.asarray(_get_model().encode(query, normalize_embeddings=True), dtype=np.float32)
    if len(vector) != 384:
        raise ValueError(f"Query embedding must have 384 dimensions, got {len(vector)}")

    conn = psycopg2.connect(settings.database_url)
    register_vector(conn)
    cursor = conn.cursor()
    try:
        embedding_column = resolve_embedding_column(cursor)
        model_column = resolve_model_column(cursor)

        where = "kd.is_active = true AND e.document_id IS NOT NULL"
        params = [vector]
        if model_column:
            where += f" AND e.{model_column} = %s"
            params.append(settings.embedding_model)
        params.extend([vector, limit or settings.similarity_limit])

        sql = f"""
            SELECT
                e.document_id,
                kd.title,
                kd.content,
                1 - (e.{embedding_column} <=> %s) AS similarity
            FROM embeddings e
            JOIN knowledge_documents kd ON e.document_id = kd.id
            WHERE {where}
            ORDER BY e.{embedding_column} <=> %s
            LIMIT %s
        """
        cursor.execute(sql, tuple(params))
        return [
            RetrievedDocument(
                document_id=row[0], title=row[1] or "", content=row[2] or "",
                similarity=float(row[3] or 0),
            )
            for row in cursor.fetchall()
        ]
    finally:
        cursor.close()
        conn.close()
