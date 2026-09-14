# RouteZero — Route Optimization

A Tamil Nadu-focused FastAPI module that accepts a pickup, intermediate stops and a final destination, then:

**Locations → Nominatim → Coordinates → OSRM matrix → OR-Tools → Optimized route**

## Design

The system does **not** precompute a matrix for every location in Tamil Nadu. Instead, it supports locations across Tamil Nadu and builds the road distance/time matrix dynamically for only the locations in the current request.

- `geocoding.py`: place text → coordinates, with Tamil Nadu validation
- `routing.py`: coordinates → OSRM road distance and duration matrices
- `optimizer.py`: fixed-start/fixed-end OR-Tools route optimization
- `main.py`: FastAPI orchestration

The pickup is always first, the destination is always last, and only intermediate stops are reordered.

## Setup

```bat
cd route-optimization
python -m venv .venv
.venv\Scripts\activate
python -m pip install -r requirements.txt
```

For public Nominatim usage, set a meaningful application User-Agent:

```bat
set ROUTEZERO_USER_AGENT=RouteZero/1.0 (your-contact-or-project-info)
```

## Run

```bat
python -m uvicorn app.main:app --reload
```

Open Swagger at `http://127.0.0.1:8000/docs`.

## API

### GET /health

Returns:

```json
{"status": "healthy"}
```

### POST /optimize-route

Request:

```json
{
  "pickup_location": "VIT Vellore",
  "stops": [
    "Katpadi Railway Station",
    "Vellore Fort",
    "CMC Vellore"
  ],
  "destination": "Chennai Central"
}
```


### Replace ONLY that part with:

```markdown
Response shape:

```json
{
  "normal_route": {
    "route": [
      "VIT Vellore",
      "Katpadi Railway Station",
      "Vellore Fort",
      "CMC Vellore",
      "Chennai Central"
    ],
    "coordinates": [
      {
        "name": "VIT Vellore",
        "latitude": 12.0,
        "longitude": 79.0
      }
    ],
    "total_distance": 150000,
    "total_duration": 10800,
    "total_distance_km": 150.0,
    "total_duration_minutes": 180.0,
    "distance_unit": "meters",
    "duration_unit": "seconds"
  },
  "optimized_route": {
    "route": [
      "VIT Vellore",
      "Vellore Fort",
      "CMC Vellore",
      "Katpadi Railway Station",
      "Chennai Central"
    ],
    "coordinates": [
      {
        "name": "VIT Vellore",
        "latitude": 12.0,
        "longitude": 79.0
      }
    ],
    "total_distance": 140000,
    "total_duration": 10000,
    "total_distance_km": 140.0,
    "total_duration_minutes": 166.7,
    "distance_unit": "meters",
    "duration_unit": "seconds"
  }
}
Values above illustrate the response format; production values come from OSRM.

## Tests

Tests mock external APIs, so pytest does not require internet:

```bat
python -m pytest -v
```

## Limits and production notes

The default maximum is 12 total locations because pairwise matrices grow quadratically and public routing/geocoding endpoints are shared resources. Configuration can be changed with environment variables.

The public Nominatim and OSRM services are suitable for development/prototyping subject to their policies and capacity. For production-scale traffic, use an appropriate hosted provider or self-host the services.

This module intentionally scopes accepted geocoding results to Tamil Nadu.
