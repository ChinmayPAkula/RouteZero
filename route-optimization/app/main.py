from fastapi import FastAPI, HTTPException

from .errors import (
    GeocodingError,
    LocationNotFoundError,
    OptimizationError,
    OutsideTamilNaduError,
    RoutingError,
)
from .geocoding import geocode_locations
from .models import OptimizeRouteRequest, OptimizeRouteResponse, RouteResult
from .optimizer import calculate_route_totals, optimize_route
from .routing import get_route_matrices


app = FastAPI(
    title="RouteZero Route Optimization API",
    version="1.0.0",
    description=(
        "Tamil Nadu route optimization using Nominatim, OSRM "
        "and Google OR-Tools."
    ),
)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "healthy"}


def build_route_result(
    route_indexes: list[int],
    names: list[str],
    coordinates: list,
    distance_matrix: list[list[int]],
    duration_matrix: list[list[int]],
) -> RouteResult:
    total_distance, total_duration = calculate_route_totals(
        route_indexes,
        distance_matrix,
        duration_matrix,
    )

    ordered_coordinates = [
        coordinates[index]
        for index in route_indexes
    ]

    return RouteResult(
        route=[
            names[index]
            for index in route_indexes
        ],
        coordinates=ordered_coordinates,
        total_distance=total_distance,
        total_duration=total_duration,
        total_distance_km=round(
            total_distance / 1000,
            2,
        ),
        total_duration_minutes=round(
            total_duration / 60,
            1,
        ),
    )


@app.post(
    "/optimize-route",
    response_model=OptimizeRouteResponse,
)
def optimize(
    request: OptimizeRouteRequest,
) -> OptimizeRouteResponse:
    names = [
        request.pickup_location,
        *request.stops,
        request.destination,
    ]

    try:
        # 1. Convert all locations to coordinates.
        coordinates = geocode_locations(names)

        # 2. Build OSRM road distance and duration matrices.
        distance_matrix, duration_matrix = get_route_matrices(
            coordinates
        )

        # 3. Normal route:
        #    Keep the exact order entered by the user.
        normal_route_indexes = list(range(len(names)))

        # 4. Optimized route:
        #    Let OR-Tools reorder only the intermediate stops.
        optimized_route_indexes = optimize_route(
            distance_matrix
        )

        # 5. Build both route results from the same matrices.
        normal_route = build_route_result(
            normal_route_indexes,
            names,
            coordinates,
            distance_matrix,
            duration_matrix,
        )

        optimized_route = build_route_result(
            optimized_route_indexes,
            names,
            coordinates,
            distance_matrix,
            duration_matrix,
        )

    except (
        LocationNotFoundError,
        OutsideTamilNaduError,
    ) as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        ) from exc

    except GeocodingError as exc:
        raise HTTPException(
            status_code=503,
            detail=str(exc),
        ) from exc

    except RoutingError as exc:
        raise HTTPException(
            status_code=502,
            detail=str(exc),
        ) from exc

    except OptimizationError as exc:
        raise HTTPException(
            status_code=500,
            detail=str(exc),
        ) from exc

    return OptimizeRouteResponse(
        normal_route=normal_route,
        optimized_route=optimized_route,
    )
