# Implementation Plan: Sorax AI Automation System

**Branch**: `sorax-automation` | **Date**: 2025-06-13 | **Spec**: `specs/sorax-automation/spec.md`
**Input**: Feature specification from `/specs/sorax-automation/spec.md`

**Note**: This template is filled in by the `/sp.plan` command. See `.specify/templates/commands/plan.md` for the execution workflow.

## Summary

A multi-agent AI automation system for Sorax Industrial Solution (Pakistan-based industrial supplies procurement). One Manager agent (OpenAI Agents SDK) coordinates 6 specialist agents: Lead, Catalog, Order Intake, Dealer Sourcing, Quotation & Invoice, and Follow-up. Built on FastAPI + PostgreSQL with Gmail API, WhatsApp Cloud API, and WeasyPrint integrations. Owner approval enforced via OpenAI Agents SDK interrupts for all client-facing financial figures.

## Technical Context

**Language/Version**: Python 3.12  
**Primary Dependencies**: FastAPI, SQLModel, OpenAI Agents SDK, Alembic, WeasyPrint, httpx (WhatsApp Cloud API + Gmail API clients), APScheduler  
**Storage**: PostgreSQL  
**Testing**: pytest with mocked Gmail/WhatsApp clients  
**Target Platform**: Linux server / VPS (Docker-compose)  
**Project Type**: Single backend project (API + agents), separate frontend dashboard (Next.js + Tailwind) for approvals  
**Performance Goals**: Order intake <120s, invoice generation <60s  
**Constraints**: No automated LinkedIn actions; owner must approve all financial figures before client send; WhatsApp via official Meta Business Cloud API only  
**Scale/Scope**: Single owner user, ~10-20 Saddar dealers, small-medium Pakistani industrial procurement clients  

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- ✅ **Principle I (Human-in-the-Loop)**: Owner approval required for all client-facing money figures. Enforced via `ApprovalRequest` table + OpenAI Agents SDK interrupts. Invoice drafts are "pending_approval" until owner approves.
- ✅ **Principle II (Compliance)**: No automated LinkedIn actions — Lead Agent drafts only, owner sends manually. WhatsApp uses official Meta Business Cloud API only.
- ✅ **Principle III (Data Safety)**: Secrets via env vars only (NFR-001, NFR-007). Read-only IMAP with SPF/DKIM checks; sender whitelist enforced.
- ✅ **Principle IV (Accuracy)**: Unknown parts, ambiguous specs, low-confidence extractions all escalate to owner — no invented values.
- ✅ **Principle V (Auditability)**: `AuditLog` entity with timestamp, agent_id, action, actor, outcome. All agent actions, dealer quotes, messages logged.
- ✅ **Principle VI (Tech Standards)**: Python 3.12, FastAPI, PostgreSQL, OpenAI Agents SDK, type hints, pytest tests for core logic, small modular code.
- ✅ **Principle VII (Simplicity First)**: Single OpenAI Agents SDK workflow. Single WhatsApp business number. Per-part-category margin (not per-item). No speculative generalizations.
- ✅ **Principle VIII (Spec-Driven)**: This plan, spec, and tasks are approved before code begins.

## Project Structure

### Documentation (this feature)

```text
specs/sorax-automation/
├── spec.md              # Feature specification
├── plan.md              # This file (/sp.plan command output)
├── research.md          # Phase 0 output (/sp.plan command)
├── data-model.md        # Phase 1 output (/sp.plan command)
├── quickstart.md        # Phase 1 output (/sp.plan command)
└── contracts/           # Phase 1 output (/sp.plan command)
```

### Source Code (repository root)

```text
backend/
├── src/
│   ├── models/          # SQLModel entities (Client, Order, Dealer, etc.)
│   ├── services/        # External clients (GmailClient, WhatsAppClient, PDFGenerator)
│   ├── agents/          # OpenAI Agents SDK: Manager + 6 specialists
│   │   ├── manager.py
│   │   ├── lead.py
│   │   ├── catalog.py
│   │   ├── order_intake.py
│   │   ├── dealer_sourcing.py
│   │   ├── quotation_invoice.py
│   │   └── follow_up.py
│   ├── api/             # FastAPI routers
│   │   ├── orders.py
│   │   ├── invoices.py
│   │   ├── approvals.py
│   │   ├── dealers.py
│   │   └── webhooks.py  # WhatsApp webhook receiver
│   ├── core/            # Config, DB session, logging setup
│   ├── jobs/            # APScheduler background jobs (email polling, follow-ups)
│   └── main.py          # FastAPI entrypoint
├── tests/
│   ├── unit/
│   ├── integration/
│   └── contract/
├── alembic/             # Migrations
├── Dockerfile
└── requirements.txt

frontend/
├── app/                 # Next.js 14 app router
├── components/          # Approval dashboard UI
└── public/              # Catalog PDF files
```

**Structure Decision**: Separated into `backend/` (agents + API) and `frontend/` (Next.js approval dashboard) for clear separation of concerns. Backend handles all agent orchestration and external integrations; frontend is a thin approval surface for the owner.

## Complexity Tracking

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| Separate frontend backend | Owner needs a simple web UI to approve invoices/quotes | Could use WhatsApp-only approval — but PDF invoices need a richer review surface than WhatsApp allows |
| APScheduler vs Celery | Background jobs (weekly follow-ups, email polling) | Celery adds Redis/rabbitmq infra — overkill for single-owner use case; APScheduler fits single-process VPS model |

## Research Notes (Phase 0)

- **WhatsApp Business Cloud API**: Official endpoint is `https://graph.facebook.com/v21.0/<PHONE_NUMBER>/messages` (or messages/{message-id}). Requires access token + phone number ID. Rate limits apply (200 req/sec per phone number, 1000/day per WABA). Webhook setup required at `/webhooks/whatsapp`.
- **Gmail API**: Requires OAuth 2.0 client credentials. IMAP alternative may be simpler for read-only access. SPF/DKIM verification requires fetching email headers and checking authentication results headers added by Gmail.
- **OpenAI Agents SDK**: Handoffs allow agent-to-agent control transfer. Interrupts allow owner approval mid-flow — critical for Principle I compliance.
- **WeasyPrint**: Renders HTML+CSS to PDF; suitable for invoice drafts with line items and styling.
- **Saddar dealers**: Physical market area in Karachi; WhatsApp is the dominant business communication channel.

## Data Model Notes (Phase 1)

Key entity relationships:
- `Client` → `Order[]`, `ClientContact[]`
- `Order` → `OrderItem[]`, `InvoiceDraft`, `DealerQuote[]`
- `Dealer` → `DealerQuote[]`, WhatsApp threads via `whatsapp_number`
- `ApprovalRequest` → references `InvoiceDraft` or other entities requiring owner review
- `AuditLog` → standalone, written by all agents

Margin model: `MarginConfig(part_category, margin_pct)` — owner sets one percentage per part category (electrical, motor, general industrial).

Invoice flow: `Order` → `DealerQuote` (selected) → `InvoiceDraft` (pending_approval) → `ApprovalRequest` (owner approves) → send via WhatsApp/email → log.

## Key Decisions and Rationale

1. **Single OpenAI Agents SDK workflow** (not distributed microservices): Matches Constitution Principle VII (simplicity first). Reduces infra complexity for a single-owner business.
2. **IMAP with sender whitelist** (not dedicated order mailbox): No DNS changes needed; owner uses existing email. Whitelist + SPF/DKIM prevents untrusted input (Principle III, IV).
3. **Per-dealer quote detail pages** (not line-by-line comparison table): Simpler UX for owner to review full dealer replies; aligns with how a procurement owner naturally compares supplier offers.
4. **Docker-compose on single VPS** (not Railway cloud): Better for a Pakistani business where local hosting may be more reliable and cost-effective; avoids vendor lock-in.
5. **APScheduler over Celery**: No need for Redis/RabbitMQ infra for this scale (Principle VII).
6. **Separate Next.js frontend for approval dashboard**: PDF invoices need a richer review surface than WhatsApp allows; Next.js provides a simple, fast approval UI.

## Interfaces and API Contracts

### WhatsApp Cloud API (Meta Business Cloud API)
- **Send**: `POST /v21.0/{phone_number_id}/messages` with JSON body → 200 OK or error
- **Webhook** (incoming messages): `POST /webhooks/whatsapp` → validate signature, parse inbound message
- **Errors**: Rate limit (429), invalid token (401), message format error (100)
- **Idempotency**: N/A (WhatsApp handles deduplication)

### Gmail API (or IMAP fallback)
- **Read orders**: IMAP `SEARCH FROM <sender>` or Gmail API `users.messages.list` + `users.messages.get`
- **Send emails**: SMTP or Gmail API `users.messages.send`
- **Errors**: Auth failure (401), rate limit (429), label not found (404)

### OpenAI Agents SDK
- **Handoffs**: Manager → specialist; context transferred
- **Interrupts**: Owner approval; workflow pauses, owner responds via dashboard, workflow resumes
- **Tools**: Each specialist exposes typed tools (Pydantic outputs)

### Approval Dashboard API (FastAPI)
- `GET /api/approvals` — list pending approval requests
- `POST /api/approvals/{id}/approve` — owner approves
- `POST /api/approvals/{id}/reject` — owner rejects (escalates back to agent)

## Non-Functional Requirements and Budgets

- **Order intake latency**: <120s from email receipt to structured order (SC-001)
- **Invoice generation latency**: <60s from quote selection (SC-003)
- **Follow-up scheduling**: Weekly cron via APScheduler
- **WhatsApp message isolation**: Dealer-to-dealer messages must never be visible (NFR-003) — enforced at message routing layer
- **Audit log completeness**: 100% of agent actions logged with timestamp (FR-013, Principle V)
- **Secrets**: All via env vars; `.env.example` provided, `.env` in `.gitignore` (NFR-001, Principle III)

## Data Management and Migration

- **Source of truth**: PostgreSQL database
- **Schema evolution**: Alembic migrations, one per entity change
- **Migration/rollback**: Standard Alembic upgrade/downgrade; no data-destructive migrations without explicit owner action
- **Data retention**: Audit log retained indefinitely; orders/invoices retained per Pakistani tax compliance (7+ years); soft-delete for CRM contacts
- **Backups**: Daily `pg_dump` to encrypted volume; owner notified of failures

## Operational Readiness

- **Observability**: Structured JSON logs (timestamp, agent_id, action, outcome) → stdout; audit trail in DB
- **Alerting**: Owner notified via WhatsApp if email polling fails, WhatsApp API errors persist, or approval pending >48h
- **Runbooks**: `docs/runbooks/email-polling-failure.md`, `docs/runbooks/approval-backlog.md`
- **Deployment**: `docker-compose up -d` on VPS; env vars set via `.env`
- **Rollback**: `git tag` per release; `docker-compose down -v` + restore DB from backup; Alembic downgrade for schema
- **Feature flags**: N/A (small system; principle VII — simplicity first)

## Risk Analysis and Mitigation

1. **WhatsApp API rate limits blocking dealer RFQs**: Mitigation — queue with backoff (already in edge cases); batch RFQs per order.
2. **Gmail/IMAP auth expiration breaking order intake**: Mitigation — alert owner via WhatsApp; "needs review" queue prevents data loss.
3. **OpenAI API failures blocking all agent workflows**: Mitigation — agents fall back to human review mode; log failure; notify owner.
4. **Owner unreachable while invoice pending approval**: Mitigation — "pending approval" saved in DB; reminder on next login; no auto-expiry (no client-facing money figure sent until approved).
5. **Dealer sends quote in non-parseable format**: Mitigation — raw reply always stored; flagged for owner review (Principle IV).

## Evaluation and Validation

- **Definition of Done**: All Phase 1–3 user stories pass their independent tests; `pytest` coverage ≥80% for core logic; Dockerfile builds; spec scenarios pass.
- **Output Validation**: Invoice PDF must include owner-approved margin and tax; audit log must contain owner approval event before any client-facing send.

## Architectural Decision Record (ADR)

1. **`adr/01-single-agent-workflow.md`** — Single OpenAI Agents SDK workflow vs. distributed microservices
2. **`adr/02-imap-with-whitelist.md`** — IMAP with sender whitelist vs. dedicated order mailbox
3. **`adr/03-docker-compose-deployment.md`** — Docker-compose on VPS vs. Railway cloud hosting