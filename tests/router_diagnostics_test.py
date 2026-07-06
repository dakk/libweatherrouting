import datetime
import os

import weatherrouting
from weatherrouting.routers.linearbestisorouter import LinearBestIsoRouter

from .mock_grib import MockGrib

polar_bavaria38 = weatherrouting.Polar(
        os.path.join(os.path.dirname(__file__), "data/bavaria38.pol")
)

def test_routing_result_contain_diagnostics():
    track = [(1, 1), (1.5, 1.5)]

    routing_obj = weatherrouting.Routing(
        LinearBestIsoRouter,
        polar_bavaria38,
        track,
        MockGrib(10, 10, 0),
        datetime.datetime.fromisoformat("2026-01-01T12:00:00")
    )

    res = routing_obj.step()

    assert isinstance(res.diagnostics, dict)
    assert "parents" in res.diagnostics
    assert "generated" in res.diagnostics
    assert "before_pruning" in res.diagnostics
    assert "after_pruning" in res.diagnostics
    assert "frontier_size" in res.diagnostics

    assert res.diagnostics["parents"] >= 1
    assert res.diagnostics["generated"] >= 0
    assert res.diagnostics["before_pruning"] >= res.diagnostics["after_pruning"]

def test_point_validity_rejections_are_reported():
    def reject_all_points(lat, lon):
        return False

    track = [(1, 1), (1.5, 1.5)]

    routing_obj = weatherrouting.Routing(
        LinearBestIsoRouter,
        polar_bavaria38,
        track,
        MockGrib(10, 10, 0),
        datetime.datetime.fromisoformat("2026-01-01T12:00:00"),
        point_validity=reject_all_points,
    )

    res = routing_obj.step()

    assert res.diagnostics["after_pruning"] > 0
    assert res.diagnostics["rejected_point_validity"] == res.diagnostics["after_pruning"]
    assert res.diagnostics["frontier_size"] == 0
