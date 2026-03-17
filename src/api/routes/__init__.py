"""API routes for customer support email agent."""

from .emails import router as emails_router
from .review import router as review_router
from .followups import router as followups_router

__all__ = ["emails_router", "review_router", "followups_router"]
