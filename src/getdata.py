import datetime
import os

import pandas as pd
import requests
from dotenv import load_dotenv
from geopy.distance import geodesic
from geopy.exc import GeocoderServiceError
from geopy.geocoders import Nominatim

load_dotenv()  # Load API key from .env file

TOKEN = os.getenv("KNMI_API_KEY")
API_VERSION = "v1"
COLLECTION = "10-minute-in-situ-meteorological-observations"
BASE_URL = f"https://api.dataplatform.knmi.nl/edr/{API_VERSION}/collections/{COLLECTION}"
HEADERS = {"Authorization": TOKEN}
TIMEOUT = 20  # seconds for before a request times out

geolocator = Nominatim(user_agent="knmi_city_lookup", timeout=TIMEOUT)


def get_latest_pressure(station_id: str) -> tuple[float, str]:
    """Get the air pressure at sea level for the given KNMI weather station (wigos) id.

    Also return the time of the data retrieval as stated in the dataset.
    """
    utc = datetime.timezone.utc
    now = datetime.datetime.now(utc)
    # Data is acquired in 10 minute intervals and uploaded with a delay of a few minutes.
    # By fetching data from the last 20 minutes, we ensure we get the latest available data.
    older = now - datetime.timedelta(minutes=20)

    params = {
        "datetime": f"{strf(older)}/{strf(now)}",
        "parameter-name": "pp",
    }

    response = requests.get(
        url=f"{BASE_URL}/locations/{station_id}",
        params=params,
        headers=HEADERS,
        timeout=TIMEOUT,
    )
    response.raise_for_status()

    # Extract relevant data from response
    coverage = response.json()["coverages"][0]
    times = coverage["domain"]["axes"]["t"]["values"]
    values = coverage["ranges"]["pp"]["values"]
    df = pd.DataFrame({"time": times, "pressure": values})

    # return the last pressure value and its corresponding time
    return df["pressure"].iloc[-1], df["time"].iloc[-1]


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
    """Get the coordinates (lon, lat) of the given city name in the Netherlands.

    The coordinates are returned flipped from typical convention of (lat, lon) to match how the data is retrieved from
    the collection.
    """
    try:
        msg = f"Could not find coordinates for city: {city_name}"
        location = geolocator.geocode(city_name, featuretype="city")
    except GeocoderServiceError as e:
        raise ValueError(msg) from e
    if not location:
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


def strf(dt: datetime.datetime) -> str:
    """Format a datetime object to a string into format required by API."""
    return dt.strftime("%Y-%m-%dT%H:%M:%SZ")
