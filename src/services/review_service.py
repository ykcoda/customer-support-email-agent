"""Service for managing human review queue."""

from typing import Dict, List, Optional


class ReviewService:
    """In-memory queue for emails awaiting human review."""

    def __init__(self):
        """Initialize review service."""
        self._queue: Dict[str, dict] = {}

    def enqueue(self, email_id: str, state_snapshot: dict) -> None:
        """
        Enqueue email for human review.

        Args:
            email_id: Email ID
            state_snapshot: Full state snapshot from LandGraph
        """
        self._queue[email_id] = state_snapshot

    def dequeue(self, email_id: str) -> Optional[dict]:
        """
        Dequeue email from review.

        Args:
            email_id: Email ID

        Returns:
            Optional[dict]: State snapshot or None if not found
        """
        return self._queue.pop(email_id, None)

    def list_pending(self) -> List[dict]:
        """
        List all emails pending review.

        Returns:
            List[dict]: All pending emails with metadata
        """
        return [
            {
                "email_id": email_id,
                "subject": state.get("subject"),
                "sender": state.get("sender"),
                "priority": state.get("priority"),
                "category": state.get("category"),
                "draft_response": state.get("draft_response"),
            }
            for email_id, state in self._queue.items()
        ]

    def is_pending(self, email_id: str) -> bool:
        """
        Check if email is pending review.

        Args:
            email_id: Email ID

        Returns:
            bool: True if pending
        """
        return email_id in self._queue


review_service = ReviewService()
