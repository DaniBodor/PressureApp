from fastapi import FastAPI, Query, HTTPException
from fastapi.responses import HTMLResponse
import datetime
from .getpressure import get_pressure, get_location
app = FastAPI()


@app.get("/", response_class=HTMLResponse)
def index():
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
def pressure_endpoint(city_name: str = Query(..., description="City in The Netherlands")):
    now = datetime.datetime.now()
    lastweek = now - datetime.timedelta(days=7)

    data_time = lastweek
    try:
        nearest_station, min_distance = get_location(city_name)
        pressure, retrieve_time = get_pressure(nearest_station, data_time)
        if pressure is None:
            raise HTTPException(status_code=404, detail=f"No data for city: {city_name}")
        return {
            "city": city_name,
            "nearest_station": nearest_station.name,
            "station_number": nearest_station.number,
            f"distance (km) to {city_name}": round(min_distance, 1),
            "data retrieved for": retrieve_time,
            "pressure (hPa) at sea level": int(pressure)
        }
    except ValueError as ve:
        return {"No data retrieved": str(ve)}
    except Exception as e:
        import traceback
        tb_str = traceback.format_exc()
        return {
            "error": str(e),
            "traceback": tb_str
        }
