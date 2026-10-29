---
id: 4
title: Sorax Automation Plan
stage: plan
date: 2025-06-13
surface: agent
model: claude-sonnet-4-6
feature: sorax-automation
branch: sorax-automation
user: ahtesham ahmed
command: /sp.plan
labels: ["plan", "architecture", "agents", "fastapi", "docker"]
links:
  spec: specs/sorax-automation/spec.md
  ticket: null
  adr: null
  pr: null
files:
  - specs/sorax-automation/plan.md
tests:
  - none
---

## Prompt

```text
/sp.plan Architecture:
- Backend: FastAPI + PostgreSQL (SQLModel), Alembic migrations.
- Agents: OpenAI Agents SDK. The Manager agent uses handoffs to the 6 specialists.
- Integrations: Gmail API (read orders, send emails), WhatsApp Cloud API (webhooks + send), WeasyPrint or ReportLab for invoice PDFs.
- Data model: Client, Contact, Lead, Catalog, Order, OrderItem, Dealer, DealerQuote, Invoice, FollowUp, AuditLog.
- Approval layer: an ApprovalRequest table. Agents create requests, the owner approves via a simple dashboard (Next.js + Tailwind) or WhatsApp reply.
- Background jobs: APScheduler or Celery for weekly follow-ups and email polling.
- Deployment: Docker, deployed on a single VPS or Railway.
- Build order: Order Intake -> Dealer Sourcing -> Quotation/Invoice -> Catalog -> Lead -> Manager wiring.
- Testing: pytest with mocked Gmail and WhatsApp clients.
```

## Response snapshot

Authored implementation plan at `specs/sorax-automation/plan.md` with full architecture (FastAPI + SQLModel + PostgreSQL + OpenAI Agents SDK), Constitution Check (all 8 principles verified), project structure (backend/ + frontend/ separation), data model notes, API contracts for WhatsApp/Gmail/OpenAI SDK/approval dashboard, NFR budgets (order intake <120s, invoice gen <60s), operational readiness (observability, alerting, runbooks, rollback), risk analysis (5 key risks), and 3 ADR suggestions. Build order: Order Intake → Dealer Sourcing → Quotation/Invoice → Catalog → Lead → Manager wiring.

## Outcome

- ✅ Impact: Architecture decisions locked for all 5 clarified ambiguities; next step is `/sp.tasks` to generate dependency-ordered tasks
- 🧪 Tests: N/A (planning artifact)
- 📁 Files: `specs/sorax-automation/plan.md` (complete plan authored)
- 🔁 Next prompts: `/sp.tasks` to generate testable, owner-assignable tasks; optionally `/sp.adr 01-single-agent-workflow.md` for the single-workflow decision
- 🧠 Reflection: All key decisions align with Constitution Principle VII (simplicity first); single VPS deployment avoids infra complexity for a single-owner business

## Evaluation notes (flywheel)

- Failure modes observed: None
- Graders run and results: N/A
- Prompt variant: N/A
- Next experiment: N/A