"""Shared pytest fixtures for all tests."""
import pytest
from fastapi.testclient import TestClient
from app.main import app


@pytest.fixture
def client():
    """FastAPI test client."""
    return TestClient(app)


@pytest.fixture
def sample_question():
    """Sample login/security question."""
    return "How do I reset my password?"


@pytest.fixture
def sample_questions():
    """List of sample questions for evaluation."""
    return [
        "I got locked out after entering the wrong password. Can I unlock myself?",
        "What are the password rules?",
        "Why do I keep getting verification codes?",
        "How often does 'remember this device' expire?",
        "I forgot my username — how do I recover it?",
        "I changed phones and now my codes don't work — what should I do?",
        "Please help me reset my password safely.",
        "Can I unlock a phone-banking user without calling support?",
        "I signed up, but I'm stuck — how do I finish setup?",
        "If I start a password reset on a federal holiday, when should I expect the next step?"
    ]


@pytest.fixture
def out_of_scope_question():
    """Question outside of login/security scope."""
    return "What's the weather today?"
