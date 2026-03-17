"""Classify node - classifies email intent, category, and priority."""

from src.graph.graph import EmailState


async def classify_node(state: EmailState) -> dict:
    """
    Classify node: Use LLM to classify email intent, category, and priority.

    Args:
        state: Current graph state

    Returns:
        dict: Updated state fields (intent, category, priority)
    """
    from src.services.llm_service import llm_service
    from src.services.email_service import email_service

    try:
        # Single LLM call returns all classification info
        result = await llm_service.classify_email(state["subject"], state["body"])

        intent = result.get("intent", "general_inquiry")
        category = result.get("category", "other")
        priority = result.get("priority", 3)

        # Update storage
        await email_service.update_email(state["email_id"], {
            "intent": intent,
            "category": category,
            "priority": priority,
        })

        return {
            "intent": intent,
            "category": category,
            "priority": priority,
        }

    except Exception as e:
        error_msg = f"Classification error: {str(e)}"
        print(f"[CLASSIFY ERROR] {error_msg}")
        await email_service.update_email(state["email_id"], {"error": error_msg})
        return {
            "intent": "general_inquiry",
            "category": "other",
            "priority": 3,
            "error": error_msg,
        }
