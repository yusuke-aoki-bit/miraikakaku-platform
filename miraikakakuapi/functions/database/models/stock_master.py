from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text, Numeric
from sqlalchemy.orm import relationship
from datetime import datetime
from .base import Base

class StockMaster(Base):
    __tablename__ = "stock_master"
    
    id = Column(Integer, primary_key=True, index=True)
    symbol = Column(String(20), unique=True, index=True, nullable=False)
    company_name = Column(String(255), nullable=False)
    exchange = Column(String(50), nullable=False)
    sector = Column(String(100))
    industry = Column(String(100))
    market_cap = Column(Numeric(15, 2))  # 時価総額
    currency = Column(String(10), default="USD")
    country = Column(String(50), default="US")
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    description = Column(Text)
    
    # 財務データ
    pe_ratio = Column(Numeric(8, 2))  # PER
    dividend_yield = Column(Numeric(5, 4))  # 配当利回り
    beta = Column(Numeric(6, 4))  # ベータ値
    
    # リレーションシップ
    price_history = relationship("StockPriceHistory", back_populates="stock", cascade="all, delete-orphan")
    predictions = relationship("StockPredictions", back_populates="stock", cascade="all, delete-orphan")