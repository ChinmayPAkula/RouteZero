from pydantic import BaseModel, Field, field_validator, model_validator

from .config import MAX_LOCATIONS


class OptimizeRouteRequest(BaseModel):
    pickup_location: str = Field(min_length=2, max_length=200)
    stops: list[str] = Field(default_factory=list)
    destination: str = Field(min_length=2, max_length=200)

    @field_validator("pickup_location", "destination")
    @classmethod
    def clean_endpoint(cls, value: str) -> str:
        value = value.strip()

        if not value:
            raise ValueError("location cannot be empty")

        return value

    @field_validator("stops")
    @classmethod
    def clean_stops(cls, values: list[str]) -> list[str]:
        cleaned = []

        for value in values:
            value = value.strip()

            if len(value) < 2 or len(value) > 200:
                raise ValueError(
                    "each stop must contain 2 to 200 characters"
                )

            cleaned.append(value)

        return cleaned

    @model_validator(mode="after")
    def validate_route(self):
        locations = [
            self.pickup_location,
            *self.stops,
            self.destination,
        ]

        if len(locations) > MAX_LOCATIONS:
            raise ValueError(
                f"at most {MAX_LOCATIONS} total locations are allowed"
            )

        normalized = [location.casefold() for location in locations]

        if len(set(normalized)) != len(normalized):
            raise ValueError(
                "pickup, stops, and destination must be unique"
            )

        return self


class Coordinate(BaseModel):
    name: str
    latitude: float
    longitude: float


class RouteResult(BaseModel):
    route: list[str]
    coordinates: list[Coordinate]
    total_distance: int
    total_duration: int
    total_distance_km: float
    total_duration_minutes: float
    distance_unit: str = "meters"
    duration_unit: str = "seconds"


class OptimizeRouteResponse(BaseModel):
    normal_route: RouteResult
    optimized_route: RouteResult