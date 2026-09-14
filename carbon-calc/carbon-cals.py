import json
import math

EMISSION_FACTORS = {
    "petrol": 2.31,     # kg CO2 / Liter
    "diesel": 2.68,     # kg CO2 / Liter
    "cng": 2.75,        # kg CO2 / kg
    "electric": 0.475   # kg CO2 / kWh (Scope 2 National Grid Average)
}

DEFAULT_VEHICLE_FUELS = {
    "two_wheeler": "petrol",
    "sedan": "petrol",
    "suv": "diesel",
    "mini_van": "cng",
    "truck": "diesel",
    "auto": "cng",
}

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

# Maps Google Maps API route traffic speed readings & colors
GMAPS_TRAFFIC_MAP = {
    "blue": "free_flow",
    "normal": "free_flow",
    "green": "free_flow",
    "orange": "moderate_traffic",
    "yellow": "moderate_traffic",
    "slow": "moderate_traffic",
    "red": "heavy_traffic",
    "dark_red": "heavy_traffic",
    "traffic_jam": "heavy_traffic",
    "stop_and_go": "heavy_traffic",
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
    avg_speed_kmh: float = None, 
    fuel: str = "petrol",
    traffic_condition: str = None
) -> tuple:
    """
    Computes (effective_efficiency, traffic_condition, congestion_index).
    Accepts either an explicit traffic condition (e.g. from Google Maps) or derives it from speed.
    """
    fuel_lower = fuel.lower()

    # If an explicit Google Maps condition was provided, resolve directly
    if traffic_condition:
        condition = traffic_condition.lower()
        if condition in GMAPS_TRAFFIC_MAP:
            condition = GMAPS_TRAFFIC_MAP[condition]
    elif avg_speed_kmh is not None:
        if avg_speed_kmh <= 25:
            condition = "heavy_traffic"
        elif avg_speed_kmh <= 50:
            condition = "moderate_traffic"
        elif avg_speed_kmh <= 85:
            condition = "free_flow"
        else:
            condition = "high_speed_cruising"
    else:
        condition = "free_flow"

    # Powertrain-specific attenuation based on resolved condition
    if fuel_lower == "electric":
        if condition == "heavy_traffic":
            return base_efficiency * 0.90, "heavy_traffic", 0.85
        elif condition == "moderate_traffic":
            return base_efficiency * 0.95, "moderate_traffic", 0.45
        elif condition == "free_flow":
            return base_efficiency * 1.00, "free_flow", 0.10
        else:  # high_speed_cruising
            return base_efficiency * 0.80, "high_speed_cruising", 0.05

    elif fuel_lower == "diesel":
        if condition == "heavy_traffic":
            return base_efficiency * 0.75, "heavy_traffic", 0.85
        elif condition == "moderate_traffic":
            return base_efficiency * 0.90, "moderate_traffic", 0.45
        elif condition == "free_flow":
            return base_efficiency * 1.00, "free_flow", 0.10
        else:
            return base_efficiency * 0.88, "high_speed_cruising", 0.05

    else:
        # Petrol / CNG light-duty curve
        if condition == "heavy_traffic":
            return base_efficiency * 0.70, "heavy_traffic", 0.85
        elif condition == "moderate_traffic":
            return base_efficiency * 0.85, "moderate_traffic", 0.45
        elif condition == "free_flow":
            return base_efficiency * 1.00, "free_flow", 0.10
        else:
            return base_efficiency * 0.90, "high_speed_cruising", 0.05


def calculate_emissions(
    distance_km: float,
    vehicle_class: str,
    fuel_type: str = None,
    avg_speed_kmh: float = 60.0,
    custom_efficiency: float = None,
    traffic_condition: str = None
) -> dict:
    """Calculates emissions for a uniform single-leg trip or average segment."""
    vehicle_key = _normalize_vehicle_key(vehicle_class)
    if vehicle_key not in VEHICLE_PROFILES:
        return {"error": f"Unknown vehicle '{vehicle_class}'. Valid: {list(VEHICLE_PROFILES.keys())}"}

    if not math.isfinite(distance_km) or distance_km < 0:
        return {"error": "Distance must be a valid non-negative number"}
    
    if traffic_condition is None:
        if not math.isfinite(avg_speed_kmh) or avg_speed_kmh <= 0:
            return {"error": "Average speed must be a valid positive number"}

    if fuel_type is None:
        fuel_key = DEFAULT_VEHICLE_FUELS[vehicle_key]
    else:
        fuel_key = _normalize_fuel_key(fuel_type)

    if fuel_key not in VEHICLE_PROFILES[vehicle_key]:
        return {"error": f"Fuel '{fuel_type}' is not supported for '{vehicle_class}'."}

    profile = VEHICLE_PROFILES[vehicle_key][fuel_key]

    if custom_efficiency is None:
        base_eff = profile["default_efficiency"]
    elif not math.isfinite(custom_efficiency) or custom_efficiency <= 0:
        return {"error": "Custom efficiency must be a valid positive number"}
    else:
        base_eff = custom_efficiency

    effective_eff, resolved_condition, congestion_index = analyze_traffic_and_efficiency(
        base_efficiency=base_eff,
        avg_speed_kmh=avg_speed_kmh,
        fuel=fuel_key,
        traffic_condition=traffic_condition
    )

    consumption = distance_km / effective_eff
    co2_kg = consumption * EMISSION_FACTORS[fuel_key]

    return {
        "vehicle": vehicle_key,
        "fuel": fuel_key,
        "distance_km": round(distance_km, 2),
        "avg_speed_kmh": round(avg_speed_kmh, 1) if avg_speed_kmh else None,
        "traffic_condition": resolved_condition,
        "congestion_index": congestion_index,
        "effective_efficiency": round(effective_eff, 2),
        "consumption": round(consumption, 2),
        "unit": profile["unit"],
        "co2_kg": round(co2_kg, 2),
        "_raw_consumption": consumption,
        "_raw_co2_kg": co2_kg
    }


def calculate_route_from_gmaps_segments(
    segments: list,
    vehicle_class: str,
    fuel_type: str = None,
    custom_efficiency: float = None
) -> dict:
    """
    Aggregates multi-segment route data received directly from Google Maps Directions/Routes API.
    
    Each element in `segments` must be a dict:
        {"distance_km": float, "traffic": "blue" | "orange" | "red" | "normal" | "slow" | "traffic_jam"}
        OR {"distance_km": float, "avg_speed_kmh": float}
    """
    if not segments:
        return {"error": "Segments list cannot be empty"}

    vehicle_key = _normalize_vehicle_key(vehicle_class)
    if vehicle_key not in VEHICLE_PROFILES:
        return {"error": f"Unknown vehicle '{vehicle_class}'. Valid: {list(VEHICLE_PROFILES.keys())}"}

    if fuel_type is None:
        fuel_key = DEFAULT_VEHICLE_FUELS[vehicle_key]
    else:
        fuel_key = _normalize_fuel_key(fuel_type)

    if fuel_key not in VEHICLE_PROFILES[vehicle_key]:
        return {"error": f"Fuel '{fuel_type}' is not supported for '{vehicle_class}'."}

    profile = VEHICLE_PROFILES[vehicle_key][fuel_key]

    if custom_efficiency is None:
        base_eff = profile["default_efficiency"]
    elif not math.isfinite(custom_efficiency) or custom_efficiency <= 0:
        return {"error": "Custom efficiency must be a valid positive number"}
    else:
        base_eff = custom_efficiency

    total_distance = 0.0
    total_consumption = 0.0
    weighted_congestion_sum = 0.0
    processed_segments = []

    for idx, seg in enumerate(segments):
        d_km = seg.get("distance_km", 0.0)
        if not math.isfinite(d_km) or d_km < 0:
            return {"error": f"Invalid distance at segment {idx}: {d_km}"}

        traffic_tag = seg.get("traffic") or seg.get("traffic_condition") or seg.get("color")
        speed_val = seg.get("avg_speed_kmh")

        eff_eff, cond, ci = analyze_traffic_and_efficiency(
            base_efficiency=base_eff,
            avg_speed_kmh=speed_val,
            fuel=fuel_key,
            traffic_condition=traffic_tag
        )

        seg_consumption = d_km / eff_eff
        seg_co2 = seg_consumption * EMISSION_FACTORS[fuel_key]

        total_distance += d_km
        total_consumption += seg_consumption
        weighted_congestion_sum += (d_km * ci)

        processed_segments.append({
            "segment_index": idx,
            "distance_km": round(d_km, 2),
            "traffic_color": traffic_tag,
            "traffic_condition": cond,
            "effective_efficiency": round(eff_eff, 2),
            "consumption": round(seg_consumption, 3),
            "co2_kg": round(seg_co2, 3)
        })

    if total_distance <= 0:
        return {"error": "Total route distance must be greater than zero"}

    total_co2 = total_consumption * EMISSION_FACTORS[fuel_key]
    avg_efficiency = total_distance / total_consumption
    avg_congestion = weighted_congestion_sum / total_distance

    return {
        "vehicle": vehicle_key,
        "fuel": fuel_key,
        "total_distance_km": round(total_distance, 2),
        "overall_effective_efficiency": round(avg_efficiency, 2),
        "total_consumption": round(total_consumption, 2),
        "unit": profile["unit"],
        "total_co2_kg": round(total_co2, 2),
        "average_congestion_index": round(avg_congestion, 2),
        "segments_breakdown": processed_segments,
        "_raw_consumption": total_consumption,
        "_raw_co2_kg": total_co2,
        "congestion_index": avg_congestion  # Compatible key for route comparison
    }


def compare_gmaps_routes(
    normal_route_segments: list,
    rz_route_segments: list,
    vehicle_class: str,
    fuel_type: str = None,
    custom_efficiency: float = None
) -> dict:
    """Compares a congested Google Maps default route against a RouteZero alternative."""
    normal = calculate_route_from_gmaps_segments(
        normal_route_segments, vehicle_class, fuel_type, custom_efficiency
    )
    route_zero = calculate_route_from_gmaps_segments(
        rz_route_segments, vehicle_class, fuel_type, custom_efficiency
    )

    if "error" in normal:
        return normal
    if "error" in route_zero:
        return route_zero

    normal_co2 = normal["_raw_co2_kg"]
    rz_co2 = route_zero["_raw_co2_kg"]

    co2_saved = normal_co2 - rz_co2
    percentage_saved = (co2_saved / normal_co2 * 100) if normal_co2 > 0 else 0.0
    congestion_reduction = normal["average_congestion_index"] - route_zero["average_congestion_index"]

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
        }
    }


if __name__ == "__main__":
    # Example scenario: 
    # Normal Route (40 km total): 10 km red gridlock, 12 km orange slowdown, 18 km blue flow.
    # RouteZero Detour (46 km total): 3 km orange, 43 km entirely blue highway.
    normal_route_google_data = [
        {"distance_km": 15.0, "traffic": "red"},
        {"distance_km": 12.0, "traffic": "orange"},
        {"distance_km": 18.0, "traffic": "blue"}
    ]

    rz_route_google_data = [
        {"distance_km": 3.0, "traffic": "orange"},
        {"distance_km": 43.0, "traffic": "blue"}
    ]

    result = compare_gmaps_routes(
        normal_route_segments=normal_route_google_data,
        rz_route_segments=rz_route_google_data,
        vehicle_class="sedan",
        fuel_type="petrol"
    )

    print(json.dumps(result, indent=4))