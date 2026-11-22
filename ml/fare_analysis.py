
import pandas as pd
import os


BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

FARE_PATH = os.path.join(
    BASE_DIR,
    "data",
    "raw",
    "transport_fares.csv"
)


def load_fare_data():

    if not os.path.exists(FARE_PATH):
        return pd.DataFrame()

    return pd.read_csv(FARE_PATH)


def find_transport_options(city, starting_point, destination):

    fares_df = load_fare_data()

    if fares_df.empty:
        return pd.DataFrame()

    required_columns = [
        "City",
        "Starting_Point",
        "Destination",
        "Transport_Type",
        "Fare_Amount",
        "Verification_Status"
    ]

    if not all(column in fares_df.columns for column in required_columns):
        return pd.DataFrame()

    fares_df = fares_df[
        fares_df["Verification_Status"]
        .astype(str).str.strip().str.lower() == "verified"
    ].copy()

    for column in ["City", "Starting_Point", "Destination"]:
        fares_df[column] = (
            fares_df[column].astype(str).str.strip().str.lower()
        )

    city = city.strip().lower()
    starting_point = starting_point.strip().lower()
    destination = destination.strip().lower()

    route_fares = fares_df[
        (fares_df["City"] == city)
        & (fares_df["Starting_Point"] == starting_point)
        & (fares_df["Destination"] == destination)
    ].copy()

    route_fares["Fare_Amount"] = pd.to_numeric(
        route_fares["Fare_Amount"],
        errors="coerce"
    )

    route_fares = route_fares.dropna(subset=["Fare_Amount"])

    route_fares = route_fares[
        route_fares["Fare_Amount"] >= 0
    ]

    return route_fares.sort_values(
        "Fare_Amount"
    ).reset_index(drop=True)


def find_cheapest_transport(city, starting_point, destination):

    options = find_transport_options(
        city, starting_point, destination
    )

    if options.empty:
        return pd.DataFrame()

    return options.head(1)


def estimate_transport_fare(distance_km, rate_per_km, base_fare=0):

    if distance_km < 0 or rate_per_km < 0 or base_fare < 0:
        raise ValueError("Fare inputs cannot be negative")

    estimated_fare = base_fare + (distance_km * rate_per_km)

    return {
        "Distance_KM": round(distance_km, 2),
        "Estimated_Fare": round(estimated_fare, 2),
        "Currency": "INR",
        "Fare_Status": "Estimated - Not Verified"
    }
