"""
Value at Risk (VaR) API Router
Phase 3.3 - Advanced Risk Management & Compliance

FastAPI endpoints for VaR calculations and risk metrics
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from fastapi.responses import JSONResponse
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta, timezone
from pydantic import BaseModel, Field
from decimal import Decimal

from middleware.tenant_auth import get_tenant_context, TenantContext
from services.var_calculation_engine import (
    get_var_engine,
    VaRCalculationEngine,
    VaRMethod,
    TimeHorizon,
    Portfolio,
    PortfolioPosition,
    VaRResult
)

router = APIRouter(prefix="/api/v1/risk/var", tags=["Value at Risk"])

# Pydantic models for API requests/responses

class PortfolioPositionRequest(BaseModel):
    """Portfolio position for VaR calculation"""
    symbol: str = Field(..., description="Stock symbol")
    quantity: Decimal = Field(..., description="Position quantity")
    current_price: Decimal = Field(..., description="Current price per share")
    historical_returns: List[float] = Field(..., description="Historical daily returns")
    beta: Optional[float] = Field(None, description="Beta coefficient")

class PortfolioRequest(BaseModel):
    """Portfolio for VaR calculation"""
    id: str = Field(..., description="Portfolio identifier")
    name: str = Field(..., description="Portfolio name")
    positions: List[PortfolioPositionRequest] = Field(..., description="Portfolio positions")
    benchmark: Optional[str] = Field("SPY", description="Benchmark symbol")
    currency: str = Field("USD", description="Portfolio currency")

class VaRCalculationRequest(BaseModel):
    """VaR calculation request"""
    portfolio: PortfolioRequest = Field(..., description="Portfolio to analyze")
    method: VaRMethod = Field(..., description="VaR calculation method")
    confidence_level: float = Field(0.95, description="Confidence level (0.90, 0.95, 0.99, etc.)")
    time_horizon: int = Field(1, description="Time horizon in days")

class MultipleVaRRequest(BaseModel):
    """Multiple VaR scenario calculation request"""
    portfolio: PortfolioRequest = Field(..., description="Portfolio to analyze")

class VaRResultResponse(BaseModel):
    """VaR calculation result response"""
    portfolio_id: str
    method: str
    confidence_level: float
    time_horizon: int
    var_amount: Decimal
    expected_shortfall: Decimal
    portfolio_value: Decimal
    var_percentage: float
    volatility: float
    calculation_date: datetime
    component_vars: Optional[Dict[str, Decimal]] = None
    back_test_results: Optional[Dict[str, Any]] = None

def convert_portfolio_request_to_portfolio(req: PortfolioRequest) -> Portfolio:
    """Convert API request to internal Portfolio object"""
    positions = []
    total_value = Decimal(0)

    # Convert positions
    for pos_req in req.positions:
        market_value = pos_req.quantity * pos_req.current_price
        total_value += market_value

        position = PortfolioPosition(
            symbol=pos_req.symbol,
            quantity=pos_req.quantity,
            current_price=pos_req.current_price,
            market_value=market_value,
            weight=0.0,  # Will be calculated after total_value is known
            historical_returns=pos_req.historical_returns,
            volatility=float(np.std(pos_req.historical_returns)) * np.sqrt(252) if pos_req.historical_returns else 0.0,
            beta=pos_req.beta
        )
        positions.append(position)

    # Calculate weights
    for position in positions:
        position.weight = float(position.market_value / total_value)

    return Portfolio(
        id=req.id,
        name=req.name,
        total_value=total_value,
        positions=positions,
        benchmark=req.benchmark,
        currency=req.currency,
        created_at=datetime.now(timezone.utc)
    )

@router.post("/calculate", response_model=VaRResultResponse)
async def calculate_var(
    request: VaRCalculationRequest,
    context: TenantContext = Depends(get_tenant_context),
    var_engine: VaRCalculationEngine = Depends(get_var_engine)
):
    """
    Calculate Value at Risk for a portfolio

    Supports multiple VaR methodologies:
    - Historical Simulation: Based on historical return distribution
    - Parametric: Assumes normal distribution using volatility
    - Monte Carlo: Simulates random scenarios
    - Hybrid: Weighted combination of multiple methods

    Returns VaR amount, Expected Shortfall, and risk metrics.
    """
    try:
        # Validate confidence level
        if not 0.5 <= request.confidence_level <= 0.999:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Confidence level must be between 0.5 and 0.999"
            )

        # Validate time horizon
        if request.time_horizon < 1 or request.time_horizon > 365:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Time horizon must be between 1 and 365 days"
            )

        # Convert request to internal portfolio object
        portfolio = convert_portfolio_request_to_portfolio(request.portfolio)

        # Validate portfolio
        if len(portfolio.positions) == 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Portfolio must contain at least one position"
            )

        # Calculate VaR
        var_result = await var_engine.calculate_portfolio_var(
            portfolio=portfolio,
            method=request.method,
            confidence_level=request.confidence_level,
            time_horizon=request.time_horizon,
            organization_id=context.organization_id
        )

        # Convert result to response format
        return VaRResultResponse(
            portfolio_id=var_result.portfolio_id,
            method=var_result.method.value,
            confidence_level=var_result.confidence_level,
            time_horizon=var_result.time_horizon,
            var_amount=var_result.var_amount,
            expected_shortfall=var_result.expected_shortfall,
            portfolio_value=var_result.portfolio_value,
            var_percentage=var_result.var_percentage,
            volatility=var_result.volatility,
            calculation_date=var_result.calculation_date,
            component_vars=var_result.component_vars,
            back_test_results=var_result.back_test_results
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error calculating VaR: {str(e)}"
        )

@router.post("/calculate-multiple")
async def calculate_multiple_var(
    request: MultipleVaRRequest,
    context: TenantContext = Depends(get_tenant_context),
    var_engine: VaRCalculationEngine = Depends(get_var_engine)
):
    """
    Calculate VaR for multiple confidence levels, time horizons, and methods

    Returns comprehensive VaR analysis across:
    - Confidence levels: 95%, 99%, 99.9%
    - Time horizons: 1 day, 1 week, 1 month
    - Methods: Historical, Parametric, Monte Carlo
    """
    try:
        # Convert request to internal portfolio object
        portfolio = convert_portfolio_request_to_portfolio(request.portfolio)

        # Calculate multiple scenarios
        results = await var_engine.calculate_multiple_scenarios(
            portfolio=portfolio,
            organization_id=context.organization_id
        )

        # Convert results to response format
        response_results = {}
        for method, var_results in results.items():
            response_results[method] = []
            for var_result in var_results:
                response_results[method].append({
                    "confidence_level": var_result.confidence_level,
                    "time_horizon": var_result.time_horizon,
                    "var_amount": float(var_result.var_amount),
                    "expected_shortfall": float(var_result.expected_shortfall),
                    "var_percentage": var_result.var_percentage,
                    "volatility": var_result.volatility
                })

        return {
            "portfolio_id": portfolio.id,
            "portfolio_value": float(portfolio.total_value),
            "calculation_date": datetime.now(timezone.utc).isoformat(),
            "results": response_results
        }

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error calculating multiple VaR scenarios: {str(e)}"
        )

@router.get("/history")
async def get_var_history(
    context: TenantContext = Depends(get_tenant_context),
    var_engine: VaRCalculationEngine = Depends(get_var_engine),
    portfolio_id: Optional[str] = Query(None, description="Filter by portfolio ID"),
    days: int = Query(30, description="Number of days of history to retrieve")
):
    """
    Get VaR calculation history for organization

    Returns historical VaR calculations with filtering options:
    - By portfolio (optional)
    - By time period (last N days)
    """
    try:
        if days < 1 or days > 365:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Days must be between 1 and 365"
            )

        history = await var_engine.get_var_history(
            organization_id=context.organization_id,
            portfolio_id=portfolio_id,
            days=days
        )

        return {
            "organization_id": context.organization_id,
            "portfolio_id": portfolio_id,
            "days": days,
            "total_calculations": len(history),
            "calculations": history
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error getting VaR history: {str(e)}"
        )

@router.post("/reports/generate")
async def generate_var_report(
    portfolio_id: str,
    start_date: datetime,
    end_date: datetime,
    context: TenantContext = Depends(get_tenant_context),
    var_engine: VaRCalculationEngine = Depends(get_var_engine)
):
    """
    Generate comprehensive VaR report for a portfolio

    Report includes:
    - Summary statistics (average, max, min VaR)
    - Method comparison analysis
    - Confidence level breakdown
    - Time horizon analysis
    - Trend analysis
    """
    try:
        # Validate date range
        if end_date <= start_date:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="End date must be after start date"
            )

        # Validate date range is not too large
        if (end_date - start_date).days > 365:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Date range cannot exceed 365 days"
            )

        report = await var_engine.generate_var_report(
            organization_id=context.organization_id,
            portfolio_id=portfolio_id,
            start_date=start_date,
            end_date=end_date
        )

        return report

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error generating VaR report: {str(e)}"
        )

@router.get("/methods")
async def get_var_methods():
    """Get available VaR calculation methods"""
    methods = [
        {
            "code": method.value,
            "name": method.name,
            "description": {
                VaRMethod.HISTORICAL_SIMULATION: "Uses historical return distribution",
                VaRMethod.PARAMETRIC: "Assumes normal distribution with volatility",
                VaRMethod.MONTE_CARLO: "Simulates random market scenarios",
                VaRMethod.HYBRID: "Weighted combination of multiple methods"
            }.get(method, "")
        }
        for method in VaRMethod
    ]

    confidence_levels = [0.90, 0.95, 0.99, 0.999]
    time_horizons = [1, 7, 30, 90, 365]

    return {
        "methods": methods,
        "confidence_levels": confidence_levels,
        "time_horizons": time_horizons,
        "default_confidence_level": 0.95,
        "default_time_horizon": 1
    }

@router.get("/health")
async def var_health_check(
    var_engine: VaRCalculationEngine = Depends(get_var_engine)
):
    """Health check for VaR calculation engine"""
    try:
        # Test database connection
        with var_engine.SessionLocal() as session:
            session.execute("SELECT 1")

        return {
            "status": "healthy",
            "service": "var_calculation_engine",
            "supported_methods": len(VaRMethod),
            "default_confidence_levels": len(var_engine.default_confidence_levels),
            "default_time_horizons": len(var_engine.default_time_horizons),
            "historical_window": var_engine.historical_window,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"VaR calculation engine unhealthy: {str(e)}"
        )

# Import numpy for calculations
import numpy as np