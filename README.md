# Krishi Mausam AI

Farmer-focused weather alert dashboard for **all districts in India**. Pulls open-source forecasts, translates them into the local language of each district, and adds simple advisories for sowing, fertilizer, harvest, and irrigation.

## Features

- **All India districts** with coordinates and state-wise local language mapping
- **Short / medium / long term** forecasts (1–3, 4–7, 8–16 days)
- **Open-Meteo only** for live district forecasts (free, open-source, no API key)
- **Farmer advisories** in plain language with sowing, fertilizer, harvest, irrigation warnings
- **SMS blast preview** button per district (integration placeholder)
- Filter by state, search districts, paginated browsing
- **Read aloud** on each card (browser text-to-speech in the district’s local language)

## Quick start

### 1. Build district data

```powershell
cd "d:\work\Innovations\Weather AI"
python scripts/build_districts.py
```

### 2. Backend

```powershell
cd backend
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```

### 3. Frontend

```powershell
cd frontend
npm install
npm run dev
```

Open **http://localhost:5173**

## Deploy on Vercel (frontend + API)

This repo is configured for a **single Vercel project** — React frontend and FastAPI backend (via serverless function).

1. Import [github.com/Jinius007/weather-ai](https://github.com/Jinius007/weather-ai) on Vercel.
2. Leave **Root Directory** empty (repo root). Vercel reads `vercel.json` at the root.
3. Deploy. No `VITE_API_BASE` is needed — the UI calls `/api/...` on the same domain.

Optional: set `VITE_API_BASE` only if the API is hosted on a different domain.

### Local production preview

```powershell
cd frontend
npm install
npm run build
npx vercel dev
```
## API overview

| Endpoint | Description |
|----------|-------------|
| `GET /api/stats` | District counts and cache status |
| `GET /api/districts` | Paginated district list |
| `GET /api/forecasts` | Paginated forecasts with advisories |
| `POST /api/forecasts/refresh` | Batch refresh from Open-Meteo |
| `POST /api/sms/preview/{district_id}` | SMS message preview |

## Planned integrations

- Real SMS gateway (MSG91, Twilio, government Kisan SMS channels)

## Data sources

- District geocodes: [Indian District GeoCoded Pin Code Data](https://gist.github.com/VinayaSathyanarayana/7d4e61430936e2fa08388465fd46cb98)
- Weather: [Open-Meteo](https://open-meteo.com/) (CC BY 4.0)
