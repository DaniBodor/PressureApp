import timeit

from getdata import get_latest_pressure, get_location

if __name__ == "__main__":
    # Test the script with a user input
    city_name = input("City in the Netherlands: ")
    start = timeit.default_timer()

    try:
        nearest_station, min_distance = get_location(city_name)
        print(f"Nearest station to {city_name} is at {min_distance:.2f} km distance.")
        time = timeit.default_timer() - start
        print(f"Process complete after {time:.2f} seconds.")

        pressure = get_latest_pressure(nearest_station)
        print(f"Air pressure at {pressure[1]}: {pressure[0]} hPa")
        time = timeit.default_timer() - start
        print(f"Process complete after {time:.2f} seconds.")
    except ValueError as e:
        print(e)
        time = timeit.default_timer() - start
        print(f"Process complete after {time:.2f} seconds.")
    except Exception as e:  # noqa: BLE001
        print(f"An error occurred: {e}")
        time = timeit.default_timer() - start
        print(f"Process complete after {time:.2f} seconds.")
