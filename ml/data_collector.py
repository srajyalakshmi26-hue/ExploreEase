
import requests
import os
import json
import hashlib

from datetime import datetime, timedelta
from geopy.geocoders import Nominatim


OVERPASS_URLS = [
    "https://overpass-api.de/api/interpreter",
    "https://overpass.private.coffee/api/interpreter",
    "https://maps.mail.ru/osm/tools/overpass/api/interpreter"
]

geolocator = Nominatim(user_agent="ExploreEase")

CACHE_DIR = os.path.join("data", "cache")
CACHE_DURATION = 24


def get_location_coordinates(location):

    result = geolocator.geocode(location)

    if result is None:
        raise ValueError("Location not found")

    return result.latitude, result.longitude


def get_cache_file(location, radius):

    cache_key = hashlib.md5(
        f"{location.strip().lower()}_{radius}".encode()
    ).hexdigest()

    os.makedirs(CACHE_DIR, exist_ok=True)

    return os.path.join(CACHE_DIR, f"{cache_key}.json")


def get_cached_data(location, radius):

    cache_file = get_cache_file(location, radius)

    if not os.path.exists(cache_file):
        return None

    try:
        with open(cache_file, "r", encoding="utf-8") as file:
            cached = json.load(file)

        saved_time = datetime.fromisoformat(cached["timestamp"])

        if datetime.now() - saved_time < timedelta(hours=CACHE_DURATION):
            return cached["data"]

    except (ValueError, KeyError, OSError, json.JSONDecodeError):
        return None

    return None


def get_stale_cached_data(location, radius):

    cache_file = get_cache_file(location, radius)

    if not os.path.exists(cache_file):
        return None

    try:
        with open(cache_file, "r", encoding="utf-8") as file:
            cached = json.load(file)

        return cached["data"]

    except (ValueError, KeyError, OSError, json.JSONDecodeError):
        return None


def save_cached_data(location, radius, data):

    cache_file = get_cache_file(location, radius)

    cached = {
        "timestamp": datetime.now().isoformat(),
        "data": data
    }

    with open(cache_file, "w", encoding="utf-8") as file:
        json.dump(cached, file, ensure_ascii=False, indent=2)


def collect_city_data(city, radius=15000):

    cached_data = get_cached_data(city, radius)

    if cached_data is not None:
        return cached_data

    latitude, longitude = get_location_coordinates(city)

    query = f"""
    [out:json][timeout:60];

    (
      nwr(around:{radius},{latitude},{longitude})
        ["tourism"~"attraction|museum|gallery|viewpoint|zoo|theme_park"];

      nwr(around:{radius},{latitude},{longitude})
        ["historic"~"monument|castle|archaeological_site"];

      nwr(around:{radius},{latitude},{longitude})
        ["leisure"~"park|garden"];

      nwr(around:{radius},{latitude},{longitude})
        ["amenity"~"restaurant|cafe|fast_food"];
    );

    out center tags;
    """

    result = None
    last_error = None

    for url in OVERPASS_URLS:

        try:
            response = requests.post(
                url,
                data={"data": query},
                headers={
                    "User-Agent": "ExploreEase/1.0"
                },
                timeout=60
            )

            response.raise_for_status()

            result = response.json()

            if result.get("remark"):
                raise RuntimeError(result["remark"])

            break

        except (requests.RequestException, ValueError, RuntimeError) as error:
            last_error = error
            result = None

    if result is None:

        stale_data = get_stale_cached_data(city, radius)

        if stale_data is not None:
            return stale_data

        raise RuntimeError(
            f"All Overpass endpoints failed: {last_error}"
        )

    collected_data = []

    for element in result["elements"]:

        tags = element.get("tags", {})

        if "lat" in element and "lon" in element:
            place_lat = element["lat"]
            place_lon = element["lon"]

        else:
            center = element.get("center", {})
            place_lat = center.get("lat")
            place_lon = center.get("lon")

        if not tags.get("name") or place_lat is None or place_lon is None:
            continue

        category = (
            tags.get("amenity")
            or tags.get("tourism")
            or tags.get("historic")
            or tags.get("leisure")
            or "other"
        )

        collected_data.append({
            "Place_ID": f"{element['type']}_{element['id']}",
            "Place_Name": tags["name"],
            "City": city,
            "Category": category,
            "Latitude": place_lat,
            "Longitude": place_lon,
            "Source": "OpenStreetMap"
        })

    save_cached_data(city, radius, collected_data)

    return collected_data
