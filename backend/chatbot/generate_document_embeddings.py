import os
import numpy as np
import psycopg2
from dotenv import load_dotenv
from sentence_transformers import SentenceTransformer
from pgvector.psycopg2 import register_vector

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
    cursor.execute("""
        SELECT id, title, content
        FROM knowledge_documents
        WHERE is_active = true
        ORDER BY id
    """)
    documents = cursor.fetchall()
    print(f"Found {len(documents)} active documents")

    for document_id, title, content in documents:
        text = f"{title}\n\n{content or ''}"
        embedding = np.asarray(
            model.encode(text, normalize_embeddings=True),
            dtype=np.float32
        )

        if len(embedding) != 384:
            raise ValueError(f"Document {document_id}: expected 384 dimensions, got {len(embedding)}")

        cursor.execute("""
            DELETE FROM embeddings
            WHERE document_id = %s AND model_name = %s
        """, (document_id, MODEL_NAME))

        cursor.execute("""
            INSERT INTO embeddings (document_id, embedding_vector, model_name)
            VALUES (%s, %s, %s)
        """, (document_id, embedding, MODEL_NAME))

        print(f"✓ Embedded {document_id}: {title}")

    conn.commit()

    cursor.execute("""
        SELECT COUNT(*) FROM embeddings
        WHERE document_id IS NOT NULL AND model_name = %s
    """, (MODEL_NAME,))
    print(f"SUCCESS: {cursor.fetchone()[0]} document embeddings stored")

except Exception:
    conn.rollback()
    raise
finally:
    cursor.close()
    conn.close()
