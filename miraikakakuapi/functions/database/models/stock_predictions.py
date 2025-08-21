from sqlalchemy import Column, Integer, String, DateTime, Float, ForeignKey, Text, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime
from .base import Base

class StockPredictions(Base):
    __tablename__ = "stock_predictions"
    
    id = Column(Integer, primary_key=True, index=True)
    symbol = Column(String(20), ForeignKey("stock_master.symbol"), nullable=False, index=True)
    prediction_date = Column(DateTime, nullable=False, index=True)
    created_at = Column(DateTime, nullable=False)
    predicted_price = Column(Float, nullable=False)
    predicted_change = Column(Float)
    predicted_change_percent = Column(Float)
    confidence_score = Column(Float)
    model_type = Column(String(50), nullable=False)  # Cloud SQLではmodel_type
    model_version = Column(String(20))
    prediction_horizon = Column(Integer, nullable=False)
    is_active = Column(Boolean, nullable=False)
    is_accurate = Column(Boolean)
    notes = Column(Text)
    
    # リレーションシップ
    stock = relationship("StockMaster", back_populates="predictions")