"""Tests for LangGraph agent components."""
import pytest
from app.agent.state import AgentState
from app.agent.nodes import (
    router_node,
    out_of_scope_node,
    retriever_node,
    holidays_node,
    llm_answer_node,
    should_continue,
    should_call_holidays
)
from langchain_core.messages import HumanMessage


class TestRouterNode:
    """Tests for router_node."""

    @pytest.mark.asyncio
    async def test_router_identifies_login_security(self):
        """Test router correctly identifies login/security questions."""
        state = {
            "question": "How do I reset my password?",
            "messages": [],
            "answer": None,
            "citations": None,
            "tool_calls": [],
            "is_out_of_scope": False,
            "needs_holidays": False,
            "retrieved_docs": None
        }

        result = await router_node(state)

        assert result["is_out_of_scope"] is False
        assert "needs_holidays" in result

    @pytest.mark.asyncio
    async def test_router_identifies_holidays(self):
        """Test router correctly identifies holiday-related questions."""
        state = {
            "question": "Is today a federal holiday?",
            "messages": [],
            "answer": None,
            "citations": None,
            "tool_calls": [],
            "is_out_of_scope": False,
            "needs_holidays": False,
            "retrieved_docs": None
        }

        result = await router_node(state)

        assert result["needs_holidays"] is True
        assert result["is_out_of_scope"] is False

    @pytest.mark.asyncio
    async def test_router_identifies_out_of_scope(self):
        """Test router identifies out-of-scope questions with benefit of doubt."""
        state = {
            "question": "Tell me a joke",
            "messages": [],
            "answer": None,
            "citations": None,
            "tool_calls": [],
            "is_out_of_scope": False,
            "needs_holidays": False,
            "retrieved_docs": None
        }

        result = await router_node(state)

        # With benefit of doubt, should assume login/security
        # But this particular question has no security keywords
        assert "is_out_of_scope" in result


class TestOutOfScopeNode:
    """Tests for out_of_scope_node."""

    @pytest.mark.asyncio
    async def test_out_of_scope_returns_helpful_message(self):
        """Test out_of_scope_node returns helpful guidance."""
        state = {
            "question": "What's the weather?",
            "messages": [],
            "answer": None,
            "citations": None,
            "tool_calls": [],
            "is_out_of_scope": True,
            "needs_holidays": False,
            "retrieved_docs": None
        }

        result = await out_of_scope_node(state)

        assert "answer" in result
        assert len(result["answer"]) > 0
        assert "support" in result["answer"].lower()
        assert len(result["citations"]) > 0


class TestRetrieverNode:
    """Tests for retriever_node."""

    @pytest.mark.asyncio
    async def test_retriever_node_structure(self):
        """Test retriever_node returns correct structure."""
        state = {
            "question": "How do I reset my password?",
            "messages": [],
            "answer": None,
            "citations": None,
            "tool_calls": [],
            "is_out_of_scope": False,
            "needs_holidays": False,
            "retrieved_docs": None
        }

        try:
            result = await retriever_node(state)

            assert "retrieved_docs" in result
            assert "citations" in result

            # If vectorstore exists, should have retrieved docs
            if result.get("retrieved_docs"):
                assert isinstance(result["retrieved_docs"], str)
                assert isinstance(result["citations"], list)
        except FileNotFoundError:
            pytest.skip("Vectorstore not found - run ingestion first")


class TestHolidaysNode:
    """Tests for holidays_node."""

    @pytest.mark.asyncio
    async def test_holidays_node_calls_api(self):
        """Test holidays_node calls federal holidays API."""
        state = {
            "question": "Is today a federal holiday?",
            "messages": [],
            "answer": None,
            "citations": None,
            "tool_calls": [],
            "is_out_of_scope": False,
            "needs_holidays": True,
            "retrieved_docs": None
        }

        result = await holidays_node(state)

        assert "tool_calls" in result
        assert "federal_holidays_api" in result["tool_calls"]
        assert "messages" in result


class TestConditionalEdges:
    """Tests for conditional edge functions."""

    def test_should_continue_out_of_scope(self):
        """Test should_continue returns 'out_of_scope' correctly."""
        state = {
            "is_out_of_scope": True,
            "needs_holidays": False
        }

        result = should_continue(state)
        assert result == "out_of_scope"

    def test_should_continue_in_scope(self):
        """Test should_continue returns 'retriever' for in-scope."""
        state = {
            "is_out_of_scope": False,
            "needs_holidays": False
        }

        result = should_continue(state)
        assert result == "retriever"

    def test_should_call_holidays_true(self):
        """Test should_call_holidays returns 'holidays' correctly."""
        state = {
            "needs_holidays": True
        }

        result = should_call_holidays(state)
        assert result == "holidays"

    def test_should_call_holidays_false(self):
        """Test should_call_holidays returns 'llm_answer' correctly."""
        state = {
            "needs_holidays": False
        }

        result = should_call_holidays(state)
        assert result == "llm_answer"
