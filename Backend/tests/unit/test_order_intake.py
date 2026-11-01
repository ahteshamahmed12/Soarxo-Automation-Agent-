"""Unit tests for User Story 2: Structured Order Intake.

Tests LineItem extraction logic (T018) and Order model validation (T019).
"""

import pytest
from sqlmodel import SQLModel, Session, create_engine
from sqlalchemy.pool import StaticPool

# Import the models package so all tables are registered
# before SQLModel.metadata.create_all() runs.
from src.models import *  # noqa: F401,F403
from src.models.order import Order, OrderItem, OrderStatus
from src.models.client import Client


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture(name="db_engine")
def db_engine_fixture():
    engine = create_engine(
        "sqlite:///",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    SQLModel.metadata.create_all(engine)
    # Seed a client row so Order (FK to clients) can be created.
    with Session(engine) as s:
        s.add(Client(id=1, name="Test Client", email="client@example.com", company="Acme Inc"))
        s.commit()
    yield engine
    SQLModel.metadata.drop_all(engine)
    engine.dispose()


@pytest.fixture(name="order_db")
def order_db_fixture(db_engine):
    with Session(db_engine) as session:
        yield session


# ---------------------------------------------------------------------------
# T018: LineItem extraction logic
# ---------------------------------------------------------------------------

class TestLineItemExtraction:
    """Tests for extracting OrderItem/LineItem from email text."""

    def test_extract_line_item_from_parsed_dict(self, order_db):
        """Extract a single line item from a parsed-order dict."""
        from src.services.email_parser import OrderEmailParser

        parser = OrderEmailParser()
        item = parser.extract_line_item(
            description="Motor 1 HP, 3-phase",
            quantity=2.0,
            unit="pcs",
            part_number="MTR-001",
        )
        assert item is not None
        assert item.part_number == "MTR-001"
        assert "Motor 1 HP" in item.description
        assert item.quantity == 2.0
        assert item.unit == "pcs"

    def test_extract_line_item_without_part_number(self, order_db):
        """When part_number is unknown, return None or a flagged item."""
        from src.services.email_parser import OrderEmailParser

        parser = OrderEmailParser()
        result = parser.extract_line_item(
            description="Industrial bearings",
            quantity=5.0,
            unit="pcs",
            part_number=None,
        )
        # Unknown parts should be flagged — returned with part_number None
        # so the caller can escalate per Principle IV.
        assert result is not None
        assert result.part_number is None

    def test_extract_multiple_line_items(self, order_db):
        """Extract multiple line items from an order email body."""
        from src.services.email_parser import OrderEmailParser

        parser = OrderEmailParser()
        body = (
            "Dear Sorax,\n"
            "Please provide the following items:\n"
            "1. Motor 1 HP - 2 pcs\n"
            "2. Bearings SKF - 5 pcs\n"
            "3. Control panel - 1 unit\n"
        )
        items = parser.extract_line_items(body)
        assert len(items) >= 1
        # At least the first recognized item should have quantity 2
        found_two = any(i.quantity == 2.0 for i in items)
        assert found_two

    def test_extract_quantity_parses_integer_string(self, order_db):
        """Quantity '3' should parse to numeric 3.0."""
        from src.services.email_parser import OrderEmailParser

        parser = OrderEmailParser()
        item = parser.extract_line_item(
            description="Cables",
            quantity="3",
            unit="pcs",
            part_number=None,
        )
        assert item.quantity == 3.0

    def test_extract_quantity_raises_on_invalid(self, order_db):
        """Non-numeric quantity should raise ValueError to prevent guessing."""
        from src.services.email_parser import OrderEmailParser

        parser = OrderEmailParser()
        with pytest.raises(ValueError):
            parser.extract_line_item(
                description="Ambiguous item",
                quantity="a few",  # non-numeric per edge case
                unit="pcs",
                part_number=None,
            )


# ---------------------------------------------------------------------------
# T019: Order model validation
# ---------------------------------------------------------------------------

class TestOrderModelValidation:
    """Tests for SQLModel Order entity validation and defaults."""

    def test_order_requires_client_id_and_source_email(self, order_db):
        """Order cannot be created without client_id and source_email."""
        with pytest.raises(Exception):
            order = Order(source_email="missing@example.com")
            order_db.add(order)
            order_db.commit()

    def test_order_defaults_to_intake_pending_status(self, order_db):
        """New orders default to INTAKE_PENDING status."""
        order = Order(client_id=1, source_email="client@example.com")
        order_db.add(order)
        order_db.commit()
        order_db.refresh(order)
        assert order.status == OrderStatus.INTAKE_PENDING

    def test_order_items_relation_populated(self, order_db):
        """Order.items returns related OrderItem objects."""
        order = Order(client_id=1, source_email="client@example.com")
        order_db.add(order)
        order_db.commit()
        order_db.refresh(order)

        item = OrderItem(
            order_id=order.id,
            part_number="ABC-123",
            description="Test part",
            quantity=1.0,
            unit="pcs",
        )
        order_db.add(item)
        order_db.commit()
        order_db.refresh(order)
        assert len(order.items) == 1
        assert order.items[0].part_number == "ABC-123"

    def test_order_source_email_stored(self, order_db):
        """source_email is persisted on the Order entity."""
        email = "test@example.com"
        order = Order(client_id=1, source_email=email)
        order_db.add(order)
        order_db.commit()
        order_db.refresh(order)
        assert order.source_email == email

    def test_orderitem_quantity_must_be_positive(self, order_db):
        """OrderItem with non-positive quantity should fail validation."""
        order = Order(client_id=1, source_email="ok@example.com")
        order_db.add(order)
        order_db.commit()
        order_db.refresh(order)

        item = OrderItem(
            order_id=order.id,
            part_number="X",
            description="bad",
            quantity=0.0,
            unit="pcs",
        )
        with pytest.raises(Exception):
            order_db.add(item)
            order_db.commit()
