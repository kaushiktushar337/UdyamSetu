# UdyamSetu Frontend

UdyamSetu is a simple business-advisory experience for entrepreneurs who want to understand a business idea before investing in it. This frontend connects the user-facing app to the UdyamSetu backend, which handles the AI assistant, market insights, funding data and ML-based business analysis.

## What the app does

- **AI Assistant** — chat about business ideas, loans, schemes and next steps. Conversations can be restored using the backend conversation history.
- **Business Insights** — load location-specific demand, competition and opportunity metrics from the database and show the strongest business matches.
- **Financial Calculator** — estimate a basic funding structure and run the full UdyamSetu decision engine.
- **Schemes & Loan Plans** — retrieve active records from `scheme_rules` and `loan_plans` and rank them using the information the user provides.
- **Location support** — users can choose a supported area or use their current location. The app shows the resolved area name and uses its location ID when talking to the backend.

## Run locally

### 1. Start the backend

From the UdyamSetu backend directory:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m uvicorn api.main:app --reload --host 0.0.0.0 --port 8000
```

Using the virtual-environment Python directly avoids PowerShell execution-policy issues.

### 2. Start the frontend

```powershell
npm install
npm run dev
```

If the backend is running on another URL, copy `.env.example` to `.env` and change:

```env
VITE_API_BASE_URL=http://localhost:8000
```

Then open the Vite URL shown in the terminal (normally `http://localhost:5173`).

## Backend endpoints used by the frontend

| Endpoint | Used for |
| --- | --- |
| `POST /api/chat` | AI assistant messages |
| `GET /api/chat/history/{conversation_id}` | Restoring chat history |
| `POST /api/location` | Saving and resolving a user's current area |
| `GET /api/location/latest/{user_id}` | Restoring the last saved area |
| `GET /api/locations` | Supported location selector |
| `POST /api/insights` | Location/category market insights |
| `POST /api/funding/recommendations` | Scheme and loan matching |
| `POST /api/analyze` | ML/ASUSE decision-engine analysis |
| `GET /health` | Backend health check |

The frontend treats the backend as the source of truth for these features. It does not silently replace a failed API request with fake market or funding results.

## Location behavior

Location is requested only when the user chooses **Use my current location**. The resolved area is kept in the browser so it can be reused by the assistant, calculator and funding/insights screens.

## Before pushing to Git

The repository intentionally does not include `node_modules`, `dist`, local `.env` files or editor files. Install dependencies with `npm install` after cloning.

Check the project with:

```powershell
npm run build
```

## Deployment

This is a standard Vite React application. Set `VITE_API_BASE_URL` to the deployed backend URL in the hosting provider's environment settings, then run the normal Vite build.

For a single-page application, configure the host to serve `index.html` for client-side routes such as `/insights`, `/calculator`, `/schemes` and `/assistant`.

## Notes

The UI presents market, funding and ML results as advisory information. Official scheme eligibility, loan approval and final business viability always depend on the relevant authority, lender and the entrepreneur's actual circumstances.
