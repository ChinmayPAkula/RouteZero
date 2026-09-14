import httpx
import pytest

from app.errors import RoutingError
from app.models import Coordinate
import app.routing as routing


POINTS = [
    Coordinate(name="A", latitude=12.0, longitude=79.0),
    Coordinate(name="B", latitude=13.0, longitude=80.0),
]


def test_osrm_matrices(monkeypatch):
    def fake_get(*args, **kwargs):
        return httpx.Response(
            200,
            json={
                "code": "Ok",
                "distances": [[0, 1000.4], [1001.2, 0]],
                "durations": [[0, 120.2], [121.1, 0]],
            },
            request=httpx.Request("GET", "https://example.test"),
        )
    monkeypatch.setattr(routing.httpx, "get", fake_get)
    distances, durations = routing.get_route_matrices(POINTS)
    assert distances == [[0, 1000], [1001, 0]]
    assert durations == [[0, 120], [121, 0]]


def test_osrm_null_route_rejected(monkeypatch):
    def fake_get(*args, **kwargs):
        return httpx.Response(
            200,
            json={
                "code": "Ok",
                "distances": [[0, None], [None, 0]],
                "durations": [[0, None], [None, 0]],
            },
            request=httpx.Request("GET", "https://example.test"),
        )
    monkeypatch.setattr(routing.httpx, "get", fake_get)
    with pytest.raises(RoutingError):
        routing.get_route_matrices(POINTS)
