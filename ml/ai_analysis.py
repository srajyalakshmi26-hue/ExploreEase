
import pandas as pd
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer


analyzer = SentimentIntensityAnalyzer()


def analyze_place_categories(places):

    if places.empty or "Category" not in places.columns:
        return pd.DataFrame()

    return (
        places.groupby("Category")
        .size()
        .reset_index(name="Place_Count")
        .sort_values("Place_Count", ascending=False)
        .reset_index(drop=True)
    )


def analyze_city_popularity(places):

    if places.empty or "City" not in places.columns:
        return pd.DataFrame()

    return (
        places.groupby("City")
        .agg(
            Total_Places=("Place_ID", "count"),
            Total_Categories=("Category", "nunique")
        )
        .reset_index()
        .sort_values("Total_Places", ascending=False)
        .reset_index(drop=True)
    )


def get_top_places(places, limit=10):

    if places.empty:
        return pd.DataFrame()

    if "Place_ID" in places.columns:
        places = places.drop_duplicates(subset=["Place_ID"])

    return places.head(limit).reset_index(drop=True)


def rank_places(places, category=None, limit=10):

    if places.empty:
        return pd.DataFrame()

    ranked_places = places.copy()

    if category:
        ranked_places = ranked_places[
            ranked_places["Category"].astype(str).str.strip().str.lower()
            == category.strip().lower()
        ]

    if ranked_places.empty:
        return ranked_places

    if "Place_ID" in ranked_places.columns:
        ranked_places = ranked_places.drop_duplicates(subset=["Place_ID"])

    available_columns = []

    for column in ["Rating", "Review_Count"]:

        if column in ranked_places.columns:
            ranked_places[column] = pd.to_numeric(
                ranked_places[column],
                errors="coerce"
            )
            available_columns.append(column)

    if available_columns:
        ranked_places = ranked_places.sort_values(
            by=available_columns,
            ascending=[False] * len(available_columns),
            na_position="last"
        )

    return ranked_places.head(limit).reset_index(drop=True)


def get_popular_places(places, limit=10):

    if places.empty:
        return pd.DataFrame()

    if not all(
        column in places.columns
        for column in ["Rating", "Review_Count"]
    ):
        return pd.DataFrame()

    rated_places = places.copy()

    rated_places["Rating"] = pd.to_numeric(
        rated_places["Rating"], errors="coerce"
    )

    rated_places["Review_Count"] = pd.to_numeric(
        rated_places["Review_Count"], errors="coerce"
    )

    rated_places = rated_places[
        rated_places["Rating"].between(0, 5)
        & (rated_places["Review_Count"] > 0)
    ]

    if rated_places.empty:
        return pd.DataFrame()

    return rank_places(rated_places, limit=limit)


def analyze_review_sentiment(reviews):

    if reviews.empty or "Review_Text" not in reviews.columns:
        return pd.DataFrame()

    result = reviews.copy()

    result["Review_Text"] = (
        result["Review_Text"].fillna("").astype(str).str.strip()
    )

    result = result[result["Review_Text"] != ""].copy()

    if result.empty:
        return pd.DataFrame()

    result["Compound_Score"] = result["Review_Text"].apply(
        lambda review: analyzer.polarity_scores(review)["compound"]
    )

    result["Sentiment"] = result["Compound_Score"].apply(
        lambda score:
            "Positive" if score >= 0.05
            else "Negative" if score <= -0.05
            else "Neutral"
    )

    return result.reset_index(drop=True)


def get_sentiment_summary(reviews):

    analyzed_reviews = analyze_review_sentiment(reviews)

    if analyzed_reviews.empty:
        return pd.DataFrame(
            columns=["Sentiment", "Review_Count", "Percentage"]
        )

    summary = (
        analyzed_reviews["Sentiment"]
        .value_counts()
        .reindex(["Positive", "Negative", "Neutral"], fill_value=0)
        .reset_index()
    )

    summary.columns = ["Sentiment", "Review_Count"]

    total_reviews = summary["Review_Count"].sum()

    summary["Percentage"] = (
        summary["Review_Count"] / total_reviews * 100
    ).round(2)

    return summary
def load_and_analyze_reviews():

    import os

    base_dir = os.path.dirname(
        os.path.dirname(os.path.abspath(__file__))
    )

    file_path = os.path.join(
        base_dir, "data", "raw", "place_reviews.csv"
    )

    if not os.path.exists(file_path):
        return pd.DataFrame(), pd.DataFrame()

    reviews = pd.read_csv(file_path)

    analyzed_reviews = analyze_review_sentiment(reviews)

    summary = get_sentiment_summary(reviews)

    return analyzed_reviews, summary

def calculate_recommendation_score(places):

    if places.empty or "Distance_KM" not in places.columns:
        return pd.DataFrame()

    result = places.copy()

    result["Distance_KM"] = pd.to_numeric(
        result["Distance_KM"],
        errors="coerce"
    )

    result = result.dropna(subset=["Distance_KM"])

    result = result[result["Distance_KM"] >= 0].copy()

    if result.empty:
        return result

    max_distance = result["Distance_KM"].max()

    if max_distance == 0:
        result["Distance_Score"] = 100
    else:
        result["Distance_Score"] = (
            1 - result["Distance_KM"] / max_distance
        ) * 100

    result["Recommendation_Score"] = (
        result["Distance_Score"] * 0.30
    )

    result["Recommendation_Basis"] = "Distance only - ratings unavailable"

    available_weight = 0.30

    if "Rating" in result.columns:

        result["Rating"] = pd.to_numeric(
            result["Rating"], errors="coerce"
        )

        valid_rating = result["Rating"].between(0, 5)

        result.loc[valid_rating, "Recommendation_Score"] += (
            result.loc[valid_rating, "Rating"] / 5 * 100 * 0.40
        )

        result.loc[valid_rating, "Recommendation_Basis"] = (
            "Rating and distance"
        )

        available_weight += 0.40

    if "Review_Count" in result.columns:

        result["Review_Count"] = pd.to_numeric(
            result["Review_Count"], errors="coerce"
        )

        valid_reviews = result["Review_Count"] >= 0

        max_reviews = result.loc[valid_reviews, "Review_Count"].max()

        if pd.notna(max_reviews) and max_reviews > 0:

            result.loc[valid_reviews, "Recommendation_Score"] += (
                result.loc[valid_reviews, "Review_Count"]
                / max_reviews * 100 * 0.30
            )

            result.loc[valid_reviews, "Recommendation_Basis"] = (
                "Rating, reviews and distance"
            )

            available_weight += 0.30

    result["Recommendation_Score"] = (
        result["Recommendation_Score"] / available_weight
    ).round(2)

    return result.sort_values(
        "Recommendation_Score",
        ascending=False
    ).reset_index(drop=True)
from ml.new_features.review_analysis import (
    analyze_reviews,
    get_review_summary,
    analyze_feedback_topics
)
from ml.new_features.popularity_analysis import (
    calculate_popularity_score,
    get_trending_places,
    get_highly_rated_places,
    get_less_reviewed_places
)