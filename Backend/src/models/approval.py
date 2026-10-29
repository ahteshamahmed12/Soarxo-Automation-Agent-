from datetime import datetime
from enum import Enum
from typing import Optional

from sqlmodel import Field, Relationship, SQLModel


class ApprovalStatus(str, Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"


class ApprovalRequest(SQLModel, table=True):
    __tablename__ = "approval_requests"

    id: Optional[int] = Field(default=None, primary_key=True)
    entity_type: str   # e.g., "invoice", "quote", "message"
    entity_id: int     # references the entity (InvoiceDraft.id, etc.)
    amount: Optional[float] = None  # financial figure requiring approval
    reason: str        # what needs approval (e.g., "invoice total: PKR 125,000")
    status: ApprovalStatus = Field(default=ApprovalStatus.PENDING)
    created_at: datetime = Field(
        default_factory=datetime.utcnow, sa_column_kwargs={"default": "now()"}
    )
    resolved_at: Optional[datetime] = None
    resolved_by: Optional[str] = None  # owner identifier

    invoice: Optional["InvoiceDraft"] = Relationship(back_populates="approval_request")


class ApprovalRequestLog(SQLModel, table=True):
    __tablename__ = "approval_request_logs"

    id: Optional[int] = Field(default=None, primary_key=True)
    request_id: int = Field(foreign_key="approval_requests.id")
    status: str
    actor: str  # "owner", "system", "agent"
    action: str  # "approve", "reject", "escalate", "remind"
    note: Optional[str] = None
    timestamp: datetime = Field(
        default_factory=datetime.utcnow, sa_column_kwargs={"default": "now()"}
    )


# Avoid circular imports
from .invoice import InvoiceDraft  # noqa: E402