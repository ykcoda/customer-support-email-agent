"""Human review and approval routes."""

from fastapi import APIRouter, HTTPException
from src.schemas.email import ReviewAction
from src.services.review_service import review_service
from src.services.email_service import email_service
from src.graph.nodes.send_reply import send_reply_node
from src.graph.nodes.followup import followup_node

router = APIRouter(prefix="/review", tags=["review"])


@router.get("/")
async def list_pending_reviews():
    """
    List all emails pending human review.

    Returns:
        List of pending emails with key info
    """
    pending = review_service.list_pending()
    return {
        "count": len(pending),
        "emails": pending,
    }


@router.post("/{email_id}/approve")
async def approve_email(email_id: str, action: ReviewAction):
    """
    Approve a pending email for sending.
    This resumes the graph from send_reply node.

    Args:
        email_id: Email ID to approve
        action: Approval action with optional reviewer notes

    Returns:
        Approval status

    Raises:
        HTTPException: 404 if email not in review queue
    """
    # Get the stored state from review queue
    state_snapshot = review_service.dequeue(email_id)
    if not state_snapshot:
        raise HTTPException(status_code=404, detail=f"Email {email_id} not in review queue")

    try:
        # Update state with approval
        state_snapshot["human_approved"] = True
        state_snapshot["reviewer_notes"] = action.reviewer_notes
        state_snapshot["needs_human_review"] = False

        # Resume workflow by calling send_reply node directly
        print(f"[APPROVE] Resuming email {email_id} for sending...")
        result = await send_reply_node(state_snapshot)
        state_snapshot.update(result)

        # Check if follow-up is needed
        if state_snapshot.get("requires_follow_up"):
            await followup_node(state_snapshot)

        # Update email record with approval info
        await email_service.update_email(email_id, {
            "human_approved": True,
            "reviewer_notes": action.reviewer_notes,
        })

        return {
            "email_id": email_id,
            "status": "approved_and_sent",
            "message": f"Email sent to {state_snapshot.get('sender')}",
        }

    except Exception as e:
        error_msg = f"Approval error: {str(e)}"
        print(f"[APPROVE ERROR] {error_msg}")
        raise HTTPException(status_code=500, detail=error_msg)


@router.post("/{email_id}/reject")
async def reject_email(email_id: str, action: ReviewAction):
    """
    Reject a pending email (don't send).

    Args:
        email_id: Email ID to reject
        action: Rejection action with optional reviewer notes

    Returns:
        Rejection status

    Raises:
        HTTPException: 404 if email not in review queue
    """
    state_snapshot = review_service.dequeue(email_id)
    if not state_snapshot:
        raise HTTPException(status_code=404, detail=f"Email {email_id} not in review queue")

    try:
        # Mark as rejected
        await email_service.update_email(email_id, {
            "human_approved": False,
            "reviewer_notes": action.reviewer_notes,
            "status": "rejected",
        })

        print(f"[REJECT] Email {email_id} rejected by reviewer: {action.reviewer_notes}")

        return {
            "email_id": email_id,
            "status": "rejected",
            "message": f"Email rejected. Notes: {action.reviewer_notes}",
        }

    except Exception as e:
        error_msg = f"Rejection error: {str(e)}"
        print(f"[REJECT ERROR] {error_msg}")
        raise HTTPException(status_code=500, detail=error_msg)
