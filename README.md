
# ExploreEase – AI-Powered Automated Travel Discovery Platform

## Project Overview
ExploreEase is an AI-powered travel discovery platform designed to help users explore places, discover local food, compare transportation options, and plan trips according to their interests and budget.

The platform aims to support different locations dynamically instead of depending on a fixed set of cities or datasets.

## Technologies Used
- Python
- Pandas and NumPy
- OpenStreetMap (OSM)
- Overpass API
- Geopy
- VADER Sentiment Analysis
- FastAPI (Backend – planned integration)
- React and Leaflet (Frontend)

## Implemented Features

### 1. Location-Based Data Collection
- Collects tourist places and restaurants using OpenStreetMap.
- Supports different locations through geocoding.
- Includes caching to reduce repeated API requests.

### 2. Data Processing
- Cleans collected location information.
- Removes duplicate and incomplete records.
- Prepares data for recommendations and analysis.

### 3. AI-Based Recommendations
- Recommends places based on available interests and location information.
- Supports rating, review sentiment, popularity and distance-based ranking when relevant information is available.

### 4. Review Analysis
- Analyzes review sentiment using VADER.
- Generates review summaries.
- Identifies feedback topics such as cleanliness, safety, crowd and maintenance.

### 5. Popularity Analysis
- Calculates a prototype popularity score using ratings and review counts.
- Supports highly rated and less-reviewed place identification.

### 6. Food and Transportation Recommendations
- Supports food recommendations based on preferences.
- Provides transport fare selection using route and currency information.
- Includes price and fare verification workflows.

### 7. Smart Trip Planning
- Generates a nearby-place itinerary.
- Calculates trip costs using available entry fees, food costs and transport costs.
- Checks whether the estimated total fits the user's budget.

### 8. Data Refresh
- Supports on-demand location data updates using OpenStreetMap.
- Reports update status and collection information.

## Project Structure

```text
ExploreEase/
├── backend/                  # FastAPI backend - pending
├── data/
│   ├── raw/                  # Supporting and backup data
│   └── processed/            # Processed reference data
├── ml/
│   ├── new_features/
│   │   ├── review_analysis.py
│   │   ├── popularity_analysis.py
│   │   ├── recommendation_engine.py
│   │   ├── food_recommendation.py
│   │   ├── transport_recommendation.py
│   │   ├── smart_trip_planner.py
│   │   ├── data_updater.py
│   │   └── test_features.py
│   ├── ai_analysis.py
│   ├── data_collector.py
│   ├── data_processor.py
│   ├── recommendation.py
│   ├── food_price_manager.py
│   ├── transport_fare_manager.py
│   ├── fare_analysis.py
│   └── trip_planner.py
├── ML_INTEGRATION_GUIDE.md
├── requirements.txt
└── README.md
```

## Dataset Note
The available CSV datasets are retained for backup, reference and testing purposes. The main project approach is dynamic location-based collection and analysis rather than depending on fixed city datasets.

## Testing
The individual new feature modules have passed 7 basic functional tests using temporary test data.

All existing and new ML modules have also passed a combined import check.

These tests verify basic functionality, not complete production or end-to-end application integration.

## Pending Work
- Connect ML functionality to the FastAPI backend.
- Integrate frontend and backend APIs.
- Connect authorized user reviews and actual rating information.
- Improve real-time popularity and recommendation analysis.
- Integrate reliable, verified food prices and transportation fares.
- Implement scheduled data refresh and better handling of API failures.
- Perform complete application testing.

## Team Responsibilities
- **Member 1:** Frontend development and map integration.
- **Member 2:** FastAPI backend, database and API development.
- **Member 3:** Data collection, processing, AI/ML recommendations, fare analysis and trip planning.

## Current Project Status
The core ML modules and their basic tests are prepared. Full application integration is pending backend and frontend development.