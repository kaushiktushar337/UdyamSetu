# UdyamSetu Backend

FastAPI backend for the UdyamSetu AI assistant, business insights, ASUSE ML model, Decision Engine, live location services, and funding recommendations.

## Run

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m uvicorn api.main:app --reload --host 0.0.0.0 --port 8000
```

Create `.env` from `.env.example` and provide the PostgreSQL/Supabase `DATABASE_URL` and `OPENROUTER_API_KEY`.

## Test

```powershell
python -m pytest -q
```

## Train ASUSE model

```powershell
python -m ml_engine.training.train_asuse_model --data data/asuse_2023_24_training.csv --model models/asuse_profitability.joblib
```

## Database reference

`database/ml_schema.sql` contains the ML/Decision Engine schema reference. The live application also expects the database team's chatbot, location, and funding tables.

## Documentation

- `docs/api.md` — API reference
- `docs/chatbot.md` — chatbot architecture and behavior
- `database/seed_reference_data.py` — reference-data seeding
