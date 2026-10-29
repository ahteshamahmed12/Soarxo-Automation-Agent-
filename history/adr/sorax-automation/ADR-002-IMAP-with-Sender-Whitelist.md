# ADR-002: IMAP with Sender Whitelist and SPF/DKIM Verification for Order Intake

> **Scope**: Document the decision for read-only IMAP with sender whitelist and SPF/DKIM verification as the email ingestion model, rather than a dedicated order mailbox or Gmail API push notifications.

- **Status:** Accepted
- **Date:** 2025-06-13
- **Feature:** sorax-automation
- **Context:** The Order Intake Agent must read client order emails from the owner's existing business email account. The business owner uses Gmail/IMAP for client communication. Email is the trigger for the entire order→invoice pipeline. The system must prevent untrusted or spoofed emails from being auto-processed into orders (Constitution Principle III — Data Safety; Principle IV — Accuracy).

<!-- Significance checklist (ALL must be true to justify this ADR)
     1) Impact: Long-term consequence for architecture/platform/security? ✅ Yes — determines email ingestion reliability, security posture, and owner onboarding friction.
     2) Alternatives: Multiple viable options considered with tradeoffs? ✅ Yes — dedicated mailbox, Gmail API push, IMAP with whitelist.
     3) Scope: Cross-cutting concern (not an isolated detail)? ✅ Yes — affects Order Intake Agent, security model, and onboarding.
     If any are false, prefer capturing as a PHR note instead of an ADR. -->

## Decision

Adopt **read-only IMAP with a pre-approved sender whitelist and SPF/DKIM verification**:

- The Order Intake Agent connects to the owner's existing email via IMAP (read-only).
- Only emails from senders on a pre-approved client list are auto-processed into structured orders.
- All incoming emails undergo SPF/DKIM authentication result checks (via Gmail header analysis or IMAP `auth` results).
- Emails from unknown senders or failing SPF/DKIM are routed to a "needs review" queue for explicit owner approval — never auto-processed.
- Email content is treated strictly as data; the agent never executes instructions found in email body text.

Components:
- **Email access**: IMAP (read-only), authenticated with OAuth 2.0 app password or service account
- **Sender filtering**: Whitelist of client email addresses/domains, configurable by owner
- **Authentication check**: SPF/DKIM result header inspection (Gmail adds `Authentication-Results` headers automatically)
- **Fallback**: "needs review" queue in `ApprovalRequest` table for untrusted emails
- **Outbound**: Emails sent via SMTP or Gmail API (separate send path, also subject to approval for price-bearing content)

## Consequences

### Positive

- **No DNS changes required**: Owner uses existing email; no need to configure a new domain or MX records — reduces onboarding friction for a small business.
- **Security boundary**: Sender whitelist + SPF/DKIM prevents spoofed or untrusted emails from entering the order pipeline, directly satisfying Constitution Principle III (data safety) and Principle IV (no fabricated data).
- **Familiar UX**: Owner retains their existing email workflow; the system augments rather than disrupts.
- **Simplicity**: IMAP polling is simpler than Gmail API push notifications (no public webhook URL needed); Constitution Principle VII.
- **Auditability**: All emails (processed and skipped) are logged in `AuditLog` with sender, SPF/DKIM result, and disposition.

### Negative

- **Polling latency**: IMAP polling (every 30s–1min) introduces delay vs. real-time push notifications; acceptable given the 2-minute order intake target.
- **IMAP reliability dependency**: If the owner's email is temporarily unreachable (Gmail outage, auth expiry), orders may backlog; mitigated by alerting and the "needs review" queue.
- **Limited structure**: IMAP provides raw email; no Gmail API metadata (labels, threads) that could aid deduplication; mitigated by email ID tracking in DB.

## Alternatives Considered

**Alternative A — Dedicated order mailbox** (e.g., orders@sorax.com):
- *Rejected*: Requires DNS changes (MX record, SPF/DKIM/DMARC for new subdomain), email forwarding setup, and owner training. Adds a second email address to manage. Overkill for the business scale; IMAP whitelist is simpler (Constitution Principle VII).

**Alternative B — Gmail API push notifications**:
- *Rejected*: Requires a public HTTPS webhook endpoint, OAuth consent screen submission to Google, and persistent webhook registration. More complex for a single-VPS deployment. IMAP polling is simpler and sufficient for the 2-minute target.

**Alternative C — Accept all senders without whitelist**:
- *Rejected*: Violates Constitution Principle III (data safety) and Principle IV (accuracy). Untrusted emails could inject bogus orders or malicious payloads. The owner explicitly requires approval gates for financial data.

## References

- Feature Spec: `specs/sorax-automation/spec.md` (FR-001, FR-002, NFR-007)
- Implementation Plan: `specs/sorax-automation/plan.md` (Key Decision #2, Complexity Tracking)
- Related ADRs: ADR-001 (multi-agent with approval gates)
- Evaluator Evidence: N/A (security decision, validated against Constitution Principles III and IV)