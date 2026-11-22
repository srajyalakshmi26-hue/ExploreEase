import pandas as pd


def process_city_data(collected_data):

    if not collected_data:
        return pd.DataFrame()

    df = pd.DataFrame(collected_data)

    # Remove records without names or coordinates
    df = df.dropna(
        subset=["Place_Name", "Latitude", "Longitude"]
    )

    # Remove duplicate place IDs
    df = df.drop_duplicates(subset=["Place_ID"])

    # Remove duplicate place names and coordinates
    df = df.drop_duplicates(
        subset=["Place_Name", "Latitude", "Longitude"]
    )

    # Clean place names
    df["Place_Name"] = df["Place_Name"].str.strip()

    # Remove empty names
    df = df[df["Place_Name"] != ""]

    # Reset row numbering
    df = df.reset_index(drop=True)

    return df