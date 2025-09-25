from sqlalchemy import (
    Column,
    Integer,
    String,
    DateTime,
    Numeric,
    ForeignKey,
    Text,
    Boolean,
)
from sqlalchemy.orm import relationship
from datetime import datetime
from .base import Base


class StockPredictions(Base):
    __tablename__ = "stock_predictions"

    id = Column(Integer, primary_key=True, index=True)
    symbol = Column(
        String(20), ForeignKey("stock_master.symbol"), nullable=False, index=True
    )
    prediction_date = Column(DateTime, nullable=False, index=True)
    target_date = Column(DateTime, nullable=False)
    predicted_price = Column(Numeric(12, 4), nullable=False)
    current_price = Column(Numeric(12, 4))  # Current price at time of prediction
    predicted_change = Column(Numeric(12, 4))  # Absolute change predicted
    predicted_change_percent = Column(Numeric(8, 4))  # Percentage change predicted
    confidence_score = Column(Numeric(5, 4))
    prediction_type = Column(String(50), default="daily")  # 'daily', 'weekly', 'monthly'
    model_name = Column(String(100), nullable=False)
    model_version = Column(String(50))
    model_type = Column(String(50))  # Type of model used
    features_used = Column(Text)  # JSON形式で使用した特徴量を保存
    prediction_days = Column(Integer)  # Number of days ahead predicted
    prediction_horizon = Column(Integer)  # Prediction horizon in days
    actual_price = Column(Numeric(12, 4))  # 実際の価格（後で更新）
    accuracy_score = Column(Numeric(5, 4))  # 精度スコア
    is_validated = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # リレーションシップ
    stock = relationship("StockMaster", back_populates="predictions")