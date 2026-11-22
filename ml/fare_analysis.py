
import pandas as pd
import os


BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

FARE_PATH = os.path.join(
    BASE_DIR, "data", "raw", "transport_fares.csv"
)


def validate_currency(currency):

    currency = str(currency).strip().upper()

    if len(currency) != 3 or not currency.isalpha():
        raise ValueError("Enter a valid three-letter currency code")

    return currency


def load_fare_data():

    if not os.path.exists(FARE_PATH):
        return pd.DataFrame()

    return pd.read_csv(FARE_PATH)


def find_transport_options(
    city,
    starting_point,
    destination,
    country=None,
    currency=None
):

    fares_df = load_fare_data()

    if fares_df.empty:
        return pd.DataFrame()

    required_columns = [
        "City",
        "Starting_Point",
        "Destination",
        "Transport_Type",
        "Fare_Amount",
        "Verification_Status",
        "Currency"
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

    route_fares = fares_df[
        (fares_df["City"] == city.strip().lower())
        & (fares_df["Starting_Point"] == starting_point.strip().lower())
        & (fares_df["Destination"] == destination.strip().lower())
    ].copy()

    if country:

        if "Country" not in route_fares.columns:
            return pd.DataFrame()

        route_fares = route_fares[
            route_fares["Country"].astype(str).str.strip().str.lower()
            == country.strip().lower()
        ]

    if currency:

        currency = validate_currency(currency)

        route_fares = route_fares[
            route_fares["Currency"].astype(str).str.strip().str.upper()
            == currency
        ]

    route_fares["Currency"] = (
        route_fares["Currency"].astype(str).str.strip().str.upper()
    )

    route_fares["Fare_Amount"] = pd.to_numeric(
        route_fares["Fare_Amount"],
        errors="coerce"
    )

    route_fares = route_fares.dropna(subset=["Fare_Amount"])

    route_fares = route_fares[
        route_fares["Fare_Amount"] >= 0
    ]

    if currency:
        route_fares = route_fares.sort_values("Fare_Amount")
    else:
        route_fares = route_fares.sort_values(
            ["Currency", "Fare_Amount"]
        )

    return route_fares.reset_index(drop=True)


def find_cheapest_transport(
    city,
    starting_point,
    destination,
    country=None,
    currency=None
):

    options = find_transport_options(
        city,
        starting_point,
        destination,
        country,
        currency
    )

    if options.empty:
        return pd.DataFrame()

    # Different currencies cannot be compared directly.
    if currency is None and options["Currency"].nunique() > 1:
        return pd.DataFrame()

    return options.head(1)


def estimate_transport_fare(
    distance_km,
    rate_per_km,
    base_fare=0,
    currency="INR"
):

    distance_km = float(distance_km)
    rate_per_km = float(rate_per_km)
    base_fare = float(base_fare)

    currency = validate_currency(currency)

    if distance_km < 0 or rate_per_km < 0 or base_fare < 0:
        raise ValueError("Fare inputs cannot be negative")

    estimated_fare = base_fare + (
        distance_km * rate_per_km
    )

    return {
        "Distance_KM": round(distance_km, 2),
        "Estimated_Fare": round(estimated_fare, 2),
        "Currency": currency,
        "Fare_Status": "Estimated - Not Verified"
    }
