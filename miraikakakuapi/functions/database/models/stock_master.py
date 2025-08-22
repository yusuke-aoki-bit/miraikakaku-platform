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
        
        symbol = Column(String(20), primary_key=True, index=True, nullable=False)
        name = Column(String(200), nullable=False)
        exchange = Column(String(255))
        sector = Column(String(100))
        industry = Column(String(100))
        country = Column(String(50))
        website = Column(String(200))
        description = Column(Text)
        is_active = Column(Boolean, default=True)
        created_at = Column(DateTime, default=datetime.utcnow)
        updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
        
        price_history = relationship("StockPriceHistory", back_populates="stock", cascade="all, delete-orphan")
        predictions = relationship("StockPredictions", back_populates="stock", cascade="all, delete-orphan")

# 既存コードとの互換性のため
__all__ = ['StockMaster']