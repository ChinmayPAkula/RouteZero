"""
main.py
-------
The actual FastAPI application: defines the HTTP endpoints and wires the
validated request (models.py) into the existing optimizer (optimizer.py).

This file does NOT contain any OR-Tools logic itself — it only calls
solve_route(), which already exists and is already tested.
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from app.models import OptimizeRouteRequest, OptimizeRouteResponse
from app.optimizer import solve_route

app = FastAPI(title="RouteZero Backend", version="0.1.0")

# ----------------------------------------------------------------------
# CORS (Cross-Origin Resource Sharing)
#
# Browsers block a webpage on one origin (e.g. http://localhost:3000,
# the frontend teammate's dev server) from calling an API on a different
# origin (e.g. http://localhost:8000, this backend) UNLESS the API
# explicitly allows it. CORS middleware adds the headers that say
# "yes, this origin is allowed to call me."
#
# For an MVP/hackathon, we allow all origins to keep development simple.
# In a real production system you'd restrict this to the frontend's
# actual domain.
# ----------------------------------------------------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health_check() -> dict:
    """Simple endpoint to confirm the server is up and responding."""
    return {"status": "ok"}


@app.post("/optimize-route", response_model=OptimizeRouteResponse)
def optimize_route(request: OptimizeRouteRequest) -> OptimizeRouteResponse:
    """
    Accepts locations + a distance matrix + a depot index, runs the
    OR-Tools optimizer, and returns the optimized route and total distance.

    FastAPI has already validated `request` against OptimizeRouteRequest's
    rules (models.py) before this function is even called — if the JSON
    didn't fit that shape, the client already got an HTTP 422 and we never
    got here.
    """
    try:
        result = solve_route(
            locations=request.locations,
            distance_matrix=request.distance_matrix,
            depot=request.depot,
        )
    except ValueError as error:
        # solve_route raises ValueError if OR-Tools can't find a solution.
        # We turn that into a clean HTTP error instead of a raw 500 crash.
        raise HTTPException(status_code=422, detail=str(error))

    return OptimizeRouteResponse(
        route=result["route"],
        total_distance=result["total_distance"],
        unit="km",
    )
