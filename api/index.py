import sys
from pathlib import Path

# Vercel runs this file from /api; add backend package to import path.
BACKEND_DIR = Path(__file__).resolve().parents[1] / "backend"
sys.path.insert(0, str(BACKEND_DIR))

from mangum import Mangum  # noqa: E402

from main import app  # noqa: E402

handler = Mangum(app, lifespan="off")
