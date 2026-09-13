import json

# Emission factors: mass of CO2 emitted per physical fuel or energy unit
EMISSION_FACTORS = {
    "petrol": 2.31,  # kg CO2 / Liter (DEFRA / EPA)
    "diesel": 2.68,  # kg CO2 / Liter (DEFRA / EPA)
    "cng": 2.75,  # kg CO2 / kg    (ARAI / BEE)
    "electric": 0.475,  # kg CO2 / kWh   (CEA India / IEA Grid Baseline)
}

# Supported vehicle classes mapped across all 4 fuel types (Petrol, Diesel, CNG, Electric)
VEHICLE_PROFILES = {
    "two_wheeler": {
        "petrol": {"default_efficiency": 50.0, "unit": "km/L"},
        "diesel": {
            "default_efficiency": 70.0,
            "unit": "km/L",
        },  # Historical & agricultural diesel bikes (e.g., RE Taurus 325cc)
        "cng": {
            "default_efficiency": 65.0,
            "unit": "km/kg",
        },  # e.g., Bajaj Freedom 125
        "electric": {
            "default_efficiency": 35.0,
            "unit": "km/kWh",
        },  # e.g., Ather 450X, Ola S1
    },
    "sedan": {
        "petrol": {"default_efficiency": 15.0, "unit": "km/L"},
        "diesel": {"default_efficiency": 18.0, "unit": "km/L"},
        "cng": {"default_efficiency": 22.0, "unit": "km/kg"},
        "electric": {"default_efficiency": 6.5, "unit": "km/kWh"},
    },
    "suv": {
        "petrol": {"default_efficiency": 10.0, "unit": "km/L"},
        "diesel": {"default_efficiency": 12.0, "unit": "km/L"},
        "cng": {"default_efficiency": 14.0, "unit": "km/kg"},
        "electric": {"default_efficiency": 5.5, "unit": "km/kWh"},
    },
    "mini_van": {
        "petrol": {"default_efficiency": 14.0, "unit": "km/L"},
        "diesel": {"default_efficiency": 16.0, "unit": "km/L"},
        "cng": {"default_efficiency": 20.0, "unit": "km/kg"},
        "electric": {"default_efficiency": 5.0, "unit": "km/kWh"},
    },
    "truck": {
        "petrol": {"default_efficiency": 6.5, "unit": "km/L"},
        "diesel": {"default_efficiency": 4.5, "unit": "km/L"},
        "cng": {"default_efficiency": 5.0, "unit": "km/kg"},
        "electric": {"default_efficiency": 1.5, "unit": "km/kWh"},
    },
    "auto": {
        "petrol": {"default_efficiency": 25.0, "unit": "km/L"},
        "diesel": {"default_efficiency": 22.0, "unit": "km/L"},
        "cng": {"default_efficiency": 28.0, "unit": "km/kg"},
        "electric": {"default_efficiency": 14.0, "unit": "km/kWh"},
    },
}

# Default fuel fallback if omitted by the caller
DEFAULT_VEHICLE_FUELS = {
    "two_wheeler": "petrol",
    "sedan": "petrol",
    "suv": "diesel",
    "mini_van": "petrol",
    "truck": "diesel",
    "auto": "cng",
}


def _normalize_key(key: str) -> str:
  """Normalizes string inputs to lowercase with underscores (handles spaces and hyphens)."""
  if not key:
    return ""
  return key.strip().lower().replace(" ", "_").replace("-", "_")


def analyze_traffic_and_efficiency(
    base_efficiency: float, avg_speed_kmh: float
):
  """Adjusts baseline efficiency based on speed tiers and returns:

  (effective_efficiency, traffic_condition, congestion_index)
  """
  if avg_speed_kmh <= 25:
    return base_efficiency * 0.70, "heavy_traffic", 0.85
  elif avg_speed_kmh <= 50:
    return base_efficiency * 0.85, "moderate_traffic", 0.45
  elif avg_speed_kmh <= 85:
    return base_efficiency * 1.00, "free_flow", 0.10
  else:
    return base_efficiency * 0.90, "high_speed_cruising", 0.05


def calculate_emissions(
    distance_km: float,
    vehicle_class: str,
    fuel_type: str = None,
    avg_speed_kmh: float = 60.0,
    custom_efficiency: float = None,
) -> dict:
  vehicle_key = _normalize_key(vehicle_class)
  if vehicle_key not in VEHICLE_PROFILES:
    valid_vehicles = list(VEHICLE_PROFILES.keys())
    return {
        "error": (
            f"Unknown vehicle '{vehicle_class}'. Valid categories:"
            f" {valid_vehicles}"
        )
    }

  # Fall back to category default fuel if none specified
  if fuel_type is None:
    fuel_key = DEFAULT_VEHICLE_FUELS[vehicle_key]
  else:
    fuel_key = _normalize_key(fuel_type)

  if fuel_key not in VEHICLE_PROFILES[vehicle_key]:
    valid_fuels = list(VEHICLE_PROFILES[vehicle_key].keys())
    return {
        "error": (
            f"Fuel '{fuel_type}' is not supported for '{vehicle_class}'."
            f" Valid options: {valid_fuels}"
        )
    }

  if distance_km < 0:
    return {"error": "Distance cannot be negative"}
  if avg_speed_kmh <= 0:
    return {"error": "Average speed must be greater than zero"}

  profile = VEHICLE_PROFILES[vehicle_key][fuel_key]
  base_eff = (
      custom_efficiency
      if (custom_efficiency and custom_efficiency > 0)
      else profile["default_efficiency"]
  )

  # Calculate speed and congestion-adjusted efficiency
  effective_eff, traffic_condition, congestion_index = (
      analyze_traffic_and_efficiency(base_eff, avg_speed_kmh)
  )

  consumption = distance_km / effective_eff
  co2_kg = consumption * EMISSION_FACTORS[fuel_key]

  return {
      "vehicle": vehicle_key,
      "fuel": fuel_key,
      "distance_km": round(distance_km, 2),
      "avg_speed_kmh": round(avg_speed_kmh, 1),
      "traffic_condition": traffic_condition,
      "congestion_index": congestion_index,
      "effective_efficiency": round(effective_eff, 2),
      "consumption": round(consumption, 2),
      "unit": profile["unit"],
      "co2_kg": round(co2_kg, 2),
  }


def compare_routes(
    normal_km: float,
    normal_speed_kmh: float,
    rz_km: float,
    rz_speed_kmh: float,
    vehicle_class: str,
    fuel_type: str = None,
    custom_efficiency: float = None,
) -> dict:
  normal = calculate_emissions(
      normal_km, vehicle_class, fuel_type, normal_speed_kmh, custom_efficiency
  )
  route_zero = calculate_emissions(
      rz_km, vehicle_class, fuel_type, rz_speed_kmh, custom_efficiency
  )

  if "error" in normal:
    return normal
  if "error" in route_zero:
    return route_zero

  co2_saved = max(0.0, normal["co2_kg"] - route_zero["co2_kg"])
  percentage_saved = (
      (co2_saved / normal["co2_kg"] * 100) if normal["co2_kg"] > 0 else 0.0
  )
  congestion_reduction = max(
      0.0, normal["congestion_index"] - route_zero["congestion_index"]
  )

  return {
      "vehicle_type": vehicle_class,
      "fuel_type": normal["fuel"],
      "normal_route": normal,
      "route_zero": route_zero,
      "metrics_comparison": {
          "co2_saved_kg": round(co2_saved, 2),
          "co2_percentage_reduction": round(percentage_saved, 2),
          "congestion_avoided": round(congestion_reduction, 2),
          "normal_traffic": normal["traffic_condition"],
          "route_zero_traffic": route_zero["traffic_condition"],
      },
  }


if __name__ == "__main__":
  # Test: Comparing routes on a Diesel Two-Wheeler
  diesel_bike_result = compare_routes(
      normal_km=25.0,
      normal_speed_kmh=20.0,
      rz_km=29.0,
      rz_speed_kmh=55.0,
      vehicle_class="two_wheeler",
      fuel_type="diesel",
  )
  print("--- DIESEL TWO WHEELER TEST ---")
  print(json.dumps(diesel_bike_result, indent=4))