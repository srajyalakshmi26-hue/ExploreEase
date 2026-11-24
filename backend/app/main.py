import sys
from pathlib import Path

# --------------------------------------------------
# PROJECT ROOT CONFIGURATION
# --------------------------------------------------

# Project structure:
# ExploreEase-main/
#     backend/
#         app/
#             main.py
#     ml/

PROJECT_ROOT = Path(__file__).resolve().parents[2]

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


# --------------------------------------------------
# FASTAPI IMPORTS
# --------------------------------------------------

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.db.database import Base, engine
from app.models import User, SavedPlace  # Register ORM models
from app.api.routes import router


# --------------------------------------------------
# DATABASE INITIALIZATION
# --------------------------------------------------

Base.metadata.create_all(bind=engine)


# --------------------------------------------------
# FASTAPI APPLICATION
# --------------------------------------------------

app = FastAPI(
    title=settings.APP_NAME,
    version="1.0.0",
    description="ExploreEase travel discovery and planning API"
)


# --------------------------------------------------
# CORS CONFIGURATION
# --------------------------------------------------

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)


# --------------------------------------------------
# API ROUTES
# --------------------------------------------------

app.include_router(
    router,
    prefix=settings.API_V1_PREFIX
)


# --------------------------------------------------
# ROOT ENDPOINT
# --------------------------------------------------

@app.get("/")
def root():
    return {
        "message": "Welcome to ExploreEase API",
        "docs": "/docs",
        "health": "/health"
    }


# --------------------------------------------------
# HEALTH CHECK
# --------------------------------------------------

@app.get("/health")
def health():
    return {
        "status": "healthy",
        "service": "ExploreEase API"
    }
