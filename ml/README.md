# ExploreEase – Member 3: Dataset and AI/ML Module

## 1. Overview
This module provides dataset collection, preprocessing, AI-based recommendations, review sentiment analysis, cost analysis, and budget trip planning for ExploreEase.

## 2. Technologies Used
- Python
- Pandas
- NumPy
- Requests
- Geopy
- VADER Sentiment

## 3. Main Modules

| File | Purpose |
|---|---|
| data_collector.py | Collects location-based data using OpenStreetMap |
| data_processor.py | Cleans and preprocesses collected data |
| recommendation.py | Recommends tourist places and restaurants |
| ai_analysis.py | Performs recommendation scoring and review sentiment analysis |
| fare_analysis.py | Finds verified transport fares and calculates estimates |
| food_price_manager.py | Handles food-price submissions and verification |
| trip_planner.py | Supports food, entry-fee and budget trip calculations |

## 4. Datasets
- Tourist places
- Restaurants
- Place reviews
- Place entry costs
- Local food information
- Food-price submissions
- Transport fares

Data files are maintained under the `data` directory.

## 5. Data Collection
OpenStreetMap is used to collect location-based places and restaurants. The collector supports locations beyond the initial testing cities and uses caching to reduce repeated requests.

## 6. AI and Analysis
- Place recommendation scoring
- Distance-based ranking
- Rating and review-based scoring when data is available
- Review sentiment analysis using VADER
- Place and category analysis

## 7. Cost and Trip Planning
The module uses verified entry fees and food prices where available. Transport fares can be retrieved from verified records or calculated as estimates. Missing costs are reported instead of being treated as verified values.

## 8. Important Limitations
- Visitor reviews require an authorized review data source.
- Food prices and transport fares may not be available for every location.
- Estimated fares are not verified fares.
- OpenStreetMap data does not itself provide current menu prices or visitor reviews.
- Data sources and verification status should be retained.

## 9. Installation
Install the dependencies listed in `ml/requirements.txt`.

Run Python commands from the ExploreEase project root.

## 10. Backend Integration Handoff
The backend can import the required functions from the `ml` package. API routes and request/response formats should be finalized after the team selects its backend framework.
