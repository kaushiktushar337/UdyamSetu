import os
import numpy as np
import psycopg2
from dotenv import load_dotenv
from sentence_transformers import SentenceTransformer
from pgvector.psycopg2 import register_vector
from chatbot.db_schema import get_embeddings_columns, resolve_embedding_column, resolve_model_column

load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")
MODEL_NAME = os.getenv("MODEL_NAME", "paraphrase-multilingual-MiniLM-L12-v2")
if not DATABASE_URL:
    raise ValueError("DATABASE_URL is missing from .env")
model = SentenceTransformer(MODEL_NAME)

def store_message_embedding(message_id, message_text):
    embedding = np.asarray(model.encode(message_text, normalize_embeddings=True), dtype=np.float32)
    if len(embedding) != 384:
        raise ValueError("Embedding must have exactly 384 dimensions")

    conn = psycopg2.connect(DATABASE_URL)
    register_vector(conn)
    cursor = conn.cursor()
    try:
        columns = get_embeddings_columns(cursor)
        if 'message_id' not in columns:
            raise RuntimeError("The current embeddings table has no message_id column; message embeddings are not enabled in this database schema.")
        embedding_column = resolve_embedding_column(cursor)
        model_column = resolve_model_column(cursor)
        if model_column:
            cursor.execute(
                f"INSERT INTO embeddings (message_id, {embedding_column}, {model_column}) VALUES (%s, %s, %s)",
                (message_id, embedding, MODEL_NAME),
            )
        else:
            cursor.execute(
                f"INSERT INTO embeddings (message_id, {embedding_column}) VALUES (%s, %s)",
                (message_id, embedding),
            )
        conn.commit()
        return embedding
    except Exception:
        conn.rollback(); raise
    finally:
        cursor.close(); conn.close()
