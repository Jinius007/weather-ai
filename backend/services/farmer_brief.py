from __future__ import annotations

import math
import time
from datetime import datetime, timezone
from typing import Any

import httpx

from services.location import find_nearest_district
from services.weather import WEATHER_SOURCE, _weather_code_label, load_districts

OPEN_METEO_URL = "https://api.open-meteo.com/v1/forecast"

BRIEF_TEMPLATES: dict[str, dict[str, Any]] = {
    "hi": {
        "outlook_rain": "{area} में अगले 24–48 घंटे में बारिश की संभावना है।",
        "outlook_heavy_rain": "{area} में अगले 24–48 घंटे में तेज़ बारिश की संभावना है।",
        "outlook_dry": "{area} में अगले 24–48 घंटे में मौसम शुष्क और गर्म रह सकता है।",
        "outlook_cloudy": "{area} में अगले 24–48 घंटे में बादल छाए रह सकते हैं, हल्की बारिश संभव है।",
        "outlook_clear": "{area} में अगले 24–48 घंटे में मौसम साफ रहने की संभावना है।",
        "numbers": "अधिकतम तापमान {tmax}°C, न्यूनतम {tmin}°C। अनुमानित बारिश {rain} mm।",
        "warn_sowing": "విత్తని डालें।",
        "warn_harvest": "कटाई न करें।",
        "warn_fertilizer": "खाद न डालें।",
        "warn_pesticide": "कीटनाशक छिड़काव न करें।",
        "warn_irrigation": "सिंचाई न करें।",
    },
    "te": {
        "outlook_rain": "{area} లో 24–48 గంటల్లో వర్షం పడే అవకాశం ఉంది.",
        "outlook_heavy_rain": "{area} లో 24–48 గంటల్లో భారీ వర్షం రావచ్చు.",
        "outlook_dry": "{area} లో 24–48 గంటలు వేడిగా, పొడిగా ఉండవచ్చు.",
        "outlook_cloudy": "{area} లో 24–48 గంటల్లో మేఘావృతం, తేలికపాటి వర్షం.",
        "outlook_clear": "{area} లో 24–48 గంటల్లో వాతావరణం స్పష్టంగా ఉండవచ్చు.",
        "numbers": "గరిష్ట {tmax}°C, కనిష్ట {tmin}°C. అంచనా వర్షం {rain} mm.",
        "warn_sowing": "విత్తని डालें।",
        "warn_harvest": "పంట కోయవద్దు.",
        "warn_fertilizer": "ఎరువులు వేయవద్దు.",
        "warn_pesticide": "కీటకనాశిని పిచికారీ చేయవద్దు.",
        "warn_irrigation": "నీటిపారుదల చేయవద్దు.",
    },
    "ta": {
        "outlook_rain": "{area} இல் 24–48 மணி நேரத்தில் மழை பெய்யலாம்.",
        "outlook_heavy_rain": "{area} இல் 24–48 மணி நேரத்தில் கனமழை வரலாம்.",
        "outlook_dry": "{area} இல் 24–48 மணி நேரம் வெப்பமும் வறட்சியும்.",
        "outlook_cloudy": "{area} இல் 24–48 மணி நேரம் மேகமூட்டம், லேசான மழை.",
        "outlook_clear": "{area} இல் 24–48 மணி நேரம் வானிலை தெளிவாக.",
        "numbers": "அதிகபட்சம் {tmax}°C, குறைந்த {tmin}°C. மழை {rain} mm.",
        "warn_sowing": "విత్తని डालें।",
        "warn_harvest": "அறுவடை செய்ய வேண்டாம்.",
        "warn_fertilizer": "உரம் இட வேண்டாம்.",
        "warn_pesticide": "பூச்சிக்கொல்லி தெளிக்க வேண்டாம்.",
        "warn_irrigation": "பாசனம் செய்ய வேண்டாம்.",
    },
    "mr": {
        "outlook_rain": "{area} मध्ये पुढील 24–48 तासांत पाऊस पडण्याची शक्यता.",
        "outlook_heavy_rain": "{area} मध्ये पुढील 24–48 तासांत जोरदार पाऊस.",
        "outlook_dry": "{area} मध्ये पुढील 24–48 तास उष्ण व कोरडे.",
        "outlook_cloudy": "{area} मध्ये पुढील 24–48 तास ढगाळ, हलका पाऊस.",
        "outlook_clear": "{area} मध्ये पुढील 24–48 तास हवामान स्वच्छ.",
        "numbers": "कमाल {tmax}°C, किमान {tmin}°C. पाऊस {rain} mm.",
        "warn_sowing": "విత్తని डालें।",
        "warn_harvest": "कापणी करू नका.",
        "warn_fertilizer": "खत घालू नका.",
        "warn_pesticide": "कीटकनाशक फवारणी करू नका.",
        "warn_irrigation": "सिंचन करू नका.",
    },
    "bn": {
        "outlook_rain": "{area} এ 24–48 ঘণ্টায় বৃষ্টির সম্ভাবনা।",
        "outlook_heavy_rain": "{area} এ 24–48 ঘণ্টায় ভারী বৃষ্টির সম্ভাবনা।",
        "outlook_dry": "{area} এ 24–48 ঘণ্টা গরম ও শুষ্ক থাকতে পারে।",
        "outlook_cloudy": "{area} এ 24–48 ঘণ্টা মেঘলা, হালকা বৃষ্টি।",
        "outlook_clear": "{area} এ 24–48 ঘণ্টা পরিষ্কার আবহাওয়া।",
        "numbers": "সর্বোচ্চ {tmax}°C, সর্বনিম্ন {tmin}°C। বৃষ্টি {rain} mm।",
        "warn_sowing": "విత్తని डालें।",
        "warn_harvest": "ফসল তুলবেন না।",
        "warn_fertilizer": "সার দেবেন না।",
        "warn_pesticide": "কীটনাশক প্রয়োগ করবেন না।",
        "warn_irrigation": "সেচ দেবেন না।",
    },
}

for code in ("kn", "ml", "gu", "pa", "or", "as"):
    if code not in BRIEF_TEMPLATES:
        BRIEF_TEMPLATES[code] = BRIEF_TEMPLATES["hi"]


def _negative_warnings(
    rain: float, t_max: float, t_min: float, wind: float, rain_prob: float, weather: str
) -> list[str]:
    warnings: list[str] = []
    w = weather.lower()
    heavy_rain = rain >= 15 or "heavy" in w or "thunder" in w or rain_prob >= 70
    light_rain = 3 <= rain < 15 or "drizzle" in w or "rain" in w
    dry_hot = rain < 3 and t_max >= 36
    windy = wind >= 35

    if heavy_rain:
        warnings.extend(["sowing", "harvest", "fertilizer", "pesticide", "irrigation"])
    elif light_rain:
        warnings.extend(["pesticide", "fertilizer", "harvest"])
        if rain >= 8:
            warnings.append("sowing")
    elif dry_hot:
        warnings.extend(["sowing", "pesticide"])
    elif windy:
        warnings.append("pesticide")

    if t_max >= 40 and "pesticide" not in warnings:
        warnings.append("pesticide")

    seen: set[str] = set()
    unique: list[str] = []
    for item in warnings:
        if item not in seen:
            seen.add(item)
            unique.append(item)
    return unique


def _pick_outlook_key(rain: float, weather: str, rain_prob: float) -> str:
    w = weather.lower()
    if rain >= 15 or "heavy" in w or "thunder" in w:
        return "outlook_heavy_rain"
    if rain >= 3 or rain_prob >= 50 or "rain" in w or "drizzle" in w:
        return "outlook_rain"
    if "cloud" in w or "overcast" in w:
        return "outlook_cloudy"
    if rain < 2 and "clear" in w:
        return "outlook_clear"
    if rain < 3:
        return "outlook_dry"
    return "outlook_cloudy"


def build_farmer_brief(district: dict[str, Any], daily: dict[str, Any]) -> dict[str, Any]:
    lang = district.get("language_code", "hi")
    templates = BRIEF_TEMPLATES.get(lang, BRIEF_TEMPLATES["hi"])
    area = district["name"]

    dates = daily.get("time", [])[:2]
    precip = daily.get("precipitation_sum", [])[:2]
    temp_max = daily.get("temperature_2m_max", [])[:2]
    temp_min = daily.get("temperature_2m_min", [])[:2]
    codes = daily.get("weather_code", [])[:2]
    wind = daily.get("wind_speed_10m_max", [])[:2]
    rain_prob = daily.get("precipitation_probability_max", [])[:2]

    total_rain = round(sum(p or 0 for p in precip), 1)
    tmax = round(max(temp_max) if temp_max else 30, 1)
    tmin = round(min(temp_min) if temp_min else 20, 1)
    max_wind = max(wind) if wind else 0
    max_prob = max(rain_prob) if rain_prob else 0
    dominant = _weather_code_label(max(codes, key=codes.count) if codes else 0)

    outlook_key = _pick_outlook_key(total_rain, dominant, max_prob)
    outlook = templates[outlook_key].format(area=area)
    numbers = templates["numbers"].format(tmax=tmax, tmin=tmin, rain=total_rain)

    warning_keys = _negative_warnings(total_rain, tmax, tmin, max_wind, max_prob, dominant)
    warning_lines = [templates[f"warn_{k}"] for k in warning_keys if f"warn_{k}" in templates]

    parts = [outlook, numbers]
    if warning_lines:
        parts.append(" ".join(warning_lines))
    message_local = " ".join(parts)

    return {
        "district_id": district["id"],
        "district_name": district["name"],
        "state": district["state"],
        "language_code": lang,
        "language_name": district["language_name"],
        "distance_km": district.get("distance_km"),
        "location_method": district.get("location_method", "gps"),
        "source": WEATHER_SOURCE,
        "updated_at": datetime.now(timezone.utc).isoformat(),
        "forecast_fetched_at": datetime.now(timezone.utc).isoformat(),
        "period_hours": 48,
        "period_label": "24–48 hours",
        "outlook_local": outlook,
        "numbers_local": numbers,
        "warnings_local": warning_lines,
        "message_local": message_local,
        "weather_summary": dominant,
        "total_rainfall_mm": total_rain,
        "temp_max_c": tmax,
        "temp_min_c": tmin,
    }


async def _fetch_open_meteo_daily(lat: float, lon: float) -> dict[str, Any]:
    """Always fetch live forecast from Open-Meteo (no cache)."""
    params = {
        "latitude": lat,
        "longitude": lon,
        "daily": "weather_code,temperature_2m_max,temperature_2m_min,precipitation_sum,precipitation_probability_max,wind_speed_10m_max",
        "timezone": "Asia/Kolkata",
        "forecast_days": 2,
        "_t": int(time.time()),
    }
    headers = {"Cache-Control": "no-cache"}

    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.get(OPEN_METEO_URL, params=params, headers=headers)
        response.raise_for_status()
        return response.json()


async def resolve_coords_from_ip(client_ip: str | None) -> tuple[float, float]:
    if not client_ip or client_ip in ("127.0.0.1", "::1"):
        raise ValueError("Could not detect location from IP")

    async with httpx.AsyncClient(timeout=10.0) as client:
        response = await client.get(f"http://ip-api.com/json/{client_ip}?fields=lat,lon,status")
        response.raise_for_status()
        data = response.json()

    if data.get("status") != "success":
        raise ValueError("Could not detect location from IP")

    return float(data["lat"]), float(data["lon"])


async def fetch_local_farmer_brief(
    latitude: float,
    longitude: float,
    *,
    location_method: str = "gps",
) -> dict[str, Any]:
    districts = load_districts()
    if not districts:
        raise ValueError("District data unavailable")

    district = find_nearest_district(latitude, longitude, districts)
    district = {**district, "location_method": location_method}

    weather = await _fetch_open_meteo_daily(district["latitude"], district["longitude"])
    return build_farmer_brief(district, weather.get("daily", {}))


async def fetch_local_farmer_brief_from_ip(client_ip: str | None) -> dict[str, Any]:
    lat, lon = await resolve_coords_from_ip(client_ip)
    return await fetch_local_farmer_brief(lat, lon, location_method="ip")
