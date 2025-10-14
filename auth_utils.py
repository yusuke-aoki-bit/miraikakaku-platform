"""
JWT Authentication Utilities for Miraikakaku
Handles token generation, validation, and user authentication
"""

from datetime import datetime, timedelta
from typing import Optional, Dict
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import HTTPException, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import os

# Configuration
SECRET_KEY = os.getenv("JWT_SECRET_KEY", "miraikakaku-secret-key-change-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
REFRESH_TOKEN_EXPIRE_DAYS = 7

# Password hashing - using pbkdf2_sha256 instead of bcrypt to avoid 72-byte limit
# pbkdf2_sha256 is secure, NIST-approved, and has no password length restrictions
pwd_context = CryptContext(
    schemes=["pbkdf2_sha256"],
    deprecated="auto"
)

# HTTP Bearer token scheme
security = HTTPBearer()


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a plain password against a hashed password"""
    # Bcrypt has a maximum password length of 72 bytes
    # Truncate if necessary to avoid errors
    password_bytes = plain_password.encode('utf-8')
    if len(password_bytes) > 72:
        plain_password = password_bytes[:72].decode('utf-8', errors='ignore')

    try:
        return pwd_context.verify(plain_password, hashed_password)
    except Exception as e:
        # If verification fails due to bcrypt error, return False
        return False


def get_password_hash(password: str) -> str:
    """Hash a password using bcrypt"""
    # Bcrypt has a maximum password length of 72 bytes
    # Truncate BEFORE encoding to ensure we stay under the limit
    password_bytes = password.encode('utf-8')
    if len(password_bytes) > 72:
        # Truncate to 72 bytes
        password = password_bytes[:72].decode('utf-8', errors='ignore')

    # Ensure password is a string (not bytes) for passlib
    if isinstance(password, bytes):
        password = password.decode('utf-8', errors='ignore')

    try:
        return pwd_context.hash(password)
    except ValueError as e:
        # Catch bcrypt-specific errors about password length
        if "72 bytes" in str(e):
            # Manually truncate and retry
            password_truncated = password[:72] if isinstance(password, str) else password.decode('utf-8', errors='ignore')[:72]
            return pwd_context.hash(password_truncated)
        raise ValueError(f"Failed to hash password: {str(e)}")
    except Exception as e:
        # If hashing fails, raise a clear error
        raise ValueError(f"Failed to hash password: {str(e)}")


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """
    Create a JWT access token

    Args:
        data: Dictionary containing user information (user_id, username, etc.)
        expires_delta: Optional custom expiration time

    Returns:
        Encoded JWT token string
    """
    to_encode = data.copy()

    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)

    to_encode.update({
        "exp": expire,
        "iat": datetime.utcnow(),
        "type": "access"
    })

    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def create_refresh_token(data: dict) -> str:
    """
    Create a JWT refresh token with longer expiration

    Args:
        data: Dictionary containing user information

    Returns:
        Encoded JWT refresh token string
    """
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)

    to_encode.update({
        "exp": expire,
        "iat": datetime.utcnow(),
        "type": "refresh"
    })

    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def decode_token(token: str) -> Dict:
    """
    Decode and validate a JWT token

    Args:
        token: JWT token string

    Returns:
        Decoded token payload

    Raises:
        HTTPException: If token is invalid or expired
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Could not validate credentials: {str(e)}",
            headers={"WWW-Authenticate": "Bearer"},
        )


def verify_access_token(token: str) -> Dict:
    """
    Verify an access token and return the payload

    Args:
        token: JWT access token string

    Returns:
        Token payload if valid

    Raises:
        HTTPException: If token is invalid, expired, or not an access token
    """
    payload = decode_token(token)

    if payload.get("type") != "access":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token type",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return payload


def verify_refresh_token(token: str) -> Dict:
    """
    Verify a refresh token and return the payload

    Args:
        token: JWT refresh token string

    Returns:
        Token payload if valid

    Raises:
        HTTPException: If token is invalid, expired, or not a refresh token
    """
    payload = decode_token(token)

    if payload.get("type") != "refresh":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token type",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return payload


def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> Dict:
    """
    FastAPI dependency to get the current authenticated user from the token

    Args:
        credentials: HTTP Authorization header with Bearer token

    Returns:
        User information from token payload

    Raises:
        HTTPException: If authentication fails
    """
    token = credentials.credentials
    payload = verify_access_token(token)

    user_id = payload.get("user_id")
    username = payload.get("username")

    if user_id is None or username is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return {
        "user_id": user_id,
        "username": username,
        "email": payload.get("email"),
        "is_admin": payload.get("is_admin", False)
    }


def get_current_active_user(current_user: Dict = Depends(get_current_user)) -> Dict:
    """
    FastAPI dependency to get current active user (for future use with is_active checks)

    Args:
        current_user: Current user from get_current_user dependency

    Returns:
        Current user if active
    """
    # In the future, we can add database lookup to check if user is still active
    return current_user


def require_admin(current_user: Dict = Depends(get_current_user)) -> Dict:
    """
    FastAPI dependency to require admin privileges

    Args:
        current_user: Current user from get_current_user dependency

    Returns:
        Current user if admin

    Raises:
        HTTPException: If user is not an admin
    """
    if not current_user.get("is_admin", False):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin privileges required"
        )

    return current_user
