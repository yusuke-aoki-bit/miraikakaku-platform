from sqlalchemy import Column, Integer, String, DateTime, Text, Numeric, Boolean
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()


class AIInferenceLog(Base):
    __tablename__ = "ai_inference_log"

    id = Column(Integer, primary_key=True, index=True)
    request_id = Column(String(100), unique=True, index=True, nullable=False)
    model_name = Column(String(100), nullable=False)
    model_version = Column(String(50))
    input_data = Column(Text)  # JSON形式の入力データ
    output_data = Column(Text)  # JSON形式の出力データ
    inference_time_ms = Column(Integer)  # 推論時間（ミリ秒）
    confidence_score = Column(Numeric(5, 4))
    error_message = Column(Text)
    is_successful = Column(Boolean, default=True)
    endpoint = Column(String(255))
    user_id = Column(String(100))
    session_id = Column(String(100))
    created_at = Column(DateTime, default=datetime.utcnow, index=True)

    # パフォーマンス監視用
    cpu_usage = Column(Numeric(5, 2))
    memory_usage = Column(Numeric(10, 2))
    gpu_usage = Column(Numeric(5, 2))
