"""Intake node - validates and marks email as processing."""

from src.graph.graph import EmailState


async def intake_node(state: EmailState) -> dict:
    """
    Intake node: Validate email and mark as processing.

    Args:
        state: Current graph state

    Returns:
        dict: Updated state fields
    """
    from src.services.email_service import email_service

    email_id = state.get("email_id")

    # Mark email as processing in storage
    await email_service.update_email(email_id, {"status": "processing"})

    return {"email_id": email_id}
