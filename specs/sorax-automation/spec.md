# Feature Specification: Sorax AI Automation System

**Feature Branch**: `sorax-automation`  
**Created**: 2025-06-13  
**Status**: Draft  
**Input**: User description: "Build an AI automation system for Sorax Industrial Solution..."

This spec is governed by the Sorax Industrial Solution Automation Constitution (`.specify/memory/constitution.md`).

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Generate Invoice Draft (Priority: P1) 🎯 MVP

**As the** business owner, **I want** the system to generate an invoice draft with my configured profit margin and taxes after a dealer quote is selected, **so that** I can review and approve it before sending to the client.

**Why this priority**: P1 — the invoice is the contractual and financial commitment step; without it the pipeline cannot close.

**Independent Test**: A test can simulate a selected dealer quote (itemized list + unit price) and verify a PDF invoice is generated within 1 minute, with correct margin and tax applied, and routed to the owner for approval (not sent to client).

**Acceptance Scenarios**:

1. **Given** a chosen dealer quote with part number, description, quantity, and unit price, **When** the Quotation and Invoice Agent processes it, **Then** it applies the configured profit margin percentage and tax rate, generates a PDF with line items, subtotal, margin, taxes, and total, and presents it for owner approval.
2. **Given** no margin/tax config exists for a part category, **When** an invoice is requested, **Then** the system flags the missing config and asks the owner to set it, rather than inventing a value (Per Constitution Principle IV — Accuracy).
3. **Given** an invoice draft is generated, **When** the owner has not approved it, **Then** it is NOT sent to the client and is logged as "pending approval" (Per Constitution Principle I — Human-in-the-Loop).

---

### User Story 2 - Structured Order Intake (Priority: P1)

**As the** business owner, **I want** client order emails to be parsed into structured data (items, quantities, specs) within 2 minutes, **so that** I don't have to manually transcribe orders.

**Why this priority**: P1 — upstream of invoicing; if the order isn't captured correctly, the invoice and sourcing will be wrong.

**Independent Test**: A test can feed a sample order email (in the existing format clients use) and verify the extracted structured order matches expected items, quantities, and specs within 120 seconds.

**Acceptance Scenarios**:

1. **Given** a client order email arrives in the owner's inbox (or is forwarded), **When** the Order Intake Agent processes it, **Then** it produces a structured order (part number/description, quantity, unit) and sends an order-received email to the client within 2 minutes.
2. **Given** an email with an unrecognized part or ambiguous spec, **When** the Order Intake Agent parses it, **Then** it flags the unknown item, says so explicitly, and escalates to the owner rather than guessing (Per Constitution Principle IV).
3. **Given** a structured order is created, **When** it is saved, **Then** an audit log entry is written with timestamp, source email, and extracted data (Per Constitution Principle V — Auditability).

---

### User Story 3 - Dealer RFQ Dispatch (Priority: P2)

**As the** business owner, **I want** the system to send WhatsApp RFQs to my Saddar dealers without manual typing, **so that** I get competitive quotes faster.

**Why this priority**: P2 — required to get the data needed for owner-approved invoicing, but secondary to the core order→invoice flow.

**Independent Test**: A test can trigger an RFQ for a set of parts and verify that WhatsApp messages are sent via the Meta Business Cloud API to the configured Saddar dealer contacts, without manual typing.

**Acceptance Scenarios**:

1. **Given** a structured order, **When** the owner approves, **Then** the Dealer Sourcing Agent sends a WhatsApp RFQ (part number, description, quantity) to all configured Saddar dealers via the official Meta Business Cloud API (Per Constitution Principle II — Compliance).
2. **Given** a dealer replies with a quote, **When** the Dealer Sourcing Agent receives it, **Then** it extracts the quoted price and normalizes it into the comparison dashboard for owner review.
3. **Given** a dealer does not respond within 24 hours, **When** the Follow-up Agent runs, **Then** it sends a WhatsApp reminder to that dealer (owner-approved template only).

---

### User Story 4 - Follow-up & CRM Tracking (Priority: P2)

**As the** business owner, **I want** the system to send weekly follow-up emails to every client and track replies, **so that** I don't lose orders to inaction.

**Why this priority**: P2 — retention/delivery hygiene; not blocking the core order→invoice→ship cycle.

**Independent Test**: A test can set a client's last-contact date, run the Follow-up Agent, and verify a follow-up email is sent if 7 days have passed, and that a reply (simulated) is recorded in the CRM data store.

**Acceptance Scenarios**:

1. **Given** a client with an outstanding (unpaid / unfulfilled) order, **When** 7 days have passed since last contact, **Then** the Follow-up Agent sends a follow-up email and logs the send timestamp.
2. **Given** a client replies to a follow-up email, **When** the reply is received, **Then** the Follow-up Agent records the reply content and timestamp in the CRM and notifies the owner.
3. **Given** a client with no recent activity, **When** the Follow-up Agent runs weekly, **Then** only one follow-up email is sent per week per client (no spam).

---

### User Story 5 - Lead Discovery & Connection Drafting (Priority: P3)

**As the** business owner, **I want** the Lead Agent to find procurement/supply-chain contacts and draft LinkedIn connection + follow-up messages, **so that** I can send them manually.

**Why this priority**: P3 — top-of-funnel; important for growth but not for completing an existing order.

**Independent Test**: A test can run the Lead Agent against a seeded LinkedIn search result set and verify it outputs a draft connection request and follow-up message containing the company bio, for the owner to send manually.

**Acceptance Scenarios**:

1. **Given** a target company in Pakistan in the electrical/industrial procurement domain, **When** the Lead Agent searches LinkedIn, **Then** it identifies procurement/supply-chain contacts and drafts a connection request + follow-up message with the company bio (Per Constitution Principle II — no auto LinkedIn actions; owner sends manually).
2. **Given** a drafted message, **When** the owner reviews it, **Then** the owner can edit and send it manually; the sent event is logged (Per Constitution Principle V — Auditability).
3. **Given** a contact responds with a WhatsApp number, **When** the Lead Agent captures it, **Then** it enriches the CRM contact record with the number for the Catalog Agent to use.

---

### User Story 6 - Catalog Distribution (Priority: P3)

**As the** business owner, **I want** the Catalog Agent to respond to WhatsApp inquiries with the right catalog, **so that** potential clients get the right product list without me typing it.

**Why this priority**: P3 — part of lead nurturing; depends on Lead Agent bringing in contacts.

**Independent Test**: A test can simulate a WhatsApp inquiry for a specific part category and verify the Catalog Agent responds with the correct catalog file/URL via the official WhatsApp Business Cloud API.

**Acceptance Scenarios**:

1. **Given** a WhatsApp inquiry from a lead asking for a specific product category (e.g., "motor parts"), **When** the Catalog Agent receives it, **Then** it replies with the relevant catalog via the official WhatsApp Business Cloud API (Per Constitution Principle II — Compliance).
2. **Given** an inquiry for an unknown category, **When** the Catalog Agent receives it, **Then** it responds with a generic greeting and escalates to the owner with the inquiry logged.
3. **Given** a catalog is sent, **When** the lead requests a quotation, **Then** the Catalog Agent tags the conversation for the Order Intake / Quotation flow.

---

## Clarifications

### Session 2025-06-13

- Q: How should profit margins be configured for invoice generation? → A: Per-part-category percentage — one rate per category (e.g., electrical parts: 25%, motor parts: 20%).
- Q: How should dealer quotes be compared for owner selection? → A: Per-dealer quote detail pages with full reply navigation; owner reviews each dealer's detailed quote before choosing.
- Q: How should WhatsApp conversations be modeled across agents? → A: One thread per counterparty (client or dealer) on a single Sorax business number; messages stored with order_id and message_type (RFQ, quote_reply, invoice, follow_up); dealers never see other dealers' messages.
- Q: How should the system access client order emails? → A: Read-only IMAP to owner's email with sender whitelist, SPF/DKIM checks; unknown senders go to a "needs review" queue; email content treated as data only, never agent instructions.
- Q: How should the Manager agent coordinate specialist agents? → A: Single OpenAI Agents SDK workflow with Manager handoffs to specialists; state in PostgreSQL; owner approval via SDK interrupts.

## Edge Cases

- What happens when the Order Intake Agent receives an email with a part not in the local catalog? → Flag as unknown, escalate to owner, do not invent specs (Principle IV).
- How does the system handle a dealer who sends an RFQ reply in a non-standard format? → Log the raw reply, attempt structured extraction, and if confidence is low, flag for owner review.
- What happens when the owner is unreachable for invoice approval (e.g., on travel)? → The invoice draft is saved as "pending approval" and a reminder is surfaced on next login; no client-facing money figure is sent (Principle I).
- What happens when WhatsApp API rate limits are hit? → Dealer RFQs are queued with backoff and retried; owner is notified of delay.
- What happens when a client's order email has ambiguous quantities (e.g., "a few")? → Flag for owner clarification; do not assume a number (Principle IV).
- What happens when an email is received from a sender not on the approved client list? → Email goes to a "needs review" queue; owner must explicitly approve before parsing into an order.
- What happens when an email fails SPF/DKIM verification? → Email is flagged as untrusted, goes to the "needs review" queue, and is not auto-processed (Principle III).

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: Order Intake Agent MUST parse a client order email into structured data (part number/description, quantity, unit) within 2 minutes.
- **FR-002**: Order Intake Agent MUST send an order-received confirmation email to the client after parsing.
- **FR-003**: Dealer Sourcing Agent MUST send WhatsApp RFQs to configured Saddar dealers via the official Meta Business Cloud API using one thread per counterparty.
- **FR-004**: Dealer Sourcing Agent MUST collect and normalize dealer quote replies into per-dealer detail pages for owner comparison.
- **FR-005**: Quotation and Invoice Agent MUST apply the owner-configured per-part-category profit margin and tax rates.
- **FR-006**: Quotation and Invoice Agent MUST generate a PDF invoice draft and route it for owner approval before client send.
- **FR-007**: Follow-up Agent MUST send a weekly follow-up email to each client with an outstanding order if 7 days have passed since last contact.
- **FR-008**: Follow-up Agent MUST record client replies in the CRM.
- **FR-009**: Lead Agent MUST find procurement/supply-chain contacts on LinkedIn for target companies in Pakistan; catalog inquiries handled via WhatsApp thread per counterparty.
- **FR-010**: Lead Agent MUST draft LinkedIn connection and follow-up messages for the owner to send manually; captured WhatsApp numbers enrich CRM contact records.
- **FR-011**: Catalog Agent MUST respond to WhatsApp inquiries with the relevant catalog via the official WhatsApp Business Cloud API.
- **FR-012**: Manager agent MUST coordinate the 6 specialist agents via handoffs within a single OpenAI Agents SDK workflow; state persisted in PostgreSQL; owner approval enforced via SDK interrupts.
- **FR-013**: System MUST log every agent action, dealer quote, and client-facing message with a timestamp (audit trail).
- **FR-014**: System MUST ensure 100% of client-facing money figures (invoice totals, quoted prices) require explicit owner approval before send.

### Key Entities

- **Order**: client, items[], status, source_email, created_at
- **LineItem**: part_number, description, quantity, unit
- **Dealer**: name, whatsapp_number, location (e.g., Saddar), active
- **DealerQuote**: dealer_id, order_id, line_items[], total, quoted_at, raw_reply, status (pending/selected/rejected)
- **InvoiceDraft**: order_id, line_items[], margin_pct, tax_rate, subtotal, total, status (pending_approval/sent), pdf_url, created_at
- **ClientContact**: name, email, whatsapp_number (if provided), company, last_contacted_at, crm_status
- **LeadContact**: name, title, company, linkedin_url, source_company
- **AuditLog**: timestamp, agent_id, action, actor (agent/owner), outcome, metadata
- **MarginConfig**: part_category, margin_pct
- **TaxConfig**: tax_name, rate_pct

### Non-functional Requirements (from Constitution)

- **NFR-001**: All secrets (WhatsApp API token, IMAP credentials, DB credentials) MUST be loaded from environment variables only (Principle III).
- **NFR-002**: No automated LinkedIn messaging — Lead Agent drafts only; owner sends manually (Principle II).
- **NFR-003**: WhatsApp integration MUST use the official Meta Business Cloud API only (Principle II). One thread per counterparty on a single Sorax business number; dealer messages never visible to other dealers.
- **NFR-004**: Agents MUST never invent prices, stock, or part specs; MUST escalate unknowns (e.g., unknown sender, unknown part, low-confidence quote extraction) to the owner (Principle IV).
- **NFR-005**: All client-facing financial figures MUST be owner-approved via SDK interrupts before leaving the system (Principle I).
- **NFR-006**: All core logic MUST have pytest tests; code MUST use type hints and be modular (Principle VI).
- **NFR-007**: Email source MUST connect via read-only IMAP with SPF/DKIM verification; only pre-approved sender list is auto-processed (Principle III).

## Success Criteria *(mandatory)*

1. **SC-001**: An order email becomes a structured order within 2 minutes (tested via simulated email input → structured Order verification).
2. **SC-002**: Dealer RFQs are sent via WhatsApp without manual typing (tested via API mock → verify message sent to correct dealer contacts).
3. **SC-003**: Invoice drafts are generated in under 1 minute after a quote is chosen (tested via chosen-quote input → PDF invoice verification).
4. **SC-004**: 100% of client-facing money figures are owner-approved (tested via audit-log scan of all client invoices/quotes).

## Out of Scope

- Auto-negotiation of final price with dealers or clients.
- Automated LinkedIn actions (connection requests sent by bot, messages sent without owner review).
- Phone calls (no voice/VoIP automation).
- Payment processing (no automated receipt generation, no payment gateway integration).
- Inventory management (stock levels, purchase order creation to dealers beyond RFQ).