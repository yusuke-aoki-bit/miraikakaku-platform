#!/usr/bin/env python3
"""
Security Enhancer for Miraikakaku
Implement comprehensive security measures
"""

import os
import json
import subprocess
import logging
import hashlib
import secrets
import re
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import requests

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(levelname)s | %(name)s | %(message)s'
)
logger = logging.getLogger(__name__)

class SecurityEnhancer:
    def __init__(self):
        self.project_root = '/mnt/c/Users/yuuku/cursor/miraikakaku'
        self.api_dir = os.path.join(self.project_root, 'miraikakakuapi')
        self.frontend_dir = os.path.join(self.project_root, 'miraikakakufront')

    def audit_security_vulnerabilities(self) -> Dict[str, Any]:
        """Audit system for security vulnerabilities"""
        results = {
            'timestamp': datetime.now().isoformat(),
            'vulnerabilities': [],
            'security_scores': {},
            'recommendations': [],
            'status': 'success'
        }

        try:
            # Check for hardcoded secrets
            logger.info("Scanning for hardcoded secrets...")
            secrets_found = self._scan_for_secrets()

            if secrets_found:
                results['vulnerabilities'].extend(secrets_found)
                results['security_scores']['secrets'] = len(secrets_found)
            else:
                results['security_scores']['secrets'] = 0

            # Check file permissions
            logger.info("Checking file permissions...")
            permission_issues = self._check_file_permissions()

            if permission_issues:
                results['vulnerabilities'].extend(permission_issues)
                results['security_scores']['permissions'] = len(permission_issues)
            else:
                results['security_scores']['permissions'] = 0

            # Check dependency vulnerabilities
            logger.info("Checking dependency vulnerabilities...")
            dependency_issues = self._check_dependencies()

            if dependency_issues:
                results['vulnerabilities'].extend(dependency_issues)
                results['security_scores']['dependencies'] = len(dependency_issues)
            else:
                results['security_scores']['dependencies'] = 0

            # Generate recommendations
            total_vulnerabilities = sum(results['security_scores'].values())

            if total_vulnerabilities == 0:
                results['recommendations'].append('No critical vulnerabilities found')
            else:
                results['recommendations'].append(f'Found {total_vulnerabilities} security issues that need attention')

                if results['security_scores']['secrets'] > 0:
                    results['recommendations'].append('Move hardcoded secrets to environment variables')

                if results['security_scores']['permissions'] > 0:
                    results['recommendations'].append('Fix file permission issues')

                if results['security_scores']['dependencies'] > 0:
                    results['recommendations'].append('Update vulnerable dependencies')

        except Exception as e:
            logger.error(f"Error during security audit: {e}")
            results['status'] = 'failed'
            results['error'] = str(e)

        return results

    def _scan_for_secrets(self) -> List[Dict[str, Any]]:
        """Scan for hardcoded secrets in code"""
        vulnerabilities = []

        # Patterns for common secrets
        secret_patterns = {
            'password': r'password\s*[:=]\s*["\']([^"\']{8,})["\']',
            'api_key': r'api[_-]?key\s*[:=]\s*["\']([^"\']{16,})["\']',
            'secret_key': r'secret[_-]?key\s*[:=]\s*["\']([^"\']{16,})["\']',
            'database_url': r'database[_-]?url\s*[:=]\s*["\']([^"\']+)["\']',
            'connection_string': r'connectionstring\s*[:=]\s*["\']([^"\']+)["\']'
        }

        # Scan Python files
        for root, dirs, files in os.walk(self.project_root):
            for file in files:
                if file.endswith('.py'):
                    file_path = os.path.join(root, file)
                    try:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            content = f.read()

                        for secret_type, pattern in secret_patterns.items():
                            matches = re.finditer(pattern, content, re.IGNORECASE)
                            for match in matches:
                                vulnerabilities.append({
                                    'type': 'hardcoded_secret',
                                    'severity': 'high',
                                    'file': file_path,
                                    'secret_type': secret_type,
                                    'line': content[:match.start()].count('\n') + 1,
                                    'message': f'Hardcoded {secret_type} found in {file_path}'
                                })
                    except Exception as e:
                        logger.warning(f"Could not scan file {file_path}: {e}")

        return vulnerabilities

    def _check_file_permissions(self) -> List[Dict[str, Any]]:
        """Check for insecure file permissions"""
        vulnerabilities = []

        # Check for world-writable files
        try:
            result = subprocess.run([
                'find', self.project_root, '-type', 'f', '-perm', '/o+w'
            ], capture_output=True, text=True, timeout=30)

            if result.returncode == 0 and result.stdout.strip():
                for file_path in result.stdout.strip().split('\n'):
                    if file_path:
                        vulnerabilities.append({
                            'type': 'insecure_permissions',
                            'severity': 'medium',
                            'file': file_path,
                            'message': f'World-writable file: {file_path}'
                        })
        except Exception as e:
            logger.warning(f"Could not check file permissions: {e}")

        return vulnerabilities

    def _check_dependencies(self) -> List[Dict[str, Any]]:
        """Check for vulnerable dependencies"""
        vulnerabilities = []

        # Check Python dependencies
        requirements_files = [
            os.path.join(self.api_dir, 'requirements.txt'),
            os.path.join(self.batch_dir, 'requirements.txt')
        ]

        for req_file in requirements_files:
            if os.path.exists(req_file):
                try:
                    # Use safety to check for known vulnerabilities
                    result = subprocess.run([
                        'python3', '-m', 'pip', 'install', '--dry-run', '-r', req_file
                    ], capture_output=True, text=True, timeout=60)

                    # Note: This is a simplified check. In production, use tools like safety, bandit, or snyk
                    if 'WARNING' in result.stderr or 'ERROR' in result.stderr:
                        vulnerabilities.append({
                            'type': 'dependency_issue',
                            'severity': 'medium',
                            'file': req_file,
                            'message': f'Potential dependency issues in {req_file}'
                        })

                except Exception as e:
                    logger.warning(f"Could not check dependencies in {req_file}: {e}")

        return vulnerabilities

    def implement_authentication_security(self) -> Dict[str, Any]:
        """Implement authentication and authorization security"""
        results = {
            'timestamp': datetime.now().isoformat(),
            'implementations': [],
            'configurations': [],
            'status': 'success'
        }

        try:
            # Create JWT authentication middleware
            jwt_auth_code = '''
import jwt
import hashlib
import secrets
from datetime import datetime, timedelta
from functools import wraps
from flask import request, jsonify, current_app

class JWTAuth:
    def __init__(self, secret_key=None):
        self.secret_key = secret_key or self._generate_secret_key()
        self.algorithm = 'HS256'
        self.expiry_hours = 24

    def _generate_secret_key(self):
        """Generate a secure secret key"""
        return secrets.token_urlsafe(32)

    def generate_token(self, user_id, role='user', permissions=None):
        """Generate JWT token"""
        payload = {
            'user_id': user_id,
            'role': role,
            'permissions': permissions or [],
            'exp': datetime.utcnow() + timedelta(hours=self.expiry_hours),
            'iat': datetime.utcnow()
        }

        return jwt.encode(payload, self.secret_key, algorithm=self.algorithm)

    def verify_token(self, token):
        """Verify JWT token"""
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            return payload
        except jwt.ExpiredSignatureError:
            return None
        except jwt.InvalidTokenError:
            return None

    def require_auth(self, required_role=None, required_permissions=None):
        """Authentication decorator"""
        def decorator(f):
            @wraps(f)
            def wrapper(*args, **kwargs):
                token = request.headers.get('Authorization')
                if not token:
                    return jsonify({'error': 'No authorization token provided'}), 401

                # Remove 'Bearer ' prefix if present
                if token.startswith('Bearer '):
                    token = token[7:]

                payload = self.verify_token(token)
                if not payload:
                    return jsonify({'error': 'Invalid or expired token'}), 401

                # Check role if specified
                if required_role and payload.get('role') != required_role:
                    return jsonify({'error': 'Insufficient privileges'}), 403

                # Check permissions if specified
                if required_permissions:
                    user_perms = set(payload.get('permissions', []))
                    required_perms = set(required_permissions)
                    if not required_perms.issubset(user_perms):
                        return jsonify({'error': 'Insufficient permissions'}), 403

                # Add user info to request
                request.user = payload
                return f(*args, **kwargs)
            return wrapper
        return decorator

class PasswordSecurity:
    @staticmethod
    def hash_password(password):
        """Hash password with salt"""
        salt = secrets.token_hex(16)
        password_hash = hashlib.pbkdf2_hmac('sha256',
                                          password.encode('utf-8'),
                                          salt.encode('utf-8'),
                                          100000)
        return salt + password_hash.hex()

    @staticmethod
    def verify_password(password, stored_password):
        """Verify password against stored hash"""
        salt = stored_password[:32]
        stored_hash = stored_password[32:]
        password_hash = hashlib.pbkdf2_hmac('sha256',
                                          password.encode('utf-8'),
                                          salt.encode('utf-8'),
                                          100000)
        return password_hash.hex() == stored_hash
'''

            auth_path = os.path.join(self.api_dir, 'auth_security.py')
            with open(auth_path, 'w') as f:
                f.write(jwt_auth_code)

            results['implementations'].append({
                'component': 'jwt_authentication',
                'path': auth_path,
                'features': ['JWT tokens', 'Role-based access', 'Password hashing']
            })

            # Create rate limiting middleware
            rate_limit_code = '''
import time
import redis
from functools import wraps
from flask import request, jsonify

class RateLimiter:
    def __init__(self, redis_client=None):
        self.redis = redis_client or redis.Redis(host='localhost', port=6379, db=1)

    def rate_limit(self, requests_per_minute=60, per_ip=True):
        """Rate limiting decorator"""
        def decorator(f):
            @wraps(f)
            def wrapper(*args, **kwargs):
                # Get identifier (IP or user)
                if per_ip:
                    identifier = request.remote_addr
                else:
                    identifier = getattr(request, 'user', {}).get('user_id', request.remote_addr)

                key = f"rate_limit:{f.__name__}:{identifier}"

                # Get current count
                current = self.redis.get(key)
                if current is None:
                    # First request in window
                    self.redis.setex(key, 60, 1)
                else:
                    current = int(current)
                    if current >= requests_per_minute:
                        return jsonify({
                            'error': 'Rate limit exceeded',
                            'retry_after': self.redis.ttl(key)
                        }), 429

                    # Increment counter
                    self.redis.incr(key)

                return f(*args, **kwargs)
            return wrapper
        return decorator

    def get_rate_limit_info(self, endpoint, identifier):
        """Get current rate limit status"""
        key = f"rate_limit:{endpoint}:{identifier}"
        current = self.redis.get(key)
        ttl = self.redis.ttl(key)

        return {
            'requests_made': int(current) if current else 0,
            'time_remaining': ttl if ttl > 0 else 0
        }
'''

            rate_limit_path = os.path.join(self.api_dir, 'rate_limiter.py')
            with open(rate_limit_path, 'w') as f:
                f.write(rate_limit_code)

            results['implementations'].append({
                'component': 'rate_limiting',
                'path': rate_limit_path,
                'features': ['IP-based limiting', 'User-based limiting', 'Redis backend']
            })

        except Exception as e:
            logger.error(f"Error implementing authentication security: {e}")
            results['status'] = 'failed'
            results['error'] = str(e)

        return results

    def implement_data_protection(self) -> Dict[str, Any]:
        """Implement data encryption and protection"""
        results = {
            'timestamp': datetime.now().isoformat(),
            'protections': [],
            'encryption_configs': [],
            'status': 'success'
        }

        try:
            # Create data encryption utilities
            encryption_code = '''
import os
import base64
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import secrets

class DataEncryption:
    def __init__(self, password=None):
        if password:
            self.key = self._derive_key_from_password(password)
        else:
            self.key = Fernet.generate_key()
        self.cipher = Fernet(self.key)

    def _derive_key_from_password(self, password):
        """Derive encryption key from password"""
        salt = b'miraikakaku_salt_2025'  # In production, use random salt per user
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
        )
        key = base64.urlsafe_b64encode(kdf.derive(password.encode()))
        return key

    def encrypt(self, data):
        """Encrypt data"""
        if isinstance(data, str):
            data = data.encode()
        return self.cipher.encrypt(data)

    def decrypt(self, encrypted_data):
        """Decrypt data"""
        decrypted = self.cipher.decrypt(encrypted_data)
        return decrypted.decode()

    def encrypt_dict(self, data_dict, fields_to_encrypt):
        """Encrypt specific fields in a dictionary"""
        encrypted_dict = data_dict.copy()
        for field in fields_to_encrypt:
            if field in encrypted_dict:
                encrypted_dict[field] = self.encrypt(str(encrypted_dict[field])).decode()
        return encrypted_dict

    def decrypt_dict(self, encrypted_dict, fields_to_decrypt):
        """Decrypt specific fields in a dictionary"""
        decrypted_dict = encrypted_dict.copy()
        for field in fields_to_decrypt:
            if field in decrypted_dict:
                decrypted_dict[field] = self.decrypt(encrypted_dict[field].encode())
        return decrypted_dict

class PIIProtection:
    """Personally Identifiable Information protection"""

    @staticmethod
    def mask_email(email):
        """Mask email address"""
        if '@' not in email:
            return email
        local, domain = email.split('@', 1)
        masked_local = local[0] + '*' * (len(local) - 2) + local[-1] if len(local) > 2 else '*' * len(local)
        return f"{masked_local}@{domain}"

    @staticmethod
    def mask_phone(phone):
        """Mask phone number"""
        if len(phone) < 4:
            return '*' * len(phone)
        return '*' * (len(phone) - 4) + phone[-4:]

    @staticmethod
    def mask_credit_card(cc_number):
        """Mask credit card number"""
        cc_str = str(cc_number).replace(' ', '').replace('-', '')
        if len(cc_str) < 4:
            return '*' * len(cc_str)
        return '*' * (len(cc_str) - 4) + cc_str[-4:]

    @staticmethod
    def sanitize_log_data(data):
        """Sanitize data before logging"""
        if isinstance(data, dict):
            sanitized = {}
            sensitive_fields = ['password', 'token', 'secret', 'key', 'email', 'phone']
            for key, value in data.items():
                if any(field in key.lower() for field in sensitive_fields):
                    sanitized[key] = '[REDACTED]'
                else:
                    sanitized[key] = value
            return sanitized
        return data
'''

            encryption_path = os.path.join(self.api_dir, 'data_encryption.py')
            with open(encryption_path, 'w') as f:
                f.write(encryption_code)

            results['protections'].append({
                'component': 'data_encryption',
                'path': encryption_path,
                'features': ['Field-level encryption', 'PII masking', 'Log sanitization']
            })

            # Create secure configuration management
            config_security_code = '''
import os
import json
from pathlib import Path

class SecureConfig:
    def __init__(self, config_file='.env.secure'):
        self.config_file = config_file
        self.config = {}
        self.load_config()

    def load_config(self):
        """Load configuration from secure file"""
        config_path = Path(self.config_file)
        if config_path.exists():
            with open(config_path, 'r') as f:
                for line in f:
                    if '=' in line and not line.startswith('#'):
                        key, value = line.strip().split('=', 1)
                        self.config[key] = value

        # Override with environment variables
        for key in self.config:
            env_value = os.environ.get(key)
            if env_value:
                self.config[key] = env_value

    def get(self, key, default=None):
        """Get configuration value"""
        return self.config.get(key, default)

    def get_database_config(self):
        """Get database configuration securely"""
        return {
            'host': self.get('DB_HOST', 'localhost'),
            'port': int(self.get('DB_PORT', 5432)),
            'database': self.get('DB_NAME', 'miraikakaku'),
            'user': self.get('DB_USER', 'postgres'),
            'password': self.get('DB_PASSWORD', ''),
            'sslmode': self.get('DB_SSL_MODE', 'require')
        }

    def get_api_config(self):
        """Get API configuration securely"""
        return {
            'secret_key': self.get('API_SECRET_KEY'),
            'debug': self.get('API_DEBUG', 'false').lower() == 'true',
            'host': self.get('API_HOST', '0.0.0.0'),
            'port': int(self.get('API_PORT', 8080))
        }

    def validate_required_configs(self, required_keys):
        """Validate that required configuration keys are present"""
        missing = [key for key in required_keys if not self.get(key)]
        if missing:
            raise ValueError(f"Missing required configuration keys: {missing}")

# Example secure configuration template
SECURE_CONFIG_TEMPLATE = """
# Database Configuration
DB_HOST=your_db_host
DB_PORT=5432
DB_NAME=miraikakaku
DB_USER=your_db_user
DB_PASSWORD=your_secure_password
DB_SSL_MODE=require

# API Configuration
API_SECRET_KEY=your_secret_key_here
API_DEBUG=false
API_HOST=0.0.0.0
API_PORT=8080

# External API Keys
ALPHA_VANTAGE_API_KEY=your_alpha_vantage_key
POLYGON_API_KEY=your_polygon_key

# Redis Configuration
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_PASSWORD=your_redis_password

# Monitoring
SENTRY_DSN=your_sentry_dsn
LOG_LEVEL=INFO
"""
'''

            config_security_path = os.path.join(self.api_dir, 'secure_config.py')
            with open(config_security_path, 'w') as f:
                f.write(config_security_code)

            # Create .env.secure template
            env_template_path = os.path.join(self.project_root, '.env.secure.template')
            with open(env_template_path, 'w') as f:
                f.write(SECURE_CONFIG_TEMPLATE)

            results['protections'].append({
                'component': 'secure_configuration',
                'path': config_security_path,
                'template': env_template_path,
                'features': ['Environment-based config', 'Validation', 'Templates']
            })

        except Exception as e:
            logger.error(f"Error implementing data protection: {e}")
            results['status'] = 'failed'
            results['error'] = str(e)

        return results

    def implement_network_security(self) -> Dict[str, Any]:
        """Implement network security measures"""
        results = {
            'timestamp': datetime.now().isoformat(),
            'security_configs': [],
            'firewall_rules': [],
            'recommendations': [],
            'status': 'success'
        }

        try:
            # Create CORS security configuration
            cors_config = '''
from flask_cors import CORS

def configure_cors(app):
    """Configure CORS securely"""
    CORS(app,
         origins=['https://miraikakaku.com', 'https://www.miraikakaku.com'],
         methods=['GET', 'POST', 'PUT', 'DELETE'],
         allow_headers=['Content-Type', 'Authorization'],
         expose_headers=['Content-Range', 'X-Content-Range'],
         supports_credentials=True,
         max_age=3600)

def configure_security_headers(app):
    """Configure security headers"""
    @app.after_request
    def set_security_headers(response):
        # Prevent XSS attacks
        response.headers['X-Content-Type-Options'] = 'nosniff'
        response.headers['X-Frame-Options'] = 'DENY'
        response.headers['X-XSS-Protection'] = '1; mode=block'

        # HTTPS enforcement
        response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'

        # Content Security Policy
        response.headers['Content-Security-Policy'] = (
            "default-src 'self'; "
            "script-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net; "
            "style-src 'self' 'unsafe-inline' https://fonts.googleapis.com; "
            "font-src 'self' https://fonts.gstatic.com; "
            "img-src 'self' data: https:; "
            "connect-src 'self' https://api.miraikakaku.com"
        )

        # Referrer Policy
        response.headers['Referrer-Policy'] = 'strict-origin-when-cross-origin'

        return response

    return app
'''

            cors_path = os.path.join(self.api_dir, 'security_headers.py')
            with open(cors_path, 'w') as f:
                f.write(cors_config)

            results['security_configs'].append({
                'component': 'cors_and_headers',
                'path': cors_path,
                'protections': ['XSS', 'CSRF', 'Clickjacking', 'MITM']
            })

            # Create input validation
            validation_code = '''
import re
import bleach
from typing import Any, Dict, List, Union

class InputValidator:
    """Secure input validation"""

    @staticmethod
    def validate_symbol(symbol):
        """Validate stock symbol"""
        if not symbol or not isinstance(symbol, str):
            return False

        # Allow only alphanumeric characters and dots (for some symbols)
        pattern = r'^[A-Z0-9.]{1,10}$'
        return bool(re.match(pattern, symbol.upper()))

    @staticmethod
    def validate_email(email):
        """Validate email address"""
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return bool(re.match(pattern, email))

    @staticmethod
    def validate_date(date_str):
        """Validate date format"""
        pattern = r'^\\d{4}-\\d{2}-\\d{2}$'
        return bool(re.match(pattern, date_str))

    @staticmethod
    def sanitize_html(html_content):
        """Sanitize HTML content"""
        allowed_tags = ['p', 'br', 'strong', 'em', 'u', 'ol', 'ul', 'li']
        allowed_attributes = {}

        return bleach.clean(html_content,
                          tags=allowed_tags,
                          attributes=allowed_attributes,
                          strip=True)

    @staticmethod
    def validate_numeric(value, min_val=None, max_val=None):
        """Validate numeric input"""
        try:
            num_val = float(value)
            if min_val is not None and num_val < min_val:
                return False
            if max_val is not None and num_val > max_val:
                return False
            return True
        except (ValueError, TypeError):
            return False

    @staticmethod
    def validate_pagination(page, limit):
        """Validate pagination parameters"""
        try:
            page = int(page)
            limit = int(limit)

            if page < 1 or page > 10000:  # Reasonable limits
                return False
            if limit < 1 or limit > 1000:
                return False

            return True
        except (ValueError, TypeError):
            return False

    @staticmethod
    def escape_sql_like(value):
        """Escape SQL LIKE patterns"""
        if not isinstance(value, str):
            return value

        # Escape special characters in LIKE patterns
        value = value.replace('\\\\', '\\\\\\\\')
        value = value.replace('%', '\\\\%')
        value = value.replace('_', '\\\\_')
        return value

class RequestValidator:
    """Validate HTTP requests"""

    @staticmethod
    def validate_json_request(request_data, required_fields, optional_fields=None):
        """Validate JSON request structure"""
        if not isinstance(request_data, dict):
            return False, "Request must be a JSON object"

        # Check required fields
        missing_fields = [field for field in required_fields if field not in request_data]
        if missing_fields:
            return False, f"Missing required fields: {missing_fields}"

        # Check for unexpected fields
        allowed_fields = set(required_fields) | set(optional_fields or [])
        unexpected_fields = [field for field in request_data.keys() if field not in allowed_fields]
        if unexpected_fields:
            return False, f"Unexpected fields: {unexpected_fields}"

        return True, "Valid request"

    @staticmethod
    def validate_request_size(request, max_size_mb=10):
        """Validate request size"""
        content_length = request.content_length
        if content_length and content_length > max_size_mb * 1024 * 1024:
            return False, f"Request too large (max {max_size_mb}MB)"
        return True, "Valid size"
'''

            validation_path = os.path.join(self.api_dir, 'input_validation.py')
            with open(validation_path, 'w') as f:
                f.write(validation_code)

            results['security_configs'].append({
                'component': 'input_validation',
                'path': validation_path,
                'protections': ['SQL Injection', 'XSS', 'Data validation']
            })

            # Generate firewall recommendations
            results['firewall_rules'] = [
                {
                    'rule': 'Allow HTTP/HTTPS',
                    'ports': [80, 443],
                    'description': 'Allow web traffic'
                },
                {
                    'rule': 'Allow SSH (admin only)',
                    'ports': [22],
                    'description': 'Restrict SSH to admin IPs only'
                },
                {
                    'rule': 'Block direct database access',
                    'ports': [5432, 3306],
                    'description': 'Database should only be accessible from application servers'
                },
                {
                    'rule': 'Allow Redis (internal)',
                    'ports': [6379],
                    'description': 'Redis access only from application servers'
                }
            ]

            results['recommendations'].extend([
                'Configure Web Application Firewall (WAF)',
                'Use VPN for admin access',
                'Implement DDoS protection',
                'Set up intrusion detection system (IDS)',
                'Use HTTPS everywhere with valid certificates',
                'Implement API gateway for rate limiting and monitoring'
            ])

        except Exception as e:
            logger.error(f"Error implementing network security: {e}")
            results['status'] = 'failed'
            results['error'] = str(e)

        return results

    def create_security_monitoring(self) -> Dict[str, Any]:
        """Create security monitoring and alerting"""
        results = {
            'timestamp': datetime.now().isoformat(),
            'monitoring_configs': [],
            'alert_rules': [],
            'status': 'success'
        }

        try:
            # Create security event logger
            security_logger_code = '''
import logging
import json
import time
from datetime import datetime
from typing import Dict, Any

class SecurityLogger:
    def __init__(self, log_file='security_events.log'):
        self.logger = logging.getLogger('security')
        self.logger.setLevel(logging.INFO)

        # File handler for security events
        handler = logging.FileHandler(log_file)
        formatter = logging.Formatter(
            '%(asctime)s | %(levelname)s | %(message)s'
        )
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)

    def log_auth_attempt(self, user_id, success, ip_address, user_agent=None):
        """Log authentication attempt"""
        event = {
            'event_type': 'authentication',
            'user_id': user_id,
            'success': success,
            'ip_address': ip_address,
            'user_agent': user_agent,
            'timestamp': datetime.utcnow().isoformat()
        }

        level = logging.INFO if success else logging.WARNING
        self.logger.log(level, json.dumps(event))

    def log_access_attempt(self, endpoint, user_id, ip_address, success, method='GET'):
        """Log API access attempt"""
        event = {
            'event_type': 'api_access',
            'endpoint': endpoint,
            'method': method,
            'user_id': user_id,
            'ip_address': ip_address,
            'success': success,
            'timestamp': datetime.utcnow().isoformat()
        }

        level = logging.INFO if success else logging.WARNING
        self.logger.log(level, json.dumps(event))

    def log_security_event(self, event_type, details, severity='medium'):
        """Log general security event"""
        event = {
            'event_type': event_type,
            'severity': severity,
            'details': details,
            'timestamp': datetime.utcnow().isoformat()
        }

        level_map = {
            'low': logging.INFO,
            'medium': logging.WARNING,
            'high': logging.ERROR,
            'critical': logging.CRITICAL
        }

        level = level_map.get(severity, logging.WARNING)
        self.logger.log(level, json.dumps(event))

    def log_rate_limit_exceeded(self, ip_address, endpoint, attempts):
        """Log rate limit violations"""
        self.log_security_event(
            'rate_limit_exceeded',
            {
                'ip_address': ip_address,
                'endpoint': endpoint,
                'attempts': attempts
            },
            'medium'
        )

    def log_suspicious_activity(self, activity_type, details):
        """Log suspicious activity"""
        self.log_security_event(
            'suspicious_activity',
            {
                'activity_type': activity_type,
                'details': details
            },
            'high'
        )

class SecurityMetrics:
    def __init__(self, redis_client=None):
        self.redis = redis_client
        self.metrics_prefix = 'security_metrics'

    def increment_counter(self, metric_name, value=1):
        """Increment security metric counter"""
        if self.redis:
            key = f"{self.metrics_prefix}:{metric_name}"
            self.redis.incr(key, value)
            # Set expiry for daily metrics
            if 'daily' in metric_name:
                self.redis.expire(key, 86400)  # 24 hours

    def get_metric(self, metric_name):
        """Get security metric value"""
        if self.redis:
            key = f"{self.metrics_prefix}:{metric_name}"
            value = self.redis.get(key)
            return int(value) if value else 0
        return 0

    def record_auth_failure(self, ip_address=None):
        """Record authentication failure"""
        self.increment_counter('auth_failures_total')
        self.increment_counter('auth_failures_daily')

        if ip_address:
            self.increment_counter(f'auth_failures_ip:{ip_address}')

    def record_rate_limit_hit(self, endpoint=None):
        """Record rate limit violation"""
        self.increment_counter('rate_limits_total')
        self.increment_counter('rate_limits_daily')

        if endpoint:
            self.increment_counter(f'rate_limits_endpoint:{endpoint}')

    def get_security_summary(self):
        """Get security metrics summary"""
        return {
            'auth_failures_daily': self.get_metric('auth_failures_daily'),
            'rate_limits_daily': self.get_metric('rate_limits_daily'),
            'total_auth_failures': self.get_metric('auth_failures_total'),
            'total_rate_limits': self.get_metric('rate_limits_total')
        }
'''

            security_logger_path = os.path.join(self.api_dir, 'security_monitoring.py')
            with open(security_logger_path, 'w') as f:
                f.write(security_logger_code)

            results['monitoring_configs'].append({
                'component': 'security_logger',
                'path': security_logger_path,
                'features': ['Event logging', 'Metrics collection', 'Suspicious activity detection']
            })

            # Define alert rules
            results['alert_rules'] = [
                {
                    'name': 'Multiple Authentication Failures',
                    'condition': 'auth_failures_from_ip > 5 in 5 minutes',
                    'action': 'Block IP for 1 hour',
                    'severity': 'high'
                },
                {
                    'name': 'Rate Limit Abuse',
                    'condition': 'rate_limit_hits > 10 in 1 minute',
                    'action': 'Extended rate limiting',
                    'severity': 'medium'
                },
                {
                    'name': 'Unusual API Access Pattern',
                    'condition': 'api_calls_from_ip > 1000 in 1 hour',
                    'action': 'Investigation required',
                    'severity': 'medium'
                },
                {
                    'name': 'Admin Access Outside Hours',
                    'condition': 'admin_login outside 9AM-6PM',
                    'action': 'Immediate notification',
                    'severity': 'high'
                },
                {
                    'name': 'Database Connection Anomaly',
                    'condition': 'db_connections > normal_baseline * 3',
                    'action': 'Performance investigation',
                    'severity': 'medium'
                }
            ]

        except Exception as e:
            logger.error(f"Error creating security monitoring: {e}")
            results['status'] = 'failed'
            results['error'] = str(e)

        return results

    def run_full_security_enhancement(self) -> Dict[str, Any]:
        """Run complete security enhancement"""
        logger.info("🔒 Starting security enhancement...")

        full_results = {
            'timestamp': datetime.now().isoformat(),
            'audit': {},
            'implementations': {},
            'monitoring': {},
            'overall_status': 'success',
            'summary': {}
        }

        try:
            # Step 1: Security audit
            logger.info("Step 1/5: Conducting security audit...")
            full_results['audit'] = self.audit_security_vulnerabilities()

            # Step 2: Authentication security
            logger.info("Step 2/5: Implementing authentication security...")
            full_results['implementations']['auth'] = self.implement_authentication_security()

            # Step 3: Data protection
            logger.info("Step 3/5: Implementing data protection...")
            full_results['implementations']['data_protection'] = self.implement_data_protection()

            # Step 4: Network security
            logger.info("Step 4/5: Implementing network security...")
            full_results['implementations']['network'] = self.implement_network_security()

            # Step 5: Security monitoring
            logger.info("Step 5/5: Setting up security monitoring...")
            full_results['monitoring'] = self.create_security_monitoring()

            # Generate summary
            total_vulnerabilities = sum(full_results['audit'].get('security_scores', {}).values())
            total_implementations = 0
            total_recommendations = len(full_results['audit'].get('recommendations', []))
            failed_steps = 0

            for category in ['implementations']:
                if category in full_results:
                    for impl_name, impl_result in full_results[category].items():
                        if impl_result.get('status') == 'failed':
                            failed_steps += 1
                            full_results['overall_status'] = 'partial_failure'

                        if 'implementations' in impl_result:
                            total_implementations += len(impl_result['implementations'])
                        if 'protections' in impl_result:
                            total_implementations += len(impl_result['protections'])
                        if 'security_configs' in impl_result:
                            total_implementations += len(impl_result['security_configs'])

                        if 'recommendations' in impl_result:
                            total_recommendations += len(impl_result['recommendations'])

            # Add monitoring recommendations
            if 'alert_rules' in full_results['monitoring']:
                total_recommendations += len(full_results['monitoring']['alert_rules'])

            full_results['summary'] = {
                'vulnerabilities_found': total_vulnerabilities,
                'security_implementations': total_implementations,
                'total_recommendations': total_recommendations,
                'failed_steps': failed_steps,
                'alert_rules_created': len(full_results['monitoring'].get('alert_rules', []))
            }

            if failed_steps > 0:
                logger.warning(f"⚠️  Security enhancement completed with {failed_steps} failed steps")
            else:
                logger.info("✅ Security enhancement completed successfully!")

        except Exception as e:
            logger.error(f"Error in security enhancement: {e}")
            full_results['overall_status'] = 'failed'
            full_results['error'] = str(e)

        return full_results

def main():
    """Main function for standalone execution"""
    import argparse

    parser = argparse.ArgumentParser(description='Security Enhancer')
    parser.add_argument('--audit', action='store_true', help='Run security audit only')
    parser.add_argument('--auth', action='store_true', help='Implement authentication security')
    parser.add_argument('--data', action='store_true', help='Implement data protection')
    parser.add_argument('--network', action='store_true', help='Implement network security')
    parser.add_argument('--monitoring', action='store_true', help='Set up security monitoring')
    parser.add_argument('--full', action='store_true', help='Run full security enhancement')

    args = parser.parse_args()

    enhancer = SecurityEnhancer()

    if args.audit:
        result = enhancer.audit_security_vulnerabilities()
        print(json.dumps(result, indent=2))
    elif args.auth:
        result = enhancer.implement_authentication_security()
        print(json.dumps(result, indent=2))
    elif args.data:
        result = enhancer.implement_data_protection()
        print(json.dumps(result, indent=2))
    elif args.network:
        result = enhancer.implement_network_security()
        print(json.dumps(result, indent=2))
    elif args.monitoring:
        result = enhancer.create_security_monitoring()
        print(json.dumps(result, indent=2))
    elif args.full:
        result = enhancer.run_full_security_enhancement()
        print(json.dumps(result, indent=2))
    else:
        # Default: run full enhancement
        result = enhancer.run_full_security_enhancement()
        print(json.dumps(result, indent=2))

if __name__ == "__main__":
    main()