from __future__ import annotations

from typing import Any


def build_advisories(forecast_slice: dict[str, Any]) -> dict[str, dict[str, str]]:
    rain = forecast_slice.get("total_rainfall_mm", 0) or 0
    t_max = forecast_slice.get("avg_temp_max_c", 30) or 30
    t_min = forecast_slice.get("avg_temp_min_c", 20) or 20
    wind = forecast_slice.get("max_wind_kmh", 0) or 0
    rain_prob = forecast_slice.get("max_rain_probability_pct", 0) or 0
    weather = (forecast_slice.get("dominant_weather") or "").lower()

    advisories: dict[str, dict[str, str]] = {}

    # Sowing
    if rain >= 15 and t_max <= 38 and "heavy" not in weather and "thunder" not in weather:
        level, msg = "good", "Soil moisture is improving. Good window for sowing if seeds are ready."
    elif rain >= 40 or "heavy" in weather or "thunder" in weather:
        level, msg = "avoid", "Heavy rain or storms expected. Delay sowing until fields drain."
    elif rain < 3 and t_max > 36:
        level, msg = "caution", "Dry and hot spell. Pre-sow only with assured irrigation."
    else:
        level, msg = "neutral", "Weather is mixed. Sow only where irrigation backup is available."

    advisories["sowing"] = {"level": level, "message_en": msg}

    # Fertilizer
    if rain >= 25 or rain_prob >= 70:
        level, msg = "avoid", "Heavy rain may wash away fertilizer. Apply after rain passes."
    elif rain < 5 and 20 <= t_max <= 34:
        level, msg = "good", "Stable weather. Suitable for top-dressing fertilizer in moist soil."
    elif t_max > 38:
        level, msg = "caution", "High heat stress. Avoid urea application during peak afternoon heat."
    else:
        level, msg = "neutral", "Apply fertilizer in evening hours and irrigate lightly if no rain."

    advisories["fertilizer"] = {"level": level, "message_en": msg}

    # Harvest
    if rain < 5 and wind < 30 and t_max < 40:
        level, msg = "good", "Dry weather supports harvesting and field drying of grains."
    elif rain >= 10 or "rain" in weather or "drizzle" in weather:
        level, msg = "avoid", "Rain may damage cut crop and increase moisture in grain. Delay harvest."
    elif wind >= 40:
        level, msg = "caution", "Strong winds may cause lodging. Harvest standing crop first."
    else:
        level, msg = "neutral", "Monitor daily weather before starting harvest operations."

    advisories["harvest"] = {"level": level, "message_en": msg}

    # Irrigation
    if rain >= 20:
        level, msg = "good", "Rainfall likely to meet crop water need. Reduce irrigation to save water."
    elif rain < 5 and t_max > 32:
        level, msg = "urgent", "Hot and dry period. Plan irrigation early morning or evening."
    elif rain < 8 and t_min > 24:
        level, msg = "caution", "Low rainfall with warm nights. Maintain soil moisture for root crops."
    else:
        level, msg = "neutral", "Irrigate based on soil moisture; light rain may not be enough."

    advisories["irrigation"] = {"level": level, "message_en": msg}

    return advisories


def enrich_forecast_with_advisories(forecast_entry: dict[str, Any]) -> dict[str, Any]:
    enriched = dict(forecast_entry)
    enriched_forecasts = {}

    for term, slice_data in forecast_entry.get("forecasts", {}).items():
        slice_copy = dict(slice_data)
        slice_copy["advisories"] = build_advisories(slice_data)
        enriched_forecasts[term] = slice_copy

    enriched["forecasts"] = enriched_forecasts
    return enriched
