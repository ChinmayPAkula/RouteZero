from route_optimization.optimizer import calculate_route_totals, optimize_route


def test_fixed_start_end_and_visits_each_stop_once():
    matrix = [
        [0, 10, 1, 50],
        [10, 0, 1, 1],
        [1, 1, 0, 10],
        [50, 1, 10, 0],
    ]
    route = optimize_route(matrix)
    assert route[0] == 0
    assert route[-1] == 3
    assert sorted(route) == [0, 1, 2, 3]
    assert route == [0, 2, 1, 3]


def test_totals_follow_returned_route():
    distance = [[0, 5, 9], [5, 0, 7], [9, 7, 0]]
    duration = [[0, 50, 90], [50, 0, 70], [90, 70, 0]]
    assert calculate_route_totals([0, 1, 2], distance, duration) == (12, 120)
