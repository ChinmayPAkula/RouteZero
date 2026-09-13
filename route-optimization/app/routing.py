import httpx

from .config import HTTP_TIMEOUT, OSRM_URL, USER_AGENT
from .errors import RoutingError
from .models import Coordinate


def get_route_matrices(
    coordinates: list[Coordinate],
) -> tuple[list[list[int]], list[list[int]]]:
    coordinate_string = ";".join(
        f"{point.longitude},{point.latitude}" for point in coordinates
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
        raise RoutingError("Routing service unavailable") from exc

    if payload.get("code") != "Ok":
        raise RoutingError(payload.get("message") or "OSRM could not build a route matrix")

    distances = payload.get("distances")
    durations = payload.get("durations")
    size = len(coordinates)

    if (
        not isinstance(distances, list)
        or not isinstance(durations, list)
        or len(distances) != size
        or len(durations) != size
        or any(not isinstance(row, list) or len(row) != size for row in distances)
        or any(not isinstance(row, list) or len(row) != size for row in durations)
    ):
        raise RoutingError("Routing service returned an invalid matrix")

    if any(value is None for row in distances for value in row) or any(
        value is None for row in durations for value in row
    ):
        raise RoutingError("No drivable route exists between one or more locations")

    return (
        [[int(round(value)) for value in row] for row in distances],
        [[int(round(value)) for value in row] for row in durations],
    )
