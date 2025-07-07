import sys
import requests
from datetime import datetime, timezone

api_version = "v1"
collection = "10-minute-in-situ-meteorological-observations"
base_url = f"https://api.dataplatform.knmi.nl/edr/{api_version}/collections/{collection}"
token = "eyJvcmciOiI1ZTU1NGUxOTI3NGE5NjAwMDEyYTNlYjEiLCJpZCI6IjdiYjVkMjVlMjhmMDQ0ZmQ5ZGZiYmFiMDI5YmIzMGU3IiwiaCI6Im11cm11cjEyOCJ9"
headers = {"Authorization": token}


def metadata():
    r = requests.get(base_url, headers=headers)
    r.raise_for_status()
    return r.json()


def locations():
    r = requests.get(f"{base_url}/locations", headers=headers)
    r.raise_for_status()
    return r.json()


def location(location_id, params):
    r = requests.get(f"{base_url}/locations/{location_id}", params=params, headers=headers)
    r.raise_for_status()
    return r.json()


def main():

    current_time = datetime.now(timezone.utc)
    # Round down to the last 10-minute timepoint
    last_measurement = current_time.replace(minute=((current_time.minute // 10)-1) * 10, second=0)
    last_measurement = last_measurement.strftime("%Y-%m-%dT%H:%M:%SZ")
    print(last_measurement)
    params = {
        # "datetime": "2022-07-19T06:00:00Z/2022-07-19T18:00:00Z",
        "datetime": f"{last_measurement}/{last_measurement}",
        "parameter-name": "pp",
    }
    response = location("0-20000-0-06260", params)
    pp_value = response['coverages'][0]['ranges']['pp']['values'][0]
    print(pp_value)


if __name__ == "__main__":
    sys.exit(main())
