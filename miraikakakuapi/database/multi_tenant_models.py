"""
Multi-tenant Database Models
Phase 3.2 - マルチテナント・エンタープライズ統合

Complete data isolation and organization-specific configurations
"""

import uuid
from datetime import datetime, timezone
from typing import Dict, List, Optional, Any, Set
from enum import Enum
import json

from sqlalchemy import (
    Column, String, Integer, Float, DateTime, Boolean, Text, JSON,
    ForeignKey, Index, UniqueConstraint, CheckConstraint, Table
)
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, validates, Session
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.sql import func

Base = declarative_base()

class PlanType(Enum):
    BASIC = "basic"
    PROFESSIONAL = "professional"
    ENTERPRISE = "enterprise"
    CUSTOM = "custom"

class OrganizationStatus(Enum):
    ACTIVE = "active"
    SUSPENDED = "suspended"
    TRIAL = "trial"
    PENDING = "pending"

class UserRole(Enum):
    ADMIN = "admin"
    MANAGER = "manager"
    ANALYST = "analyst"
    VIEWER = "viewer"
    API_USER = "api_user"
    COMPLIANCE = "compliance"

class SubscriptionStatus(Enum):
    ACTIVE = "active"
    EXPIRED = "expired"
    CANCELLED = "cancelled"
    PENDING = "pending"

# Organization and User Management

class Organization(Base):
    """組織・企業テーブル"""
    __tablename__ = 'organizations'

    # Primary Key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    # Basic Information
    name = Column(String(255), nullable=False, index=True)
    display_name = Column(String(255), nullable=False)
    slug = Column(String(100), nullable=False, unique=True, index=True)

    # Contact Information
    domain = Column(String(255))  # email domain for SSO
    primary_contact_email = Column(String(255), nullable=False)
    phone = Column(String(50))
    website = Column(String(255))

    # Address
    address_line1 = Column(String(255))
    address_line2 = Column(String(255))
    city = Column(String(100))
    state = Column(String(100))
    postal_code = Column(String(20))
    country = Column(String(2))  # ISO country code

    # Business Information
    industry = Column(String(100))
    company_size = Column(String(50))  # "1-10", "11-50", "51-200", etc.
    tax_id = Column(String(50))
    registration_number = Column(String(100))

    # Plan and Status
    plan_type = Column(String(20), nullable=False, default=PlanType.BASIC.value)
    status = Column(String(20), nullable=False, default=OrganizationStatus.ACTIVE.value)

    # Limits and Quotas
    max_users = Column(Integer, default=5)
    max_api_calls_per_month = Column(Integer, default=10000)
    max_predictions_per_day = Column(Integer, default=1000)
    max_symbols_tracked = Column(Integer, default=50)

    # Features (JSON array of enabled features)
    enabled_features = Column(JSONB, default=list)

    # Settings (Organization-specific configurations)
    settings = Column(JSONB, default=dict)

    # Metadata
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    trial_end_date = Column(DateTime(timezone=True))
    subscription_end_date = Column(DateTime(timezone=True))

    # Relationships
    users = relationship("User", back_populates="organization", cascade="all, delete-orphan")
    subscriptions = relationship("Subscription", back_populates="organization", cascade="all, delete-orphan")
    audit_logs = relationship("AuditLog", back_populates="organization")

    # Indexes and Constraints
    __table_args__ = (
        Index('idx_org_status_plan', 'status', 'plan_type'),
        Index('idx_org_created_at', 'created_at'),
        CheckConstraint("plan_type IN ('basic', 'professional', 'enterprise', 'custom')", name='chk_plan_type'),
        CheckConstraint("status IN ('active', 'suspended', 'trial', 'pending')", name='chk_org_status'),
    )

    @validates('slug')
    def validate_slug(self, key, slug):
        import re
        if not re.match(r'^[a-z0-9-]+$', slug):
            raise ValueError('Slug must contain only lowercase letters, numbers, and hyphens')
        return slug

    @hybrid_property
    def is_trial(self):
        return self.status == OrganizationStatus.TRIAL.value

    @hybrid_property
    def is_enterprise(self):
        return self.plan_type == PlanType.ENTERPRISE.value

    def get_feature_limit(self, feature: str) -> Optional[int]:
        """Get specific feature limit for this organization"""
        limits = self.settings.get('feature_limits', {})
        return limits.get(feature)

    def has_feature(self, feature: str) -> bool:
        """Check if organization has specific feature enabled"""
        return feature in (self.enabled_features or [])

class User(Base):
    """ユーザーテーブル（マルチテナント対応）"""
    __tablename__ = 'users'

    # Primary Key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    organization_id = Column(UUID(as_uuid=True), ForeignKey('organizations.id'), nullable=False, index=True)

    # Authentication
    email = Column(String(255), nullable=False, unique=True, index=True)
    username = Column(String(100), nullable=False, index=True)
    password_hash = Column(String(255))

    # Profile
    first_name = Column(String(100))
    last_name = Column(String(100))
    display_name = Column(String(200))
    avatar_url = Column(String(500))

    # Role and Permissions
    role = Column(String(20), nullable=False, default=UserRole.VIEWER.value)
    permissions = Column(JSONB, default=list)  # Additional custom permissions

    # API Access
    api_key = Column(String(100), unique=True, index=True)
    api_key_expires_at = Column(DateTime(timezone=True))

    # Settings
    timezone = Column(String(50), default='UTC')
    language = Column(String(5), default='en')
    preferences = Column(JSONB, default=dict)

    # Status
    is_active = Column(Boolean, default=True, index=True)
    is_email_verified = Column(Boolean, default=False)
    email_verification_token = Column(String(100))

    # Rate Limiting
    api_rate_limit_per_hour = Column(Integer, default=1000)

    # Metadata
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    last_login_at = Column(DateTime(timezone=True))
    last_activity_at = Column(DateTime(timezone=True))

    # Relationships
    organization = relationship("Organization", back_populates="users")
    audit_logs = relationship("AuditLog", back_populates="user")
    user_sessions = relationship("UserSession", back_populates="user", cascade="all, delete-orphan")

    # Indexes and Constraints
    __table_args__ = (
        Index('idx_user_org_role', 'organization_id', 'role'),
        Index('idx_user_active', 'is_active'),
        Index('idx_user_last_activity', 'last_activity_at'),
        UniqueConstraint('organization_id', 'username', name='uq_org_username'),
        CheckConstraint("role IN ('admin', 'manager', 'analyst', 'viewer', 'api_user', 'compliance')", name='chk_user_role'),
    )

    @hybrid_property
    def full_name(self):
        return f"{self.first_name} {self.last_name}".strip()

    def has_permission(self, permission: str) -> bool:
        """Check if user has specific permission"""
        # Check role-based permissions
        role_permissions = {
            UserRole.ADMIN.value: ['admin', 'manage_users', 'manage_organization', 'view_audit', 'manage_compliance'],
            UserRole.MANAGER.value: ['manage_team', 'view_reports', 'manage_alerts'],
            UserRole.ANALYST.value: ['create_analysis', 'view_advanced_data', 'export_data'],
            UserRole.VIEWER.value: ['view_basic_data'],
            UserRole.API_USER.value: ['api_access', 'view_basic_data'],
            UserRole.COMPLIANCE.value: ['view_compliance', 'manage_compliance', 'view_audit'],
        }

        base_permissions = role_permissions.get(self.role, [])
        custom_permissions = self.permissions or []

        return permission in base_permissions or permission in custom_permissions

class Subscription(Base):
    """組織の課金・サブスクリプション情報"""
    __tablename__ = 'subscriptions'

    # Primary Key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    organization_id = Column(UUID(as_uuid=True), ForeignKey('organizations.id'), nullable=False)

    # Subscription Details
    plan_type = Column(String(20), nullable=False)
    status = Column(String(20), nullable=False, default=SubscriptionStatus.ACTIVE.value)

    # Billing
    monthly_price = Column(Float)  # USD
    currency = Column(String(3), default='USD')
    billing_cycle = Column(String(10), default='monthly')  # monthly, yearly

    # Period
    start_date = Column(DateTime(timezone=True), nullable=False)
    end_date = Column(DateTime(timezone=True))
    next_billing_date = Column(DateTime(timezone=True))

    # External Integration
    stripe_subscription_id = Column(String(100))
    stripe_customer_id = Column(String(100))

    # Usage Tracking
    current_period_api_calls = Column(Integer, default=0)
    current_period_predictions = Column(Integer, default=0)

    # Metadata
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    cancelled_at = Column(DateTime(timezone=True))
    cancellation_reason = Column(Text)

    # Relationships
    organization = relationship("Organization", back_populates="subscriptions")

    __table_args__ = (
        Index('idx_subscription_org_status', 'organization_id', 'status'),
        Index('idx_subscription_billing_date', 'next_billing_date'),
        CheckConstraint("status IN ('active', 'expired', 'cancelled', 'pending')", name='chk_subscription_status'),
    )

# Multi-tenant Data Models

class TenantStockPrice(Base):
    """組織別株価データ（データ分離）"""
    __tablename__ = 'tenant_stock_prices'

    # Primary Key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    organization_id = Column(UUID(as_uuid=True), ForeignKey('organizations.id'), nullable=False, index=True)

    # Stock Data
    symbol = Column(String(20), nullable=False, index=True)
    date = Column(DateTime(timezone=True), nullable=False, index=True)

    # Price Data
    open_price = Column(Float)
    high_price = Column(Float)
    low_price = Column(Float)
    close_price = Column(Float, nullable=False)
    adjusted_close = Column(Float)
    volume = Column(Integer)

    # Market Data
    market_cap = Column(Float)
    pe_ratio = Column(Float)
    dividend_yield = Column(Float)

    # Data Source
    data_source = Column(String(50), default='yahoo')
    data_quality_score = Column(Float, default=1.0)

    # Metadata
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    __table_args__ = (
        Index('idx_tenant_price_org_symbol_date', 'organization_id', 'symbol', 'date'),
        Index('idx_tenant_price_date', 'date'),
        UniqueConstraint('organization_id', 'symbol', 'date', name='uq_org_symbol_date'),
    )

class TenantStockPrediction(Base):
    """組織別予測データ（データ分離）"""
    __tablename__ = 'tenant_stock_predictions'

    # Primary Key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    organization_id = Column(UUID(as_uuid=True), ForeignKey('organizations.id'), nullable=False, index=True)

    # Prediction Details
    symbol = Column(String(20), nullable=False, index=True)
    prediction_date = Column(DateTime(timezone=True), nullable=False, index=True)
    target_date = Column(DateTime(timezone=True), nullable=False)

    # Prediction Data
    predicted_price = Column(Float, nullable=False)
    confidence_score = Column(Float, nullable=False)
    model_version = Column(String(50), nullable=False)

    # AI Analysis
    factors = Column(JSONB)  # AI decision factors
    technical_indicators = Column(JSONB)
    sentiment_score = Column(Float)

    # Performance Tracking
    actual_price = Column(Float)  # Filled when target_date is reached
    accuracy_score = Column(Float)

    # Custom Model Settings (per organization)
    model_parameters = Column(JSONB)
    custom_weights = Column(JSONB)

    # Metadata
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    __table_args__ = (
        Index('idx_tenant_pred_org_symbol_date', 'organization_id', 'symbol', 'prediction_date'),
        Index('idx_tenant_pred_target_date', 'target_date'),
        Index('idx_tenant_pred_confidence', 'confidence_score'),
    )

class TenantWatchlist(Base):
    """組織別ウォッチリスト"""
    __tablename__ = 'tenant_watchlists'

    # Primary Key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    organization_id = Column(UUID(as_uuid=True), ForeignKey('organizations.id'), nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id'), nullable=False)

    # Watchlist Details
    name = Column(String(200), nullable=False)
    description = Column(Text)
    symbols = Column(JSONB, nullable=False)  # Array of symbols

    # Settings
    is_public = Column(Boolean, default=False)  # Share within organization
    alert_enabled = Column(Boolean, default=True)
    alert_threshold = Column(Float, default=0.05)  # 5% change

    # Metadata
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    __table_args__ = (
        Index('idx_watchlist_org_user', 'organization_id', 'user_id'),
        Index('idx_watchlist_public', 'is_public'),
    )

class TenantAlert(Base):
    """組織別アラート設定"""
    __tablename__ = 'tenant_alerts'

    # Primary Key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    organization_id = Column(UUID(as_uuid=True), ForeignKey('organizations.id'), nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id'), nullable=False)

    # Alert Configuration
    name = Column(String(200), nullable=False)
    symbol = Column(String(20), nullable=False, index=True)
    alert_type = Column(String(50), nullable=False)  # price_threshold, volume_spike, etc.

    # Conditions (JSON configuration)
    conditions = Column(JSONB, nullable=False)

    # Notification Settings
    notification_channels = Column(JSONB)  # email, slack, webhook, etc.
    notification_frequency = Column(String(20), default='immediate')

    # Status
    is_active = Column(Boolean, default=True, index=True)
    last_triggered_at = Column(DateTime(timezone=True))
    trigger_count = Column(Integer, default=0)

    # Metadata
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    __table_args__ = (
        Index('idx_alert_org_user_active', 'organization_id', 'user_id', 'is_active'),
        Index('idx_alert_symbol_active', 'symbol', 'is_active'),
    )

# System Models

class UserSession(Base):
    """ユーザーセッション管理"""
    __tablename__ = 'user_sessions'

    # Primary Key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id'), nullable=False)

    # Session Data
    session_token = Column(String(100), nullable=False, unique=True, index=True)
    ip_address = Column(String(45))  # Support IPv6
    user_agent = Column(Text)

    # Session Metadata
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    last_activity_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    expires_at = Column(DateTime(timezone=True), nullable=False)

    # Status
    is_active = Column(Boolean, default=True, index=True)

    # Relationships
    user = relationship("User", back_populates="user_sessions")

    __table_args__ = (
        Index('idx_session_user_active', 'user_id', 'is_active'),
        Index('idx_session_expires', 'expires_at'),
    )

class AuditLog(Base):
    """監査ログ（組織別）"""
    __tablename__ = 'audit_logs'

    # Primary Key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    organization_id = Column(UUID(as_uuid=True), ForeignKey('organizations.id'), nullable=False, index=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id'), nullable=True, index=True)

    # Event Details
    event_type = Column(String(100), nullable=False, index=True)
    event_category = Column(String(50), nullable=False, index=True)  # auth, data, system, compliance
    resource_type = Column(String(100))
    resource_id = Column(String(100))

    # Event Data
    description = Column(Text, nullable=False)
    details = Column(JSONB)  # Additional event details

    # Request Context
    ip_address = Column(String(45))
    user_agent = Column(Text)
    request_id = Column(String(100), index=True)

    # Risk Assessment
    risk_level = Column(String(20), default='low')  # low, medium, high, critical

    # Metadata
    timestamp = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), index=True)

    # Relationships
    organization = relationship("Organization", back_populates="audit_logs")
    user = relationship("User", back_populates="audit_logs")

    __table_args__ = (
        Index('idx_audit_org_time', 'organization_id', 'timestamp'),
        Index('idx_audit_event_type', 'event_type'),
        Index('idx_audit_risk_level', 'risk_level'),
    )

class SystemConfiguration(Base):
    """システム設定（マルチテナント対応）"""
    __tablename__ = 'system_configurations'

    # Primary Key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    organization_id = Column(UUID(as_uuid=True), ForeignKey('organizations.id'), nullable=False, index=True)

    # Configuration
    config_key = Column(String(200), nullable=False, index=True)
    config_value = Column(JSONB)
    config_type = Column(String(50), nullable=False)  # feature_flags, limits, integrations, etc.

    # Metadata
    description = Column(Text)
    is_encrypted = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    created_by = Column(UUID(as_uuid=True), ForeignKey('users.id'))

    __table_args__ = (
        UniqueConstraint('organization_id', 'config_key', name='uq_org_config_key'),
        Index('idx_config_type', 'config_type'),
    )

# Database utility functions

def get_tenant_filter(organization_id: uuid.UUID):
    """Get SQLAlchemy filter for tenant isolation"""
    def tenant_filter(query):
        return query.filter_by(organization_id=organization_id)
    return tenant_filter

class TenantQueryMixin:
    """Mixin to add tenant-aware query methods"""

    @classmethod
    def for_organization(cls, session: Session, organization_id: uuid.UUID):
        """Get query filtered by organization"""
        return session.query(cls).filter(cls.organization_id == organization_id)

    @classmethod
    def create_for_organization(cls, session: Session, organization_id: uuid.UUID, **kwargs):
        """Create record for specific organization"""
        instance = cls(organization_id=organization_id, **kwargs)
        session.add(instance)
        return instance

# Add mixin to relevant models
TenantStockPrice.__bases__ += (TenantQueryMixin,)
TenantStockPrediction.__bases__ += (TenantQueryMixin,)
TenantWatchlist.__bases__ += (TenantQueryMixin,)
TenantAlert.__bases__ += (TenantQueryMixin,)