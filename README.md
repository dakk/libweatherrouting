# libweatherrouting

[![Build Status](https://travis-ci.com/dakk/libweatherrouting.svg?branch=master)](https://travis-ci.com/dakk/libweatherrouting.svg?branch=master)
[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)

A 100% python weather routing library for sailing


## License

Read the LICENSE file.

## Install

`pip install git+https://github.com/dakk/libweatherrouting.git`

## Usage

For a comprehensive usage reference example pleace refer to [wind_forecast_routing QGIS plugin](https://github.com/enricofer/wind_forecast_routing/blob/master/wind_forecast_routing_algorithm.py) or [GWeatherRouting standalone application](https://github.com/dakk/gweatherrouting)

Almost one external function has to be implemented as a preliminary requirement for library usage:

### Wind direction and speed for a given location at specified time
A function that accept a datetime item, a float latitude and float longitude as parameters, 
performs a wind forecast analysis for the specified time and location (usually sampling a grib file)
and returns a tuple with true wind direction (`twd`) expressed in radians and true wind speed (`tws`) expressed in meters per second

```
def getWindAt( t, lat, lon)
    # wind forecast analysys implementation
    ...
    return (twd, tws)
```

### Point validity (Optional)
A function that accept a float latitude and float longitude as parameters, 
performs a test to check if the specified location is eligible as waypoint (i.e. lay or not on sea)
and returns a boolean (True if valid, False if invalid)

```
def point_validity(lat, lon)
    # 
    ...
    return True/False
```

### Line validity (Optional)
A function that accept a vector defined as four float parameters (latitude1, longitude1, latitude2, longitude2)
performs a test to check whether the specified line between two waypoints is valid (i.e. lays completely or not on sea, or in other words is in line of sight)
and returns a boolean (True if valid, False if invalid)

```
def line_validity(lat1, lon1, lat1, lon1)
    # 
    ...
    return True/False
```

### import weatherrouting module

```
from weatherrouting import Routing, Polar
from weatherrouting.routers.linearbestisorouter import LinearBestIsoRouter
from datetime import datetime
```

### Define a track points list
Define a list of trackpoints as lat,long tuples (almost 2) that have to be reached by route

```
track = ((5.1, 38.1), (5.2, 38.4), (5.7, 38.2))
```

### Define a polar wrapper
Define the polar object from a [polar file]( https://www.seapilot.com/features/polars/ ) describing the performance of the boat at different wind speeds (`tws`) and different angles (`twd`)

```
polar_obj = Polar("polar_files/bavaria38.pol")
```

### Define the start datetime
Define the polar object from a [polar file]( https://www.seapilot.com/features/polars/ ) describing the performance of the boat at different wind speeds (`tws`) and different angles (`twd~)

```
start = datetime.fromisoformat('2021-04-02T12:00:00')
```

### Define routing object 

```
routing_obj = Routing(
    LinearBestIsoRouter,            # specify a router type
    polar_obj,                      # the polar object for a specific sail boat
    track,                          # the list of track points (lat,lon)
    getWindAt,                      # the function that returns (twd,tws) for a specified (datetime, lat, lon)
    start,                          # the start datetime
    start_position = (4.8,37.8)     # the start location (optional, the first track point if undefined)
    pointValidity = point_validity  # the point validity function (optional)
    lineValidity = line_validity    # the line validity function (optional)
)
```

### Perform route calculation
Calculate subsequent steps until the end track point is reached

```
while not self.routing_obj.end:
    res = self.routing_obj.step()

```
the step method returns a RoutingResult object with the following informations during routing calculation:
```
res.time         # the datetime of step  
res.isochrones   # all points reached at a specified datetime
res.progress     # the calculation progress
res.path         # when the end track point is reached contains the route path
res.position    
```
and after the end of the routing calculation contains a list of tuple containing the waypoints informations (lat,lon,datetime, twd, tws, speed, heading)
```
res.path         # the list of route waypoints
```

### Export path as geojson
The path could be exported as a geojson object for cartographic representation
```
from weatherrouting.utils import pathAsGeojson
import json

json.dumps(pathAsGeojson(res.path))
```
