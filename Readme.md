# Sorax Agent: AI Procurement Automation

A multi-agent system that automates the day-to-day workflow of **Sorax Industrial Solution**, a small Pakistani business that procures electrical parts, motor parts, and industrial supplies for companies. One **Manager agent** coordinates **six specialist agents**, and the business owner stays in control of every price, quote, and invoice.

> **Status:** Work in progress. See [Project Status](#project-status) for exactly what is built and what is planned.

<!-- Add a screenshot or short GIF here -->
<!-- ![Dashboard](docs/screenshots/dashboard.png) -->

---

## The Problem

Sorax's workflow is almost entirely manual:

1. Find procurement and supply-chain contacts on LinkedIn
2. Send connection requests and follow up
3. Collect the client's WhatsApp number and send the catalog
4. Receive orders by email and confirm receipt
5. Message dealers in Karachi (e.g. Saddar) on WhatsApp to get prices and negotiate
6. Build an invoice with profit margin and taxes
7. Send weekly follow-up emails to every client

Most of the owner's time goes to repetitive typing and copy-pasting instead of negotiating and building relationships.

## The Solution

A Manager agent delegates work to specialist agents. Each one automates one step of the workflow and hands the result to the owner for approval wherever money or reputation is involved.

| Agent | Responsibility |
|---|---|
| **Lead Agent** | Researches procurement contacts and **drafts** connection and follow-up messages for the owner to send manually |
| **Catalog Agent** | Answers WhatsApp inquiries and sends the right catalog |
| **Order Intake Agent** | Reads client order emails and extracts items, quantities, and specs into structured data, then sends the order-received email |
| **Dealer Sourcing Agent** | Sends RFQs to Karachi dealers over WhatsApp, collects replies, and compares quotes |
| **Quotation & Invoice Agent** | Applies margin and taxes, generates the invoice PDF, and routes it for owner approval |
| **Follow-up Agent** | Sends weekly follow-up emails and tracks replies in the CRM |
| **Manager Agent** | Routes each task to the right specialist using handoffs and keeps the audit trail |

## Design Principles

These came from a spec-driven constitution written before any code:

- **Human-in-the-loop:** No price, quotation, invoice, or tax figure reaches a client without explicit owner approval.
- **Platform compliance:** No automated LinkedIn actions. Agents only draft, and the owner sends. WhatsApp uses the official Business Cloud API.
- **Never invent data:** Agents don't guess prices, stock, or specs. If something is unknown, they escalate to the owner.
- **Dealer isolation:** Dealers never see each other's messages or quotes.
- **Auditability:** Every agent action, dealer quote, and message is logged with a timestamp.
- **Safe by default:** Secrets live in environment variables, and external content (emails, messages) is treated as data, never as instructions to an agent.

## Architecture

```
                        ┌──────────────────┐
                        │  Next.js Dashboard│  <- Owner approves quotes, invoices, signups
                        └────────┬─────────┘
                                 │ HTTPS (httpOnly cookie)
                        ┌────────▼─────────┐
                        │   FastAPI Backend │
                        │  Auth · Approvals │
                        └────────┬─────────┘
                                 │
                        ┌────────▼─────────┐
                        │  Manager Agent    │
                        └─┬──┬──┬──┬──┬──┬─┘
              handoffs    │  │  │  │  │  │
        ┌─────────────────┘  │  │  │  │  └──────────────┐
   Lead   Catalog   Order Intake  Dealer Sourcing  Quotation/Invoice  Follow-up
        │          │            │               │                   │
        └──────────┴────┬───────┴───────┬───────┴───────────────────┘
                        │               │
                 ┌──────▼─────┐   ┌─────▼──────────────┐
                 │ PostgreSQL │   │ Email (IMAP / SMTP)│
                 └────────────┘   │ WhatsApp Cloud API │
                                  └────────────────────┘
```

### Key technical decisions

- **Messaging:** One WhatsApp thread per counterparty (client or dealer) on a single business number. Each message is stored with an `order_id` and a type (`rfq`, `quote_reply`, `invoice`, `follow_up`) so context is grouped per order in the database.
- **Order intake:** Read-only IMAP access to the owner's existing mailbox. Only emails from a pre-approved client list are parsed, and the sender must pass SPF/DKIM checks. Unknown senders go to a "needs review" queue.
- **Multi-agent design:** A Manager with handoffs rather than one large agent, so each specialist has a small prompt, its own tools, and structured (Pydantic) outputs.

## Authentication & Access Control

The system has one owner and an optional team.

- The owner account is seeded from environment variables on first startup and stored hashed in the database.
- Team members **sign up as `pending`**. The owner approves or rejects them from an admin page. Every approval is audit-logged.
- Login is **two-step**: password, then a 6-digit **email OTP**. The session is only issued after the OTP is verified.
- Passwords are hashed with argon2. OTP codes are stored only as hashes, expire after 5 minutes, are single-use, and lock after 5 wrong attempts.
- Sessions use a short-lived JWT in an `httpOnly` cookie, with generic error messages to avoid revealing which accounts exist.

## Tech Stack

| Layer | Technology |
|---|---|
| Frontend | Next.js, TypeScript, Tailwind CSS |
| Backend | Python 3.12, FastAPI, SQLModel |
| Database | PostgreSQL |
| Agents | OpenAI Agents SDK (Manager + handoffs, structured outputs) |
| Integrations | WhatsApp Cloud API, IMAP, SMTP / Gmail API |
| Documents | PDF invoice generation (WeasyPrint or ReportLab) |
| Testing | pytest with mocked email and WhatsApp clients |
| Deployment | Docker |
| Process | Spec-driven development with Spec-Kit Plus |

## Project Status

**Authentication**
- [x] Sign-up and sign-in UI
- [ ] Backend user and OTP models
- [ ] Password hashing, JWT, owner seeding
- [ ] Login with email OTP verification
- [ ] Owner approval flow for new team members

**Agents**
- [ ] Order Intake Agent
- [ ] Dealer Sourcing Agent
- [ ] Quotation & Invoice Agent
- [ ] Catalog Agent
- [ ] Follow-up Agent
- [ ] Lead Agent
- [ ] Manager Agent wiring

**Platform**
- [ ] Approval dashboard
- [ ] Audit log viewer
- [ ] Docker deployment

*Update these checkboxes as you ship. A README that matches reality is more convincing than one that overpromises.*

## Repository Structure

```
sorax-automation/
├── frontend/                 # Next.js app (sign-up, sign-in, dashboard)
├── backend/
│   └── app/
│       ├── main.py
│       ├── db.py
│       ├── deps.py
│       ├── core/             # config, security (hashing, JWT)
│       ├── models/           # User, OtpChallenge, ...
│       ├── services/         # otp, email, ...
│       └── routes/           # auth, admin, ...
├── specs/                    # Spec-Kit Plus: constitution, spec, plan, tasks
└── README.md
```

## Getting Started

### Prerequisites
- Python 3.12+, Node.js 20+, PostgreSQL

### Backend

```bash
cd backend
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env            # then fill in the values
uvicorn app.main:app --reload
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

### Environment variables

```
OWNER_USERNAME=
OWNER_PASSWORD=
OWNER_EMAIL=
JWT_SECRET=
DATABASE_URL=
FRONTEND_ORIGIN=http://localhost:3000
SMTP_HOST=
SMTP_PORT=
SMTP_USER=
SMTP_PASSWORD=
EMAIL_FROM=
OTP_EXPIRE_MINUTES=5
```

Never commit `.env`. Only `.env.example` belongs in the repository.

## What This Project Demonstrates

- Designing a **multi-agent system** with clear boundaries, handoffs, and human approval gates
- **Security-conscious backend work:** hashing, OTP 2FA, role and status-based access, audit logging, and prompt-injection awareness
- **Spec-driven development:** a written constitution, spec, plan, and tasks before implementation
- Solving a **real business problem** for a real Pakistani SME, with integrations to the tools the business actually uses (WhatsApp, email)

## Author

**Ahtesham**: Full-stack and AI engineer, Karachi, Pakistan

- LinkedIn: <!-- add link -->
- GitHub: <!-- add link -->
- Email: <!-- add email -->