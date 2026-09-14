from fastapi.testclient import TestClient

import app.main as main_module
from app.config import MAX_LOCATIONS
from app.main import app
from app.models import Coordinate


client = TestClient(app)


def test_health():
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}


def test_optimize_route(monkeypatch):
    names = ["Vellore", "Salem", "Chennai"]

    coords = [
        Coordinate(
            name=name,
            latitude=12.0 + index,
            longitude=79.0 + index,
        )
        for index, name in enumerate(names)
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

    monkeypatch.setattr(
        main_module,
        "geocode_locations",
        lambda x: coords,
    )

    monkeypatch.setattr(
        main_module,
        "get_route_matrices",
        lambda x: (distances, durations),
    )

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

    # Both route versions must be present.
    assert "normal_route" in data
    assert "optimized_route" in data

    normal_route = data["normal_route"]
    optimized_route = data["optimized_route"]

    # Normal route must preserve the user's entered order.
    assert normal_route["route"] == names

    # Optimized route must also start at pickup
    # and finish at destination.
    assert optimized_route["route"][0] == "Vellore"
    assert optimized_route["route"][-1] == "Chennai"

    # Every location must be visited exactly once.
    assert sorted(optimized_route["route"]) == sorted(names)

    # Normal route totals.
    assert normal_route["total_distance"] == 30
    assert normal_route["total_duration"] == 300

    # Optimized route totals.
    assert optimized_route["total_distance"] == 30
    assert optimized_route["total_duration"] == 300

    # Values required by carbon-calc comparison.
    assert normal_route["total_distance_km"] == 0.03
    assert normal_route["total_duration_minutes"] == 5.0

    assert optimized_route["total_distance_km"] == 0.03
    assert optimized_route["total_duration_minutes"] == 5.0


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
            "stops": [
                f"Stop {index}"
                for index in range(MAX_LOCATIONS - 1)
            ],
            "destination": "End",
        },
    )

    assert response.status_code == 422