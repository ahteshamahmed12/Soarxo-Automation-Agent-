---
id: 6
title: Sorax Automation Tasks
stage: tasks
date: 2025-06-13
surface: agent
model: claude-sonnet-4-6
feature: sorax-automation
branch: sorax-automation
user: ahtesham ahmed
command: /sp.tasks
labels: ["tasks", "implementation", "mvp", "parallel"]
links:
  spec: specs/sorax-automation/spec.md
  ticket: null
  adr: null
  pr: null
files:
  - specs/sorax-automation/tasks.md
tests:
  - none
---

## Prompt

```text
/sp.tasks (run after /sp.specify + /sp.plan + /sp.adr for sorax-automation feature)
```

## Response snapshot

Generated 80 tasks at `specs/sorax-automation/tasks.md` organized into 10 phases: Setup (7 tasks), Foundational (10 tasks), US2 Order Intake (8 tasks), US1 Invoice Draft (10 tasks), US3 Dealer RFQ (7 tasks), US4 Follow-up (6 tasks), US6 Catalog (6 tasks), US5 Lead (8 tasks), Manager Wiring (8 tasks), Polish (11 tasks). Tasks organized by user story with checklist format, parallel markers, story labels, and exact file paths. Build order follows priority: Order Intake → Invoice Draft → Dealer RFQ → Follow-up → Catalog → Lead → Manager wiring. MVP = US1 + US2 only.

## Outcome

- ✅ Impact: Task breakdown ready for implementation; each user story independently testable; P1 stories (Order Intake + Invoice Draft) identified as MVP
- 🧪 Tests: pytest unit + integration tests included per user story (Constitution NFR-006)
- 📁 Files: `specs/sorax-automation/tasks.md` (80 tasks across 10 phases)
- 🔁 Next prompts: Begin implementation with Phase 1 (Setup) → Phase 2 (Foundational) → Phase 3+ (User Stories)
- 🧠 Reflection: All tasks follow checklist format; parallel opportunities identified; dependencies clearly mapped; build order respects spec priorities

## Evaluation notes (flywheel)

- Failure modes observed: None
- Graders run and results: All tasks follow format [ID] [P?] [Story?] Description with file paths
- Prompt variant: N/A
- Next experiment: N/A