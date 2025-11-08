"""Tests for FastAPI endpoints."""
import pytest


class TestHealthEndpoint:
    """Tests for /health endpoint."""

    def test_health_check(self, client):
        """Test health check endpoint returns 200."""
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json() == {"status": "healthy"}


class TestChatEndpoint:
    """Tests for /chat endpoint."""

    def test_chat_endpoint_structure(self, client, sample_question):
        """Test chat endpoint returns correct structure."""
        response = client.post(
            "/chat",
            json={"question": sample_question}
        )
        assert response.status_code == 200
        data = response.json()

        # Verify response structure
        assert "answer" in data
        assert "citations" in data
        assert "timing_ms" in data
        assert "tool_calls" in data

        # Verify types
        assert isinstance(data["answer"], str)
        assert isinstance(data["citations"], list)
        assert isinstance(data["timing_ms"], int)
        assert isinstance(data["tool_calls"], list)

    def test_chat_returns_answer(self, client, sample_question):
        """Test chat endpoint returns non-empty answer."""
        response = client.post(
            "/chat",
            json={"question": sample_question}
        )
        assert response.status_code == 200
        data = response.json()
        assert len(data["answer"]) > 0

    def test_chat_includes_citations(self, client, sample_question):
        """Test chat endpoint includes citations for in-scope questions."""
        response = client.post(
            "/chat",
            json={"question": sample_question}
        )
        assert response.status_code == 200
        data = response.json()
        assert len(data["citations"]) > 0

        # Verify citation structure
        citation = data["citations"][0]
        assert "title" in citation
        assert "url" in citation

    def test_chat_timing_under_sla(self, client, sample_question):
        """Test chat response time is under 5s SLA (p95)."""
        response = client.post(
            "/chat",
            json={"question": sample_question}
        )
        assert response.status_code == 200
        data = response.json()

        # p95 latency requirement: ≤ 5000ms
        assert data["timing_ms"] <= 5000, f"Response took {data['timing_ms']}ms, exceeds 5s SLA"

    def test_out_of_scope_question(self, client, out_of_scope_question):
        """Test out-of-scope questions are handled gracefully."""
        response = client.post(
            "/chat",
            json={"question": out_of_scope_question}
        )
        assert response.status_code == 200
        data = response.json()

        # Should still return structured response
        assert "answer" in data
        assert len(data["answer"]) > 0

    def test_holidays_question_calls_tool(self, client):
        """Test holidays question triggers federal holidays API."""
        response = client.post(
            "/chat",
            json={"question": "Is today a federal holiday?"}
        )
        assert response.status_code == 200
        data = response.json()

        # Should have called federal_holidays_api tool
        assert "federal_holidays_api" in data["tool_calls"]

    def test_missing_question_field(self, client):
        """Test API returns 422 for missing question field."""
        response = client.post(
            "/chat",
            json={}
        )
        assert response.status_code == 422

    def test_empty_question(self, client):
        """Test API handles empty question."""
        response = client.post(
            "/chat",
            json={"question": ""}
        )
        # Should still return 200 with some response
        assert response.status_code == 200
