---
id: 1
title: Create Sorax Constitution
stage: constitution
date: 2025-06-13
surface: agent
model: claude-sonnet-4-6
feature: none
branch: main
user: ahtesham ahmed
command: /sp.constitution
labels: ["constitution", "governance", "principles"]
links:
  spec: null
  ticket: null
  adr: null
  pr: null
files:
  - .specify/memory/constitution.md
tests:
  - none
---

## Prompt

```text
/sp.constitution Create principles for Sorax Industrial Solution automation, a multi-agent system that helps a small Pakistani industrial-supplies procurement business.

Principles:
1. Human-in-the-loop: no price, quotation, invoice, or tax figure is sent to a client without explicit owner approval.
2. Compliance: no automated LinkedIn actions. Agents only draft messages, and the owner sends them manually. WhatsApp uses the official Business Cloud API only.
3. Data safety: client and dealer data, prices, and margins stay private. Secrets live only in environment variables.
4. Accuracy: agents never invent prices, stock, or part specs. If unknown, they say so and escalate to the owner.
5. Auditability: every agent action, dealer quote, and message is logged with a timestamp.
6. Tech standards: Python 3.12, FastAPI, PostgreSQL, OpenAI Agents SDK, type hints, pytest tests for all core logic, and small modular code.
7. Simplicity first: build the smallest working version of each agent before adding features.
8. Spec-driven: no code without an approved spec, plan, and tasks.
```

## Response snapshot

Authored the Sorax Industrial Solution Automation Constitution at `.specify/memory/constitution.md` (v1.0.0). Eight principles encoded as declarative, testable rules (I Human-in-the-Loop, II Compliance, III Data Safety, IV Accuracy, V Auditability, VI Tech Standards, VII Simplicity First, VIII Spec-Driven Delivery) plus Additional Constraints, Development Workflow, and Governance sections. The existing template's placeholders for `[PRINCIPLE_1..6]` and `[SECTION_2/3]` were consolidated into the 8 provided principles and supporting sections. A Sync Impact Report was prepended as an HTML comment. Templates flagged for alignment: plan-template.md (Constitution Check gates), spec-template.md (compliance/approval gates), tasks-template.md (approval-gated, audit-log, data-safety task types). No remaining bracket tokens. Initial version ratified 2025-06-13.

## Outcome

- ✅ Impact: Established governance framework for the Sorax automation project; all future specs/plans/tasks now required to pass constitution compliance
- 🧪 Tests: N/A (constitution authoring, no code)
- 📁 Files: `.specify/memory/constitution.md` (complete authorship)
- 🔁 Next prompts: User may invoke `/sp.specify` for the first feature, referencing constitution principles
- 🧠 Reflection: Template had 6 placeholder principles but user supplied 8 — extended structure accordingly; kept minimal comments after replacing tokens

## Evaluation notes (flywheel)

- Failure modes observed: None
- Graders run and results: N/A
- Prompt variant: N/A
- Next experiment: N/A