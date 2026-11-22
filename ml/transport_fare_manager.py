
import pandas as pd
import os
from urllib.parse import urlparse
from datetime import date


BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

FARE_PATH = os.path.join(
    BASE_DIR, "data", "raw", "transport_fares.csv"
)

SUBMISSION_PATH = os.path.join(
    BASE_DIR, "data", "raw", "transport_fare_submissions.csv"
)


FARE_COLUMNS = [
    "City", "Starting_Point", "Destination", "Transport_Type",
    "Fare_Amount", "Distance_KM", "Submitted_Date",
    "Verification_Status", "Source", "Country", "Currency",
    "Starting_Latitude", "Starting_Longitude",
    "Destination_Latitude", "Destination_Longitude",
    "Last_Updated"
]

SUBMISSION_COLUMNS = FARE_COLUMNS + [
    "Source_URL", "Verification_Notes"
]


def load_data(file_path, columns):

    if not os.path.exists(file_path):
        return pd.DataFrame(columns=columns)

    data = pd.read_csv(file_path)

    for column in columns:
        if column not in data.columns:
            data[column] = ""

    return data[columns]


def validate_currency(currency):

    currency = str(currency).strip().upper()

    if len(currency) != 3 or not currency.isalpha():
        raise ValueError("Enter a valid three-letter currency code")

    return currency


def validate_coordinates(
    starting_latitude=None,
    starting_longitude=None,
    destination_latitude=None,
    destination_longitude=None
):

    coordinates = [
        starting_latitude,
        starting_longitude,
        destination_latitude,
        destination_longitude
    ]

    if all(value is None for value in coordinates):
        return coordinates

    if any(value is None for value in coordinates):
        raise ValueError("Provide all four route coordinates")

    coordinates = [float(value) for value in coordinates]

    if not -90 <= coordinates[0] <= 90:
        raise ValueError("Invalid starting latitude")

    if not -180 <= coordinates[1] <= 180:
        raise ValueError("Invalid starting longitude")

    if not -90 <= coordinates[2] <= 90:
        raise ValueError("Invalid destination latitude")

    if not -180 <= coordinates[3] <= 180:
        raise ValueError("Invalid destination longitude")

    return coordinates


def validate_source(source, source_url, evidence_checked):

    if evidence_checked is not True:
        raise ValueError(
            "Check an official or authorized fare source before verification"
        )

    parsed_url = urlparse(source_url.strip())

    if parsed_url.scheme != "https" or not parsed_url.netloc:
        raise ValueError("A valid HTTPS source URL is required")

    if not source.strip():
        raise ValueError("Source name is required")


def submit_transport_fare(
    city,
    starting_point,
    destination,
    transport_type,
    fare_amount,
    country,
    currency,
    source="",
    source_url="",
    distance_km=None,
    starting_latitude=None,
    starting_longitude=None,
    destination_latitude=None,
    destination_longitude=None
):

    fare_amount = float(fare_amount)
    currency = validate_currency(currency)

    if fare_amount < 0:
        raise ValueError("Fare cannot be negative")

    if not city.strip() or not country.strip():
        raise ValueError("City and country are required")

    if not starting_point.strip() or not destination.strip():
        raise ValueError("Starting point and destination are required")

    if not transport_type.strip():
        raise ValueError("Transport type is required")

    if distance_km is not None:
        distance_km = float(distance_km)

        if distance_km < 0:
            raise ValueError("Distance cannot be negative")

    coordinates = validate_coordinates(
        starting_latitude,
        starting_longitude,
        destination_latitude,
        destination_longitude
    )

    submissions = load_data(
        SUBMISSION_PATH,
        SUBMISSION_COLUMNS
    )

    new_submission = {
        "City": city.strip(),
        "Starting_Point": starting_point.strip(),
        "Destination": destination.strip(),
        "Transport_Type": transport_type.strip(),
        "Fare_Amount": fare_amount,
        "Distance_KM": distance_km,
        "Submitted_Date": date.today().isoformat(),
        "Verification_Status": "Pending",
        "Source": source,
        "Country": country.strip(),
        "Currency": currency,
        "Starting_Latitude": coordinates[0],
        "Starting_Longitude": coordinates[1],
        "Destination_Latitude": coordinates[2],
        "Destination_Longitude": coordinates[3],
        "Last_Updated": "",
        "Source_URL": source_url,
        "Verification_Notes": ""
    }

    submissions = pd.concat(
        [submissions, pd.DataFrame([new_submission])],
        ignore_index=True
    )

    submissions.to_csv(SUBMISSION_PATH, index=False)

    return "Transport fare submission saved as Pending"


def verify_transport_fare(
    submission_index,
    verified_fare,
    verification_source,
    verification_url,
    evidence_checked=False
):

    validate_source(
        verification_source,
        verification_url,
        evidence_checked
    )

    submissions = load_data(
        SUBMISSION_PATH,
        SUBMISSION_COLUMNS
    )

    if submission_index not in submissions.index:
        raise IndexError("Invalid submission index")

    submission = submissions.loc[submission_index]

    if str(submission["Verification_Status"]).lower() == "verified":
        raise ValueError("This fare is already verified")

    verified_fare = float(verified_fare)

    if verified_fare < 0:
        raise ValueError("Verified fare cannot be negative")

    submitted_fare = float(submission["Fare_Amount"])

    if submitted_fare != verified_fare:
        raise ValueError(
            "Fare mismatch. Submission remains Pending."
        )

    fares = load_data(FARE_PATH, FARE_COLUMNS)

    new_fare = {
        column: submission[column]
        for column in FARE_COLUMNS
    }

    new_fare["Source"] = (
        f"{verification_source.strip()} | {verification_url.strip()}"
    )

    new_fare["Verification_Status"] = "Verified"
    new_fare["Last_Updated"] = date.today().isoformat()

    fares = pd.concat(
        [fares, pd.DataFrame([new_fare])],
        ignore_index=True
    )

    fares.to_csv(FARE_PATH, index=False)

    submissions.loc[
        submission_index, "Verification_Status"
    ] = "Verified"

    submissions.loc[
        submission_index, "Verification_Notes"
    ] = "Fare manually checked against authorized source"

    submissions.to_csv(SUBMISSION_PATH, index=False)

    return "Transport fare verified successfully"
