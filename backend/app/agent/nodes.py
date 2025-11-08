from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage
from app.agent.state import AgentState
from app.agent.prompts import SYSTEM_PROMPT, ROUTER_PROMPT
from app.tools.holidays import is_federal_holiday
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

    print(f"[Router] Question: {question}")
    print(f"[Router] is_login_security: {is_login_security}, needs_holidays: {needs_holidays}")

    return {
        **state,
        "is_out_of_scope": not is_login_security,
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

async def llm_answer_node(state: AgentState) -> AgentState:
    """
    Generates the final answer using the LLM.
    The LLM will provide warm, helpful responses about login/security topics.
    """
    question = state["question"]

    # Build messages for LLM
    messages = [
        SystemMessage(content=SYSTEM_PROMPT),
        HumanMessage(content=question)
    ]

    # Add holiday context if available
    if state.get("needs_holidays") and state.get("messages"):
        # Find holiday info messages
        for msg in state.get("messages", []):
            if isinstance(msg, SystemMessage) and "Holiday Information" in msg.content:
                messages.append(msg)

    # Call OpenAI LLM
    response = await llm.ainvoke(messages)
    answer = response.content

    # Generate citations (will be replaced by RAG later)
    citations = [{"title": "Banking Security Guide", "url": "#"}]

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

    if state.get("needs_holidays"):
        return "holidays"

    return "llm_answer"
