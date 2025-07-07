import datetime
import traceback

from fastapi import FastAPI, Query
from fastapi.responses import HTMLResponse

from .getpressure import get_location, get_pressure

app = FastAPI()


@app.get("/", response_class=HTMLResponse)
def index() -> str:
    """Render the main page with a form to input a city name."""
    return """
    <html>
        <body>
            <h2>City in the Netherlands:</h2>
            <form action="/pressure">
                <input type="text" name="city_name" />
                <input type="submit" value="Submit" />
            </form>
        </body>
    </html>
    """


@app.get("/pressure")
def pressure_endpoint(city_name: str = Query(..., description="City in The Netherlands")) -> dict:
    """Return the air pressure at sea level for the nearest KNMI weather station to the given city."""
    now = datetime.datetime.now()
    lastweek = now - datetime.timedelta(days=7)

    data_time = lastweek
    try:
        nearest_station, min_distance = get_location(city_name)
        pressure, retrieve_time = get_pressure(nearest_station, data_time)
        return {
            "city": city_name,
            # "nearest_station": nearest_station.name,
            # "station_number": nearest_station.number,
            "distance (km) to nearest weather station": round(min_distance, 1),
            "data retrieved for timepoint": retrieve_time,
            "pressure (hPa) at sea level": float(pressure),
        }
    except ValueError as ve:
        return {"No data retrieved": str(ve)}
    except Exception as e:  # noqa: BLE001
        # Log the traceback for debugging purposes
        tb_str = traceback.format_exc()
        return {"error": str(e), "traceback": tb_str}
