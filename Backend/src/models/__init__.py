from sqlmodel import SQLModel

# Re-export all models for SQLModel.metadata.create_all()
from .client import Client, ClientContact
from .order import Order, OrderItem, LineItem
from .dealer import Dealer, DealerQuote
from .invoice import InvoiceDraft
from .catalog import Catalog
from .contact import LeadContact
from .approval import ApprovalRequest
from .config import MarginConfig, TaxConfig
from .audit import AuditLog

__all__ = [
    "SQLModel",
    "Client",
    "ClientContact",
    "Order",
    "OrderItem",
    "LineItem",
    "Dealer",
    "DealerQuote",
    "InvoiceDraft",
    "Catalog",
    "LeadContact",
    "ApprovalRequest",
    "MarginConfig",
    "TaxConfig",
    "AuditLog",
]