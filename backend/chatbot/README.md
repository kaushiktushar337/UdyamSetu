# UdyamSetu Embedding Backend

## Setup

```bash
python -m venv venv
```

Windows:

```bash
venv\Scripts\activate
```

Install:

```bash
pip install -r requirements.txt
```

Copy `.env.example` to `.env` and put your database connection string in it.

## Generate embeddings

```bash
python generate_document_embeddings.py
```

The script fetches active documents, generates 384-dimensional embeddings, stores the matching document ID and model name, and verifies the result.

## Search

```bash
python similarity_search.py
```

## Security

Never commit `.env` to GitHub.
