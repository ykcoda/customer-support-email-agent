"""Send reply node - sends the final response email."""

from src.graph.graph import EmailState


async def send_reply_node(state: EmailState) -> dict:
    """
    Send reply node: Send the final response email to the customer.

    Args:
        state: Current graph state

    Returns:
        dict: Updated state fields (final_response, sent)
    """
    from src.services.email_service import email_service

    try:
        # Use draft response as final response
        final_response = state.get("draft_response") or "Thank you for reaching out. We appreciate your message."

        # Send email (simulated)
        success = await email_service.send_email(
            recipient=state["sender"],
            subject=f"Re: {state['subject']}",
            body=final_response,
        )

        # Update email record
        status = "completed" if success else "failed"
        await email_service.update_email(state["email_id"], {
            "final_response": final_response,
            "sent": success,
            "status": status,
        })

        return {
            "final_response": final_response,
            "sent": success,
        }

    except Exception as e:
        error_msg = f"Send reply error: {str(e)}"
        print(f"[SEND REPLY ERROR] {error_msg}")
        await email_service.update_email(state["email_id"], {
            "error": error_msg,
            "status": "failed",
        })
        return {
            "final_response": state.get("draft_response") or "Error sending response.",
            "sent": False,
            "error": error_msg,
        }
