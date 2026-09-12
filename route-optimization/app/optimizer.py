"""
optimizer.py
------------
The core route-optimization logic for RouteZero.

This file has ONE job: given a list of locations and a distance matrix,
use the OR-Tools routing solver to find an optimized route (minimizing
total distance) that starts at the depot, visits every other location
exactly once, and returns to the depot.

This is the "Traveling Salesman Problem" (a special case of the
Vehicle Routing Problem with only one vehicle). We use Google OR-Tools
to solve it — we do NOT calculate the route by hand.
"""

from ortools.constraint_solver import routing_enums_pb2
from ortools.constraint_solver import pywrapcp


def solve_route(
    locations: list[str],
    distance_matrix: list[list[int]],
    depot: int = 0,
) -> dict:
    """
    Solve the route optimization problem using OR-Tools.

    Parameters
    ----------
    locations : list of location names, e.g. ["Depot", "A", "B", "C", "D"]

    distance_matrix : 2D list where distance_matrix[i][j] is the distance
                       from location i to location j

    depot : the index in `locations` where the route must start and end

    Returns
    -------
    dict with keys:
        "route": list of location names in visiting order
                 (starts and ends at depot)

        "total_distance": total distance of that route
    """

    num_locations = len(locations)

    # 1. Create the Routing Index Manager.
    #    This translates between OR-Tools' internal node numbering and
    #    our own location indices. With 1 vehicle, this is mostly bookkeeping.
    manager = pywrapcp.RoutingIndexManager(
        num_locations,
        1,
        depot,
    )

    # 2. Create the Routing Model.
    #    This is the object that represents the problem to solve.
    routing = pywrapcp.RoutingModel(manager)

    # 3. Create a distance callback.
    #    OR-Tools uses this function to obtain the distance between
    #    any two locations.
    def distance_callback(from_index, to_index):
        from_node = manager.IndexToNode(from_index)
        to_node = manager.IndexToNode(to_index)

        return distance_matrix[from_node][to_node]

    # 4. Register the callback with the routing model.
    transit_callback_index = routing.RegisterTransitCallback(
        distance_callback
    )

    # 5. Tell OR-Tools that the cost of traveling any arc
    #    is the distance between the two locations.
    routing.SetArcCostEvaluatorOfAllVehicles(
        transit_callback_index
    )

    # 6. Configure the search strategy.
    #    PATH_CHEAPEST_ARC builds an initial route by choosing
    #    relatively cheap arcs.
    search_parameters = pywrapcp.DefaultRoutingSearchParameters()

    search_parameters.first_solution_strategy = (
        routing_enums_pb2.FirstSolutionStrategy.PATH_CHEAPEST_ARC
    )

    # Prevent the OR-Tools solver from running indefinitely.
    # This limits CPU time for every optimization request.
    search_parameters.time_limit.seconds = 5

    # 7. Solve the problem.
    solution = routing.SolveWithParameters(search_parameters)

    if solution is None:
        raise ValueError(
            "No solution found for the given locations/distance matrix."
        )

    # 8. Extract the route from the solution.
    route_indices = []

    index = routing.Start(0)

    while not routing.IsEnd(index):
        node = manager.IndexToNode(index)
        route_indices.append(node)

        index = solution.Value(
            routing.NextVar(index)
        )

    # Add the final return to the depot.
    route_indices.append(
        manager.IndexToNode(index)
    )

    # Calculate the total distance directly from the returned route.
    # This guarantees that total_distance matches the actual route,
    # including the final return to the depot.
    total_distance = sum(
        distance_matrix[from_node][to_node]
        for from_node, to_node in zip(
            route_indices,
            route_indices[1:],
        )
    )

    # 9. Convert indices back into location names.
    route_names = [
        locations[i]
        for i in route_indices
    ]

    return {
        "route": route_names,
        "total_distance": total_distance,
    }


if __name__ == "__main__":
    # Quick manual test.
    # Run this file directly with:
    # python app/optimizer.py

    locations = [
        "Depot",
        "A",
        "B",
        "C",
        "D",
    ]

    distance_matrix = [
        [0, 10, 15, 20, 12],
        [10, 0, 8, 14, 7],
        [15, 8, 0, 9, 11],
        [20, 14, 9, 0, 6],
        [12, 7, 11, 6, 0],
    ]

    result = solve_route(
        locations,
        distance_matrix,
        depot=0,
    )

    print(
        "Route:",
        " -> ".join(result["route"]),
    )

    print(
        "Total distance:",
        result["total_distance"],
    )