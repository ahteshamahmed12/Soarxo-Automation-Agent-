"""Unit tests for auth service (password hashing, JWT)."""

from datetime import timedelta
from unittest.mock import patch

import pytest
from jose import jwt
from passlib.context import CryptContext

from src.core.config import settings
from src.services.auth import (
    create_access_token,
    decode_token,
    hash_password,
    verify_password,
)


class TestPasswordHashing:
    """T027-equivalent: password hashing with Argon2."""

    def test_hash_password_returns_different_hash_each_time(self):
        """Same password → different hashes (salt is random)."""
        h1 = hash_password("mysecretpassword")
        h2 = hash_password("mysecretpassword")
        assert h1 != h2
        assert h1.startswith("$argon2")

    def test_verify_password_correct(self):
        """Correct password verifies True."""
        hashed = hash_password("correct-password-123")
        assert verify_password("correct-password-123", hashed) is True

    def test_verify_password_wrong(self):
        """Wrong password verifies False."""
        hashed = hash_password("correct-password-123")
        assert verify_password("wrong-password", hashed) is False

    def test_hash_password_short_input(self):
        """Short password still hashes (length is app's concern, not passlib's)."""
        hashed = hash_password("short")
        assert verify_password("short", hashed) is True


class TestJWTTokens:
    """Tests for JWT token creation and decoding."""

    def test_create_access_token_returns_valid_jwt(self):
        """Token decodes with correct claims."""
        token = create_access_token({"sub": "42"})
        payload = decode_token(token)
        assert payload["sub"] == "42"
        assert "exp" in payload
        assert "iat" in payload

    def test_create_access_token_custom_expiry(self):
        """Custom expires_delta sets correct expiry."""
        token = create_access_token({"sub": "1"}, expires_delta=timedelta(minutes=5))
        payload = decode_token(token)
        # exp - iat should be ~5 minutes (300 seconds), allow 5s tolerance
        import time
        diff = payload["exp"] - payload["iat"]
        assert 295 <= diff <= 305

    def test_decode_token_invalid_token_raises(self):
        """Invalid token raises JWTError."""
        from jose import JWTError
        with pytest.raises(JWTError):
            decode_token("invalid.token.here")

    def test_decode_token_expired_raises(self):
        """Expired token raises JWTError."""
        from jose import JWTError
        from datetime import datetime, timedelta, timezone
        expired = jwt.encode(
            {"sub": "1", "exp": datetime.now(timezone.utc) - timedelta(minutes=5),
             "iat": datetime.now(timezone.utc) - timedelta(minutes=10)},
            settings.JWT_SECRET_KEY,
            algorithm=settings.JWT_ALGORITHM,
        )
        with pytest.raises(JWTError):
            decode_token(expired)

    def test_token_uses_configured_algorithm(self):
        """Token is encoded with HS256."""
        token = create_access_token({"sub": "1"})
        header = jwt.get_unverified_header(token)
        assert header["alg"] == "HS256"
