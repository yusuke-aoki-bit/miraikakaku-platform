from sqlalchemy import Column, Integer, String, DateTime, Numeric, ForeignKey, Index
from sqlalchemy.orm import relationship
from datetime import datetime
from .base import Base


class StockPriceHistory(Base):
    __tablename__ = "stock_prices"

    id = Column(Integer, primary_key=True, index=True)
    symbol = Column(
        String(20), ForeignKey("stock_master.symbol"), nullable=False, index=True
    )
    date = Column(DateTime, nullable=False, index=True)
    open_price = Column(Numeric(12, 4))
    high_price = Column(Numeric(12, 4))
    low_price = Column(Numeric(12, 4))
    close_price = Column(Numeric(12, 4), nullable=False)
    adjusted_close = Column(Numeric(12, 4))
    volume = Column(Integer)
    # data_source = Column(String(50), default="yfinance")  # 実際のDBには存在しない
    created_at = Column(DateTime, default=datetime.utcnow)

    # インデックスの作成
    __table_args__ = (
        Index("idx_symbol_date", "symbol", "date"),
        Index("idx_date_symbol", "date", "symbol"),
    )

    # リレーションシップ
    stock = relationship("StockMaster", back_populates="price_history")
