"""Followup node - schedules follow-up for the email."""

from datetime import datetime, timedelta
from src.graph.graph import EmailState


async def followup_node(state: EmailState) -> dict:
    """
    Followup node: Schedule a follow-up for this email.

    Args:
        state: Current graph state

    Returns:
        dict: Updated state fields (follow_up_date)
    """
    from src.services.followup_service import followup_service

    try:
        # Determine follow-up date
        follow_up_date_str = state.get("follow_up_date")
        if follow_up_date_str:
            follow_up_date = datetime.fromisoformat(follow_up_date_str)
        else:
            # Default: 3 days from now for complaints, 7 days for requests
            if state.get("category") == "complaint":
                follow_up_date = datetime.utcnow() + timedelta(days=3)
            else:
                follow_up_date = datetime.utcnow() + timedelta(days=7)

        # Schedule follow-up
        reason = f"Category: {state.get('category')}, Priority: {state.get('priority')}"
        followup_service.schedule(
            email_id=state["email_id"],
            follow_up_date=follow_up_date,
            reason=reason,
        )

        print(f"[FOLLOWUP] Email {state['email_id']} scheduled for {follow_up_date.isoformat()}")

        return {"follow_up_date": follow_up_date.isoformat()}

    except Exception as e:
        error_msg = f"Followup scheduling error: {str(e)}"
        print(f"[FOLLOWUP ERROR] {error_msg}")
        return {"error": error_msg}
