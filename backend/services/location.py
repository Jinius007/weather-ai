from __future__ import annotations

import math
from typing import Any


def _haversine_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    r = 6371.0
    p1, p2 = math.radians(lat1), math.radians(lat2)
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = math.sin(dlat / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dlon / 2) ** 2
    return 2 * r * math.asin(math.sqrt(a))


def find_nearest_district(latitude: float, longitude: float, districts: list[dict[str, Any]]) -> dict[str, Any]:
    best = min(
        districts,
        key=lambda d: _haversine_km(latitude, longitude, d["latitude"], d["longitude"]),
    )
    distance_km = round(_haversine_km(latitude, longitude, best["latitude"], best["longitude"]), 1)
    return {**best, "distance_km": distance_km}
