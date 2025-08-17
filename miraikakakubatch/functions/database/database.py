from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", "mysql+pymysql://user:password@localhost:3306/miraikakaku")

engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,
    pool_recycle=300,
    echo=os.getenv("LOG_LEVEL") == "DEBUG"
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db_session() -> Session:
    """データベースセッションを取得"""
    return SessionLocal()

def init_database():
    """データベースを初期化"""
    from .models import stock_master, stock_price_history, stock_predictions, ai_inference_log
    Base.metadata.create_all(bind=engine)