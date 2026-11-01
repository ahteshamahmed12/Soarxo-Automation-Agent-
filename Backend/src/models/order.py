from datetime import datetime
from enum import Enum
from typing import Optional

from sqlmodel import CheckConstraint, Field, Relationship, SQLModel

from ..core.utils import utcnow


class OrderStatus(str, Enum):
    DRAFT = "draft"
    INTAKE_PENDING = "intake_pending"
    INTAKE_COMPLETED = "intake_completed"
    RFQ_SENT = "rfq_sent"
    QUOTE_RECEIVED = "quote_received"
    QUOTE_SELECTED = "quote_selected"
    INVOICE_DRAFTED = "invoice_drafted"
    INVOICE_APPROVED = "invoice_approved"
    SENT_TO_CLIENT = "sent_to_client"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class Order(SQLModel, table=True):
    __tablename__ = "orders"

    id: Optional[int] = Field(default=None, primary_key=True)
    client_id: int = Field(foreign_key="clients.id")
    source_email: str
    source_email_id: Optional[str] = None
    status: OrderStatus = Field(default=OrderStatus.INTAKE_PENDING)
    notes: Optional[str] = None
    created_at: datetime = Field(
        default_factory=utcnow, sa_column_kwargs={"default": "now()"}
    )
    updated_at: datetime = Field(
        default_factory=utcnow,
        sa_column_kwargs={"default": "now()", "onupdate": "now()"},
    )

    client: "Client" = Relationship(back_populates="orders")
    items: list["OrderItem"] = Relationship(
        back_populates="order",
        sa_relationship_kwargs={"lazy": "selectin"},
    )
    invoice: Optional["InvoiceDraft"] = Relationship(back_populates="order")
    dealer_quotes: list["DealerQuote"] = Relationship(
        back_populates="order",
        sa_relationship_kwargs={"lazy": "selectin"},
    )


class OrderItem(SQLModel, table=True):
    __tablename__ = "order_items"
    __table_args__ = (
        CheckConstraint("quantity > 0", name="ck_order_item_quantity_positive"),
    )

    id: Optional[int] = Field(default=None, primary_key=True)
    order_id: int = Field(foreign_key="orders.id")
    part_number: str
    description: str
    quantity: float
    unit: str
    specs: Optional[str] = None
    category: Optional[str] = None

    order: "Order" = Relationship(back_populates="items")


class LineItem(SQLModel, table=True):
    __tablename__ = "line_items"

    id: Optional[int] = Field(default=None, primary_key=True)
    order_id: int = Field(foreign_key="orders.id")
    description: str
    quantity: float
    unit: str
    part_number: Optional[str] = None
    unit_price: Optional[float] = None


# Avoid circular imports
from .client import Client  # noqa: E402
from .dealer import DealerQuote  # noqa: E402
from .invoice import InvoiceDraft  # noqa: E402
