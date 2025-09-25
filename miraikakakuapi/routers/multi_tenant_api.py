"""
Multi-tenant API Endpoints
Phase 3.2 - Enterprise Multi-tenant APIs

Complete tenant-isolated API endpoints with RBAC
"""

import uuid
import logging
from datetime import datetime, timezone, timedelta
from typing import Dict, List, Optional, Any

from fastapi import APIRouter, Depends, HTTPException, status, Query, Path, Body
from pydantic import BaseModel, EmailStr, validator
import asyncio

from services.multi_tenant_manager import get_tenant_manager, MultiTenantManager, PlanType
from middleware.tenant_auth import (
    TenantContext, get_tenant_context, get_current_user, get_current_organization,
    require_permission, require_role, require_feature, require_admin, require_manager_or_admin,
    check_tenant_rate_limit, create_access_token, create_refresh_token
)
from database.multi_tenant_models import User, Organization, UserRole, OrganizationStatus

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create API router
router = APIRouter(prefix="/api/v1/tenant", tags=["Multi-tenant"])

# Pydantic models for request/response

class OrganizationCreate(BaseModel):
    name: str
    display_name: str
    primary_contact_email: EmailStr
    plan_type: str = "basic"
    industry: Optional[str] = None
    company_size: Optional[str] = None
    phone: Optional[str] = None
    website: Optional[str] = None

    @validator('plan_type')
    def validate_plan_type(cls, v):
        valid_plans = [plan.value for plan in PlanType]
        if v not in valid_plans:
            raise ValueError(f'Plan type must be one of: {valid_plans}')
        return v

class OrganizationUpdate(BaseModel):
    display_name: Optional[str] = None
    phone: Optional[str] = None
    website: Optional[str] = None
    industry: Optional[str] = None
    company_size: Optional[str] = None

class UserCreate(BaseModel):
    email: EmailStr
    username: str
    password: str
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    role: str = "viewer"

    @validator('role')
    def validate_role(cls, v):
        valid_roles = [role.value for role in UserRole]
        if v not in valid_roles:
            raise ValueError(f'Role must be one of: {valid_roles}')
        return v

class UserUpdate(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    role: Optional[str] = None
    is_active: Optional[bool] = None
    permissions: Optional[List[str]] = None

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class LoginResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int = 3600
    user: Dict[str, Any]
    organization: Dict[str, Any]

class TenantStockDataRequest(BaseModel):
    symbol: str
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None

class TenantPredictionRequest(BaseModel):
    symbol: str
    horizon_days: int = 30
    model_type: str = "ensemble"
    confidence_threshold: float = 0.8

class WatchlistCreate(BaseModel):
    name: str
    symbols: List[str]
    description: Optional[str] = None
    is_public: bool = False

class AlertCreate(BaseModel):
    name: str
    symbol: str
    alert_type: str
    conditions: Dict[str, Any]
    notification_channels: List[str] = ["email"]

# Authentication endpoints

@router.post("/auth/login", response_model=LoginResponse)
async def login(
    login_data: LoginRequest,
    tenant_manager: MultiTenantManager = Depends(get_tenant_manager)
):
    """Authenticate user and return tokens"""
    user = tenant_manager.authenticate_user(login_data.email, login_data.password)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User account is inactive"
        )

    # Get organization
    organization = tenant_manager.get_organization(user.organization_id)
    if not organization:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Organization not found"
        )

    # Check organization status
    if organization.status not in [OrganizationStatus.ACTIVE.value, OrganizationStatus.TRIAL.value]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Organization is {organization.status}"
        )

    # Create tokens
    access_token = create_access_token(user.id)
    refresh_token = create_refresh_token(user.id)

    return LoginResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        user={
            "id": str(user.id),
            "email": user.email,
            "username": user.username,
            "full_name": user.full_name,
            "role": user.role,
            "permissions": user.permissions
        },
        organization={
            "id": str(organization.id),
            "name": organization.name,
            "display_name": organization.display_name,
            "plan_type": organization.plan_type,
            "status": organization.status,
            "enabled_features": organization.enabled_features
        }
    )

@router.get("/auth/me")
async def get_current_user_info(
    user: User = Depends(get_current_user),
    organization: Organization = Depends(get_current_organization)
):
    """Get current user and organization info"""
    return {
        "user": {
            "id": str(user.id),
            "email": user.email,
            "username": user.username,
            "full_name": user.full_name,
            "role": user.role,
            "permissions": user.permissions,
            "last_login_at": user.last_login_at.isoformat() if user.last_login_at else None
        },
        "organization": {
            "id": str(organization.id),
            "name": organization.name,
            "display_name": organization.display_name,
            "plan_type": organization.plan_type,
            "status": organization.status,
            "enabled_features": organization.enabled_features
        }
    }

# Organization management endpoints

@router.post("/organizations", dependencies=[Depends(require_admin())])
async def create_organization(
    org_data: OrganizationCreate,
    tenant_manager: MultiTenantManager = Depends(get_tenant_manager)
):
    """Create new organization (Admin only)"""
    try:
        plan_type = PlanType(org_data.plan_type)
        organization = tenant_manager.create_organization(
            name=org_data.name,
            display_name=org_data.display_name,
            primary_contact_email=org_data.primary_contact_email,
            plan_type=plan_type,
            industry=org_data.industry,
            phone=org_data.phone,
            website=org_data.website
        )

        return {
            "id": str(organization.id),
            "name": organization.name,
            "slug": organization.slug,
            "plan_type": organization.plan_type,
            "status": organization.status
        }

    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

@router.get("/organization")
async def get_organization_info(
    organization: Organization = Depends(get_current_organization),
    tenant_manager: MultiTenantManager = Depends(get_tenant_manager)
):
    """Get current organization detailed info"""
    dashboard_data = tenant_manager.get_organization_dashboard_data(organization.id)

    return {
        "organization": dashboard_data.get("organization", {}),
        "users": dashboard_data.get("users", {}),
        "usage": dashboard_data.get("usage", {}),
        "recent_activity": dashboard_data.get("recent_activity", {}),
        "subscription": {
            "plan_type": organization.plan_type,
            "status": organization.status,
            "trial_end_date": organization.trial_end_date.isoformat() if organization.trial_end_date else None,
            "subscription_end_date": organization.subscription_end_date.isoformat() if organization.subscription_end_date else None
        }
    }

@router.put("/organization")
async def update_organization(
    org_update: OrganizationUpdate,
    organization: Organization = Depends(get_current_organization),
    context: TenantContext = Depends(require_manager_or_admin()),
    tenant_manager: MultiTenantManager = Depends(get_tenant_manager)
):
    """Update organization information"""
    try:
        updated_org = tenant_manager.update_organization(
            organization.id,
            **org_update.dict(exclude_unset=True)
        )

        return {
            "id": str(updated_org.id),
            "name": updated_org.name,
            "display_name": updated_org.display_name,
            "phone": updated_org.phone,
            "website": updated_org.website,
            "industry": updated_org.industry,
            "updated_at": updated_org.updated_at.isoformat()
        }

    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

@router.post("/organization/upgrade")
async def upgrade_organization_plan(
    new_plan: str = Body(..., embed=True),
    organization: Organization = Depends(get_current_organization),
    context: TenantContext = Depends(require_admin()),
    tenant_manager: MultiTenantManager = Depends(get_tenant_manager)
):
    """Upgrade organization plan"""
    try:
        plan_type = PlanType(new_plan)
        updated_org = tenant_manager.upgrade_organization_plan(organization.id, plan_type)

        return {
            "message": f"Plan upgraded to {new_plan}",
            "organization": {
                "plan_type": updated_org.plan_type,
                "enabled_features": updated_org.enabled_features,
                "limits": {
                    "max_users": updated_org.max_users,
                    "max_api_calls_per_month": updated_org.max_api_calls_per_month,
                    "max_predictions_per_day": updated_org.max_predictions_per_day,
                    "max_symbols_tracked": updated_org.max_symbols_tracked
                }
            }
        }

    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

# User management endpoints

@router.get("/users")
async def get_organization_users(
    organization: Organization = Depends(get_current_organization),
    context: TenantContext = Depends(require_manager_or_admin()),
    tenant_manager: MultiTenantManager = Depends(get_tenant_manager),
    active_only: bool = Query(True, description="Return only active users")
):
    """Get all users in organization"""
    users = tenant_manager.get_organization_users(organization.id, active_only)

    return {
        "users": [
            {
                "id": str(user.id),
                "email": user.email,
                "username": user.username,
                "full_name": user.full_name,
                "role": user.role,
                "is_active": user.is_active,
                "last_login_at": user.last_login_at.isoformat() if user.last_login_at else None,
                "created_at": user.created_at.isoformat()
            }
            for user in users
        ],
        "total": len(users)
    }

@router.post("/users")
async def create_user(
    user_data: UserCreate,
    organization: Organization = Depends(get_current_organization),
    context: TenantContext = Depends(require_manager_or_admin()),
    tenant_manager: MultiTenantManager = Depends(get_tenant_manager)
):
    """Create new user in organization"""
    try:
        role = UserRole(user_data.role)
        user = tenant_manager.create_user(
            organization_id=organization.id,
            email=user_data.email,
            username=user_data.username,
            password=user_data.password,
            role=role,
            first_name=user_data.first_name,
            last_name=user_data.last_name
        )

        return {
            "id": str(user.id),
            "email": user.email,
            "username": user.username,
            "role": user.role,
            "created_at": user.created_at.isoformat()
        }

    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

@router.put("/users/{user_id}")
async def update_user(
    user_id: uuid.UUID = Path(...),
    user_update: UserUpdate = ...,
    organization: Organization = Depends(get_current_organization),
    context: TenantContext = Depends(require_manager_or_admin()),
    tenant_manager: MultiTenantManager = Depends(get_tenant_manager)
):
    """Update user in organization"""
    with tenant_manager.get_session() as session:
        user = session.query(User).filter_by(
            id=user_id,
            organization_id=organization.id
        ).first()

        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

        # Update user fields
        update_data = user_update.dict(exclude_unset=True)
        for key, value in update_data.items():
            if hasattr(user, key):
                setattr(user, key, value)

        user.updated_at = datetime.now(timezone.utc)
        session.commit()
        session.refresh(user)

        return {
            "id": str(user.id),
            "email": user.email,
            "username": user.username,
            "role": user.role,
            "is_active": user.is_active,
            "updated_at": user.updated_at.isoformat()
        }

# Data access endpoints (tenant-isolated)

@router.get("/data/stocks/{symbol}/prices")
async def get_tenant_stock_prices(
    symbol: str = Path(...),
    start_date: Optional[datetime] = Query(None),
    end_date: Optional[datetime] = Query(None),
    organization: Organization = Depends(get_current_organization),
    context: TenantContext = Depends(check_tenant_rate_limit("stock_data", 1000)),
    tenant_manager: MultiTenantManager = Depends(get_tenant_manager)
):
    """Get stock price data (tenant-isolated)"""
    stock_data = tenant_manager.get_tenant_stock_data(
        organization.id,
        symbol.upper(),
        start_date,
        end_date
    )

    return {
        "symbol": symbol.upper(),
        "organization_id": str(organization.id),
        "data_points": len(stock_data),
        "data": [
            {
                "date": price.date.isoformat(),
                "open": price.open_price,
                "high": price.high_price,
                "low": price.low_price,
                "close": price.close_price,
                "volume": price.volume,
                "data_source": price.data_source,
                "quality_score": price.data_quality_score
            }
            for price in stock_data
        ]
    }

@router.get("/data/stocks/{symbol}/predictions")
async def get_tenant_predictions(
    symbol: str = Path(...),
    limit: int = Query(100, ge=1, le=1000),
    organization: Organization = Depends(get_current_organization),
    context: TenantContext = Depends(require_feature("predictions")),
    tenant_manager: MultiTenantManager = Depends(get_tenant_manager)
):
    """Get AI predictions (tenant-isolated)"""
    predictions = tenant_manager.get_tenant_predictions(
        organization.id,
        symbol.upper(),
        limit
    )

    return {
        "symbol": symbol.upper(),
        "organization_id": str(organization.id),
        "predictions_count": len(predictions),
        "predictions": [
            {
                "prediction_date": pred.prediction_date.isoformat(),
                "target_date": pred.target_date.isoformat(),
                "predicted_price": pred.predicted_price,
                "confidence_score": pred.confidence_score,
                "model_version": pred.model_version,
                "factors": pred.factors,
                "actual_price": pred.actual_price,
                "accuracy_score": pred.accuracy_score
            }
            for pred in predictions
        ]
    }

@router.post("/data/predictions/request")
async def request_prediction(
    prediction_request: TenantPredictionRequest,
    organization: Organization = Depends(get_current_organization),
    user: User = Depends(get_current_user),
    context: TenantContext = Depends(require_feature("realtime_streaming")),
    tenant_manager: MultiTenantManager = Depends(get_tenant_manager)
):
    """Request new AI prediction (tenant-isolated)"""
    # This would integrate with the realtime inference engine
    # For now, return a placeholder response

    return {
        "request_id": str(uuid.uuid4()),
        "symbol": prediction_request.symbol.upper(),
        "status": "queued",
        "estimated_completion": (datetime.now(timezone.utc) + timedelta(seconds=30)).isoformat(),
        "model_type": prediction_request.model_type,
        "confidence_threshold": prediction_request.confidence_threshold
    }

# Watchlist management

@router.get("/watchlists")
async def get_user_watchlists(
    user: User = Depends(get_current_user),
    organization: Organization = Depends(get_current_organization),
    tenant_manager: MultiTenantManager = Depends(get_tenant_manager)
):
    """Get user's watchlists"""
    with tenant_manager.get_session() as session:
        from database.multi_tenant_models import TenantWatchlist

        watchlists = (session.query(TenantWatchlist)
                     .filter_by(organization_id=organization.id, user_id=user.id)
                     .order_by(TenantWatchlist.created_at.desc())
                     .all())

        return {
            "watchlists": [
                {
                    "id": str(watchlist.id),
                    "name": watchlist.name,
                    "description": watchlist.description,
                    "symbols": watchlist.symbols,
                    "is_public": watchlist.is_public,
                    "alert_enabled": watchlist.alert_enabled,
                    "created_at": watchlist.created_at.isoformat(),
                    "symbols_count": len(watchlist.symbols or [])
                }
                for watchlist in watchlists
            ]
        }

@router.post("/watchlists")
async def create_watchlist(
    watchlist_data: WatchlistCreate,
    user: User = Depends(get_current_user),
    organization: Organization = Depends(get_current_organization),
    tenant_manager: MultiTenantManager = Depends(get_tenant_manager)
):
    """Create new watchlist"""
    try:
        watchlist = tenant_manager.create_tenant_watchlist(
            organization_id=organization.id,
            user_id=user.id,
            name=watchlist_data.name,
            symbols=watchlist_data.symbols,
            description=watchlist_data.description,
            is_public=watchlist_data.is_public
        )

        return {
            "id": str(watchlist.id),
            "name": watchlist.name,
            "symbols": watchlist.symbols,
            "symbols_count": len(watchlist.symbols or []),
            "created_at": watchlist.created_at.isoformat()
        }

    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

# Analytics and reporting

@router.get("/analytics/usage")
async def get_usage_analytics(
    days: int = Query(30, ge=1, le=365),
    organization: Organization = Depends(get_current_organization),
    context: TenantContext = Depends(require_permission("view_analytics")),
    tenant_manager: MultiTenantManager = Depends(get_tenant_manager)
):
    """Get usage analytics for organization"""
    usage_data = tenant_manager.check_usage_limits(organization.id)

    return {
        "organization_id": str(organization.id),
        "period_days": days,
        "current_usage": usage_data,
        "plan_limits": {
            "max_users": organization.max_users,
            "max_api_calls_per_month": organization.max_api_calls_per_month,
            "max_predictions_per_day": organization.max_predictions_per_day,
            "max_symbols_tracked": organization.max_symbols_tracked
        }
    }

@router.get("/audit-logs")
async def get_audit_logs(
    start_date: Optional[datetime] = Query(None),
    end_date: Optional[datetime] = Query(None),
    event_types: Optional[List[str]] = Query(None),
    limit: int = Query(100, ge=1, le=1000),
    organization: Organization = Depends(get_current_organization),
    context: TenantContext = Depends(require_permission("view_audit")),
    tenant_manager: MultiTenantManager = Depends(get_tenant_manager)
):
    """Get audit logs for organization"""
    audit_logs = tenant_manager.get_audit_logs(
        organization.id,
        start_date,
        end_date,
        event_types,
        limit
    )

    return {
        "organization_id": str(organization.id),
        "logs_count": len(audit_logs),
        "logs": [
            {
                "id": str(log.id),
                "event_type": log.event_type,
                "event_category": log.event_category,
                "description": log.description,
                "user_id": str(log.user_id) if log.user_id else None,
                "resource_type": log.resource_type,
                "resource_id": log.resource_id,
                "risk_level": log.risk_level,
                "ip_address": log.ip_address,
                "timestamp": log.timestamp.isoformat(),
                "details": log.details
            }
            for log in audit_logs
        ]
    }

# Health check for tenant-specific services

@router.get("/health")
async def tenant_health_check(
    organization: Organization = Depends(get_current_organization),
    tenant_manager: MultiTenantManager = Depends(get_tenant_manager)
):
    """Health check for tenant services"""
    dashboard_data = tenant_manager.get_organization_dashboard_data(organization.id)

    return {
        "status": "healthy",
        "organization": {
            "id": str(organization.id),
            "name": organization.name,
            "status": organization.status,
            "plan_type": organization.plan_type
        },
        "system": {
            "database": "connected",
            "cache": "available",
            "services": "operational"
        },
        "usage_summary": dashboard_data.get("usage", {}),
        "timestamp": datetime.now(timezone.utc).isoformat()
    }