# Mini WebAPI to retrieve the current air pressure at a given location in NL

## Usage

### Installation

0. Create and activate a fresh python environment, e.g. using [conda](https://docs.conda.io/projects/conda/en/latest/user-guide/tasks/manage-environments.html#creating-an-environment-with-commands).
1. Clone the current package from GitHub.
2. Install requirements by running:

```bash
pip install -r requirements.txt
```

### Running the WebAPI

0. Request an EDR API key [from KNMI](https://developer.dataplatform.knmi.nl/apis).
1. Rename the `.env.template` file in this repo to `.env` and add your API key.
   - By renaming the file, it will not be tracked.
2. Start the API by running from the repository home folder.

```bash
uvicorn src.pressure_api:app --reload
```

3. Visit http://127.0.0.1:8000/
4. Input a city in The Netherlands to retrieve the air pressure data at sea level for the closest weather station.

### Test in terminal

There are two options to test the script from the terminal rather than from the API. In either case, first follow steps 0 and 1 from above

- For a given manual input, run `python src/run_manual.py`
- To test a pre-determined range of valid and non-valid inputs, run `pytest src/test_local.py`
  - this may take 30-60 seconds to complete

## Assignment

Make a Web API in the programming language of your choice. The API should have a single endpoint that you can give the name of a town in The Netherlands as input, and it will return the current air pressure (at sea level) of the closest KNMI Automatic Weather Station, and the distance to that Automatic Weather Station as output. Use the 10-minute-in-situ-meteorological-observations collection of the [KDP EDR API](https://developer.dataplatform.knmi.nl/edr-api) and any other publicly available API’s you want. During the interview, we would like to discuss the code, and the choices you've made.
