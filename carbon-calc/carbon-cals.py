import json
import math

# Emission Factors (kg CO2 per unit)
# Scope 1 direct tailpipe combustion factors via DEFRA / EPA / ARAI.
# Scope 2 grid electricity generation intensity (fixed-scope benchmark)
# via Central Electricity Authority (CEA) India / UK DEFRA Open Government Licence.
EMISSION_FACTORS = {
    "petrol": 2.31,     # kg CO2 / Liter
    "diesel": 2.68,     # kg CO2 / Liter
    "cng": 2.75,        # kg CO2 / kg
    "electric": 0.475   # kg CO2 / kWh (Fixed-scope estimate: National grid average)
}

# Standard default fuel assigned if none is specified by the caller
DEFAULT_VEHICLE_FUELS = {
    "two_wheeler": "petrol",
    "sedan": "petrol",
    "suv": "diesel",
    "mini_van": "cng",
    "truck": "diesel",
    "auto": "cng",
}

# Full matrix of 6 vehicles x 4 fuel variants (24 combinations)
# Baseline efficiencies reflect standardized real-world mixed fleet operations.
VEHICLE_PROFILES = {
    "two_wheeler": {
        "petrol": {"default_efficiency": 50.0, "unit": "km/L"},
        "electric": {"default_efficiency": 25.0, "unit": "km/kWh"},
        "cng": {"default_efficiency": 65.0, "unit": "km/kg"},
        "diesel": {"default_efficiency": 45.0, "unit": "km/L"},
    },
    "sedan": {
        "petrol": {"default_efficiency": 15.0, "unit": "km/L"},
        "diesel": {"default_efficiency": 18.0, "unit": "km/L"},
        "cng": {"default_efficiency": 22.0, "unit": "km/kg"},
        "electric": {"default_efficiency": 6.5, "unit": "km/kWh"},
    },
    "suv": {
        "diesel": {"default_efficiency": 12.0, "unit": "km/L"},
        "petrol": {"default_efficiency": 10.0, "unit": "km/L"},
        "cng": {"default_efficiency": 13.5, "unit": "km/kg"},
        "electric": {"default_efficiency": 5.0, "unit": "km/kWh"},
    },
    "mini_van": {
        "cng": {"default_efficiency": 18.0, "unit": "km/kg"},
        "petrol": {"default_efficiency": 13.0, "unit": "km/L"},
        "diesel": {"default_efficiency": 15.0, "unit": "km/L"},
        "electric": {"default_efficiency": 5.5, "unit": "km/kWh"},
    },
    "truck": {
        "diesel": {"default_efficiency": 4.5, "unit": "km/L"},
        "cng": {"default_efficiency": 4.0, "unit": "km/kg"},
        "petrol": {"default_efficiency": 3.5, "unit": "km/L"},
        "electric": {"default_efficiency": 1.2, "unit": "km/kWh"},
    },
    "auto": {
        "cng": {"default_efficiency": 28.0, "unit": "km/kg"},
        "petrol": {"default_efficiency": 22.0, "unit": "km/L"},
        "diesel": {"default_efficiency": 25.0, "unit": "km/L"},
        "electric": {"default_efficiency": 12.0, "unit": "km/kWh"},
    },
}

# Alias dictionary to normalize common naming variations
VEHICLE_ALIASES = {
    "bike": "two_wheeler",
    "two wheeler": "two_wheeler",
    "two_wheeler": "two_wheeler",
    "2 wheeler": "two_wheeler",
    "motorcycle": "two_wheeler",
    "sedan": "sedan",
    "car": "sedan",
    "suv": "suv",
    "mini van": "mini_van",
    "minivan": "mini_van",
    "mini_van": "mini_van",
    "van": "mini_van",
    "truck": "truck",
    "freight": "truck",
    "auto": "auto",
    "auto rickshaw": "auto",
    "auto_rickshaw": "auto",
    "autorickshaw": "auto",
    "three wheeler": "auto",
    "3 wheeler": "auto",
    "ev_car": "sedan",
}


def _normalize_vehicle_key(key: str) -> str:
    if not key:
        return ""
    cleaned = key.strip().lower().replace("-", " ")
    return VEHICLE_ALIASES.get(cleaned, cleaned.replace(" ", "_"))


def _normalize_fuel_key(key: str) -> str:
    return key.strip().lower() if key else ""


def analyze_traffic_and_efficiency(
    base_efficiency: float, 
    avg_speed_kmh: float, 
    fuel: str = "petrol"
) -> tuple:
    """
    Adjusts base fuel efficiency based on vehicle speed tiers and powertrain characteristics.
    Returns: (effective_efficiency, traffic_condition, congestion_index)
    """
    fuel_lower = fuel.lower()

    if fuel_lower == "electric":
        # EVs leverage regenerative braking in slow traffic, but suffer battery drain
        # and aerodynamic resistance at sustained highway speeds.
        if avg_speed_kmh <= 25:
            return base_efficiency * 0.90, "heavy_traffic", 0.85
        elif avg_speed_kmh <= 50:
            return base_efficiency * 0.95, "moderate_traffic", 0.45
        elif avg_speed_kmh <= 85:
            return base_efficiency * 1.00, "free_flow", 0.10
        else:
            return base_efficiency * 0.80, "high_speed_cruising", 0.05

    elif fuel_lower == "diesel":
        # Compression-ignition diesel engines exhibit lower idling fuel loss
        # and superior low-end torque in stop-and-go congestion.
        if avg_speed_kmh <= 25:
            return base_efficiency * 0.75, "heavy_traffic", 0.85
        elif avg_speed_kmh <= 50:
            return base_efficiency * 0.90, "moderate_traffic", 0.45
        elif avg_speed_kmh <= 85:
            return base_efficiency * 1.00, "free_flow", 0.10
        else:
            return base_efficiency * 0.88, "high_speed_cruising", 0.05

    else:
        # Standard spark-ignition curve (applies to Petrol and CNG Otto-cycle engines)
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
    custom_efficiency: float = None
) -> dict:
    vehicle_key = _normalize_vehicle_key(vehicle_class)
    if vehicle_key not in VEHICLE_PROFILES:
        valid_vehicles = list(VEHICLE_PROFILES.keys())
        return {"error": f"Unknown vehicle '{vehicle_class}'. Valid: {valid_vehicles}"}

    # Strict numeric finite validation
    if not math.isfinite(distance_km) or distance_km < 0:
        return {"error": "Distance must be a valid non-negative number"}
    if not math.isfinite(avg_speed_kmh) or avg_speed_kmh <= 0:
        return {"error": "Average speed must be a valid positive number"}

    # Resolve fuel type
    if fuel_type is None:
        fuel_key = DEFAULT_VEHICLE_FUELS[vehicle_key]
    else:
        fuel_key = _normalize_fuel_key(fuel_type)

    if fuel_key not in VEHICLE_PROFILES[vehicle_key]:
        valid_fuels = list(VEHICLE_PROFILES[vehicle_key].keys())
        return {
            "error": f"Fuel '{fuel_type}' is not supported for '{vehicle_class}'. Valid options: {valid_fuels}"
        }

    profile = VEHICLE_PROFILES[vehicle_key][fuel_key]

    # Validate custom efficiency vs default selection
    if custom_efficiency is None:
        base_eff = profile["default_efficiency"]
    elif not math.isfinite(custom_efficiency) or custom_efficiency <= 0:
        return {"error": "Custom efficiency must be a valid positive number"}
    else:
        base_eff = custom_efficiency

    effective_eff, traffic_condition, congestion_index = analyze_traffic_and_efficiency(
        base_eff, avg_speed_kmh, fuel_key
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
        "_raw_consumption": consumption,
        "_raw_co2_kg": co2_kg
    }


def compare_routes(
    normal_km: float,
    normal_speed_kmh: float,
    rz_km: float,
    rz_speed_kmh: float,
    vehicle_class: str,
    fuel_type: str = None,
    custom_efficiency: float = None
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

    # Unrounded floats prevent precision loss during subtraction
    normal_co2_raw = normal.get("_raw_co2_kg", normal["co2_kg"])
    rz_co2_raw = route_zero.get("_raw_co2_kg", route_zero["co2_kg"])

    # Signed differences: positive = savings, negative = deterioration
    co2_saved = normal_co2_raw - rz_co2_raw
    percentage_saved = (co2_saved / normal_co2_raw * 100) if normal_co2_raw > 0 else 0.0
    congestion_reduction = normal["congestion_index"] - route_zero["congestion_index"]

    # Filter private calculation keys from final API response
    normal_display = {k: v for k, v in normal.items() if not k.startswith("_")}
    rz_display = {k: v for k, v in route_zero.items() if not k.startswith("_")}

    return {
        "vehicle_type": vehicle_class,
        "normal_route": normal_display,
        "route_zero": rz_display,
        "metrics_comparison": {
            "co2_saved_kg": round(co2_saved, 2),
            "co2_percentage_reduction": round(percentage_saved, 2),
            "congestion_avoided": round(congestion_reduction, 2),
            "normal_traffic": normal["traffic_condition"],
            "route_zero_traffic": route_zero["traffic_condition"]
        }
    }


if __name__ == "__main__":
    result = compare_routes(
        normal_km=40.0, normal_speed_kmh=18.0,
        rz_km=46.0, rz_speed_kmh=65.0,
        vehicle_class="Mini van", fuel_type="cng"
    )
    print(json.dumps(result, indent=4))