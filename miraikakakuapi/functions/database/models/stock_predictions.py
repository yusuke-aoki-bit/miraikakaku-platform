from sqlalchemy import Column, Integer, String, DateTime, Numeric, ForeignKey, Text, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime

Base = declarative_base()

class StockPredictions(Base):
    __tablename__ = "stock_predictions"
    
    id = Column(Integer, primary_key=True, index=True)
    symbol = Column(String(20), ForeignKey("stock_master.symbol"), nullable=False, index=True)
    prediction_date = Column(DateTime, nullable=False, index=True)
    target_date = Column(DateTime, nullable=False)
    predicted_price = Column(Numeric(12, 4), nullable=False)
    confidence_score = Column(Numeric(5, 4))
    prediction_type = Column(String(50), nullable=False)  # 'daily', 'weekly', 'monthly'
    model_name = Column(String(100), nullable=False)
    model_version = Column(String(50))
    features_used = Column(Text)  # JSON形式で使用した特徴量を保存
    actual_price = Column(Numeric(12, 4))  # 実際の価格（後で更新）
    accuracy_score = Column(Numeric(5, 4))  # 精度スコア
    is_validated = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # リレーションシップ
    stock = relationship("StockMaster", back_populates="predictions")