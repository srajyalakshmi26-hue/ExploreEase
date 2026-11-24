from pathlib import Path

import pandas as pd
from sqlalchemy import (
    MetaData,
    Table,
    Column,
    Integer,
    String,
    Float,
    Text,
    Numeric,
    Index,
    insert,
    delete,
)

import sys

BACKEND_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BACKEND_ROOT))

from app.db.database import engine


# --------------------------------------------------
# PROJECT PATHS
# --------------------------------------------------

ROOT = Path(__file__).resolve().parents[2]

PLACES_FILE = ROOT / "data" / "processed" / "tourist_places.csv"
RESTAURANTS_FILE = ROOT / "data" / "processed" / "restaurants.csv"
COSTS_FILE = ROOT / "data" / "raw" / "place_costs.csv"
FOOD_FILE = ROOT / "data" / "raw" / "local_food.csv"


# --------------------------------------------------
# DATABASE TABLE DEFINITIONS
# --------------------------------------------------

metadata = MetaData()

tourist_places = Table(
    "tourist_places",
    metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("city", String(120), nullable=False),
    Column("place_name", String(255), nullable=False),
    Column("category", String(120), nullable=False),
    Column("latitude", Float, nullable=False),
    Column("longitude", Float, nullable=False),
    Column("osm_id", String(120), nullable=False),
)

restaurants = Table(
    "restaurants",
    metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("city", String(120), nullable=False),
    Column("restaurant_name", String(255), nullable=False),
    Column("category", String(120), nullable=False),
    Column("cuisine", String(255), nullable=True),
    Column("latitude", Float, nullable=False),
    Column("longitude", Float, nullable=False),
    Column("osm_id", String(120), nullable=False),
)

place_costs = Table(
    "place_costs",
    metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("city", String(120), nullable=False),
    Column("place_name", String(255), nullable=False),
    Column("entry_fee", Numeric(12, 2), nullable=False),
    Column("currency", String(20), nullable=False),
    Column("source", Text, nullable=False),
    Column("last_updated", String(30), nullable=True),
    Column("verification_status", String(100), nullable=True),
)

local_food = Table(
    "local_food",
    metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("city", String(120), nullable=False),
    Column("food_name", String(255), nullable=False),
    Column("description", Text, nullable=True),
    Column("approx_price", Numeric(12, 2), nullable=True),
    Column("currency", String(20), nullable=True),
    Column("restaurant_name", String(255), nullable=True),
    Column("restaurant_id", String(120), nullable=True),
    Column("source", Text, nullable=True),
    Column("last_updated", String(30), nullable=True),
    Column("verification_status", String(100), nullable=True),
    Column("country", String(100), nullable=True),
    Column("latitude", Float, nullable=True),
    Column("longitude", Float, nullable=True),
)


# --------------------------------------------------
# INDEXES
# --------------------------------------------------

Index("idx_places_city", tourist_places.c.city)
Index("idx_places_category", tourist_places.c.category)

Index("idx_restaurants_city", restaurants.c.city)
Index("idx_restaurants_category", restaurants.c.category)

Index("idx_costs_city", place_costs.c.city)
Index("idx_food_city", local_food.c.city)


# --------------------------------------------------
# CSV IMPORT FUNCTION
# --------------------------------------------------

def load_csv(file_path, column_mapping, table):

    if not file_path.exists():
        raise FileNotFoundError(
            f"Dataset not found: {file_path}"
        )

    df = pd.read_csv(file_path)

    df = df.rename(columns=column_mapping)

    expected_columns = [
        column.name
        for column in table.columns
        if column.name != "id"
    ]

    missing_columns = [
        column
        for column in expected_columns
        if column not in df.columns
    ]

    if missing_columns:
        raise ValueError(
            f"Missing columns in {file_path.name}: {missing_columns}"
        )

    df = df[expected_columns]

    # Convert pandas NaN values into Python None.
    df = df.astype(object).where(pd.notna(df), None)

    return df.to_dict(orient="records")


# --------------------------------------------------
# COLUMN MAPPINGS
# --------------------------------------------------

datasets = [
    (
        "Tourist Places",
        PLACES_FILE,
        tourist_places,
        {
            "City": "city",
            "Place_Name": "place_name",
            "Category": "category",
            "Latitude": "latitude",
            "Longitude": "longitude",
            "OSM_ID": "osm_id",
        },
    ),
    (
        "Restaurants",
        RESTAURANTS_FILE,
        restaurants,
        {
            "City": "city",
            "Restaurant_Name": "restaurant_name",
            "Category": "category",
            "Cuisine": "cuisine",
            "Latitude": "latitude",
            "Longitude": "longitude",
            "OSM_ID": "osm_id",
        },
    ),
    (
        "Place Costs",
        COSTS_FILE,
        place_costs,
        {
            "City": "city",
            "Place_Name": "place_name",
            "Entry_Fee": "entry_fee",
            "Currency": "currency",
            "Source": "source",
            "Last_Updated": "last_updated",
            "Verification_Status": "verification_status",
        },
    ),
    (
        "Local Food",
        FOOD_FILE,
        local_food,
        {
            "City": "city",
            "Food_Name": "food_name",
            "Description": "description",
            "Approx_Price": "approx_price",
            "Currency": "currency",
            "Restaurant_Name": "restaurant_name",
            "Restaurant_ID": "restaurant_id",
            "Source": "source",
            "Last_Updated": "last_updated",
            "Verification_Status": "verification_status",
            "Country": "country",
            "Latitude": "latitude",
            "Longitude": "longitude",
        },
    ),
]


# --------------------------------------------------
# DATABASE IMPORT
# --------------------------------------------------

def main():

    print("\nEXPLOREEASE DATABASE IMPORT")
    print("=" * 45)

    prepared_data = []

    # Read and validate all CSVs before modifying the database.
    for name, file_path, table, mapping in datasets:

        records = load_csv(file_path, mapping, table)

        prepared_data.append((name, table, records))

        print(f"{name}: {len(records)} records validated")

    print("\nConnecting to Neon PostgreSQL...")

    # Create tables and import data transactionally.
    with engine.begin() as connection:

        metadata.create_all(connection)

        for name, table, records in prepared_data:

            # Refresh only these four dataset tables.
            connection.execute(delete(table))

            if records:

                for start in range(0, len(records), 1000):

                    batch = records[start:start + 1000]

                    connection.execute(
                        insert(table),
                        batch
                    )

            count = connection.execute(
                table.select().with_only_columns(table.c.id)
            ).fetchall()

            print(f"{name}: {len(count)} records imported")

    print("\n" + "=" * 45)
    print("DATABASE IMPORT COMPLETED SUCCESSFULLY!")
    print("Existing users and saved_places tables preserved.")
    print("=" * 45)


if __name__ == "__main__":
    try:
        main()

    except Exception as error:
        print("\nDATABASE IMPORT FAILED!")
        print("Error:", error)
        raise

    finally:
        engine.dispose()