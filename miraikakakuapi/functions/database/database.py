# 共通のデータベース設定を使用
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '../../../shared'))

from config.database import get_db, init_database, SessionLocal, db_config

# 既存コードとの互換性のため
engine = db_config.get_engine()

async def init_database_api():
    """API固有のデータベース初期化"""
    from .models import Base, StockMaster, StockPriceHistory, StockPredictions, AIInferenceLog
    Base.metadata.create_all(bind=engine)