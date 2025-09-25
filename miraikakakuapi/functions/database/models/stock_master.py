from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text, Numeric, BigInteger, Float
from sqlalchemy.orm import relationship
from datetime import datetime
from .base import Base


class StockMaster(Base):
    __tablename__ = "stock_master"

    symbol = Column(String(20), primary_key=True, nullable=False, index=True)
    name = Column(String(300))
    long_name = Column(String(500))
    exchange = Column(String(100))
    market = Column(String(50))
    sector = Column(String(150))
    industry = Column(String(150))
    country = Column(String(100))
    website = Column(String(500))
    description = Column(Text)
    business_summary = Column(Text)
    currency = Column(String(10))

    # Financial Information
    market_cap = Column(BigInteger)
    enterprise_value = Column(BigInteger)
    enterprise_to_revenue = Column(Float)
    enterprise_to_ebitda = Column(Float)
    employees = Column(Integer)

    # Valuation Metrics
    trailing_pe = Column(Float)
    forward_pe = Column(Float)
    peg_ratio = Column(Float)
    price_to_sales_trailing_12months = Column(Float)
    price_to_book = Column(Float)

    # Financial Ratios
    profit_margins = Column(Float)
    operating_margins = Column(Float)
    return_on_assets = Column(Float)
    return_on_equity = Column(Float)
    revenue_per_share = Column(Float)

    # Growth Metrics
    revenue_growth = Column(Float)
    earnings_growth = Column(Float)
    earnings_quarterly_growth = Column(Float)

    # Dividend Information
    dividend_rate = Column(Float)
    dividend_yield = Column(Float)
    payout_ratio = Column(Float)

    # Cash and Debt
    total_cash = Column(BigInteger)
    total_cash_per_share = Column(Float)
    total_debt = Column(BigInteger)
    debt_to_equity = Column(Float)
    current_ratio = Column(Float)
    quick_ratio = Column(Float)

    # Trading Information
    beta = Column(Float)
    fifty_two_week_low = Column(Float)
    fifty_two_week_high = Column(Float)
    fifty_day_average = Column(Float)
    two_hundred_day_average = Column(Float)

    # Volume and Shares
    average_volume = Column(BigInteger)
    average_volume_10days = Column(BigInteger)
    shares_outstanding = Column(BigInteger)
    float_shares = Column(BigInteger)
    held_percent_insiders = Column(Float)
    held_percent_institutions = Column(Float)

    # Technical Indicators (captured from yfinance)
    recommendation_mean = Column(Float)
    recommendation_key = Column(String(20))
    number_of_analyst_opinions = Column(Integer)

    # Additional Information
    time_zone = Column(String(50))
    uuid = Column(String(100))

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
