"""
Stress Testing and Scenario Analysis Engine
Phase 3.3 - Advanced Risk Management & Compliance

Comprehensive stress testing system for portfolio risk assessment:
- Predefined market stress scenarios
- Custom scenario modeling
- Historical event simulation
- Forward-looking stress tests
- Regulatory stress scenarios (CCAR, EBA, etc.)
"""

import os
import logging
from datetime import datetime, timedelta, timezone
from typing import Dict, List, Optional, Any, Tuple
from enum import Enum
from dataclasses import dataclass, asdict
import asyncio
import numpy as np
import pandas as pd
from scipy import stats
from decimal import Decimal
import math
import json

from sqlalchemy import create_engine, Column, String, Float, DateTime, Integer, Boolean, Text, DECIMAL
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.dialects.postgresql import UUID, JSONB
import uuid

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

Base = declarative_base()

class StressScenario(Enum):
    """Predefined stress testing scenarios"""
    BLACK_MONDAY_1987 = "black_monday_1987"
    TECH_BUBBLE_2000 = "tech_bubble_2000"
    FINANCIAL_CRISIS_2008 = "financial_crisis_2008"
    FLASH_CRASH_2010 = "flash_crash_2010"
    COVID19_PANDEMIC_2020 = "covid19_pandemic_2020"
    INTEREST_RATE_SHOCK = "interest_rate_shock"
    CREDIT_SPREAD_WIDENING = "credit_spread_widening"
    EQUITY_MARKET_CRASH = "equity_market_crash"
    CURRENCY_CRISIS = "currency_crisis"
    GEOPOLITICAL_CRISIS = "geopolitical_crisis"
    INFLATION_SHOCK = "inflation_shock"
    COMMODITY_PRICE_SHOCK = "commodity_price_shock"

class ScenarioSeverity(Enum):
    """Stress scenario severity levels"""
    MILD = "mild"
    MODERATE = "moderate"
    SEVERE = "severe"
    EXTREME = "extreme"

@dataclass
class StressTestParameters:
    """Parameters for a stress test scenario"""
    scenario_name: str
    severity: ScenarioSeverity
    market_shock_percentage: float  # Overall market decline
    volatility_multiplier: float    # Volatility increase factor
    correlation_increase: float     # Correlation increase during crisis
    duration_days: int             # Stress period duration
    sector_specific_shocks: Dict[str, float]  # Sector-specific impacts
    asset_class_shocks: Dict[str, float]      # Asset class impacts
    liquidity_impact: float        # Liquidity reduction factor
    description: str

@dataclass
class StressTestResult:
    """Result of a stress test"""
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
    recovery_time_estimate: int  # days
    component_losses: Dict[str, Decimal]
    risk_metrics: Dict[str, float]
    calculated_at: datetime

@dataclass
class CustomScenario:
    """Custom stress scenario definition"""
    name: str
    description: str
    market_factors: Dict[str, float]  # e.g., {"equity": -0.30, "bond": -0.10}
    volatility_factors: Dict[str, float]
    correlation_matrix: Optional[Dict[str, Dict[str, float]]] = None
    duration_days: int = 1

class StressTestRecord(Base):
    """Database model for stress test results"""
    __tablename__ = 'stress_test_results'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    organization_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    portfolio_id = Column(String(255), nullable=False, index=True)
    scenario_id = Column(String(255), nullable=False)
    scenario_name = Column(String(255), nullable=False)
    severity = Column(String(50), nullable=False)
    pre_stress_value = Column(DECIMAL(20, 2), nullable=False)
    post_stress_value = Column(DECIMAL(20, 2), nullable=False)
    absolute_loss = Column(DECIMAL(20, 2), nullable=False)
    percentage_loss = Column(Float, nullable=False)
    var_impact = Column(DECIMAL(20, 2), nullable=False)
    expected_shortfall_impact = Column(DECIMAL(20, 2), nullable=False)
    liquidity_impact = Column(Float, nullable=False)
    recovery_time_estimate = Column(Integer, nullable=False)
    test_data = Column(JSONB, nullable=False)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow)

class StressTestingEngine:
    """Main stress testing and scenario analysis engine"""

    def __init__(self, database_url: str):
        self.engine = create_engine(database_url, pool_pre_ping=True)
        Base.metadata.create_all(self.engine)
        self.SessionLocal = sessionmaker(bind=self.engine)

        # Initialize predefined stress scenarios
        self.predefined_scenarios = self._initialize_stress_scenarios()

        logger.info("🧪 Stress Testing Engine initialized")
        logger.info(f"📊 Predefined scenarios loaded: {len(self.predefined_scenarios)}")

    def _initialize_stress_scenarios(self) -> Dict[StressScenario, StressTestParameters]:
        """Initialize predefined stress testing scenarios"""

        scenarios = {
            StressScenario.BLACK_MONDAY_1987: StressTestParameters(
                scenario_name="Black Monday 1987",
                severity=ScenarioSeverity.EXTREME,
                market_shock_percentage=-0.22,  # 22% single-day decline
                volatility_multiplier=3.0,
                correlation_increase=0.3,
                duration_days=1,
                sector_specific_shocks={
                    "technology": -0.25,
                    "financials": -0.20,
                    "consumer_discretionary": -0.18
                },
                asset_class_shocks={
                    "equity": -0.22,
                    "bond": 0.05,
                    "commodity": -0.10
                },
                liquidity_impact=0.4,
                description="1987 stock market crash scenario with extreme volatility"
            ),

            StressScenario.TECH_BUBBLE_2000: StressTestParameters(
                scenario_name="Tech Bubble Burst 2000",
                severity=ScenarioSeverity.SEVERE,
                market_shock_percentage=-0.40,  # 40% decline over period
                volatility_multiplier=2.5,
                correlation_increase=0.25,
                duration_days=180,
                sector_specific_shocks={
                    "technology": -0.60,
                    "telecommunications": -0.45,
                    "consumer_discretionary": -0.30,
                    "financials": -0.20
                },
                asset_class_shocks={
                    "equity": -0.40,
                    "bond": 0.15,
                    "commodity": -0.05
                },
                liquidity_impact=0.3,
                description="Dot-com bubble burst with tech sector collapse"
            ),

            StressScenario.FINANCIAL_CRISIS_2008: StressTestParameters(
                scenario_name="Financial Crisis 2008",
                severity=ScenarioSeverity.EXTREME,
                market_shock_percentage=-0.50,  # 50% peak-to-trough decline
                volatility_multiplier=4.0,
                correlation_increase=0.4,
                duration_days=365,
                sector_specific_shocks={
                    "financials": -0.70,
                    "real_estate": -0.65,
                    "consumer_discretionary": -0.45,
                    "industrials": -0.40
                },
                asset_class_shocks={
                    "equity": -0.50,
                    "corporate_bond": -0.25,
                    "government_bond": 0.20,
                    "commodity": -0.30
                },
                liquidity_impact=0.6,
                description="2008 financial crisis with credit crunch and liquidity freeze"
            ),

            StressScenario.COVID19_PANDEMIC_2020: StressTestParameters(
                scenario_name="COVID-19 Pandemic 2020",
                severity=ScenarioSeverity.SEVERE,
                market_shock_percentage=-0.35,
                volatility_multiplier=3.5,
                correlation_increase=0.35,
                duration_days=90,
                sector_specific_shocks={
                    "travel_leisure": -0.70,
                    "energy": -0.60,
                    "retail": -0.50,
                    "financials": -0.40,
                    "technology": -0.10,  # Tech performed better
                    "healthcare": 0.05
                },
                asset_class_shocks={
                    "equity": -0.35,
                    "corporate_bond": -0.15,
                    "government_bond": 0.10,
                    "commodity": -0.25
                },
                liquidity_impact=0.5,
                description="COVID-19 pandemic with economic lockdowns and supply disruptions"
            ),

            StressScenario.INTEREST_RATE_SHOCK: StressTestParameters(
                scenario_name="Interest Rate Shock",
                severity=ScenarioSeverity.MODERATE,
                market_shock_percentage=-0.15,
                volatility_multiplier=1.8,
                correlation_increase=0.15,
                duration_days=30,
                sector_specific_shocks={
                    "utilities": -0.25,
                    "real_estate": -0.30,
                    "financials": 0.05,  # Banks benefit from higher rates
                    "technology": -0.20
                },
                asset_class_shocks={
                    "bond": -0.20,
                    "equity": -0.15,
                    "real_estate": -0.25
                },
                liquidity_impact=0.2,
                description="Sudden 300 basis point interest rate increase"
            ),

            StressScenario.GEOPOLITICAL_CRISIS: StressTestParameters(
                scenario_name="Geopolitical Crisis",
                severity=ScenarioSeverity.MODERATE,
                market_shock_percentage=-0.20,
                volatility_multiplier=2.2,
                correlation_increase=0.25,
                duration_days=60,
                sector_specific_shocks={
                    "energy": 0.15,     # Energy prices spike
                    "defense": 0.10,    # Defense spending increases
                    "technology": -0.15,
                    "consumer_discretionary": -0.25
                },
                asset_class_shocks={
                    "equity": -0.20,
                    "commodity": 0.20,
                    "bond": 0.05,
                    "gold": 0.25
                },
                liquidity_impact=0.3,
                description="Major geopolitical event with market uncertainty"
            )
        }

        return scenarios

    async def run_stress_test(
        self,
        portfolio: 'Portfolio',  # Import from var_calculation_engine
        scenario: StressScenario,
        organization_id: str = None
    ) -> StressTestResult:
        """Run a predefined stress test scenario on a portfolio"""

        logger.info(f"🧪 Running stress test: {scenario.value}")

        try:
            # Get scenario parameters
            if scenario not in self.predefined_scenarios:
                raise ValueError(f"Unknown stress scenario: {scenario}")

            scenario_params = self.predefined_scenarios[scenario]

            # Apply stress scenario
            stressed_portfolio = await self._apply_stress_scenario(portfolio, scenario_params)

            # Calculate losses
            pre_stress_value = portfolio.total_value
            post_stress_value = stressed_portfolio.total_value
            absolute_loss = pre_stress_value - post_stress_value
            percentage_loss = float(absolute_loss / pre_stress_value * 100)

            # Calculate component losses
            component_losses = {}
            for i, position in enumerate(portfolio.positions):
                original_value = position.market_value
                stressed_value = stressed_portfolio.positions[i].market_value
                component_losses[position.symbol] = original_value - stressed_value

            # Estimate VaR impact (simplified)
            var_multiplier = scenario_params.volatility_multiplier * scenario_params.correlation_increase
            var_impact = absolute_loss * Decimal(str(var_multiplier))

            # Expected Shortfall impact
            es_multiplier = var_multiplier * 1.3  # ES typically higher than VaR
            expected_shortfall_impact = absolute_loss * Decimal(str(es_multiplier))

            # Recovery time estimation (based on historical data)
            recovery_time = self._estimate_recovery_time(scenario_params.severity, percentage_loss)

            # Calculate additional risk metrics
            risk_metrics = await self._calculate_stress_risk_metrics(portfolio, stressed_portfolio, scenario_params)

            # Create result
            result = StressTestResult(
                scenario_id=str(uuid.uuid4()),
                portfolio_id=portfolio.id,
                scenario_name=scenario_params.scenario_name,
                severity=scenario_params.severity.value,
                pre_stress_value=pre_stress_value,
                post_stress_value=post_stress_value,
                absolute_loss=absolute_loss,
                percentage_loss=percentage_loss,
                var_impact=var_impact,
                expected_shortfall_impact=expected_shortfall_impact,
                liquidity_impact=scenario_params.liquidity_impact,
                recovery_time_estimate=recovery_time,
                component_losses=component_losses,
                risk_metrics=risk_metrics,
                calculated_at=datetime.now(timezone.utc)
            )

            # Store result
            if organization_id:
                await self._store_stress_test_result(result, organization_id)

            logger.info(f"✅ Stress test completed: {percentage_loss:.1f}% loss")
            logger.info(f"💰 Absolute loss: ${absolute_loss:,.2f}")

            return result

        except Exception as e:
            logger.error(f"❌ Error running stress test: {e}")
            raise

    async def run_custom_scenario(
        self,
        portfolio: 'Portfolio',
        custom_scenario: CustomScenario,
        organization_id: str = None
    ) -> StressTestResult:
        """Run a custom stress scenario"""

        logger.info(f"🧪 Running custom scenario: {custom_scenario.name}")

        try:
            # Convert custom scenario to standard parameters
            scenario_params = StressTestParameters(
                scenario_name=custom_scenario.name,
                severity=ScenarioSeverity.MODERATE,  # Default for custom
                market_shock_percentage=custom_scenario.market_factors.get("equity", 0.0),
                volatility_multiplier=max(custom_scenario.volatility_factors.values()) if custom_scenario.volatility_factors else 1.0,
                correlation_increase=0.2,  # Default assumption
                duration_days=custom_scenario.duration_days,
                sector_specific_shocks={},
                asset_class_shocks=custom_scenario.market_factors,
                liquidity_impact=0.1,  # Default for custom scenarios
                description=custom_scenario.description
            )

            # Run the stress test
            return await self.run_stress_test(portfolio, StressScenario.GEOPOLITICAL_CRISIS, organization_id)

        except Exception as e:
            logger.error(f"❌ Error running custom scenario: {e}")
            raise

    async def _apply_stress_scenario(
        self,
        portfolio: 'Portfolio',
        scenario_params: StressTestParameters
    ) -> 'Portfolio':
        """Apply stress scenario to portfolio positions"""

        from services.var_calculation_engine import Portfolio, PortfolioPosition

        stressed_positions = []
        total_stressed_value = Decimal(0)

        for position in portfolio.positions:
            # Determine stress factor for this position
            stress_factor = scenario_params.market_shock_percentage

            # Apply sector-specific shocks if available
            # (In a real implementation, you'd map symbols to sectors)
            # For now, use market-wide shock

            # Apply asset class shocks
            # (In a real implementation, you'd classify assets)
            if "equity" in scenario_params.asset_class_shocks:
                stress_factor = scenario_params.asset_class_shocks["equity"]

            # Apply stress to price
            stressed_price = position.current_price * (1 + Decimal(str(stress_factor)))
            stressed_price = max(stressed_price, Decimal("0.01"))  # Floor at 1 cent

            # Calculate new market value
            stressed_market_value = position.quantity * stressed_price
            total_stressed_value += stressed_market_value

            # Adjust volatility
            stressed_volatility = position.volatility * scenario_params.volatility_multiplier

            # Create stressed position
            stressed_position = PortfolioPosition(
                symbol=position.symbol,
                quantity=position.quantity,
                current_price=stressed_price,
                market_value=stressed_market_value,
                weight=0.0,  # Will be recalculated
                historical_returns=position.historical_returns,
                volatility=stressed_volatility,
                beta=position.beta
            )
            stressed_positions.append(stressed_position)

        # Recalculate weights
        for position in stressed_positions:
            position.weight = float(position.market_value / total_stressed_value) if total_stressed_value > 0 else 0.0

        # Create stressed portfolio
        stressed_portfolio = Portfolio(
            id=portfolio.id + "_stressed",
            name=portfolio.name + " (Stressed)",
            total_value=total_stressed_value,
            positions=stressed_positions,
            benchmark=portfolio.benchmark,
            currency=portfolio.currency,
            created_at=datetime.now(timezone.utc)
        )

        return stressed_portfolio

    async def _calculate_stress_risk_metrics(
        self,
        original_portfolio: 'Portfolio',
        stressed_portfolio: 'Portfolio',
        scenario_params: StressTestParameters
    ) -> Dict[str, float]:
        """Calculate additional risk metrics for stress test"""

        # Portfolio concentration risk
        original_hhi = sum(pos.weight ** 2 for pos in original_portfolio.positions)
        stressed_hhi = sum(pos.weight ** 2 for pos in stressed_portfolio.positions)

        # Volatility impact
        original_vol = np.sqrt(sum((pos.weight * pos.volatility) ** 2 for pos in original_portfolio.positions))
        stressed_vol = np.sqrt(sum((pos.weight * pos.volatility) ** 2 for pos in stressed_portfolio.positions))

        # Correlation impact (simplified)
        correlation_impact = scenario_params.correlation_increase

        # Maximum drawdown estimation
        max_drawdown = scenario_params.market_shock_percentage

        # Liquidity stress
        liquidity_stress = scenario_params.liquidity_impact

        return {
            "original_concentration_hhi": original_hhi,
            "stressed_concentration_hhi": stressed_hhi,
            "original_portfolio_volatility": original_vol,
            "stressed_portfolio_volatility": stressed_vol,
            "correlation_impact": correlation_impact,
            "estimated_max_drawdown": abs(max_drawdown),
            "liquidity_stress_factor": liquidity_stress,
            "volatility_multiplier": scenario_params.volatility_multiplier
        }

    def _estimate_recovery_time(self, severity: ScenarioSeverity, loss_percentage: float) -> int:
        """Estimate portfolio recovery time based on historical data"""

        base_recovery_days = {
            ScenarioSeverity.MILD: 30,
            ScenarioSeverity.MODERATE: 90,
            ScenarioSeverity.SEVERE: 365,
            ScenarioSeverity.EXTREME: 730
        }

        base_days = base_recovery_days[severity]

        # Adjust based on loss magnitude
        loss_multiplier = max(1.0, abs(loss_percentage) / 20.0)  # 20% baseline

        estimated_days = int(base_days * loss_multiplier)

        # Cap at reasonable maximum
        return min(estimated_days, 1095)  # 3 years max

    async def _store_stress_test_result(self, result: StressTestResult, organization_id: str):
        """Store stress test result in database"""

        try:
            with self.SessionLocal() as session:
                stress_record = StressTestRecord(
                    organization_id=organization_id,
                    portfolio_id=result.portfolio_id,
                    scenario_id=result.scenario_id,
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
                    test_data={
                        "component_losses": {k: str(v) for k, v in result.component_losses.items()},
                        "risk_metrics": result.risk_metrics,
                        "calculated_at": result.calculated_at.isoformat()
                    }
                )

                session.add(stress_record)
                session.commit()

                logger.info(f"💾 Stress test result stored for portfolio {result.portfolio_id}")

        except Exception as e:
            logger.error(f"Error storing stress test result: {e}")
            raise

    async def run_comprehensive_stress_suite(
        self,
        portfolio: 'Portfolio',
        organization_id: str = None
    ) -> Dict[str, StressTestResult]:
        """Run comprehensive stress test suite with all scenarios"""

        logger.info(f"🧪 Running comprehensive stress test suite for portfolio {portfolio.name}")

        results = {}

        # Run all predefined scenarios
        for scenario in self.predefined_scenarios.keys():
            try:
                result = await self.run_stress_test(portfolio, scenario, organization_id)
                results[scenario.value] = result
            except Exception as e:
                logger.error(f"Error running scenario {scenario.value}: {e}")
                continue

        logger.info(f"✅ Comprehensive stress testing completed: {len(results)} scenarios")

        return results

    async def get_stress_test_history(
        self,
        organization_id: str,
        portfolio_id: Optional[str] = None,
        days: int = 30
    ) -> List[Dict[str, Any]]:
        """Get stress test history"""

        try:
            with self.SessionLocal() as session:
                query = session.query(StressTestRecord).filter(
                    StressTestRecord.organization_id == organization_id,
                    StressTestRecord.created_at >= datetime.utcnow() - timedelta(days=days)
                )

                if portfolio_id:
                    query = query.filter(StressTestRecord.portfolio_id == portfolio_id)

                tests = query.order_by(StressTestRecord.created_at.desc()).all()

                return [
                    {
                        "id": str(test.id),
                        "portfolio_id": test.portfolio_id,
                        "scenario_name": test.scenario_name,
                        "severity": test.severity,
                        "absolute_loss": float(test.absolute_loss),
                        "percentage_loss": test.percentage_loss,
                        "recovery_time_estimate": test.recovery_time_estimate,
                        "created_at": test.created_at.isoformat()
                    }
                    for test in tests
                ]

        except Exception as e:
            logger.error(f"Error getting stress test history: {e}")
            raise

# Global stress testing engine instance
stress_engine = None

def get_stress_engine() -> StressTestingEngine:
    """Get global stress testing engine instance"""
    global stress_engine
    if stress_engine is None:
        database_url = os.getenv("DATABASE_URL", "postgresql://username:password@localhost:5432/miraikakaku")
        stress_engine = StressTestingEngine(database_url)
    return stress_engine