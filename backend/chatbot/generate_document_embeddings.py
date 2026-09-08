import os
import numpy as np
import psycopg2
from dotenv import load_dotenv
from sentence_transformers import SentenceTransformer
from pgvector.psycopg2 import register_vector
from chatbot.db_schema import resolve_embedding_column, resolve_model_column

load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")
MODEL_NAME = os.getenv("MODEL_NAME", "paraphrase-multilingual-MiniLM-L12-v2")
if not DATABASE_URL:
    raise ValueError("DATABASE_URL is missing from .env")

model = SentenceTransformer(MODEL_NAME)
conn = psycopg2.connect(DATABASE_URL)
register_vector(conn)
cursor = conn.cursor()

try:
    embedding_column = resolve_embedding_column(cursor)
    model_column = resolve_model_column(cursor)

    cursor.execute("""
        SELECT id, title, content FROM knowledge_documents
        WHERE is_active = true ORDER BY id
    """)
    documents = cursor.fetchall()
    print(f"Found {len(documents)} active documents")

    for document_id, title, content in documents:
        embedding = np.asarray(model.encode(f"{title}\n\n{content or ''}", normalize_embeddings=True), dtype=np.float32)
        if len(embedding) != 384:
            raise ValueError(f"Document {document_id}: expected 384 dimensions, got {len(embedding)}")

        if model_column:
            cursor.execute(f"DELETE FROM embeddings WHERE document_id = %s AND {model_column} = %s", (document_id, MODEL_NAME))
            cursor.execute(
                f"INSERT INTO embeddings (document_id, {embedding_column}, {model_column}) VALUES (%s, %s, %s)",
                (document_id, embedding, MODEL_NAME),
            )
        else:
            cursor.execute("DELETE FROM embeddings WHERE document_id = %s", (document_id,))
            cursor.execute(
                f"INSERT INTO embeddings (document_id, {embedding_column}) VALUES (%s, %s)",
                (document_id, embedding),
            )
        print(f"Embedded {document_id}: {title}")

    conn.commit()
    cursor.execute("SELECT COUNT(*) FROM embeddings WHERE document_id IS NOT NULL")
    print(f"SUCCESS: {cursor.fetchone()[0]} document embeddings stored")
except Exception:
    conn.rollback()
    raise
finally:
    cursor.close(); conn.close()
