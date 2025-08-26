from sqlalchemy import (
    Column,
    Integer,
    String,
    DateTime,
    Float,
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
    prediction_days = Column(Integer, nullable=False)
    current_price = Column(Float, nullable=False)
    predicted_price = Column(Float, nullable=False)
    confidence_score = Column(Float)
    prediction_range_low = Column(Float)
    prediction_range_high = Column(Float)
    model_version = Column(String(50), default="LSTM_v1.0")
    model_accuracy = Column(Float)
    features_used = Column(Text)  # JSON as TEXT
    created_at = Column(DateTime, default=datetime.utcnow)

    # リレーションシップ
    stock = relationship("StockMaster", back_populates="predictions")
