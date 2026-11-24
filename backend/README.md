# ExploreEase Backend – Member 2 Contribution

This backend is the API and persistence layer for the existing ExploreEase data/ML modules.

## Current backend scope

- FastAPI application with `/health` and Swagger documentation.
- CSV-backed city, tourist-place, restaurant and local-food read APIs.
- Place recommendation endpoint that calls the repository recommendation engine.
- Review sentiment endpoint for review text supplied by the caller (requires VADER).
- Trip itinerary endpoint using the existing smart trip planner when start coordinates are supplied.
- Registration/login using Argon2 password hashing and JWT access tokens.
- SQLAlchemy models for users and saved places.
- SQLite local-development fallback and PostgreSQL connection support.
- Authenticated saved-place create/list/delete endpoints.
- Configurable CORS origins.

## Windows setup (run from the repository root)

1. Open CMD in the `ExploreEase-main` folder.
2. Run `cd backend`.
3. Run `run.bat`.
4. Open `http://127.0.0.1:8000/docs`.

The first run creates a virtual environment, installs `requirements.txt`, copies `.env.example` to `.env`, and starts the API. A blank `DATABASE_URL` uses SQLite (`backend/exploreease.db`).

For PostgreSQL, set this in `backend/.env` after creating the database:

`DATABASE_URL=postgresql+psycopg://postgres:YOUR_PASSWORD@localhost:5432/exploreease`

Before deployment, set a strong random `SECRET_KEY` and add the exact deployed frontend origin to `CORS_ORIGINS`.

## API routes

- `GET /health`
- `GET /api/v1/meta/cities`
- `GET /api/v1/places`
- `GET /api/v1/places/categories`
- `GET /api/v1/restaurants`
- `GET /api/v1/recommendations/places`
- `GET /api/v1/food`
- `POST /api/v1/reviews/analyze`
- `POST /api/v1/trips/plan`
- `POST /api/v1/auth/register`
- `POST /api/v1/auth/login`
- `GET /api/v1/auth/me` (Bearer token)
- `POST /api/v1/saved-places` (Bearer token)
- `GET /api/v1/saved-places` (Bearer token)
- `DELETE /api/v1/saved-places/{saved_id}` (Bearer token)

## Data limitations (must be shown honestly in the UI)

- OpenStreetMap records provide place metadata, not verified visitor reviews or current menu prices.
- The repository's `place_reviews.csv` and `transport_fares.csv` currently contain no data rows.
- Most `local_food.csv` price values are missing.
- The trip endpoint can provide a location itinerary and exact matching verified entry fees. It does not claim a complete trip total when food and transport prices are unavailable.
- The recommendation model must not present absent ratings/reviews as real values.

## Remaining backend work

- Add automated API tests and Alembic database migrations.
- Improve DB error handling and concurrency-safe registration.
- Add database-backed review/price submissions and moderation/verification workflows.
- Add rate limiting, refresh tokens, password reset and email verification before production.
- Add controlled OSM refresh jobs with caching, timeouts and rate limits.
- Finalize response contracts with the frontend contributor and test end-to-end integration.

## Validation status

The source files compile, and local configuration/schema/data-loading checks have been run. A complete API startup and endpoint test still requires installing all dependencies from `requirements.txt` on the development machine.
