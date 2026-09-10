# UdyamSetu deployment notes

## Render backend

Root directory:
`backend`

Build command:
`pip install -r requirements.txt`

Start command:
`uvicorn api.main:app --host 0.0.0.0 --port $PORT`

Required runtime configuration:

- `DATABASE_URL` — Supabase/PostgreSQL connection string
- `OPENROUTER_API_KEY`
- `OPENROUTER_MODEL` — for example `openrouter/free`
- `OPENROUTER_BASE_URL=https://openrouter.ai/api/v1/chat/completions`
- `CORS_ORIGINS=https://udyam-setu-udysu.vercel.app`
- `ASUSE_MODEL_PATH=models/asuse_profitability.joblib`
- `ASUSE_MODEL_PRELOAD=false`
- `MODEL_NAME=paraphrase-multilingual-MiniLM-L12-v2`

The ASUSE model is intentionally not loaded during startup on the 512 MiB Render instance. It is loaded only when an analysis actually needs the ASUSE prediction. The semantic embedding model is shared by the decision engine and chatbot so the same transformer is not loaded twice.

The persisted ASUSE model was trained with scikit-learn 1.8.0, so the backend pins `scikit-learn==1.8.0`.

## Vercel frontend

Root directory:
`frontend`

Build command:
`npm run build`

Output directory:
`dist`

Production variables:

- `VITE_API_BASE_URL=https://udyamsetu-pio1.onrender.com`
- `VITE_API_TIMEOUT_MS=90000`

Do not append `/api` to `VITE_API_BASE_URL`; the frontend adds `/api/...` to endpoint paths itself.
