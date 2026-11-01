from datetime import datetime
from typing import Optional

from sqlmodel import Field, SQLModel

from ..core.utils import utcnow


class LeadContact(SQLModel, table=True):
    __tablename__ = "lead_contacts"

    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    title: str
    company: str
    linkedin_url: Optional[str] = None
    whatsapp_number: Optional[str] = None
    source_company: Optional[str] = None
    contacted_at: Optional[datetime] = None
    status: str = "new"  # new, contacted, replied, converted
    created_at: datetime = Field(
        default_factory=utcnow, sa_column_kwargs={"default": "now()"}
    )
