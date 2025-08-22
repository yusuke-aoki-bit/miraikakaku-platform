# 共通のStockMasterモデルを使用
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '../../../shared'))

try:
    from shared.models.stock_master import StockMaster
except ImportError:
    # フォールバック: 元の定義
    from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text, Numeric
    from sqlalchemy.orm import relationship
    from datetime import datetime
    from .base import Base

    class StockMaster(Base):
        __tablename__ = "stock_master"
        
        id = Column(Integer, primary_key=True, autoincrement=True)
        symbol = Column(String(20), nullable=False, unique=True, index=True)
        name = Column(String(255), nullable=False)
        sector = Column(String(100))
        market = Column(String(50))
        country = Column(String(50), default='Japan')
        currency = Column(String(10), default='JPY')
        is_active = Column(Boolean, default=True)
        created_at = Column(DateTime, default=datetime.utcnow)
        updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
        
        price_history = relationship("StockPriceHistory", back_populates="stock", cascade="all, delete-orphan")
        predictions = relationship("StockPredictions", back_populates="stock", cascade="all, delete-orphan")

# 既存コードとの互換性のため
__all__ = ['StockMaster']