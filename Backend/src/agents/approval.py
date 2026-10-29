"""ApprovalRequest manager with interrupt handler for owner approval gates.

Constitution Principle I: No price, quotation, invoice, or tax figure is sent
to a client without explicit owner approval. This module manages the
interruption, state tracking, and approval flow for all financial documents.
"""

from datetime import datetime
from enum import Enum
from typing import Optional

from sqlmodel import Session, select
from agents import RunContext, Runner, trace

from ..core.config import settings
from ..core.logging import log
from ..models.approval import ApprovalRequest, ApprovalStatus, ApprovalRequestLog
from ..models.invoice import InvoiceDraft, InvoiceStatus


class ApprovalType(str, Enum):
    INVOICE = "invoice"
    QUOTE = "quote"
    MESSAGE = "message"


class ApprovalManager:
    """Manages owner-approval gates for financial documents."""

    def __init__(self, db_session: Session) -> None:
        self.db = db_session

    def create_approval_request(
        self,
        entity_type: ApprovalType,
        entity_id: int,
        amount: Optional[float],
        reason: str,
    ) -> ApprovalRequest:
        """Create a pending approval request for a financial document."""
        req = ApprovalRequest(
            entity_type=entity_type.value,
            entity_id=entity_id,
            amount=amount,
            reason=reason,
            status=ApprovalStatus.PENDING,
        )
        self.db.add(req)
        self.db.commit()
        self.db.refresh(req)

        log.info(
            "Approval request created",
            extra={
                "action": "approval_requested",
                "actor": "agent",
                "entity_type": entity_type.value,
                "entity_id": entity_id,
                "amount": amount,
            },
        )
        return req

    def get_pending_approvals(self) -> list[ApprovalRequest]:
        """Get all pending approval requests (for dashboard/display)."""
        stmt = select(ApprovalRequest).where(
            ApprovalRequest.status == ApprovalStatus.PENDING
        )
        return list(self.db.exec(stmt).all())

    def approve(self, request_id: int, approver: str = "owner") -> bool:
        """Approve an approval request. Triggers the resume of an interrupted agent."""
        req = self.db.get(ApprovalRequest, request_id)
        if not req or req.status != ApprovalStatus.PENDING:
            return False

        req.status = ApprovalStatus.APPROVED
        req.resolved_at = datetime.utcnow()
        req.resolved_by = approver

        # Log the approval
        self.db.add(
            ApprovalRequestLog(
                request_id=request_id,
                status=ApprovalStatus.APPROVED.value,
                actor=approver,
                action="approve",
            )
        )

        self.db.commit()

        # If this was an invoice approval, update the invoice status
        if req.entity_type == "invoice":
            invoice = self.db.get(InvoiceDraft, req.entity_id)
            if invoice and invoice.status == InvoiceStatus.PENDING_APPROVAL:
                invoice.status = InvoiceStatus.APPROVED
                invoice.approved_at = datetime.utcnow()
                self.db.add(invoice)
                self.db.commit()

        log.info(
            "Approval granted",
            extra={
                "action": "approval_granted",
                "actor": approver,
                "entity_type": req.entity_type,
                "entity_id": req.entity_id,
            },
        )
        return True

    def reject(self, request_id: int, rejector: str = "owner") -> bool:
        """Reject an approval request. Returns the workflow to the agent for escalation."""
        req = self.db.get(ApprovalRequest, request_id)
        if not req or req.status != ApprovalStatus.PENDING:
            return False

        req.status = ApprovalStatus.REJECTED
        req.resolved_at = datetime.utcnow()
        req.resolved_by = rejector

        self.db.add(
            ApprovalRequestLog(
                request_id=request_id,
                status=ApprovalStatus.REJECTED.value,
                actor=rejector,
                action="reject",
            )
        )

        self.db.commit()

        log.info(
            "Approval rejected",
            extra={
                "action": "approval_rejected",
                "actor": rejector,
                "entity_type": req.entity_type,
                "entity_id": req.entity_id,
            },
        )
        return True