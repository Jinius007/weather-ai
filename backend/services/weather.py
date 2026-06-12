from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import httpx

DATA_DIR = Path(__file__).resolve().parents[1] / "data"
DISTRICTS_FILE = DATA_DIR / "districts.json"

OPEN_METEO_URL = "https://api.open-meteo.com/v1/forecast"
WEATHER_SOURCE = "Open-Meteo (open-source global weather API)"

# In-memory cache: district_id -> forecast payload
_forecast_cache: dict[str, dict[str, Any]] = {}
_cache_fetched_at: datetime | None = None

BATCH_SIZE = 50


def load_districts() -> list[dict[str, Any]]:
    if not DISTRICTS_FILE.exists():
        return []
    return json.loads(DISTRICTS_FILE.read_text(encoding="utf-8"))


def get_district_by_id(district_id: str) -> dict[str, Any] | None:
    for district in load_districts():
        if district["id"] == district_id:
            return district
    return None


def _weather_code_label(code: int | None) -> str:
    codes = {
        0: "Clear sky",
        1: "Mainly clear",
        2: "Partly cloudy",
        3: "Overcast",
        45: "Fog",
        48: "Depositing rime fog",
        51: "Light drizzle",
        53: "Moderate drizzle",
        55: "Dense drizzle",
        61: "Slight rain",
        63: "Moderate rain",
        65: "Heavy rain",
        66: "Light freezing rain",
        67: "Heavy freezing rain",
        71: "Slight snow",
        73: "Moderate snow",
        75: "Heavy snow",
        80: "Slight rain showers",
        81: "Moderate rain showers",
        82: "Violent rain showers",
        95: "Thunderstorm",
        96: "Thunderstorm with slight hail",
        99: "Thunderstorm with heavy hail",
    }
    return codes.get(code or 0, "Variable conditions")


async def fetch_weather_for_districts(districts: list[dict[str, Any]]) -> list[dict[str, Any]]:
    if not districts:
        return []

    params = {
        "latitude": ",".join(str(d["latitude"]) for d in districts),
        "longitude": ",".join(str(d["longitude"]) for d in districts),
        "daily": "weather_code,temperature_2m_max,temperature_2m_min,precipitation_sum,precipitation_probability_max,wind_speed_10m_max",
        "timezone": "Asia/Kolkata",
        "forecast_days": 16,
    }

    async with httpx.AsyncClient(timeout=60.0) as client:
        response = await client.get(OPEN_METEO_URL, params=params)
        response.raise_for_status()
        payload = response.json()

    if isinstance(payload, dict) and "daily" in payload:
        payloads = [payload]
    else:
        payloads = payload

    now = datetime.now(timezone.utc)
    results: list[dict[str, Any]] = []

    for district, weather in zip(districts, payloads):
        daily = weather.get("daily", {})
        dates = daily.get("time", [])
        if not dates:
            continue

        short_term = _slice_forecast(daily, 0, 3, "short_term")
        medium_term = _slice_forecast(daily, 3, 7, "medium_term")
        long_term = _slice_forecast(daily, 7, 16, "long_term")

        model_updated = weather.get("generationtime_ms")
        fetched_at = now.isoformat()

        entry = {
            "district_id": district["id"],
            "district_name": district["name"],
            "state": district["state"],
            "language_code": district["language_code"],
            "language_name": district["language_name"],
            "source": WEATHER_SOURCE,
            "updated_at": fetched_at,
            "model_run_note": "Forecast from Open-Meteo (ECMWF, NOAA GFS, and other national models)",
            "forecasts": {
                "short_term": short_term,
                "medium_term": medium_term,
                "long_term": long_term,
            },
            "raw_generation_ms": model_updated,
        }
        _forecast_cache[district["id"]] = entry
        results.append(entry)

    global _cache_fetched_at
    _cache_fetched_at = now
    return results


def _slice_forecast(daily: dict[str, Any], start: int, end: int, term: str) -> dict[str, Any]:
    dates = daily.get("time", [])[start:end]
    precip = daily.get("precipitation_sum", [])[start:end]
    temp_max = daily.get("temperature_2m_max", [])[start:end]
    temp_min = daily.get("temperature_2m_min", [])[start:end]
    codes = daily.get("weather_code", [])[start:end]
    wind = daily.get("wind_speed_10m_max", [])[start:end]
    rain_prob = daily.get("precipitation_probability_max", [])[start:end]

    total_rain = round(sum(p or 0 for p in precip), 1)
    avg_max = round(sum(t or 0 for t in temp_max) / max(len(temp_max), 1), 1)
    avg_min = round(sum(t or 0 for t in temp_min) / max(len(temp_min), 1), 1)
    dominant_code = max(codes, key=codes.count) if codes else 0

    summary_en = (
        f"{term.replace('_', ' ').title()}: {_weather_code_label(dominant_code)}. "
        f"Temp {avg_min}°C–{avg_max}°C. Total rain {total_rain} mm over {len(dates)} days."
    )

    return {
        "term": term,
        "days": len(dates),
        "date_range": {"from": dates[0], "to": dates[-1]} if dates else None,
        "summary_en": summary_en,
        "total_rainfall_mm": total_rain,
        "avg_temp_max_c": avg_max,
        "avg_temp_min_c": avg_min,
        "dominant_weather": _weather_code_label(dominant_code),
        "max_wind_kmh": max(wind) if wind else 0,
        "max_rain_probability_pct": max(rain_prob) if rain_prob else 0,
        "daily": [
            {
                "date": dates[i],
                "weather": _weather_code_label(codes[i] if i < len(codes) else None),
                "temp_max_c": temp_max[i] if i < len(temp_max) else None,
                "temp_min_c": temp_min[i] if i < len(temp_min) else None,
                "rain_mm": precip[i] if i < len(precip) else None,
            }
            for i in range(len(dates))
        ],
    }


def get_cached_forecast(district_id: str) -> dict[str, Any] | None:
    return _forecast_cache.get(district_id)


def cache_status() -> dict[str, Any]:
    return {
        "cached_districts": len(_forecast_cache),
        "last_fetched_at": _cache_fetched_at.isoformat() if _cache_fetched_at else None,
    }
