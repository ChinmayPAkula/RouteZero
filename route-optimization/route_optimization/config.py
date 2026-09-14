import os

NOMINATIM_URL = os.getenv("NOMINATIM_URL", "https://nominatim.openstreetmap.org")
OSRM_URL = os.getenv("OSRM_URL", "https://router.project-osrm.org")
USER_AGENT = os.getenv("ROUTEZERO_USER_AGENT", "RouteZero/1.0 (student project)")
HTTP_TIMEOUT = float(os.getenv("HTTP_TIMEOUT", "10"))
MAX_LOCATIONS = int(os.getenv("MAX_LOCATIONS", "12"))
SOLVER_TIME_LIMIT_SECONDS = int(os.getenv("SOLVER_TIME_LIMIT_SECONDS", "5"))
NOMINATIM_MIN_INTERVAL_SECONDS = float(os.getenv("NOMINATIM_MIN_INTERVAL_SECONDS", "1.05"))
