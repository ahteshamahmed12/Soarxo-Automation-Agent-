from datetime import datetime
from enum import Enum
from typing import TYPE_CHECKING, Optional

from sqlmodel import Field, Relationship, SQLModel

from ..core.utils import utcnow

if TYPE_CHECKING:
    from .order import Order


class InvoiceStatus(str, Enum):
    PENDING_APPROVAL = "pending_approval"
    APPROVED = "approved"
    SENT = "sent"
    REJECTED = "rejected"


class InvoiceDraft(SQLModel, table=True):
    __tablename__ = "invoice_drafts"

    id: Optional[int] = Field(default=None, primary_key=True)
    order_id: int = Field(foreign_key="orders.id")
    margin_pct: float  # per-part-category margin applied
    tax_rate: float    # tax rate applied (e.g., 0.17 for 17% GST)
    subtotal: float
    total: float        # subtotal + tax
    status: InvoiceStatus = Field(default=InvoiceStatus.PENDING_APPROVAL)
    pdf_path: Optional[str] = None
    created_at: datetime = Field(
        default_factory=utcnow, sa_column_kwargs={"default": "now()"}
    )
    approved_at: Optional[datetime] = None
    sent_at: Optional[datetime] = None

    order: "Order" = Relationship(back_populates="invoice")


# Avoid circular imports
from .order import Order  # noqa: E402
