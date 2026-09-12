import json
EMISSION_FACTORS = {
    "petrol": 2.31,     # kg CO2 / Liter
    "diesel": 2.68,     # kg CO2 / Liter
    "cng": 2.75,        # kg CO2 / kg
    "electric": 0.475   # kg CO2 / kWh
}

VEHICLE_PROFILES = {
    "bike": {"fuel": "petrol", "default_efficiency": 50.0, "unit": "km/L"},
    "sedan": {"fuel": "petrol", "default_efficiency": 15.0, "unit": "km/L"},
    "suv": {"fuel": "diesel", "default_efficiency": 12.0, "unit": "km/L"},
    "truck": {"fuel": "diesel", "default_efficiency": 4.5, "unit": "km/L"},
    "ev_car": {"fuel": "electric", "default_efficiency": 6.5, "unit": "km/kWh"},
}


def analyze_traffic_and_efficiency(base_efficiency: float, avg_speed_kmh: float):
    """
    Returns:
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
    avg_speed_kmh: float = 60.0,
    custom_efficiency: float = None
) -> dict:
    vehicle_key = vehicle_class.strip().lower()
    if vehicle_key not in VEHICLE_PROFILES:
        return {"error": f"Unknown vehicle '{vehicle_class}'. Valid: {list(VEHICLE_PROFILES.keys())}"}

    if distance_km < 0:
        return {"error": "Distance cannot be negative"}
    if avg_speed_kmh <= 0:
        return {"error": "Average speed must be greater than zero"}

    profile = VEHICLE_PROFILES[vehicle_key]
    fuel = profile["fuel"]
    base_eff = custom_efficiency if (custom_efficiency and custom_efficiency > 0) else profile["default_efficiency"]

    # Compute traffic metrics & speed-adjusted mileage
    effective_eff, traffic_condition, congestion_index = analyze_traffic_and_efficiency(base_eff, avg_speed_kmh)

    consumption = distance_km / effective_eff
    co2_kg = consumption * EMISSION_FACTORS[fuel]

    return {
        "vehicle": vehicle_key,
        "fuel": fuel,
        "distance_km": round(distance_km, 2),
        "avg_speed_kmh": round(avg_speed_kmh, 1),
        "traffic_condition": traffic_condition,
        "congestion_index": congestion_index,
        "effective_efficiency": round(effective_eff, 2),
        "consumption": round(consumption, 2),
        "unit": profile["unit"],
        "co2_kg": round(co2_kg, 2)
    }


def compare_routes(
    normal_km: float,
    normal_speed_kmh: float,
    rz_km: float,
    rz_speed_kmh: float,
    vehicle_class: str,
    custom_efficiency: float = None
) -> dict:
    normal = calculate_emissions(normal_km, vehicle_class, normal_speed_kmh, custom_efficiency)
    route_zero = calculate_emissions(rz_km, vehicle_class, rz_speed_kmh, custom_efficiency)

    if "error" in normal:
        return normal
    if "error" in route_zero:
        return route_zero

    co2_saved = max(0.0, normal["co2_kg"] - route_zero["co2_kg"])
    percentage_saved = (co2_saved / normal["co2_kg"] * 100) if normal["co2_kg"] > 0 else 0.0
    congestion_reduction = max(0.0, normal["congestion_index"] - route_zero["congestion_index"])

    return {
        "vehicle_type": vehicle_class,
        "normal_route": normal,
        "route_zero": route_zero,
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
        vehicle_class="sedan"
    )
    print(json.dumps(result, indent=4))