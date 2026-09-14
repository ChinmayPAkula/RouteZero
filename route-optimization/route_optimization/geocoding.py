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
    """Return True only when the Nominatim result belongs to Tamil Nadu."""
    address = result.get("address")

    if address is None:
        address = {}

    if not isinstance(address, dict):
        return False

    state = str(address.get("state", "")).strip().casefold()
    iso = str(address.get("ISO3166-2-lvl4", "")).strip().upper()
    display = str(result.get("display_name", "")).casefold()

    # Structured address fields take precedence over display_name.
    if state or iso:
        return (
            (not state or state == "tamil nadu")
            and (not iso or iso == "IN-TN")
        )

    # Use display_name only when structured fields are unavailable.
    return "tamil nadu" in display


def _build_query_variants(name: str) -> list[str]:
    """
    Build multiple Nominatim queries.

    This helps with local places that may have different names in
    OpenStreetMap, for example:
        Katpadi Railway Station
        Katpadi Junction
    """
    name = name.strip()

    queries = [
        f"{name}, Tamil Nadu, India",
    ]

    # Handle common railway station naming differences.
    if re.search(r"\brailway\s+station\b", name, flags=re.IGNORECASE):
        junction_name = re.sub(
            r"\brailway\s+station\b",
            "Junction",
            name,
            flags=re.IGNORECASE,
        )

        queries.append(
            f"{junction_name}, Tamil Nadu, India"
        )

    # Final broad fallback.
    queries.append(name)

    # Remove duplicates while preserving order.
    return list(dict.fromkeys(queries))


def _search_nominatim(
    query: str,
    client: httpx.Client,
) -> list[dict]:
    """Search Nominatim and validate the response structure."""
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
            headers={
                "User-Agent": USER_AGENT,
            },
            timeout=HTTP_TIMEOUT,
        )

        response.raise_for_status()
        results = response.json()

    except (httpx.HTTPError, ValueError) as exc:
        raise GeocodingError(
            f"Geocoding service failed for: {query}"
        ) from exc

    # The API must return a JSON list.
    if not isinstance(results, list):
        raise GeocodingError(
            f"Invalid geocoding response for: {query}"
        )

    # Validate every result before using it.
    for result in results:
        if not isinstance(result, dict):
            raise GeocodingError(
                f"Invalid geocoding result for: {query}"
            )

        address = result.get("address")

        if address is not None and not isinstance(address, dict):
            raise GeocodingError(
                f"Invalid address data for: {query}"
            )

    return results


def geocode_location(
    name: str,
    client: httpx.Client,
) -> Coordinate:
    """
    Convert a location name into latitude/longitude.

    Multiple queries are attempted because local POIs can have
    different names in OpenStreetMap.
    """
    queries = _build_query_variants(name)
    found_results = False

    for index, query in enumerate(queries):

        # Respect Nominatim's public request-rate limit
        # when a fallback query is required.
        if index:
            time.sleep(NOMINATIM_MIN_INTERVAL_SECONDS)

        results = _search_nominatim(query, client)

        if not results:
            continue

        found_results = True

        # Only accept a result that is actually in Tamil Nadu.
        match = next(
            (
                result
                for result in results
                if _is_tamil_nadu(result)
            ),
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
                f"Invalid geocoding coordinates for: {name}"
            ) from exc

    if found_results:
        raise OutsideTamilNaduError(
            f"Location is not in Tamil Nadu: {name}"
        )

    raise LocationNotFoundError(
        f"Could not geocode location: {name}"
    )


def geocode_locations(
    names: list[str],
) -> list[Coordinate]:
    """Geocode multiple locations while respecting Nominatim rate limits."""
    coordinates: list[Coordinate] = []

    with httpx.Client() as client:

        for index, name in enumerate(names):

            # Keep requests to the public Nominatim service
            # at a safe rate.
            if index:
                time.sleep(
                    NOMINATIM_MIN_INTERVAL_SECONDS
                )

            coordinates.append(
                geocode_location(name, client)
            )

    return coordinates