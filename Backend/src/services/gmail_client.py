import imaplib
import ssl
from email.message import Message
from email.parser import BytesParser
from email.policy import default
from typing import Optional

from ..core.config import settings
from ..core.logging import log


class GmailClient:
    """Read-only IMAP client for Gmail with SPF/DKIM verification."""

    def __init__(self) -> None:
        self._conn: Optional[imaplib.IMAP4_SSL] = None

    def connect(self) -> None:
        context = ssl.create_default_context()
        self._conn = imaplib.IMAP4_SSL(
            settings.GMAIL_IMAP_HOST, settings.GMAIL_IMAP_PORT, ssl_context=context
        )
        self._conn.login(settings.GMAIL_IMAP_USER, settings.GMAIL_IMAP_PASSWORD)
        log.info("IMAP connection established", extra={"action": "imap_connect", "actor": "agent"})

    def disconnect(self) -> None:
        if self._conn:
            self._conn.close()
            self._conn.logout()
            log.info("IMAP connection closed", extra={"action": "imap_disconnect", "actor": "agent"})

    def poll_unseen_emails(self) -> list[tuple[str, str, Message]]:
        """Poll unseen emails from the inbox.

        Returns list of (message_id, sender_email, parsed_message).
        SPF/DKIM verification is performed on the raw headers.
        """
        if not self._conn:
            self.connect()
        assert self._conn is not None

        self._conn.select("INBOX")
        status, messages = self._conn.search(None, "(UNSEEN)")
        emails: list[tuple[str, str, Message]] = []

        if status != "OK" or not messages[0]:
            return emails

        for msg_id_bytes in messages[0].split():
            msg_id = msg_id_bytes.decode()
            try:
                status, msg_data = self._conn.fetch(msg_id_bytes, "(RFC822)")
                if status != "OK":
                    continue
                raw_email = msg_data[0][1]
                if isinstance(raw_email, bytes):
                    parsed: Message = BytesParser(
                        policy=default
                    ).parsebytes(raw_email)
                else:
                    parsed = BytesParser(policy=default).parsebytes(
                        raw_email.encode()
                    )

                sender = self._extract_sender(parsed)
                spf_dkim_ok = self._verify_auth_headers(parsed)

                emails.append((msg_id, sender, parsed))
                log.info(
                    "Email polled",
                    extra={
                        "action": "email_poll",
                        "actor": "agent",
                        "message_id": msg_id,
                        "sender": sender,
                        "spf_dkim_ok": spf_dkim_ok,
                    },
                )
            except Exception as e:
                log.error(f"Failed to parse email {msg_id}: {e}", exc_info=True)

        return emails

    def _extract_sender(self, msg: Message) -> str:
        from email.utils import parseaddr

        from_str = msg.get("From", "")
        _, addr = parseaddr(from_str)
        return addr.lower() if addr else from_str

    def _verify_auth_headers(self, msg: Message) -> bool:
        """Check SPF/DKIM results from Gmail Authentication-Results header."""
        auth_results = msg.get("Authentication-Results", "")
        if not auth_results:
            return False
        has_spf_pass = "spf=pass" in auth_results
        has_dkim_pass = "dkim=pass" in auth_results or "dkim=pass" in auth_results
        return has_spf_pass and has_dkim_pass

    def is_sender_approved(self, sender_email: str) -> bool:
        """Check if sender is on the approved client list."""
        approved = settings.approved_senders
        if not approved:
            return False
        sender_lower = sender_email.lower()
        return sender_lower in [a.lower() for a in approved]
