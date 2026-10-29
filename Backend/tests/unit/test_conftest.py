"""Basic tests to verify conftest fixtures work correctly."""

import pytest


def test_db_session_fixture(db_session):
    """Verify the db_session fixture provides a working SQLModel Session."""
    assert db_session is not None
    assert hasattr(db_session, "exec")
    assert hasattr(db_session, "add")
    assert hasattr(db_session, "commit")


def test_mock_whatsapp_client_fixture(mock_whatsapp_client):
    """Verify the mock_whatsapp_client fixture is properly patched."""
    assert mock_whatsapp_client is not None
    result = mock_whatsapp_client.send_text_message("+1234567890", "Hello")
    assert result == {"messages": [{"id": "test_msg_123"}]}


def test_mock_gmail_client_fixture(mock_gmail_client):
    """Verify the mock_gmail_client fixture is properly patched."""
    assert mock_gmail_client is not None
    emails = mock_gmail_client.poll_unseen_emails()
    assert emails == []


def test_mock_openai_fixture(mock_openai):
    """Verify the mock_openai fixture is provided."""
    assert mock_openai is not None


def test_environment_variables_set():
    """Verify test environment variables are set."""
    import os

    assert os.environ.get("DATABASE_URL") == "sqlite:///"
    assert os.environ.get("OPENAI_API_KEY") == "sk-test-key-for-testing"
    assert os.environ.get("WHATSAPP_TOKEN") == "test_whatsapp_token"
