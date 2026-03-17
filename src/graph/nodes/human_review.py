"""Human review node - enqueues email for human review and ends graph."""

from src.graph.graph import EmailState


async def human_review_node(state: EmailState) -> dict:
    """
    Human review node: Flag email for human review and enqueue it.
    This node ends the current graph run. A separate API call resumes from here.

    Args:
        state: Current graph state

    Returns:
        dict: Updated state fields
    """
    from src.services.review_service import review_service
    from src.services.email_service import email_service

    try:
        # Enqueue full state snapshot for human reviewer
        review_service.enqueue(state["email_id"], dict(state))

        # Update email status
        await email_service.update_email(state["email_id"], {
            "needs_human_review": True,
            "status": "awaiting_review",
        })

        print(f"[HUMAN REVIEW] Email {state['email_id']} queued for review")

        return {"needs_human_review": True}

    except Exception as e:
        error_msg = f"Human review error: {str(e)}"
        print(f"[HUMAN REVIEW ERROR] {error_msg}")
        await email_service.update_email(state["email_id"], {"error": error_msg})
        return {"needs_human_review": False, "error": error_msg}
