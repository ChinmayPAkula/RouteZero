from ortools.constraint_solver import pywrapcp, routing_enums_pb2
from .config import SOLVER_TIME_LIMIT_SECONDS
from .errors import OptimizationError


def optimize_route(distance_matrix: list[list[int]]) -> list[int]:
    """Return node indexes from fixed start (0) to fixed end (n-1)."""
    size = len(distance_matrix)
    if size < 2:
        raise OptimizationError("At least pickup and destination are required")
    if any(len(row) != size for row in distance_matrix):
        raise OptimizationError("Distance matrix must be square")
    if any(value < 0 for row in distance_matrix for value in row):
        raise OptimizationError("Distances cannot be negative")

    manager = pywrapcp.RoutingIndexManager(size, 1, [0], [size - 1])
    routing = pywrapcp.RoutingModel(manager)

    def distance_callback(from_index: int, to_index: int) -> int:
        from_node = manager.IndexToNode(from_index)
        to_node = manager.IndexToNode(to_index)
        return int(distance_matrix[from_node][to_node])

    callback_index = routing.RegisterTransitCallback(distance_callback)
    routing.SetArcCostEvaluatorOfAllVehicles(callback_index)

    search = pywrapcp.DefaultRoutingSearchParameters()
    search.first_solution_strategy = (
        routing_enums_pb2.FirstSolutionStrategy.PATH_CHEAPEST_ARC
    )
    search.local_search_metaheuristic = (
        routing_enums_pb2.LocalSearchMetaheuristic.GUIDED_LOCAL_SEARCH
    )
    search.time_limit.seconds = SOLVER_TIME_LIMIT_SECONDS

    solution = routing.SolveWithParameters(search)
    if solution is None:
        raise OptimizationError("Unable to optimize route")

    route: list[int] = []
    index = routing.Start(0)
    while not routing.IsEnd(index):
        route.append(manager.IndexToNode(index))
        index = solution.Value(routing.NextVar(index))
    route.append(manager.IndexToNode(index))
    return route


def calculate_route_totals(
    route: list[int],
    distance_matrix: list[list[int]],
    duration_matrix: list[list[int]],
) -> tuple[int, int]:
    distance = 0
    duration = 0
    for source, target in zip(route, route[1:]):
        distance += distance_matrix[source][target]
        duration += duration_matrix[source][target]
    return distance, duration
