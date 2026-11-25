# ExploreEase Frontend

React + Vite + Leaflet frontend for the ExploreEase FastAPI backend.
It uses only the endpoints that exist in the backend today.

## Run
1. Start the backend (from `backend/`): `uvicorn app.main:app --reload` (default http://localhost:8000)
2. In this folder:
   ```
   npm install
   cp .env.example .env     # set VITE_API_URL if your backend is elsewhere
   npm run dev
   ```
3. Open http://localhost:5173 (already allowed in the backend CORS settings).

For deployment, add your frontend URL to `CORS_ORIGINS` in the backend `.env` and set `VITE_API_URL` to the deployed API URL (ending in `/api/v1`).

## Pages -> backend endpoints
| Page | Endpoints |
|---|---|
| Home / city selector | GET /meta/cities |
| Places (search, filter, map, save) | GET /places, GET /places/categories |
| Restaurants | GET /restaurants |
| Local Food | GET /food |
| Recommendations | GET /recommendations/places |
| Trip Planner | POST /trips/plan |
| Review Analyzer | POST /reviews/analyze |
| Login / Register | POST /auth/login, /auth/register, GET /auth/me |
| Saved Places | GET/POST /saved-places, DELETE /saved-places/{id} |
