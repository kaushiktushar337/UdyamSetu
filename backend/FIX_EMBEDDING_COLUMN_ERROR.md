# Fix: embeddings column mismatch

The live database error showed:

`psycopg2.errors.UndefinedColumn: column e.embedding_vector does not exist`

The database currently uses `embeddings.embedding`.

The chatbot has been updated to detect the embedding column at runtime through
`information_schema.columns`, supporting both:

- `embedding`
- `embedding_vector`

This fix was applied to:
- similarity_search.py
- generate_document_embeddings.py
- message_embeddings.py

No database migration is required for this fix.
