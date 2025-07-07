import datetime

from getpressure import get_location, get_pressure

if __name__ == "__main__":
    # Test the script with a user input
    city_name = input("City in the Netherlands: ")
    now = datetime.datetime.now()
    last_week = now - datetime.timedelta(days=7)

    retrieve_time = last_week

    try:
        nearest_station, min_distance = get_location(city_name)
        print(f"Nearest station to {city_name} is at {min_distance:.2f} km distance.")

        pressure = get_pressure(nearest_station, retrieve_time)
        print(f"Air pressure at {pressure[1]}: {pressure[0]} hPa")
    except ValueError as e:
        print(e)
