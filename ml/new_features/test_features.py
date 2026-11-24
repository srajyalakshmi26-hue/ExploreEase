
import pandas as pd

from ml.new_features.review_analysis import (
    analyze_reviews,
    get_review_summary,
    analyze_feedback_topics
)

from ml.new_features.popularity_analysis import (
    calculate_popularity_score
)

from ml.new_features.recommendation_engine import recommend_places

from ml.new_features.food_recommendation import recommend_food

from ml.new_features.transport_recommendation import (
    recommend_transport,
    get_cheapest_transport
)

from ml.new_features.smart_trip_planner import (
    create_itinerary,
    calculate_complete_budget
)


# 1. REVIEW ANALYSIS

reviews = pd.DataFrame({
    "Place_ID": ["P1", "P1", "P2"],
    "Rating": [5, 4, 3],
    "Review_Text": [
        "Amazing place, very clean and beautiful!",
        "Good place and safe environment",
        "The place is crowded"
    ]
})

analyzed_reviews = analyze_reviews(reviews)
review_summary = get_review_summary(analyzed_reviews)
feedback = analyze_feedback_topics(analyzed_reviews)

assert len(analyzed_reviews) == 3
assert len(review_summary) == 2
assert not feedback.empty

print("1. Review analysis: PASSED")


# 2. POPULARITY ANALYSIS

places = pd.DataFrame({
    "Place_ID": ["P1", "P2"],
    "Rating": [4.8, 4.0],
    "Review_Count": [100, 20]
})

popular_places = calculate_popularity_score(places)

assert len(popular_places) == 2
assert popular_places.iloc[0]["Place_ID"] == "P1"

print("2. Popularity analysis: PASSED")


# 3. AI RECOMMENDATIONS

places["Average_Rating"] = places["Rating"]
places["Positive_Percentage"] = [90, 70]
places["Category"] = ["Nature Park", "Historical Place"]
places["Distance_KM"] = [3, 5]

recommendations = recommend_places(
    places,
    interests=["nature"],
    limit=5
)

assert not recommendations.empty
assert recommendations.iloc[0]["Place_ID"] == "P1"

print("3. AI recommendations: PASSED")


# 4. FOOD RECOMMENDATIONS

foods = pd.DataFrame({
    "Food_Name": ["Biryani", "Mysore Pak"],
    "Description": ["Traditional rice dish", "Traditional sweet"],
    "City": ["Hyderabad", "Bengaluru"]
})

food_results = recommend_food(
    foods,
    preferences=["rice"],
    city="Hyderabad"
)

assert len(food_results) == 1

print("4. Food recommendations: PASSED")


# 5. TRANSPORT RECOMMENDATIONS

fares = pd.DataFrame({
    "City": ["Hyderabad", "Hyderabad"],
    "Starting_Point": ["A", "A"],
    "Destination": ["B", "B"],
    "Transport_Type": ["Bus", "Taxi"],
    "Fare_Amount": [30, 150],
    "Currency": ["INR", "INR"],
    "Verification_Status": ["Verified", "Verified"],
    "Country": ["India", "India"]
})

transport_results = recommend_transport(
    fares,
    "Hyderabad",
    "A",
    "B",
    country="India",
    currency="INR"
)

cheapest = get_cheapest_transport(transport_results)

assert len(transport_results) == 2
assert cheapest.iloc[0]["Fare_Amount"] == 30

print("5. Transport recommendations: PASSED")


# 6. ITINERARY GENERATION

trip_places = pd.DataFrame({
    "Place_Name": ["Park", "Museum"],
    "Latitude": [17.40, 17.42],
    "Longitude": [78.40, 78.42]
})

itinerary = create_itinerary(
    trip_places,
    17.39,
    78.39
)

assert len(itinerary) == 2
assert list(itinerary["Visit_Order"]) == [1, 2]

print("6. Itinerary generation: PASSED")


# 7. BUDGET CALCULATION

budget_result = calculate_complete_budget(
    entry_fee=100,
    food_cost=200,
    transport_cost=50,
    budget=500,
    currency="INR"
)

assert budget_result["Total_Cost"] == 350
assert budget_result["Remaining_Budget"] == 150
assert budget_result["Status"] == "Within Budget"

print("7. Budget calculation: PASSED")


print("\nALL 7 FUNCTIONAL TESTS COMPLETED SUCCESSFULLY!")
