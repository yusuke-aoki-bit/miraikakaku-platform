from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime

Base = declarative_base()

class StockMaster(Base):
    __tablename__ = "stock_master"
    
    id = Column(Integer, primary_key=True, index=True)
    symbol = Column(String(20), unique=True, index=True, nullable=False)
    company_name = Column(String(255), nullable=False)
    exchange = Column(String(50), nullable=False)
    sector = Column(String(100))
    industry = Column(String(100))
    market_cap = Column(String(50))
    currency = Column(String(10), default="USD")
    country = Column(String(50), default="US")
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    description = Column(Text)
    
    # リレーションシップ
    price_history = relationship("StockPriceHistory", back_populates="stock")
    predictions = relationship("StockPredictions", back_populates="stock")