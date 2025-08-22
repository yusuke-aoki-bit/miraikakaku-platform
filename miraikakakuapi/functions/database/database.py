# フォールバック可能なデータベース設定
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '../../../shared'))

try:
    from shared.config.database import get_db, init_database, SessionLocal, db_config
    engine = db_config.get_engine()
except ImportError:
    # フォールバック: 元の設定
    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker
    from dotenv import load_dotenv
    
    load_dotenv()
    
    DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./miraikakaku.db")
    
    engine = create_engine(
        DATABASE_URL,
        pool_pre_ping=True,
        pool_recycle=300,
        echo=os.getenv("LOG_LEVEL") == "DEBUG",
        connect_args={"check_same_thread": False} if "sqlite" in DATABASE_URL else {}
    )
    
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    
    def get_db():
        db = SessionLocal()
        try:
            yield db
        finally:
            db.close()

async def init_database():
    """API固有のデータベース初期化"""
    from .models import Base, StockMaster, StockPriceHistory, StockPredictions, AIInferenceLog
    Base.metadata.create_all(bind=engine)