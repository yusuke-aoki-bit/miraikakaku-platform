"""
Multi-tenant Organization Manager
Phase 3.2 - マルチテナント・エンタープライズ統合

Complete organization and tenant management system
"""

import uuid
import logging
from datetime import datetime, timezone, timedelta
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
import secrets
import hashlib
import json

from sqlalchemy import create_engine, text, and_, or_, func
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.exc import IntegrityError

from database.multi_tenant_models import (
    Base, Organization, User, Subscription, TenantStockPrice,
    TenantStockPrediction, TenantWatchlist, TenantAlert,
    UserSession, AuditLog, SystemConfiguration,
    PlanType, OrganizationStatus, UserRole, SubscriptionStatus
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class OrganizationPlan:
    """Organization plan configuration"""
    name: str
    max_users: int
    max_api_calls_per_month: int
    max_predictions_per_day: int
    max_symbols_tracked: int
    features: List[str]
    monthly_price: float

# Plan configurations
PLAN_CONFIGURATIONS = {
    PlanType.BASIC: OrganizationPlan(
        name="Basic",
        max_users=5,
        max_api_calls_per_month=10000,
        max_predictions_per_day=100,
        max_symbols_tracked=10,
        features=["basic_predictions", "email_alerts"],
        monthly_price=99.0
    ),
    PlanType.PROFESSIONAL: OrganizationPlan(
        name="Professional",
        max_users=25,
        max_api_calls_per_month=100000,
        max_predictions_per_day=1000,
        max_symbols_tracked=100,
        features=[
            "basic_predictions", "advanced_predictions", "email_alerts",
            "slack_alerts", "api_access", "custom_models", "export_data",
            "realtime_streaming"
        ],
        monthly_price=499.0
    ),
    PlanType.ENTERPRISE: OrganizationPlan(
        name="Enterprise",
        max_users=500,
        max_api_calls_per_month=1000000,
        max_predictions_per_day=10000,
        max_symbols_tracked=1000,
        features=[
            "basic_predictions", "advanced_predictions", "custom_models",
            "email_alerts", "slack_alerts", "webhook_alerts", "api_access",
            "export_data", "realtime_streaming", "advanced_analytics",
            "compliance_reports", "audit_logs", "sso", "priority_support",
            "custom_integrations", "white_label", "dedicated_support"
        ],
        monthly_price=2499.0
    ),
    PlanType.CUSTOM: OrganizationPlan(
        name="Custom",
        max_users=10000,
        max_api_calls_per_month=10000000,
        max_predictions_per_day=100000,
        max_symbols_tracked=10000,
        features=["all_features"],
        monthly_price=0.0  # Custom pricing
    )
}

class MultiTenantManager:
    """マルチテナント組織管理システム"""

    def __init__(self, database_url: str):
        self.engine = create_engine(
            database_url,
            pool_size=20,
            max_overflow=30,
            pool_pre_ping=True,
            pool_recycle=3600
        )
        self.SessionLocal = sessionmaker(bind=self.engine)

        # Initialize database
        self._create_tables()

    def _create_tables(self):
        """Create all tables"""
        try:
            Base.metadata.create_all(bind=self.engine)
            logger.info("✅ Multi-tenant database tables created/updated")
        except Exception as e:
            logger.error(f"❌ Failed to create database tables: {e}")
            raise

    def get_session(self) -> Session:
        """Get database session"""
        return self.SessionLocal()

    # Organization Management

    def create_organization(
        self,
        name: str,
        display_name: str,
        primary_contact_email: str,
        plan_type: PlanType = PlanType.BASIC,
        trial_days: int = 14,
        **kwargs
    ) -> Organization:
        """Create new organization"""

        with self.get_session() as session:
            try:
                # Generate unique slug
                base_slug = name.lower().replace(' ', '-').replace('_', '-')
                base_slug = ''.join(c for c in base_slug if c.isalnum() or c == '-')

                slug = base_slug
                counter = 1
                while session.query(Organization).filter_by(slug=slug).first():
                    slug = f"{base_slug}-{counter}"
                    counter += 1

                # Get plan configuration
                plan_config = PLAN_CONFIGURATIONS[plan_type]

                # Create organization
                org = Organization(
                    name=name,
                    display_name=display_name,
                    slug=slug,
                    primary_contact_email=primary_contact_email,
                    plan_type=plan_type.value,
                    status=OrganizationStatus.TRIAL.value,
                    max_users=plan_config.max_users,
                    max_api_calls_per_month=plan_config.max_api_calls_per_month,
                    max_predictions_per_day=plan_config.max_predictions_per_day,
                    max_symbols_tracked=plan_config.max_symbols_tracked,
                    enabled_features=plan_config.features,
                    trial_end_date=datetime.now(timezone.utc) + timedelta(days=trial_days),
                    **kwargs
                )

                session.add(org)
                session.commit()
                session.refresh(org)

                # Create initial subscription
                self._create_subscription(session, org, plan_type, trial=True)

                # Create audit log
                self._log_audit_event(
                    session, org.id, None, "organization_created",
                    f"Organization '{name}' created with {plan_type.value} plan"
                )

                logger.info(f"✅ Organization created: {name} (ID: {org.id})")
                return org

            except IntegrityError as e:
                session.rollback()
                logger.error(f"❌ Failed to create organization: {e}")
                raise ValueError(f"Organization with email {primary_contact_email} already exists")

    def get_organization(self, org_id: uuid.UUID) -> Optional[Organization]:
        """Get organization by ID"""
        with self.get_session() as session:
            return session.query(Organization).filter_by(id=org_id).first()

    def get_organization_by_slug(self, slug: str) -> Optional[Organization]:
        """Get organization by slug"""
        with self.get_session() as session:
            return session.query(Organization).filter_by(slug=slug).first()

    def update_organization(self, org_id: uuid.UUID, **updates) -> Organization:
        """Update organization"""
        with self.get_session() as session:
            org = session.query(Organization).filter_by(id=org_id).first()
            if not org:
                raise ValueError(f"Organization {org_id} not found")

            for key, value in updates.items():
                if hasattr(org, key):
                    setattr(org, key, value)

            org.updated_at = datetime.now(timezone.utc)
            session.commit()
            session.refresh(org)

            self._log_audit_event(
                session, org_id, None, "organization_updated",
                f"Organization updated: {list(updates.keys())}"
            )

            return org

    def upgrade_organization_plan(self, org_id: uuid.UUID, new_plan: PlanType) -> Organization:
        """Upgrade organization plan"""
        with self.get_session() as session:
            org = session.query(Organization).filter_by(id=org_id).first()
            if not org:
                raise ValueError(f"Organization {org_id} not found")

            old_plan = org.plan_type
            plan_config = PLAN_CONFIGURATIONS[new_plan]

            # Update organization limits
            org.plan_type = new_plan.value
            org.max_users = plan_config.max_users
            org.max_api_calls_per_month = plan_config.max_api_calls_per_month
            org.max_predictions_per_day = plan_config.max_predictions_per_day
            org.max_symbols_tracked = plan_config.max_symbols_tracked
            org.enabled_features = plan_config.features
            org.status = OrganizationStatus.ACTIVE.value
            org.updated_at = datetime.now(timezone.utc)

            # Create new subscription
            self._create_subscription(session, org, new_plan, trial=False)

            session.commit()
            session.refresh(org)

            self._log_audit_event(
                session, org_id, None, "plan_upgraded",
                f"Plan upgraded from {old_plan} to {new_plan.value}"
            )

            logger.info(f"✅ Organization {org.name} upgraded to {new_plan.value}")
            return org

    def _create_subscription(self, session: Session, org: Organization, plan_type: PlanType, trial: bool = False):
        """Create subscription for organization"""
        plan_config = PLAN_CONFIGURATIONS[plan_type]

        subscription = Subscription(
            organization_id=org.id,
            plan_type=plan_type.value,
            status=SubscriptionStatus.ACTIVE.value if not trial else SubscriptionStatus.PENDING.value,
            monthly_price=0.0 if trial else plan_config.monthly_price,
            start_date=datetime.now(timezone.utc),
            end_date=org.trial_end_date if trial else None,
            next_billing_date=org.trial_end_date if trial else datetime.now(timezone.utc) + timedelta(days=30)
        )

        session.add(subscription)

    # User Management

    def create_user(
        self,
        organization_id: uuid.UUID,
        email: str,
        username: str,
        password: str,
        role: UserRole = UserRole.VIEWER,
        **kwargs
    ) -> User:
        """Create new user in organization"""

        with self.get_session() as session:
            try:
                # Check organization exists and has capacity
                org = session.query(Organization).filter_by(id=organization_id).first()
                if not org:
                    raise ValueError("Organization not found")

                user_count = session.query(User).filter_by(
                    organization_id=organization_id,
                    is_active=True
                ).count()

                if user_count >= org.max_users:
                    raise ValueError(f"Organization has reached maximum user limit ({org.max_users})")

                # Hash password
                password_hash = self._hash_password(password)

                # Generate API key if needed
                api_key = None
                if role == UserRole.API_USER:
                    api_key = self._generate_api_key()

                # Create user
                user = User(
                    organization_id=organization_id,
                    email=email,
                    username=username,
                    password_hash=password_hash,
                    role=role.value,
                    api_key=api_key,
                    **kwargs
                )

                session.add(user)
                session.commit()
                session.refresh(user)

                self._log_audit_event(
                    session, organization_id, user.id, "user_created",
                    f"User '{username}' created with role {role.value}"
                )

                logger.info(f"✅ User created: {username} in org {org.name}")
                return user

            except IntegrityError as e:
                session.rollback()
                if 'email' in str(e):
                    raise ValueError(f"User with email {email} already exists")
                elif 'username' in str(e):
                    raise ValueError(f"Username {username} already exists in organization")
                raise ValueError(f"Failed to create user: {e}")

    def authenticate_user(self, email: str, password: str) -> Optional[User]:
        """Authenticate user with email and password"""
        with self.get_session() as session:
            user = session.query(User).filter_by(email=email, is_active=True).first()

            if user and self._verify_password(password, user.password_hash):
                # Update last login
                user.last_login_at = datetime.now(timezone.utc)
                user.last_activity_at = datetime.now(timezone.utc)
                session.commit()

                self._log_audit_event(
                    session, user.organization_id, user.id, "user_login",
                    f"User '{user.username}' logged in"
                )

                return user

            return None

    def authenticate_api_key(self, api_key: str) -> Optional[User]:
        """Authenticate user with API key"""
        with self.get_session() as session:
            user = session.query(User).filter_by(
                api_key=api_key,
                is_active=True
            ).first()

            if user:
                # Check if API key is expired
                if user.api_key_expires_at and user.api_key_expires_at < datetime.now(timezone.utc):
                    return None

                # Update last activity
                user.last_activity_at = datetime.now(timezone.utc)
                session.commit()

                return user

            return None

    def get_organization_users(self, organization_id: uuid.UUID, active_only: bool = True) -> List[User]:
        """Get all users in organization"""
        with self.get_session() as session:
            query = session.query(User).filter_by(organization_id=organization_id)
            if active_only:
                query = query.filter_by(is_active=True)
            return query.all()

    # Data Access Control

    def get_tenant_data_access(self, organization_id: uuid.UUID, user_id: uuid.UUID) -> Dict[str, Any]:
        """Get data access configuration for tenant user"""
        with self.get_session() as session:
            user = session.query(User).filter_by(id=user_id, organization_id=organization_id).first()
            org = session.query(Organization).filter_by(id=organization_id).first()

            if not user or not org:
                return {"access": False, "reason": "User or organization not found"}

            if not user.is_active:
                return {"access": False, "reason": "User is inactive"}

            if org.status != OrganizationStatus.ACTIVE.value:
                return {"access": False, "reason": f"Organization status is {org.status}"}

            # Check subscription
            active_subscription = session.query(Subscription).filter_by(
                organization_id=organization_id,
                status=SubscriptionStatus.ACTIVE.value
            ).first()

            if not active_subscription:
                return {"access": False, "reason": "No active subscription"}

            return {
                "access": True,
                "user_role": user.role,
                "organization_plan": org.plan_type,
                "enabled_features": org.enabled_features,
                "limits": {
                    "max_api_calls_per_month": org.max_api_calls_per_month,
                    "max_predictions_per_day": org.max_predictions_per_day,
                    "max_symbols_tracked": org.max_symbols_tracked
                },
                "permissions": user.permissions or []
            }

    def check_feature_access(self, organization_id: uuid.UUID, feature: str) -> bool:
        """Check if organization has access to specific feature"""
        with self.get_session() as session:
            org = session.query(Organization).filter_by(id=organization_id).first()
            if not org:
                return False

            return org.has_feature(feature)

    def check_usage_limits(self, organization_id: uuid.UUID) -> Dict[str, Any]:
        """Check current usage against limits"""
        with self.get_session() as session:
            org = session.query(Organization).filter_by(id=organization_id).first()
            if not org:
                return {"error": "Organization not found"}

            # Get current month usage
            start_of_month = datetime.now(timezone.utc).replace(day=1, hour=0, minute=0, second=0, microsecond=0)

            # API calls usage (would need to track in separate table)
            subscription = session.query(Subscription).filter_by(
                organization_id=organization_id,
                status=SubscriptionStatus.ACTIVE.value
            ).first()

            api_calls_used = subscription.current_period_api_calls if subscription else 0
            predictions_used = subscription.current_period_predictions if subscription else 0

            # User count
            active_users = session.query(User).filter_by(
                organization_id=organization_id,
                is_active=True
            ).count()

            # Symbol tracking count
            watchlists = session.query(TenantWatchlist).filter_by(
                organization_id=organization_id
            ).all()
            tracked_symbols = set()
            for watchlist in watchlists:
                tracked_symbols.update(watchlist.symbols or [])

            return {
                "api_calls": {
                    "used": api_calls_used,
                    "limit": org.max_api_calls_per_month,
                    "percentage": (api_calls_used / org.max_api_calls_per_month) * 100 if org.max_api_calls_per_month > 0 else 0
                },
                "predictions": {
                    "used": predictions_used,
                    "limit": org.max_predictions_per_day,
                    "percentage": (predictions_used / org.max_predictions_per_day) * 100 if org.max_predictions_per_day > 0 else 0
                },
                "users": {
                    "used": active_users,
                    "limit": org.max_users,
                    "percentage": (active_users / org.max_users) * 100 if org.max_users > 0 else 0
                },
                "symbols": {
                    "used": len(tracked_symbols),
                    "limit": org.max_symbols_tracked,
                    "percentage": (len(tracked_symbols) / org.max_symbols_tracked) * 100 if org.max_symbols_tracked > 0 else 0
                }
            }

    # Tenant Data Management

    def get_tenant_stock_data(
        self,
        organization_id: uuid.UUID,
        symbol: str,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> List[TenantStockPrice]:
        """Get stock price data for tenant"""
        with self.get_session() as session:
            query = TenantStockPrice.for_organization(session, organization_id).filter_by(symbol=symbol)

            if start_date:
                query = query.filter(TenantStockPrice.date >= start_date)
            if end_date:
                query = query.filter(TenantStockPrice.date <= end_date)

            return query.order_by(TenantStockPrice.date.desc()).all()

    def get_tenant_predictions(
        self,
        organization_id: uuid.UUID,
        symbol: str,
        limit: int = 100
    ) -> List[TenantStockPrediction]:
        """Get predictions for tenant"""
        with self.get_session() as session:
            return (TenantStockPrediction.for_organization(session, organization_id)
                   .filter_by(symbol=symbol)
                   .order_by(TenantStockPrediction.prediction_date.desc())
                   .limit(limit)
                   .all())

    def create_tenant_watchlist(
        self,
        organization_id: uuid.UUID,
        user_id: uuid.UUID,
        name: str,
        symbols: List[str],
        **kwargs
    ) -> TenantWatchlist:
        """Create watchlist for tenant user"""
        with self.get_session() as session:
            # Check symbol limit
            org = session.query(Organization).filter_by(id=organization_id).first()
            if len(symbols) > org.max_symbols_tracked:
                raise ValueError(f"Symbol limit exceeded: {len(symbols)} > {org.max_symbols_tracked}")

            watchlist = TenantWatchlist(
                organization_id=organization_id,
                user_id=user_id,
                name=name,
                symbols=symbols,
                **kwargs
            )

            session.add(watchlist)
            session.commit()
            session.refresh(watchlist)

            self._log_audit_event(
                session, organization_id, user_id, "watchlist_created",
                f"Watchlist '{name}' created with {len(symbols)} symbols"
            )

            return watchlist

    # Audit and Logging

    def _log_audit_event(
        self,
        session: Session,
        organization_id: uuid.UUID,
        user_id: Optional[uuid.UUID],
        event_type: str,
        description: str,
        **kwargs
    ):
        """Log audit event"""
        audit_log = AuditLog(
            organization_id=organization_id,
            user_id=user_id,
            event_type=event_type,
            event_category=kwargs.get('event_category', 'system'),
            resource_type=kwargs.get('resource_type'),
            resource_id=kwargs.get('resource_id'),
            description=description,
            details=kwargs.get('details'),
            ip_address=kwargs.get('ip_address'),
            user_agent=kwargs.get('user_agent'),
            request_id=kwargs.get('request_id'),
            risk_level=kwargs.get('risk_level', 'low')
        )

        session.add(audit_log)

    def get_audit_logs(
        self,
        organization_id: uuid.UUID,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        event_types: Optional[List[str]] = None,
        limit: int = 1000
    ) -> List[AuditLog]:
        """Get audit logs for organization"""
        with self.get_session() as session:
            query = session.query(AuditLog).filter_by(organization_id=organization_id)

            if start_date:
                query = query.filter(AuditLog.timestamp >= start_date)
            if end_date:
                query = query.filter(AuditLog.timestamp <= end_date)
            if event_types:
                query = query.filter(AuditLog.event_type.in_(event_types))

            return query.order_by(AuditLog.timestamp.desc()).limit(limit).all()

    # Utility Methods

    def _hash_password(self, password: str) -> str:
        """Hash password using SHA-256 with salt"""
        salt = secrets.token_hex(32)
        password_hash = hashlib.pbkdf2_hmac('sha256', password.encode(), salt.encode(), 100000)
        return f"{salt}:{password_hash.hex()}"

    def _verify_password(self, password: str, stored_hash: str) -> bool:
        """Verify password against stored hash"""
        try:
            salt, hash_part = stored_hash.split(':', 1)
            password_hash = hashlib.pbkdf2_hmac('sha256', password.encode(), salt.encode(), 100000)
            return hash_part == password_hash.hex()
        except (ValueError, AttributeError):
            return False

    def _generate_api_key(self) -> str:
        """Generate secure API key"""
        return f"mk_{secrets.token_urlsafe(32)}"

    # Dashboard and Analytics

    def get_organization_dashboard_data(self, organization_id: uuid.UUID) -> Dict[str, Any]:
        """Get comprehensive dashboard data for organization"""
        with self.get_session() as session:
            org = session.query(Organization).filter_by(id=organization_id).first()
            if not org:
                return {"error": "Organization not found"}

            # Basic org info
            org_data = {
                "id": str(org.id),
                "name": org.name,
                "display_name": org.display_name,
                "slug": org.slug,
                "plan_type": org.plan_type,
                "status": org.status,
                "created_at": org.created_at.isoformat(),
                "enabled_features": org.enabled_features
            }

            # User statistics
            users = session.query(User).filter_by(organization_id=organization_id)
            user_stats = {
                "total": users.count(),
                "active": users.filter_by(is_active=True).count(),
                "by_role": {}
            }

            for role in UserRole:
                user_stats["by_role"][role.value] = users.filter_by(role=role.value, is_active=True).count()

            # Usage statistics
            usage_stats = self.check_usage_limits(organization_id)

            # Recent activity
            recent_logs = self.get_audit_logs(
                organization_id,
                start_date=datetime.now(timezone.utc) - timedelta(days=7),
                limit=10
            )

            activity_summary = {}
            for log in recent_logs:
                event_type = log.event_type
                activity_summary[event_type] = activity_summary.get(event_type, 0) + 1

            return {
                "organization": org_data,
                "users": user_stats,
                "usage": usage_stats,
                "recent_activity": activity_summary,
                "audit_logs_count": len(recent_logs)
            }

# Global instance
multi_tenant_manager: Optional[MultiTenantManager] = None

def get_tenant_manager() -> MultiTenantManager:
    """Get global tenant manager instance"""
    global multi_tenant_manager
    if multi_tenant_manager is None:
        database_url = "postgresql://username:password@localhost:5432/miraikakaku"
        multi_tenant_manager = MultiTenantManager(database_url)
    return multi_tenant_manager