import hashlib
import hmac
from typing import Any

import httpx

from ..core.config import settings
from ..core.logging import log


class WhatsAppClient:
    """Client for Meta Business Cloud API — sends WhatsApp messages."""

    BASE_URL = "https://graph.facebook.com/v21.0"

    def __init__(self) -> None:
        self._http = httpx.Client(
            base_url=f"{self.BASE_URL}/{settings.WHATSAPP_PHONE_NUMBER_ID}",
            headers={
                "Authorization": f"Bearer {settings.WHATSAPP_TOKEN}",
                "Content-Type": "application/json",
            },
            timeout=30.0,
        )

    def verify_webhook_signature(self, body: bytes, signature: str) -> bool:
        """Verify the X-Hub-Signature-256 header from WhatsApp webhook."""
        secret = settings.WHATSAPP_WEBHOOK_SECRET
        expected = hmac.new(
            secret.encode(), body, hashlib.sha256
        ).hexdigest()
        return hmac.compare_digest(f"sha256={expected}", signature)

    def send_text_message(self, to_number: str, text: str) -> dict[str, Any]:
        """Send a text message via WhatsApp Cloud API.

        Returns the API response JSON on success.
        Raises httpx.HTTPStatusError on API errors.
        """
        payload = {
            "messaging_product": "whatsapp",
            "to": to_number,
            "type": "text",
            "text": {"preview_url": False, "body": text},
            }
        response = self._http.post("/messages", json=payload)
        response.raise_for_status()
        result = response.json()

        log.info(
            "WhatsApp message sent",
            extra={
                "action": "whatsapp_send",
                "actor": "agent",
                "to": to_number,
                "message_id": result.get("messages", [{}])[0].get("id"),
            },
        )
        return result

    def send_template_message(
        self, to_number: str, template_name: str, components: list[dict[str, Any]] | None = None
    ) -> dict[str, Any]:
        """Send a templated message (used for notifications that don't fit 24h window)."""
        payload: dict[str, Any] = {
            "messaging_product": "whatsapp",
            "to": to_number,
            "type": "template",
            "template": {"name": template_name, "language": {"code": "en"}},
        }
        if components:
            payload["template"]["components"] = components

        response = self._http.post("/messages", json=payload)
        response.raise_for_status()
        return response.json()
