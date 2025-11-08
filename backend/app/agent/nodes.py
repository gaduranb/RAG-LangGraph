from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage
from app.agent.state import AgentState
from app.agent.prompts import SYSTEM_PROMPT, ROUTER_PROMPT
from app.tools.holidays import is_federal_holiday
from app.rag.retriever import retrieve_documents, format_retrieved_docs
from app.config import get_settings
import json

settings = get_settings()

# Initialize LLM
llm = ChatOpenAI(
    model=settings.openai_model,
    api_key=settings.openai_api_key,
    temperature=0.7
)

async def router_node(state: AgentState) -> AgentState:
    """
    Routes the question to determine:
    - If it's about login/security
    - If it needs holiday information
    """
    question = state["question"]
    question_lower = question.lower()

    # Simple keyword-based routing (reliable and fast)
    login_security_keywords = [
        "password", "login", "username", "account", "security", "verification",
        "code", "2fa", "mfa", "two-factor", "lockout", "locked", "reset",
        "forgot", "recover", "authentication", "device", "recognize", "verify"
    ]

    holiday_keywords = [
        "holiday", "festivo", "business day", "timing", "when", "hours",
        "business hours", "weekend", "saturday", "sunday"
    ]

    # Check if it's about login/security
    is_login_security = any(keyword in question_lower for keyword in login_security_keywords)

    # Check if it mentions holidays/timing
    needs_holidays = any(keyword in question_lower for keyword in holiday_keywords)

    # If no keywords match, assume it's login/security (benefit of doubt)
    if not is_login_security and not needs_holidays:
        is_login_security = True

    # In-scope if either login/security OR holidays
    is_in_scope = is_login_security or needs_holidays

    print(f"[Router] Question: {question}")
    print(f"[Router] is_login_security: {is_login_security}, needs_holidays: {needs_holidays}, is_in_scope: {is_in_scope}")

    return {
        **state,
        "is_out_of_scope": not is_in_scope,
        "needs_holidays": needs_holidays
    }

async def out_of_scope_node(state: AgentState) -> AgentState:
    """Handles questions outside of login/security scope."""
    answer = (
        "Thanks for your question! While I'm trained to help with login and security topics, "
        "this might be outside my current expertise. Please contact our support team for "
        "personalized assistance—they're here to help 24/7."
    )

    return {
        **state,
        "answer": answer,
        "citations": [{"title": "Contact Support", "url": "#"}],
        "tool_calls": []
    }

async def holidays_node(state: AgentState) -> AgentState:
    """Calls the federal holidays API."""
    holiday_info = await is_federal_holiday()

    state["tool_calls"] = state.get("tool_calls", []) + ["federal_holidays_api"]
    state["messages"] = state.get("messages", []) + [
        SystemMessage(content=f"Holiday Information: {json.dumps(holiday_info)}")
    ]

    return state

async def retriever_node(state: AgentState) -> AgentState:
    """
    Retrieves relevant documents from the vector database.
    """
    question = state["question"]

    try:
        # Retrieve top 3 most relevant documents
        docs = retrieve_documents(question, k=3)

        # Format documents
        formatted_docs = format_retrieved_docs(docs)

        # Extract citations from documents
        citations = []
        seen_sources = set()
        for doc in docs:
            source = doc.metadata.get("source", "Unknown")
            page = doc.metadata.get("page", 0)

            if source not in seen_sources:
                citations.append({
                    "title": f"{source} (Page {page + 1})",
                    "url": "#"
                })
                seen_sources.add(source)

        print(f"[RAG] Retrieved {len(docs)} documents")
        print(f"[RAG] Citations: {citations}")

        return {
            **state,
            "retrieved_docs": formatted_docs,
            "citations": citations
        }

    except FileNotFoundError as e:
        print(f"[RAG] Warning: {e}")
        return {
            **state,
            "retrieved_docs": None,
            "citations": [{"title": "Banking Security Guide", "url": "#"}]
        }

async def llm_answer_node(state: AgentState) -> AgentState:
    """
    Generates the final answer using the LLM with RAG context.
    The LLM will provide warm, helpful responses based on retrieved documents.
    """
    question = state["question"]

    # Build messages for LLM
    messages = [SystemMessage(content=SYSTEM_PROMPT)]

    # Add RAG context if available
    if state.get("retrieved_docs"):
        rag_context = (
            f"Use the following documents from our knowledge base to answer the question. "
            f"Cite specific information when relevant:\n\n"
            f"{state['retrieved_docs']}\n\n"
            f"Question: {question}"
        )
        messages.append(HumanMessage(content=rag_context))
    else:
        messages.append(HumanMessage(content=question))

    # Add holiday context if available
    if state.get("needs_holidays") and state.get("messages"):
        # Find holiday info messages
        for msg in state.get("messages", []):
            if isinstance(msg, SystemMessage) and "Holiday Information" in msg.content:
                messages.append(msg)

    # Call OpenAI LLM
    response = await llm.ainvoke(messages)
    answer = response.content

    # Use citations from retriever if available, otherwise use default
    citations = state.get("citations", [{"title": "Banking Security Guide", "url": "#"}])

    return {
        **state,
        "answer": answer,
        "citations": citations
    }

def should_call_holidays(state: AgentState) -> str:
    """Conditional edge: determine if we need to call holidays API."""
    if state.get("needs_holidays"):
        return "holidays"
    return "llm_answer"

def should_continue(state: AgentState) -> str:
    """Conditional edge: determine next node after router."""
    if state.get("is_out_of_scope"):
        return "out_of_scope"

    # All in-scope questions go through RAG retriever
    return "retriever"
