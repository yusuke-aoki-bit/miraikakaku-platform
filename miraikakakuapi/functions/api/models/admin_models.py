from pydantic import BaseModel, EmailStr
from typing import Optional


class UserCreateRequest(BaseModel):
    email: EmailStr
    password: str
    name: str
    role: str = "user"


class UserUpdateRequest(BaseModel):
    name: Optional[str] = None
    role: Optional[str] = None
    is_active: Optional[bool] = None


class UserResponse(BaseModel):
    id: str
    email: str
    name: str
    role: str
    is_active: bool
    created_at: str
    last_login: Optional[str] = None


class SystemStatsResponse(BaseModel):
    total_users: int
    total_stocks: int
    total_predictions: int
    today_predictions: int
    today_inferences: int
    recent_active_users: int
    system_uptime: str
    last_updated: str


class ModelPerformanceResponse(BaseModel):
    model_name: str
    total_predictions: int
    avg_confidence: float
    avg_accuracy: float
    last_prediction: str


class LogEntryResponse(BaseModel):
    id: int
    request_id: str
    model_name: str
    is_successful: bool
    inference_time_ms: Optional[int]
    error_message: Optional[str]
    created_at: str
