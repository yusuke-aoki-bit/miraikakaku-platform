"""
Stress Testing API Router
Phase 3.3 - Advanced Risk Management & Compliance

FastAPI endpoints for stress testing and scenario analysis
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from fastapi.responses import JSONResponse
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta, timezone
from pydantic import BaseModel, Field
from decimal import Decimal

from middleware.tenant_auth import get_tenant_context, TenantContext
from services.stress_testing_engine import (
    get_stress_engine,
    StressTestingEngine,
    StressScenario,
    ScenarioSeverity,
    CustomScenario,
    StressTestResult
)
from services.var_calculation_engine import Portfolio, PortfolioPosition

router = APIRouter(prefix="/api/v1/risk/stress", tags=["Stress Testing"])

# Pydantic models for API requests/responses

class StressTestPositionRequest(BaseModel):
    """Position for stress testing"""
    symbol: str = Field(..., description="Stock symbol")
    quantity: Decimal = Field(..., description="Position quantity")
    current_price: Decimal = Field(..., description="Current price per share")
    historical_returns: List[float] = Field(..., description="Historical daily returns")
    beta: Optional[float] = Field(None, description="Beta coefficient")

class StressTestPortfolioRequest(BaseModel):
    """Portfolio for stress testing"""
    id: str = Field(..., description="Portfolio identifier")
    name: str = Field(..., description="Portfolio name")
    positions: List[StressTestPositionRequest] = Field(..., description="Portfolio positions")
    benchmark: Optional[str] = Field("SPY", description="Benchmark symbol")
    currency: str = Field("USD", description="Portfolio currency")

class PredefinedStressTestRequest(BaseModel):
    """Predefined stress test request"""
    portfolio: StressTestPortfolioRequest = Field(..., description="Portfolio to test")
    scenario: StressScenario = Field(..., description="Stress scenario to apply")

class CustomStressTestRequest(BaseModel):
    """Custom stress test request"""
    portfolio: StressTestPortfolioRequest = Field(..., description="Portfolio to test")
    scenario_name: str = Field(..., description="Custom scenario name")
    description: str = Field(..., description="Scenario description")
    market_factors: Dict[str, float] = Field(..., description="Market factor shocks")
    volatility_factors: Dict[str, float] = Field(..., description="Volatility multipliers")
    duration_days: int = Field(1, description="Scenario duration in days")
    correlation_matrix: Optional[Dict[str, Dict[str, float]]] = Field(None, description="Correlation adjustments")

class ComprehensiveStressTestRequest(BaseModel):
    """Comprehensive stress test suite request"""
    portfolio: StressTestPortfolioRequest = Field(..., description="Portfolio to test")

class StressTestResultResponse(BaseModel):
    """Stress test result response"""
    scenario_id: str
    portfolio_id: str
    scenario_name: str
    severity: str
    pre_stress_value: Decimal
    post_stress_value: Decimal
    absolute_loss: Decimal
    percentage_loss: float
    var_impact: Decimal
    expected_shortfall_impact: Decimal
    liquidity_impact: float
    recovery_time_estimate: int
    component_losses: Dict[str, Decimal]
    risk_metrics: Dict[str, float]
    calculated_at: datetime

def convert_portfolio_request_to_portfolio(req: StressTestPortfolioRequest) -> Portfolio:
    """Convert API request to internal Portfolio object"""
    import numpy as np

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

@router.post("/predefined", response_model=StressTestResultResponse)
async def run_predefined_stress_test(
    request: PredefinedStressTestRequest,
    context: TenantContext = Depends(get_tenant_context),
    stress_engine: StressTestingEngine = Depends(get_stress_engine)
):
    """
    Run a predefined stress test scenario

    Available scenarios:
    - Black Monday 1987: Extreme single-day market crash
    - Tech Bubble 2000: Technology sector collapse
    - Financial Crisis 2008: Credit crunch and liquidity freeze
    - COVID-19 Pandemic 2020: Economic lockdown impacts
    - Interest Rate Shock: Sudden rate increases
    - Geopolitical Crisis: Market uncertainty events

    Returns detailed impact analysis including losses, VaR impact, and recovery estimates.
    """
    try:
        # Convert request to internal portfolio object
        portfolio = convert_portfolio_request_to_portfolio(request.portfolio)

        # Validate portfolio
        if len(portfolio.positions) == 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Portfolio must contain at least one position"
            )

        # Run stress test
        result = await stress_engine.run_stress_test(
            portfolio=portfolio,
            scenario=request.scenario,
            organization_id=context.organization_id
        )

        # Convert result to response format
        return StressTestResultResponse(
            scenario_id=result.scenario_id,
            portfolio_id=result.portfolio_id,
            scenario_name=result.scenario_name,
            severity=result.severity,
            pre_stress_value=result.pre_stress_value,
            post_stress_value=result.post_stress_value,
            absolute_loss=result.absolute_loss,
            percentage_loss=result.percentage_loss,
            var_impact=result.var_impact,
            expected_shortfall_impact=result.expected_shortfall_impact,
            liquidity_impact=result.liquidity_impact,
            recovery_time_estimate=result.recovery_time_estimate,
            component_losses=result.component_losses,
            risk_metrics=result.risk_metrics,
            calculated_at=result.calculated_at
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error running stress test: {str(e)}"
        )

@router.post("/custom", response_model=StressTestResultResponse)
async def run_custom_stress_test(
    request: CustomStressTestRequest,
    context: TenantContext = Depends(get_tenant_context),
    stress_engine: StressTestingEngine = Depends(get_stress_engine)
):
    """
    Run a custom stress test scenario

    Define your own market stress conditions:
    - Custom market factor shocks (e.g., equity -30%, bonds -10%)
    - Volatility multipliers by asset class
    - Custom scenario duration
    - Optional correlation matrix adjustments

    Useful for forward-looking risk assessment and "what-if" analysis.
    """
    try:
        # Convert request to internal portfolio object
        portfolio = convert_portfolio_request_to_portfolio(request.portfolio)

        # Validate portfolio
        if len(portfolio.positions) == 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Portfolio must contain at least one position"
            )

        # Validate custom scenario parameters
        if not request.market_factors:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Market factors must be specified for custom scenario"
            )

        # Create custom scenario
        custom_scenario = CustomScenario(
            name=request.scenario_name,
            description=request.description,
            market_factors=request.market_factors,
            volatility_factors=request.volatility_factors,
            correlation_matrix=request.correlation_matrix,
            duration_days=request.duration_days
        )

        # Run custom stress test
        result = await stress_engine.run_custom_scenario(
            portfolio=portfolio,
            custom_scenario=custom_scenario,
            organization_id=context.organization_id
        )

        # Convert result to response format
        return StressTestResultResponse(
            scenario_id=result.scenario_id,
            portfolio_id=result.portfolio_id,
            scenario_name=result.scenario_name,
            severity=result.severity,
            pre_stress_value=result.pre_stress_value,
            post_stress_value=result.post_stress_value,
            absolute_loss=result.absolute_loss,
            percentage_loss=result.percentage_loss,
            var_impact=result.var_impact,
            expected_shortfall_impact=result.expected_shortfall_impact,
            liquidity_impact=result.liquidity_impact,
            recovery_time_estimate=result.recovery_time_estimate,
            component_losses=result.component_losses,
            risk_metrics=result.risk_metrics,
            calculated_at=result.calculated_at
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error running custom stress test: {str(e)}"
        )

@router.post("/comprehensive")
async def run_comprehensive_stress_suite(
    request: ComprehensiveStressTestRequest,
    context: TenantContext = Depends(get_tenant_context),
    stress_engine: StressTestingEngine = Depends(get_stress_engine)
):
    """
    Run comprehensive stress test suite

    Executes all predefined stress scenarios:
    - Historical crisis scenarios (1987, 2000, 2008, 2020)
    - Forward-looking stress scenarios (interest rate, geopolitical)
    - Multiple severity levels

    Returns complete risk profile across all major stress scenarios.
    """
    try:
        # Convert request to internal portfolio object
        portfolio = convert_portfolio_request_to_portfolio(request.portfolio)

        # Validate portfolio
        if len(portfolio.positions) == 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Portfolio must contain at least one position"
            )

        # Run comprehensive stress test suite
        results = await stress_engine.run_comprehensive_stress_suite(
            portfolio=portfolio,
            organization_id=context.organization_id
        )

        # Convert results to response format
        response_results = {}
        for scenario_key, result in results.items():
            response_results[scenario_key] = {
                "scenario_name": result.scenario_name,
                "severity": result.severity,
                "absolute_loss": float(result.absolute_loss),
                "percentage_loss": result.percentage_loss,
                "var_impact": float(result.var_impact),
                "expected_shortfall_impact": float(result.expected_shortfall_impact),
                "liquidity_impact": result.liquidity_impact,
                "recovery_time_estimate": result.recovery_time_estimate,
                "component_losses": {k: float(v) for k, v in result.component_losses.items()},
                "risk_metrics": result.risk_metrics
            }

        # Calculate summary statistics
        losses = [result.percentage_loss for result in results.values()]
        recovery_times = [result.recovery_time_estimate for result in results.values()]

        summary = {
            "total_scenarios": len(results),
            "worst_case_loss": max(losses) if losses else 0.0,
            "best_case_loss": min(losses) if losses else 0.0,
            "average_loss": sum(losses) / len(losses) if losses else 0.0,
            "longest_recovery": max(recovery_times) if recovery_times else 0,
            "average_recovery": sum(recovery_times) / len(recovery_times) if recovery_times else 0
        }

        return {
            "portfolio_id": portfolio.id,
            "portfolio_value": float(portfolio.total_value),
            "test_date": datetime.now(timezone.utc).isoformat(),
            "summary": summary,
            "scenario_results": response_results
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error running comprehensive stress test: {str(e)}"
        )

@router.get("/history")
async def get_stress_test_history(
    context: TenantContext = Depends(get_tenant_context),
    stress_engine: StressTestingEngine = Depends(get_stress_engine),
    portfolio_id: Optional[str] = Query(None, description="Filter by portfolio ID"),
    days: int = Query(30, description="Number of days of history to retrieve")
):
    """
    Get stress test history for organization

    Returns historical stress test results with filtering options:
    - By portfolio (optional)
    - By time period (last N days)

    Useful for tracking portfolio stress exposure over time.
    """
    try:
        if days < 1 or days > 365:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Days must be between 1 and 365"
            )

        history = await stress_engine.get_stress_test_history(
            organization_id=context.organization_id,
            portfolio_id=portfolio_id,
            days=days
        )

        return {
            "organization_id": context.organization_id,
            "portfolio_id": portfolio_id,
            "days": days,
            "total_tests": len(history),
            "stress_tests": history
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error getting stress test history: {str(e)}"
        )

@router.get("/scenarios")
async def get_available_scenarios():
    """Get available predefined stress test scenarios"""

    scenarios = []
    for scenario in StressScenario:
        scenario_info = {
            "code": scenario.value,
            "name": scenario.name,
            "description": {
                StressScenario.BLACK_MONDAY_1987: "1987 stock market crash - extreme single-day decline",
                StressScenario.TECH_BUBBLE_2000: "Dot-com bubble burst - technology sector collapse",
                StressScenario.FINANCIAL_CRISIS_2008: "2008 financial crisis - credit crunch and banking crisis",
                StressScenario.FLASH_CRASH_2010: "2010 flash crash - algorithmic trading disruption",
                StressScenario.COVID19_PANDEMIC_2020: "COVID-19 pandemic - economic lockdowns and disruption",
                StressScenario.INTEREST_RATE_SHOCK: "Sudden interest rate increase - monetary policy shock",
                StressScenario.CREDIT_SPREAD_WIDENING: "Corporate credit spread expansion",
                StressScenario.EQUITY_MARKET_CRASH: "General equity market crash scenario",
                StressScenario.CURRENCY_CRISIS: "Currency devaluation crisis",
                StressScenario.GEOPOLITICAL_CRISIS: "Geopolitical event with market uncertainty",
                StressScenario.INFLATION_SHOCK: "Sudden inflation spike",
                StressScenario.COMMODITY_PRICE_SHOCK: "Commodity price disruption"
            }.get(scenario, ""),
            "category": "historical" if scenario.value in [
                "black_monday_1987", "tech_bubble_2000", "financial_crisis_2008",
                "flash_crash_2010", "covid19_pandemic_2020"
            ] else "forward_looking"
        }
        scenarios.append(scenario_info)

    severity_levels = [
        {
            "code": severity.value,
            "name": severity.name,
            "description": {
                ScenarioSeverity.MILD: "Limited market disruption with quick recovery",
                ScenarioSeverity.MODERATE: "Significant market stress with medium-term impact",
                ScenarioSeverity.SEVERE: "Major market crisis with long recovery period",
                ScenarioSeverity.EXTREME: "Catastrophic market event with prolonged impact"
            }.get(severity, "")
        }
        for severity in ScenarioSeverity
    ]

    return {
        "predefined_scenarios": scenarios,
        "severity_levels": severity_levels,
        "total_scenarios": len(scenarios),
        "custom_scenario_support": True
    }

@router.get("/health")
async def stress_test_health_check(
    stress_engine: StressTestingEngine = Depends(get_stress_engine)
):
    """Health check for stress testing engine"""
    try:
        # Test database connection
        with stress_engine.SessionLocal() as session:
            session.execute("SELECT 1")

        return {
            "status": "healthy",
            "service": "stress_testing_engine",
            "predefined_scenarios": len(stress_engine.predefined_scenarios),
            "supported_severities": len(ScenarioSeverity),
            "custom_scenario_support": True,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Stress testing engine unhealthy: {str(e)}"
        )