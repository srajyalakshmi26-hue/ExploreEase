
import pandas as pd


def recommend_food(
    foods,
    preferences=None,
    city=None,
    minimum_rating=None,
    limit=10
):

    if foods.empty:
        return pd.DataFrame()

    recommendations = foods.copy()

    if city and "City" in recommendations.columns:
        recommendations = recommendations[
            recommendations["City"].astype(str).str.strip().str.lower()
            == city.strip().lower()
        ]

    if preferences:
        preferences = [
            item.strip().lower() for item in preferences
        ]

        searchable_columns = [
            column for column in ["Food_Name", "Description"]
            if column in recommendations.columns
        ]

        if searchable_columns:
            matches = recommendations[searchable_columns].fillna("").apply(
                lambda row: any(
                    preference in " ".join(row.astype(str)).lower()
                    for preference in preferences
                ),
                axis=1
            )

            recommendations = recommendations[matches]

    if minimum_rating is not None:
        if "Average_Rating" not in recommendations.columns:
            return pd.DataFrame()

        recommendations["Average_Rating"] = pd.to_numeric(
            recommendations["Average_Rating"], errors="coerce"
        )

        recommendations = recommendations[
            recommendations["Average_Rating"] >= minimum_rating
        ]

    if recommendations.empty:
        return recommendations

    if "Average_Rating" in recommendations.columns:
        recommendations = recommendations.sort_values(
            "Average_Rating", ascending=False, na_position="last"
        )

    return recommendations.head(limit).reset_index(drop=True)


def get_food_details(foods, food_name):

    if foods.empty or "Food_Name" not in foods.columns:
        return pd.DataFrame()

    return foods[
        foods["Food_Name"].astype(str).str.strip().str.lower()
        == food_name.strip().lower()
    ].copy().reset_index(drop=True)
