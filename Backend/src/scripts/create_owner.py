"""CLI script: create the first owner user.

Usage:
    Set env vars, then run:
        python -m src.scripts.create_owner

    Or with inline env:
        OWNER_EMAIL=admin@company.com OWNER_PASSWORD=secret OWNER_NAME="Admin" \
            python -m src.scripts.create_owner

This script reads credentials ONLY from environment variables — they are
never committed to source control. The password is hashed with Argon2
before storage.

The script can only run once (checks for existing owner). To reset,
use the --force flag (dev only).
"""

from __future__ import annotations

import asyncio
import os
import sys

import click

from ..core.config import settings
from ..core.database import get_session
from ..models.auth import User, UserRole, UserStatus
from ..services.auth import hash_password
from sqlmodel import select


def main() -> None:
    email = os.getenv("OWNER_EMAIL", "")
    password = os.getenv("OWNER_PASSWORD", "")
    full_name = os.getenv("OWNER_NAME", "System Owner")
    force = "--force" in sys.argv

    if not email or not password:
        click.echo(
            "Error: OWNER_EMAIL and OWNER_PASSWORD env vars must be set.",
            err=True,
        )
        click.echo(
            "  Example: OWNER_EMAIL=admin@company.com "
            "OWNER_PASSWORD=secret python -m src.scripts.create_owner",
            err=True,
        )
        sys.exit(1)

    if len(password) < 8:
        click.echo("Error: OWNER_PASSWORD must be at least 8 characters.", err=True)
        sys.exit(1)

    with next(get_session()) as db:
        existing = db.exec(
            select(User).where(User.role == UserRole.OWNER)
        ).first()

        if existing and not force:
            click.echo(
                f"An owner already exists (id={existing.id}, email={existing.email}). "
                "Use --force to recreate.",
                err=True,
            )
            sys.exit(1)

        if existing and force:
            db.delete(existing)
            db.commit()
            click.echo(f"Deleted existing owner (id={existing.id}).")

        owner = User(
            email=email,
            full_name=full_name,
            password_hash=hash_password(password),
            role=UserRole.OWNER,
            status=UserStatus.ACTIVE,
        )
        db.add(owner)
        db.commit()
        db.refresh(owner)

        click.echo(f"Owner user created successfully:")
        click.echo(f"  ID:    {owner.id}")
        click.echo(f"  Email: {owner.email}")
        click.echo(f"  Role:  {owner.role}")
        click.echo(f"  Status: {owner.status}")


if __name__ == "__main__":
    main()
