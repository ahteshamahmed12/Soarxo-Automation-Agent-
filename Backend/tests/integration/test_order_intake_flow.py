"""Integration test for full order intake flow (T026).

Verifies: parsing an order email → structured Order + OrderItems in DB
→ confirmation email sent.
"""

from unittest.mock import patch, MagicMock

import pytest
from sqlmodel import SQLModel, Session, create_engine, select
from sqlalchemy.pool import StaticPool

# Import models so SQLModel.metadata has all tables registered
from src.models import *  # noqa: F401,F403
from src.models.client import Client
from src.models.order import LineItem, OrderItem, OrderStatus


@pytest.fixture(name="flow_engine")
def flow_engine_fixture():
    engine = create_engine(
        "sqlite:///",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    SQLModel.metadata.create_all(engine)
    with Session(engine) as s:
        s.add(Client(id=1, name="Flow Client", email="client@example.com", company="Acme"))
        s.commit()
    yield engine
    SQLModel.metadata.drop_all(engine)
    engine.dispose()


@pytest.fixture(name="flow_db")
def flow_db_fixture(flow_engine):
    with Session(flow_engine) as session:
        yield session


class TestOrderIntakeFlow:
    """Full flow: email parse → Order + OrderItems → confirmation."""

    def test_full_flow_parses_email_and_creates_order(self, flow_db):
        """A sample order email produces an Order with correct items in DB."""
        from src.agents.order_intake import _parse_email_body
        from src.models.order import Order

        email_body = (
            "Dear Sorax Team,\n"
            "Please quote for the following items:\n"
            "1. Motor 1 HP - 2 pcs\n"
            "2. Bearings SKF-6205 - 5 pcs\n"
            "3. Control panel - 1 unit\n"
        )

        order = _parse_email_body(
            db=flow_db,
            sender="client@example.com",
            body=email_body,
            subject="Order Request",
        )

        assert order is not None
        assert order.client_id == 1
        assert order.source_email == "client@example.com"
        assert order.status == OrderStatus.INTAKE_PENDING

        # Verify OrderItems were created
        flow_db.refresh(order)
        assert len(order.items) >= 1
        for item in order.items:
            assert item.quantity > 0
            assert item.part_number is not None

    def test_full_flow_escalates_ambiguous_quantity(self, flow_db):
        """Items with ambiguous quantities are stored as LineItem for review."""
        from src.agents.order_intake import _parse_email_body
        from src.models.order import Order

        email_body = (
            "Hi,\n"
            "1. Motor 1 HP - 2 pcs\n"
            "2. Bearings, a few pcs - 1 unit\n"
        )

        order = _parse_email_body(
            db=flow_db,
            sender="client@example.com",
            body=email_body,
            subject="Order with ambiguous qty",
        )

        flow_db.refresh(order)
        # Check for LineItem escalation records
        line_items = flow_db.exec(
            select(LineItem).where(LineItem.order_id == order.id)
        ).all()
        # The "a few" item should be escalated
        assert any(li.quantity == 0.0 and li.unit == "unknown" for li in line_items)

    def test_full_flow_confirmation_email_sent(self, flow_db):
        """After order creation, confirmation email is dispatched."""
        from src.agents.order_intake import _parse_email_body
        from src.models.order import Order

        email_body = "1. Motor 1 HP - 2 pcs\n"

        with patch("src.jobs.email_polling.smtplib") as mock_smtp:
            mock_server = MagicMock()
            mock_server.__enter__.return_value = mock_server
            mock_smtp.SMTP.return_value = mock_server

            order = _parse_email_body(
                db=flow_db,
                sender="client@example.com",
                body=email_body,
                subject="Order",
            )

            from src.jobs.email_polling import _send_confirmation_email
            _send_confirmation_email(
                to_email="client@example.com",
                order_id=order.id,
                item_count=len(order.items),
                escalated=0,
            )

            # Verify SMTP send was called
            mock_server.send_message.assert_called_once()

    def test_full_flow_new_client_auto_created(self, flow_db):
        """Unknown sender creates a new Client record."""
        from src.agents.order_intake import _parse_email_body
        from src.models.order import Order

        email_body = "1. Control panel - 1 unit\n"

        order = _parse_email_body(
            db=flow_db,
            sender="newclient@example.com",
            body=email_body,
            subject="First order",
        )

        flow_db.refresh(order)
        assert order.client is not None
        assert order.client.email == "newclient@example.com"
