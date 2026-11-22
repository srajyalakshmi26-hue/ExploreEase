
import pandas as pd
import os
import re
from urllib.parse import urlparse
from datetime import date


BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

SUBMISSION_PATH = os.path.join(
    BASE_DIR, "data", "raw", "food_price_submissions.csv"
)

FOOD_PATH = os.path.join(
    BASE_DIR, "data", "raw", "local_food.csv"
)


SUBMISSION_COLUMNS = [
    "City", "Food_Name", "Restaurant_Name", "Restaurant_ID",
    "Submitted_Price", "Currency", "Portion_Size", "Source",
    "Source_URL", "Submitted_Date", "Verification_Status",
    "Verification_Notes", "Country", "Latitude", "Longitude"
]

FOOD_COLUMNS = [
    "City", "Food_Name", "Description", "Approx_Price",
    "Currency", "Restaurant_Name", "Restaurant_ID",
    "Source", "Last_Updated", "Verification_Status",
    "Country", "Latitude", "Longitude"
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

    if not re.fullmatch(r"[A-Z]{3}", currency):
        raise ValueError("Enter a valid three-letter currency code")

    return currency


def validate_location(latitude=None, longitude=None):

    if latitude is None and longitude is None:
        return None, None

    if latitude is None or longitude is None:
        raise ValueError("Both latitude and longitude are required")

    latitude = float(latitude)
    longitude = float(longitude)

    if not -90 <= latitude <= 90:
        raise ValueError("Invalid latitude")

    if not -180 <= longitude <= 180:
        raise ValueError("Invalid longitude")

    return latitude, longitude


def validate_price_source(source, source_url, evidence_checked):

    if evidence_checked is not True:
        raise ValueError(
            "Check the official menu or authorized source before adding a price"
        )

    parsed_url = urlparse(source_url.strip())

    if parsed_url.scheme != "https" or not parsed_url.netloc:
        raise ValueError("A valid HTTPS source URL is required")

    if not source.strip():
        raise ValueError("Source name is required")


def add_authorized_food_price(
    city,
    food_name,
    restaurant_name,
    restaurant_id,
    price,
    source,
    source_url,
    evidence_checked=False,
    currency="INR",
    country="",
    latitude=None,
    longitude=None
):

    validate_price_source(source, source_url, evidence_checked)

    price = float(price)
    currency = validate_currency(currency)

    latitude, longitude = validate_location(latitude, longitude)

    if price <= 0:
        raise ValueError("Price must be greater than zero")

    if not city.strip() or not food_name.strip():
        raise ValueError("City and food name are required")

    if not restaurant_name.strip():
        raise ValueError("Restaurant name is required")

    foods = load_data(FOOD_PATH, FOOD_COLUMNS)

    duplicate = foods[
        (foods["City"].astype(str).str.lower() == city.strip().lower())
        & (foods["Food_Name"].astype(str).str.lower() == food_name.strip().lower())
        & (foods["Restaurant_ID"].astype(str) == str(restaurant_id))
        & (foods["Currency"].astype(str).str.upper() == currency)
        & (pd.to_numeric(foods["Approx_Price"], errors="coerce") == price)
        & (foods["Verification_Status"].astype(str).str.lower() == "verified")
    ]

    if not duplicate.empty:
        raise ValueError("This verified price already exists")

    new_food = {
        "City": city.strip(),
        "Food_Name": food_name.strip(),
        "Description": "",
        "Approx_Price": price,
        "Currency": currency,
        "Restaurant_Name": restaurant_name.strip(),
        "Restaurant_ID": restaurant_id,
        "Source": f"{source.strip()} | {source_url.strip()}",
        "Last_Updated": date.today().isoformat(),
        "Verification_Status": "Verified",
        "Country": country.strip(),
        "Latitude": latitude,
        "Longitude": longitude
    }

    foods = pd.concat(
        [foods, pd.DataFrame([new_food])],
        ignore_index=True
    )

    foods.to_csv(FOOD_PATH, index=False)

    return "Authorized food price added successfully"


def submit_food_price(
    city,
    food_name,
    restaurant_name,
    restaurant_id,
    price,
    currency="INR",
    portion_size="",
    source="",
    source_url="",
    country="",
    latitude=None,
    longitude=None
):

    price = float(price)
    currency = validate_currency(currency)

    latitude, longitude = validate_location(latitude, longitude)

    if price <= 0:
        raise ValueError("Price must be greater than zero")

    if not city.strip() or not food_name.strip():
        raise ValueError("City and food name are required")

    if not restaurant_name.strip():
        raise ValueError("Restaurant name is required")

    submissions = load_data(
        SUBMISSION_PATH,
        SUBMISSION_COLUMNS
    )

    new_submission = {
        "City": city.strip(),
        "Food_Name": food_name.strip(),
        "Restaurant_Name": restaurant_name.strip(),
        "Restaurant_ID": restaurant_id,
        "Submitted_Price": price,
        "Currency": currency,
        "Portion_Size": portion_size,
        "Source": source,
        "Source_URL": source_url,
        "Submitted_Date": date.today().isoformat(),
        "Verification_Status": "Pending",
        "Verification_Notes": "",
        "Country": country.strip(),
        "Latitude": latitude,
        "Longitude": longitude
    }

    submissions = pd.concat(
        [submissions, pd.DataFrame([new_submission])],
        ignore_index=True
    )

    submissions.to_csv(SUBMISSION_PATH, index=False)

    return "Submission saved as Pending"


def verify_food_price(
    submission_index,
    verified_price,
    verification_source,
    verification_url,
    evidence_checked=False
):

    validate_price_source(
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

    if str(submission["Verification_Status"]).strip().lower() == "verified":
        raise ValueError("Already verified")

    verified_price = float(verified_price)

    if verified_price <= 0:
        raise ValueError("Verified price must be greater than zero")

    submitted_price = float(submission["Submitted_Price"])

    if submitted_price != verified_price:
        raise ValueError("Price mismatch. Submission remains Pending.")

    foods = load_data(FOOD_PATH, FOOD_COLUMNS)

    new_food = {
        "City": submission["City"],
        "Food_Name": submission["Food_Name"],
        "Description": "",
        "Approx_Price": verified_price,
        "Currency": submission["Currency"],
        "Restaurant_Name": submission["Restaurant_Name"],
        "Restaurant_ID": submission["Restaurant_ID"],
        "Source": f"{verification_source.strip()} | {verification_url.strip()}",
        "Last_Updated": date.today().isoformat(),
        "Verification_Status": "Verified",
        "Country": submission["Country"],
        "Latitude": submission["Latitude"],
        "Longitude": submission["Longitude"]
    }

    foods = pd.concat(
        [foods, pd.DataFrame([new_food])],
        ignore_index=True
    )

    foods.to_csv(FOOD_PATH, index=False)

    submissions.loc[
        submission_index, "Verification_Status"
    ] = "Verified"

    submissions.loc[
        submission_index, "Verification_Notes"
    ] = "Price manually checked against authorized source"

    submissions.to_csv(SUBMISSION_PATH, index=False)

    return "Food price verified successfully"
