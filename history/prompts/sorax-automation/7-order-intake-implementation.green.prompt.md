---
id: 7
title: order-intake-implementation
stage: green
date: 2026-10-31
surface: agent
model: claude-sonnet-4-6
feature: sorax-automation
branch: main
user: ahtesham ahmed
command: phase no 03 US2 order intake p1
labels: ["order-intake", "email-parsing", "integration-test", "apscheduler"]
links:
  spec: null
  ticket: null
  adr: null
  pr: null
files:
  - /c/Users/dell/OneDrive/Desktop/Soraxo Agent/backend/src/agents/order_intake.py
  - /c/Users/dell/OneDrive/Desktop/Soraxo Agent/backend/src/jobs/email_polling.py
  - /c/Users/dell/OneDrive/Desktop/Soraxo Agent/backend/src/templates/email_received.html
  - /c/Users/dell/OneDrive/Desktop/Soraxo Agent/backend/tests/integration/test_order_intake_flow.py
  - /c/Users/dell/OneDrive/Desktop/Soraxo Agent/backend/pyproject.toml
tests:
  - /c/Users/dell/OneDrive/Desktop/Soraxo Agent/backend/tests/integration/test_order_intake_flow.py
  - /c/Users/dell/OneDrive/Desktop/Soraxo Agent/backend/tests/unit/test_order_intake.py
  - /c/Users/dell/OneDrive/Desktop/Soraxo Agent/backend/tests/unit/test_conftest.py
---

## Prompt

phase no 03 US2 order intake p1

## Response snapshot

Implemented User Story 2 (Structured Order Intake) end-to-end. Key work:

1. **OrderIntakeAgent** (`src/agents/order_intake.py`): OpenAI Agents SDK agent with a `parse_order_email` function_tool that delegates to the OrderEmailParser. Finds/creates Client records from email sender, creates Order + OrderItems, and stores ambiguous/unknown items as LineItem records for owner review (Principle IV — Never Guess). Updated to use `tools=[...]` (not `tool=`) and removed the problematic `Optional[dict]` parameter that triggered strict schema validation errors.

2. **Email polling job** (`src/jobs/email_polling.py`): APScheduler-backed EmailPollingJob that polls IMAP for unseen emails, checks SPF/DKIM via GmailClient, filters by approved senders, runs the OrderIntakeAgent, and sends a confirmation email via SMTP. Moved `smtplib` import to module level for testability.

3. **Email template** (`src/templates/email_received.html`): HTML template with Mustache-style placeholders (ORDER_ID, ITEM_COUNT, ESCALATED_COUNT) for order confirmation emails, styled with Sorax branding.

4. **Integration test** (`tests/integration/test_order_intake_flow.py`): 4 tests covering full flow — email parse → Order/OrderItems in DB, ambiguous quantity escalation, confirmation email dispatch (with mocked SMTP), and new client auto-creation.

Fixed two issues during implementation:
- Changed `function_tool` decorator parameter from `db_session_state: Optional[dict]` (triggered openai-agents strict schema error) to plain required string params.
- Fixed test fixture table creation order (import models before `SQLModel.metadata.create_all`).
- Added `apscheduler` to pyproject.toml dependencies and installed it.

All 19 tests pass (15 unit + 4 integration).

## Outcome

- ✅ Impact: User Story 2 (P1 MVP) fully implemented and independently testable. Order emails are parsed, stored, and acknowledged within the 120-second SLA target.
- 🧪 Tests: 19 passed (15 existing unit + 4 new integration). All US2 tests pass.
- 📁 Files: 5 files created/modified across agents, jobs, templates, tests, and config.
- 🔁 Next prompts: Phase 4 — User Story 1 (Generate Invoice Draft) using the completed Foundation.
- 🧠 Reflection: The openai-agents `function_tool` decorator is strict about schema — `Optional[dict]` params cause `additionalProperties` errors. Always use simple primitive params for function tools. Also, `Agent` init uses `tools` (list) not `tool` (singular).

## Evaluation notes (flywheel)

- Failure modes observed: (1) function_tool `additionalProperties` strict schema error on `Optional[dict]` param; (2) `smtplib` not at module scope causing patch failures; (3) SQLite table creation order in fixtures requiring model imports before `create_all`.
- Graders run and results (PASS/FAIL): PHR-007 tests: 19/19 PASS
- Prompt variant (if applicable): n/a
- Next experiment (smallest change to try): Consider extracting the email-sending logic into a dedicated EmailService class (like GmailClient) for cleaner testability and to separate SMTP from IMAP concerns.