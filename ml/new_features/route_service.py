
import requests


OSRM_URL = "https://router.project-osrm.org/route/v1/driving"


def get_route(start_latitude, start_longitude,
              end_latitude, end_longitude):

    try:
        coordinates = [
            start_latitude,
            start_longitude,
            end_latitude,
            end_longitude
        ]

        if not all(-90 <= value <= 90 for value in
                   [start_latitude, end_latitude]):
            raise ValueError("Invalid latitude")

        if not all(-180 <= value <= 180 for value in
                   [start_longitude, end_longitude]):
            raise ValueError("Invalid longitude")

        route_coordinates = (
            f"{start_longitude},{start_latitude};"
            f"{end_longitude},{end_latitude}"
        )

        response = requests.get(
            f"{OSRM_URL}/{route_coordinates}",
            params={
                "overview": "full",
                "geometries": "geojson"
            },
            timeout=20
        )

        response.raise_for_status()
        result = response.json()

        if result.get("code") != "Ok" or not result.get("routes"):
            return {
                "Status": "Route unavailable"
            }

        route = result["routes"][0]

        return {
            "Status": "Success",
            "Distance_KM": round(route["distance"] / 1000, 2),
            "Duration_Minutes": round(route["duration"] / 60, 2),
            "Route_Geometry": route["geometry"]
        }

    except requests.RequestException as error:
        return {
            "Status": "API request failed",
            "Error": str(error)
        }

    except (ValueError, TypeError, KeyError) as error:
        return {
            "Status": "Invalid route data",
            "Error": str(error)
        }
