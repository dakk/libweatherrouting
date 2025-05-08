# libweatherrouting

![CI Status](https://github.com/dakk/libweatherrouting/actions/workflows/ci.yaml/badge.svg)
[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)
![PyPI - Version](https://img.shields.io/pypi/v/weatherrouting)

A 100% python weather routing library for sailing. 

## Reference

An introductory explanation (english, french, spanish and italian translations) of weather routing tools and methods can be find in: https://globalsolochallenge.com/weather-routing/ 

## Install

`pip install weatherrouting`

## Usage

For a comprehensive usage reference example pleace refer to [wind_forecast_routing QGIS plugin](https://github.com/enricofer/wind_forecast_routing/blob/master/wind_forecast_routing_algorithm.py) or [GWeatherRouting standalone application](https://github.com/dakk/gweatherrouting)

Almost one external function has to be implemented as a preliminary requirement for library usage:

### Wind direction and speed for a given location at specified time
A function that accept a datetime item, a float latitude and float longitude as parameters, 
performs a wind forecast analysis for the specified time and location (usually sampling a grib file)
and returns a tuple with true wind direction (`twd`) expressed in degrees and true wind speed (`tws`) expressed in meters per second or `None` if running out of temporal/geographic grib scope.

```python
def get_wind_at(t, lat, lon)
    # wind forecast analysys implementation
    # speed is in m/s, direction in degrees
    ...
    return (twd, tws)
```

### Point validity (Optional)
A function that accept a float latitude and float longitude as parameters, 
performs a test to check if the specified location is eligible as waypoint (i.e. lay or not on sea)
and returns a boolean (True if valid, False if invalid)

```python
def point_validity(lat, lon)
    # 
    ...
    return True/False
```

### Line validity (Optional)
A function that accept a vector defined as four float parameters (latitude1, longitude1, latitude2, longitude2)
performs a test to check whether the specified line between two waypoints is valid (i.e. lays completely or not on sea, or in other words is in line of sight)
and returns a boolean (True if valid, False if invalid)

```python
def line_validity(lat1, lon1, lat1, lon1)
    # 
    ...
    return True/False
```

### Import weatherrouting module

```python
from weatherrouting import Routing, Polar
from weatherrouting.routers.linearbestisorouter import LinearBestIsoRouter
from datetime import datetime
```

### Define a track points list
Define a list of trackpoints as lat,long tuples (almost 2) that have to be reached by the route

```python
track = ((38.1, 5.1), (38.4, 5.2), (38.2, 5.7))
```

### Define a polar wrapper
Define the polar object from a [polar file]( https://www.seapilot.com/features/polars/ ) describing the performance of the boat at different wind speeds (`tws`) and different angles (`twd`)

```python
polar_obj = Polar("polar_files/bavaria38.pol")
```

### Define the start datetime
Define the polar object from a [polar file]( https://www.seapilot.com/features/polars/ ) describing the performance of the boat at different wind speeds (`tws`) and different angles (`twd~)

```python
start = datetime.fromisoformat('2021-04-02T12:00:00')
```

### Define routing object 

```python
routing_obj = Routing(
    LinearBestIsoRouter,            # specify a router type
    polar_obj,                      # the polar object for a specific sail boat
    track,                          # the list of track points (lat,lon)
    get_wind_at,                      # the function that returns (twd,tws) for a specified (datetime, lat, lon)
    start,                          # the start datetime
    start_position = (37.8, 4.8)    # the start location (lat lon, optional, the first track point if undefined)
    point_validity = point_validity  # the point validity function (optional)
    line_validity = line_validity    # the line validity function (optional)
)
```

### Perform route calculation
Calculate subsequent steps until the end track point is reached

```python
while not self.routing_obj.end:
    res = self.routing_obj.step() # default step duration is set to 1 hour

# you can call a step with custom timedelta (in hour) at anytime
while not self.routing_obj.end:
    res = self.routing_obj.step(timedelta=0.25) # 15min time delta
```
the step method returns a RoutingResult object with the following informations during routing calculation:
```python
res.time         # the datetime of step  
res.isochrones   # all points reached at a specified datetime
res.progress     # the calculation progress 
```
and after the end of the routing calculation contains a list of tuple containing the waypoints informations (lat,lon,datetime, twd, tws, speed, heading)
```python
res.path         # the list of route waypoints
```

### Export path as geojson
The path could be exported as a geojson object for cartographic representation
```python
from weatherrouting.utils import path_as_geojson
import json

json.dumps(path_as_geojson(res.path))
```



## License

Read the LICENSE file.

## Credits

This work is partially based and inspired by Riccardo Apolloni
[Virtual Sailing Simulator](https://web.archive.org/web/20180324153950/https://riccardoapolloni.altervista.org/).
