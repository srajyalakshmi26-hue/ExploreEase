
import pandas as pd


def recommend_places(
    places,
    interests=None,
    max_distance=None,
    minimum_rating=None,
    limit=10
):

    if places.empty:
        return pd.DataFrame()

    recommendations = places.copy()

    if max_distance is not None and "Distance_KM" in recommendations.columns:
        recommendations["Distance_KM"] = pd.to_numeric(
            recommendations["Distance_KM"], errors="coerce"
        )
        recommendations = recommendations[
            recommendations["Distance_KM"].notna()
            & (recommendations["Distance_KM"] <= max_distance)
        ]

    if recommendations.empty:
        return recommendations

    if minimum_rating is not None and "Average_Rating" in recommendations.columns:
        recommendations = recommendations[
            pd.to_numeric(
                recommendations["Average_Rating"], errors="coerce"
            ) >= minimum_rating
        ]

    if recommendations.empty:
        return recommendations

    interests = [item.lower().strip() for item in (interests or [])]

    if interests and "Category" in recommendations.columns:
        recommendations["Interest_Match"] = recommendations["Category"].apply(
            lambda category: any(
                interest in str(category).lower()
                for interest in interests
            )
        )
    else:
        recommendations["Interest_Match"] = False

    score_columns = {
        "Average_Rating": (0.35, 5),
        "Positive_Percentage": (0.25, 100),
        "Popularity_Score": (0.25, 100)
    }

    recommendations["Recommendation_Score"] = 0.0
    recommendations["Available_Score_Weight"] = 0.0

    for column, (weight, maximum) in score_columns.items():

        if column not in recommendations.columns:
            continue

        values = pd.to_numeric(
            recommendations[column], errors="coerce"
        )

        valid = values.notna()

        if valid.any():
            recommendations.loc[valid, "Recommendation_Score"] += (
                values[valid].clip(0, maximum) / maximum * weight * 100
            )

            recommendations.loc[valid, "Available_Score_Weight"] += weight

    recommendations["Recommendation_Score"] = (
        recommendations["Recommendation_Score"]
        / recommendations["Available_Score_Weight"].replace(0, float("nan"))
    ).fillna(0)

    recommendations.loc[
        recommendations["Interest_Match"],
        "Recommendation_Score"
    ] += 10

    recommendations["Recommendation_Score"] = (
        recommendations["Recommendation_Score"].clip(0, 100).round(2)
    )

    recommendations["Recommendation_Reason"] = recommendations.apply(
        lambda row: (
            "Matches your interests"
            if row["Interest_Match"]
            else "Recommended based on available visitor feedback"
            if row["Available_Score_Weight"] > 0
            else "Recommended based on available location information"
        ),
        axis=1
    )

    return recommendations.sort_values(
        ["Recommendation_Score", "Distance_KM"]
        if "Distance_KM" in recommendations.columns
        else ["Recommendation_Score"],
        ascending=[False, True]
        if "Distance_KM" in recommendations.columns
        else [False]
    ).head(limit).reset_index(drop=True)
