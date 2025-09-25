"""
Multi-tenant Authentication & Authorization Middleware
Phase 3.2 - Enhanced RBAC System

Complete tenant isolation and permission management
"""

import uuid
import logging
from typing import Dict, List, Optional, Any, Callable
from functools import wraps
from datetime import datetime, timezone

from fastapi import Request, HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from starlette.middleware.base import BaseHTTPMiddleware
import jwt
from jwt import InvalidTokenError

from services.multi_tenant_manager import get_tenant_manager, MultiTenantManager
from database.multi_tenant_models import User, Organization, UserRole

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Security configurations
JWT_SECRET = "your-super-secret-jwt-key"  # Should be from environment
JWT_ALGORITHM = "HS256"
API_KEY_PREFIX = "mk_"

security = HTTPBearer(auto_error=False)

class TenantContext:
    """Current request tenant context"""

    def __init__(self):
        self.user: Optional[User] = None
        self.organization: Optional[Organization] = None
        self.permissions: List[str] = []
        self.is_authenticated: bool = False
        self.auth_method: Optional[str] = None  # 'jwt', 'api_key', 'session'

    @property
    def user_id(self) -> Optional[uuid.UUID]:
        return self.user.id if self.user else None

    @property
    def organization_id(self) -> Optional[uuid.UUID]:
        return self.organization.id if self.organization else None

    @property
    def user_role(self) -> Optional[str]:
        return self.user.role if self.user else None

    @property
    def is_admin(self) -> bool:
        return self.user_role == UserRole.ADMIN.value if self.user else False

    @property
    def is_manager(self) -> bool:
        return self.user_role in [UserRole.ADMIN.value, UserRole.MANAGER.value] if self.user else False

    def has_permission(self, permission: str) -> bool:
        """Check if user has specific permission"""
        if not self.user:
            return False

        return (
            permission in self.permissions or
            self.user.has_permission(permission) or
            self.is_admin  # Admin has all permissions
        )

    def has_feature_access(self, feature: str) -> bool:
        """Check if organization has feature access"""
        if not self.organization:
            return False

        return self.organization.has_feature(feature)

class TenantAuthMiddleware(BaseHTTPMiddleware):
    """Middleware for tenant authentication and context"""

    def __init__(self, app, tenant_manager: MultiTenantManager):
        super().__init__(app)
        self.tenant_manager = tenant_manager

    async def dispatch(self, request: Request, call_next):
        # Initialize tenant context
        tenant_context = TenantContext()

        # Try to authenticate the request
        try:
            await self._authenticate_request(request, tenant_context)
        except Exception as e:
            logger.error(f"Authentication error: {e}")
            # Continue with unauthenticated context for public endpoints

        # Add context to request
        request.state.tenant_context = tenant_context

        # Process request
        response = await call_next(request)

        # Log request if authenticated
        if tenant_context.is_authenticated:
            await self._log_request(request, tenant_context)

        return response

    async def _authenticate_request(self, request: Request, context: TenantContext):
        """Authenticate request and populate context"""

        # Check for JWT token in Authorization header
        auth_header = request.headers.get("authorization")
        if auth_header and auth_header.startswith("Bearer "):
            token = auth_header.split(" ")[1]

            if await self._authenticate_jwt(token, context):
                context.auth_method = "jwt"
                return

        # Check for API key
        api_key = request.headers.get("x-api-key") or request.query_params.get("api_key")
        if api_key and api_key.startswith(API_KEY_PREFIX):
            if await self._authenticate_api_key(api_key, context):
                context.auth_method = "api_key"
                return

        # Check for session (if using session-based auth)
        session_token = request.cookies.get("session_token")
        if session_token:
            if await self._authenticate_session(session_token, context):
                context.auth_method = "session"
                return

    async def _authenticate_jwt(self, token: str, context: TenantContext) -> bool:
        """Authenticate JWT token"""
        try:
            payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
            user_id = payload.get("user_id")

            if not user_id:
                return False

            user = self.tenant_manager.get_session().query(User).filter_by(
                id=uuid.UUID(user_id),
                is_active=True
            ).first()

            if user:
                context.user = user
                context.organization = self.tenant_manager.get_organization(user.organization_id)
                context.permissions = user.permissions or []
                context.is_authenticated = True
                return True

        except (InvalidTokenError, ValueError, AttributeError) as e:
            logger.warning(f"JWT authentication failed: {e}")

        return False

    async def _authenticate_api_key(self, api_key: str, context: TenantContext) -> bool:
        """Authenticate API key"""
        user = self.tenant_manager.authenticate_api_key(api_key)

        if user:
            context.user = user
            context.organization = self.tenant_manager.get_organization(user.organization_id)
            context.permissions = user.permissions or []
            context.is_authenticated = True
            return True

        return False

    async def _authenticate_session(self, session_token: str, context: TenantContext) -> bool:
        """Authenticate session token"""
        # Implementation would check UserSession table
        # For now, return False (not implemented)
        return False

    async def _log_request(self, request: Request, context: TenantContext):
        """Log authenticated request"""
        if context.organization_id and context.user_id:
            # Could implement request logging here
            pass

# Dependency functions for FastAPI

def get_tenant_context(request: Request) -> TenantContext:
    """Get current tenant context from request"""
    return getattr(request.state, 'tenant_context', TenantContext())

def get_current_user(context: TenantContext = Depends(get_tenant_context)) -> User:
    """Get current authenticated user (required)"""
    if not context.is_authenticated or not context.user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return context.user

def get_current_user_optional(context: TenantContext = Depends(get_tenant_context)) -> Optional[User]:
    """Get current authenticated user (optional)"""
    return context.user if context.is_authenticated else None

def get_current_organization(context: TenantContext = Depends(get_tenant_context)) -> Organization:
    """Get current user's organization (required)"""
    if not context.is_authenticated or not context.organization:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Organization authentication required",
        )
    return context.organization

def get_current_organization_optional(context: TenantContext = Depends(get_tenant_context)) -> Optional[Organization]:
    """Get current user's organization (optional)"""
    return context.organization if context.is_authenticated else None

# Permission decorators and dependency functions

def require_permission(permission: str):
    """Require specific permission"""
    def permission_dependency(context: TenantContext = Depends(get_tenant_context)):
        if not context.is_authenticated:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Authentication required"
            )

        if not context.has_permission(permission):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Permission '{permission}' required"
            )

        return context

    return permission_dependency

def require_role(required_roles: List[UserRole]):
    """Require specific user role"""
    def role_dependency(context: TenantContext = Depends(get_tenant_context)):
        if not context.is_authenticated:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Authentication required"
            )

        if context.user_role not in [role.value for role in required_roles]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Role {required_roles} required"
            )

        return context

    return role_dependency

def require_feature(feature: str):
    """Require organization to have specific feature"""
    def feature_dependency(context: TenantContext = Depends(get_tenant_context)):
        if not context.is_authenticated:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Authentication required"
            )

        if not context.has_feature_access(feature):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Feature '{feature}' not available in your plan"
            )

        return context

    return feature_dependency

def require_admin():
    """Require admin role"""
    return require_role([UserRole.ADMIN])

def require_manager_or_admin():
    """Require manager or admin role"""
    return require_role([UserRole.MANAGER, UserRole.ADMIN])

# Decorator functions for non-FastAPI usage

def tenant_required(func):
    """Decorator to require tenant authentication"""
    @wraps(func)
    async def wrapper(*args, **kwargs):
        # Implementation would depend on context
        return await func(*args, **kwargs)
    return wrapper

def permission_required(permission: str):
    """Decorator to require specific permission"""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Implementation would check permission
            return await func(*args, **kwargs)
        return wrapper
    return decorator

# Utility functions

def create_access_token(user_id: uuid.UUID, expires_delta: Optional[int] = None) -> str:
    """Create JWT access token"""
    if expires_delta is None:
        expires_delta = 3600  # 1 hour

    payload = {
        "user_id": str(user_id),
        "exp": datetime.now(timezone.utc).timestamp() + expires_delta,
        "iat": datetime.now(timezone.utc).timestamp(),
        "type": "access"
    }

    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)

def create_refresh_token(user_id: uuid.UUID) -> str:
    """Create JWT refresh token"""
    payload = {
        "user_id": str(user_id),
        "exp": datetime.now(timezone.utc).timestamp() + (30 * 24 * 3600),  # 30 days
        "iat": datetime.now(timezone.utc).timestamp(),
        "type": "refresh"
    }

    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)

def verify_token(token: str) -> Dict[str, Any]:
    """Verify and decode JWT token"""
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        return payload
    except InvalidTokenError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid token: {e}"
        )

# Rate limiting per tenant

class TenantRateLimiter:
    """Rate limiter per tenant organization"""

    def __init__(self):
        self.limits = {}  # organization_id -> rate limit info

    def check_rate_limit(self, organization_id: uuid.UUID, endpoint: str, limit: int, window: int = 3600) -> bool:
        """Check if request is within rate limit"""
        # Implementation would use Redis or in-memory cache
        # For now, always return True
        return True

    def increment_usage(self, organization_id: uuid.UUID, endpoint: str):
        """Increment usage counter"""
        # Implementation would track usage
        pass

# Global rate limiter instance
tenant_rate_limiter = TenantRateLimiter()

# Rate limiting dependency
def check_tenant_rate_limit(endpoint: str, limit: int = 1000, window: int = 3600):
    """Rate limiting dependency for FastAPI endpoints"""
    def rate_limit_dependency(context: TenantContext = Depends(get_tenant_context)):
        if context.organization_id:
            if not tenant_rate_limiter.check_rate_limit(context.organization_id, endpoint, limit, window):
                raise HTTPException(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    detail="Rate limit exceeded"
                )

            tenant_rate_limiter.increment_usage(context.organization_id, endpoint)

        return context

    return rate_limit_dependency

# Usage tracking

def track_api_usage(context: TenantContext, endpoint: str, method: str):
    """Track API usage for billing and analytics"""
    if context.organization_id:
        # Implementation would update usage counters
        # Could integrate with subscription billing
        pass

# WebSocket authentication

async def authenticate_websocket(token: str, tenant_manager: MultiTenantManager) -> Optional[TenantContext]:
    """Authenticate WebSocket connection"""
    context = TenantContext()

    if await TenantAuthMiddleware(None, tenant_manager)._authenticate_jwt(token, context):
        return context

    return None