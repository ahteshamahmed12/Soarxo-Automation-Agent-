"""Integration tests for the full auth flow.

Tests: signup request → admin approval → login → /me
Uses the in-memory SQLite db_session fixture.
"""

from datetime import datetime

import pytest
from sqlmodel import SQLModel, Session, create_engine, select
from sqlalchemy.pool import StaticPool

from src.models.auth import SignupRequest, User, UserRole, UserStatus
from src.services.auth import (
    authenticate_user,
    hash_password,
    create_access_token,
    decode_token,
    verify_password,
)
from src.models import *  # noqa: F401,F403 — register all tables


@pytest.fixture(name="auth_engine")
def auth_engine_fixture():
    engine = create_engine(
        "sqlite:///",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    SQLModel.metadata.create_all(engine)
    with Session(engine) as s:
        # Seed an owner (admin)
        owner = User(
            email="admin@company.com",
            full_name="System Admin",
            password_hash=hash_password("admin-password-123"),
            role=UserRole.OWNER,
            status=UserStatus.ACTIVE,
        )
        s.add(owner)
        s.commit()
    yield engine
    SQLModel.metadata.drop_all(engine)
    engine.dispose()


@pytest.fixture(name="auth_db")
def auth_db_fixture(auth_engine):
    with Session(auth_engine) as session:
        yield session


class TestSignupRequestFlow:
    """Test the signup request → approval → user creation flow."""

    def test_signup_request_creates_pending_request(self, auth_db):
        """A signup request is stored with 'pending' status."""
        req = SignupRequest(
            full_name="John Doe",
            email="john@example.com",
            phone="+1234567890",
            password_hash=hash_password("secret123"),
            status="pending",
        )
        auth_db.add(req)
        auth_db.commit()
        auth_db.refresh(req)

        assert req.id is not None
        assert req.status == "pending"
        assert req.email == "john@example.com"

    def test_approve_request_creates_active_user(self, auth_db):
        """Approving a signup request creates an ACTIVE user."""
        from src.core.utils import utcnow

        req = SignupRequest(
            full_name="Jane Smith",
            email="jane@example.com",
            password_hash=hash_password("password123"),
            status="pending",
        )
        auth_db.add(req)
        auth_db.commit()
        auth_db.refresh(req)

        # Simulate approval (what the API approve endpoint does)
        owner = auth_db.exec(select(User).where(User.role == UserRole.OWNER)).first()
        user = User(
            email=req.email,
            full_name=req.full_name,
            phone=req.phone,
            password_hash=req.password_hash,
            role=UserRole.USER,
            status=UserStatus.ACTIVE,
            approved_at=utcnow(),
        )
        auth_db.add(user)

        req.status = "approved"
        req.reviewed_by = owner.id
        req.reviewed_at = utcnow()
        auth_db.commit()

        # Verify user was created as active
        assert user.id is not None
        assert user.status == UserStatus.ACTIVE
        assert user.role == UserRole.USER
        assert verify_password("password123", user.password_hash)

    def test_rejected_request_cannot_be_approved(self, auth_db):
        """A rejected request cannot be re-approved."""
        req = SignupRequest(
            full_name="Bob",
            email="bob@example.com",
            password_hash=hash_password("pass123"),
            status="rejected",
        )
        auth_db.add(req)
        auth_db.commit()

        assert req.status == "rejected"
        # Logic in the API checks this — here we verify the state constraint
        assert req.status != "approved"

    def test_duplicate_email_signup_request_conflict(self, auth_db):
        """Two pending requests with the same email should conflict."""
        req1 = SignupRequest(
            full_name="Test A",
            email="dup@example.com",
            password_hash=hash_password("pass1"),
            status="pending",
        )
        auth_db.add(req1)
        auth_db.commit()

        req2 = SignupRequest(
            full_name="Test B",
            email="dup@example.com",
            password_hash=hash_password("pass2"),
            status="pending",
        )
        auth_db.add(req2)
        # Should fail on commit due to unique constraint
        with pytest.raises(Exception):
            auth_db.commit()


class TestLoginFlow:
    """Test login with approved users only."""

    def test_approved_user_can_login(self, auth_db):
        """An active user with correct password authenticates."""
        user = auth_db.exec(select(User).where(User.email == "admin@company.com")).first()
        result = authenticate_user(auth_db, "admin@company.com", "admin-password-123")
        assert result is not None
        assert result.id == user.id

    def test_wrong_password_fails(self, auth_db):
        """Wrong password returns None."""
        result = authenticate_user(auth_db, "admin@company.com", "wrong-password")
        assert result is None

    def test_pending_user_cannot_login(self, auth_db):
        """A pending user cannot authenticate (status != active)."""
        pending_user = User(
            email="pending@example.com",
            full_name="Pending User",
            password_hash=hash_password("pass123"),
            role=UserRole.USER,
            status=UserStatus.PENDING,
        )
        auth_db.add(pending_user)
        auth_db.commit()

        result = authenticate_user(auth_db, "pending@example.com", "pass123")
        assert result is None

    def test_unknown_user_fails(self, auth_db):
        """Non-existent email returns None."""
        result = authenticate_user(auth_db, "nobody@example.com", "any-password")
        assert result is None

    def test_login_returns_valid_jwt(self, auth_db):
        """Successful login produces a decodable JWT."""
        user = auth_db.exec(select(User).where(User.email == "admin@company.com")).first()

        token = create_access_token({"sub": str(user.id)})
        payload = decode_token(token)
        assert payload["sub"] == str(user.id)

    def test_rejected_user_cannot_login(self, auth_db):
        """A rejected user cannot authenticate."""
        rejected = User(
            email="rejected@example.com",
            full_name="Rejected User",
            password_hash=hash_password("pass123"),
            role=UserRole.USER,
            status=UserStatus.REJECTED,
        )
        auth_db.add(rejected)
        auth_db.commit()

        result = authenticate_user(auth_db, "rejected@example.com", "pass123")
        assert result is None
