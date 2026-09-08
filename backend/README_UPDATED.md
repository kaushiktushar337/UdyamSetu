# UdyamSetu Backend - Updated Structure

## Included modules

### chatbot/
Latest provided embedding/knowledge-search backend:
- generate_document_embeddings.py
- similarity_search.py
- message_embeddings.py

This module remains independent and functional.

### ml_engine/
Existing decision engine plus:
- profile_loader.py
- business_matcher.py

## Setup

1. Create and activate a virtual environment.
2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Create `.env` from the chatbot `.env.example` and configure:

```text
DATABASE_URL=postgresql://...
MODEL_NAME=paraphrase-multilingual-MiniLM-L12-v2
```

## Import prerequisite

The 40 business profiles must first be imported into:

`business_reference_profiles`

## Test profile matching

```bash
python profile_matching_demo.py
```

## Architecture

User requirements
→ BusinessMatcher
→ Top business profiles
→ Existing Financial / Market / Operational / Risk engines
→ DecisionEngine

The chatbot and decision engine remain separate modules and can later be exposed through FastAPI endpoints.
