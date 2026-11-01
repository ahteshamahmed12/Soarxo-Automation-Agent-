"""OrderIntakeAgent — User Story 2: Structured Order Intake.

Receives an order email, parses it into structured line items, resolves the
client, creates an Order + OrderItems record, and escalates unknown parts
and ambiguous quantities to the owner (Constitution Principle IV — Accuracy).
"""

from __future__ import annotations

from agents import Agent, function_tool
from sqlmodel import Session, select

from ..core.logging import log
from ..models.client import Client
from ..models.order import LineItem, Order, OrderItem, OrderStatus
from ..services.email_parser import OrderEmailParser


def _find_or_create_client(db: Session, email: str, name: str = "") -> Client:
    """Look up a client by email; create one if unknown (pending review)."""
    stmt = select(Client).where(Client.email == email)
    client = db.exec(stmt).first()
    if client:
        return client

    client = Client(name=name or "Unknown", email=email, company=name or "Pending")
    db.add(client)
    db.commit()
    db.refresh(client)
    log.info("New client auto-created from order email", extra={
        "action": "client_created",
        "actor": "agent",
        "client_email": email,
    })
    return client


def _parse_email_body(
    db: Session, sender: str, body: str, subject: str = ""
) -> Order:
    """Parse an email body into a structured Order + OrderItems.

    Unknown / unmatched parts are stored as ``LineItem`` records (with
    ``quantity=0.0``, ``unit="unknown"``) so the owner can review them
    without guessing on values (Principle IV).
    """
    parser = OrderEmailParser()
    items, warnings = parser.extract_with_warnings(body)

    if not items and not warnings:
        raise ValueError("No line items could be parsed from the order email")

    client = _find_or_create_client(db, sender)

    order = Order(
        client_id=client.id,
        source_email=sender,
        status=OrderStatus.INTAKE_PENDING,
    )
    db.add(order)
    db.commit()
    db.refresh(order)

    # Store escalated items as LineItem records for owner review
    for wi in warnings:
        db.add(LineItem(
            order_id=order.id,
            description=wi.description,
            quantity=0.0,
            unit="unknown",
            part_number=wi.part_number,
        ))
        log.warning("Order item requires owner review", extra={
            "action": "item_escalated",
            "actor": "agent",
            "order_id": order.id,
            "reason": wi.reason,
        })

    # Persist structured order items
    for item in items:
        order_item = OrderItem(
            order_id=order.id,
            part_number=item.part_number or "UNKNOWN",
            description=item.description,
            quantity=item.quantity,
            unit=item.unit,
            specs=getattr(item, "specs", None),
            category=getattr(item, "category", None),
        )
        db.add(order_item)

    db.commit()
    db.refresh(order)
    log.info("Order parsed and stored", extra={
        "action": "order_intake_complete",
        "actor": "agent",
        "order_id": order.id,
        "item_count": len(items),
        "escalated_count": len(warnings),
    })
    return order


def _get_escalated_items(db: Session, order_id: int) -> list[str]:
    """Return descriptions of escalated (warning) line items for an order."""
    stmt = select(LineItem).where(LineItem.order_id == order_id)
    lines = db.exec(stmt).all()
    return [li.description for li in lines if li.quantity == 0.0 and li.unit == "unknown"]


@function_tool
def parse_order_email(
    sender: str,
    subject: str,
    body: str,
) -> dict:
    """Parse a client order email into a structured Order.

    Returns a dict with ``order_id``, ``status``, ``item_count``, and
    ``escalated_items`` (items needing owner review).
    """
    from ..core.database import get_session

    with get_session() as db:
        order = _parse_email_body(db, sender, body, subject)
        escalated = _get_escalated_items(db, order.id)
        return {
            "order_id": order.id,
            "status": order.status.value,
            "item_count": len(order.items),
            "escalated_items": escalated,
        }


def build_order_intake_agent() -> Agent:
    """Construct the OrderIntakeAgent with the email-parsing tool."""
    return Agent(
        name="order_intake_agent",
        instructions=(
            "You are the Order Intake Agent for Sorax Industrial Solution. "
            "Your job is to parse client order emails into structured "
            "OrderItems. For each email you receive, call the parse_order_email "
            "tool with the sender, subject, and body. Do NOT guess quantities "
            "or part numbers — escalate ambiguous items to the owner. "
            "Never send any price, quotation, or tax figure without owner approval."
        ),
        tools=[parse_order_email],
    )


order_intake_agent = build_order_intake_agent()
