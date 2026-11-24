import pandas as pd

from sqlalchemy import text

from app.db.database import engine


# --------------------------------------------------
# DATABASE DATA SERVICE
# All datasets are retrieved from Neon PostgreSQL.
# Original CSV column names are preserved for API/ML.
# --------------------------------------------------


def _read_table(query: str) -> pd.DataFrame:
    """
    Execute a PostgreSQL query and return a DataFrame.
    """

    with engine.connect() as connection:
        return pd.read_sql_query(
            text(query),
            connection
        )


# --------------------------------------------------
# TOURIST PLACES
# --------------------------------------------------

def places() -> pd.DataFrame:

    query = """
        SELECT
            city AS "City",
            place_name AS "Place_Name",
            category AS "Category",
            latitude AS "Latitude",
            longitude AS "Longitude",
            osm_id AS "OSM_ID"
        FROM tourist_places
        ORDER BY city, place_name
    """

    return _read_table(query)


# --------------------------------------------------
# RESTAURANTS
# --------------------------------------------------

def restaurants() -> pd.DataFrame:

    query = """
        SELECT
            city AS "City",
            restaurant_name AS "Restaurant_Name",
            category AS "Category",
            cuisine AS "Cuisine",
            latitude AS "Latitude",
            longitude AS "Longitude",
            osm_id AS "OSM_ID"
        FROM restaurants
        ORDER BY city, restaurant_name
    """

    return _read_table(query)


# --------------------------------------------------
# PLACE COSTS
# --------------------------------------------------

def costs() -> pd.DataFrame:

    query = """
        SELECT
            city AS "City",
            place_name AS "Place_Name",
            entry_fee AS "Entry_Fee",
            currency AS "Currency",
            source AS "Source",
            last_updated AS "Last_Updated",
            verification_status AS "Verification_Status"
        FROM place_costs
        ORDER BY city, place_name
    """

    return _read_table(query)


# --------------------------------------------------
# LOCAL FOOD
# --------------------------------------------------

def foods() -> pd.DataFrame:

    query = """
        SELECT
            city AS "City",
            food_name AS "Food_Name",
            description AS "Description",
            approx_price AS "Approx_Price",
            currency AS "Currency",
            restaurant_name AS "Restaurant_Name",
            restaurant_id AS "Restaurant_ID",
            source AS "Source",
            last_updated AS "Last_Updated",
            verification_status AS "Verification_Status",
            country AS "Country",
            latitude AS "Latitude",
            longitude AS "Longitude"
        FROM local_food
        ORDER BY city, food_name
    """

    return _read_table(query)


# --------------------------------------------------
# DATAFRAME TO API RECORDS
# --------------------------------------------------

def records(df: pd.DataFrame) -> list[dict]:

    if df.empty:
        return []

    clean = df.astype(object).where(
        pd.notna(df),
        None
    )

    return clean.to_dict(orient="records")