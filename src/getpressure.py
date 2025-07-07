import datetime
import knmi
from geopy.geocoders import Nominatim
from geopy.distance import geodesic
from knmi.metadata import Station

STATIONS = knmi.stations

def get_time():
    current_time = datetime.datetime.now()
    return current_time.strftime("%Y%m%d%H") # formatted as YYYYMMDDHH

def get_location(input_city):
    coordinates = _get_input_coordinates(input_city)
    nearest_station, min_distance = _get_nearest_station(coordinates)
    return nearest_station, min_distance

def get_pressure(station: Station, current_time: str):
    pressure_df = knmi.get_hour_data_dataframe(
        stations=station.number,
        start=current_time,
        end=current_time,
        variables=["P"],
    )
    return pressure_df["P"]


def _get_input_coordinates(city_name):
    geolocator = Nominatim(user_agent="knmi_city_lookup")
    location = geolocator.geocode(city_name, featuretype="city")
    if not location:
        raise ValueError(f"Could not find coordinates for city: {city_name}")
    location = geolocator.geocode(city_name, country_codes="nl", featuretype="city")
    if not location:
        raise ValueError(f"The city of {city_name} is not in the Netherlands.")
    return location.latitude, location.longitude


def _get_nearest_station(city_coords):
    min_distance = float("inf")
    nearest_station = None

    for station in STATIONS.values():
        station_coords = (station.latitude, station.longitude)
        distance = geodesic(city_coords, station_coords).kilometers
        if distance < min_distance:
            min_distance = distance
            nearest_station = station

    return nearest_station, min_distance
