"""
PostgreSQL Cloud SQL専用データベース設定（Batchサービス用）
SQLiteフォールバックなし、MySQL廃止
"""

import os
import logging
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.pool import NullPool
from dotenv import load_dotenv
from google.cloud.sql.connector import Connector
import pg8000

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

Base = declarative_base()


class CloudSQLConnection:
    """PostgreSQL Cloud SQL専用接続マネージャー（Batch用）"""

    def __init__(self):
        self.connector = None
        self.engine = None
        self.SessionLocal = None
        self._initialize_connection()

    def _initialize_connection(self):
        """PostgreSQL Cloud SQL接続の初期化"""
        try:
            # PostgreSQL接続情報
            project_id = os.getenv("GCP_PROJECT_ID", "pricewise-huqkr")
            region = os.getenv("CLOUD_SQL_REGION", "us-central1")
            instance_name = os.getenv("CLOUD_SQL_INSTANCE", "miraikakaku-postgres")
            database_name = os.getenv("POSTGRES_DATABASE", "miraikakaku")
            db_user = os.getenv("POSTGRES_USER", "postgres")
            db_password = os.getenv("POSTGRES_PASSWORD", "miraikakaku-postgres-secure-2024")

            # Cloud SQL Connectorを使用
            self.connector = Connector()

            def get_conn():
                conn = self.connector.connect(
                    f"{project_id}:{region}:{instance_name}",
                    "pg8000",
                    user=db_user,
                    password=db_password,
                    db=database_name,
                )
                return conn

            # PostgreSQL SQLAlchemy エンジンの作成
            self.engine = create_engine(
                "postgresql+pg8000://",
                creator=get_conn,
                poolclass=NullPool,  # Cloud SQLでは接続プールを無効化
                echo=os.getenv("LOG_LEVEL") == "DEBUG",
            )

            # セッション作成
            self.SessionLocal = sessionmaker(
                autocommit=False, autoflush=False, bind=self.engine
            )

            # 接続テスト
            with self.engine.connect() as conn:
                result = conn.execute(text("SELECT 1"))
                logger.info("✅ Batch: PostgreSQL Cloud SQL接続成功")

        except Exception as e:
            logger.error(f"❌ Batch: PostgreSQL Cloud SQL接続エラー: {e}")
            raise Exception(f"PostgreSQL Cloud SQLへの接続に失敗しました: {e}")

    def get_session(self):
        """データベースセッション取得"""
        if not self.SessionLocal:
            raise Exception("データベース接続が初期化されていません")
        return self.SessionLocal()

    def execute_query(self, query: str, params: dict = None):
        """クエリ実行"""
        with self.engine.connect() as conn:
            result = conn.execute(text(query), params or {})
            conn.commit()
            return result

    def bulk_insert(self, table: str, data: list):
        """バルクインサート"""
        if not data:
            return

        with self.engine.connect() as conn:
            # データからカラム名を取得
            columns = list(data[0].keys())

            # プレースホルダー作成
            placeholders = ", ".join([f":{col}" for col in columns])

            # INSERT文生成
            query = f"""
                INSERT INTO {table} ({', '.join(columns)})
                VALUES ({placeholders})
            """

            # バッチ実行
            for batch in self._batch_data(data, 100):
                conn.execute(text(query), batch)
            conn.commit()

            logger.info(f"✅ {table}に{len(data)}件のデータを挿入")

    def _batch_data(self, data: list, batch_size: int):
        """データをバッチに分割"""
        for i in range(0, len(data), batch_size):
            yield data[i : i + batch_size]

    def get_stock_count(self):
        """銘柄数取得"""
        result = self.execute_query("SELECT COUNT(*) FROM stock_master")
        return result.scalar()

    def close_connection(self):
        """接続をクローズ"""
        if self.connector:
            self.connector.close()


# グローバルインスタンス
db = CloudSQLConnection()


def get_db_session():
    """セッション取得関数"""
    return db.get_session()


def test_connection():
    """接続テスト"""
    try:
        count = db.get_stock_count()
        logger.info(f"✅ Batch接続テスト成功: {count}銘柄")
        return True
    except Exception as e:
        logger.error(f"❌ Batch接続テスト失敗: {e}")
        return False
