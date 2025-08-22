"""
Cloud SQL専用データベース設定
SQLiteフォールバックなし
"""

import os
import logging
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.pool import NullPool
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

Base = declarative_base()

class CloudSQLConnection:
    """Cloud SQL専用接続マネージャー"""
    
    def __init__(self):
        self.engine = None
        self.SessionLocal = None
        self._initialize_connection()
    
    def _initialize_connection(self):
        """Cloud SQL接続の初期化"""
        try:
            # 環境変数から接続情報取得
            if os.getenv('GAE_ENV', '').startswith('standard'):
                # App Engine本番環境
                unix_socket = f"/cloudsql/{os.environ['CLOUD_SQL_CONNECTION_NAME']}"
                connection_string = (
                    f"mysql+pymysql://root:{os.environ['CLOUD_SQL_PASSWORD']}@/"
                    f"miraikakaku_prod?unix_socket={unix_socket}"
                )
            else:
                # ローカル開発環境 or Cloud Run
                host = os.getenv('CLOUD_SQL_HOST', '34.58.103.36')
                password = os.getenv('CLOUD_SQL_PASSWORD', 'Yuuku717')
                connection_string = (
                    f"mysql+pymysql://root:{password}@{host}:3306/miraikakaku_prod"
                )
            
            # エンジン作成
            self.engine = create_engine(
                connection_string,
                poolclass=NullPool,  # Cloud SQLでは接続プールを無効化
                echo=os.getenv("LOG_LEVEL") == "DEBUG",
                connect_args={
                    "connect_timeout": 30,
                    "charset": "utf8mb4"
                }
            )
            
            # セッション作成
            self.SessionLocal = sessionmaker(
                autocommit=False,
                autoflush=False,
                bind=self.engine
            )
            
            # 接続テスト
            with self.engine.connect() as conn:
                result = conn.execute(text("SELECT 1"))
                logger.info("✅ Cloud SQL接続成功")
                
        except Exception as e:
            logger.error(f"❌ Cloud SQL接続エラー: {e}")
            raise Exception(f"Cloud SQLへの接続に失敗しました: {e}")
    
    def get_db(self):
        """データベースセッション取得"""
        if not self.SessionLocal:
            raise Exception("データベース接続が初期化されていません")
        
        db = self.SessionLocal()
        try:
            yield db
        finally:
            db.close()
    
    def get_engine(self):
        """エンジン取得"""
        if not self.engine:
            raise Exception("データベースエンジンが初期化されていません")
        return self.engine

# グローバルインスタンス
db_connection = CloudSQLConnection()

# 便利な関数をエクスポート
get_db = db_connection.get_db
get_engine = db_connection.get_engine

def init_database():
    """データベース初期化（テーブル作成）"""
    from database.models import (
        StockMaster, 
        StockPrices, 
        StockPredictions,
        BatchLogs,
        AIInferenceLog
    )
    
    try:
        Base.metadata.create_all(bind=db_connection.engine)
        logger.info("✅ データベーステーブル初期化完了")
    except Exception as e:
        logger.error(f"❌ テーブル初期化エラー: {e}")
        raise

def test_connection():
    """接続テスト"""
    try:
        db = next(get_db())
        result = db.execute(text("SELECT COUNT(*) FROM stock_master"))
        count = result.scalar()
        logger.info(f"✅ 接続テスト成功: {count}銘柄")
        return True
    except Exception as e:
        logger.error(f"❌ 接続テスト失敗: {e}")
        return False