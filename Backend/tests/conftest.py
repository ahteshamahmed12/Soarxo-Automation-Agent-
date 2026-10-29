"""Shared test fixtures for all tests.

Provides mocked DB sessions, WhatsApp client, Gmail client, and OpenAI clients.
"""

import os

# Set test environment variables BEFORE importing src modules
# (settings singleton is instantiated at import time)
os.environ.setdefault("DATABASE_URL", "sqlite:///")
os.environ.setdefault("OPENAI_API_KEY", "sk-test-key-for-testing")
os.environ.setdefault("WHATSAPP_TOKEN", "test_whatsapp_token")
os.environ.setdefault("WHATSAPP_PHONE_NUMBER_ID", "123456789")
os.environ.setdefault("WHATSAPP_WEBHOOK_SECRET", "test_webhook_secret")
os.environ.setdefault("GMAIL_IMAP_USER", "test@example.com")
os.environ.setdefault("GMAIL_IMAP_PASSWORD", "test_app_password")
os.environ.setdefault("SMTP_USER", "test@example.com")
os.environ.setdefault("SMTP_PASSWORD", "test_smtp_password")
os.environ.setdefault("APPROVED_CLIENT_SENDERS", "approved@example.com")

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from sqlmodel import SQLModel, create_engine, Session
from sqlalchemy.pool import StaticPool


@pytest.fixture(name="db_session")
def db_session() -> Session:
    """In-memory SQLite database for unit tests."""
    engine = create_engine(
        "sqlite:///",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        yield session
    SQLModel.metadata.drop_all(engine)
    engine.dispose()


@pytest.fixture(name="mock_whatsapp_client")
def mock_whatsapp_client() -> MagicMock:
    """Mock WhatsAppClient for tests."""
    with patch("src.services.whatsapp_client.WhatsAppClient") as MockClass:
        mock = MockClass.return_value
        mock.send_text_message.return_value = {
            "messages": [{"id": "test_msg_123"}]
        }
        mock.send_template_message.return_value = {
            "messages": [{"id": "test_template_123"}]
        }
        mock.verify_webhook_signature.return_value = True
        yield mock


@pytest.fixture(name="mock_gmail_client")
def mock_gmail_client() -> MagicMock:
    """Mock GmailClient for tests."""
    with patch("src.services.gmail_client.GmailClient") as MockClass:
        mock = MockClass.return_value
        mock.poll_unseen_emails.return_value = []
        mock.is_sender_approved.return_value = True
        mock.connect.return_value = None
        mock.disconnect.return_value = None
        mock._extract_sender.return_value = "sender@example.com"
        mock._verify_auth_headers.return_value = True
        yield mock


@pytest.fixture(name="mock_openai")
def mock_openai() -> MagicMock:
    """Mock OpenAI client for agent tests."""
    mock = AsyncMock()
    mock.chat = MagicMock()
    mock.chat.completions = MagicMock()
    return mock