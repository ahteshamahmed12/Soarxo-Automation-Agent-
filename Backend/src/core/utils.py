"""Shared datetime utilities."""

from datetime import datetime, timezone


def utcnow() -> datetime:
    """Return a timezone-aware UTC datetime (avoids deprecated datetime.utcnow())."""
    return datetime.now(timezone.utc)
