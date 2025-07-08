import timeit

import pytest

from src.getdata import get_latest_pressure, get_location


def run_locally(city_name: str) -> tuple[float, float, str]:
    """Run the get_location and get_latest_pressure functions locally."""
    station_id, min_distance, station_name = get_location(city_name)
    pressure, _timepoint = get_latest_pressure(station_id, station_name)
    return min_distance, pressure


def test_valid_inputs() -> None:
    test_start = timeit.default_timer()
    valid_cities = [
        "Amsterdam",
        "amsterdam",  # case insensitivity
        "  amsterdam  ",  # leading/trailing spaces
        "den Haag",  # other city, odd capitalization
        "'s Gravenhage",  # special character in name
        "s gravenhage",  # ommission of apostrophe
        "saba",  # non-mainland Netherlands
        "Άμστερνταμ",  # Greek script
        "אמסטרדם",  # Hebrew (right-to-left) script
    ]
    for city in valid_cities:
        print(f"Testing city: {city}", end="")
        min_distance, pressure = run_locally(city)
        assert min_distance < 100, f"{city} is not within 100 km of a weather station."
        assert 800 < pressure < 1200, f"Pressure for {city} must be within 800 - 1200 hPa range."
        elapsed = timeit.default_timer() - test_start
        print(f" - Complete after {elapsed:.2f} seconds.")


def test_invalid_inputs() -> None:
    test_start = timeit.default_timer()
    non_existing_cities = [
        "InvalidCityName123",
        "",
        "jksdfkgd",
        "478765",
        "!!!",
        " ",
    ]
    for city in non_existing_cities:
        print(f"Testing city: {city}", end="")
        with pytest.raises(ValueError, match="Could not find coordinates for city"):
            _, _ = run_locally(city)
        elapsed = timeit.default_timer() - test_start
        print(f" - Complete after {elapsed:.2f} seconds.")


def test_foreign() -> None:
    test_start = timeit.default_timer()
    foreign_cities = [
        "Berlin",
        "תל אביב",  # Tel Aviv
        "北京",  # Beijing
    ]
    for city in foreign_cities:
        print(f"Testing city: {city}", end="")
        with pytest.raises(ValueError, match="not in the Netherlands"):
            _, _ = run_locally(city)
        elapsed = timeit.default_timer() - test_start
        print(f" - Complete after {elapsed:.2f} seconds.")


def test_no_data() -> None:
    """Test that the function raises an error when no data is available."""
    test_start = timeit.default_timer()
    no_data_cities = ["Kalenberg", "Nederland", "Meppel"]
    # TODO: It's unclear whether these cities will never have data, but at time of writing, they do not.
    for city in no_data_cities:
        with pytest.raises(ValueError, match="No data found for station"):
            _, _ = run_locally(city)
        elapsed = timeit.default_timer() - test_start
        print(f" - Complete after {elapsed:.2f} seconds.")
