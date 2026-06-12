from __future__ import annotations

import asyncio
from typing import Any

import httpx
from fastapi import FastAPI, HTTPException, Query, Request, Response
from fastapi.middleware.cors import CORSMiddleware

from services.advisory import enrich_forecast_with_advisories
from services.farmer_brief import fetch_local_farmer_brief, fetch_local_farmer_brief_from_ip
from services.translation import translate_forecast_entry
from services.weather import (
    BATCH_SIZE,
    cache_status,
    fetch_weather_for_districts,
    get_cached_forecast,
    get_district_by_id,
    load_districts,
)

app = FastAPI(title="Krishi Mausam AI", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

_refresh_lock = asyncio.Lock()


@app.get("/api/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/api/stats")
async def stats() -> dict[str, Any]:
    districts = load_districts()
    states = sorted({d["state"] for d in districts})
    languages = sorted({d["language_name"] for d in districts})
    return {
        "total_districts": len(districts),
        "total_states": len(states),
        "languages": languages,
        "cache": cache_status(),
    }


@app.get("/api/districts")
async def list_districts(
    state: str | None = None,
    search: str | None = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=200),
) -> dict[str, Any]:
    districts = load_districts()
    if state:
        districts = [d for d in districts if d["state"].lower() == state.lower()]
    if search:
        q = search.lower()
        districts = [d for d in districts if q in d["name"].lower() or q in d["state"].lower()]

    total = len(districts)
    start = (page - 1) * page_size
    end = start + page_size
    page_items = districts[start:end]

    return {
        "total": total,
        "page": page,
        "page_size": page_size,
        "items": page_items,
    }


@app.get("/api/states")
async def list_states() -> list[str]:
    return sorted({d["state"] for d in load_districts()})


def _no_cache_headers() -> dict[str, str]:
    return {
        "Cache-Control": "no-store, no-cache, must-revalidate, max-age=0",
        "Pragma": "no-cache",
    }


def _client_ip(request: Request) -> str | None:
    forwarded = request.headers.get("x-forwarded-for")
    if forwarded:
        return forwarded.split(",")[0].strip()
    if request.client:
        return request.client.host
    return None


@app.get("/api/local-forecast")
async def local_forecast(
    request: Request,
    response: Response,
    lat: float | None = Query(None, ge=-90, le=90),
    lon: float | None = Query(None, ge=-180, le=180),
) -> dict[str, Any]:
    for key, value in _no_cache_headers().items():
        response.headers[key] = value

    try:
        if lat is not None and lon is not None:
            return await fetch_local_farmer_brief(lat, lon, location_method="gps")
        return await fetch_local_farmer_brief_from_ip(_client_ip(request))
    except httpx.HTTPError as exc:
        raise HTTPException(status_code=502, detail="Weather service unavailable") from exc
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@app.get("/api/forecasts/{district_id}")
async def get_forecast(district_id: str, refresh: bool = False) -> dict[str, Any]:
    district = get_district_by_id(district_id)
    if not district:
        raise HTTPException(status_code=404, detail="District not found")

    cached = get_cached_forecast(district_id)
    if cached and not refresh:
        return translate_forecast_entry(enrich_forecast_with_advisories(cached))

    results = await fetch_weather_for_districts([district])
    if not results:
        raise HTTPException(status_code=502, detail="Weather service unavailable")

    return translate_forecast_entry(enrich_forecast_with_advisories(results[0]))


@app.post("/api/forecasts/refresh")
async def refresh_forecasts(
    state: str | None = None,
    limit: int = Query(100, ge=1, le=500),
) -> dict[str, Any]:
    async with _refresh_lock:
        districts = load_districts()
        if state:
            districts = [d for d in districts if d["state"].lower() == state.lower()]
        districts = districts[:limit]

        refreshed = 0
        for i in range(0, len(districts), BATCH_SIZE):
            batch = districts[i : i + BATCH_SIZE]
            batch_results = await fetch_weather_for_districts(batch)
            refreshed += len(batch_results)
            await asyncio.sleep(0.3)

        return {
            "refreshed": refreshed,
            "requested": len(districts),
            "cache": cache_status(),
        }


@app.get("/api/forecasts")
async def list_forecasts(
    state: str | None = None,
    term: str | None = Query(None, pattern="^(short_term|medium_term|long_term)$"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    refresh_missing: bool = True,
) -> dict[str, Any]:
    districts = load_districts()
    if state:
        districts = [d for d in districts if d["state"].lower() == state.lower()]

    total = len(districts)
    start = (page - 1) * page_size
    page_districts = districts[start : start + page_size]

    missing = [d for d in page_districts if not get_cached_forecast(d["id"])]
    if refresh_missing and missing:
        for i in range(0, len(missing), BATCH_SIZE):
            await fetch_weather_for_districts(missing[i : i + BATCH_SIZE])
            await asyncio.sleep(0.2)

    items = []
    for district in page_districts:
        cached = get_cached_forecast(district["id"])
        if not cached:
            continue
        enriched = translate_forecast_entry(enrich_forecast_with_advisories(cached))
        if term:
            enriched["active_term"] = term
            enriched["active_forecast"] = enriched["forecasts"].get(term)
        items.append(enriched)

    return {
        "total": total,
        "page": page,
        "page_size": page_size,
        "items": items,
        "cache": cache_status(),
    }


@app.post("/api/sms/preview/{district_id}")
async def sms_preview(district_id: str, term: str = "short_term") -> dict[str, Any]:
    forecast = await get_forecast(district_id)
    active = forecast["forecasts"].get(term)
    if not active:
        raise HTTPException(status_code=400, detail="Invalid forecast term")

    advisories = active.get("advisories", {})
    sms_body = active.get("message_local", "")
    for key in ("sowing", "fertilizer", "harvest", "irrigation"):
        adv = advisories.get(key, {})
        if adv.get("message_local"):
            sms_body += f"\n• {adv['message_local']}"

    farmer_groups = [
        f"{forecast['district_name']} Kisan Samiti",
        f"{forecast['state']} Krishi SMS Group",
        "District Agriculture Officer List",
    ]

    return {
        "district_id": district_id,
        "district_name": forecast["district_name"],
        "state": forecast["state"],
        "language": forecast["language_name"],
        "term": term,
        "source": forecast["source"],
        "updated_at": forecast["updated_at"],
        "sms_body": sms_body,
        "character_count": len(sms_body),
        "farmer_groups": farmer_groups,
        "status": "preview_only",
        "message": "SMS integration not connected. This shows what would be sent.",
    }
