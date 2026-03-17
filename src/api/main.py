"""FastAPI application entry point."""

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pathlib import Path
from src.core import settings
from src.api.routes import emails_router, review_router, followups_router

app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    debug=settings.debug,
)

# Mount routers with /api prefix
app.include_router(emails_router, prefix="/api")
app.include_router(review_router, prefix="/api")
app.include_router(followups_router, prefix="/api")

# Mount static files
static_dir = Path(__file__).parent.parent / "static"
if static_dir.exists():
    app.mount("/static", StaticFiles(directory=static_dir), name="static")


@app.get("/")
async def root():
    """Root endpoint - serve dashboard."""
    dashboard_path = Path(__file__).parent.parent / "templates" / "dashboard.html"
    if dashboard_path.exists():
        return FileResponse(dashboard_path)
    return {
        "message": "Customer Support Email Agent API",
        "version": settings.app_version,
        "status": "running",
        "docs": "/docs",
        "openapi": "/openapi.json",
    }


@app.get("/health")
async def health():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "app": settings.app_name,
        "version": settings.app_version,
    }
