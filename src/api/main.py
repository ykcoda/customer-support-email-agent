"""FastAPI application entry point."""

from fastapi import FastAPI
from src.core import settings
from src.api.routes import emails_router, review_router, followups_router

app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    debug=settings.debug,
)

# Mount routers
app.include_router(emails_router)
app.include_router(review_router)
app.include_router(followups_router)


@app.get("/")
async def root():
    """Root endpoint."""
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
