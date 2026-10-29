# ADR-001: Multi-Agent Manager with Handoffs and Human Approval Gates

> **Scope**: Document the decision for a Manager-with-handoffs multi-agent design and mandatory owner approval gates for all pricing, rather than a single agent or auto-pricing.

- **Status:** Accepted
- **Date:** 2025-06-13
- **Feature:** sorax-automation
- **Context:** The Sorax automation system handles a Pakistani industrial-supplies procurement business. The business owner (single user) makes the final call on pricing, terms, and client commitments. The system must coordinate 6 specialists (Lead, Catalog, Order Intake, Dealer Sourcing, Quotation & Invoice, Follow-up) across a pipeline: lead → inquiry → order → RFQ → quote → invoice → follow-up. Any architecture must enforce that the owner approves every client-facing financial figure before it leaves the system (Constitution Principle I).

<!-- Significance checklist (ALL must be true to justify this ADR)
     1) Impact: Long-term consequence for architecture/platform/security? ✅ Yes — determines agent SDK usage, orchestration model, test strategy, and data flow across all 6 agents.
     2) Alternatives: Multiple viable options considered with tradeoffs? ✅ Yes — single-agent, distributed microservices, or manager-with-handoffs.
     3) Scope: Cross-cutting concern (not an isolated detail)? ✅ Yes — affects every agent and every integration.
     If any are false, prefer capturing as a PHR note instead of an ADR. -->

## Decision

Adopt a **Manager-with-handoffs** multi-agent design using the OpenAI Agents SDK:

- One Manager agent orchestrates 6 specialist agents via SDK handoffs (control transfer with context).
- Owner approval is enforced via **SDK interrupts** at all financial decision points (invoice generation, quote acceptance, pricing output to clients).
- Approval state is persisted in an `ApprovalRequest` table; the workflow pauses until the owner approves via the Next.js dashboard or WhatsApp reply.
- No agent can emit a client-facing price, invoice total, or tax figure without an owner-approved `ApprovalRequest` record in the audit trail.

Components:
- **Agent Framework**: OpenAI Agents SDK (handoffs + interrupts)
- **Orchestration**: Single Manager agent, in-process (not distributed)
- **Approval gate**: `ApprovalRequest` table + SDK interrupts + Next.js dashboard
- **Audit**: All approval events logged in `AuditLog` with timestamp and owner identity

## Consequences

### Positive

- **Clear separation of concerns**: Each specialist agent has a single responsibility (e.g., Order Intake parses emails, Dealer Sourcing sends RFQs), making testing and iteration simpler.
- **Owner control preserved**: Financial commitment points are explicit, auditable, and cannot be bypassed — directly satisfies Constitution Principle I and the user's stated requirement.
- **Context transfer via handoffs**: The Manager passes full context (order data, dealer quotes, margin config) to each specialist, reducing re-prompting and improving accuracy (Principle IV).
- **Simplicity first**: Single in-process workflow avoids distributed messaging queue complexity (Constitution Principle VII), fitting a single-owner business on a single VPS.
- **Testability**: Each agent can be tested in isolation with mocked tools; approval gates can be simulated by pre-seeding `ApprovalRequest` records.

### Negative

- **Single point of failure**: If the Manager agent fails, the entire workflow stalls (mitigated by error-handling runbooks).
- **Interrupt latency**: Owner must actively approve via dashboard or WhatsApp, which could delay invoice delivery if the owner is unavailable (mitigated by 48h reminder alerts and "pending approval" dashboard).
- **SDK lock-in**: Heavy reliance on OpenAI Agents SDK handoffs and interrupts means switching agent frameworks would require significant rework.

## Alternatives Considered

**Alternative A — Single monolithic agent**: One agent handles all 6 steps in a single prompt.
- *Rejected*: Loses the ability to isolate specialist failures, harder to test individual components, and handoff semantics (which carry context cleanly) would need to be replicated manually. Also makes the approval-gate boundary less explicit in code.

**Alternative B — Distributed microservices with message queue**: Each agent is a separate service; RabbitMQ or Redis queues coordinate handoffs.
- *Rejected*: Adds Redis/RabbitMQ infrastructure (Constitution Principle VII — simplicity first), introduces message-ordering complexity, and makes owner-approval interrupts harder to implement consistently across services. Overkill for a single-owner business.

**Alternative C — One big agent with tool-calling only (no handoffs)**: Manager calls tools (functions) but never transfers control to a named agent.
- *Rejected*: Loses the explicit agent boundary that makes the approval gate testable; harder to reason about which agent is responsible for which approval. Handoffs provide clearer ownership of state transitions.

## References

- Feature Spec: `specs/sorax-automation/spec.md`
- Implementation Plan: `specs/sorax-automation/plan.md`
- Related ADRs: ADR-002 (approval gate enforcement), ADR-003 (Docker deployment)
- Evaluator Evidence: N/A (architectural decision, validated against Constitution)