from langgraph.graph import StateGraph, END
from app.agent.state import AgentState
from app.agent.nodes import (
    router_node,
    out_of_scope_node,
    holidays_node,
    retriever_node,
    llm_answer_node,
    should_continue,
    should_call_holidays
)

def create_agent_graph():
    """
    Creates the LangGraph StateGraph for the banking support agent.

    Flow:
    START → router → conditional:
        - out_of_scope → out_of_scope → END
        - in_scope → retriever (RAG) → conditional:
            - needs_holidays → holidays → llm_answer → END
            - no holidays → llm_answer → END
    """
    # Initialize graph
    workflow = StateGraph(AgentState)

    # Add nodes
    workflow.add_node("router", router_node)
    workflow.add_node("out_of_scope", out_of_scope_node)
    workflow.add_node("retriever", retriever_node)  # RAG retrieval
    workflow.add_node("holidays", holidays_node)
    workflow.add_node("llm_answer", llm_answer_node)

    # Define edges
    workflow.set_entry_point("router")

    # Conditional routing from router
    workflow.add_conditional_edges(
        "router",
        should_continue,
        {
            "out_of_scope": "out_of_scope",
            "retriever": "retriever"  # In-scope questions go through RAG
        }
    )

    # After out_of_scope → END
    workflow.add_edge("out_of_scope", END)

    # Conditional routing from retriever (after RAG)
    workflow.add_conditional_edges(
        "retriever",
        should_call_holidays,
        {
            "holidays": "holidays",
            "llm_answer": "llm_answer"
        }
    )

    # After holidays → llm_answer
    workflow.add_edge("holidays", "llm_answer")

    # After llm_answer → END
    workflow.add_edge("llm_answer", END)

    # Compile the graph
    return workflow.compile()

# Create the compiled graph
agent_graph = create_agent_graph()
