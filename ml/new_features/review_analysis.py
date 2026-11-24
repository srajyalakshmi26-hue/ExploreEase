
import pandas as pd
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

analyzer = SentimentIntensityAnalyzer()


def analyze_reviews(reviews):

    if reviews.empty:
        return pd.DataFrame()

    required_columns = ["Place_ID", "Rating", "Review_Text"]

    if not all(column in reviews.columns for column in required_columns):
        raise ValueError("Required review columns are missing")

    reviews = reviews.copy()

    reviews["Rating"] = pd.to_numeric(
        reviews["Rating"], errors="coerce"
    )

    reviews = reviews.dropna(subset=["Place_ID", "Rating", "Review_Text"])

    reviews = reviews[
        reviews["Rating"].between(1, 5)
        & reviews["Review_Text"].astype(str).str.strip().ne("")
    ].copy()

    reviews["Sentiment_Score"] = reviews["Review_Text"].apply(
        lambda text: analyzer.polarity_scores(str(text))["compound"]
    )

    reviews["Sentiment"] = reviews["Sentiment_Score"].apply(
        lambda score: (
            "Positive" if score >= 0.05
            else "Negative" if score <= -0.05
            else "Neutral"
        )
    )

    return reviews


def get_review_summary(reviews):

    if reviews.empty:
        return pd.DataFrame()

    summary = reviews.groupby("Place_ID").agg(
        Average_Rating=("Rating", "mean"),
        Total_Reviews=("Rating", "count"),
        Positive_Reviews=(
            "Sentiment",
            lambda values: (values == "Positive").sum()
        ),
        Negative_Reviews=(
            "Sentiment",
            lambda values: (values == "Negative").sum()
        ),
        Neutral_Reviews=(
            "Sentiment",
            lambda values: (values == "Neutral").sum()
        )
    ).reset_index()

    summary["Average_Rating"] = summary["Average_Rating"].round(2)

    summary["Positive_Percentage"] = (
        summary["Positive_Reviews"] / summary["Total_Reviews"] * 100
    ).round(2)

    return summary


def analyze_feedback_topics(reviews):

    topics = {
        "Cleanliness": ["clean", "dirty", "hygiene"],
        "Safety": ["safe", "unsafe", "security"],
        "Crowd": ["crowded", "crowd", "busy"],
        "Maintenance": ["maintenance", "damaged", "facilities"]
    }

    if reviews.empty:
        return pd.DataFrame()

    results = []

    for place_id, group in reviews.groupby("Place_ID"):

        for topic, keywords in topics.items():

            count = group["Review_Text"].astype(str).apply(
                lambda text: any(
                    word in text.lower() for word in keywords
                )
            ).sum()

            results.append({
                "Place_ID": place_id,
                "Topic": topic,
                "Mention_Count": int(count)
            })

    return pd.DataFrame(results)
