# UdyamSetu Frontend

Componentized React frontend for the UdyamSetu prototype.

## Stack

- React.js
- JavaScript (ES6+)
- Tailwind CSS
- Recharts-ready architecture
- Lucide React
- React Router

## Run

```bash
npm install
npm run dev
```

## Pages

- `/` — Home
- `/how-it-works` — How UdyamSetu works
- `/schemes` — Government schemes
- `/insights` — Business insights
- `/calculator` — Financial calculator + scheme router
- `/assistant` — AI Business Assistant

## Structure

`src/components` contains reusable UI sections, `src/pages` contains route-level pages, `src/data` contains prototype data, and `src/utils` contains deterministic financial/scheme logic.

This is frontend-only. Replace the prototype data/actions with the FastAPI endpoints from the project specification when the backend is connected.
