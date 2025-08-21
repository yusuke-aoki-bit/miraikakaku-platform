from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class StockSearchResponse(BaseModel):
    symbol: str
    company_name: str
    exchange: str
    sector: Optional[str] = None
    industry: Optional[str] = None

class StockPriceResponse(BaseModel):
    symbol: str
    date: datetime
    open_price: Optional[float] = None
    high_price: Optional[float] = None
    low_price: Optional[float] = None
    close_price: float
    volume: Optional[int] = None
    data_source: str

class StockPredictionResponse(BaseModel):
    symbol: str
    prediction_date: datetime
    predicted_price: float
    confidence_score: Optional[float] = None
    model_type: str
    prediction_horizon: int
    is_active: bool

class StockPredictionRequest(BaseModel):
    symbol: str
    prediction_type: str = "daily"
    model_name: Optional[str] = "default"

class HealthResponse(BaseModel):
    status: str
    service: str
    environment: str
    timestamp: datetime