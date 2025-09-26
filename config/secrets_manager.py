"""
Google Secret Manager integration for secure credential management
"""
import os
import json
from typing import Optional, Dict, Any
from google.cloud import secretmanager
import logging

logger = logging.getLogger(__name__)


class SecretsManager:
    """Manages secrets using Google Secret Manager"""

    def __init__(self, project_id: Optional[str] = None):
        self.project_id = project_id or os.getenv('GCP_PROJECT_ID')
        self.client = None
        self._cache: Dict[str, Any] = {}

        if self.project_id:
            try:
                self.client = secretmanager.SecretManagerServiceClient()
            except Exception as e:
                logger.warning(f"Failed to initialize Secret Manager client: {e}")

    def get_secret(self, secret_id: str, version: str = "latest") -> Optional[str]:
        """Retrieve a secret from Google Secret Manager"""

        # Check cache first
        cache_key = f"{secret_id}:{version}"
        if cache_key in self._cache:
            return self._cache[cache_key]

        # Try to get from Secret Manager
        if self.client and self.project_id:
            try:
                name = f"projects/{self.project_id}/secrets/{secret_id}/versions/{version}"
                response = self.client.access_secret_version(request={"name": name})
                secret_value = response.payload.data.decode("UTF-8")
                self._cache[cache_key] = secret_value
                return secret_value
            except Exception as e:
                logger.error(f"Failed to retrieve secret {secret_id}: {e}")

        # Fallback to environment variable
        env_value = os.getenv(secret_id.upper().replace('-', '_'))
        if env_value:
            logger.info(f"Using environment variable for {secret_id}")
            return env_value

        return None

    def get_database_config(self) -> Dict[str, str]:
        """Get database configuration from secrets"""
        return {
            'host': self.get_secret('db-host') or os.getenv('POSTGRES_HOST', 'localhost'),
            'port': self.get_secret('db-port') or os.getenv('POSTGRES_PORT', '5432'),
            'database': self.get_secret('db-name') or os.getenv('POSTGRES_DB', 'miraikakaku'),
            'user': self.get_secret('db-user') or os.getenv('POSTGRES_USER', 'postgres'),
            'password': self.get_secret('db-password') or os.getenv('POSTGRES_PASSWORD', ''),
        }

    def get_jwt_config(self) -> Dict[str, Any]:
        """Get JWT configuration from secrets"""
        return {
            'secret_key': self.get_secret('jwt-secret-key') or os.getenv('JWT_SECRET_KEY', ''),
            'algorithm': self.get_secret('jwt-algorithm') or os.getenv('JWT_ALGORITHM', 'HS256'),
            'expiration_hours': int(self.get_secret('jwt-expiration') or os.getenv('JWT_EXPIRATION_HOURS', '24')),
        }

    def get_api_keys(self) -> Dict[str, str]:
        """Get external API keys from secrets"""
        return {
            'alpha_vantage': self.get_secret('alpha-vantage-api-key') or os.getenv('ALPHA_VANTAGE_API_KEY', ''),
            'polygon': self.get_secret('polygon-api-key') or os.getenv('POLYGON_API_KEY', ''),
            'yahoo_finance': self.get_secret('yahoo-finance-api-key') or os.getenv('YAHOO_FINANCE_API_KEY', ''),
        }


# Singleton instance
secrets_manager = SecretsManager()