import sys
from pathlib import Path

# Add sibling module folder to Python's import path
sys.path.append(str(Path(__file__).resolve().parent.parent.parent / "route-optimization"))

from fastapi import FastAPI, HTTPException

from route_optimization.errors import (
    GeocodingError,
    LocationNotFoundError,
    OptimizationError,
    OutsideTamilNaduError,
    RoutingError,
)
from route_optimization.geocoding import geocode_locations
from route_optimization.models import OptimizeRouteRequest, OptimizeRouteResponse
from route_optimization.optimizer import optimize_route
from route_optimization.routing import get_route_matrices
from route_optimization.main import build_route_result

app = FastAPI(title="RouteZero Backend")


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "healthy"}


@app.post("/optimize-route", response_model=OptimizeRouteResponse)
def optimize(request: OptimizeRouteRequest) -> OptimizeRouteResponse:
    names = [request.pickup_location, *request.stops, request.destination]

    try:
        coordinates = geocode_locations(names)
        distance_matrix, duration_matrix = get_route_matrices(coordinates)

        normal_route_indexes = list(range(len(names)))
        optimized_route_indexes = optimize_route(distance_matrix)

        normal_route = build_route_result(
            normal_route_indexes, names, coordinates, distance_matrix, duration_matrix
        )
        optimized_route = build_route_result(
            optimized_route_indexes, names, coordinates, distance_matrix, duration_matrix
        )

    except (LocationNotFoundError, OutsideTamilNaduError) as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except GeocodingError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    except RoutingError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc
    except OptimizationError as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc

    return OptimizeRouteResponse(
        normal_route=normal_route,
        optimized_route=optimized_route,
    )