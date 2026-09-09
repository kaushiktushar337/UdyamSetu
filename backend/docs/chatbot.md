# AI Assistant

The UdyamSetu assistant combines conversation memory, multilingual embeddings, PostgreSQL/pgvector retrieval, funding context, and an OpenRouter-hosted language model.

## Local setup

Install the single backend dependency file from `backend/requirements.txt`, then create `backend/.env` from `backend/.env.example`.

Start the API from the `backend` directory:

```powershell
.\.venv\Scripts\python.exe -m uvicorn api.main:app --reload --host 0.0.0.0 --port 8000
```

The frontend sends chat messages to `/api/chat`.

## Embeddings

Document embeddings use `paraphrase-multilingual-MiniLM-L12-v2` and a 384-dimensional vector. The helper scripts in `backend/chatbot/` can generate and test document embeddings against the project's PostgreSQL/pgvector setup.

## Memory

Conversation history is handled by the conversation manager and is designed to use the database message/conversation tables when they are available.

## Funding context

Funding-related questions can retrieve active records from `scheme_rules` and `loan_plans` and pass their stored values into the assistant as structured context.

## Security

Keep `backend/.env` out of source control. Never commit database credentials or API keys.
