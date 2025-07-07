import datetime
import knmi
from geopy.geocoders import Nominatim
from geopy.distance import geodesic
from knmi.metadata import Station

STATIONS = knmi.stations


def get_location(input_city):
    coordinates = _get_input_coordinates(input_city)
    nearest_station, min_distance = _get_nearest_station(coordinates)
    return nearest_station, min_distance

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

def get_pressure(station: Station, time: datetime.datetime):
    # TODO: Use the 10-minute data instead of hourly data.
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
    except IndexError:
        raise ValueError(f"No data available for station {station.name} at {time}.")


if __name__ == "__main__":
    # Test the script with a user input
    city_name = input("City in the Netherlands: ")
    now = datetime.datetime.now()
    last_week = now - datetime.timedelta(days=7)

    retrieve_time = last_week

    try:
        nearest_station, min_distance = get_location(city_name)
        print(f"Nearest station to {city_name} is {nearest_station.name} ({nearest_station.number})")
        print(f"Distance: {min_distance:.2f} km")

        pressure = get_pressure(nearest_station, retrieve_time)
        print(f"Air pressure on {retrieve_time.strftime('%Y-%m-%d %H:00')}: {pressure} hPa")
    except ValueError as e:
        print(e)
