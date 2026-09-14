class RouteZeroError(Exception):
    """Base exception for expected RouteZero failures."""


class GeocodingError(RouteZeroError):
    pass


class LocationNotFoundError(GeocodingError):
    pass


class OutsideTamilNaduError(GeocodingError):
    pass


class RoutingError(RouteZeroError):
    pass


class OptimizationError(RouteZeroError):
    pass
