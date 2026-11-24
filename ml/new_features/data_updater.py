
import time
from datetime import datetime, timezone

from ml.data_collector import collect_city_data
from ml.data_processor import process_city_data


def update_location_data(location, radius=15000):

    try:
        collected_data = None

        for attempt in range(3):
            try:
                collected_data = collect_city_data(
                    location,
                    radius=radius
                )
                break

            except Exception as error:
                status_code = getattr(
                    getattr(error, "response", None),
                    "status_code",
                    None
                )

                if status_code not in (502, 503, 504) or attempt == 2:
                    raise

                time.sleep(2 * (attempt + 1))

        processed_data = process_city_data(collected_data)

        if processed_data.empty:
            return {
                "Status": "No data available",
                "Location": location,
                "Record_Count": 0,
                "Places": processed_data
            }

        updated_time = datetime.now(timezone.utc).isoformat()

        processed_data["Last_Updated"] = updated_time
        processed_data["Data_Source"] = "OpenStreetMap"

        return {
            "Status": "Updated successfully",
            "Location": location,
            "Record_Count": len(processed_data),
            "Last_Updated": updated_time,
            "Places": processed_data
        }

    except Exception as error:
        return {
            "Status": "Update failed",
            "Location": location,
            "Error": str(error)
        }


def get_update_summary(update_result):

    if update_result["Status"] != "Updated successfully":
        return update_result

    return {
        "Location": update_result["Location"],
        "Status": update_result["Status"],
        "Record_Count": update_result["Record_Count"],
        "Last_Updated": update_result["Last_Updated"],
        "Data_Source": "OpenStreetMap"
    }
