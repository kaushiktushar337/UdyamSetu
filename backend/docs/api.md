# UdyamSetu ML Decision Engine API

The API exposes the combined business matcher + ASUSE model + financial + market + operational + risk + decision engine.

## Run locally

From the `backend` directory:

```powershell
uvicorn api.main:app --reload --host 0.0.0.0 --port 8000
```

Open the interactive API documentation at `/docs`.

## Configuration

- `DATABASE_URL` — production PostgreSQL connection. If omitted, the API uses the bundled 40-profile CSV for local demos/tests.
- `ASUSE_MODEL_PATH` — optional path to the trained ASUSE `.joblib` model. Defaults to `models/asuse_profitability.joblib`.
- `CORS_ORIGINS` — comma-separated frontend origins. Defaults to `*` for local development.

## POST `/api/analyze`

Example request:

```json
{
  "user_id": "optional-user-uuid",
  "business_id": "optional-existing-business-uuid",
  "location_id": "optional-location-uuid",
  "available_capital": 500000,
  "funding_available": 0,
  "interests": "bakery food",
  "skills": "baking",
  "experience_years": 3,
  "available_resources": [],
  "infrastructure": [],
  "location": "Jaipur",
  "preferences": "small scale",
  "planned_workers": 4,
  "business_age_years": 1,
  "daily_work_hours": 8,
  "top_k": 5,
  "persist": false
}
```

The endpoint selects the highest-ranked business recommendation and returns its combined decision, score breakdown, ASUSE prediction, strengths, concerns and recommendations.

Set `persist=true` only when `user_id`, `business_id` and `location_id` refer to real records in the application database.

## GET `/api/recommendations`

Uses the same request fields and returns the ranked top-k recommendations without persisting an analysis.

## GET `/health`

Returns service and ASUSE-model loading status.

## Design note

The ASUSE output is a historical profitability signal. It is not presented as a guarantee or probability of future business success. UdyamSetu's confidence value is a data-quality confidence score, not a success probability.


## Funding / Scheme / Loan APIs

The database-backed funding layer uses the `scheme_rules` and `loan_plans` tables supplied by the database team.

- `POST /api/funding/recommendations` — ranked schemes and loan plans using project cost, requested loan, category, location and supplied eligibility fields.
- `GET /api/funding/schemes` — active/effective scheme rules.
- `GET /api/funding/loans` — active loan plans.

The AI chatbot also adds structured funding data to its trusted context when a funding-related message is detected. It never invents eligibility, approval, interest rates, or limits.

The decision engine attaches funding recommendations to the top business recommendation when `DATABASE_URL` is configured. The estimated loan need is calculated as project cost minus declared available capital/funding.

Important: `scheme_rules` has no category column, so scheme ranking uses the stored project-cost/effective-date rules and only treats category mentions in the stored scheme name/description as an additional signal. Loan plans can use `target_segments`, geographic fields, loan range and stored eligibility fields.
