"""
Security utilities: Argon2id password hashing and JWT authentication.
"""
from datetime import datetime, timedelta, timezone
from typing import Optional, Any, Dict
from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError
import jwt
from app.core.config import settings
from app.core.errors import AuthenticationException

ph = PasswordHasher()


def hash_password(password: str) -> str:
    """Hash password using Argon2id."""
    return ph.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify password against Argon2id hash."""
    try:
        return ph.verify(hashed_password, plain_password)
    except (VerifyMismatchError, Exception):
        return False


def create_access_token(subject: str, role: str = "USER", expires_delta: Optional[timedelta] = None) -> str:
    """Create signed JWT access token."""
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode: Dict[str, Any] = {
        "sub": str(subject),
        "role": role,
        "exp": expire,
        "iat": datetime.now(timezone.utc)
    }
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt


def decode_token(token: str) -> Dict[str, Any]:
    """Decode and validate JWT access token."""
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        raise AuthenticationException("Token has expired")
    except jwt.InvalidTokenError:
        raise AuthenticationException("Invalid authentication token")
