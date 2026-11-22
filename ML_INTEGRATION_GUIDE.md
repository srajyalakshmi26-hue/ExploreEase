# ExploreEase – ML Integration Guide

## 1. Purpose
This document explains how Member 2 (Backend Developer) can integrate Member 3's Dataset and AI/ML modules with the FastAPI backend.

## 2. Python Modules

All modules are available inside the `ml/` package.

| Module | Responsibility |
|---|---|
| data_collector.py | Live OpenStreetMap data collection |
| data_processor.py | Data cleaning and preprocessing |
| recommendation.py | Tourist place and restaurant recommendations |
| ai_analysis.py | Recommendation scoring and sentiment analysis |
| fare_analysis.py | Transport fare analysis |
| food_price_manager.py | Food price submission and verification |
| trip_planner.py | Food cost and budget trip planning |

## 3. Recommended Backend Integration

The backend should import ML functions directly instead of duplicating their logic.

### Tourist places
Module: `ml.recommendation`

Relevant functions:
- `recommend_live_places()`
- `recommend_ai_places()`

### Restaurants
Module: `ml.recommendation`

Relevant functions:
- `recommend_live_restaurants()`
- `recommend_restaurants_with_food_prices()`

### Review analysis
Module: `ml.ai_analysis`

Relevant functions:
- `analyze_review_sentiment()`
- `get_sentiment_summary()`

### Food prices
Module: `ml.food_price_manager`

Relevant functions:
- `submit_food_price()`
- `verify_food_price()`
- `add_authorized_food_price()`

### Transport fares
Module: `ml.fare_analysis`

Relevant functions:
- `find_transport_options()`
- `find_cheapest_transport()`
- `estimate_transport_fare()`

### Budget trip planning
Module: `ml.trip_planner`

Relevant functions:
- `get_place_costs()`
- `recommend_local_food()`
- `calculate_trip_cost()`
- `create_budget_trip()`

## 4. Suggested FastAPI Endpoints

| Method | Endpoint | Purpose |
|---|---|---|
| GET | /places/recommend | Recommend tourist places |
| GET | /restaurants/recommend | Recommend restaurants |
| POST | /reviews/analyze | Analyze review sentiment |
| GET | /food/prices | Retrieve verified food prices |
| POST | /food/submit | Submit food prices |
| GET | /transport/fares | Retrieve transport options |
| POST | /trip/plan | Create a budget trip |

These are proposed API contracts. Member 2 should finalize request and response schemas.

## 5. Integration Requirements
- Run the backend from the ExploreEase project root.
- Import functions from the `ml` package.
- Convert Pandas DataFrames into JSON-compatible responses.
- Validate user inputs using Pydantic models.
- Handle unavailable data without inventing values.
- Keep API keys and secrets outside source code.
- Avoid blocking FastAPI request handling with long-running collection operations.

## 6. Data Limitations
- OpenStreetMap provides place information, not current visitor reviews or menu prices.
- Sentiment analysis requires authorized review text.
- Food prices and transport fares are only available when verified records exist.
- Estimated transport fares must be clearly labelled as estimates.
- Missing costs must remain unavailable rather than being treated as zero.

## 7. Project Structure

The backend will be maintained by Member 2 in the `backend/` directory. The `ml/` directory remains the responsibility of Member 3.

Backend and frontend integration will be completed collaboratively after API contracts are agreed.
