# Assignment

Make a Web API in the programming language of your choice. The API should have a single endpoint that you can give the name of a town in The Netherlands as input, and it will return the current air pressure (at sea level) of the closest KNMI Automatic Weather Station, and the distance to that Automatic Weather Station as output. Use the 10-minute-in-situ-meteorological-observations collection of the KDP EDR API (https://developer.dataplatform.knmi.nl/edr-api) and any other publicly available API’s you want. During the interview, we would like to discuss the code, and the choices you've made. Could you upload your solution to the following URLhttps://surfdrive.surf.nl/files/index.php/s/IJq1xfMqbz83LRF, at least one day ahead of the interview:Other means to share the code are also fine.


# Breakdown

#### Make a Web API in the programming language of your choice.

- Python
- OpenAPI

#### Input

The API should have a single endpoint that you can give the name of a town in The Netherlands as input

- Read input
- Error if invalid
  - not recognized
  - not in NL
  - no data

#### Behind the scenes

and it will return the current air pressure (at sea level) of the closest KNMI Automatic Weather Station, and the distance to that Automatic Weather Station as output.

Use the 10-minute-in-situ-meteorological-observations collection of the [KDP EDR API](https://developer.dataplatform.knmi.nl/edr-api) and any other publicly available API’s you want.

- Get current time
  - datetime
- Get closest weather station
  1. pre-existing package; OR
  2. calculate
    - convert to lon/lat coordinates
    - fetch all weather stations coordinates
    - fetch closest (check scipy/numpy)
- Get current air pressure
  - read from [KDP EDR API](https://developer.dataplatform.knmi.nl/edr-api)

#### Output

Display:
- location of weatherstation
- distance to input city
- time of latest measurement
- air pressure


#### Interview:

During the interview, we would like to discuss the code, and the choices you've made. Could you upload your solution to the following URL https://surfdrive.surf.nl/files/index.php/s/IJq1xfMqbz83LRF, at least one day ahead of the interview:Other means to share the code are also fine.
