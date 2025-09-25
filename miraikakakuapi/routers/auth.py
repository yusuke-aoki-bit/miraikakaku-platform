from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
from typing import Dict
import logging
from ..services.auth_service import AuthService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/auth", tags=["authentication"])
security = HTTPBearer()

# Service instance
auth_service = AuthService()


# Request/Response Models
class UserRegister(BaseModel):
    username: str
    email: str
    password: str


class UserLogin(BaseModel):
    username: str
    password: str


# Dependency to get current user
async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> Dict:
    """Dependency to get current authenticated user."""
    try:
        token = credentials.credentials
        user = await auth_service.get_current_user(token)
        return user
    except Exception as e:
        logger.error(f"Authentication error: {e}")
        raise HTTPException(status_code=401, detail="Invalid authentication credentials")


@router.post("/register")
async def register(user_data: UserRegister):
    """Register a new user account."""
    try:
        # Validate input
        if not user_data.username or len(user_data.username) < 3:
            raise HTTPException(status_code=400, detail="Username must be at least 3 characters")

        if not user_data.email or "@" not in user_data.email:
            raise HTTPException(status_code=400, detail="Valid email address is required")

        if not user_data.password or len(user_data.password) < 6:
            raise HTTPException(status_code=400, detail="Password must be at least 6 characters")

        # Register user
        result = await auth_service.register_user(
            user_data.username.strip(),
            user_data.email.strip().lower(),
            user_data.password
        )

        return result

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Registration error: {e}")
        raise HTTPException(status_code=500, detail="Registration failed. Please try again.")


@router.post("/login")
async def login(user_data: UserLogin):
    """Authenticate user login."""
    try:
        # Validate input
        if not user_data.username or not user_data.password:
            raise HTTPException(status_code=400, detail="Username and password are required")

        # Authenticate user
        result = await auth_service.authenticate_user(
            user_data.username.strip(),
            user_data.password
        )

        return result

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Login error: {e}")
        raise HTTPException(status_code=500, detail="Authentication failed. Please try again.")


@router.get("/me")
async def get_me(current_user: Dict = Depends(get_current_user)):
    """Get current user information."""
    try:
        return {
            "user": current_user,
            "message": "User information retrieved successfully"
        }

    except Exception as e:
        logger.error(f"Get user info error: {e}")
        raise HTTPException(status_code=500, detail="Error retrieving user information")


@router.get("/verify")
async def verify_token(current_user: Dict = Depends(get_current_user)):
    """Verify if the current token is valid."""
    try:
        return {
            "valid": True,
            "user_id": current_user.get("user_id"),
            "username": current_user.get("username"),
            "message": "Token is valid"
        }

    except Exception as e:
        logger.error(f"Token verification error: {e}")
        raise HTTPException(status_code=401, detail="Invalid or expired token")