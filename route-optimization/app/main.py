from fastapi import FastAPI, HTTPException

from .errors import (
    GeocodingError,
    LocationNotFoundError,
    OptimizationError,
    OutsideTamilNaduError,
    RoutingError,
)
from .geocoding import geocode_locations
from .models import OptimizeRouteRequest, OptimizeRouteResponse
from .optimizer import calculate_route_totals, optimize_route
from .routing import get_route_matrices

app = FastAPI(
    title="RouteZero Route Optimization API",
    version="1.0.0",
    description="Tamil Nadu route optimization using Nominatim, OSRM and Google OR-Tools.",
)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "healthy"}


@app.post("/optimize-route", response_model=OptimizeRouteResponse)
def optimize(request: OptimizeRouteRequest) -> OptimizeRouteResponse:
    names = [request.pickup_location, *request.stops, request.destination]

    try:
        coordinates = geocode_locations(names)
        distance_matrix, duration_matrix = get_route_matrices(coordinates)
        route_indexes = optimize_route(distance_matrix)
        total_distance, total_duration = calculate_route_totals(
            route_indexes, distance_matrix, duration_matrix
        )
    except (LocationNotFoundError, OutsideTamilNaduError) as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except GeocodingError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    except RoutingError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc
    except OptimizationError as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc

    ordered_coordinates = [coordinates[i] for i in route_indexes]
    return OptimizeRouteResponse(
        route=[names[i] for i in route_indexes],
        coordinates=ordered_coordinates,
        total_distance=total_distance,
        total_duration=total_duration,
        total_distance_km=round(total_distance / 1000, 2),
        total_duration_minutes=round(total_duration / 60, 1),
    )
