"""Order email parser.

Parses client order emails into structured ``OrderItem`` objects.
Unknown parts or ambiguous quantities are surfaced for owner review
(Constitution Principle IV — Accuracy).
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from email.message import Message
from typing import Optional

from ..models.order import OrderItem


@dataclass
class ParseWarning:
    """Flags items that need owner review."""

    part_number: Optional[str]
    description: str
    reason: str  # why this item needs review


@dataclass
class ParsedOrder:
    """Result of parsing an order email."""

    items: list[OrderItem]
    unknown_parts: list[ParseWarning] = field(default_factory=list)
    sender: str = ""
    subject: str = ""


# Matches lines like:
#   "1. Motor 1 HP - 2 pcs"
#   "2. Bearings SKF - 5 pcs"
#   "3. Control panel - 1 unit"
#   "  4. Cable 10mm - 3 meters"
# Captures: description, quantity, unit
_LINE_RE = re.compile(
    r"""
    ^\s*
    (\d+[.)\s]*)?           # optional line number: "1." "1)" "1 " or none
    (?P<desc>.+?)           # description (non-greedy)
    \s*-\s*                 # separator " - "
    (?P<qty>\d+(?:\.\d+)?)  # quantity: digits with optional decimals
    \s*(?P<unit>[a-zA-Z]+)  # unit: word
    \s*$
    """,
    re.VERBOSE,
)

# Quantity patterns that should NOT be treated as numeric
_AMBIGUOUS_QUANTITY_RE = re.compile(
    r"\b(a few|a couple|some|couple of|several|several|many|lot|lots)\b",
    re.IGNORECASE,
)

# Part number pattern: alphanumeric with hyphens, e.g. MTR-001, ABC.123
_PART_NUMBER_RE = re.compile(r"\b([A-Z0-9]+[-.][A-Z0-9-]\w*)\b")

# Common units
_KNOWN_UNITS = {"pcs", "piece", "pieces", "unit", "units", "meter", "meters",
                "mtr", "mtrs", "kg", "kilogram", "kilograms", "g", "gram",
                "litre", "litres", "l", "set", "sets", "roll", "rolls"}


class OrderEmailParser:
    """Parses client order emails into structured OrderItems.

    Handles the order format used by Sorax clients: numbered or bulleted
    line items with quantity and unit, e.g.::

        1. Motor 1 HP - 2 pcs
        2. Bearings SKF-6205 - 5 pcs
        3. Control panel - 1 unit
    """

    def extract_line_item(
        self,
        description: str,
        quantity: float | str,
        unit: str,
        part_number: Optional[str] = None,
    ) -> Optional[OrderItem]:
        """Extract a single OrderItem from parsed field values.

        Raises ``ValueError`` if the quantity is non-numeric or non-positive
        (per Principle IV — never guess ambiguous values).
        """
        if isinstance(quantity, str):
            parsed_qty = self._try_parse_quantity(quantity.strip())
            if parsed_qty is None:
                raise ValueError(f"Cannot parse quantity: {quantity!r}")
            quantity = parsed_qty

        if quantity <= 0:
            raise ValueError(f"Quantity must be positive: {quantity}")

        return OrderItem(
            part_number=part_number,
            description=description.strip(),
            quantity=quantity,
            unit=unit.strip(),
        )

    def extract_line_items(self, body: str) -> list[OrderItem]:
        """Extract multiple line items from an email body.

        Unknown / ambiguous parts are skipped from the returned list and
        surfaced separately via :meth:`extract_with_warnings`.
        """
        items, _ = self.extract_with_warnings(body)
        return items

    def extract_with_warnings(
        self, body: str
    ) -> tuple[list[OrderItem], list[ParseWarning]]:
        """Extract line items and also return flagged unknown parts.

        Returns ``(items, warnings)`` where ``warnings`` captures items that
        could not be confidently parsed for owner review.
        """
        items: list[OrderItem] = []
        warnings: list[ParseWarning] = []

        for raw_line in body.splitlines():
            line = raw_line.strip()
            if not line or line.startswith(("Subject:", "Dear", "Hi", "Hello")):
                continue

            match = _LINE_RE.match(line)
            if not match:
                continue

            desc = match.group("desc").strip()
            qty_str = match.group("qty")
            unit = match.group("unit").strip().lower()

            # Detect ambiguous quantities (Principle IV)
            if (
                _AMBIGUOUS_QUANTITY_RE.search(desc)
                or _AMBIGUOUS_QUANTITY_RE.search(qty_str)
            ):
                warnings.append(
                    ParseWarning(
                        part_number=None,
                        description=desc,
                        reason="ambiguous quantity — requires owner clarification",
                    )
                )
                continue

            try:
                qty = float(qty_str)
            except ValueError:
                warnings.append(
                    ParseWarning(
                        part_number=None,
                        description=desc,
                        reason=f"unparseable quantity: {qty_str!r}",
                    )
                )
                continue

            if qty <= 0:
                warnings.append(
                    ParseWarning(
                        part_number=None,
                        description=desc,
                        reason=f"non-positive quantity: {qty}",
                    )
                )
                continue

            # Try to find a part number in the description
            part_match = _PART_NUMBER_RE.search(desc)
            part_number = part_match.group(1) if part_match else None

            # Normalize unit
            if unit in {"piece", "pieces"}:
                unit = "pcs"

            item = OrderItem(
                part_number=part_number,
                description=desc,
                quantity=qty,
                unit=unit,
            )
            items.append(item)

        return items, warnings

    def _try_parse_quantity(self, qty_str: str) -> Optional[float]:
        """Attempt to parse a quantity string. Return None if ambiguous."""
        if _AMBIGUOUS_QUANTITY_RE.search(qty_str):
            return None
        try:
            return float(qty_str)
        except ValueError:
            return None

    def parse_email(self, msg: Message) -> ParsedOrder:
        """Parse a full email Message into a :class:`ParsedOrder`."""
        subject = msg.get("Subject", "")
        from email.utils import parseaddr
        _, sender = parseaddr(msg.get("From", ""))

        body = ""
        if msg.is_multipart():
            for part in msg.walk():
                if part.get_content_type() == "text/plain":
                    body = part.get_content()
                    break
        else:
            body = msg.get_content() or ""

        items, warnings = self.extract_with_warnings(body)
        return ParsedOrder(
            items=items,
            unknown_parts=warnings,
            sender=sender.lower(),
            subject=subject,
        )
