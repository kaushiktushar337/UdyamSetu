# UdyamSetu Complete Chatbot

## Full flow

User message
→ semantic embedding (384 dimensions)
→ pgvector retrieval from `knowledge_documents` + `embeddings`
→ relevance filtering and context building
→ conversation memory
→ OpenRouter chat completion
→ grounded response + source metadata

## Database contract confirmed from the existing chatbot files

### knowledge_documents
The existing retrieval code uses:
- id
- title
- content
- is_active

### embeddings
The existing retrieval/message embedding code uses:
- document_id
- message_id
- embedding_vector
- model_name

The supplied backend did not include the final conversation/message table DDL. The
ConversationManager therefore detects compatible message tables at runtime
(`messages`, `chat_messages`, or `conversation_messages`) and falls back to
in-memory conversation memory if those tables are absent. This prevents us from
inventing columns that may conflict with the database team's schema.

## Run tests

```bash
python -m unittest chatbot.tests.test_chatbot_pipeline -v
```

## Run CLI

```bash
python -m chatbot.cli_chat
```

## Environment

Copy `.env.example` to `.env` in the backend root and set DATABASE_URL and
OPENROUTER_API_KEY.
