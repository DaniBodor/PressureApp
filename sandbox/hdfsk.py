import requests
from datetime import datetime, timedelta, timezone

# === Configuration ===
API_KEY = "eyJvcmciOiI1ZTU1NGUxOTI3NGE5NjAwMDEyYTNlYjEiLCJpZCI6IjdiYjVkMjVlMjhmMDQ0ZmQ5ZGZiYmFiMDI5YmIzMGU3IiwiaCI6Im11cm11cjEyOCJ9"  # Replace with your real KNMI API key
BASE_URL = "https://api.dataplatform.knmi.nl/edr/v1"
COLLECTION = "10-minute-in-situ-meteorological-observations"

# === Time window: last 30 minutes ===
def valid_datetime_input(timepoint: datetime):
    return timepoint.isoformat(timespec='seconds').replace('+00:00','Z')

now = valid_datetime_input(datetime.now(timezone.utc))
start = valid_datetime_input(now - timedelta(minutes=30))


# === API request ===
params = {
    "bbox": "3.0,50.7,7.3,53.7",  # Covers the Netherlands
    "datetime": f"{start}/{now}",
    "parameter-name": "air_pressure_at_sea_level",
    "crs": "EPSG:4326"
}

headers = {
    "Authorization": API_KEY
}

response = requests.get(
    f"{BASE_URL}/collections/{COLLECTION}/items",
    headers=headers,
    params=params
)

response.raise_for_status()
data = response.json()

# === Print useful info ===
features = data.get("features", [])
if not features:
    print("No data found.")
else:
    print(f"Found {len(features)} measurements for air pressure.\n")
    for f in features:
        station = f.get("id")
        coords = f.get("geometry", {}).get("coordinates", [])
        props = f.get("properties", {})
        time = props.get("datetime")
        pressure = props.get("parameter", {}).get("air_pressure_at_sea_level")
        print(f"Station: {station}")
        print(f"  Time: {time}")
        print(f"  Pressure: {pressure} hPa")
        print(f"  Location (lon, lat): {coords[:2]}")
        print("-" * 30)
