from sqlmodel import SQLModel

from .approval import ApprovalRequest
from .audit import AuditLog
from .catalog import Catalog

# Re-export all models for SQLModel.metadata.create_all()
from .auth import SignupRequest, User, UserRole, UserStatus
from .client import Client, ClientContact
from .config import MarginConfig, TaxConfig
from .contact import LeadContact
from .dealer import Dealer, DealerQuote
from .invoice import InvoiceDraft
from .order import LineItem, Order, OrderItem

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
    "User",
    "SignupRequest",
    "UserRole",
    "UserStatus",
]
