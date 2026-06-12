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

## Deploy on Vercel (frontend)

1. Push this repo to GitHub (see below).
2. In [Vercel](https://vercel.com), import the repository.
3. Set **Root Directory** to `frontend`.
4. Build settings (auto-detected): `npm run build`, output `dist`.
5. Deploy the **backend** separately (Render, Railway, Fly.io, etc.) and expose it over HTTPS.
6. In Vercel → Project → Settings → Environment Variables, add:
   - `VITE_API_BASE` = your backend URL (e.g. `https://krishi-mausam-api.onrender.com`) — no trailing slash.

The frontend calls `${VITE_API_BASE}/api/...` in production. Local dev uses the Vite proxy when `VITE_API_BASE` is empty.

### Backend on Render (example)

- Root directory: `backend`
- Build: `pip install -r requirements.txt`
- Start: `uvicorn main:app --host 0.0.0.0 --port $PORT`
- Ensure `districts.json` exists (run `python scripts/build_districts.py` once locally and commit, or add a build step).

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
