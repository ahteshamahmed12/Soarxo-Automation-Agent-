from datetime import datetime
from typing import Optional

from sqlmodel import Field, Relationship, SQLModel

from ..core.utils import utcnow


class Dealer(SQLModel, table=True):
    __tablename__ = "dealers"

    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    whatsapp_number: str
    location: str = "Saddar"  # Karachi's Saddar market area
    active: bool = True
    notes: Optional[str] = None
    created_at: datetime = Field(
        default_factory=utcnow, sa_column_kwargs={"default": "now()"}
    )

    quotes: list["DealerQuote"] = Relationship(
        back_populates="dealer",
        sa_relationship_kwargs={"lazy": "selectin"},
    )


class DealerQuote(SQLModel, table=True):
    __tablename__ = "dealer_quotes"

    id: Optional[int] = Field(default=None, primary_key=True)
    dealer_id: int = Field(foreign_key="dealers.id")
    order_id: int = Field(foreign_key="orders.id")
    total: float
    quoted_at: datetime = Field(
        default_factory=utcnow, sa_column_kwargs={"default": "now()"}
    )
    raw_reply: Optional[str] = None
    status: str = "pending"  # pending, selected, rejected

    dealer: "Dealer" = Relationship(back_populates="quotes")
    order: "Order" = Relationship(back_populates="dealer_quotes")
    line_items: list["DealerQuoteItem"] = Relationship(
        back_populates="quote",
        sa_relationship_kwargs={"lazy": "selectin"},
    )


class DealerQuoteItem(SQLModel, table=True):
    __tablename__ = "dealer_quote_items"

    id: Optional[int] = Field(default=None, primary_key=True)
    quote_id: int = Field(foreign_key="dealer_quotes.id")
    part_number: Optional[str] = None
    description: str
    quantity: float
    unit_price: float

    quote: "DealerQuote" = Relationship(back_populates="line_items")


# Avoid circular imports
from .order import Order  # noqa: E402
