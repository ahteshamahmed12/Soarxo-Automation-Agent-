# ADR-003: Docker-Compose on Single VPS with Separate Approval Dashboard

> **Scope**: Document the decision for Docker-compose deployment on a single VPS with a separate Next.js approval dashboard, rather than managed cloud platforms or full-stack integrated deployment.

- **Status:** Accepted
- **Date:** 2025-06-13
- **Feature:** sorax-automation
- **Context:** The Sorax automation system must run reliably in Pakistan for a small industrial-supplies procurement business. The system includes a Python FastAPI backend with agents, integrations (WhatsApp, Gmail), a PostgreSQL database, background jobs, and a lightweight approval dashboard for the owner. Deployment must be low-infrastructure, cost-effective, and easy for an owner with minimal ops experience to manage. Constitution Principle VII (simplicity first) applies.

<!-- Significance checklist (ALL must be true to justify this ADR)
     1) Impact: Long-term consequence for architecture/platform/security? ✅ Yes — determines deployment model, infra complexity, cost, and owner ops burden.
     2) Alternatives: Multiple viable options considered with tradeoffs? ✅ Yes — Railway, Fly.io, single VPS Docker, Kubernetes.
     3) Scope: Cross-cutting concern (not an isolated detail)? ✅ Yes — affects all components, backup strategy, and future scaling.
     If any are false, prefer capturing as a PHR note instead of an ADR. -->

## Decision

Adopt **Docker-compose on a single VPS with a separate Next.js approval dashboard**:

- Backend (FastAPI + agents + APScheduler + PostgreSQL) and frontend (Next.js approval dashboard) are separate services.
- Both are containerized with Docker and orchestrated via `docker-compose`.
- Deployment target is a single VPS (Linux, e.g., DigitalOcean/Contabo/Vultr) — chosen for Pakistani market cost/reliability.
- Secrets are injected via `.env` file (gitignored); no secrets baked into images.
- Daily `pg_dump` backups to encrypted volume; owner notified via WhatsApp on failure.
- Rollback: `docker-compose down -v` + restore from backup; Alembic downgrade for schema changes.

Components:
- **Runtime**: Docker + docker-compose on single Linux VPS
- **Backend**: FastAPI app container, SQLModel + Alembic, APScheduler
- **Frontend**: Next.js 14 container (thin approval UI only)
- **Database**: PostgreSQL container with daily backup cron
- **Secrets**: `.env` file, loaded at container startup (no env vars in images)
- **Backups**: `pg_dump` to encrypted volume, retention: 7 daily + 4 weekly

## Consequences

### Positive

- **Cost-effective for Pakistan**: Single VPS avoids cloud provider premiums; predictable monthly cost (~$10–20/month depending on provider).
- **Full control**: Owner controls the server, backups, and data residency — important for client/dealer privacy (Constitution Principle III).
- **No vendor lock-in**: Easy to migrate between VPS providers (DigitalOcean → Contabo → etc.) by copying the volume and `.env`.
- **Simplicity**: Single `docker-compose up -d` deployment; no managed orchestration (Constitution Principle VII). Owner with basic SSH skills can manage.
- **Separation of concerns**: Backend (agents + API) and frontend (approval UI) evolve independently; frontend can be replaced or re-skinned without touching agent logic.

### Negative

- **Manual ops**: Owner must handle VPS provisioning, OS updates, Docker updates, and backup restoration — requires some technical skill.
- **No auto-scaling**: Single VPS has limited resources; if system grows significantly, requires manual migration (accepted given current scope).
- **Single-region deployment**: Single VPS in one location; no multi-region failover (acceptable for a small single-owner business).

## Alternatives Considered

**Alternative A — Managed cloud platform (Railway, Fly.io, Render)**:
- *Rejected*: Higher cost for Pakistani businesses (USD pricing, potential payment-method friction); vendor lock-in to platform-specific deployment model; harder to control data residency and backups. Single VPS is more cost-effective and controllable.

**Alternative B — Kubernetes cluster**:
- *Rejected*: Massive over-engineering for a single-owner business (Constitution Principle VII). Requires k8s expertise, multiple nodes, and ongoing maintenance. Docker-compose on a single VPS is sufficient and simpler.

**Alternative C — Monolithic full-stack (backend serves frontend)**:
- *Rejected*: Mixing agent orchestration with UI rendering increases coupling. If the frontend needs UI-only changes (e.g., approval dashboard tweaks), the entire backend+agent stack would need redeployment. Separation allows independent frontend evolution and testing.

## References

- Feature Spec: `specs/sorax-automation/spec.md` (NFR-001 for secrets, SC-001/SC-003 for latency)
- Implementation Plan: `specs/sorax-automation/plan.md` (Key Decision #4, Complexity Tracking)
- Related ADRs: ADR-001 (multi-agent design), ADR-002 (IMAP ingestion)
- Evaluator Evidence: N/A (deployment decision, validated against Constitution Principle VII — simplicity first)