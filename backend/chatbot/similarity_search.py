"""
Knowledge retrieval using the existing project schema:

knowledge_documents(id, title, content, is_active)
embeddings(document_id, embedding_vector, model_name, ...)

This is a refactor of the original script into a reusable service.
"""
from __future__ import annotations
import numpy as np
from .config import settings
from .schemas import RetrievedDocument

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

    vector = np.asarray(
        _get_model().encode(query, normalize_embeddings=True),
        dtype=np.float32
    )
    if len(vector) != 384:
        raise ValueError(f"Query embedding must have 384 dimensions, got {len(vector)}")

    conn = psycopg2.connect(settings.database_url)
    register_vector(conn)
    cursor = conn.cursor()
    try:
        cursor.execute("""
            SELECT
                e.document_id,
                kd.title,
                kd.content,
                1 - (e.embedding_vector <=> %s) AS similarity
            FROM embeddings e
            JOIN knowledge_documents kd ON e.document_id = kd.id
            WHERE kd.is_active = true
              AND e.document_id IS NOT NULL
              AND e.model_name = %s
            ORDER BY e.embedding_vector <=> %s
            LIMIT %s
        """, (vector, settings.embedding_model, vector, limit or settings.similarity_limit))
        return [
            RetrievedDocument(
                document_id=row[0],
                title=row[1] or "",
                content=row[2] or "",
                similarity=float(row[3] or 0),
            )
            for row in cursor.fetchall()
        ]
    finally:
        cursor.close()
        conn.close()
