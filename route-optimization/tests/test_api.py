"""
test_api.py
-----------
Tests for the HTTP layer (app/main.py) using FastAPI's TestClient,
which lets us call the endpoints in-process without actually starting
a live uvicorn server.
"""

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)

VALID_PAYLOAD = {
    "locations": ["Depot", "A", "B", "C", "D"],
    "distance_matrix": [
        [0, 10, 15, 20, 12],
        [10, 0, 8, 14, 7],
        [15, 8, 0, 9, 11],
        [20, 14, 9, 0, 6],
        [12, 7, 11, 6, 0],
    ],
    "depot": 0,
}


def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_optimize_route_valid_request():
    response = client.post("/optimize-route", json=VALID_PAYLOAD)
    assert response.status_code == 200

    body = response.json()
    assert body["route"][0] == "Depot"
    assert body["route"][-1] == "Depot"
    assert body["unit"] == "km"
    assert isinstance(body["total_distance"], int)
    assert body["total_distance"] > 0


def test_empty_locations_rejected():
    payload = {"locations": [], "distance_matrix": [], "depot": 0}
    response = client.post("/optimize-route", json=payload)
    assert response.status_code == 422


def test_invalid_matrix_dimensions_rejected():
    payload = {
        "locations": ["Depot", "A", "B"],
        "distance_matrix": [[0, 10], [10, 0, 5], [20, 5, 0]],
        "depot": 0,
    }
    response = client.post("/optimize-route", json=payload)
    assert response.status_code == 422


def test_invalid_depot_rejected():
    payload = {
        "locations": ["Depot", "A", "B"],
        "distance_matrix": [
            [0, 10, 15],
            [10, 0, 8],
            [15, 8, 0],
        ],
        "depot": 9,
    }
    response = client.post("/optimize-route", json=payload)
    assert response.status_code == 422


def test_negative_distance_rejected():
    payload = {
        "locations": ["Depot", "A"],
        "distance_matrix": [[0, -5], [-5, 0]],
        "depot": 0,
    }
    response = client.post("/optimize-route", json=payload)
    assert response.status_code == 422
def test_too_many_locations_rejected():
    locations = [f"Location{i}" for i in range(101)]
    distance_matrix = [[0] * 101 for _ in range(101)]

    response = client.post(
        "/optimize-route",
        json={
            "locations": locations,
            "distance_matrix": distance_matrix,
            "depot": 0,
        },
    )

    assert response.status_code == 422
