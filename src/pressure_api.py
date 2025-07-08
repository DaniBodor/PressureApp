import traceback

from fastapi import FastAPI, Query
from fastapi.responses import HTMLResponse

from src.getdata import get_latest_pressure, get_location

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
    try:
        station_id, min_distance, station_name = get_location(city_name)
        pressure, retrieve_time = get_latest_pressure(station_id, station_name)
        return {
            "target city": city_name,
            "nearest weather station": station_name,
            "nearest weather station id": station_id,
            f"distance (km) from {city_name} to {station_name}": round(min_distance, 1),
            "data retrieved for timepoint (UTC)": retrieve_time.replace("T", " ").replace(":00Z", ""),
            f"pressure (hPa) at sea level for {station_name}": float(pressure),
        }
    except ValueError as e:
        return {"No data retrieved": str(e)}
    except Exception as e:  # noqa: BLE001
        # Log the traceback for debugging purposes
        tb_str = traceback.format_exc()
        return {"error": str(e), "traceback": tb_str}
