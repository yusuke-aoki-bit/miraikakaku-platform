# 共通のデータベース設定を使用
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '../../../shared'))

from config.database import get_db, init_database, SessionLocal, db_config
from sqlalchemy.orm import Session

# 既存コードとの互換性のため
engine = db_config.get_engine()

def get_db_session() -> Session:
    """データベースセッションを取得"""
    return SessionLocal()

def init_database_batch():
    """バッチ固有のデータベース初期化"""
    from .models import stock_master, stock_price_history, stock_predictions, ai_inference_log
    from shared.models.base import Base
    Base.metadata.create_all(bind=engine)