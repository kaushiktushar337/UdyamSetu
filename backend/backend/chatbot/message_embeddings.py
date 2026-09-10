import os
import numpy as np
import psycopg2
from dotenv import load_dotenv
from sentence_transformers import SentenceTransformer
from pgvector.psycopg2 import register_vector

load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")
MODEL_NAME = os.getenv("MODEL_NAME", "paraphrase-multilingual-MiniLM-L12-v2")
model = SentenceTransformer(MODEL_NAME)

def store_message_embedding(message_id, message_text):
    embedding = np.asarray(
        model.encode(message_text, normalize_embeddings=True),
        dtype=np.float32
    )

    if len(embedding) != 384:
        raise ValueError("Embedding must have exactly 384 dimensions")

    conn = psycopg2.connect(DATABASE_URL)
    register_vector(conn)
    cursor = conn.cursor()

    try:
        cursor.execute("""
            INSERT INTO embeddings (message_id, embedding_vector, model_name)
            VALUES (%s, %s, %s)
        """, (message_id, embedding, MODEL_NAME))
        conn.commit()
        return embedding
    except Exception:
        conn.rollback()
        raise
    finally:
        cursor.close()
        conn.close()
