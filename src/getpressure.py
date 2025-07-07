import datetime

import knmi
from geopy.distance import geodesic
from geopy.geocoders import Nominatim
from knmi.metadata import Station

STATIONS = knmi.stations


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
    return location.latitude, location.longitude


def _get_nearest_station(city_coords: tuple[float, float]) -> tuple[Station, float]:
    min_distance = float("inf")
    nearest_station = None

    for station in STATIONS.values():
        station_coords = (station.latitude, station.longitude)
        distance = geodesic(city_coords, station_coords).kilometers
        if distance < min_distance:
            min_distance = distance
            nearest_station = station

    return nearest_station, min_distance

def get_pressure(station: Station, time: datetime.datetime) -> tuple[float, str]:
    """Get the air pressure at sea level for the given station and time.

    Also return the time of the data retrieval as stated in the dataset.
    """
    # TODO: Use the 10-minute data instead of hourly data.
    return _get_hourly_pressure(station, time)

def _get_hourly_pressure(station: Station, time: datetime.datetime) -> tuple[float, str]:
    """Get the air pressure at sea level for the given station and time using hourly data."""
    # The hourly data is not updated in real time, so at best can pick up from few days ago.
    retrieve_time = time.strftime("%Y%m%d%H")  # format as YYYYMMDDHH
    pressure_df = knmi.get_hour_data_dataframe(
        stations=[station.number],
        start=retrieve_time,
        end=retrieve_time,
        variables=["P"],  # NOTE: in the real time data, the pressure at sea level variable is "pp" instead of "P".
    )
    try:
        return pressure_df["P"].values[0], retrieve_time
    except IndexError as e:
        msg = f"No data available for station {station.name} at {time}."
        raise ValueError(msg) from e

def _get_nearrealtime_pressure(station: Station, time: datetime.datetime) -> tuple[float, str]:
    ...
