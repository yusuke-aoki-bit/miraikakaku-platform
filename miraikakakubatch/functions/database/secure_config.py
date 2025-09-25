"""
Secure Database Configuration using Google Secret Manager
"""
import os
from typing import Dict, Optional
from google.cloud import secretmanager
import logging

logger = logging.getLogger(__name__)

class SecureDBConfig:
    """Secure database configuration manager using Secret Manager"""

    def __init__(self, project_id: Optional[str] = None):
        self.project_id = project_id or os.getenv('GOOGLE_CLOUD_PROJECT', '465603676610')
        self.client = secretmanager.SecretManagerServiceClient()
        self._config_cache = {}

    def get_secret(self, secret_name: str) -> str:
        """Retrieve secret from Secret Manager with caching"""
        if secret_name in self._config_cache:
            return self._config_cache[secret_name]

        try:
            secret_path = f"projects/{self.project_id}/secrets/{secret_name}/versions/latest"
            response = self.client.access_secret_version(request={"name": secret_path})
            secret_value = response.payload.data.decode("UTF-8")

            # Cache for session (not persistent)
            self._config_cache[secret_name] = secret_value
            logger.info(f"Successfully retrieved secret: {secret_name}")
            return secret_value

        except Exception as e:
            logger.error(f"Failed to retrieve secret {secret_name}: {e}")
            # Fallback to environment variables for local development
            fallback_value = os.getenv(f"DB_{secret_name.upper().replace('-', '_')}")
            if fallback_value:
                logger.warning(f"Using fallback environment variable for {secret_name}")
                return fallback_value
            raise

    def get_db_config(self) -> Dict[str, str]:
        """Get complete database configuration from Secret Manager"""
        try:
            config = {
                "host": self.get_secret("db-host"),
                "user": self.get_secret("db-user"),
                "password": self.get_secret("db-password"),
                "database": self.get_secret("db-name"),
                "port": 5432
            }
            logger.info("Database configuration loaded securely from Secret Manager")
            return config

        except Exception as e:
            logger.error(f"Failed to load secure database config: {e}")
            # Emergency fallback for critical operations
            logger.warning("Using emergency fallback configuration")
            return {
                "host": os.getenv("DB_HOST", "localhost"),
                "user": os.getenv("DB_USER", "postgres"),
                "password": os.getenv("DB_PASSWORD", ""),
                "database": os.getenv("DB_NAME", "miraikakaku"),
                "port": 5432
            }

    def get_database_url(self) -> str:
        """Get PostgreSQL connection URL"""
        config = self.get_db_config()
        return f"postgresql://{config['user']}:{config['password']}@{config['host']}:{config['port']}/{config['database']}"

# Global instance for easy import
secure_config = SecureDBConfig()

def get_secure_db_config() -> Dict[str, str]:
    """Convenience function to get secure database configuration"""
    return secure_config.get_db_config()

def get_secure_database_url() -> str:
    """Convenience function to get secure database URL"""
    return secure_config.get_database_url()