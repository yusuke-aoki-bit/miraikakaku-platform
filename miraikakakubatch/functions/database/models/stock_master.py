from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text, Numeric
from sqlalchemy.orm import relationship
from datetime import datetime
from .base import Base


class StockMaster(Base):
    __tablename__ = "stock_master"

    symbol = Column(String(20), primary_key=True, nullable=False, index=True)
    name = Column(String(300))
    exchange = Column(String(100))
    market = Column(String(50))
    sector = Column(String(150))
    industry = Column(String(150))
    country = Column(String(100))
    website = Column(String(255))
    description = Column(Text)
    currency = Column(String(10))
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow)

    price_history = relationship(
        "StockPriceHistory", back_populates="stock", cascade="all, delete-orphan"
    )
    predictions = relationship(
        "StockPredictions", back_populates="stock", cascade="all, delete-orphan"
    )


# 既存コードとの互換性のため
__all__ = ["StockMaster"]
