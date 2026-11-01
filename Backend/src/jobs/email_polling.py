"""Email polling job — schedules IMAP checks via APScheduler.

Polls Gmail inbox for unseen order emails, feeds each one through the
OrderIntakeAgent, and sends a confirmation email back to the sender.
"""

from __future__ import annotations

import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Optional

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger

from ..agents.order_intake import order_intake_agent
from ..core.config import settings
from ..core.logging import log
from ..services.gmail_client import GmailClient


def _send_confirmation_email(
    to_email: str, order_id: int, item_count: int, escalated: int
) -> None:
    """Send a confirmation email back to the client after order intake.

    Uses SMTP (settings.SMTP_*) to send. Requires the HTML template at
    src/templates/email_received.html.
    """
    template_path = os.path.join(
        os.path.dirname(os.path.dirname(__file__)),
        "templates",
        "email_received.html",
    )
    with open(template_path, "r") as f:
        html_body = f.read()

    html_body = html_body.replace("{{ORDER_ID}}", str(order_id))
    html_body = html_body.replace("{{ITEM_COUNT}}", str(item_count))
    html_body = html_body.replace("{{ESCALATED_COUNT}}", str(escalated))

    msg = MIMEMultipart("alternative")
    msg["Subject"] = f"Sorax — Order Received (Order #{order_id})"
    msg["From"] = settings.SMTP_USER
    msg["To"] = to_email
    msg.attach(MIMEText(html_body, "html"))

    with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT) as server:
        server.starttls()
        server.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
        server.send_message(msg)

    log.info("Confirmation email sent", extra={
        "action": "email_send",
        "actor": "agent",
        "to": to_email,
        "order_id": order_id,
    })


class EmailPollingJob:
    """APScheduler-backed job that polls for order emails."""

    def __init__(self) -> None:
        self.scheduler: Optional[BackgroundScheduler] = None
        self.gmail = GmailClient()

    def start(self, interval_minutes: int = 2) -> None:
        """Start the background scheduler polling for emails."""
        self.scheduler = BackgroundScheduler()
        trigger = IntervalTrigger(minutes=interval_minutes)
        self.scheduler.add_job(
            self.poll,
            trigger,
            id="email_polling",
            replace_existing=True,
        )
        self.scheduler.start()
        log.info("Email polling started", extra={
            "action": "polling_start",
            "actor": "system",
            "interval_minutes": interval_minutes,
        })

    def stop(self) -> None:
        """Stop the background scheduler."""
        if self.scheduler:
            self.scheduler.shutdown()
            self.scheduler = None
            log.info("Email polling stopped", extra={
                "action": "polling_stop",
                "actor": "system",
            })

    def poll(self) -> None:
        """Poll unseen emails and process each as a potential order."""
        try:
            self.gmail.connect()
            emails = self.gmail.poll_unseen_emails()

            for msg_id, sender, message in emails:
                try:
                    self._process_email(msg_id, sender, message)
                except Exception as e:
                    log.error(f"Failed to process email {msg_id}", exc_info=True)
                    log.error(f"Error: {e}", exc_info=True)
        except Exception:
            log.error("Email poll cycle failed", exc_info=True)
        finally:
            self.gmail.disconnect()

    def _process_email(
        self, msg_id: str, sender: str, message: "email.message.Message"  # noqa: F821
    ) -> None:
        """Process a single email — check if it's from an approved sender, parse."""
        # Only process emails from approved client senders
        if not self.gmail.is_sender_approved(sender):
            log.info("Email from unregistered sender — skipping", extra={
                "action": "email_skip",
                "actor": "system",
                "sender": sender,
                "message_id": msg_id,
            })
            return

        subject = message.get("Subject", "")
        from email import message_from_bytes
        if message.is_multipart():
            body = ""
            for part in message.walk():
                if part.get_content_type() == "text/plain":
                    body = part.get_content()
                    break
        else:
            body = message.get_content() or ""

        log.info("Processing order email", extra={
            "action": "email_process",
            "actor": "system",
            "sender": sender,
            "subject": subject,
            "message_id": msg_id,
        })

        # Run the OrderIntakeAgent to parse and store the order
        result = order_intake_agent.run(
            f"Parse this order email. Sender: {sender}. Subject: {subject}. Body:\n{body}"
        )

        # Extract structured result from agent output
        # The agent calls parse_order_email tool which returns a dict
        tool_result = None
        for item in result.new_items:
            if item.type == "tool_call_result":
                tool_result = item.result
                break

        if tool_result and tool_result.get("order_id"):
            order_id = tool_result["order_id"]
            item_count = tool_result.get("item_count", 0)
            escalated = len(tool_result.get("escalated_items", []))
            _send_confirmation_email(sender, order_id, item_count, escalated)


# Singleton instance for scheduler use
email_polling_job = EmailPollingJob()
