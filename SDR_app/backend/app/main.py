"""Main FastAPI application for SDR_app."""
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pathlib import Path
import logging.config
import os

# Configure logging
logging_conf_path = Path(__file__).parent.parent / "logging.ini"
if logging_conf_path.exists():
    logging.config.fileConfig(logging_conf_path, disable_existing_loggers=False)

logger = logging.getLogger("uvicorn")

# Import routes
from backend.app.routes import status, scanner, recordings
from backend.app.config import API_TITLE, API_VERSION, API_DESCRIPTION, STATIC_DIR

# Create FastAPI app
app = FastAPI(
    title=API_TITLE,
    version=API_VERSION,
    description=API_DESCRIPTION
)

# Include routers
app.include_router(status.router)
app.include_router(scanner.router)
app.include_router(recordings.router)

# Mount static files if they exist (React build)
if STATIC_DIR.exists():
    app.mount("/assets", StaticFiles(directory=str(STATIC_DIR / "assets")), name="assets")
    logger.info(f"Mounted static files from {STATIC_DIR}")

@app.get("/")
async def root():
    """Serve React app or API info."""
    index_path = STATIC_DIR / "index.html"
    if index_path.exists():
        return FileResponse(index_path)
    else:
        return {
            "app": "SDR_app",
            "version": API_VERSION,
            "message": "React frontend not built yet. Access API docs at /docs"
        }

@app.get("/health")
async def health():
    """Health check endpoint."""
    return {"status": "healthy"}

@app.on_event("startup")
async def startup_event():
    """Application startup."""
    logger.info(f"Starting {API_TITLE} v{API_VERSION}")
    logger.info("Scanner engine initialized")

@app.on_event("shutdown")
async def shutdown_event():
    """Application shutdown."""
    from backend.app.scanner.engine import scanner_engine
    if scanner_engine.is_running():
        logger.info("Stopping scanner...")
        await scanner_engine.stop_scan()
    logger.info("Application shutdown complete")
