
import pandas as pd


def calculate_popularity_score(places):

    if places.empty:
        return pd.DataFrame()

    places = places.copy()

    required_columns = ["Place_ID", "Rating", "Review_Count"]

    if not all(column in places.columns for column in required_columns):
        raise ValueError("Required popularity columns are missing")

    places["Rating"] = pd.to_numeric(
        places["Rating"], errors="coerce"
    )

    places["Review_Count"] = pd.to_numeric(
        places["Review_Count"], errors="coerce"
    )

    places = places.dropna(subset=["Place_ID", "Rating", "Review_Count"])

    places = places[
        places["Rating"].between(1, 5)
        & (places["Review_Count"] > 0)
    ].copy()

    if places.empty:
        return places

    places["Popularity_Score"] = (
        (places["Rating"] / 5) * 70
        + (places["Review_Count"] / (places["Review_Count"] + 10)) * 30
    ).round(2)

    return places.sort_values(
        "Popularity_Score", ascending=False
    ).reset_index(drop=True)


def get_trending_places(places, limit=10):

    ranked_places = calculate_popularity_score(places)

    return ranked_places.head(limit)


def get_highly_rated_places(places, minimum_rating=4):

    ranked_places = calculate_popularity_score(places)

    return ranked_places[
        ranked_places["Rating"] >= minimum_rating
    ].reset_index(drop=True)


def get_less_reviewed_places(places, maximum_reviews=10):

    if places.empty:
        return pd.DataFrame()

    if not {"Place_ID", "Review_Count"}.issubset(places.columns):
        raise ValueError("Required review columns are missing")

    review_counts = pd.to_numeric(
        places["Review_Count"], errors="coerce"
    )

    return places[
        review_counts.notna() & (review_counts <= maximum_reviews)
    ].copy().reset_index(drop=True)
