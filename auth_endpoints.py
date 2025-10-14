"""
Authentication API Endpoints for Miraikakaku
Provides user registration, login, logout, and token refresh functionality
"""

from fastapi import APIRouter, HTTPException, status, Depends
from pydantic import BaseModel, EmailStr, Field
from typing import Optional
import psycopg2
from psycopg2.extras import RealDictCursor
from datetime import datetime, timedelta
import os

from auth_utils import (
    get_password_hash,
    verify_password,
    create_access_token,
    create_refresh_token,
    verify_refresh_token,
    get_current_user,
    get_current_active_user
)

# Create router
router = APIRouter(prefix="/api/auth", tags=["authentication"])


# Pydantic models
class UserRegister(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr
    password: str = Field(..., min_length=8)
    full_name: Optional[str] = None


class UserLogin(BaseModel):
    username: str
    password: str


class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class TokenRefresh(BaseModel):
    refresh_token: str


class UserResponse(BaseModel):
    id: int
    username: str
    email: str
    full_name: Optional[str]
    is_active: bool
    is_admin: bool
    created_at: datetime


# Database connection helper
def get_db_config():
    host = os.getenv('POSTGRES_HOST', 'localhost')
    config = {
        'database': os.getenv('POSTGRES_DB', 'miraikakaku'),
        'user': os.getenv('POSTGRES_USER', 'postgres'),
        'password': os.getenv('POSTGRES_PASSWORD', 'Miraikakaku2024!')
    }
    if host.startswith('/cloudsql/'):
        config['host'] = host
    else:
        config['host'] = host
        config['port'] = int(os.getenv('POSTGRES_PORT', 5433))
    return config


def get_db_connection():
    return psycopg2.connect(**get_db_config())


# Endpoints
@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register_user(user: UserRegister):
    """
    Register a new user

    - Creates a new user account with hashed password
    - Username and email must be unique
    - Password must be at least 8 characters
    """
    try:
        conn = get_db_connection()
        cur = conn.cursor(cursor_factory=RealDictCursor)

        # Check if username already exists
        cur.execute("SELECT id FROM users WHERE username = %s", (user.username,))
        if cur.fetchone():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username already registered"
            )

        # Check if email already exists
        cur.execute("SELECT id FROM users WHERE email = %s", (user.email,))
        if cur.fetchone():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )

        # Hash password
        password_hash = get_password_hash(user.password)

        # Insert new user
        cur.execute("""
            INSERT INTO users (username, email, password_hash, full_name, is_active, is_admin)
            VALUES (%s, %s, %s, %s, true, false)
            RETURNING id, username, email, full_name, is_active, is_admin, created_at
        """, (user.username, user.email, password_hash, user.full_name))

        new_user = cur.fetchone()
        conn.commit()

        cur.close()
        conn.close()

        return UserResponse(**new_user)

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to register user: {str(e)}"
        )


@router.post("/login", response_model=Token)
def login_user(user: UserLogin):
    """
    Login with username and password

    - Returns access token (30 min) and refresh token (7 days)
    - Access token is used for API requests
    - Refresh token is used to get new access token
    """
    try:
        conn = get_db_connection()
        cur = conn.cursor(cursor_factory=RealDictCursor)

        # Get user by username
        cur.execute("""
            SELECT id, username, email, password_hash, is_active, is_admin
            FROM users
            WHERE username = %s
        """, (user.username,))

        db_user = cur.fetchone()

        if not db_user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect username or password",
                headers={"WWW-Authenticate": "Bearer"},
            )

        # Verify password
        if not verify_password(user.password, db_user['password_hash']):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect username or password",
                headers={"WWW-Authenticate": "Bearer"},
            )

        # Check if user is active
        if not db_user['is_active']:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="User account is inactive"
            )

        # Update last login
        cur.execute("""
            UPDATE users SET last_login = CURRENT_TIMESTAMP WHERE id = %s
        """, (db_user['id'],))
        conn.commit()

        # Create tokens
        token_data = {
            "user_id": db_user['id'],
            "username": db_user['username'],
            "email": db_user['email'],
            "is_admin": db_user['is_admin']
        }

        access_token = create_access_token(token_data)
        refresh_token = create_refresh_token(token_data)

        cur.close()
        conn.close()

        return Token(
            access_token=access_token,
            refresh_token=refresh_token
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to login: {str(e)}"
        )


@router.post("/refresh", response_model=Token)
def refresh_access_token(token_refresh: TokenRefresh):
    """
    Refresh access token using refresh token

    - Validates the refresh token
    - Issues a new access token and refresh token
    - Old refresh token becomes invalid
    """
    try:
        # Verify refresh token
        payload = verify_refresh_token(token_refresh.refresh_token)

        # Create new tokens
        token_data = {
            "user_id": payload.get("user_id"),
            "username": payload.get("username"),
            "email": payload.get("email"),
            "is_admin": payload.get("is_admin", False)
        }

        access_token = create_access_token(token_data)
        refresh_token = create_refresh_token(token_data)

        return Token(
            access_token=access_token,
            refresh_token=refresh_token
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to refresh token: {str(e)}"
        )


@router.post("/logout")
def logout_user(current_user: dict = Depends(get_current_user)):
    """
    Logout current user

    - In a full implementation, this would revoke the token
    - For now, client should delete the token
    - Returns success message
    """
    # In production, you would:
    # 1. Add token to blacklist/revocation list
    # 2. Store revoked tokens in user_sessions table
    # 3. Check blacklist on each request

    return {
        "message": "Successfully logged out",
        "username": current_user.get("username")
    }


@router.get("/me", response_model=UserResponse)
def get_current_user_info(current_user: dict = Depends(get_current_active_user)):
    """
    Get current authenticated user information

    - Requires valid access token
    - Returns full user profile
    """
    try:
        conn = get_db_connection()
        cur = conn.cursor(cursor_factory=RealDictCursor)

        # Get full user information
        cur.execute("""
            SELECT id, username, email, full_name, is_active, is_admin, created_at
            FROM users
            WHERE id = %s
        """, (current_user['user_id'],))

        user = cur.fetchone()

        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )

        cur.close()
        conn.close()

        return UserResponse(**user)

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get user info: {str(e)}"
        )


@router.put("/me")
def update_current_user(
    full_name: Optional[str] = None,
    current_user: dict = Depends(get_current_active_user)
):
    """
    Update current user information

    - Requires valid access token
    - Can update full_name (more fields can be added)
    """
    try:
        conn = get_db_connection()
        cur = conn.cursor()

        if full_name is not None:
            cur.execute("""
                UPDATE users SET full_name = %s, updated_at = CURRENT_TIMESTAMP
                WHERE id = %s
            """, (full_name, current_user['user_id']))

        conn.commit()
        cur.close()
        conn.close()

        return {
            "message": "User information updated successfully",
            "username": current_user.get("username")
        }

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update user: {str(e)}"
        )
