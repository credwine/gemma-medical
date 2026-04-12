"""Gemma Medical -- Privacy-First Medical AI for Community Health Workers.

Powered by Gemma 4 running locally via Ollama. No data ever leaves your device.
"""

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pathlib import Path

from backend.routers import assistant, clinic, drugs, maternal, medtranslate
from backend.routers import patients, visits, medications, analytics
from backend.routers import referrals, qrcode, formulary, queue
from backend.ollama_client import check_model

app = FastAPI(
    title="Gemma Medical",
    description="Privacy-first medical AI for community health workers in developing countries",
    version="1.0.0",
)

# Mount frontend static files
FRONTEND_DIR = Path(__file__).parent.parent / "frontend"
app.mount("/css", StaticFiles(directory=FRONTEND_DIR / "css"), name="css")
app.mount("/js", StaticFiles(directory=FRONTEND_DIR / "js"), name="js")
app.mount("/assets", StaticFiles(directory=FRONTEND_DIR / "assets"), name="assets")

# Register API routers
app.include_router(assistant.router)
app.include_router(clinic.router)
app.include_router(drugs.router)
app.include_router(maternal.router)
app.include_router(medtranslate.router)

# EMR/EHR module routers
app.include_router(patients.router)
app.include_router(visits.router)
app.include_router(medications.router)
app.include_router(analytics.router)

# Clinical tools
app.include_router(referrals.router)
app.include_router(qrcode.router)
app.include_router(formulary.router)
app.include_router(queue.router)


@app.get("/manifest.json")
async def serve_manifest():
    """Serve PWA manifest from root path."""
    return FileResponse(FRONTEND_DIR / "manifest.json", media_type="application/manifest+json")


@app.get("/sw.js")
async def serve_sw():
    """Serve service worker from root path (required for proper scope)."""
    return FileResponse(FRONTEND_DIR / "sw.js", media_type="application/javascript")


@app.get("/favicon.ico")
async def serve_favicon():
    """Serve favicon."""
    icon = FRONTEND_DIR / "assets" / "icon-192.svg"
    if icon.exists():
        return FileResponse(icon, media_type="image/svg+xml")
    return FileResponse(FRONTEND_DIR / "assets" / "icon-192.svg")


@app.get("/")
async def serve_index():
    """Serve the main application page."""
    return FileResponse(FRONTEND_DIR / "index.html")


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    model_status = await check_model()
    return {
        "status": "ok" if model_status["gemma4_ready"] else "degraded",
        "gemma_medical_version": "1.0.0",
        "model_status": model_status,
    }
