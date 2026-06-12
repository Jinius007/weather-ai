"""Build normalized districts.json from raw geocoded pincode data."""
import json
import re
import uuid
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "backend" / "data" / "districts_raw.json"
OUT = ROOT / "backend" / "data" / "districts.json"

STATE_LANGUAGE = {
    "ANDHRA PRADESH": ("te", "Telugu"),
    "ARUNACHAL PRADESH": ("hi", "Hindi"),
    "ASSAM": ("as", "Assamese"),
    "BIHAR": ("hi", "Hindi"),
    "CHATTISGARH": ("hi", "Hindi"),
    "CHHATTISGARH": ("hi", "Hindi"),
    "GOA": ("mr", "Marathi"),
    "GUJARAT": ("gu", "Gujarati"),
    "HARYANA": ("hi", "Hindi"),
    "HIMACHAL PRADESH": ("hi", "Hindi"),
    "JAMMU AND KASHMIR": ("hi", "Hindi"),
    "JAMMU & KASHMIR": ("hi", "Hindi"),
    "JHARKHAND": ("hi", "Hindi"),
    "KARNATAKA": ("kn", "Kannada"),
    "KERALA": ("ml", "Malayalam"),
    "MADHYA PRADESH": ("hi", "Hindi"),
    "MAHARASHTRA": ("mr", "Marathi"),
    "MANIPUR": ("hi", "Hindi"),
    "MEGHALAYA": ("hi", "Hindi"),
    "MIZORAM": ("hi", "Hindi"),
    "NAGALAND": ("hi", "Hindi"),
    "ORISSA": ("or", "Odia"),
    "ODISHA": ("or", "Odia"),
    "PUNJAB": ("pa", "Punjabi"),
    "RAJASTHAN": ("hi", "Hindi"),
    "SIKKIM": ("hi", "Hindi"),
    "TAMIL NADU": ("ta", "Tamil"),
    "TRIPURA": ("bn", "Bengali"),
    "UTTAR PRADESH": ("hi", "Hindi"),
    "UTTARAKHAND": ("hi", "Hindi"),
    "WEST BENGAL": ("bn", "Bengali"),
    "DELHI": ("hi", "Hindi"),
    "PONDICHERRY": ("ta", "Tamil"),
    "PUDUCHERRY": ("ta", "Tamil"),
    "CHANDIGARH": ("pa", "Punjabi"),
    "ANDAMAN AND NICOBAR ISLANDS": ("hi", "Hindi"),
    "DADRA AND NAGAR HAVELI": ("gu", "Gujarati"),
    "DAMAN AND DIU": ("gu", "Gujarati"),
    "LAKSHADWEEP": ("ml", "Malayalam"),
    "LADAKH": ("hi", "Hindi"),
    "TELANGANA": ("te", "Telugu"),
}


def slugify(name: str, state: str) -> str:
    base = re.sub(r"[^a-z0-9]+", "-", f"{name}-{state}".lower()).strip("-")
    return base or str(uuid.uuid4())[:8]


def load_raw() -> dict:
    text = RAW.read_text(encoding="utf-8")
    text = re.sub(r",\s*}", "}", text)
    text = re.sub(r",\s*]", "]", text)
    return json.loads(text)


def main() -> None:
    raw = load_raw()
    districts = []
    seen = set()

    for name, info in raw.items():
        if name.startswith("_") or not isinstance(info, dict):
            continue
        state = str(info.get("State", "")).strip().upper()
        geo = info.get("GeoCode")
        if not state or not geo or len(geo) != 2:
            continue
        try:
            lat, lon = float(geo[0]), float(geo[1])
        except (TypeError, ValueError):
            continue
        if not (-90 <= lat <= 90 and -180 <= lon <= 180):
            continue

        lang_code, lang_name = STATE_LANGUAGE.get(state, ("hi", "Hindi"))
        district_id = slugify(name, state)
        if district_id in seen:
            district_id = f"{district_id}-{len(seen)}"
        seen.add(district_id)

        districts.append(
            {
                "id": district_id,
                "name": name,
                "state": state.title(),
                "latitude": round(lat, 4),
                "longitude": round(lon, 4),
                "language_code": lang_code,
                "language_name": lang_name,
            }
        )

    districts.sort(key=lambda d: (d["state"], d["name"]))
    OUT.write_text(json.dumps(districts, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Wrote {len(districts)} districts to {OUT}")


if __name__ == "__main__":
    main()
