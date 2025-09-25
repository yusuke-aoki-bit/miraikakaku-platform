#!/usr/bin/env python3
"""
統一データベース設定管理
安全な認証情報管理のための中央化されたモジュール
"""

import os
import sys
import logging
from typing import Dict, Optional

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SecureDatabaseConfig:
    """安全なデータベース設定管理"""

    def __init__(self):
        self.use_secret_manager = os.getenv('USE_SECRET_MANAGER', 'false').lower() == 'true'
        self.project_id = os.getenv('GCP_PROJECT_ID', 'pricewise-huqkr')

    def get_database_config(self) -> Dict[str, str]:
        """データベース設定を安全に取得"""

        # Google Secret Manager使用時
        if self.use_secret_manager:
            try:
                from google.cloud import secretmanager

                client = secretmanager.SecretManagerServiceClient()

                # Secret Managerから認証情報を取得
                def get_secret(secret_name: str) -> str:
                    name = f"projects/{self.project_id}/secrets/{secret_name}/versions/latest"
                    try:
                        response = client.access_secret_version(request={"name": name})
                        return response.payload.data.decode("UTF-8")
                    except Exception as e:
                        logger.warning(f"Secret {secret_name} not found: {e}")
                        return None

                db_password = get_secret('db-password')

                if db_password:
                    return {
                        'host': os.getenv('DB_HOST', '34.173.9.214'),
                        'port': int(os.getenv('DB_PORT', '5432')),
                        'database': os.getenv('DB_NAME', 'miraikakaku'),
                        'user': os.getenv('DB_USER', 'postgres'),
                        'password': db_password
                    }

            except ImportError:
                logger.warning("Google Cloud Secret Manager not available, falling back to environment variables")

        # 環境変数からのフォールバック（本番環境では必須）
        db_password = os.getenv('DB_PASSWORD')

        if not db_password:
            logger.error("⚠️  データベースパスワードが設定されていません！")
            logger.error("   環境変数 DB_PASSWORD を設定するか、Google Secret Manager を使用してください。")
            logger.error("   セキュリティ上の理由により、デフォルト値は提供されません。")
            sys.exit(1)

        return {
            'host': os.getenv('DB_HOST', '34.173.9.214'),
            'port': int(os.getenv('DB_PORT', '5432')),
            'database': os.getenv('DB_NAME', 'miraikakaku'),
            'user': os.getenv('DB_USER', 'postgres'),
            'password': db_password
        }

    def get_connection_string(self) -> str:
        """PostgreSQL接続文字列を取得"""
        config = self.get_database_config()

        return f"postgresql://{config['user']}:{config['password']}@{config['host']}:{config['port']}/{config['database']}"

    def get_psycopg2_params(self) -> Dict[str, any]:
        """psycopg2用の接続パラメータを取得"""
        config = self.get_database_config()

        return {
            'host': config['host'],
            'port': config['port'],
            'database': config['database'],
            'user': config['user'],
            'password': config['password'],
            'sslmode': 'require'  # セキュリティ強化
        }

    def get_sqlalchemy_url(self) -> str:
        """SQLAlchemy用のURL文字列を取得"""
        config = self.get_database_config()

        return f"postgresql+psycopg2://{config['user']}:{config['password']}@{config['host']}:{config['port']}/{config['database']}?sslmode=require"

# グローバルインスタンス
db_config = SecureDatabaseConfig()

def get_db_config() -> Dict[str, str]:
    """データベース設定を取得する便利関数"""
    return db_config.get_database_config()

def get_db_connection_string() -> str:
    """データベース接続文字列を取得する便利関数"""
    return db_config.get_connection_string()

def get_db_psycopg2_params() -> Dict[str, any]:
    """psycopg2接続パラメータを取得する便利関数"""
    return db_config.get_psycopg2_params()

def get_db_sqlalchemy_url() -> str:
    """SQLAlchemy URL を取得する便利関数"""
    return db_config.get_sqlalchemy_url()

if __name__ == "__main__":
    # テスト実行
    try:
        config = get_db_config()
        logger.info("✅ データベース設定の取得に成功")
        logger.info(f"   Host: {config['host']}")
        logger.info(f"   Database: {config['database']}")
        logger.info(f"   User: {config['user']}")
        logger.info(f"   Password: {'*' * len(config['password'])}")
    except Exception as e:
        logger.error(f"❌ データベース設定の取得に失敗: {e}")
        sys.exit(1)