
import pandas as pd
import math


def calculate_distance(lat1, lon1, lat2, lon2):

    earth_radius = 6371

    lat1, lon1, lat2, lon2 = map(
        math.radians, [lat1, lon1, lat2, lon2]
    )

    latitude_difference = lat2 - lat1
    longitude_difference = lon2 - lon1

    value = (
        math.sin(latitude_difference / 2) ** 2
        + math.cos(lat1) * math.cos(lat2)
        * math.sin(longitude_difference / 2) ** 2
    )

    return 2 * earth_radius * math.asin(math.sqrt(value))


def create_itinerary(places, start_latitude, start_longitude):

    if places.empty:
        return pd.DataFrame()

    required_columns = ["Place_Name", "Latitude", "Longitude"]

    if not all(column in places.columns for column in required_columns):
        raise ValueError("Required place columns are missing")

    remaining = places.copy()

    remaining["Latitude"] = pd.to_numeric(
        remaining["Latitude"], errors="coerce"
    )

    remaining["Longitude"] = pd.to_numeric(
        remaining["Longitude"], errors="coerce"
    )

    remaining = remaining.dropna(
        subset=["Place_Name", "Latitude", "Longitude"]
    ).reset_index(drop=True)

    itinerary = []
    current_latitude = float(start_latitude)
    current_longitude = float(start_longitude)

    while not remaining.empty:

        remaining["Distance_From_Current_KM"] = remaining.apply(
            lambda row: calculate_distance(
                current_latitude,
                current_longitude,
                row["Latitude"],
                row["Longitude"]
            ),
            axis=1
        )

        nearest_index = remaining[
            "Distance_From_Current_KM"
        ].idxmin()

        selected = remaining.loc[nearest_index].copy()
        itinerary.append(selected)

        current_latitude = selected["Latitude"]
        current_longitude = selected["Longitude"]

        remaining = remaining.drop(index=nearest_index)

    result = pd.DataFrame(itinerary).reset_index(drop=True)
    result["Visit_Order"] = range(1, len(result) + 1)

    return result


def calculate_complete_budget(
    entry_fee,
    food_cost,
    transport_cost,
    budget,
    currency
):

    costs = {
        "Entry_Fee": entry_fee,
        "Food_Cost": food_cost,
        "Transport_Cost": transport_cost
    }

    missing_costs = [
        name for name, value in costs.items()
        if value is None
    ]

    if missing_costs:
        return {
            "Status": "Incomplete cost information",
            "Total_Cost": None,
            "Remaining_Budget": None,
            "Missing_Costs": missing_costs,
            "Currency": currency
        }

    try:
        values = {
            name: float(value) for name, value in costs.items()
        }
        budget = float(budget)
    except (TypeError, ValueError):
        raise ValueError("Cost and budget values must be numeric")

    if any(value < 0 for value in values.values()) or budget < 0:
        raise ValueError("Costs and budget cannot be negative")

    total_cost = sum(values.values())
    remaining_budget = budget - total_cost

    return {
        "Status": (
            "Within Budget"
            if remaining_budget >= 0
            else "Over Budget"
        ),
        "Total_Cost": round(total_cost, 2),
        "Remaining_Budget": round(remaining_budget, 2),
        "Missing_Costs": [],
        "Currency": currency,
        "Cost_Details": values
    }
