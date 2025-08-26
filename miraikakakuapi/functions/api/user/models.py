from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime, date
from enum import Enum


# Enums


class InvestmentStyle(str, Enum):
    conservative = "conservative"
    moderate = "moderate"
    aggressive = "aggressive"
    growth = "growth"
    value = "value"


class RiskTolerance(str, Enum):
    low = "low"
    medium = "medium"
    high = "high"


class InvestmentExperience(str, Enum):
    beginner = "beginner"
    intermediate = "intermediate"
    advanced = "advanced"
    expert = "expert"


class Priority(str, Enum):
    high = "high"
    medium = "medium"
    low = "low"


class FactorType(str, Enum):
    technical = "technical"
    fundamental = "fundamental"
    sentiment = "sentiment"
    news = "news"
    pattern = "pattern"


class ContestStatus(str, Enum):
    active = "active"
    closed = "closed"
    completed = "completed"


class ConfidenceLevel(str, Enum):
    low = "low"
    medium = "medium"
    high = "high"


class ThemeCategory(str, Enum):
    technology = "technology"
    energy = "energy"
    finance = "finance"
    healthcare = "healthcare"
    consumer = "consumer"
    industrial = "industrial"
    materials = "materials"


class TrendDirection(str, Enum):
    bullish = "bullish"
    bearish = "bearish"
    neutral = "neutral"


# User Profile Models


class UserProfileCreate(BaseModel):
    user_id: str
    username: Optional[str] = None
    email: Optional[str] = None
    investment_style: InvestmentStyle = InvestmentStyle.moderate
    risk_tolerance: RiskTolerance = RiskTolerance.medium
    investment_experience: InvestmentExperience = InvestmentExperience.beginner
    preferred_sectors: Optional[List[str]] = None
    investment_goals: Optional[str] = None
    total_portfolio_value: Optional[float] = None


class UserProfileUpdate(BaseModel):
    username: Optional[str] = None
    email: Optional[str] = None
    investment_style: Optional[InvestmentStyle] = None
    risk_tolerance: Optional[RiskTolerance] = None
    investment_experience: Optional[InvestmentExperience] = None
    preferred_sectors: Optional[List[str]] = None
    investment_goals: Optional[str] = None
    total_portfolio_value: Optional[float] = None


class UserProfileResponse(BaseModel):
    id: int
    user_id: str
    username: Optional[str]
    email: Optional[str]
    investment_style: InvestmentStyle
    risk_tolerance: RiskTolerance
    investment_experience: InvestmentExperience
    preferred_sectors: Optional[List[str]]
    investment_goals: Optional[str]
    total_portfolio_value: Optional[float]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# AI Decision Factor Models


class AiDecisionFactorResponse(BaseModel):
    id: int
    factor_type: FactorType
    factor_name: str
    influence_score: float
    description: Optional[str]
    confidence: Optional[float]
    created_at: datetime

    class Config:
        from_attributes = True


class EnhancedPredictionResponse(BaseModel):
    id: int
    symbol: str
    prediction_date: date
    predicted_price: float
    confidence_score: Optional[float]
    model_version: Optional[str]
    decision_factors: List[AiDecisionFactorResponse]

    class Config:
        from_attributes = True


# Watchlist Models


class WatchlistCreate(BaseModel):
    symbol: str
    alert_threshold_up: Optional[float] = None
    alert_threshold_down: Optional[float] = None
    notes: Optional[str] = None
    priority: Priority = Priority.medium


class WatchlistResponse(BaseModel):
    id: int
    user_id: str
    symbol: str
    added_at: datetime
    alert_threshold_up: Optional[float]
    alert_threshold_down: Optional[float]
    notes: Optional[str]
    priority: Priority

    class Config:
        from_attributes = True


# Portfolio Models


class PortfolioResponse(BaseModel):
    id: int
    user_id: str
    symbol: str
    shares: float
    average_cost: float
    purchase_date: Optional[date]
    portfolio_weight: Optional[float]
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# Contest Models


class PredictionContestResponse(BaseModel):
    id: int
    contest_name: str
    symbol: str
    contest_start_date: date
    prediction_deadline: datetime
    target_date: date
    actual_price: Optional[float]
    status: ContestStatus
    prize_description: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True


class ContestPredictionCreate(BaseModel):
    user_id: str
    predicted_price: float
    confidence_level: ConfidenceLevel = ConfidenceLevel.medium
    reasoning: Optional[str] = None


class ContestPredictionResponse(BaseModel):
    id: int
    contest_id: int
    user_id: str
    predicted_price: float
    confidence_level: ConfidenceLevel
    reasoning: Optional[str]
    accuracy_score: Optional[float]
    rank_position: Optional[int]
    submitted_at: datetime

    class Config:
        from_attributes = True


# Theme Insights Models


class ThemeInsightResponse(BaseModel):
    id: int
    theme_name: str
    theme_category: ThemeCategory
    insight_date: date
    title: str
    summary: str
    key_metrics: Optional[Dict[str, Any]]
    related_symbols: Optional[Dict[str, Any]]
    trend_direction: TrendDirection
    impact_score: Optional[float]
    created_at: datetime

    class Config:
        from_attributes = True


# Personalized Recommendation Models


class PersonalizedRecommendationResponse(BaseModel):
    symbol: str
    company_name: str
    recommendation_score: float
    reasoning: str
    risk_level: str
    expected_return: float
    time_horizon: str
    match_reasons: List[str]


class InvestmentStyleAnalysis(BaseModel):
    current_style: InvestmentStyle
    confidence: float
    characteristics: List[str]
    recommendations: List[str]
    portfolio_allocation_suggestion: Dict[str, float]
