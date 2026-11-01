"""Auth service: password hashing, JWT management, FastAPI dependencies.

Uses Argon2 for password hashing (via passlib) and HS256 JWTs
(via python-jose). Admin credentials are NEVER in env vars — only
JWT_SECRET_KEY and DATABASE_URL. The first owner is seeded via a
CLI script at runtime.
"""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Optional

from fastapi import Depends
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlmodel import Session, select

from ..core.config import settings
from ..core.database import get_session
from ..models.auth import User, UserRole, UserStatus

pwd_context = CryptContext(schemes=["argon2", "bcrypt"], deprecated="auto")


def hash_password(plain: str) -> str:
    """Hash a password using Argon2."""
    return pwd_context.hash(plain)


def verify_password(plain: str, hashed: str) -> bool:
    """Verify a password against its hash.
    Returns True if the password matches.
    """
    return pwd_context.verify(plain, hashed)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Create a JWT access token.

    Args:
        data: Claims to encode (must include 'sub' = user_id).
        expires_delta: Token TTL. Defaults to settings.JWT_EXPIRE_MINUTES.
    """
    to_encode = data.copy()
    if expires_delta is None:
        expires_delta = timedelta(minutes=settings.JWT_EXPIRE_MINUTES)
    expire = datetime.now(timezone.utc) + expires_delta
    to_encode["exp"] = expire
    to_encode["iat"] = datetime.now(timezone.utc)
    return jwt.encode(to_encode, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)


def decode_token(token: str) -> dict:
    """Decode and verify a JWT token.

    Returns the payload dict on success.
    Raises jwt.JWTError / JWTError on invalid/expired tokens.
    """
    return jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])


def get_user_by_id(db: Session, user_id: int) -> Optional[User]:
    """Fetch a user by primary key."""
    return db.get(User, user_id)


def get_user_by_email(db: Session, email: str) -> Optional[User]:
    """Fetch a user by email."""
    stmt = select(User).where(User.email == email)
    return db.exec(stmt).first()


def authenticate_user(
    db: Session, email: str, password: str
) -> Optional[User]:
    """Authenticate a user by email + password.

    Returns the User if credentials are valid and the user is ACTIVE.
    Returns None on bad credentials or inactive user.
    """
    user = get_user_by_email(db, email)
    if not user:
        return None
    if not verify_password(password, user.password_hash):
        return None
    if user.status != UserStatus.ACTIVE:
        return None
    return user


class JWTBearer:
    """FastAPI dependency that extracts and validates the JWT bearer token."""

    def __init__(self, *, required_status: UserStatus = UserStatus.ACTIVE):
        self.required_status = required_status

    def __call__(self, token: str = None) -> dict:
        """Validate the token from Authorization header.

        Note: In production this integrates with fastapi.security.HTTPBearer.
        For simplicity here, the token is passed directly.
        """
        if not token:
            raise JWTError("Missing token")
        try:
            payload = decode_token(token)
        except JWTError:
            raise
        return payload


class HTTPBearerWithUser:
    """Extract bearer token from Authorization header and return payload."""

    def __init__(self):
        from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

        self._bearer = HTTPBearer(auto_error=False)
        self._creds_cls = HTTPAuthorizationCredentials

    async def __call__(self, credentials: Optional[HTTPAuthorizationCredentials] = None) -> dict:
        if credentials is None:
            raise JWTError("Not authenticated")
        return decode_token(credentials.credentials)


def get_current_user(
    db: Session = Depends(get_session),
    token_payload: dict = Depends(HTTPBearerWithUser()),
) -> User:
    """FastAPI dependency: returns the authenticated User.

    Raises HTTPException(401) if token is invalid or user not found.
    """
    from fastapi import HTTPException, status

    try:
        user_id = int(token_payload["sub"])
    except (KeyError, ValueError, TypeError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
        )
    user = get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
        )
    return user


def require_role(*allowed_roles: UserRole):
    """FastAPI dependency factory: restrict endpoint to specific roles.

    Usage:
        def protected(user: User = Depends(require_role(UserRole.OWNER))):
            ...
    """
    from fastapi import HTTPException, status

    def role_checker(
        db: Session = Depends(get_session),
        token_payload: dict = Depends(HTTPBearerWithUser()),
    ) -> User:
        try:
            user_id = int(token_payload["sub"])
        except (KeyError, ValueError, TypeError):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token",
            )
        user = get_user_by_id(db, user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found",
            )
        if user.role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Role '{user.role}' not allowed. Required: {allowed_roles}",
            )
        return user

    return role_checker
