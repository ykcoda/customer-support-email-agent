"""Draft response node - generates response using LLM and KB context."""

from src.graph.graph import EmailState


async def draft_response_node(state: EmailState) -> dict:
    """
    Draft response node: Generate response using LLM with KB context.

    Args:
        state: Current graph state

    Returns:
        dict: Updated state fields (draft_response, requires_follow_up)
    """
    from src.services.llm_service import llm_service
    from src.services.email_service import email_service

    try:
        # Build context from KB results
        kb_results = state.get("kb_results") or []
        context_parts = []

        for entry in kb_results[:3]:  # Use top 3 KB articles
            question = entry.get("question") or entry.get("title", "")
            answer = entry.get("answer") or entry.get("content", "")
            if question or answer:
                context_parts.append(f"Q: {question}\nA: {answer}")

        context = "\n\n".join(context_parts) if context_parts else "No specific KB articles found."

        # Generate response using LLM
        draft = await llm_service.generate_response(
            subject=state["subject"],
            body=state["body"],
            category=state.get("category", "other"),
            context=context,
        )

        # Determine if follow-up is needed based on category
        # Complaints and requests typically need follow-up
        requires_follow_up = state.get("category") in ("complaint", "request")

        # Update storage
        await email_service.update_email(state["email_id"], {
            "draft_response": draft,
            "requires_follow_up": requires_follow_up,
        })

        return {
            "draft_response": draft,
            "requires_follow_up": requires_follow_up,
            "needs_human_review": False,  # Default; may be overridden by routing
        }

    except Exception as e:
        error_msg = f"Response generation error: {str(e)}"
        print(f"[DRAFT RESPONSE ERROR] {error_msg}")
        await email_service.update_email(state["email_id"], {"error": error_msg})
        return {
            "draft_response": f"Thank you for your email. We'll get back to you shortly.",
            "requires_follow_up": False,
            "error": error_msg,
        }
