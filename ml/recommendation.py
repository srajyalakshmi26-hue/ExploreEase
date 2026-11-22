
import pandas as pd
import os
import numpy as np

from ml.data_collector import collect_city_data
from ml.data_processor import process_city_data
from ml.ai_analysis import calculate_recommendation_score

from ml.ai_analysis import (
    analyze_place_categories,
    analyze_city_popularity,
    get_top_places,
    rank_places,
    get_popular_places
)


BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

DATA_PATH = os.path.join(
    BASE_DIR, "data", "processed", "tourist_places.csv"
)

RESTAURANT_PATH = os.path.join(
    BASE_DIR, "data", "processed", "restaurants.csv"
)

REVIEWS_PATH = os.path.join(
    BASE_DIR, "data", "raw", "place_reviews.csv"
)


# ----------------------------------
# LOAD DATASETS
# ----------------------------------

def load_dataset(file_path):

    if not os.path.exists(file_path):
        return pd.DataFrame()

    return pd.read_csv(file_path)


places_df = load_dataset(DATA_PATH)
restaurants_df = load_dataset(RESTAURANT_PATH)
reviews_df = load_dataset(REVIEWS_PATH)


# ----------------------------------
# DISTANCE CALCULATION
# ----------------------------------

def calculate_distance(
    user_lat,
    user_lon,
    place_lat,
    place_lon
):

    user_lat = np.radians(user_lat)
    user_lon = np.radians(user_lon)

    place_lat = np.radians(place_lat)
    place_lon = np.radians(place_lon)

    lat_difference = place_lat - user_lat
    lon_difference = place_lon - user_lon

    a = (
        np.sin(lat_difference / 2) ** 2
        + np.cos(user_lat)
        * np.cos(place_lat)
        * np.sin(lon_difference / 2) ** 2
    )

    c = 2 * np.arcsin(np.sqrt(a))

    earth_radius = 6371

    return earth_radius * c


# ----------------------------------
# CITY-BASED RECOMMENDATIONS
# ----------------------------------

def recommend_places(city, category=None):

    if places_df.empty:
        return pd.DataFrame()

    filtered_places = places_df[
        places_df["City"].astype(str).str.strip().str.lower()
        == city.strip().lower()
    ].copy()

    if category:
        filtered_places = filtered_places[
            filtered_places["Category"].astype(str).str.lower()
            == category.strip().lower()
        ]

    return filtered_places.head(5).reset_index(drop=True)


def recommend_restaurants(city, category=None):

    if restaurants_df.empty:
        return pd.DataFrame()

    filtered_restaurants = restaurants_df[
        restaurants_df["City"].astype(str).str.strip().str.lower()
        == city.strip().lower()
    ].copy()

    if category:
        filtered_restaurants = filtered_restaurants[
            filtered_restaurants["Category"].astype(str).str.lower()
            == category.strip().lower()
        ]

    return filtered_restaurants.head(5).reset_index(drop=True)


# ----------------------------------
# NEARBY PLACE RECOMMENDATIONS
# ----------------------------------

def recommend_nearby_places(user_lat, user_lon, city=None):

    if places_df.empty:
        return pd.DataFrame()

    nearby_places = places_df.copy()

    if city:
        nearby_places = nearby_places[
            nearby_places["City"].astype(str).str.strip().str.lower()
            == city.strip().lower()
        ].copy()

    if nearby_places.empty:
        return nearby_places

    nearby_places["Distance_KM"] = calculate_distance(
        user_lat,
        user_lon,
        nearby_places["Latitude"].astype(float),
        nearby_places["Longitude"].astype(float)
    )

    return (
        nearby_places.sort_values("Distance_KM")
        .head(5)
        .reset_index(drop=True)
    )


def recommend_places_within_radius(
    user_lat,
    user_lon,
    max_distance,
    city=None
):

    if places_df.empty:
        return pd.DataFrame()

    nearby_places = places_df.copy()

    if city:
        nearby_places = nearby_places[
            nearby_places["City"].astype(str).str.strip().str.lower()
            == city.strip().lower()
        ].copy()

    if nearby_places.empty:
        return nearby_places

    nearby_places["Distance_KM"] = calculate_distance(
        user_lat,
        user_lon,
        nearby_places["Latitude"].astype(float),
        nearby_places["Longitude"].astype(float)
    )

    return (
        nearby_places[
            nearby_places["Distance_KM"] <= max_distance
        ]
        .sort_values("Distance_KM")
        .reset_index(drop=True)
    )


def recommend_nearby_restaurants(
    user_lat,
    user_lon,
    city=None,
    max_distance=None
):

    if restaurants_df.empty:
        return pd.DataFrame()

    nearby_restaurants = restaurants_df.copy()

    if city:
        nearby_restaurants = nearby_restaurants[
            nearby_restaurants["City"].astype(str).str.strip().str.lower()
            == city.strip().lower()
        ].copy()

    if nearby_restaurants.empty:
        return nearby_restaurants

    nearby_restaurants["Distance_KM"] = calculate_distance(
        user_lat,
        user_lon,
        nearby_restaurants["Latitude"].astype(float),
        nearby_restaurants["Longitude"].astype(float)
    )

    if max_distance is not None:
        nearby_restaurants = nearby_restaurants[
            nearby_restaurants["Distance_KM"] <= max_distance
        ]

    return (
        nearby_restaurants.sort_values("Distance_KM")
        .head(5)
        .reset_index(drop=True)
    )


# ----------------------------------
# REVIEW-BASED RECOMMENDATIONS
# ----------------------------------

def recommend_best_places(city, min_reviews=1):

    if reviews_df.empty:
        return pd.DataFrame()

    required_columns = [
        "City", "Rating", "Review_Count"
    ]

    if not all(
        column in reviews_df.columns
        for column in required_columns
    ):
        return pd.DataFrame()

    city_reviews = reviews_df[
        reviews_df["City"].astype(str).str.strip().str.lower()
        == city.strip().lower()
    ].copy()

    if city_reviews.empty:
        return pd.DataFrame()

    city_reviews["Rating"] = pd.to_numeric(
        city_reviews["Rating"],
        errors="coerce"
    )

    city_reviews["Review_Count"] = pd.to_numeric(
        city_reviews["Review_Count"],
        errors="coerce"
    )

    city_reviews = city_reviews[
        city_reviews["Rating"].between(0, 5)
        & (city_reviews["Review_Count"] >= min_reviews)
    ]

    return city_reviews.sort_values(
        by=["Rating", "Review_Count"],
        ascending=[False, False]
    ).reset_index(drop=True)


# ----------------------------------
# LIVE LOCATION DATA
# ----------------------------------

def collect_and_process_city_data(city, radius=5000):

    collected_data = collect_city_data(city, radius)

    return process_city_data(collected_data)


# ----------------------------------
# LIVE PLACE RECOMMENDATIONS
# ----------------------------------

def recommend_live_places(
    city,
    category=None,
    radius=5000,
    limit=5,
    live_data=None
):

    if live_data is None:
        live_data = collect_and_process_city_data(city, radius)

    if live_data.empty:
        return pd.DataFrame()

    places = live_data[
        live_data["City"].astype(str).str.strip().str.lower()
        == city.strip().lower()
    ].copy()

    restaurant_categories = [
        "restaurant", "cafe", "fast_food"
    ]

    places = places[
        ~places["Category"].astype(str).str.lower()
        .isin(restaurant_categories)
    ]

    if category:
        places = places[
            places["Category"].astype(str).str.strip().str.lower()
            == category.strip().lower()
        ]

    return places.head(limit).reset_index(drop=True)


def recommend_live_restaurants(
    city,
    category=None,
    radius=5000,
    limit=5,
    live_data=None
):

    if live_data is None:
        live_data = collect_and_process_city_data(city, radius)

    if live_data.empty:
        return pd.DataFrame()

    restaurants = live_data[
        live_data["City"].astype(str).str.strip().str.lower()
        == city.strip().lower()
    ].copy()

    restaurant_categories = [
        "restaurant", "cafe", "fast_food"
    ]

    restaurants = restaurants[
        restaurants["Category"].astype(str).str.lower()
        .isin(restaurant_categories)
    ]

    if category:
        restaurants = restaurants[
            restaurants["Category"].astype(str).str.strip().str.lower()
            == category.strip().lower()
        ]

    return restaurants.head(limit).reset_index(drop=True)


# ----------------------------------
# LIVE CITY ANALYSIS
# ----------------------------------

def analyze_live_city(city, radius=5000, live_data=None):

    if live_data is None:
        live_data = collect_and_process_city_data(city, radius)

    if live_data.empty:
        return {
            "Total_Places": 0,
            "Category_Analysis": pd.DataFrame(),
            "Top_Places": pd.DataFrame(),
            "Rating_Based_Popular_Places": pd.DataFrame()
        }

    city_data = live_data[
        live_data["City"].astype(str).str.strip().str.lower()
        == city.strip().lower()
    ].copy()

    return {
        "Total_Places": len(city_data),
        "Category_Analysis": analyze_place_categories(city_data),
        "Top_Places": get_top_places(city_data, 10),
        "Rating_Based_Popular_Places": get_popular_places(city_data, 10)
    }


# ----------------------------------
# RANKED PLACE RECOMMENDATIONS
# ----------------------------------

def recommend_ranked_places(
    city,
    category=None,
    limit=10,
    live_data=None
):

    if live_data is None:
        live_data = collect_and_process_city_data(city)

    if live_data.empty:
        return pd.DataFrame()

    city_places = live_data[
        live_data["City"].astype(str).str.strip().str.lower()
        == city.strip().lower()
    ].copy()

    return rank_places(
        city_places,
        category=category,
        limit=limit
    )


# ----------------------------------
# POPULAR PLACE RECOMMENDATIONS
# ----------------------------------

def recommend_popular_places(
    city,
    limit=10,
    live_data=None
):

    if live_data is None:
        live_data = collect_and_process_city_data(city)

    if live_data.empty:
        return pd.DataFrame()

    city_places = live_data[
        live_data["City"].astype(str).str.strip().str.lower()
        == city.strip().lower()
    ].copy()

    return get_popular_places(
        city_places,
        limit=limit
    )

def recommend_ai_places(places, limit=10):

    if places.empty:
        return pd.DataFrame()

    if "Distance_KM" not in places.columns:
        return pd.DataFrame()

    ranked_places = calculate_recommendation_score(places)

    if ranked_places.empty:
        return ranked_places

    return ranked_places.head(limit).reset_index(drop=True)

# ----------------------------------
# LIVE RESTAURANTS WITH VERIFIED FOOD PRICES
# ----------------------------------

def recommend_restaurants_with_food_prices(
    city,
    category=None,
    radius=5000,
    limit=5,
    live_data=None
):

    from ml.trip_planner import recommend_local_food

    restaurants = recommend_live_restaurants(
        city=city,
        category=category,
        radius=radius,
        limit=limit,
        live_data=live_data
    )

    if restaurants.empty:
        return restaurants

    food_prices = recommend_local_food(city)

    if food_prices.empty:
        restaurants["Food_Prices"] = None
        restaurants["Food_Price_Status"] = "Not available"
        return restaurants

    if "Place_ID" not in restaurants.columns:
        restaurants["Food_Prices"] = None
        restaurants["Food_Price_Status"] = "Restaurant ID unavailable"
        return restaurants

    restaurants["Food_Prices"] = restaurants["Place_ID"].apply(
        lambda restaurant_id: food_prices[
            food_prices["Restaurant_ID"].astype(str).str.strip()
            == str(restaurant_id).strip()
        ][["Food_Name", "Approx_Price", "Currency"]].to_dict("records")
    )

    restaurants["Food_Price_Status"] = restaurants[
        "Food_Prices"
    ].apply(
        lambda prices: "Verified prices available"
        if prices else "Not available"
    )

    return restaurants
