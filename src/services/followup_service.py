"""Service for managing follow-up scheduling."""

from typing import List
from datetime import datetime
from src.schemas.email import FollowUpRecord


class FollowUpService:
    """In-memory list for scheduled follow-ups."""

    def __init__(self):
        """Initialize followup service."""
        self._followups: List[FollowUpRecord] = []

    def schedule(self, email_id: str, follow_up_date: datetime, reason: str) -> FollowUpRecord:
        """
        Schedule a follow-up.

        Args:
            email_id: Email ID
            follow_up_date: When to follow up
            reason: Reason for follow-up

        Returns:
            FollowUpRecord: Created follow-up record
        """
        record = FollowUpRecord(
            email_id=email_id,
            follow_up_date=follow_up_date,
            reason=reason,
            created_at=datetime.utcnow(),
        )
        self._followups.append(record)
        return record

    def list_all(self) -> List[FollowUpRecord]:
        """
        List all scheduled follow-ups.

        Returns:
            List[FollowUpRecord]: All follow-up records
        """
        return self._followups

    def list_due(self, as_of: datetime) -> List[FollowUpRecord]:
        """
        List follow-ups that are due.

        Args:
            as_of: Reference date/time

        Returns:
            List[FollowUpRecord]: Due follow-ups
        """
        return [f for f in self._followups if f.follow_up_date <= as_of]


followup_service = FollowUpService()
