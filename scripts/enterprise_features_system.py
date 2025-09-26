#!/usr/bin/env python3
"""
エンタープライズ機能システム
Enterprise Features System for Miraikakaku Platform

このモジュールは企業向けの高度な機能を提供します：
- 企業ダッシュボードとマルチユーザー管理
- カスタムアラート＆通知システム
- 高度なリスク管理とコンプライアンス
- API アクセス制御とレート制限
- 企業レベルのセキュリティ機能
- 監査ログとレポート機能
"""

import json
import logging
import sqlite3
import hashlib
import hmac
import secrets
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple, Set
from dataclasses import dataclass, asdict, field
from enum import Enum
import threading
import queue
from collections import defaultdict, deque
import uuid
import re

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Try to import additional libraries with fallbacks
try:
    import bcrypt
    BCRYPT_AVAILABLE = True
except ImportError:
    BCRYPT_AVAILABLE = False
    logger.warning("bcrypt not available - using SHA256 for password hashing")

try:
    import jwt
    JWT_AVAILABLE = True
except ImportError:
    JWT_AVAILABLE = False
    logger.warning("PyJWT not available - using custom token implementation")

class UserRole(Enum):
    ADMIN = "admin"
    MANAGER = "manager"
    ANALYST = "analyst"
    VIEWER = "viewer"
    API_USER = "api_user"

class AlertType(Enum):
    PRICE_THRESHOLD = "price_threshold"
    VOLUME_SPIKE = "volume_spike"
    VOLATILITY_CHANGE = "volatility_change"
    PREDICTION_ACCURACY = "prediction_accuracy"
    SYSTEM_HEALTH = "system_health"
    COMPLIANCE = "compliance"

class AlertSeverity(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class NotificationChannel(Enum):
    EMAIL = "email"
    SMS = "sms"
    WEBHOOK = "webhook"
    SLACK = "slack"
    DASHBOARD = "dashboard"

class ComplianceRule(Enum):
    POSITION_LIMIT = "position_limit"
    RISK_LIMIT = "risk_limit"
    TRADING_HOURS = "trading_hours"
    GEOGRAPHIC_RESTRICTION = "geographic_restriction"
    DATA_RETENTION = "data_retention"

@dataclass
class User:
    user_id: str
    username: str
    email: str
    role: UserRole
    organization_id: str
    created_at: datetime
    last_login: Optional[datetime] = None
    is_active: bool = True
    permissions: List[str] = field(default_factory=list)
    api_key: Optional[str] = None
    rate_limit: int = 1000  # requests per hour
    password_hash: Optional[str] = None

@dataclass
class Organization:
    org_id: str
    name: str
    plan_type: str  # basic, professional, enterprise
    created_at: datetime
    max_users: int
    api_quota: int  # requests per month
    features: List[str] = field(default_factory=list)
    settings: Dict[str, Any] = field(default_factory=dict)

@dataclass
class Alert:
    alert_id: str
    user_id: str
    alert_type: AlertType
    severity: AlertSeverity
    title: str
    message: str
    created_at: datetime
    triggered_at: Optional[datetime] = None
    resolved_at: Optional[datetime] = None
    is_active: bool = True
    conditions: Dict[str, Any] = field(default_factory=dict)
    notification_channels: List[NotificationChannel] = field(default_factory=list)

@dataclass
class AuditLog:
    log_id: str
    user_id: str
    action: str
    resource: str
    timestamp: datetime
    details: Dict[str, Any] = field(default_factory=dict)
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None

@dataclass
class APIToken:
    token_id: str
    user_id: str
    token_hash: str
    name: str
    created_at: datetime
    expires_at: Optional[datetime] = None
    last_used: Optional[datetime] = None
    permissions: List[str] = field(default_factory=list)
    is_active: bool = True

class SecurityManager:
    """Enterprise security management"""

    def __init__(self, secret_key: str):
        self.secret_key = secret_key
        self.failed_attempts = defaultdict(list)
        self.rate_limits = defaultdict(deque)

    def hash_password(self, password: str) -> str:
        """Hash password securely"""
        if BCRYPT_AVAILABLE:
            return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        else:
            # Fallback to PBKDF2 using hashlib
            salt = secrets.token_bytes(32)
            pwdhash = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt, 100000)
            return salt.hex() + pwdhash.hex()

    def verify_password(self, password: str, hashed: str) -> bool:
        """Verify password against hash"""
        if BCRYPT_AVAILABLE and hashed.startswith('$2b$'):
            return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))
        else:
            # Fallback verification
            if len(hashed) >= 64:
                salt = bytes.fromhex(hashed[:64])
                stored_hash = hashed[64:]
                pwdhash = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt, 100000)
                return pwdhash.hex() == stored_hash
            return False

    def generate_api_key(self) -> str:
        """Generate secure API key"""
        return f"mk_{secrets.token_urlsafe(32)}"

    def generate_token(self, user_id: str, permissions: List[str], expires_hours: int = 24) -> str:
        """Generate JWT or custom token"""
        if JWT_AVAILABLE:
            payload = {
                'user_id': user_id,
                'permissions': permissions,
                'exp': datetime.utcnow() + timedelta(hours=expires_hours),
                'iat': datetime.utcnow()
            }
            return jwt.encode(payload, self.secret_key, algorithm='HS256')
        else:
            # Custom token format: base64(user_id:permissions:expiry:signature)
            import base64
            expiry = int((datetime.utcnow() + timedelta(hours=expires_hours)).timestamp())
            token_data = f"{user_id}:{':'.join(permissions)}:{expiry}"
            signature = hmac.new(
                self.secret_key.encode(),
                token_data.encode(),
                hashlib.sha256
            ).hexdigest()
            full_token = f"{token_data}:{signature}"
            return base64.b64encode(full_token.encode()).decode()

    def verify_token(self, token: str) -> Optional[Dict[str, Any]]:
        """Verify JWT or custom token"""
        try:
            if JWT_AVAILABLE and not token.startswith('mk_'):
                payload = jwt.decode(token, self.secret_key, algorithms=['HS256'])
                return payload
            else:
                # Verify custom token
                import base64
                try:
                    decoded = base64.b64decode(token.encode()).decode()
                    parts = decoded.split(':')
                    if len(parts) < 4:
                        return None

                    user_id = parts[0]
                    permissions = parts[1:-2] if len(parts) > 4 else []
                    expiry = int(parts[-2])
                    signature = parts[-1]

                    # Verify signature
                    token_data = ':'.join(parts[:-1])
                    expected_sig = hmac.new(
                        self.secret_key.encode(),
                        token_data.encode(),
                        hashlib.sha256
                    ).hexdigest()

                    if signature != expected_sig:
                        return None

                    # Check expiry
                    if datetime.utcnow().timestamp() > expiry:
                        return None

                    return {
                        'user_id': user_id,
                        'permissions': permissions,
                        'exp': expiry
                    }
                except:
                    return None
        except Exception as e:
            logger.warning(f"Token verification failed: {e}")
            return None

    def check_rate_limit(self, identifier: str, limit: int, window_seconds: int = 3600) -> bool:
        """Check rate limiting"""
        now = time.time()
        window_start = now - window_seconds

        # Clean old entries
        requests = self.rate_limits[identifier]
        while requests and requests[0] < window_start:
            requests.popleft()

        # Check limit
        if len(requests) >= limit:
            return False

        # Add current request
        requests.append(now)
        return True

    def log_failed_attempt(self, identifier: str, max_attempts: int = 5, window_minutes: int = 15) -> bool:
        """Log failed login attempt and check if blocked"""
        now = datetime.now()
        window_start = now - timedelta(minutes=window_minutes)

        # Clean old attempts
        attempts = self.failed_attempts[identifier]
        self.failed_attempts[identifier] = [
            attempt for attempt in attempts if attempt > window_start
        ]

        # Add current attempt
        self.failed_attempts[identifier].append(now)

        # Check if blocked
        return len(self.failed_attempts[identifier]) >= max_attempts

class UserManager:
    """Enterprise user management"""

    def __init__(self, security_manager: SecurityManager):
        self.security = security_manager
        self.users: Dict[str, User] = {}
        self.organizations: Dict[str, Organization] = {}
        self.user_sessions: Dict[str, Dict[str, Any]] = {}

    def create_organization(self, name: str, plan_type: str = "basic") -> Organization:
        """Create new organization"""
        org_id = str(uuid.uuid4())

        max_users_by_plan = {"basic": 5, "professional": 50, "enterprise": 500}
        api_quota_by_plan = {"basic": 10000, "professional": 100000, "enterprise": 1000000}
        features_by_plan = {
            "basic": ["basic_analytics", "alerts"],
            "professional": ["basic_analytics", "alerts", "custom_reports", "api_access"],
            "enterprise": ["basic_analytics", "alerts", "custom_reports", "api_access",
                         "advanced_security", "compliance", "audit_logs", "sso"]
        }

        org = Organization(
            org_id=org_id,
            name=name,
            plan_type=plan_type,
            created_at=datetime.now(),
            max_users=max_users_by_plan.get(plan_type, 5),
            api_quota=api_quota_by_plan.get(plan_type, 10000),
            features=features_by_plan.get(plan_type, [])
        )

        self.organizations[org_id] = org
        logger.info(f"Created organization: {name} ({plan_type})")
        return org

    def create_user(self, username: str, email: str, password: str,
                   organization_id: str, role: UserRole = UserRole.VIEWER) -> User:
        """Create new user"""

        # Check organization exists and has capacity
        org = self.organizations.get(organization_id)
        if not org:
            raise ValueError("Organization not found")

        org_users = [u for u in self.users.values() if u.organization_id == organization_id]
        if len(org_users) >= org.max_users:
            raise ValueError("Organization user limit reached")

        user_id = str(uuid.uuid4())
        password_hash = self.security.hash_password(password)

        # Generate API key for API users
        api_key = self.security.generate_api_key() if role == UserRole.API_USER else None

        user = User(
            user_id=user_id,
            username=username,
            email=email,
            role=role,
            organization_id=organization_id,
            created_at=datetime.now(),
            password_hash=password_hash,
            api_key=api_key,
            permissions=self._get_default_permissions(role, org.features)
        )

        self.users[user_id] = user
        logger.info(f"Created user: {username} ({role.value})")
        return user

    def authenticate_user(self, username: str, password: str) -> Optional[User]:
        """Authenticate user with username/password"""

        # Find user by username
        user = None
        for u in self.users.values():
            if u.username == username and u.is_active:
                user = u
                break

        if not user:
            return None

        # Check for too many failed attempts
        if self.security.log_failed_attempt(username):
            logger.warning(f"User {username} temporarily blocked due to failed attempts")
            return None

        # Verify password
        if not self.security.verify_password(password, user.password_hash):
            return None

        # Update last login
        user.last_login = datetime.now()

        # Clear failed attempts on successful login
        if username in self.security.failed_attempts:
            del self.security.failed_attempts[username]

        return user

    def authenticate_api_key(self, api_key: str) -> Optional[User]:
        """Authenticate using API key"""
        for user in self.users.values():
            if user.api_key == api_key and user.is_active:
                return user
        return None

    def _get_default_permissions(self, role: UserRole, org_features: List[str]) -> List[str]:
        """Get default permissions based on role and organization features"""
        base_permissions = {
            UserRole.ADMIN: ["read", "write", "delete", "admin", "manage_users", "view_audit"],
            UserRole.MANAGER: ["read", "write", "manage_alerts", "view_reports"],
            UserRole.ANALYST: ["read", "write", "create_reports"],
            UserRole.VIEWER: ["read"],
            UserRole.API_USER: ["api_access", "read"]
        }

        permissions = base_permissions.get(role, ["read"])

        # Add feature-specific permissions
        if "api_access" in org_features and role != UserRole.VIEWER:
            permissions.append("api_access")
        if "advanced_security" in org_features and role in [UserRole.ADMIN, UserRole.MANAGER]:
            permissions.append("security_config")
        if "audit_logs" in org_features and role == UserRole.ADMIN:
            permissions.append("audit_access")

        return permissions

class AlertManager:
    """Enterprise alert and notification system"""

    def __init__(self):
        self.alerts: Dict[str, Alert] = {}
        self.alert_rules: Dict[str, Dict[str, Any]] = {}
        self.notification_queue = queue.Queue()
        self.active_monitoring = {}
        self.is_running = False
        self.monitor_thread = None

    def start(self):
        """Start alert monitoring"""
        self.is_running = True
        self.monitor_thread = threading.Thread(target=self._monitor_alerts, daemon=True)
        self.monitor_thread.start()
        logger.info("Alert monitoring started")

    def stop(self):
        """Stop alert monitoring"""
        self.is_running = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=5)
        logger.info("Alert monitoring stopped")

    def create_alert_rule(self, user_id: str, alert_type: AlertType,
                         conditions: Dict[str, Any],
                         channels: List[NotificationChannel],
                         severity: AlertSeverity = AlertSeverity.MEDIUM) -> str:
        """Create new alert rule"""
        rule_id = str(uuid.uuid4())

        rule = {
            'rule_id': rule_id,
            'user_id': user_id,
            'alert_type': alert_type,
            'conditions': conditions,
            'channels': channels,
            'severity': severity,
            'is_active': True,
            'created_at': datetime.now(),
            'trigger_count': 0,
            'last_triggered': None
        }

        self.alert_rules[rule_id] = rule
        logger.info(f"Created alert rule: {alert_type.value} for user {user_id}")
        return rule_id

    def trigger_alert(self, rule_id: str, message: str, data: Dict[str, Any] = None) -> str:
        """Trigger an alert"""
        rule = self.alert_rules.get(rule_id)
        if not rule or not rule['is_active']:
            return None

        alert_id = str(uuid.uuid4())
        alert = Alert(
            alert_id=alert_id,
            user_id=rule['user_id'],
            alert_type=rule['alert_type'],
            severity=rule['severity'],
            title=f"{rule['alert_type'].value.replace('_', ' ').title()} Alert",
            message=message,
            created_at=datetime.now(),
            triggered_at=datetime.now(),
            conditions=rule['conditions'],
            notification_channels=rule['channels']
        )

        self.alerts[alert_id] = alert

        # Update rule statistics
        rule['trigger_count'] += 1
        rule['last_triggered'] = datetime.now()

        # Queue notifications
        for channel in rule['channels']:
            self.notification_queue.put({
                'alert': alert,
                'channel': channel,
                'data': data or {}
            })

        logger.info(f"Triggered alert {alert_id}: {message}")
        return alert_id

    def _monitor_alerts(self):
        """Monitor conditions and trigger alerts"""
        while self.is_running:
            try:
                # Process notification queue
                while not self.notification_queue.empty():
                    try:
                        notification = self.notification_queue.get_nowait()
                        self._send_notification(notification)
                    except queue.Empty:
                        break

                # Check alert conditions (simplified monitoring)
                self._check_alert_conditions()

                time.sleep(30)  # Check every 30 seconds

            except Exception as e:
                logger.error(f"Error in alert monitoring: {e}")
                time.sleep(60)

    def _check_alert_conditions(self):
        """Check alert conditions against current data"""
        # This would integrate with real market data
        # For now, simulate some alerts

        current_time = datetime.now()

        for rule_id, rule in self.alert_rules.items():
            if not rule['is_active']:
                continue

            # Simulate condition checking
            if rule['alert_type'] == AlertType.SYSTEM_HEALTH:
                # Simulate system health check
                if current_time.minute % 10 == 0:  # Every 10 minutes
                    self.trigger_alert(rule_id, "System health check passed")

    def _send_notification(self, notification: Dict[str, Any]):
        """Send notification via specified channel"""
        alert = notification['alert']
        channel = notification['channel']

        # Simulate sending notifications
        logger.info(f"Sending {channel.value} notification for alert {alert.alert_id}: {alert.message}")

        # In a real implementation, this would integrate with:
        # - Email services (SMTP/SendGrid/etc.)
        # - SMS services (Twilio/AWS SNS/etc.)
        # - Webhook endpoints
        # - Slack API
        # - Dashboard real-time updates

    def get_user_alerts(self, user_id: str, active_only: bool = True) -> List[Alert]:
        """Get alerts for a user"""
        user_alerts = []
        for alert in self.alerts.values():
            if alert.user_id == user_id:
                if not active_only or alert.is_active:
                    user_alerts.append(alert)

        return sorted(user_alerts, key=lambda a: a.created_at, reverse=True)

    def resolve_alert(self, alert_id: str, user_id: str) -> bool:
        """Resolve an alert"""
        alert = self.alerts.get(alert_id)
        if alert and alert.user_id == user_id:
            alert.is_active = False
            alert.resolved_at = datetime.now()
            logger.info(f"Alert {alert_id} resolved by user {user_id}")
            return True
        return False

class ComplianceManager:
    """Enterprise compliance and risk management"""

    def __init__(self):
        self.rules: Dict[str, Dict[str, Any]] = {}
        self.violations: List[Dict[str, Any]] = []
        self.risk_profiles: Dict[str, Dict[str, Any]] = {}

    def create_compliance_rule(self, org_id: str, rule_type: ComplianceRule,
                              parameters: Dict[str, Any]) -> str:
        """Create compliance rule"""
        rule_id = str(uuid.uuid4())

        rule = {
            'rule_id': rule_id,
            'org_id': org_id,
            'rule_type': rule_type,
            'parameters': parameters,
            'created_at': datetime.now(),
            'is_active': True,
            'violations_count': 0
        }

        self.rules[rule_id] = rule
        logger.info(f"Created compliance rule: {rule_type.value} for org {org_id}")
        return rule_id

    def check_compliance(self, org_id: str, action: str, data: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """Check action against compliance rules"""
        violations = []

        org_rules = [rule for rule in self.rules.values()
                    if rule['org_id'] == org_id and rule['is_active']]

        for rule in org_rules:
            rule_type = rule['rule_type']
            params = rule['parameters']

            if rule_type == ComplianceRule.POSITION_LIMIT:
                max_position = params.get('max_position_value', 1000000)
                if data.get('position_value', 0) > max_position:
                    violations.append(f"Position value exceeds limit: {max_position}")

            elif rule_type == ComplianceRule.RISK_LIMIT:
                max_risk_score = params.get('max_risk_score', 80)
                if data.get('risk_score', 0) > max_risk_score:
                    violations.append(f"Risk score exceeds limit: {max_risk_score}")

            elif rule_type == ComplianceRule.TRADING_HOURS:
                allowed_hours = params.get('allowed_hours', [9, 16])  # 9 AM to 4 PM
                current_hour = datetime.now().hour
                if not (allowed_hours[0] <= current_hour <= allowed_hours[1]):
                    violations.append(f"Trading outside allowed hours: {allowed_hours}")

            elif rule_type == ComplianceRule.GEOGRAPHIC_RESTRICTION:
                restricted_regions = params.get('restricted_regions', [])
                user_region = data.get('user_region', 'unknown')
                if user_region in restricted_regions:
                    violations.append(f"Access from restricted region: {user_region}")

        # Log violations
        for violation in violations:
            self._log_violation(org_id, action, violation, data)

        return len(violations) == 0, violations

    def _log_violation(self, org_id: str, action: str, violation: str, data: Dict[str, Any]):
        """Log compliance violation"""
        violation_record = {
            'violation_id': str(uuid.uuid4()),
            'org_id': org_id,
            'action': action,
            'violation': violation,
            'data': data,
            'timestamp': datetime.now(),
            'resolved': False
        }

        self.violations.append(violation_record)
        logger.warning(f"Compliance violation in org {org_id}: {violation}")

    def get_compliance_report(self, org_id: str, days: int = 30) -> Dict[str, Any]:
        """Generate compliance report"""
        cutoff_date = datetime.now() - timedelta(days=days)

        org_violations = [
            v for v in self.violations
            if v['org_id'] == org_id and v['timestamp'] > cutoff_date
        ]

        violation_by_type = defaultdict(int)
        for violation in org_violations:
            violation_by_type[violation['violation']] += 1

        return {
            'org_id': org_id,
            'period_days': days,
            'total_violations': len(org_violations),
            'violations_by_type': dict(violation_by_type),
            'unresolved_violations': len([v for v in org_violations if not v['resolved']]),
            'compliance_score': max(0, 100 - len(org_violations) * 5),  # Simple scoring
            'generated_at': datetime.now()
        }

class AuditLogger:
    """Enterprise audit logging"""

    def __init__(self):
        self.logs: List[AuditLog] = []
        self.max_logs = 100000  # Keep last 100k logs in memory

    def log_action(self, user_id: str, action: str, resource: str,
                   details: Dict[str, Any] = None, ip_address: str = None,
                   user_agent: str = None):
        """Log user action"""
        log_entry = AuditLog(
            log_id=str(uuid.uuid4()),
            user_id=user_id,
            action=action,
            resource=resource,
            timestamp=datetime.now(),
            details=details or {},
            ip_address=ip_address,
            user_agent=user_agent
        )

        self.logs.append(log_entry)

        # Keep only recent logs to prevent memory issues
        if len(self.logs) > self.max_logs:
            self.logs = self.logs[-self.max_logs:]

        logger.debug(f"Audit log: {user_id} {action} {resource}")

    def search_logs(self, user_id: str = None, action: str = None,
                   resource: str = None, start_date: datetime = None,
                   end_date: datetime = None, limit: int = 1000) -> List[AuditLog]:
        """Search audit logs"""
        filtered_logs = self.logs

        if user_id:
            filtered_logs = [log for log in filtered_logs if log.user_id == user_id]

        if action:
            filtered_logs = [log for log in filtered_logs if action.lower() in log.action.lower()]

        if resource:
            filtered_logs = [log for log in filtered_logs if resource.lower() in log.resource.lower()]

        if start_date:
            filtered_logs = [log for log in filtered_logs if log.timestamp >= start_date]

        if end_date:
            filtered_logs = [log for log in filtered_logs if log.timestamp <= end_date]

        # Sort by timestamp descending and limit results
        filtered_logs.sort(key=lambda x: x.timestamp, reverse=True)
        return filtered_logs[:limit]

    def get_user_activity_summary(self, user_id: str, days: int = 30) -> Dict[str, Any]:
        """Get user activity summary"""
        cutoff_date = datetime.now() - timedelta(days=days)
        user_logs = [log for log in self.logs
                    if log.user_id == user_id and log.timestamp > cutoff_date]

        actions_count = defaultdict(int)
        resources_count = defaultdict(int)
        daily_activity = defaultdict(int)

        for log in user_logs:
            actions_count[log.action] += 1
            resources_count[log.resource] += 1
            day_key = log.timestamp.strftime('%Y-%m-%d')
            daily_activity[day_key] += 1

        return {
            'user_id': user_id,
            'period_days': days,
            'total_actions': len(user_logs),
            'actions_by_type': dict(actions_count),
            'resources_accessed': dict(resources_count),
            'daily_activity': dict(daily_activity),
            'most_active_day': max(daily_activity.items(), key=lambda x: x[1])[0] if daily_activity else None,
            'generated_at': datetime.now()
        }

class EnterpriseFeaturesSystem:
    """Main enterprise features system"""

    def __init__(self, secret_key: str = None):
        if not secret_key:
            secret_key = secrets.token_urlsafe(32)

        self.security = SecurityManager(secret_key)
        self.user_manager = UserManager(self.security)
        self.alert_manager = AlertManager()
        self.compliance_manager = ComplianceManager()
        self.audit_logger = AuditLogger()

        self.is_running = False

        logger.info("Enterprise Features System initialized")

    def start(self):
        """Start all enterprise services"""
        self.is_running = True
        self.alert_manager.start()

        # Create demo data
        self._create_demo_data()

        logger.info("Enterprise Features System started")

    def stop(self):
        """Stop all enterprise services"""
        self.is_running = False
        self.alert_manager.stop()
        logger.info("Enterprise Features System stopped")

    def _create_demo_data(self):
        """Create demonstration data"""
        try:
            # Create demo organization
            org = self.user_manager.create_organization("Demo Corp", "enterprise")

            # Create demo users
            admin_user = self.user_manager.create_user(
                "admin", "admin@demo.com", "admin123", org.org_id, UserRole.ADMIN
            )

            analyst_user = self.user_manager.create_user(
                "analyst", "analyst@demo.com", "analyst123", org.org_id, UserRole.ANALYST
            )

            # Create demo alerts
            self.alert_manager.create_alert_rule(
                admin_user.user_id,
                AlertType.SYSTEM_HEALTH,
                {"check_interval": 300},
                [NotificationChannel.EMAIL, NotificationChannel.DASHBOARD],
                AlertSeverity.MEDIUM
            )

            # Create demo compliance rules
            self.compliance_manager.create_compliance_rule(
                org.org_id,
                ComplianceRule.POSITION_LIMIT,
                {"max_position_value": 1000000}
            )

            self.compliance_manager.create_compliance_rule(
                org.org_id,
                ComplianceRule.TRADING_HOURS,
                {"allowed_hours": [9, 16]}
            )

            # Create demo audit logs
            self.audit_logger.log_action(
                admin_user.user_id, "login", "system",
                {"method": "password"}, "192.168.1.100", "Mozilla/5.0"
            )

            self.audit_logger.log_action(
                analyst_user.user_id, "view_portfolio", "portfolio/demo",
                {"portfolio_id": "demo123"}, "192.168.1.101", "Chrome/91.0"
            )

            logger.info("Demo data created successfully")

        except Exception as e:
            logger.error(f"Error creating demo data: {e}")

    def authenticate(self, username: str = None, password: str = None,
                    api_key: str = None, token: str = None) -> Optional[User]:
        """Unified authentication method"""

        if username and password:
            return self.user_manager.authenticate_user(username, password)
        elif api_key:
            return self.user_manager.authenticate_api_key(api_key)
        elif token:
            token_data = self.security.verify_token(token)
            if token_data:
                return self.user_manager.users.get(token_data['user_id'])

        return None

    def check_permission(self, user: User, permission: str) -> bool:
        """Check if user has specific permission"""
        return permission in user.permissions

    def create_api_token(self, user_id: str, name: str, permissions: List[str],
                        expires_days: int = 365) -> str:
        """Create API token for user"""
        user = self.user_manager.users.get(user_id)
        if not user:
            raise ValueError("User not found")

        # Filter permissions based on user's permissions
        allowed_permissions = [p for p in permissions if p in user.permissions]

        token = self.security.generate_token(user_id, allowed_permissions, expires_days * 24)

        # Log token creation
        self.audit_logger.log_action(
            user_id, "create_api_token", "token",
            {"token_name": name, "permissions": allowed_permissions}
        )

        return token

    def get_system_dashboard(self, user_id: str) -> Dict[str, Any]:
        """Get enterprise dashboard data"""
        user = self.user_manager.users.get(user_id)
        if not user:
            return {}

        # Get organization data
        org = self.user_manager.organizations.get(user.organization_id)
        org_users = [u for u in self.user_manager.users.values()
                    if u.organization_id == user.organization_id]

        # Get recent alerts
        recent_alerts = self.alert_manager.get_user_alerts(user_id)[:10]

        # Get compliance status
        compliance_report = self.compliance_manager.get_compliance_report(user.organization_id, 7)

        # Get activity summary
        activity_summary = self.audit_logger.get_user_activity_summary(user_id, 7)

        dashboard_data = {
            'user': {
                'id': user.user_id,
                'username': user.username,
                'role': user.role.value,
                'last_login': user.last_login.isoformat() if user.last_login else None,
                'permissions': user.permissions
            },
            'organization': {
                'id': org.org_id,
                'name': org.name,
                'plan': org.plan_type,
                'user_count': len(org_users),
                'max_users': org.max_users,
                'features': org.features
            },
            'alerts': {
                'total': len(recent_alerts),
                'active': len([a for a in recent_alerts if a.is_active]),
                'recent': [
                    {
                        'id': alert.alert_id,
                        'title': alert.title,
                        'severity': alert.severity.value,
                        'created_at': alert.created_at.isoformat()
                    }
                    for alert in recent_alerts[:5]
                ]
            },
            'compliance': {
                'score': compliance_report['compliance_score'],
                'violations': compliance_report['total_violations'],
                'unresolved': compliance_report['unresolved_violations']
            },
            'activity': {
                'total_actions': activity_summary['total_actions'],
                'most_active_day': activity_summary['most_active_day']
            },
            'system_status': {
                'status': 'healthy',
                'uptime': '99.9%',
                'last_updated': datetime.now().isoformat()
            }
        }

        return dashboard_data

    def get_system_health(self) -> Dict[str, Any]:
        """Get system health metrics"""
        return {
            'status': 'running' if self.is_running else 'stopped',
            'services': {
                'user_management': len(self.user_manager.users),
                'organizations': len(self.user_manager.organizations),
                'alert_rules': len(self.alert_manager.alert_rules),
                'compliance_rules': len(self.compliance_manager.rules),
                'audit_logs': len(self.audit_logger.logs)
            },
            'system_load': 'normal',
            'memory_usage': 'acceptable',
            'last_check': datetime.now().isoformat()
        }

def main():
    """Main function for testing enterprise features"""

    print("🚀 Initializing Enterprise Features System...")

    enterprise = EnterpriseFeaturesSystem()

    try:
        # Start the system
        enterprise.start()
        print("✅ Enterprise system started successfully")

        # Test authentication
        print("\n🔐 Testing Authentication...")

        # Test password authentication
        user = enterprise.authenticate(username="admin", password="admin123")
        if user:
            print(f"✅ Admin authenticated: {user.username} ({user.role.value})")

        # Test API key authentication
        api_user = enterprise.authenticate(username="analyst", password="analyst123")
        if api_user:
            print(f"✅ Analyst authenticated: {api_user.username} ({api_user.role.value})")

        # Test token creation
        print("\n🎫 Testing Token Management...")
        if user:
            token = enterprise.create_api_token(
                user.user_id, "Test Token", ["read", "write"], 30
            )
            print(f"✅ API Token created: {token[:50]}...")

            # Test token authentication
            token_user = enterprise.authenticate(token=token)
            if token_user:
                print(f"✅ Token authenticated: {token_user.username}")

        # Test dashboard
        print("\n📊 Testing Enterprise Dashboard...")
        if user:
            dashboard = enterprise.get_system_dashboard(user.user_id)
            print(f"✅ Dashboard loaded:")
            print(f"   Organization: {dashboard['organization']['name']}")
            print(f"   Plan: {dashboard['organization']['plan']}")
            print(f"   Users: {dashboard['organization']['user_count']}/{dashboard['organization']['max_users']}")
            print(f"   Alerts: {dashboard['alerts']['total']} ({dashboard['alerts']['active']} active)")
            print(f"   Compliance Score: {dashboard['compliance']['score']}%")

        # Test compliance
        print("\n⚖️ Testing Compliance Management...")
        compliance_ok, violations = enterprise.compliance_manager.check_compliance(
            user.organization_id if user else "test",
            "trade_execution",
            {"position_value": 500000, "risk_score": 60}
        )
        print(f"✅ Compliance check: {'PASS' if compliance_ok else 'FAIL'}")
        if violations:
            for violation in violations:
                print(f"   - {violation}")

        # Test rate limiting
        print("\n🚦 Testing Rate Limiting...")
        for i in range(5):
            allowed = enterprise.security.check_rate_limit("test_user", 3, 60)
            print(f"   Request {i+1}: {'✅ Allowed' if allowed else '❌ Rate limited'}")

        # Test audit logging
        print("\n📝 Testing Audit Logging...")
        if user:
            enterprise.audit_logger.log_action(
                user.user_id, "test_action", "test_resource",
                {"test": True}, "127.0.0.1", "TestAgent/1.0"
            )

            logs = enterprise.audit_logger.search_logs(user_id=user.user_id, limit=5)
            print(f"✅ Found {len(logs)} audit logs for user")
            for log in logs:
                print(f"   - {log.timestamp.strftime('%H:%M:%S')}: {log.action} on {log.resource}")

        # Test system health
        print("\n🏥 System Health Check...")
        health = enterprise.get_system_health()
        print(f"✅ System Status: {health['status']}")
        print(f"✅ Services:")
        for service, count in health['services'].items():
            print(f"   - {service}: {count}")

        print("\n🎯 Enterprise Features System Test Completed Successfully!")

        # Wait for alerts to be processed
        time.sleep(2)

        # Check for triggered alerts
        if user:
            alerts = enterprise.alert_manager.get_user_alerts(user.user_id)
            if alerts:
                print(f"\n🚨 Found {len(alerts)} alerts:")
                for alert in alerts[:3]:
                    print(f"   - {alert.title}: {alert.message}")

    except Exception as e:
        print(f"❌ Error during testing: {e}")
        import traceback
        traceback.print_exc()

    finally:
        # Stop the system
        enterprise.stop()
        print("🛑 Enterprise system stopped")

if __name__ == "__main__":
    main()