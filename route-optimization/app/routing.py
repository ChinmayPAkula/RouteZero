import math

import httpx

from .config import HTTP_TIMEOUT, OSRM_URL, USER_AGENT
from .errors import RoutingError
from .models import Coordinate


def get_route_matrices(
    coordinates: list[Coordinate],
) -> tuple[list[list[int]], list[list[int]]]:
    """
    Request distance and duration matrices from OSRM.

    OSRM returns distances in meters and durations in seconds.
    """

    coordinate_string = ";".join(
        f"{point.longitude},{point.latitude}"
        for point in coordinates
    )

    url = f"{OSRM_URL}/table/v1/driving/{coordinate_string}"

    try:
        response = httpx.get(
            url,
            params={"annotations": "distance,duration"},
            headers={"User-Agent": USER_AGENT},
            timeout=HTTP_TIMEOUT,
        )

        response.raise_for_status()
        payload = response.json()

    except (httpx.HTTPError, ValueError) as exc:
        raise RoutingError(
            "Routing service unavailable"
        ) from exc

    # OSRM must return a JSON object.
    # Prevents errors such as:
    # AttributeError: 'list' object has no attribute 'get'
    if not isinstance(payload, dict):
        raise RoutingError(
            "Invalid routing response"
        )

    if payload.get("code") != "Ok":
        message = payload.get("message")

        if not isinstance(message, str) or not message.strip():
            message = "OSRM could not build a route matrix"

        raise RoutingError(message)

    distances = payload.get("distances")
    durations = payload.get("durations")

    size = len(coordinates)

    # Validate matrix structure before accessing individual cells.
    if (
        not isinstance(distances, list)
        or not isinstance(durations, list)
        or len(distances) != size
        or len(durations) != size
        or any(
            not isinstance(row, list) or len(row) != size
            for row in distances
        )
        or any(
            not isinstance(row, list) or len(row) != size
            for row in durations
        )
    ):
        raise RoutingError(
            "Routing service returned an invalid matrix"
        )

    # Validate every distance and duration value.
    for row in distances:
        for value in row:
            if (
                isinstance(value, bool)
                or not isinstance(value, (int, float))
                or not math.isfinite(value)
            ):
                raise RoutingError(
                    "Routing service returned an invalid distance value"
                )

    for row in durations:
        for value in row:
            if (
                isinstance(value, bool)
                or not isinstance(value, (int, float))
                or not math.isfinite(value)
            ):
                raise RoutingError(
                    "Routing service returned an invalid duration value"
                )

    # OSRM uses null when there is no route between two locations.
    if any(
        value is None
        for row in distances
        for value in row
    ) or any(
        value is None
        for row in durations
        for value in row
    ):
        raise RoutingError(
            "No drivable route exists between one or more locations"
        )

    return (
        [
            [int(round(value)) for value in row]
            for row in distances
        ],
        [
            [int(round(value)) for value in row]
            for row in durations
        ],
    )