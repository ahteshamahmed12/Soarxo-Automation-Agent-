from datetime import datetime
from typing import Optional

from sqlmodel import Field, Relationship, SQLModel


class Client(SQLModel, table=True):
    __tablename__ = "clients"

    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    email: str
    company: str
    phone: Optional[str] = None
    created_at: datetime = Field(
        default_factory=datetime.utcnow, sa_column_kwargs={"default": "now()"}
    )
    updated_at: datetime = Field(
        default_factory=datetime.utcnow,
        sa_column_kwargs={"default": "now()", "onupdate": "now()"},
    )

    contacts: list["ClientContact"] = Relationship(
        back_populates="client",
        sa_relationship_kwargs={"lazy": "selectin"},
    )
    orders: list["Order"] = Relationship(
        back_populates="client",
        sa_relationship_kwargs={"lazy": "selectin"},
    )


class ClientContact(SQLModel, table=True):
    __tablename__ = "client_contacts"

    id: Optional[int] = Field(default=None, primary_key=True)
    client_id: int = Field(foreign_key="clients.id")
    name: str
    email: str
    whatsapp_number: Optional[str] = None
    last_contacted_at: Optional[datetime] = None
    crm_status: str = "active"

    client: "Client" = Relationship(back_populates="contacts")


# Avoid circular import for type annotations
from .order import Order  # noqa: E402