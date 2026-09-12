# RouteZero — Backend & Route Optimization Module

## 1. What RouteZero is

RouteZero is a carbon-aware logistics route optimization system built for
Engineering Day 2026. It aims to help delivery operations pick efficient
routes and, eventually, understand the carbon/fuel cost of those routes.

## 2. What this module does

This is the **Backend + Route Optimization** module. Given a set of
delivery locations and the distances between them, it computes an
optimized delivery route (starting and ending at a depot) and the total
distance of that route, and exposes this as a REST API for the frontend
to call.

Real road-distance integration (OSRM/OpenRouteService) and carbon
calculation are planned future extensions — not part of this MVP.

## 3. Architecture

```
Frontend
   |
   v
POST /optimize-route
   |
   v
FastAPI
   |
   v
Pydantic validation
   |
   v
Route Optimizer (solve_route)
   |
   v
Google OR-Tools Routing Solver
   |
   v
Optimized Route + Total Distance
   |
   v
JSON Response
   |
   v
Frontend
```

## 4. Tech stack

- Python 3
- FastAPI — web framework / REST API
- Pydantic — request/response validation
- Google OR-Tools — routing solver
- Uvicorn — ASGI server to run FastAPI
- Pytest + httpx — testing

## 5. Project structure

```
routezero/
│
├── app/
│   ├── __init__.py
│   ├── main.py         # FastAPI app, endpoints
│   ├── models.py        # Pydantic request/response models + validation
│   └── optimizer.py     # OR-Tools route optimization logic
│
├── tests/
│   ├── test_optimizer.py
│   └── test_api.py
│
├── requirements.txt
└── README.md
```

## 6. Installation

Windows:

```
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

macOS/Linux:

```
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## 7. Running the server

```
uvicorn app.main:app --reload
```

Then open: http://127.0.0.1:8000/docs

## 8. API endpoints

### `GET /health`

Returns:

```json
{ "status": "ok" }
```

### `POST /optimize-route`

**Example request:**

```json
{
  "locations": ["Depot", "A", "B", "C", "D"],
  "distance_matrix": [
    [0, 10, 15, 20, 12],
    [10, 0, 8, 14, 7],
    [15, 8, 0, 9, 11],
    [20, 14, 9, 0, 6],
    [12, 7, 11, 6, 0]
  ],
  "depot": 0
}
```

**Example response:**

```json
{
  "route": ["Depot", "A", "B", "C", "D", "Depot"],
  "total_distance": 45,
  "unit": "km"
}
```

Invalid input (e.g. mismatched matrix dimensions, negative distances, an
out-of-range depot) returns HTTP 422 with a JSON body describing exactly
what was wrong — it never reaches the optimizer.

## 9. How OR-Tools is used

`app/optimizer.py` builds an OR-Tools `RoutingModel` for a single
vehicle. A distance callback tells the solver the cost between any two
locations (read from the supplied distance matrix). The solver uses the
`PATH_CHEAPEST_ARC` first-solution strategy to build an optimized route
under a minimum-distance objective, which is then read back out and
converted into location names and a total distance. The route is
computed by OR-Tools every time — it is never hardcoded.

## 10. Running tests

```
pytest tests/ -v
```

This runs 12 tests covering: the optimizer directly (route starts/ends at
depot, every location visited once, distance calculated correctly), and
the API layer (`/health`, a valid `/optimize-route` call, and rejection
of empty locations, mismatched matrix dimensions, an invalid depot, and
negative distances).
