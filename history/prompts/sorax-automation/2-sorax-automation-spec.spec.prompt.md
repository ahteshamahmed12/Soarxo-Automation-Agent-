---
id: 2
title: Sorax Automation Spec
stage: spec
date: 2025-06-13
surface: agent
model: claude-sonnet-4-6
feature: sorax-automation
branch: sorax-automation
user: ahtesham ahmed
command: /sp.specify
labels: ["spec", "automation", "agents", "Pakistan", "industrial-supplies"]
links:
  spec: specs/sorax-automation/spec.md
  ticket: null
  adr: null
  pr: null
files:
  - specs/sorax-automation/spec.md
tests:
  - none
---

## Prompt

```text
/sp.specify Build an AI automation system for Sorax Industrial Solution, which procures electrical parts, motor parts, and industrial supplies for companies in Pakistan.

Current manual flow to automate:
LinkedIn lead search -> connection request -> reply with company bio -> ask for WhatsApp number -> send catalog -> client emails an order -> send order-received email -> WhatsApp Karachi dealers (e.g. Saddar) for prices and negotiate -> create invoice with profit margin and taxes -> occasional calls -> weekly follow-up email to every client.

System: one Manager agent coordinating 6 specialist agents:
1. Lead Agent: finds procurement/supply-chain contacts and drafts connection and follow-up messages for the owner to send manually.
2. Catalog Agent: handles WhatsApp inquiries and sends the right catalog.
3. Order Intake Agent: reads client order emails, extracts items, quantities, and specs into structured data, and sends the order-received email.
4. Dealer Sourcing Agent: sends WhatsApp RFQs to Saddar dealers, collects replies, and compares quotes.
5. Quotation and Invoice Agent: applies margin and taxes, generates the invoice PDF, and routes it for owner approval.
6. Follow-up Agent: sends weekly follow-up emails to every client and tracks replies in the CRM.

User: the business owner (single user), who approves, negotiates, and handles calls.

Success criteria:
- An order email becomes a structured order within 2 minutes.
- Dealer RFQs go out without manual typing.
- Invoice drafts are generated in under 1 minute after the quote is chosen.
- 100% of client-facing money figures are owner-approved.

Out of scope: auto-negotiation of final price, automated LinkedIn actions, phone calls, payments.
```

## Response snapshot

Authored a complete feature specification at `specs/sorax-automation/spec.md` covering 6 user stories (P1–P3), 14 functional requirements, 8 non-functional requirements aligned with the Sorax Constitution (Principles I–VI), key data entities, edge cases, and 4 measurable success criteria. The Manager + 6 specialist agent architecture is captured with clear responsibilities and handoff points. Out of scope explicitly defined: auto-negotiation, automated LinkedIn actions, phone calls, payments, and inventory management.

## Outcome

- ✅ Impact: Establishes the spec foundation for the Sorax AI automation system; next step is `/sp.plan` to produce the architecture plan (FastAPI backend, PostgreSQL schema, OpenAI Agents SDK orchestration, WhatsApp Business Cloud API integration)
- 🧪 Tests: N/A (spec authoring)
- 📁 Files: `specs/sorax-automation/spec.md` (complete spec authoring)
- 🔁 Next prompts: `/sp.plan` to generate implementation plan with Constitution Check gates
- 🧠 Reflection: 6 agents mapped cleanly to 6 user stories; success criteria are all testable via API mocks and timing assertions

## Evaluation notes (flywheel)

- Failure modes observed: None
- Graders run and results: N/A
- Prompt variant: N/A
- Next experiment: N/A