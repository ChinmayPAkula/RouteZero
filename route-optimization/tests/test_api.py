from fastapi.testclient import TestClient
import app.main as main_module
from app.main import app
from app.models import Coordinate
from app.config import MAX_LOCATIONS

client = TestClient(app)


def test_health():
    assert client.get("/health").json() == {"status": "healthy"}


def test_optimize_route(monkeypatch):
    names = ["Vellore", "Salem", "Chennai"]
    coords = [
        Coordinate(name=n, latitude=12.0 + i, longitude=79.0 + i)
        for i, n in enumerate(names)
    ]
    distances = [
        [0, 10, 100],
        [10, 0, 20],
        [100, 20, 0],
    ]
    durations = [
        [0, 100, 1000],
        [100, 0, 200],
        [1000, 200, 0],
    ]
    monkeypatch.setattr(main_module, "geocode_locations", lambda x: coords)
    monkeypatch.setattr(main_module, "get_route_matrices", lambda x: (distances, durations))

    response = client.post(
        "/optimize-route",
        json={
            "pickup_location": "Vellore",
            "stops": ["Salem"],
            "destination": "Chennai",
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert data["route"] == names
    assert data["total_distance"] == 30
    assert data["total_duration"] == 300


def test_duplicate_location_is_422():
    response = client.post(
        "/optimize-route",
        json={
            "pickup_location": "Vellore",
            "stops": ["Salem", "vellore"],
            "destination": "Chennai",
        },
    )
    assert response.status_code == 422


def test_too_many_locations_is_422():
    response = client.post(
        "/optimize-route",
        json={
            "pickup_location": "Start",
            "stops": [f"Stop {i}" for i in range(MAX_LOCATIONS - 1)],
            "destination": "End",
        },
    )
    assert response.status_code == 422
