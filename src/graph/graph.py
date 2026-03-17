"""LandGraph workflow definition for customer support email agent."""

from typing import TypedDict, Optional
from langgraph.graph import StateGraph


class EmailState(TypedDict):
    """Complete state for email processing workflow."""

    # Input fields
    email_id: str
    sender: str
    subject: str
    body: str
    metadata: dict

    # Classification results
    intent: Optional[str]
    category: Optional[str]
    priority: Optional[int]

    # Knowledge base search results
    kb_results: Optional[list]

    # Response generation
    draft_response: Optional[str]

    # Human review
    needs_human_review: bool
    human_approved: Optional[bool]
    reviewer_notes: Optional[str]

    # Final output
    final_response: Optional[str]
    sent: bool

    # Follow-up scheduling
    requires_follow_up: bool
    follow_up_date: Optional[str]

    # Error tracking
    error: Optional[str]


def route_after_draft(state: EmailState) -> str:
    """
    Conditional routing after draft response.
    Route to human_review if high priority or complaint, else to send_reply.
    """
    priority = state.get("priority", 0)
    category = state.get("category", "")

    if priority >= 4 or category == "complaint":
        return "human_review"
    return "send_reply"


def route_after_send(state: EmailState) -> str:
    """
    Conditional routing after sending reply.
    Route to followup if needed, else END.
    """
    if state.get("requires_follow_up"):
        return "followup"
    return "END"


def build_email_agent_graph():
    """
    Build the complete LandGraph workflow for email processing.

    Workflow flow:
    intake → classify → kb_search → draft_response
                                        ↓
                    (priority≥4 or complaint) → human_review → END
                                        ↓
                                  send_reply
                                        ↓
                            (requires_follow_up) → followup → END

    Returns:
        Compiled graph ready for execution
    """
    from langgraph.graph import END
    from src.graph.nodes import (
        intake_node,
        classify_node,
        kb_search_node,
        draft_response_node,
        human_review_node,
        send_reply_node,
        followup_node,
    )

    workflow = StateGraph(EmailState)

    # Add all nodes
    workflow.add_node("intake", intake_node)
    workflow.add_node("classify", classify_node)
    workflow.add_node("kb_search", kb_search_node)
    workflow.add_node("draft_response", draft_response_node)
    workflow.add_node("human_review", human_review_node)
    workflow.add_node("send_reply", send_reply_node)
    workflow.add_node("followup", followup_node)

    # Add linear edges
    workflow.add_edge("intake", "classify")
    workflow.add_edge("classify", "kb_search")
    workflow.add_edge("kb_search", "draft_response")

    # Conditional edge: after draft_response
    workflow.add_conditional_edges(
        "draft_response",
        route_after_draft,
        {"human_review": "human_review", "send_reply": "send_reply"},
    )

    # human_review ends the graph (resume via API)
    workflow.add_edge("human_review", END)

    # Conditional edge: after send_reply
    workflow.add_conditional_edges(
        "send_reply",
        route_after_send,
        {"followup": "followup", "END": END},
    )

    # Final edge
    workflow.add_edge("followup", END)

    # Set entry point
    workflow.set_entry_point("intake")

    # Compile and return
    return workflow.compile()


# Global agent graph instance
email_agent = build_email_agent_graph()
