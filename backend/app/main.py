import sys
from pathlib import Path

# Add sibling module folders to Python's import path
sys.path.append(str(Path(__file__).resolve().parent.parent.parent / "route-optimization"))
sys.path.append(str(Path(__file__).resolve().parent.parent.parent / "carbon-calc"))

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from route_optimization.errors import (
    GeocodingError,
    LocationNotFoundError,
    OptimizationError,
    OutsideTamilNaduError,
    RoutingError,
)
from route_optimization.geocoding import geocode_locations
from route_optimization.models import OptimizeRouteRequest, RouteResult
from route_optimization.optimizer import optimize_route
from route_optimization.routing import get_route_matrices
from route_optimization.main import build_route_result
from carbon_calc.calculator import compare_routes

app = FastAPI(title="RouteZero Backend")


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "healthy"}


def _compute_routes(request: OptimizeRouteRequest):
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

    return normal_route, optimized_route


class PlanRouteRequest(OptimizeRouteRequest):
    vehicle_class: str
    fuel_type: str | None = None


class EmissionsComparison(BaseModel):
    vehicle_type: str
    normal_route: dict
    route_zero: dict
    metrics_comparison: dict


class PlanRouteResponse(BaseModel):
    normal_route: RouteResult
    optimized_route: RouteResult
    emissions: EmissionsComparison


def compute_avg_speed_kmh(route: RouteResult) -> float:
    hours = route.total_duration_minutes / 60
    if hours <= 0:
        return 0.0
    return route.total_distance_km / hours


@app.post("/plan-route", response_model=PlanRouteResponse)
def plan_route(request: PlanRouteRequest) -> PlanRouteResponse:
    normal_route, optimized_route = _compute_routes(request)

    normal_speed = compute_avg_speed_kmh(normal_route)
    optimized_speed = compute_avg_speed_kmh(optimized_route)

    emissions_result = compare_routes(
        normal_km=normal_route.total_distance_km,
        normal_speed_kmh=normal_speed,
        rz_km=optimized_route.total_distance_km,
        rz_speed_kmh=optimized_speed,
        vehicle_class=request.vehicle_class,
        fuel_type=request.fuel_type,
    )

    if "error" in emissions_result:
        raise HTTPException(status_code=400, detail=emissions_result["error"])

    return PlanRouteResponse(
        normal_route=normal_route,
        optimized_route=optimized_route,
        emissions=EmissionsComparison(**emissions_result),
    )