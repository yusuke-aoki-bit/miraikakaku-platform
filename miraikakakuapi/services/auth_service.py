import logging
import hashlib
import secrets
import jwt
from datetime import datetime, timedelta
from typing import Optional, Dict
from fastapi import HTTPException
from ..core.config import settings
from ..core.database import db

logger = logging.getLogger(__name__)


class AuthService:
    """Service for handling user authentication and authorization."""

    def __init__(self):
        self.jwt_secret = settings.jwt_secret
        self.jwt_algorithm = settings.jwt_algorithm
        self.access_token_expire_minutes = settings.access_token_expire_minutes

    def create_jwt_token(self, user_data: dict) -> str:
        """Create JWT token for authenticated user."""
        try:
            payload = {
                "user_id": user_data.get("user_id"),
                "email": user_data.get("email"),
                "username": user_data.get("username"),
                "exp": datetime.utcnow() + timedelta(minutes=self.access_token_expire_minutes),
                "iat": datetime.utcnow(),
                "type": "access"
            }

            token = jwt.encode(payload, self.jwt_secret, algorithm=self.jwt_algorithm)
            return token

        except Exception as e:
            logger.error(f"Error creating JWT token: {e}")
            raise HTTPException(status_code=500, detail="Error creating authentication token")

    def verify_jwt_token(self, token: str) -> Dict:
        """Verify and decode JWT token."""
        try:
            payload = jwt.decode(token, self.jwt_secret, algorithms=[self.jwt_algorithm])

            # Check if token is expired
            if datetime.utcfromtimestamp(payload.get("exp", 0)) < datetime.utcnow():
                raise HTTPException(status_code=401, detail="Token expired")

            return payload

        except jwt.ExpiredSignatureError:
            raise HTTPException(status_code=401, detail="Token expired")
        except jwt.JWTError:
            raise HTTPException(status_code=401, detail="Invalid token")
        except Exception as e:
            logger.error(f"Error verifying JWT token: {e}")
            raise HTTPException(status_code=401, detail="Invalid token")

    def hash_password(self, password: str) -> str:
        """Hash password using salt."""
        salt = secrets.token_hex(16)
        password_hash = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt.encode('utf-8'), 100000)
        return f"{salt}:{password_hash.hex()}"

    def verify_password(self, password: str, stored_hash: str) -> bool:
        """Verify password against stored hash."""
        try:
            salt, stored_password_hash = stored_hash.split(':')
            password_hash = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt.encode('utf-8'), 100000)
            return stored_password_hash == password_hash.hex()
        except Exception as e:
            logger.error(f"Error verifying password: {e}")
            return False

    async def register_user(self, username: str, email: str, password: str) -> Dict:
        """Register a new user."""
        try:
            # Check if user already exists
            async with db.get_connection() as conn:
                existing_user = await conn.fetchrow(
                    "SELECT user_id FROM users WHERE email = $1 OR username = $2",
                    email, username
                )

                if existing_user:
                    raise HTTPException(status_code=400, detail="User already exists")

                # Hash password
                password_hash = self.hash_password(password)

                # Insert new user
                user_id = await conn.fetchval(
                    """
                    INSERT INTO users (username, email, password_hash, created_at, is_active)
                    VALUES ($1, $2, $3, $4, $5)
                    RETURNING user_id
                    """,
                    username, email, password_hash, datetime.utcnow(), True
                )

                # Create JWT token
                user_data = {
                    "user_id": user_id,
                    "username": username,
                    "email": email
                }

                token = self.create_jwt_token(user_data)

                return {
                    "message": "User registered successfully",
                    "user": {
                        "user_id": user_id,
                        "username": username,
                        "email": email
                    },
                    "access_token": token,
                    "token_type": "bearer"
                }

        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error registering user: {e}")
            raise HTTPException(status_code=500, detail="Registration failed")

    async def authenticate_user(self, username: str, password: str) -> Dict:
        """Authenticate user login."""
        try:
            async with db.get_connection() as conn:
                # Find user by username or email
                user = await conn.fetchrow(
                    """
                    SELECT user_id, username, email, password_hash, is_active
                    FROM users
                    WHERE (username = $1 OR email = $1) AND is_active = true
                    """,
                    username
                )

                if not user:
                    raise HTTPException(status_code=401, detail="Invalid credentials")

                # Verify password
                if not self.verify_password(password, user["password_hash"]):
                    raise HTTPException(status_code=401, detail="Invalid credentials")

                # Update last login
                await conn.execute(
                    "UPDATE users SET last_login = $1 WHERE user_id = $2",
                    datetime.utcnow(), user["user_id"]
                )

                # Create JWT token
                user_data = {
                    "user_id": user["user_id"],
                    "username": user["username"],
                    "email": user["email"]
                }

                token = self.create_jwt_token(user_data)

                return {
                    "message": "Login successful",
                    "user": {
                        "user_id": user["user_id"],
                        "username": user["username"],
                        "email": user["email"]
                    },
                    "access_token": token,
                    "token_type": "bearer"
                }

        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error authenticating user: {e}")
            raise HTTPException(status_code=500, detail="Authentication failed")

    async def get_current_user(self, token: str) -> Dict:
        """Get current user from token."""
        payload = self.verify_jwt_token(token)

        try:
            async with db.get_connection() as conn:
                user = await conn.fetchrow(
                    """
                    SELECT user_id, username, email, is_active
                    FROM users
                    WHERE user_id = $1 AND is_active = true
                    """,
                    payload.get("user_id")
                )

                if not user:
                    raise HTTPException(status_code=401, detail="User not found")

                return {
                    "user_id": user["user_id"],
                    "username": user["username"],
                    "email": user["email"]
                }

        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error getting current user: {e}")
            raise HTTPException(status_code=401, detail="Invalid user session")

    async def get_user_portfolios(self, user_id: int) -> list:
        """Get user's portfolios."""
        try:
            async with db.get_connection() as conn:
                portfolios = await conn.fetch(
                    """
                    SELECT portfolio_id, name, description, created_at, updated_at
                    FROM portfolios
                    WHERE user_id = $1
                    ORDER BY created_at DESC
                    """,
                    user_id
                )

                portfolio_list = []
                for portfolio in portfolios:
                    # Get portfolio holdings
                    holdings = await conn.fetch(
                        """
                        SELECT symbol, shares, average_price, current_price, total_value
                        FROM portfolio_holdings
                        WHERE portfolio_id = $1
                        """,
                        portfolio["portfolio_id"]
                    )

                    portfolio_data = {
                        "portfolio_id": portfolio["portfolio_id"],
                        "name": portfolio["name"],
                        "description": portfolio["description"],
                        "created_at": portfolio["created_at"].isoformat(),
                        "updated_at": portfolio["updated_at"].isoformat(),
                        "holdings": [dict(holding) for holding in holdings],
                        "total_value": sum(holding["total_value"] or 0 for holding in holdings)
                    }

                    portfolio_list.append(portfolio_data)

                return portfolio_list

        except Exception as e:
            logger.error(f"Error getting user portfolios: {e}")
            return []