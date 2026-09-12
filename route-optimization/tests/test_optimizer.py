"""
test_optimizer.py
------------------
Tests for the pure OR-Tools logic in app/optimizer.py — no HTTP involved,
just calling solve_route() directly with Python data.
"""

from app.optimizer import solve_route


LOCATIONS = ["Depot", "A", "B", "C", "D"]
DISTANCE_MATRIX = [
    [0, 10, 15, 20, 12],
    [10, 0, 8, 14, 7],
    [15, 8, 0, 9, 11],
    [20, 14, 9, 0, 6],
    [12, 7, 11, 6, 0],
]


def test_basic_optimizer_returns_result():
    result = solve_route(LOCATIONS, DISTANCE_MATRIX, depot=0)
    assert "route" in result
    assert "total_distance" in result


def test_route_starts_at_depot():
    result = solve_route(LOCATIONS, DISTANCE_MATRIX, depot=0)
    assert result["route"][0] == "Depot"


def test_route_ends_at_depot():
    result = solve_route(LOCATIONS, DISTANCE_MATRIX, depot=0)
    assert result["route"][-1] == "Depot"


def test_every_location_is_visited_exactly_once():
    result = solve_route(LOCATIONS, DISTANCE_MATRIX, depot=0)
    # route includes the depot twice (start and end) — everything else once
    middle_stops = result["route"][1:-1]
    assert sorted(middle_stops) == sorted(LOCATIONS[1:])
    assert len(middle_stops) == len(set(middle_stops))


def test_total_distance_matches_returned_route():
    result = solve_route(LOCATIONS, DISTANCE_MATRIX, depot=0)

    route = result["route"]
    route_indices = [LOCATIONS.index(location) for location in route]

    expected_distance = sum(
        DISTANCE_MATRIX[from_node][to_node]
        for from_node, to_node in zip(route_indices, route_indices[1:])
    )

    assert result["total_distance"] == expected_distance

def test_smaller_four_location_case():
    locations = ["Depot", "A", "B", "C"]
    matrix = [
        [0, 5, 8, 6],
        [5, 0, 4, 7],
        [8, 4, 0, 3],
        [6, 7, 3, 0],
    ]
    result = solve_route(locations, matrix, depot=0)
    assert result["route"][0] == "Depot"
    assert result["route"][-1] == "Depot"
    assert result["total_distance"] > 0
