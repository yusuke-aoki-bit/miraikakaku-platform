#!/usr/bin/env python3
"""
本番環境用データベース設定最適化
Production Database Configuration Optimization

Cloud SQL接続問題の解決とパフォーマンス最適化
"""

import os
import logging
from typing import Dict, Any, Optional
from sqlalchemy import create_engine, MetaData
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import QueuePool
import json

logger = logging.getLogger(__name__)

class ProductionDBConfig:
    """本番環境データベース設定管理"""

    def __init__(self):
        self.connection_name = "pricewise-huqkr:us-central1:miraikakaku-postgres"
        self.database_name = "miraikakaku"
        self.username = "postgres"

    def get_cloud_sql_config(self) -> Dict[str, Any]:
        """Cloud SQL最適化設定を取得"""
        return {
            # 接続プール設定
            'pool_size': 10,
            'max_overflow': 20,
            'pool_pre_ping': True,
            'pool_recycle': 3600,  # 1時間

            # タイムアウト設定
            'connect_timeout': 60,
            'tcp_keepalives_idle': 600,
            'tcp_keepalives_interval': 30,
            'tcp_keepalives_count': 3,

            # SSL設定
            'sslmode': 'require',
        }

    def get_unix_socket_url(self) -> str:
        """Unix Socket接続URL（Cloud Run用）"""
        password = os.environ.get('DB_PASSWORD', 'os.getenv('DB_PASSWORD', '')')
        return (
            f"postgresql+psycopg2://{self.username}:{password}@/"
            f"{self.database_name}?host=/cloudsql/{self.connection_name}"
        )

    def get_tcp_connection_url(self) -> str:
        """TCP接続URL（フォールバック用）"""
        password = os.environ.get('DB_PASSWORD', 'os.getenv('DB_PASSWORD', '')')
        host = os.environ.get('DB_HOST', '34.173.9.214')  # Cloud SQL Public IP
        return (
            f"postgresql+psycopg2://{self.username}:{password}@{host}:5432/"
            f"{self.database_name}"
        )

    def create_optimized_engine(self):
        """最適化されたSQLAlchemyエンジンを作成"""
        config = self.get_cloud_sql_config()

        # Cloud Run環境の検出
        is_cloud_run = os.environ.get('K_SERVICE') is not None

        if is_cloud_run:
            # Cloud Run: Unix Socket接続
            database_url = self.get_unix_socket_url()
            logger.info("Using Cloud Run Unix Socket connection")
        else:
            # ローカル開発: TCP接続
            database_url = self.get_tcp_connection_url()
            logger.info("Using TCP connection for local development")

        # PostgreSQL固有のパラメーターをconnect_argsに移動
        connect_args = {
            'connect_timeout': config.pop('connect_timeout'),
            'options': f"-c tcp_keepalives_idle={config.pop('tcp_keepalives_idle')} "
                      f"-c tcp_keepalives_interval={config.pop('tcp_keepalives_interval')} "
                      f"-c tcp_keepalives_count={config.pop('tcp_keepalives_count')}",
            'sslmode': config.pop('sslmode')
        }

        try:
            engine = create_engine(
                database_url,
                poolclass=QueuePool,
                connect_args=connect_args,
                **config,
                echo=False  # 本番環境ではログ無効化
            )

            # 接続テスト
            with engine.connect() as conn:
                from sqlalchemy import text
                conn.execute(text("SELECT 1"))
                logger.info("Database connection test successful")

            return engine

        except Exception as e:
            logger.error(f"Primary connection failed: {e}")

            # フォールバック: TCP接続を試行
            if is_cloud_run:
                logger.info("Attempting TCP fallback connection")
                try:
                    # フォールバック用の設定を再構築
                    fallback_config = self.get_cloud_sql_config()
                    fallback_connect_args = {
                        'connect_timeout': fallback_config.pop('connect_timeout'),
                        'options': f"-c tcp_keepalives_idle={fallback_config.pop('tcp_keepalives_idle')} "
                                  f"-c tcp_keepalives_interval={fallback_config.pop('tcp_keepalives_interval')} "
                                  f"-c tcp_keepalives_count={fallback_config.pop('tcp_keepalives_count')}",
                        'sslmode': fallback_config.pop('sslmode')
                    }

                    fallback_engine = create_engine(
                        self.get_tcp_connection_url(),
                        poolclass=QueuePool,
                        connect_args=fallback_connect_args,
                        **fallback_config,
                        echo=False
                    )

                    with fallback_engine.connect() as conn:
                        from sqlalchemy import text
                        conn.execute(text("SELECT 1"))
                        logger.info("Fallback TCP connection successful")

                    return fallback_engine

                except Exception as fallback_error:
                    logger.error(f"Fallback connection also failed: {fallback_error}")

            raise e

    def get_health_check_query(self) -> str:
        """ヘルスチェック用クエリ"""
        return """
        SELECT
            'healthy' as status,
            current_timestamp as timestamp,
            current_database() as database,
            current_user as user,
            version() as version
        """

    def test_connection(self, engine) -> Dict[str, Any]:
        """データベース接続テスト"""
        try:
            from sqlalchemy import text
            with engine.connect() as conn:
                result = conn.execute(text(self.get_health_check_query())).fetchone()
                return {
                    'status': 'connected',
                    'database': result.database,
                    'user': result.user,
                    'timestamp': result.timestamp.isoformat(),
                    'version': result.version[:50] + '...' if len(result.version) > 50 else result.version
                }
        except Exception as e:
            return {
                'status': 'error',
                'message': str(e),
                'timestamp': None
            }

def get_production_db_engine():
    """本番環境用データベースエンジンを取得"""
    config = ProductionDBConfig()
    return config.create_optimized_engine()

def get_production_session_maker():
    """本番環境用セッションメーカーを取得"""
    engine = get_production_db_engine()
    return sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 環境変数設定の推奨事項
RECOMMENDED_ENV_VARS = {
    'DB_PASSWORD': 'データベースパスワード（Secret Manager推奨）',
    'DB_HOST': 'Cloud SQL Public IP（TCP接続用）',
    'GOOGLE_CLOUD_PROJECT': 'pricewise-huqkr',
    'K_SERVICE': 'Cloud Runサービス名（自動設定）'
}

if __name__ == "__main__":
    # 設定テスト
    logging.basicConfig(level=logging.INFO)
    config = ProductionDBConfig()

    try:
        engine = config.create_optimized_engine()
        health = config.test_connection(engine)
        print("✅ Production DB Configuration Test:")
        print(json.dumps(health, indent=2, default=str))
    except Exception as e:
        print(f"❌ Configuration test failed: {e}")