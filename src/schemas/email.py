"""Email data models for customer support agent."""

from pydantic import BaseModel, Field, EmailStr
from typing import Optional, List
from datetime import datetime


class EmailRequest(BaseModel):
    """Email submission request."""

    sender: EmailStr = Field(..., description="Sender email address")
    subject: str = Field(..., min_length=1, max_length=255)
    body: str = Field(..., min_length=1, max_length=10000)
    metadata: Optional[dict] = Field(default_factory=dict, description="Additional metadata")


class EmailResponse(BaseModel):
    """Email submission response."""

    email_id: str
    status: str
    message: str
    timestamp: datetime


class ClassificationResult(BaseModel):
    """Result of email classification."""

    intent: str = Field(description="Email intent type")
    category: str = Field(description="Email category (complaint, question, feedback, request, other)")
    priority: int = Field(ge=1, le=5, description="Priority level 1-5")


class ReviewAction(BaseModel):
    """Action taken by human reviewer."""

    approved: bool
    reviewer_notes: Optional[str] = None


class FollowUpRecord(BaseModel):
    """Scheduled follow-up record."""

    email_id: str
    follow_up_date: datetime
    reason: str
    created_at: datetime


class EmailRecord(BaseModel):
    """Complete email record stored in system."""

    email_id: str
    sender: str
    subject: str
    body: str
    metadata: dict = Field(default_factory=dict)

    # Classification results
    intent: Optional[str] = None
    category: Optional[str] = None
    priority: Optional[int] = None

    # KB search results
    kb_results: Optional[List[dict]] = None

    # Response generation
    draft_response: Optional[str] = None

    # Human review
    needs_human_review: bool = False
    human_approved: Optional[bool] = None
    reviewer_notes: Optional[str] = None

    # Final output
    final_response: Optional[str] = None
    sent: bool = False

    # Follow-up
    requires_follow_up: bool = False
    follow_up_date: Optional[datetime] = None

    # Status tracking
    status: str = Field(default="pending", description="pending|processing|awaiting_review|completed|failed")
    error: Optional[str] = None

    created_at: datetime
    updated_at: datetime
    received_at: Optional[datetime] = None

    class Config:
        """Pydantic config."""
        populate_by_name = True
