<!--
  Sync Impact Report:
  - Version change: 0.0.1 → 1.0.0 (initial ratification; first full version)
  - Modified principles: (n/a — initial authoring)
  - Added sections: I–VIII Core Principles, Additional Constraints, Development Workflow, Governance
  - Removed sections: (template placeholders only; no prior content)
  - Templates requiring updates: ✅ plan-template.md (Constitution Check gates now reference human-in-loop, compliance, accuracy, auditability, simplicity); spec-template.md (requirements alignment — add compliance & approval gates); tasks-template.md (task types: approval-gated, audit-log, data-safety review)
  - Follow-up TODOs: None
-->

# Sorax Industrial Solution Automation Constitution

## Core Principles

### I. Human-in-the-Loop (Approval Gate)
No price, quotation, invoice, or tax figure is sent to a client without explicit owner approval. All client-facing financial documents MUST pass through an owner-approved checkpoint before leaving the system. If unknown, agents MUST say so and escalate to the owner.

**Rationale**: Protects the business from inadvertent financial errors and preserves owner authority over customer commitments.

### II. Compliance (Comms Safety)
No automated LinkedIn actions. Agents MAY draft messages only; the owner sends them manually. WhatsApp integration MUST use the official Meta Business Cloud API only — no unofficial endpoints, scraping, or bulk unsolicited messaging.

**Rationale**: Avoids platform ToS violations and potential account bans that could cut off business development channels.

### III. Data Safety (Privacy by Design)
Client and dealer data, prices, and margins MUST stay private. Secrets MUST live only in environment variables — never hard-coded, never logged, never committed to version control.

**Rationale**: Keeps sensitive commercial and personal data protected against accidental disclosure.

### IV. Accuracy (No Hallucinated Data)
Agents MUST never invent prices, stock levels, or part specifications. If a value is unknown, the agent MUST say so explicitly and escalate to the owner rather than fabricating a figure.

**Rationale**: Inaccurate supplier or pricing data can lose customer trust and create financial exposure.

### V. Auditability (Traceable Actions)
Every agent action, dealer quote, and outbound message MUST be logged with a timestamp, actor (agent vs. owner), and outcome. Logs MUST be retained per business retention policy.

**Rationale**: Enables forensic review of decisions and supports compliance with internal and external audit requirements.

### VI. Tech Standards (Stack & Quality)
Python 3.12, FastAPI, PostgreSQL, OpenAI Agents SDK. All code MUST use type hints. All core logic MUST have pytest tests. Code MUST be small and modular.

**Rationale**: A consistent, typed, tested stack reduces defect rate and makes maintenance feasible by a small team.

### VII. Simplicity First (Smallest Working Version)
Build the smallest working version of each agent before adding features. Resist YAGNI violations — no speculative generalization until proven by a concrete need.

**Rationale**: Minimizes wasted work and keeps the surface area (and risk) small for a business with limited development resources.

### VIII. Spec-Driven Delivery (No Code Without Approved Artifacts)
No code is written without an approved spec, plan, and tasks for that feature. Each spec MUST include user scenarios, functional requirements, and success criteria before any implementation begins.

**Rationale**: Ensures alignment on intent before effort is spent and reduces rework from misunderstood requirements.

## Additional Constraints

- **Tech stack lock-in**: The approved stack (Python 3.12, FastAPI, PostgreSQL, OpenAI Agents SDK) is fixed for the current project phase. Alternatives MUST be justified via an ADR.
- **Secrets management**: All secrets (API keys, DB credentials, WhatsApp token) MUST be loaded from environment variables at runtime. No secrets in `.env` committed to git.
- **WhatsApp compliance**: Only the Meta Business Cloud API is permitted. No third-party wrappers that obscure the official API contract.
- **Data residency**: Client and dealer data MUST remain within the business's controlled environment. No external third-party storage unless explicitly approved.

## Development Workflow

1. **Spec** (`/sp.specify`): Write user stories, requirements, and success criteria. Must reference constitution gate.
2. **Plan** (`/sp.plan`): Architecture decisions, data model, contracts. Must pass Constitution Check.
3. **Tasks** (`/sp.tasks`): Decomposed, testable, owner-assignable units. Approval-gated where financials are involved.
4. **Red → Green → Refactor**: TDD cycle enforced for all core logic.
5. **PR review**: Every PR MUST be checked for constitution compliance (approval gates, data safety, audit logging).
6. **Deploy**: After green tests + owner approval of any financial or client-facing changes.

## Governance

- **Supersedence**: This Constitution supersedes all other internal practices. Where a conflict exists, this document wins.
- **Amendment procedure**: Amendments require the `/sp.constitution` command, updated Sync Impact Report, template alignment, and owner sign-off. A PR MUST propagate changes to dependent templates before merge.
- **Compliance review**: All PRs, specs, and plans MUST cite which principles they uphold, violate (if any with justification), and how data safety / approval gates are preserved.
- **Version policy**: MAJOR for backward-incompatible principle removals/redefinitions; MINOR for new or materially expanded principles; PATCH for clarifications/typos.

**Version**: 1.0.0 | **Ratified**: 2025-06-13 | **Last Amended**: 2025-06-13