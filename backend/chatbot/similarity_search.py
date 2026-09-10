from __future__ import annotations
import numpy as np
from .config import settings
from .schemas import RetrievedDocument
_model = None


def _get_model():
    global _model

    if _model is None:
        from sentence_transformers import SentenceTransformer

        _model = SentenceTransformer(
            settings.embedding_model
        )

    return _model
def preload_model():
    """
    Load the embedding model during application startup
    instead of waiting for the first chatbot request.
    """
    model = _get_model()

    # Small validation to ensure the expected model is loaded.
    test_embedding = model.encode(
        "UdyamSetu startup check",
        normalize_embeddings=True
    )

    if len(test_embedding) != 384:
        raise RuntimeError(
            f"Embedding model returned {len(test_embedding)} dimensions; "
            "expected 384."
        )

    return model
def _column(cursor, table: str, candidates: tuple[str, ...]) -> str | None:
    cursor.execute("SELECT column_name FROM information_schema.columns WHERE table_schema='public' AND table_name=%s", (table,))
    cols = {r[0] for r in cursor.fetchall()}
    return next((c for c in candidates if c in cols), None)

def search_knowledge(query: str, limit: int | None = None) -> list[RetrievedDocument]:
    if not settings.database_url:
        return []
    import psycopg2
    from pgvector.psycopg2 import register_vector
    vector = np.asarray(_get_model().encode(query, normalize_embeddings=True), dtype=np.float32)
    if len(vector) != 384:
        raise ValueError(f"Query embedding must be 384 dimensions, got {len(vector)}")
    conn = psycopg2.connect(settings.database_url)
    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT EXISTS (SELECT 1 FROM knowledge_documents WHERE is_active = true) AND EXISTS (SELECT 1 FROM embeddings WHERE document_id IS NOT NULL)")
            if not cursor.fetchone()[0]:
                return []
            register_vector(conn)
            embedding_col = _column(cursor, "embeddings", ("embedding", "embedding_vector"))
            model_col = _column(cursor, "embeddings", ("model_name", "model"))
            if not embedding_col:
                return []
            where = "kd.is_active = true AND e.document_id IS NOT NULL"
            params: list = []
            if model_col:
                where += f" AND e.{model_col} = %s"
                params.append(settings.embedding_model)
            params.extend([vector, vector, limit or settings.similarity_limit])
            cursor.execute(
                f"""SELECT e.document_id, kd.title, kd.content, 1 - (e.{embedding_col} <=> %s) AS similarity
                    FROM embeddings e JOIN knowledge_documents kd ON e.document_id = kd.id
                    WHERE {where}
                    ORDER BY e.{embedding_col} <=> %s LIMIT %s""",
                params,
            )
            return [RetrievedDocument(document_id=r[0], title=r[1] or "", content=r[2] or "", similarity=float(r[3] or 0)) for r in cursor.fetchall()]
    finally:
        conn.close()
