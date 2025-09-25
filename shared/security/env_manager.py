#!/usr/bin/env python3
"""
Secure Environment Variable Management System
Provides encrypted storage and secure loading of environment variables
"""
import os
import json
import base64
import secrets
from pathlib import Path
from typing import Dict, Optional, Any
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

class SecureEnvManager:
    """Secure environment variable manager with encryption"""

    def __init__(self, master_password: Optional[str] = None):
        self.master_password = master_password or os.getenv('MIRAIKAKAKU_MASTER_KEY')
        self.env_dir = Path(__file__).parent / 'encrypted_env'
        self.env_dir.mkdir(exist_ok=True)

    def _derive_key(self, password: str, salt: bytes) -> bytes:
        """Derive encryption key from password"""
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
        )
        key = base64.urlsafe_b64encode(kdf.derive(password.encode()))
        return key

    def encrypt_env_file(self, env_file_path: str, environment: str = 'production') -> bool:
        """Encrypt .env file and store securely"""
        try:
            if not self.master_password:
                raise ValueError("Master password not provided")

            env_path = Path(env_file_path)
            if not env_path.exists():
                raise FileNotFoundError(f"Environment file not found: {env_file_path}")

            # Read environment variables
            env_vars = {}
            with open(env_path, 'r') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#'):
                        if '=' in line:
                            key, value = line.split('=', 1)
                            env_vars[key.strip()] = value.strip()

            # Generate salt and encrypt
            salt = secrets.token_bytes(16)
            key = self._derive_key(self.master_password, salt)
            fernet = Fernet(key)

            encrypted_data = fernet.encrypt(json.dumps(env_vars).encode())

            # Store encrypted file
            encrypted_file = self.env_dir / f"{environment}.enc"
            with open(encrypted_file, 'wb') as f:
                f.write(salt + encrypted_data)

            print(f"✅ Environment variables encrypted: {encrypted_file}")
            return True

        except Exception as e:
            print(f"❌ Failed to encrypt environment file: {e}")
            return False

    def decrypt_and_load_env(self, environment: str = 'production') -> Dict[str, str]:
        """Decrypt and load environment variables"""
        try:
            if not self.master_password:
                raise ValueError("Master password not provided")

            encrypted_file = self.env_dir / f"{environment}.enc"
            if not encrypted_file.exists():
                raise FileNotFoundError(f"Encrypted environment file not found: {encrypted_file}")

            # Read and decrypt
            with open(encrypted_file, 'rb') as f:
                data = f.read()

            salt = data[:16]
            encrypted_data = data[16:]

            key = self._derive_key(self.master_password, salt)
            fernet = Fernet(key)

            decrypted_data = fernet.decrypt(encrypted_data)
            env_vars = json.loads(decrypted_data.decode())

            # Load into environment
            for key, value in env_vars.items():
                os.environ[key] = value

            return env_vars

        except Exception as e:
            print(f"❌ Failed to decrypt environment file: {e}")
            return {}

    def generate_secure_credentials(self) -> Dict[str, str]:
        """Generate new secure credentials"""
        return {
            'JWT_SECRET_KEY': secrets.token_urlsafe(64),
            'SESSION_SECRET': secrets.token_urlsafe(32),
            'ENCRYPTION_KEY': secrets.token_urlsafe(32),
            'DB_PASSWORD': self._generate_secure_password(),
            'GRAFANA_PASSWORD': self._generate_secure_password(16),
            'REDIS_PASSWORD': self._generate_secure_password(12),
        }

    def _generate_secure_password(self, length: int = 20) -> str:
        """Generate cryptographically secure password"""
        alphabet = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789!@#$%^&*"
        return ''.join(secrets.choice(alphabet) for _ in range(length))

    def create_secure_env_file(self, template_path: str, output_path: str,
                              custom_values: Optional[Dict[str, str]] = None) -> bool:
        """Create secure .env file from template"""
        try:
            template_file = Path(template_path)
            if not template_file.exists():
                raise FileNotFoundError(f"Template file not found: {template_path}")

            # Generate secure credentials
            secure_creds = self.generate_secure_credentials()
            if custom_values:
                secure_creds.update(custom_values)

            # Read template
            with open(template_file, 'r') as f:
                template_content = f.read()

            # Replace placeholders with secure values
            replacements = {
                'your-jwt-secret-key-here': secure_creds['JWT_SECRET_KEY'],
                'generate-secure-session-secret': secure_creds['SESSION_SECRET'],
                'your-secure-password': secure_creds['DB_PASSWORD'],
                'generate-secure-password': secure_creds['GRAFANA_PASSWORD'],
            }

            for placeholder, value in replacements.items():
                template_content = template_content.replace(placeholder, value)

            # Write secure .env file
            with open(output_path, 'w') as f:
                f.write(template_content)

            # Set secure file permissions (readable only by owner)
            os.chmod(output_path, 0o600)

            print(f"✅ Secure environment file created: {output_path}")
            return True

        except Exception as e:
            print(f"❌ Failed to create secure environment file: {e}")
            return False

class EnvironmentValidator:
    """Validate environment configuration"""

    def __init__(self):
        self.required_vars = [
            'DATABASE_URL', 'JWT_SECRET_KEY', 'GCP_PROJECT_ID'
        ]
        self.security_checks = [
            self._check_jwt_secret_strength,
            self._check_database_url_security,
            self._check_password_strength
        ]

    def validate_environment(self) -> Dict[str, Any]:
        """Comprehensive environment validation"""
        results = {
            'is_valid': True,
            'missing_vars': [],
            'security_issues': [],
            'warnings': []
        }

        # Check required variables
        for var in self.required_vars:
            if not os.getenv(var):
                results['missing_vars'].append(var)
                results['is_valid'] = False

        # Run security checks
        for check in self.security_checks:
            issues = check()
            results['security_issues'].extend(issues)
            if issues:
                results['is_valid'] = False

        return results

    def _check_jwt_secret_strength(self) -> list:
        """Check JWT secret key strength"""
        issues = []
        jwt_secret = os.getenv('JWT_SECRET_KEY')

        if jwt_secret:
            if len(jwt_secret) < 32:
                issues.append("JWT_SECRET_KEY too short (minimum 32 characters)")
            if jwt_secret in ['your-jwt-secret-key-here', 'secret']:
                issues.append("JWT_SECRET_KEY using default/weak value")

        return issues

    def _check_database_url_security(self) -> list:
        """Check database URL security"""
        issues = []
        db_url = os.getenv('DATABASE_URL')

        if db_url:
            if 'localhost' not in db_url and not db_url.startswith('postgresql://'):
                # Production database should use SSL
                if 'sslmode=' not in db_url:
                    issues.append("Production database should use SSL connection")

            # Check for weak passwords in URL
            if any(weak in db_url.lower() for weak in ['password', '123456', 'admin']):
                issues.append("Database URL contains potentially weak password")

        return issues

    def _check_password_strength(self) -> list:
        """Check password strength for various services"""
        issues = []
        password_vars = ['POSTGRES_PASSWORD', 'GRAFANA_PASSWORD', 'REDIS_PASSWORD']

        for var in password_vars:
            password = os.getenv(var)
            if password and len(password) < 12:
                issues.append(f"{var} is too short (minimum 12 characters)")

        return issues

def main():
    """Command line interface for secure environment management"""
    import argparse

    parser = argparse.ArgumentParser(description='Secure Environment Variable Manager')
    parser.add_argument('action', choices=['encrypt', 'decrypt', 'generate', 'validate'])
    parser.add_argument('--env-file', help='Path to .env file')
    parser.add_argument('--environment', default='production', help='Environment name')
    parser.add_argument('--template', help='Template file path')
    parser.add_argument('--output', help='Output file path')

    args = parser.parse_args()

    if args.action == 'encrypt':
        manager = SecureEnvManager()
        success = manager.encrypt_env_file(args.env_file, args.environment)
        exit(0 if success else 1)

    elif args.action == 'decrypt':
        manager = SecureEnvManager()
        env_vars = manager.decrypt_and_load_env(args.environment)
        print(f"Loaded {len(env_vars)} environment variables")

    elif args.action == 'generate':
        manager = SecureEnvManager()
        success = manager.create_secure_env_file(args.template, args.output)
        exit(0 if success else 1)

    elif args.action == 'validate':
        validator = EnvironmentValidator()
        results = validator.validate_environment()

        if results['is_valid']:
            print("✅ Environment configuration is valid")
        else:
            print("❌ Environment configuration has issues:")
            for issue in results['missing_vars']:
                print(f"  - Missing: {issue}")
            for issue in results['security_issues']:
                print(f"  - Security: {issue}")

if __name__ == "__main__":
    main()