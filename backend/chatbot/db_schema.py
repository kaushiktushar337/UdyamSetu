from __future__ import annotations

"""Runtime compatibility helpers for the UdyamSetu embeddings table.

The database team has used different column layouts during development.  We detect
what actually exists instead of assuming optional metadata columns such as
`model_name`.
"""


def get_embeddings_columns(cursor) -> set[str]:
    cursor.execute("""
        SELECT column_name
        FROM information_schema.columns
        WHERE table_schema = 'public' AND table_name = 'embeddings'
    """)
    return {row[0] for row in cursor.fetchall()}


def resolve_embedding_column(cursor) -> str:
    available = get_embeddings_columns(cursor)
    if 'embedding_vector' in available:
        return 'embedding_vector'
    if 'embedding' in available:
        return 'embedding'
    raise RuntimeError(
        "The embeddings table has neither 'embedding_vector' nor 'embedding'. "
        f"Available columns: {sorted(available)}"
    )


def resolve_model_column(cursor) -> str | None:
    """Return an optional model metadata column if the DB has one."""
    available = get_embeddings_columns(cursor)
    for name in ('model_name', 'model'):
        if name in available:
            return name
    return None
