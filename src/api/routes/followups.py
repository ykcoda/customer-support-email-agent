"""Follow-up management routes."""

from fastapi import APIRouter
from datetime import datetime

router = APIRouter(prefix="/followups", tags=["followups"])


@router.get("/")
async def list_followups():
    """
    List all scheduled follow-ups.

    Returns:
        List of follow-up records
    """
    from src.services.followup_service import followup_service

    all_followups = followup_service.list_all()
    due = followup_service.list_due(datetime.utcnow())

    return {
        "total": len(all_followups),
        "due_count": len(due),
        "all_followups": [f.model_dump() for f in all_followups],
        "due_followups": [f.model_dump() for f in due],
    }
