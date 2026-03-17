"""KB search node - searches knowledge base for relevant documents."""

from src.graph.graph import EmailState


async def kb_search_node(state: EmailState) -> dict:
    """
    KB search node: Perform keyword search against knowledge base.

    Args:
        state: Current graph state

    Returns:
        dict: Updated state fields (kb_results)
    """
    from src.services.storage_service import storage_service
    from src.services.email_service import email_service
    from src.utils.helpers import truncate_text

    try:
        # Build query from subject and body
        query = f"{state['subject']} {truncate_text(state['body'], 300)}"

        # Search knowledge base
        results = await storage_service.search_knowledge_base(query)

        # Update storage
        await email_service.update_email(state["email_id"], {"kb_results": results})

        return {"kb_results": results}

    except Exception as e:
        error_msg = f"KB search error: {str(e)}"
        print(f"[KB SEARCH ERROR] {error_msg}")
        await email_service.update_email(state["email_id"], {"error": error_msg})
        return {"kb_results": [], "error": error_msg}
