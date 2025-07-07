import datetime

import knmi
import pandas as pd
import requests
from geopy.distance import geodesic
from geopy.geocoders import Nominatim
from knmi.metadata import Station

API_VERSION = "v1"
COLLECTION = "10-minute-in-situ-meteorological-observations"
BASE_URL = f"https://api.dataplatform.knmi.nl/edr/{API_VERSION}/collections/{COLLECTION}"
TOKEN = "eyJvcmciOiI1ZTU1NGUxOTI3NGE5NjAwMDEyYTNlYjEiLCJpZCI6IjdiYjVkMjVlMjhmMDQ0ZmQ5ZGZiYmFiMDI5YmIzMGU3IiwiaCI6Im11cm11cjEyOCJ9"  # noqa: S105 E501
HEADERS = {"Authorization": TOKEN}
TIMEOUT = 20  # seconds for requests timeout
REALTIME = False  # Set to False to use hourly data instead of near real-time data

def get_location(input_city: str) -> tuple[Station, float]:
    """Get the nearest KNMI weather station to the given city and the distance to it in km."""
    coordinates = _get_input_coordinates(input_city)
    nearest_station, min_distance = _get_nearest_station(coordinates)
    return nearest_station, min_distance


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


def _get_nearest_station(city_coords: tuple[float, float], wigos: bool = REALTIME) -> tuple[Station, float]:
    min_distance = float("inf")
    nearest_station = None

    if not wigos:
        for station in knmi.stations.values():
            station_coords = (station.longitude, station.latitude)
            distance = geodesic(city_coords, station_coords).kilometers
            if distance < min_distance:
                min_distance = distance
                nearest_station = station.number

    else:
        for station, station_coords in _get_wigos_stations().items():
            distance = geodesic(city_coords, station_coords).kilometers
            if distance < min_distance:
                min_distance = distance
                nearest_station = station

    return nearest_station, min_distance


def _get_wigos_stations() -> dict[str, tuple[float, float]]:
    r = requests.get(f"{BASE_URL}/locations", headers=HEADERS, timeout=TIMEOUT)
    r.raise_for_status()
    data = r.json()

    # Flatten the nested JSON structure
    df = pd.json_normalize(data["features"])
    # Create dict from id and coordinates columns
    return dict(zip(df["id"], df["geometry.coordinates"]))


def get_pressure(station: str, time_point: datetime.datetime, realtime: bool = REALTIME) -> tuple[float, str]:
    """Get the air pressure at sea level for the given station and time.

    Also return the time of the data retrieval as stated in the dataset.
    """
    if realtime:
        return _get_nearrealtime_pressure(station, time_point)
    return _get_hourly_pressure(station, time_point)


def _get_hourly_pressure(station: str, time_point: datetime.datetime) -> tuple[float, str]:
    """Get the air pressure at sea level for the given station and time using hourly data."""
    # The hourly data is not updated in real time, so at best can pick up from few days ago.
    retrieve_time = time_point.strftime("%Y%m%d%H")  # format as YYYYMMDDHH
    pressure_df = knmi.get_hour_data_dataframe(
        stations=[station],
        start=retrieve_time,
        end=retrieve_time,
        variables=["P"],  # NOTE: in the real time data, the pressure at sea level variable is "pp" instead of "P".
    )
    try:
        return pressure_df["P"].to_numpy()[0], retrieve_time
    except IndexError as e:
        msg = f"No data available for station {station.name} at {time_point}."
        raise ValueError(msg) from e


def _get_nearrealtime_pressure(location_id: str, time_point: datetime.datetime) -> tuple[float, str]:
    # Round down to the last 10-minute timepoint
    current_time = datetime.datetime.now(datetime.UTC)

    # HACK: Due to a delay in saving the data, we are picking up the last measurement from 10 minutes ago.
    # A more elegant solution would be to do a while loop or try/except until it succeeds.
    last_measurement = current_time.replace(minute=((current_time.minute // 10) - 1) * 10, second=0)
    last_measurement = last_measurement.strftime("%Y-%m-%dT%H:%M:%SZ")
    params = {
        "datetime": f"{last_measurement}/{last_measurement}",
        "parameter-name": "pp",
    }

    response = requests.get(f"{BASE_URL}/locations/{location_id}", params=params, headers=HEADERS, timeout=TIMEOUT)
    response.raise_for_status()
    response = response.json()

    df = pd.json_normalize(response["coverages"])
    return df["ranges.pp.values"].iloc[0][0], last_measurement
