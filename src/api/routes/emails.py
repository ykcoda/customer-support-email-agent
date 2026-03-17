"""Email submission and status routes."""

from fastapi import APIRouter, HTTPException
from src.schemas.email import EmailRequest, EmailResponse, EmailRecord
from src.services.email_service import email_service
from src.graph.graph import email_agent

router = APIRouter(prefix="/emails", tags=["emails"])


@router.post("/", response_model=EmailResponse)
async def submit_email(request: EmailRequest):
    """
    Submit a customer support email for processing.
    Triggers the full LandGraph workflow.

    Args:
        request: Email request with sender, subject, body

    Returns:
        EmailResponse: Email ID and initial status
    """
    # Store email and get ID
    email_id, record = await email_service.receive_email(request)

    # Build initial LandGraph state
    initial_state = {
        "email_id": email_id,
        "sender": record.sender,
        "subject": record.subject,
        "body": record.body,
        "metadata": record.metadata,
        # Classification (populated by classify node)
        "intent": None,
        "category": None,
        "priority": None,
        # KB search (populated by kb_search node)
        "kb_results": None,
        # Response generation (populated by draft_response node)
        "draft_response": None,
        # Human review
        "needs_human_review": False,
        "human_approved": None,
        "reviewer_notes": None,
        # Final output
        "final_response": None,
        "sent": False,
        # Follow-up
        "requires_follow_up": False,
        "follow_up_date": None,
        # Error tracking
        "error": None,
    }

    try:
        # Run the graph asynchronously
        print(f"[SUBMIT] Processing email {email_id} through LandGraph...")
        await email_agent.ainvoke(initial_state)
        print(f"[SUBMIT] Email {email_id} processing complete")
    except Exception as e:
        error_msg = f"Graph execution error: {str(e)}"
        print(f"[SUBMIT ERROR] {error_msg}")
        await email_service.update_email(email_id, {"error": error_msg, "status": "failed"})

    # Get updated record
    updated = await email_service.get_email(email_id)

    return EmailResponse(
        email_id=email_id,
        status=updated.status,
        message=f"Email processed successfully. Status: {updated.status}",
        timestamp=updated.updated_at,
    )


@router.get("/", response_model=list[EmailRecord])
async def list_emails():
    """
    List all emails in the system.

    Returns:
        List[EmailRecord]: All email records
    """
    return await email_service.list_emails()


@router.get("/{email_id}", response_model=EmailRecord)
async def get_email(email_id: str):
    """
    Get email details by ID.

    Args:
        email_id: Email ID

    Returns:
        EmailRecord: The email record

    Raises:
        HTTPException: 404 if email not found
    """
    record = await email_service.get_email(email_id)
    if not record:
        raise HTTPException(status_code=404, detail=f"Email {email_id} not found")
    return record
