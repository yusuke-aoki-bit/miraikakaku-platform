from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
import os
from dotenv import load_dotenv

load_dotenv()

# 共通のベースクラス
Base = declarative_base()

class DatabaseConfig:
    """統一されたデータベース設定クラス"""
    
    def __init__(self):
        self.database_url = os.getenv("DATABASE_URL", "sqlite:///./miraikakaku.db")
        self.pool_pre_ping = True
        self.pool_recycle = 300
        self.echo = os.getenv("LOG_LEVEL") == "DEBUG"
        
    def get_engine(self):
        """データベースエンジンを取得"""
        connect_args = {}
        if "sqlite" in self.database_url:
            connect_args["check_same_thread"] = False
            
        return create_engine(
            self.database_url,
            pool_pre_ping=self.pool_pre_ping,
            pool_recycle=self.pool_recycle,
            echo=self.echo,
            connect_args=connect_args
        )
    
    def get_session_local(self):
        """セッションローカルを取得"""
        engine = self.get_engine()
        return sessionmaker(autocommit=False, autoflush=False, bind=engine)

# グローバルなデータベース設定インスタンス
db_config = DatabaseConfig()
SessionLocal = db_config.get_session_local()

def get_db():
    """データベースセッションを取得"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def init_database():
    """データベースを初期化"""
    engine = db_config.get_engine()
    Base.metadata.create_all(bind=engine)