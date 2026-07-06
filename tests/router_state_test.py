import datetime

from weatherrouting.routers.router import RoutingResult
from weatherrouting.routers.linearbestisorouter import LinearBestIsoRouter
from .mock_grib import MockGrib

def test_routing_result_defaults_are_not_shared():
    t = datetime.datetime.fromisoformat("2026-01-01T12:00:00")

    r1 = RoutingResult(time=t)
    r2 = RoutingResult(time=t)

    r1.path.append("x")
    r1.isochrones.append(["iso"])

    assert r2.path == []
    assert r2.isochrones == []

def test_router_params_are_instance_local():
    grib = MockGrib(10, 10, 0)

    r1 = LinearBestIsoRouter(None, grib)
    r2 = LinearBestIsoRouter(None, grib)

    r1.set_param_value("subdiv", 5)

    assert r1.get_param_value("subdiv") == 5
    assert r2.get_param_value("subdiv") == 1
