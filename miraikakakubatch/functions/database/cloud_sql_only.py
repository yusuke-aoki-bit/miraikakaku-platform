"""
Cloud SQL専用データベース設定（Batchサービス用）
SQLiteフォールバックなし
"""

import os
import logging
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.pool import NullPool
from dotenv import load_dotenv
import pymysql

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

Base = declarative_base()


class CloudSQLConnection:
    """Cloud SQL専用接続マネージャー（Batch用）"""

    def __init__(self):
        self.engine = None
        self.SessionLocal = None
        self._initialize_connection()

    def _initialize_connection(self):
        """Cloud SQL接続の初期化"""
        try:
            # 環境変数から接続情報取得
            if os.getenv("GAE_ENV", "").startswith("standard"):
                # App Engine本番環境
                unix_socket = f"/cloudsql/{os.environ['CLOUD_SQL_CONNECTION_NAME']}"
                connection_string = (
                    f"mysql+pymysql://root:{os.environ['CLOUD_SQL_PASSWORD']}@/"
                    f"miraikakaku_prod?unix_socket={unix_socket}"
                )
            else:
                # ローカル開発環境 or Cloud Run
                host = os.getenv("CLOUD_SQL_HOST", "34.58.103.36")
                password = os.getenv("CLOUD_SQL_PASSWORD", "Yuuku717")
                connection_string = (
                    f"mysql+pymysql://root:{password}@{host}:3306/miraikakaku_prod"
                )

            # エンジン作成
            self.engine = create_engine(
                connection_string,
                poolclass=NullPool,  # Cloud SQLでは接続プールを無効化
                echo=os.getenv("LOG_LEVEL") == "DEBUG",
                connect_args={"connect_timeout": 30, "charset": "utf8mb4"},
            )

            # セッション作成
            self.SessionLocal = sessionmaker(
                autocommit=False, autoflush=False, bind=self.engine
            )

            # 接続テスト
            with self.engine.connect() as conn:
                result = conn.execute(text("SELECT 1"))
                logger.info("✅ Batch: Cloud SQL接続成功")

        except Exception as e:
            logger.error(f"❌ Batch: Cloud SQL接続エラー: {e}")
            raise Exception(f"Cloud SQLへの接続に失敗しました: {e}")

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
