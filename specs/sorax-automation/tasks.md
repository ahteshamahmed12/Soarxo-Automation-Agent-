# Tasks: Sorax AI Automation System

**Input**: Design documents from `/specs/sorax-automation/`
**Prerequisites**: plan.md (required), spec.md (required for user stories), ADR-001, ADR-002, ADR-003

**Tests**: Core logic tests included per Constitution NFR-006 (Principle VI). pytest with mocked Gmail/WhatsApp clients.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story?] Description`

- **[P]**: Can run in parallel (different files, no dependencies on incomplete tasks)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

- **Backend**: `backend/src/`, `backend/tests/`
- **Frontend**: `frontend/app/`, `frontend/components/`

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and basic structure

- [ ] T001 Initialize Python 3.12 project with FastAPI + SQLModel + OpenAI Agents SDK in `backend/requirements.txt`
- [ ] T002 Set up Alembic migrations in `backend/alembic/` with config in `backend/alembic.ini`
- [ ] T003 Create project structure: `backend/src/{models,services,agents,api,core,jobs}` and `backend/tests/{unit,integration,contract}`
- [ ] T004 Create `backend/.env.example` with all required env vars (DB, OpenAI, Gmail, WhatsApp)
- [ ] T005 Create `docker-compose.yml` with backend, PostgreSQL, and frontend services per ADR-003
- [ ] T006 [P] Configure linting/formatting (ruff, mypy) in `backend/pyproject.toml`
- [ ] T007 [P] Set up pytest config in `backend/pyproject.toml`

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**CRITICAL**: No user story work can begin until this phase is complete

- [ ] T008 Create SQLModel database config and session management in `backend/src/core/database.py`
- [ ] T009 Create shared models: Client, Contact, Order, OrderItem, Dealer, DealerQuote, InvoiceDraft, AuditLog, ApprovalRequest, MarginConfig, TaxConfig in `backend/src/models/__init__.py`
- [ ] T010 [P] Create `backend/src/core/config.py` with Pydantic settings (env-var loaded secrets)
- [ ] T011 [P] Create `backend/src/core/logging.py` with structured JSON logging
- [ ] T012 Create `backend/src/services/whatsapp_client.py` for Meta Business Cloud API (send + webhook validation)
- [ ] T013 [P] Create `backend/src/services/gmail_client.py` for read-only IMAP email polling with SPF/DKIM checks
- [ ] T014 Create `backend/src/services/pdf_generator.py` using WeasyPrint for invoice PDFs
- [ ] T015 Create Alembic migration for all foundational models in `backend/alembic/versions/`
- [ ] T016 Create `backend/tests/conftest.py` with mocked DB, WhatsApp, Gmail, OpenAI clients
- [ ] T017 Create `backend/src/agents/approval.py` - ApprovalRequest manager with interrupt handler

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 2 - Structured Order Intake (Priority: P1) 🎯 MVP

**Goal**: Client order emails are parsed into structured Order data within 2 minutes, order-received confirmation sent.

**Independent Test**: Feed a sample order email; verify structured Order in DB and confirmation email sent within 120 seconds.

### Tests for User Story 2

- [ ] T018 [P] [US2] Unit test for LineItem extraction logic in `backend/tests/unit/test_order_intake.py`
- [ ] T019 [P] [US2] Unit test for Order model validation in `backend/tests/unit/test_order_intake.py`

### Implementation for User Story 2

- [X] T020 Create Order and OrderItem models in `backend/src/models/order.py`
- [X] T021 [P] Create Client and ClientContact models in `backend/src/models/client.py`
- [X] T022 Create OrderIntakeAgent in `backend/src/agents/order_intake.py` with email parsing tool
- [X] T023 Create `backend/src/services/email_parser.py` for order email extraction with unknown-part escalation
- [X] T024 Create email polling job in `backend/src/jobs/email_polling.py` using APScheduler
- [X] T025 [P] Create order-received email template in `backend/src/templates/email_received.html`
- [X] T026 Add integration test for full order intake flow in `backend/tests/integration/test_order_intake_flow.py`

**Checkpoint**: User Story 2 should be fully functional and testable independently

---

## Phase 4: User Story 1 - Generate Invoice Draft (Priority: P1) 🎯 MVP

**Goal**: After a dealer quote is selected and approved, generate an invoice PDF draft and route for owner approval. All financial figures require owner approval before client send.

**Independent Test**: Feed a selected dealer quote; verify InvoiceDraft in DB with correct margin/tax applied and ApprovalRequest created (no PDF sent to client).

### Tests for User Story 1

- [ ] T027 [P] [US1] Unit test for margin calculation (per-part-category) in `backend/tests/unit/test_margin_calc.py`
- [ ] T028 [P] [US1] Unit test for tax calculation in `backend/tests/unit/test_tax_calc.py`
- [ ] T029 [P] [US1] Unit test for DealerQuote model validation in `backend/tests/unit/test_dealer_quote.py`

### Implementation for User Story 1

- [ ] T030 Create QuotationInvoiceAgent in `backend/src/agents/quotation_invoice.py` with invoice generation tool
- [ ] T031 Create Dealer and DealerQuote models in `backend/src/models/dealer.py`
- [ ] T032 Create InvoiceDraft model in `backend/src/models/invoice.py`
- [ ] T033 Create `backend/src/templates/invoice_template.html` for WeasyPrint rendering
- [ ] T034 Create ApprovalRequest model in `backend/src/models/approval.py`
- [ ] T035 [P] Create FastAPI router for invoice draft API in `backend/src/api/invoices.py`
- [ ] T036 [P] Create FastAPI router for approval requests in `backend/src/api/approvals.py`
- [ ] T037 Add integration test for invoice generation flow in `backend/tests/integration/test_invoice_flow.py`

**Checkpoint**: User Story 1 should be fully functional and testable independently

---

## Phase 5: User Story 3 - Dealer RFQ Dispatch (Priority: P2)

**Goal**: After order intake, send WhatsApp RFQs to Saddar dealers without manual typing; collect and normalize replies.

**Independent Test**: Trigger RFQ for a chosen order; verify WhatsApp messages sent to correct dealer contacts via API mock; verify quote reply parsing.

### Tests for User Story 3

- [ ] T038 [P] [US3] Unit test for WhatsApp message payload builder in `backend/tests/unit/test_whatsapp_client.py`
- [ ] T039 [P] [US3] Unit test for DealerQuote extraction from WhatsApp reply in `backend/tests/unit/test_dealer_sourcing.py`

### Implementation for User Story 3

- [ ] T040 Create DealerSourcingAgent in `backend/src/agents/dealer_sourcing.py` with RFQ dispatch tool
- [ ] T041 Create WhatsApp webhook receiver in `backend/src/api/webhooks.py` (verify signature, parse inbound message)
- [ ] T042 Create `backend/src/services/dealer_manager.py` for dealer contact registry (Saddar dealers)
- [ ] T043 [P] Create WhatsApp rate-limit queue in `backend/src/services/whatsapp_queue.py`
- [ ] T044 Add integration test for RFQ dispatch flow in `backend/tests/integration/test_rfq_dispatch.py`

**Checkpoint**: User Story 3 should be fully functional and testable independently

---

## Phase 6: User Story 4 - Follow-up & CRM Tracking (Priority: P2)

**Goal**: Send weekly follow-up emails to clients with outstanding orders; track replies in CRM.

**Independent Test**: Set a client last-contact date 8 days ago; run Follow-up Agent; verify follow-up email sent and reply recorded.

### Tests for User Story 4

- [ ] T045 [P] [US4] Unit test for follow-up scheduling logic in `backend/tests/unit/test_followup.py`
- [ ] T046 [P] [US4] Unit test for reply parsing logic in `backend/tests/unit/test_reply_parser.py`

### Implementation for User Story 4

- [ ] T047 Create FollowUpAgent in `backend/src/agents/follow_up.py` with email scheduling tool
- [ ] T048 Create `backend/src/jobs/followup_scheduler.py` using APScheduler (weekly cron)
- [ ] T049 [P] Create `backend/src/templates/email_followup.html` template
- [ ] T050 Add integration test for follow-up flow in `backend/tests/integration/test_followup_flow.py`

**Checkpoint**: User Story 4 should be fully functional and testable independently

---

## Phase 7: User Story 6 - Catalog Distribution (Priority: P3)

**Goal**: Respond to WhatsApp inquiries with the right catalog file/URL via the official WhatsApp Business Cloud API.

**Independent Test**: Simulate a WhatsApp inquiry for "motor parts"; verify Catalog Agent responds with the correct catalog URL via API mock.

### Tests for User Story 6

- [ ] T051 [P] [US6] Unit test for catalog routing logic in `backend/tests/unit/test_catalog.py`

### Implementation for User Story 6

- [ ] T052 Create CatalogAgent in `backend/src/agents/catalog.py` with inquiry response tool
- [ ] T053 Create `backend/src/models/catalog.py` with Catalog entity (part_category, file_path, whatsapp_url)
- [ ] T054 [P] Create `backend/src/services/catalog_store.py` for catalog file registry
- [ ] T055 Create `frontend/public/catalogs/` directory and add catalog PDF files
- [ ] T056 Add integration test for catalog dispatch in `backend/tests/integration/test_catalog_flow.py`

**Checkpoint**: User Story 6 should be fully functional and testable independently

---

## Phase 8: User Story 5 - Lead Discovery & Connection Drafting (Priority: P3)

**Goal**: Find procurement/supply-chain contacts on LinkedIn for target Pakistani companies; draft connection + follow-up messages for owner to send manually.

**Independent Test**: Run Lead Agent against a seeded LinkedIn result set; verify output draft message contains company bio. No automated LinkedIn actions.

### Tests for User Story 5

- [ ] T057 [P] [US5] Unit test for LinkedIn profile parsing in `backend/tests/unit/test_lead_agent.py`
- [ ] T058 [P] [US5] Unit test for draft message generation in `backend/tests/unit/test_lead_draft.py`

### Implementation for User Story 5

- [ ] T059 Create LeadAgent in `backend/src/agents/lead.py` with LinkedIn search + draft tool
- [ ] T060 Create `backend/src/models/contact.py` with LeadContact entity
- [ ] T061 [P] Create `backend/src/services/linkedin_client.py` for LinkedIn search (drafts only, no auto-send)
- [ ] T062 Create `backend/src/templates/linkedin_draft_template.txt` for connection request + follow-up
- [ ] T063 Add integration test for lead discovery flow in `backend/tests/integration/test_lead_flow.py`

**Checkpoint**: User Story 5 should be fully functional and testable independently

---

## Phase 9: Manager Agent Wiring

**Goal**: Connect all 6 specialist agents under the Manager agent with handoffs, interrupts, and state routing.

**Independent Test**: Trigger end-to-end flow (order intake → dealer RFQ → quote selection → invoice draft → approval route); verify Manager orchestrates all specialists and approval interrupts fire correctly.

- [ ] T064 Create Manager agent in `backend/src/agents/manager.py` with handoff orchestration
- [ ] T065 Create OpenAI Agents SDK workflow config in `backend/src/core/agents.py` (model, tools, interrupts)
- [ ] T066 Create FastAPI router for agent orchestration in `backend/src/api/orchestrator.py`
- [ ] T067 Create `backend/tests/integration/test_e2e_flow.py` for full pipeline integration test
- [ ] T068 Create Next.js approval dashboard in `frontend/app/approvals/page.tsx`
- [ ] T069 [P] Create approval dashboard API client in `frontend/services/approvalApi.ts`
- [ ] T070 Create `backend/src/templates/email_approval_reminder.html` for 48h approval reminders
- [ ] T071 [P] Create `backend/src/jobs/approval_reminder.py` for pending-approval alerts to owner

**Checkpoint**: Full end-to-end automation flow operational with owner approval gates

---

## Phase 10: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories

- [ ] T072 [P] Add audit logging decorator in `backend/src/core/audit.py` for all agent actions
- [ ] T073 [P] Add audit log model enhancement in `backend/src/models/audit.py` with actor tracking
- [ ] T074 Create `backend/docs/runbooks/email-polling-failure.md`
- [ ] T075 Create `backend/docs/runbooks/approval-backlog.md`
- [ ] T076 Add Dockerfile for backend in `backend/Dockerfile`
- [ ] T077 Add Dockerfile for frontend in `frontend/Dockerfile`
- [ ] T078 Update docker-compose with production env vars and health checks
- [ ] T079 Create `backend/tests/unit/test_audit_log.py` for audit trail verification
- [ ] T080 Create `backend/tests/unit/test_approval_gate.py` for financial figure approval enforcement
- [ ] Run full pytest suite with coverage check (target: >=80% for core logic)

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phase 3-8)**: All depend on Foundational phase completion
  - User stories can proceed sequentially in priority order (P1 -> P2 -> P3)
  - US1 (Invoice) and US2 (Order Intake) are both P1 and can be built in parallel after foundation
- **Manager Wiring (Phase 9)**: Depends on all 6 specialist agents being complete (Phases 3-8)
- **Polish (Phase 10)**: Depends on all prior phases

### User Story Dependencies

- **User Story 1 (Invoice Draft)**: Can start after Foundational (Phase 2) - No dependencies on other stories
- **User Story 2 (Order Intake)**: Can start after Foundational (Phase 2) - No dependencies on other stories
- **User Story 3 (Dealer RFQ)**: Can start after Foundational (Phase 2) - No dependencies on other stories
- **User Story 4 (Follow-up)**: Can start after Foundational (Phase 2) - No dependencies on other stories
- **User Story 5 (Lead Discovery)**: Can start after Foundational (Phase 2) - No dependencies on other stories
- **User Story 6 (Catalog)**: Can start after Foundational (Phase 2) - No dependencies on other stories
- **Manager Wiring**: Depends on all 6 specialist agents being implemented

### Within Each User Story

- Models before services
- Services before agents/endpoints
- Core implementation before integration tests
- Story complete before moving to next priority

### Parallel Opportunities

- All Setup tasks marked [P] can run in parallel
- All Foundational tasks marked [P] can run in parallel (within Phase 2)
- Once Foundational phase completes, all user stories can start in parallel (if team capacity allows)
- Tests for a user story marked [P] can run in parallel
- Models within a story marked [P] can run in parallel
- Different user stories can be worked on in parallel by different team members

---

## Parallel Example: User Story 1 & 2 (Both P1 MVP)

```bash
# Launch tests for US1 and US2 together:
Task: "Unit test for margin calculation in backend/tests/unit/test_margin_calc.py"
Task: "Unit test for order extraction logic in backend/tests/unit/test_order_intake.py"

# Launch models for US1 and US2 together:
Task: "Create InvoiceDraft model in backend/src/models/invoice.py"
Task: "Create Order and OrderItem models in backend/src/models/order.py"
```

---

## Implementation Strategy

### MVP First (User Story 1 + 2 Only)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational (CRITICAL - blocks all stories)
3. Complete Phase 3: User Story 2 (Order Intake)
4. Complete Phase 4: User Story 1 (Invoice Draft)
5. **STOP and VALIDATE**: Test US1 and US2 independently - this is the core order-to-invoice flow
6. Deploy/demo if ready

### Incremental Delivery

1. Complete Setup + Foundational -> Foundation ready
2. Add User Story 2 (Order Intake) -> Test independently -> Deploy/Demo
3. Add User Story 1 (Invoice Draft) -> Test independently -> Deploy/Demo (MVP!)
4. Add User Story 3 (Dealer RFQ) -> Test independently -> Deploy/Demo
5. Add User Story 4 (Follow-up) -> Test independently -> Deploy/Demo
6. Add User Story 6 (Catalog) -> Test independently -> Deploy/Demo
7. Add User Story 5 (Lead Discovery) -> Test independently -> Deploy/Demo
8. Wire Manager agent -> Full end-to-end flow

### Parallel Team Strategy

With multiple developers:

1. Team completes Setup + Foundational together
2. Once Foundational is done:
   - Developer A: User Story 2 (Order Intake)
   - Developer B: User Story 1 (Invoice Draft)
3. Stories complete and integrate independently
4. Specialist agents built, then Manager wiring integrates all

---

## Notes

- [P] tasks = different files, no dependencies
- [Story] label maps task to specific user story for traceability
- Each user story should be independently completable and testable
- Verify models before services, services before endpoints
- Commit after each task or logical group
- Stop at any checkpoint to validate story independently
- Avoid: vague tasks, same file conflicts, cross-story dependencies that break independence
