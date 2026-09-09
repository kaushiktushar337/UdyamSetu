# Frontend and Backend Integration

The React frontend talks to the FastAPI service for the data-driven parts of UdyamSetu.

## Connected features

- AI Assistant: `/api/chat` and conversation history
- Live location: `/api/location`, `/api/location/latest/{user_id}`, `/api/locations`
- Business Insights: `/api/insights`
- Funding: `/api/funding/recommendations`
- Business analysis: `/api/analyze`
- Health check: `/health`

## Local development

Start the backend on port 8000, then start the Vite frontend on port 5173.

The frontend uses `VITE_API_BASE_URL` to find the backend.

## Location

The browser asks for location only after the user chooses **Use my current location**. The backend resolves it to a supported reference location and stores the capture. The UI uses the returned estimated area and location ID for subsequent requests.

## Error handling

API errors are normalized in `frontend/src/services/api.js`. Structured FastAPI validation responses are converted into readable messages so objects are never rendered as `[object Object]`.

## Production

Set `VITE_API_BASE_URL` to the deployed FastAPI URL before building the frontend. The hosting provider must also serve `index.html` for client-side routes.
