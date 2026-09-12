"""
models.py
---------
Defines the shape of data coming INTO the API (the request), and validates
it before it's allowed anywhere near the OR-Tools optimizer.

We use Pydantic's `BaseModel` + `field_validator` to describe the fields
we expect and write small functions that check them.
"""

from pydantic import BaseModel, field_validator


class OptimizeRouteRequest(BaseModel):
    """
    The expected JSON body for POST /optimize-route.

    Example:
    {
        "locations": ["Depot", "A", "B", "C", "D"],
        "distance_matrix": [[0, 10, 15, 20, 12], ...],
        "depot": 0
    }
    """

    locations: list[str]
    distance_matrix: list[list[int]]
    depot: int

    # ----------------------------------------------------------------
    # VALIDATORS
    # Each one runs automatically whenever a request is parsed.
    # If a validator raises ValueError, FastAPI turns it into a clean
    # HTTP 422 response — the exception never reaches our own code.
    # ----------------------------------------------------------------

    @field_validator("locations")
    @classmethod
    def locations_not_empty(cls, locations: list[str]) -> list[str]:
        if len(locations) == 0:
            raise ValueError("locations must not be empty")
        return locations

    @field_validator("distance_matrix")
    @classmethod
    def matrix_not_empty(cls, matrix: list[list[int]]) -> list[list[int]]:
        if len(matrix) == 0:
            raise ValueError("distance_matrix must not be empty")
        return matrix

    # This validator needs to compare distance_matrix against locations,
    # so it runs AFTER both fields are parsed (mode="after" gives it
    # access to `self`, i.e. the whole partially-built model).
    @field_validator("distance_matrix", mode="after")
    @classmethod
    def matrix_matches_locations(cls, matrix, info):
        locations = info.data.get("locations")
        if locations is None:
            # locations itself already failed validation; skip this check
            return matrix

        n = len(locations)

        if len(matrix) != n:
            raise ValueError(
                f"distance_matrix must have {n} rows (one per location), got {len(matrix)}"
            )

        for row_index, row in enumerate(matrix):
            if len(row) != n:
                raise ValueError(
                    f"row {row_index} of distance_matrix has {len(row)} columns, expected {n}"
                )

        return matrix

    @field_validator("distance_matrix", mode="after")
    @classmethod
    def distances_non_negative(cls, matrix: list[list[int]]) -> list[list[int]]:
        for row_index, row in enumerate(matrix):
            for col_index, value in enumerate(row):
                if value < 0:
                    raise ValueError(
                        f"distance_matrix[{row_index}][{col_index}] is negative ({value}); "
                        "distances must be >= 0"
                    )
        return matrix

    @field_validator("depot")
    @classmethod
    def depot_in_range(cls, depot: int, info) -> int:
        locations = info.data.get("locations")
        if locations is not None and not (0 <= depot < len(locations)):
            raise ValueError(
                f"depot must be a valid index between 0 and {len(locations) - 1}, got {depot}"
            )
        return depot


class OptimizeRouteResponse(BaseModel):
    """
    The JSON shape we send BACK to the client.
    Declaring this (instead of just returning a raw dict) means FastAPI
    will show it in the Swagger docs and double-check our own output.
    """

    route: list[str]
    total_distance: int
    unit: str = "km"
