from langgraph.graph import StateGraph, END
from app.agent.state import AgentState
from app.agent.nodes import (
    router_node,
    out_of_scope_node,
    holidays_node,
    llm_answer_node,
    should_continue
)

def create_agent_graph():
    """
    Creates the LangGraph StateGraph for the banking support agent.

    Flow:
    START → router → (out_of_scope | holidays → llm_answer | llm_answer) → END
    """
    # Initialize graph
    workflow = StateGraph(AgentState)

    # Add nodes
    workflow.add_node("router", router_node)
    workflow.add_node("out_of_scope", out_of_scope_node)
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
            "holidays": "holidays",
            "llm_answer": "llm_answer"
        }
    )

    # After out_of_scope → END
    workflow.add_edge("out_of_scope", END)

    # After holidays → llm_answer
    workflow.add_edge("holidays", "llm_answer")

    # After llm_answer → END
    workflow.add_edge("llm_answer", END)

    # Compile the graph
    return workflow.compile()

# Create the compiled graph
agent_graph = create_agent_graph()
