"""Auth models: User, SignupRequest with role-based access control.

Admin is a normal User row with role=owner, password Argon2-hashed.
Signup requests are stored separately until admin approves.
"""

from datetime import datetime
from enum import Enum
from typing import Optional

from sqlmodel import Field, SQLModel

from ..core.utils import utcnow


class UserRole(str, Enum):
    OWNER = "owner"
    ADMIN = "admin"
    USER = "user"


class UserStatus(str, Enum):
    PENDING = "pending"
    ACTIVE = "active"
    REJECTED = "rejected"


class User(SQLModel, table=True):
    __tablename__ = "users"

    id: Optional[int] = Field(default=None, primary_key=True)
    email: str = Field(index=True, unique=True, nullable=False)
    full_name: str = Field(nullable=False)
    phone: Optional[str] = None
    password_hash: str = Field(nullable=False)
    role: UserRole = Field(default=UserRole.USER)
    status: UserStatus = Field(default=UserStatus.PENDING)
    created_at: datetime = Field(
        default_factory=utcnow, sa_column_kwargs={"default": "now()"}
    )
    approved_at: Optional[datetime] = None

    def __repr__(self) -> str:
        return f"User(id={self.id}, email={self.email!r}, role={self.role}, status={self.status})"


class SignupRequest(SQLModel, table=True):
    __tablename__ = "signup_requests"

    id: Optional[int] = Field(default=None, primary_key=True)
    full_name: str = Field(nullable=False)
    email: str = Field(index=True, unique=True, nullable=False)
    phone: Optional[str] = None
    password_hash: str = Field(nullable=False)
    status: str = Field(default="pending")  # pending, approved, rejected
    created_at: datetime = Field(
        default_factory=utcnow, sa_column_kwargs={"default": "now()"}
    )
    reviewed_by: Optional[int] = Field(default=None, foreign_key="users.id")
    reviewed_at: Optional[datetime] = None
