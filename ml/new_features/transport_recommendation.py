
import pandas as pd


def recommend_transport(
    fares,
    city,
    starting_point,
    destination,
    country=None,
    currency=None
):

    if fares.empty:
        return pd.DataFrame()

    required_columns = [
        "City",
        "Starting_Point",
        "Destination",
        "Transport_Type",
        "Fare_Amount",
        "Currency",
        "Verification_Status"
    ]

    if not all(column in fares.columns for column in required_columns):
        raise ValueError("Required transport columns are missing")

    options = fares.copy()

    options = options[
        options["Verification_Status"].astype(str).str.strip().str.lower()
        == "verified"
    ].copy()

    for column in ["City", "Starting_Point", "Destination"]:
        options[column] = options[column].astype(str).str.strip().str.lower()

    options = options[
        (options["City"] == city.strip().lower())
        & (options["Starting_Point"] == starting_point.strip().lower())
        & (options["Destination"] == destination.strip().lower())
    ].copy()

    if country:
        if "Country" not in options.columns:
            return pd.DataFrame()

        options = options[
            options["Country"].astype(str).str.strip().str.lower()
            == country.strip().lower()
        ]

    if currency:
        currency = currency.strip().upper()

        if len(currency) != 3 or not currency.isalpha():
            raise ValueError("Enter a valid three-letter currency code")

        options = options[
            options["Currency"].astype(str).str.strip().str.upper()
            == currency
        ]

    options["Fare_Amount"] = pd.to_numeric(
        options["Fare_Amount"], errors="coerce"
    )

    options = options.dropna(subset=["Fare_Amount"])
    options = options[options["Fare_Amount"] >= 0]

    if options.empty:
        return options

    if not currency and options["Currency"].nunique() > 1:
        return options.sort_values(
            ["Currency", "Fare_Amount"]
        ).reset_index(drop=True)

    return options.sort_values(
        "Fare_Amount"
    ).reset_index(drop=True)


def get_cheapest_transport(options):

    if options.empty:
        return pd.DataFrame()

    if options["Currency"].nunique() > 1:
        return pd.DataFrame()

    return options.head(1).copy().reset_index(drop=True)
