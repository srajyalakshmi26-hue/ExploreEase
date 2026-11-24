from typing import Optional

from pydantic import BaseModel, Field, ConfigDict


class TripPlanRequest(BaseModel):
    city: str = Field(min_length=2, max_length=100)
    budget: float = Field(gt=0, le=10_000_000)
    currency: str = Field(default="INR", min_length=3, max_length=3, pattern=r"^[A-Za-z]{3}$")
    start_latitude: Optional[float] = Field(default=None, ge=-90, le=90)
    start_longitude: Optional[float] = Field(default=None, ge=-180, le=180)
    interests: list[str] = Field(default_factory=list, max_length=20)
    days: int = Field(default=1, ge=1, le=14)
    max_places: int = Field(default=8, ge=1, le=30)

    model_config = ConfigDict(str_strip_whitespace=True)


class ReviewAnalysisRequest(BaseModel):
    reviews: list[str] = Field(min_length=1, max_length=100)


class SavedPlaceCreate(BaseModel):
    place_name: str = Field(min_length=1, max_length=255)
    city: str = Field(min_length=2, max_length=120)
    category: Optional[str] = Field(default=None, max_length=100)
    latitude: Optional[float] = Field(default=None, ge=-90, le=90)
    longitude: Optional[float] = Field(default=None, ge=-180, le=180)
    osm_id: Optional[str] = Field(default=None, max_length=100)

    model_config = ConfigDict(str_strip_whitespace=True)
