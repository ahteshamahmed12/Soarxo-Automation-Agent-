"""Initial schema with all foundational entities.

Revision ID: 001_initial_schema
Revises:
Create Date: 2025-06-13

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers
revision = "001_initial_schema"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # -- clients --
    op.create_table(
        "clients",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("email", sa.String(), nullable=False),
        sa.Column("company", sa.String(), nullable=False),
        sa.Column("phone", sa.String(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
    )

    # -- client_contacts --
    op.create_table(
        "client_contacts",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("client_id", sa.Integer(), sa.ForeignKey("clients.id"), nullable=False),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("email", sa.String(), nullable=False),
        sa.Column("whatsapp_number", sa.String(), nullable=True),
        sa.Column("last_contacted_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("crm_status", sa.String(), nullable=False, server_default="active"),
    )

    # -- orders --
    op.create_table(
        "orders",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("client_id", sa.Integer(), sa.ForeignKey("clients.id"), nullable=False),
        sa.Column("source_email", sa.String(), nullable=False),
        sa.Column("source_email_id", sa.String(), nullable=True),
        sa.Column("status", sa.String(), nullable=False, server_default="intake_pending"),
        sa.Column("notes", sa.String(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
    )

    # -- order_items --
    op.create_table(
        "order_items",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("order_id", sa.Integer(), sa.ForeignKey("orders.id"), nullable=False),
        sa.Column("part_number", sa.String(), nullable=False),
        sa.Column("description", sa.String(), nullable=False),
        sa.Column("quantity", sa.Numeric(12, 2), nullable=False),
        sa.Column("unit", sa.String(), nullable=False),
        sa.Column("specs", sa.String(), nullable=True),
        sa.Column("category", sa.String(), nullable=True),
    )

    # -- line_items --
    op.create_table(
        "line_items",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("order_id", sa.Integer(), sa.ForeignKey("orders.id"), nullable=False),
        sa.Column("description", sa.String(), nullable=False),
        sa.Column("quantity", sa.Numeric(12, 2), nullable=False),
        sa.Column("unit", sa.String(), nullable=False),
        sa.Column("part_number", sa.String(), nullable=True),
        sa.Column("unit_price", sa.Numeric(12, 2), nullable=True),
    )

    # -- dealers --
    op.create_table(
        "dealers",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("whatsapp_number", sa.String(), nullable=False),
        sa.Column("location", sa.String(), nullable=False, server_default="Saddar"),
        sa.Column("active", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.Column("notes", sa.String(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
    )

    # -- dealer_quotes --
    op.create_table(
        "dealer_quotes",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("dealer_id", sa.Integer(), sa.ForeignKey("dealers.id"), nullable=False),
        sa.Column("order_id", sa.Integer(), sa.ForeignKey("orders.id"), nullable=False),
        sa.Column("total", sa.Numeric(12, 2), nullable=False),
        sa.Column(
            "quoted_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column("raw_reply", sa.Text(), nullable=True),
        sa.Column("status", sa.String(), nullable=False, server_default="pending"),
    )

    # -- dealer_quote_items --
    op.create_table(
        "dealer_quote_items",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("quote_id", sa.Integer(), sa.ForeignKey("dealer_quotes.id"), nullable=False),
        sa.Column("part_number", sa.String(), nullable=True),
        sa.Column("description", sa.String(), nullable=False),
        sa.Column("quantity", sa.Numeric(12, 2), nullable=False),
        sa.Column("unit_price", sa.Numeric(12, 2), nullable=False),
    )

    # -- invoice_drafts --
    op.create_table(
        "invoice_drafts",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("order_id", sa.Integer(), sa.ForeignKey("orders.id"), nullable=False),
        sa.Column("margin_pct", sa.Numeric(5, 2), nullable=False),
        sa.Column("tax_rate", sa.Numeric(5, 4), nullable=False),
        sa.Column("subtotal", sa.Numeric(12, 2), nullable=False),
        sa.Column("total", sa.Numeric(12, 2), nullable=False),
        sa.Column("status", sa.String(), nullable=False, server_default="pending_approval"),
        sa.Column("pdf_path", sa.String(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column("approved_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("sent_at", sa.DateTime(timezone=True), nullable=True),
    )

    # -- catalogs --
    op.create_table(
        "catalogs",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("part_category", sa.String(), nullable=False),
        sa.Column("file_name", sa.String(), nullable=False),
        sa.Column("file_path", sa.String(), nullable=False),
        sa.Column("whatsapp_url", sa.String(), nullable=True),
        sa.Column("keywords", sa.String(), nullable=False, server_default=""),
        sa.Column("active", sa.Boolean(), nullable=False, server_default=sa.text("true")),
    )

    # -- lead_contacts --
    op.create_table(
        "lead_contacts",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("title", sa.String(), nullable=False),
        sa.Column("company", sa.String(), nullable=False),
        sa.Column("linkedin_url", sa.String(), nullable=True),
        sa.Column("whatsapp_number", sa.String(), nullable=True),
        sa.Column("source_company", sa.String(), nullable=True),
        sa.Column("contacted_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("status", sa.String(), nullable=False, server_default="new"),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
    )

    # -- margin_configs --
    op.create_table(
        "margin_configs",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("part_category", sa.String(), nullable=False),
        sa.Column("margin_pct", sa.Numeric(5, 2), nullable=False),
    )

    # -- tax_configs --
    op.create_table(
        "tax_configs",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("tax_name", sa.String(), nullable=False),
        sa.Column("rate_pct", sa.Numeric(5, 2), nullable=False),
    )

    # -- approval_requests --
    op.create_table(
        "approval_requests",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("entity_type", sa.String(), nullable=False),
        sa.Column("entity_id", sa.Integer(), nullable=False),
        sa.Column("amount", sa.Numeric(12, 2), nullable=True),
        sa.Column("reason", sa.String(), nullable=False),
        sa.Column("status", sa.String(), nullable=False, server_default="pending"),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column("resolved_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("resolved_by", sa.String(), nullable=True),
    )

    # -- approval_request_logs --
    op.create_table(
        "approval_request_logs",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("request_id", sa.Integer(), sa.ForeignKey("approval_requests.id"), nullable=False),
        sa.Column("status", sa.String(), nullable=False),
        sa.Column("actor", sa.String(), nullable=False),
        sa.Column("action", sa.String(), nullable=False),
        sa.Column("note", sa.String(), nullable=True),
        sa.Column(
            "timestamp",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
    )

    # -- audit_logs --
    op.create_table(
        "audit_logs",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column(
            "timestamp",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column("agent_id", sa.String(), nullable=False),
        sa.Column("action", sa.String(), nullable=False),
        sa.Column("actor", sa.String(), nullable=False),
        sa.Column("outcome", sa.String(), nullable=False),
        sa.Column("order_id", sa.Integer(), nullable=True),
        sa.Column("metadata", postgresql.JSONB(), nullable=True),
        sa.Column("retained_until", sa.DateTime(timezone=True), nullable=True),
    )


def downgrade() -> None:
    op.drop_table("audit_logs")
    op.drop_table("approval_request_logs")
    op.drop_table("approval_requests")
    op.drop_table("tax_configs")
    op.drop_table("margin_configs")
    op.drop_table("lead_contacts")
    op.drop_table("catalogs")
    op.drop_table("invoice_drafts")
    op.drop_table("dealer_quote_items")
    op.drop_table("dealer_quotes")
    op.drop_table("dealers")
    op.drop_table("line_items")
    op.drop_table("order_items")
    op.drop_table("orders")
    op.drop_table("client_contacts")
    op.drop_table("clients")