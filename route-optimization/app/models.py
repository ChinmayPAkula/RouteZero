"""
models.py
---------
Defines and validates the request/response data models for the
route-optimization API.

The request validation prevents malformed or excessively large inputs
from reaching the OR-Tools optimizer.
"""

from pydantic import BaseModel, field_validator


# Maximum number of locations allowed in one optimization request.
# This prevents unbounded solver work and excessive memory usage.
MAX_LOCATIONS = 100


class OptimizeRouteRequest(BaseModel):
    """
    Expected JSON body for POST /optimize-route.

    Example:
    {
        "locations": ["Depot", "A", "B", "C"],
        "distance_matrix": [
            [0, 10, 15, 20],
            [10, 0, 8, 14],
            [15, 8, 0, 9],
            [20, 14, 9, 0]
        ],
        "depot": 0
    }
    """

    locations: list[str]
    distance_matrix: list[list[int]]
    depot: int

    @field_validator("locations")
    @classmethod
    def locations_valid(cls, locations: list[str]) -> list[str]:
        if not locations:
            raise ValueError("locations must not be empty")

        if len(locations) > MAX_LOCATIONS:
            raise ValueError(
                f"locations must contain at most {MAX_LOCATIONS} locations, "
                f"got {len(locations)}"
            )

        return locations

    @field_validator("distance_matrix")
    @classmethod
    def matrix_not_empty(cls, matrix: list[list[int]]) -> list[list[int]]:
        if not matrix:
            raise ValueError("distance_matrix must not be empty")

        return matrix

    @field_validator("distance_matrix", mode="after")
    @classmethod
    def matrix_matches_locations(cls, matrix, info):
        locations = info.data.get("locations")

        # If locations failed validation, skip this check.
        if locations is None:
            return matrix

        n = len(locations)

        if len(matrix) != n:
            raise ValueError(
                f"distance_matrix must have {n} rows "
                f"(one per location), got {len(matrix)}"
            )

        for row_index, row in enumerate(matrix):
            if len(row) != n:
                raise ValueError(
                    f"row {row_index} of distance_matrix has "
                    f"{len(row)} columns, expected {n}"
                )

        return matrix

    @field_validator("distance_matrix", mode="after")
    @classmethod
    def distances_non_negative(cls, matrix: list[list[int]]) -> list[list[int]]:
        for row_index, row in enumerate(matrix):
            for col_index, value in enumerate(row):
                if value < 0:
                    raise ValueError(
                        f"distance_matrix[{row_index}][{col_index}] "
                        f"is negative ({value}); distances must be >= 0"
                    )

        return matrix

    @field_validator("depot")
    @classmethod
    def depot_in_range(cls, depot: int, info) -> int:
        locations = info.data.get("locations")

        if locations is not None and not (0 <= depot < len(locations)):
            raise ValueError(
                f"depot must be a valid index between 0 and "
                f"{len(locations) - 1}, got {depot}"
            )

        return depot


class OptimizeRouteResponse(BaseModel):
    """
    JSON shape returned by POST /optimize-route.
    """

    route: list[str]
    total_distance: int
    unit: str = "km"