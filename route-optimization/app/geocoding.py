import re
import time

import httpx

from .config import (
    HTTP_TIMEOUT,
    NOMINATIM_MIN_INTERVAL_SECONDS,
    NOMINATIM_URL,
    USER_AGENT,
)
from .errors import GeocodingError, LocationNotFoundError, OutsideTamilNaduError
from .models import Coordinate


def _is_tamil_nadu(result: dict) -> bool:
    address = result.get("address") or {}
    state = str(address.get("state", "")).strip().casefold()
    iso = str(address.get("ISO3166-2-lvl4", "")).strip().upper()
    display = str(result.get("display_name", "")).casefold()

    return (
        state == "tamil nadu"
        or iso == "IN-TN"
        or "tamil nadu" in display
    )


def _build_query_variants(name: str) -> list[str]:
    """
    Build multiple Nominatim queries so common local POIs
    such as railway stations can still be found.
    """
    name = name.strip()

    queries = [
        f"{name}, Tamil Nadu, India",
    ]

    # Common railway-station naming difference:
    # "Katpadi Railway Station" -> "Katpadi Junction"
    if re.search(r"\brailway\s+station\b", name, flags=re.IGNORECASE):
        junction_name = re.sub(
            r"\brailway\s+station\b",
            "Junction",
            name,
            flags=re.IGNORECASE,
        )
        queries.append(f"{junction_name}, Tamil Nadu, India")

    # Final broad fallback.
    queries.append(name)

    # Remove duplicates while preserving order.
    return list(dict.fromkeys(queries))


def _search_nominatim(query: str, client: httpx.Client) -> list[dict]:
    try:
        response = client.get(
            f"{NOMINATIM_URL}/search",
            params={
                "q": query,
                "format": "jsonv2",
                "limit": 5,
                "addressdetails": 1,
                "countrycodes": "in",
            },
            headers={"User-Agent": USER_AGENT},
            timeout=HTTP_TIMEOUT,
        )
        response.raise_for_status()

        results = response.json()

    except (httpx.HTTPError, ValueError) as exc:
        raise GeocodingError(
            f"Geocoding service failed for: {query}"
        ) from exc

    if not isinstance(results, list):
        raise GeocodingError(
            f"Invalid geocoding response for: {query}"
        )

    return results


def geocode_location(name: str, client: httpx.Client) -> Coordinate:
    """
    Convert a location name into coordinates.

    Multiple query variants are attempted because local POIs
    can have different names in OpenStreetMap.
    """
    queries = _build_query_variants(name)
    found_results = False

    for index, query in enumerate(queries):
        # Respect the public Nominatim request-rate limit
        # when a fallback query is required.
        if index:
            time.sleep(NOMINATIM_MIN_INTERVAL_SECONDS)

        results = _search_nominatim(query, client)

        if not results:
            continue

        found_results = True

        match = next(
            (item for item in results if _is_tamil_nadu(item)),
            None,
        )

        if match is None:
            continue

        try:
            return Coordinate(
                name=name,
                latitude=float(match["lat"]),
                longitude=float(match["lon"]),
            )
        except (KeyError, TypeError, ValueError) as exc:
            raise GeocodingError(
                f"Invalid geocoding response for: {name}"
            ) from exc

    if found_results:
        raise OutsideTamilNaduError(
            f"Location is not in Tamil Nadu: {name}"
        )

    raise LocationNotFoundError(
        f"Could not geocode location: {name}"
    )


def geocode_locations(names: list[str]) -> list[Coordinate]:
    coordinates: list[Coordinate] = []

    with httpx.Client() as client:
        for index, name in enumerate(names):
            if index:
                # Public Nominatim policy requires low request frequency.
                time.sleep(NOMINATIM_MIN_INTERVAL_SECONDS)

            coordinates.append(
                geocode_location(name, client)
            )

    return coordinates