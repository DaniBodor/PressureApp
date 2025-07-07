import datetime
import os

import pandas as pd
import requests
from dotenv import load_dotenv
from geopy.distance import geodesic
from geopy.geocoders import Nominatim

load_dotenv()  # Load API key from .env file

TOKEN = os.getenv("KNMI_API_KEY")
API_VERSION = "v1"
COLLECTION = "10-minute-in-situ-meteorological-observations"
BASE_URL = f"https://api.dataplatform.knmi.nl/edr/{API_VERSION}/collections/{COLLECTION}"
HEADERS = {"Authorization": TOKEN}
TIMEOUT = 20  # seconds for before a request times out


def get_pressure(station_id: str) -> tuple[float, str]:
    """Get the air pressure at sea level for the given KNMI weather station (wigos) id.

    Also return the time of the data retrieval as stated in the dataset.
    """
    utc = datetime.timezone.utc
    current_time = datetime.datetime.now(utc)

    # Round down to the last 10-minute timepoint
    # HACK: Due to a delay in saving the data, we are picking up the last measurement from 10 minutes ago.
    # A more elegant solution would be to do a while loop or try/except until it succeeds.
    # TODO: fix this, it can lead to a negative time!
    last_measurement = current_time.replace(minute=((current_time.minute // 10) - 1) * 10, second=0)
    last_measurement = last_measurement.strftime("%Y-%m-%dT%H:%M:%SZ")
    params = {
        "datetime": f"{last_measurement}/{last_measurement}",
        "parameter-name": "pp",
    }

    response = requests.get(
        url=f"{BASE_URL}/locations/{station_id}",
        params=params,
        headers=HEADERS,
        timeout=TIMEOUT,
    )
    response.raise_for_status()
    response = response.json()

    df = pd.json_normalize(response["coverages"])
    pressure_value = df["ranges.pp.values"].iloc[0][0]
    return pressure_value, last_measurement


def get_location(input_city: str) -> tuple[str, float]:
    """Get the nearest KNMI weather station to the given city and the distance to it in km."""
    city_coords = _get_input_coordinates(input_city)
    min_distance = float("inf")
    nearest_station_id = None

    for station_id, station_coords in _get_wigos_station_data().items():
        distance = geodesic(city_coords, station_coords).kilometers
        if distance < min_distance:
            min_distance = distance
            nearest_station_id = station_id
    return nearest_station_id, min_distance


def _get_input_coordinates(city_name: str) -> tuple[float, float]:
    """Get the coordinates (lat, lon) of the given city name in the Netherlands."""
    geolocator = Nominatim(user_agent="knmi_city_lookup")
    location = geolocator.geocode(city_name, featuretype="city")
    if not location:
        msg = f"Could not find coordinates for city: {city_name}"
        raise ValueError(msg)
    location = geolocator.geocode(city_name, country_codes="nl", featuretype="city")
    if not location:
        msg = f"The city of {city_name} is not in the Netherlands."
        raise ValueError(msg)
    return location.longitude, location.latitude


def _get_wigos_station_data() -> dict[str, tuple[float, float]]:
    """Get the WIGOS ID and coordinates for all KNMI weather stations."""
    response = requests.get(
        url=f"{BASE_URL}/locations",
        headers=HEADERS,
        timeout=TIMEOUT,
    )
    response.raise_for_status()
    data = response.json()

    # Flatten the nested JSON structure
    df = pd.json_normalize(data["features"])
    # Create dict from id and coordinates columns
    return dict(zip(df["id"], df["geometry.coordinates"]))
