from datetime import datetime
from typing import Any, Optional

from sqlalchemy import Column
from sqlmodel import Field, JSON, SQLModel


class AuditLog(SQLModel, table=True):
    __tablename__ = "audit_logs"

    id: Optional[int] = Field(default=None, primary_key=True)
    timestamp: datetime = Field(
        default_factory=datetime.utcnow, sa_column_kwargs={"default": "now()"}
    )
    agent_id: str
    action: str
    actor: str   # "agent" or "owner"
    outcome: str  # "success", "escalated", "failed", "approved", "rejected"
    order_id: Optional[int] = None
    audit_metadata: Optional[dict[str, Any]] = Field(
        default=None,
        sa_column=Column("metadata", JSON()),
    )
    retained_until: Optional[datetime] = None  # for 7-year retention policy