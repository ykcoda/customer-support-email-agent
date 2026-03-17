"""Email service for handling email operations."""

from typing import Optional, List, Dict
from datetime import datetime, timezone
from src.schemas.email import EmailRequest, EmailRecord
from src.utils.helpers import generate_email_id


class EmailService:
    """Service for email operations using in-memory storage."""

    def __init__(self):
        """Initialize email service with empty store."""
        self._store: Dict[str, EmailRecord] = {}

    async def receive_email(self, email: EmailRequest) -> tuple[str, EmailRecord]:
        """
        Receive and store a new email.

        Args:
            email: Email request object

        Returns:
            tuple: (email_id, EmailRecord)
        """
        email_id = generate_email_id()
        now = datetime.now(timezone.utc)
        record = EmailRecord(
            email_id=email_id,
            sender=str(email.sender),
            subject=email.subject,
            body=email.body,
            metadata=email.metadata or {},
            status="pending",
            created_at=now,
            updated_at=now,
        )
        self._store[email_id] = record
        return email_id, record

    async def send_email(self, recipient: str, subject: str, body: str) -> bool:
        """
        Send an email (simulated).

        Args:
            recipient: Recipient email address
            subject: Email subject
            body: Email body

        Returns:
            bool: Success status
        """
        # Simulated: in a real app this calls SMTP or SendGrid
        print(f"[EMAIL SENT] To: {recipient} | Subject: {subject} | Body length: {len(body)}")
        return True

    async def get_email(self, email_id: str) -> Optional[EmailRecord]:
        """
        Get email by ID.

        Args:
            email_id: Email ID

        Returns:
            Optional[EmailRecord]: Email record or None if not found
        """
        return self._store.get(email_id)

    async def list_emails(self) -> List[EmailRecord]:
        """
        List all emails.

        Returns:
            List[EmailRecord]: All email records
        """
        return list(self._store.values())

    async def update_email(self, email_id: str, updates: dict) -> bool:
        """
        Update email fields.

        Args:
            email_id: Email ID
            updates: Dict of fields to update

        Returns:
            bool: Success status
        """
        if email_id not in self._store:
            return False

        record = self._store[email_id]
        updated_dict = record.model_dump()
        updated_dict.update({**updates, "updated_at": datetime.now(timezone.utc)})
        self._store[email_id] = EmailRecord(**updated_dict)
        return True


email_service = EmailService()
