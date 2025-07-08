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


def get_latest_pressure(station_id: str) -> tuple[float | None, str | None]:
    """Get the air pressure at sea level for the given KNMI weather station (wigos) id.

    Returns a tuple containing the latest pressure value and the time of the data retrieval as stated in the dataset.
    Returns None for both values if no data is available for the station.
    """
    utc = datetime.timezone.utc
    now = datetime.datetime.now(utc)
    # Data is acquired in 10 minute intervals and uploaded with a (non-constant) delay of a few minutes.
    # By fetching data from the last 20 minutes, we ensure we get the latest available data.
    older = now - datetime.timedelta(hours=48)

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
    try:
        response.raise_for_status()
    except requests.HTTPError:
        return None, None

    # Extract relevant data from response
    coverage = response.json()["coverages"][0]
    times = coverage["domain"]["axes"]["t"]["values"]
    values = coverage["ranges"]["pp"]["values"]
    df = pd.DataFrame({"time": times, "pressure": values})

    # return the last pressure value and its corresponding time
    return df["pressure"].iloc[-1], df["time"].iloc[-1]


def get_location(input_city: str) -> tuple[str, float, str]:
    """Find the nearest KNMI weather station to the given city.

    Returns the wigos station id, distance to input city, and the name of the station.
    """
    city_coords = _get_input_coordinates(input_city)
    min_distance = float("inf")

    for _, station in _get_wigos_station_data().iterrows():
        distance = geodesic(city_coords, station["coordinates"]).kilometers
        if distance < min_distance:
            min_distance = distance
            nearest_station_id = station["station_id"]
            station_name = station["station_name"]
    return nearest_station_id, min_distance, station_name


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


def _get_wigos_station_data() -> pd.DataFrame:
    """Get data for weather stations in the collection.

    Returns a dataframe containing the wigos id ("station_id"), coordinates, and name ("station_name") for each station.
    """
    response = requests.get(
        url=f"{BASE_URL}/locations",
        headers=HEADERS,
        timeout=TIMEOUT,
    )
    response.raise_for_status()
    # TODO: Consider looking whether there is a way to filter stations by whether or not they include air pressure data.
    # TODO: How to handle potential error? This should only occur if the API is down or the request times out, which
    # should be rare

    # Get the relevant data from the response
    df = pd.json_normalize(response.json()["features"])
    df = df.rename(
        columns={
            "id": "station_id",
            "geometry.coordinates": "coordinates",
            "properties.name": "station_name",
        }
    )
    return df[["station_id", "coordinates", "station_name"]]


def strf(dt: datetime.datetime) -> str:
    """Format a datetime object to a string into format required by the API."""
    return dt.strftime("%Y-%m-%dT%H:%M:%SZ")
