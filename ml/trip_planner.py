
import pandas as pd
import os

from ml.recommendation import (
    collect_and_process_city_data,
    calculate_distance
)

from ml.fare_analysis import (
    find_cheapest_transport,
    estimate_transport_fare
)

from ml.new_features.route_service import get_route


BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# ----------------------------------
# LOAD DATASETS
# ----------------------------------

def load_csv(filename):

    file_path = os.path.join(
        BASE_DIR, "data", "raw", filename
    )

    if not os.path.exists(file_path):
        return pd.DataFrame()

    return pd.read_csv(file_path)


def validate_currency(currency):

    currency = str(currency).strip().upper()

    if len(currency) != 3 or not currency.isalpha():
        raise ValueError("Enter a valid three-letter currency code")

    return currency


# ----------------------------------
# PLACE ENTRY FEE ANALYSIS
# ----------------------------------

def get_place_costs(places, country=None, currency=None):

    places = places.copy()
    costs = load_csv("place_costs.csv")

    places["Entry_Fee"] = None
    places["Entry_Fee_Currency"] = None

    if costs.empty:
        return places

    required_columns = [
        "City", "Place_Name", "Entry_Fee",
        "Verification_Status"
    ]

    if not all(column in costs.columns for column in required_columns):
        return places

    if "Country" not in costs.columns:
        costs["Country"] = ""

    if "Currency" not in costs.columns:
        costs["Currency"] = ""

    costs = costs[
        costs["Verification_Status"]
        .astype(str).str.strip().str.lower() == "verified"
    ].copy()

    costs["Entry_Fee"] = pd.to_numeric(
        costs["Entry_Fee"], errors="coerce"
    )

    costs = costs.dropna(subset=["Entry_Fee"])
    costs = costs[costs["Entry_Fee"] >= 0]

    if country:
        costs = costs[
            costs["Country"].astype(str).str.strip().str.lower()
            == country.strip().lower()
        ]

    if currency:
        currency = validate_currency(currency)

        costs = costs[
            costs["Currency"].astype(str).str.strip().str.upper()
            == currency
        ]

    merge_columns = ["City", "Place_Name"]

    if "Country" in places.columns:
        merge_columns.append("Country")

    for column in merge_columns:
        places[column] = places[column].astype(str).str.strip()
        costs[column] = costs[column].astype(str).str.strip()

    costs = costs.drop_duplicates()

    costs["_Match_Count"] = costs.groupby(
        merge_columns
    )["Place_Name"].transform("size")

    costs = costs[costs["_Match_Count"] == 1].copy()
    costs = costs.drop(columns=["_Match_Count"])

    places = places.drop(
        columns=["Entry_Fee", "Entry_Fee_Currency"],
        errors="ignore"
    )

    return places.merge(
        costs[
            merge_columns + ["Entry_Fee", "Currency"]
        ].rename(
            columns={"Currency": "Entry_Fee_Currency"}
        ),
        on=merge_columns,
        how="left",
        suffixes=("", "_cost")
    )


# ----------------------------------
# VERIFIED LOCAL FOOD RECOMMENDATIONS
# ----------------------------------

def recommend_local_food(
    city,
    restaurant_id=None,
    country=None,
    currency=None
):

    food = load_csv("local_food.csv")

    if food.empty:
        return pd.DataFrame()

    required_columns = [
        "City", "Food_Name", "Approx_Price",
        "Currency", "Restaurant_Name", "Restaurant_ID",
        "Source", "Last_Updated", "Verification_Status"
    ]

    if not all(column in food.columns for column in required_columns):
        return pd.DataFrame()

    if "Country" not in food.columns:
        food["Country"] = ""

    city_food = food[
        food["City"].astype(str).str.strip().str.lower()
        == city.strip().lower()
    ].copy()

    if country:
        city_food = city_food[
            city_food["Country"].astype(str).str.strip().str.lower()
            == country.strip().lower()
        ]

    if currency:
        currency = validate_currency(currency)

        city_food = city_food[
            city_food["Currency"].astype(str).str.strip().str.upper()
            == currency
        ]

    city_food["Approx_Price"] = pd.to_numeric(
        city_food["Approx_Price"], errors="coerce"
    )

    city_food = city_food[
        (city_food["Approx_Price"] > 0)
        & (
            city_food["Verification_Status"]
            .astype(str).str.strip().str.lower() == "verified"
        )
    ].copy()

    if restaurant_id is not None:
        city_food = city_food[
            city_food["Restaurant_ID"].astype(str).str.strip()
            == str(restaurant_id).strip()
        ]

    return city_food.sort_values(
        "Approx_Price"
    ).reset_index(drop=True)


# ----------------------------------
# FOOD COST
# ----------------------------------

def get_food_cost(
    city,
    food_name,
    restaurant_id=None,
    country=None,
    currency=None
):

    food = recommend_local_food(
        city,
        restaurant_id,
        country,
        currency
    )

    if food.empty:
        return None

    selected_food = food[
        food["Food_Name"].astype(str).str.strip().str.lower()
        == food_name.strip().lower()
    ]

    if selected_food.empty:
        return None

    return float(selected_food.iloc[0]["Approx_Price"])


# ----------------------------------
# VERIFIED TRANSPORT FARE
# ----------------------------------

def get_transport_cost(
    city,
    starting_point,
    destination,
    country=None,
    currency=None
):

    options = find_cheapest_transport(
        city,
        starting_point,
        destination,
        country,
        currency
    )

    if options.empty:
        return None

    return float(options.iloc[0]["Fare_Amount"])


# ----------------------------------
# ESTIMATED TRANSPORT FARE
# ----------------------------------

def get_transport_estimate(
    distance_km,
    rate_per_km,
    base_fare=0,
    currency="INR"
):

    return estimate_transport_fare(
        distance_km,
        rate_per_km,
        base_fare,
        currency
    )


# ----------------------------------
# COMPLETE TRIP COST CALCULATION
# ----------------------------------

def calculate_trip_cost(
    entry_fee,
    transport_fare,
    food_cost,
    budget,
    transport_fare_status="Verified",
    entry_fee_currency=None,
    transport_fare_currency=None,
    food_cost_currency=None,
    budget_currency=None
):

    budget = float(budget)

    if budget < 0:
        raise ValueError("Budget cannot be negative")

    costs = {
        "Entry_Fee": entry_fee,
        "Transport_Fare": transport_fare,
        "Food_Cost": food_cost
    }

    currencies = {
        "Entry_Fee": entry_fee_currency,
        "Transport_Fare": transport_fare_currency,
        "Food_Cost": food_cost_currency
    }

    missing_costs = []

    for name, value in costs.items():

        if value is None or pd.isna(value):
            missing_costs.append(name)

        elif float(value) < 0:
            raise ValueError(name + " cannot be negative")

    if missing_costs:

        return {
            "Status": "Insufficient cost information",
            "Total_Cost": None,
            "Remaining_Budget": None,
            "Currency": budget_currency,
            "Missing_Costs": missing_costs,
            "Transport_Fare_Status": transport_fare_status
        }

    if budget_currency is None or any(
        currency is None for currency in currencies.values()
    ):

        return {
            "Status": "Currency information required",
            "Total_Cost": None,
            "Remaining_Budget": None,
            "Missing_Costs": [],
            "Transport_Fare_Status": transport_fare_status
        }

    budget_currency = validate_currency(budget_currency)

    currencies = {
        name: validate_currency(currency)
        for name, currency in currencies.items()
    }

    if any(
        currency != budget_currency
        for currency in currencies.values()
    ):

        return {
            "Status": "Currency mismatch - conversion required",
            "Total_Cost": None,
            "Remaining_Budget": None,
            "Currency": budget_currency,
            "Missing_Costs": [],
            "Transport_Fare_Status": transport_fare_status
        }

    total_cost = sum(
        float(value) for value in costs.values()
    )

    remaining_budget = budget - total_cost

    is_estimated = (
        str(transport_fare_status).strip().lower()
        != "verified"
    )

    if is_estimated:
        status = (
            "Estimated total - within budget"
            if total_cost <= budget
            else "Estimated total - over budget"
        )
    else:
        status = (
            "Within budget"
            if total_cost <= budget
            else "Over budget"
        )

    return {
        "Status": status,
        "Total_Cost": round(total_cost, 2),
        "Remaining_Budget": round(remaining_budget, 2),
        "Currency": budget_currency,
        "Missing_Costs": [],
        "Transport_Fare_Status": transport_fare_status,
        "Cost_Details": costs
    }


# ----------------------------------
# MULTI-STOP BUDGET TRIP PLANNER
# ----------------------------------

def create_budget_trip(
    city,
    user_lat,
    user_lon,
    budget,
    max_distance,
    live_data=None,
    country=None,
    currency=None
):

    if budget < 0 or max_distance < 0:
        raise ValueError("Budget and distance cannot be negative")

    if currency:
        currency = validate_currency(currency)

    if live_data is None:
        live_data = collect_and_process_city_data(city)

    if live_data.empty:
        return pd.DataFrame(), pd.DataFrame()

    required_columns = [
        "City", "Place_Name", "Latitude", "Longitude"
    ]

    if not all(column in live_data.columns for column in required_columns):
        return pd.DataFrame(), pd.DataFrame()

    city_places = live_data[
        live_data["City"].astype(str).str.strip().str.lower()
        == city.strip().lower()
    ].copy()

    if city_places.empty:
        return pd.DataFrame(), pd.DataFrame()

    city_places["Latitude"] = pd.to_numeric(
        city_places["Latitude"], errors="coerce"
    )

    city_places["Longitude"] = pd.to_numeric(
        city_places["Longitude"], errors="coerce"
    )

    city_places = city_places.dropna(
        subset=["Latitude", "Longitude"]
    )

    city_places = city_places.drop_duplicates(
        subset=["Place_Name", "Latitude", "Longitude"]
    ).reset_index(drop=True)

    if city_places.empty:
        return pd.DataFrame(), pd.DataFrame()

    city_places["Distance_KM"] = calculate_distance(
        user_lat,
        user_lon,
        city_places["Latitude"],
        city_places["Longitude"]
    )

    city_places = city_places[
        city_places["Distance_KM"] <= max_distance
    ].copy()

    if city_places.empty:
        return pd.DataFrame(), pd.DataFrame()

    city_places = get_place_costs(
        city_places,
        country=country,
        currency=currency
    )

    city_places["Entry_Fee_Status"] = city_places[
        "Entry_Fee"
    ].apply(
        lambda fee: "Verified"
        if pd.notna(fee)
        else "Not available"
    )

    available_currencies = (
        city_places["Entry_Fee_Currency"]
        .dropna()
        .astype(str)
        .str.strip()
        .str.upper()
    )

    available_currencies = [
        value for value in available_currencies if value
    ]

    if currency is None and len(set(available_currencies)) > 1:

        city_places["Entry_Fee_Status"] = (
            "Currency selection required"
        )

        return pd.DataFrame(), city_places.reset_index(drop=True)

    if currency is None and available_currencies:
        currency = available_currencies[0]

    verified_places = city_places[
        city_places["Entry_Fee_Status"] == "Verified"
    ].copy()

    unavailable_places = city_places[
        city_places["Entry_Fee_Status"] != "Verified"
    ].copy()

    remaining_budget = float(budget)
    current_lat = float(user_lat)
    current_lon = float(user_lon)

    selected_places = []
    cumulative_distance = 0.0

    # Greedy nearest-next-stop route planning
    while not verified_places.empty:

        verified_places["Distance_From_Previous_KM"] = (
            calculate_distance(
                current_lat,
                current_lon,
                verified_places["Latitude"],
                verified_places["Longitude"]
            )
        )

        nearest_places = verified_places.sort_values(
            "Distance_From_Previous_KM"
        )

        affordable_places = nearest_places[
            nearest_places["Entry_Fee"] <= remaining_budget
        ]

        if affordable_places.empty:
            break

        selected_index = affordable_places.index[0]
        selected_place = verified_places.loc[selected_index].copy()

        leg_distance = float(
            selected_place["Distance_From_Previous_KM"]
        )

        cumulative_distance += leg_distance
        remaining_budget -= float(selected_place["Entry_Fee"])

        selected_place["Trip_Stop"] = len(selected_places) + 1

        selected_place["Cumulative_Travel_Distance_KM"] = round(
            cumulative_distance, 2
        )

        selected_place["Remaining_Budget"] = round(
            remaining_budget, 2
        )

        selected_place["Budget_Currency"] = currency

        selected_places.append(selected_place)

        current_lat = float(selected_place["Latitude"])
        current_lon = float(selected_place["Longitude"])

        verified_places = verified_places.drop(
            index=selected_index
        )

    if selected_places:

        selected_places = pd.DataFrame(selected_places)

        selected_places = selected_places.sort_values(
            "Trip_Stop"
        ).reset_index(drop=True)

    else:

        selected_places = pd.DataFrame(
            columns=list(city_places.columns)
            + [
                "Distance_From_Previous_KM",
                "Trip_Stop",
                "Cumulative_Travel_Distance_KM",
                "Remaining_Budget",
                "Budget_Currency"
            ]
        )

    # ----------------------------------
    # OSRM ROAD ROUTE INTEGRATION
    # ----------------------------------

    route_columns = [
        "Route_Status",
        "Road_Distance_KM",
        "Estimated_Travel_Minutes",
        "Route_Geometry"
    ]

    for column in route_columns:
        selected_places[column] = None

    current_lat = float(user_lat)
    current_lon = float(user_lon)

    for index, place in selected_places.iterrows():

        route = get_route(
            current_lat,
            current_lon,
            float(place["Latitude"]),
            float(place["Longitude"])
        )

        selected_places.at[index, "Route_Status"] = route["Status"]

        if route["Status"] == "Success":

            selected_places.at[index, "Road_Distance_KM"] = (
                route["Distance_KM"]
            )

            selected_places.at[index, "Estimated_Travel_Minutes"] = (
                route["Duration_Minutes"]
            )

            selected_places.at[index, "Route_Geometry"] = (
                route["Route_Geometry"]
            )

        current_lat = float(place["Latitude"])
        current_lon = float(place["Longitude"])

    unavailable_places = unavailable_places.reset_index(drop=True)

    return selected_places, unavailable_places


# ----------------------------------
# SMART TRIP PLANNER IMPORTS
# ----------------------------------

from ml.new_features.smart_trip_planner import (
    create_itinerary,
    calculate_complete_budget
)
