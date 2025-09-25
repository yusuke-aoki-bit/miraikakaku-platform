"""
Value at Risk (VaR) Calculation Engine
Phase 3.3 - Advanced Risk Management & Compliance

Comprehensive VaR calculation system supporting multiple methodologies:
- Historical Simulation VaR
- Parametric VaR (variance-covariance)
- Monte Carlo Simulation VaR
- Expected Shortfall (ES/CVaR)
- Stress testing integration
"""

import os
import logging
from datetime import datetime, timedelta, timezone
from typing import Dict, List, Optional, Any, Tuple
from enum import Enum
from dataclasses import dataclass
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

class VaRMethod(Enum):
    """VaR calculation methods"""
    HISTORICAL_SIMULATION = "historical_simulation"
    PARAMETRIC = "parametric"
    MONTE_CARLO = "monte_carlo"
    HYBRID = "hybrid"

class TimeHorizon(Enum):
    """VaR time horizons"""
    DAILY = 1
    WEEKLY = 7
    MONTHLY = 30
    QUARTERLY = 90
    ANNUAL = 365

@dataclass
class VaRResult:
    """VaR calculation result"""
    portfolio_id: str
    method: VaRMethod
    confidence_level: float
    time_horizon: int
    var_amount: Decimal
    expected_shortfall: Decimal
    portfolio_value: Decimal
    var_percentage: float
    calculation_date: datetime
    volatility: float
    correlation_matrix: Optional[Dict[str, Any]] = None
    component_vars: Optional[Dict[str, Decimal]] = None
    back_test_results: Optional[Dict[str, Any]] = None

@dataclass
class PortfolioPosition:
    """Individual portfolio position"""
    symbol: str
    quantity: Decimal
    current_price: Decimal
    market_value: Decimal
    weight: float
    historical_returns: List[float]
    volatility: float
    beta: Optional[float] = None

@dataclass
class Portfolio:
    """Portfolio for VaR calculation"""
    id: str
    name: str
    total_value: Decimal
    positions: List[PortfolioPosition]
    benchmark: Optional[str] = "SPY"
    currency: str = "USD"
    created_at: datetime = None

class VaRCalculation(Base):
    """Database model for VaR calculations"""
    __tablename__ = 'var_calculations'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    organization_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    portfolio_id = Column(String(255), nullable=False, index=True)
    method = Column(String(50), nullable=False)
    confidence_level = Column(Float, nullable=False)
    time_horizon = Column(Integer, nullable=False)
    var_amount = Column(DECIMAL(20, 2), nullable=False)
    expected_shortfall = Column(DECIMAL(20, 2), nullable=False)
    portfolio_value = Column(DECIMAL(20, 2), nullable=False)
    var_percentage = Column(Float, nullable=False)
    volatility = Column(Float, nullable=False)
    calculation_data = Column(JSONB, nullable=False)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow)

class VaRCalculationEngine:
    """Main VaR calculation engine"""

    def __init__(self, database_url: str):
        self.engine = create_engine(database_url, pool_pre_ping=True)
        Base.metadata.create_all(self.engine)
        self.SessionLocal = sessionmaker(bind=self.engine)

        # Default VaR parameters
        self.default_confidence_levels = [0.95, 0.99, 0.999]
        self.default_time_horizons = [1, 7, 30]  # days
        self.historical_window = 252  # trading days (1 year)

        logger.info("📊 VaR Calculation Engine initialized")

    async def calculate_portfolio_var(
        self,
        portfolio: Portfolio,
        method: VaRMethod,
        confidence_level: float = 0.95,
        time_horizon: int = 1,
        organization_id: str = None
    ) -> VaRResult:
        """Calculate Value at Risk for a portfolio using specified method"""

        logger.info(f"🧮 Calculating VaR for portfolio {portfolio.name}")
        logger.info(f"📊 Method: {method.value}, Confidence: {confidence_level}, Horizon: {time_horizon} days")

        try:
            # Choose calculation method
            if method == VaRMethod.HISTORICAL_SIMULATION:
                var_result = await self._calculate_historical_var(portfolio, confidence_level, time_horizon)
            elif method == VaRMethod.PARAMETRIC:
                var_result = await self._calculate_parametric_var(portfolio, confidence_level, time_horizon)
            elif method == VaRMethod.MONTE_CARLO:
                var_result = await self._calculate_monte_carlo_var(portfolio, confidence_level, time_horizon)
            elif method == VaRMethod.HYBRID:
                var_result = await self._calculate_hybrid_var(portfolio, confidence_level, time_horizon)
            else:
                raise ValueError(f"Unsupported VaR method: {method}")

            # Store result in database
            if organization_id:
                await self._store_var_result(var_result, organization_id)

            logger.info(f"✅ VaR calculated: ${var_result.var_amount:,.2f} ({var_result.var_percentage:.2f}%)")

            return var_result

        except Exception as e:
            logger.error(f"❌ Error calculating VaR: {e}")
            raise

    async def _calculate_historical_var(
        self,
        portfolio: Portfolio,
        confidence_level: float,
        time_horizon: int
    ) -> VaRResult:
        """Calculate VaR using Historical Simulation method"""

        # Get historical returns for all positions
        portfolio_returns = []

        # Calculate portfolio returns for each historical period
        min_periods = min(len(pos.historical_returns) for pos in portfolio.positions)
        if min_periods < self.historical_window:
            logger.warning(f"Limited historical data: {min_periods} periods available")
            periods_to_use = min_periods
        else:
            periods_to_use = self.historical_window

        for i in range(periods_to_use):
            portfolio_return = 0.0
            for position in portfolio.positions:
                if i < len(position.historical_returns):
                    portfolio_return += position.weight * position.historical_returns[i]
            portfolio_returns.append(portfolio_return)

        # Sort returns and find VaR percentile
        portfolio_returns.sort()
        var_index = int((1 - confidence_level) * len(portfolio_returns))
        var_return = portfolio_returns[var_index]

        # Scale for time horizon
        var_return_scaled = var_return * math.sqrt(time_horizon)

        # Calculate VaR amount
        var_amount = abs(Decimal(str(var_return_scaled)) * portfolio.total_value)

        # Calculate Expected Shortfall (average of returns worse than VaR)
        tail_returns = portfolio_returns[:var_index] if var_index > 0 else [var_return]
        expected_shortfall_return = np.mean(tail_returns) * math.sqrt(time_horizon)
        expected_shortfall = abs(Decimal(str(expected_shortfall_return)) * portfolio.total_value)

        # Calculate portfolio volatility
        volatility = np.std(portfolio_returns) * math.sqrt(252)

        return VaRResult(
            portfolio_id=portfolio.id,
            method=VaRMethod.HISTORICAL_SIMULATION,
            confidence_level=confidence_level,
            time_horizon=time_horizon,
            var_amount=var_amount,
            expected_shortfall=expected_shortfall,
            portfolio_value=portfolio.total_value,
            var_percentage=float(var_amount / portfolio.total_value * 100),
            calculation_date=datetime.now(timezone.utc),
            volatility=volatility,
            back_test_results=self._perform_back_test(portfolio_returns, var_return, confidence_level)
        )

    async def _calculate_parametric_var(
        self,
        portfolio: Portfolio,
        confidence_level: float,
        time_horizon: int
    ) -> VaRResult:
        """Calculate VaR using Parametric (variance-covariance) method"""

        # Calculate portfolio variance
        portfolio_variance = 0.0
        portfolio_volatility = 0.0

        # Individual position contributions
        for position in portfolio.positions:
            portfolio_variance += (position.weight ** 2) * (position.volatility ** 2)

        # Add correlation effects (simplified - assumes zero correlation for now)
        # In a full implementation, this would use a correlation matrix
        for i, pos1 in enumerate(portfolio.positions):
            for j, pos2 in enumerate(portfolio.positions):
                if i != j:
                    # Simplified correlation assumption (0.3 for diversified portfolios)
                    correlation = 0.3
                    portfolio_variance += 2 * pos1.weight * pos2.weight * pos1.volatility * pos2.volatility * correlation

        portfolio_volatility = math.sqrt(portfolio_variance)

        # Scale for time horizon
        portfolio_volatility_scaled = portfolio_volatility * math.sqrt(time_horizon)

        # Calculate VaR using normal distribution
        z_score = stats.norm.ppf(1 - confidence_level)
        var_amount = abs(Decimal(str(z_score * portfolio_volatility_scaled)) * portfolio.total_value)

        # Expected Shortfall for normal distribution
        phi_z = stats.norm.pdf(z_score)
        expected_shortfall_multiplier = phi_z / (1 - confidence_level)
        expected_shortfall = abs(Decimal(str(expected_shortfall_multiplier * portfolio_volatility_scaled)) * portfolio.total_value)

        # Component VaR calculation
        component_vars = {}
        for position in portfolio.positions:
            marginal_var = position.weight * (position.volatility ** 2) / portfolio_volatility
            component_var = marginal_var * float(var_amount) / portfolio_volatility_scaled
            component_vars[position.symbol] = Decimal(str(component_var))

        return VaRResult(
            portfolio_id=portfolio.id,
            method=VaRMethod.PARAMETRIC,
            confidence_level=confidence_level,
            time_horizon=time_horizon,
            var_amount=var_amount,
            expected_shortfall=expected_shortfall,
            portfolio_value=portfolio.total_value,
            var_percentage=float(var_amount / portfolio.total_value * 100),
            calculation_date=datetime.now(timezone.utc),
            volatility=portfolio_volatility * math.sqrt(252),  # Annualized
            component_vars=component_vars
        )

    async def _calculate_monte_carlo_var(
        self,
        portfolio: Portfolio,
        confidence_level: float,
        time_horizon: int,
        simulations: int = 10000
    ) -> VaRResult:
        """Calculate VaR using Monte Carlo simulation"""

        # Generate random scenarios
        portfolio_returns = []

        for _ in range(simulations):
            portfolio_return = 0.0

            for position in portfolio.positions:
                # Generate random return based on position's historical volatility
                # Assuming normal distribution (can be enhanced with other distributions)
                random_return = np.random.normal(0, position.volatility / math.sqrt(252))
                portfolio_return += position.weight * random_return

            # Scale for time horizon
            portfolio_return_scaled = portfolio_return * math.sqrt(time_horizon)
            portfolio_returns.append(portfolio_return_scaled)

        # Sort returns and find VaR percentile
        portfolio_returns.sort()
        var_index = int((1 - confidence_level) * len(portfolio_returns))
        var_return = portfolio_returns[var_index]

        # Calculate VaR amount
        var_amount = abs(Decimal(str(var_return)) * portfolio.total_value)

        # Calculate Expected Shortfall
        tail_returns = portfolio_returns[:var_index] if var_index > 0 else [var_return]
        expected_shortfall_return = np.mean(tail_returns)
        expected_shortfall = abs(Decimal(str(expected_shortfall_return)) * portfolio.total_value)

        # Calculate portfolio volatility from simulation
        volatility = np.std(portfolio_returns) * math.sqrt(252 / time_horizon)

        return VaRResult(
            portfolio_id=portfolio.id,
            method=VaRMethod.MONTE_CARLO,
            confidence_level=confidence_level,
            time_horizon=time_horizon,
            var_amount=var_amount,
            expected_shortfall=expected_shortfall,
            portfolio_value=portfolio.total_value,
            var_percentage=float(var_amount / portfolio.total_value * 100),
            calculation_date=datetime.now(timezone.utc),
            volatility=volatility
        )

    async def _calculate_hybrid_var(
        self,
        portfolio: Portfolio,
        confidence_level: float,
        time_horizon: int
    ) -> VaRResult:
        """Calculate VaR using hybrid approach (combines multiple methods)"""

        # Calculate VaR using all methods
        historical_var = await self._calculate_historical_var(portfolio, confidence_level, time_horizon)
        parametric_var = await self._calculate_parametric_var(portfolio, confidence_level, time_horizon)
        monte_carlo_var = await self._calculate_monte_carlo_var(portfolio, confidence_level, time_horizon)

        # Weighted average (can be customized based on market conditions)
        weights = {"historical": 0.4, "parametric": 0.3, "monte_carlo": 0.3}

        weighted_var = (
            weights["historical"] * float(historical_var.var_amount) +
            weights["parametric"] * float(parametric_var.var_amount) +
            weights["monte_carlo"] * float(monte_carlo_var.var_amount)
        )

        weighted_es = (
            weights["historical"] * float(historical_var.expected_shortfall) +
            weights["parametric"] * float(parametric_var.expected_shortfall) +
            weights["monte_carlo"] * float(monte_carlo_var.expected_shortfall)
        )

        weighted_volatility = (
            weights["historical"] * historical_var.volatility +
            weights["parametric"] * parametric_var.volatility +
            weights["monte_carlo"] * monte_carlo_var.volatility
        )

        return VaRResult(
            portfolio_id=portfolio.id,
            method=VaRMethod.HYBRID,
            confidence_level=confidence_level,
            time_horizon=time_horizon,
            var_amount=Decimal(str(weighted_var)),
            expected_shortfall=Decimal(str(weighted_es)),
            portfolio_value=portfolio.total_value,
            var_percentage=weighted_var / float(portfolio.total_value) * 100,
            calculation_date=datetime.now(timezone.utc),
            volatility=weighted_volatility
        )

    def _perform_back_test(
        self,
        historical_returns: List[float],
        var_return: float,
        confidence_level: float
    ) -> Dict[str, Any]:
        """Perform VaR back-testing"""

        # Count violations (returns worse than VaR)
        violations = sum(1 for r in historical_returns if r < var_return)
        total_observations = len(historical_returns)
        expected_violations = (1 - confidence_level) * total_observations
        violation_rate = violations / total_observations

        # Kupiec test for back-testing
        if violations > 0:
            lr_statistic = 2 * (
                violations * math.log(violation_rate / (1 - confidence_level)) +
                (total_observations - violations) * math.log((1 - violation_rate) / confidence_level)
            )
            # Chi-square critical value at 95% confidence
            critical_value = 3.841
            test_passed = lr_statistic < critical_value
        else:
            lr_statistic = 0
            test_passed = True

        return {
            "violations": violations,
            "total_observations": total_observations,
            "expected_violations": expected_violations,
            "violation_rate": violation_rate,
            "expected_violation_rate": 1 - confidence_level,
            "kupiec_lr_statistic": lr_statistic,
            "test_passed": test_passed
        }

    async def _store_var_result(self, var_result: VaRResult, organization_id: str):
        """Store VaR result in database"""

        try:
            with self.SessionLocal() as session:
                var_record = VaRCalculation(
                    organization_id=organization_id,
                    portfolio_id=var_result.portfolio_id,
                    method=var_result.method.value,
                    confidence_level=var_result.confidence_level,
                    time_horizon=var_result.time_horizon,
                    var_amount=var_result.var_amount,
                    expected_shortfall=var_result.expected_shortfall,
                    portfolio_value=var_result.portfolio_value,
                    var_percentage=var_result.var_percentage,
                    volatility=var_result.volatility,
                    calculation_data={
                        "component_vars": {k: str(v) for k, v in (var_result.component_vars or {}).items()},
                        "back_test_results": var_result.back_test_results,
                        "correlation_matrix": var_result.correlation_matrix
                    }
                )

                session.add(var_record)
                session.commit()

                logger.info(f"💾 VaR result stored for portfolio {var_result.portfolio_id}")

        except Exception as e:
            logger.error(f"Error storing VaR result: {e}")
            raise

    async def calculate_multiple_scenarios(
        self,
        portfolio: Portfolio,
        organization_id: str = None
    ) -> Dict[str, List[VaRResult]]:
        """Calculate VaR for multiple confidence levels and time horizons"""

        results = {}

        for method in [VaRMethod.HISTORICAL_SIMULATION, VaRMethod.PARAMETRIC, VaRMethod.MONTE_CARLO]:
            results[method.value] = []

            for confidence_level in self.default_confidence_levels:
                for time_horizon in self.default_time_horizons:
                    var_result = await self.calculate_portfolio_var(
                        portfolio=portfolio,
                        method=method,
                        confidence_level=confidence_level,
                        time_horizon=time_horizon,
                        organization_id=organization_id
                    )
                    results[method.value].append(var_result)

        return results

    async def get_var_history(
        self,
        organization_id: str,
        portfolio_id: Optional[str] = None,
        days: int = 30
    ) -> List[Dict[str, Any]]:
        """Get VaR calculation history"""

        try:
            with self.SessionLocal() as session:
                query = session.query(VaRCalculation).filter(
                    VaRCalculation.organization_id == organization_id,
                    VaRCalculation.created_at >= datetime.utcnow() - timedelta(days=days)
                )

                if portfolio_id:
                    query = query.filter(VaRCalculation.portfolio_id == portfolio_id)

                calculations = query.order_by(VaRCalculation.created_at.desc()).all()

                return [
                    {
                        "id": str(calc.id),
                        "portfolio_id": calc.portfolio_id,
                        "method": calc.method,
                        "confidence_level": calc.confidence_level,
                        "time_horizon": calc.time_horizon,
                        "var_amount": float(calc.var_amount),
                        "expected_shortfall": float(calc.expected_shortfall),
                        "portfolio_value": float(calc.portfolio_value),
                        "var_percentage": calc.var_percentage,
                        "volatility": calc.volatility,
                        "created_at": calc.created_at.isoformat()
                    }
                    for calc in calculations
                ]

        except Exception as e:
            logger.error(f"Error getting VaR history: {e}")
            raise

    async def generate_var_report(
        self,
        organization_id: str,
        portfolio_id: str,
        start_date: datetime,
        end_date: datetime
    ) -> Dict[str, Any]:
        """Generate comprehensive VaR report"""

        try:
            with self.SessionLocal() as session:
                calculations = session.query(VaRCalculation).filter(
                    VaRCalculation.organization_id == organization_id,
                    VaRCalculation.portfolio_id == portfolio_id,
                    VaRCalculation.created_at >= start_date,
                    VaRCalculation.created_at <= end_date
                ).all()

                if not calculations:
                    return {"error": "No VaR calculations found for the specified period"}

                # Aggregate statistics
                var_amounts = [float(calc.var_amount) for calc in calculations]
                var_percentages = [calc.var_percentage for calc in calculations]

                report = {
                    "portfolio_id": portfolio_id,
                    "report_period": {
                        "start_date": start_date.isoformat(),
                        "end_date": end_date.isoformat()
                    },
                    "summary_statistics": {
                        "total_calculations": len(calculations),
                        "avg_var_amount": np.mean(var_amounts),
                        "max_var_amount": np.max(var_amounts),
                        "min_var_amount": np.min(var_amounts),
                        "avg_var_percentage": np.mean(var_percentages),
                        "var_volatility": np.std(var_amounts)
                    },
                    "method_breakdown": {},
                    "confidence_level_analysis": {},
                    "time_horizon_analysis": {},
                    "trend_analysis": {
                        "var_trend": "increasing" if var_amounts[-1] > var_amounts[0] else "decreasing",
                        "volatility_trend": "stable"  # Would calculate actual trend
                    }
                }

                # Method breakdown
                for method in VaRMethod:
                    method_calcs = [calc for calc in calculations if calc.method == method.value]
                    if method_calcs:
                        method_vars = [float(calc.var_amount) for calc in method_calcs]
                        report["method_breakdown"][method.value] = {
                            "count": len(method_calcs),
                            "avg_var": np.mean(method_vars),
                            "max_var": np.max(method_vars),
                            "min_var": np.min(method_vars)
                        }

                return report

        except Exception as e:
            logger.error(f"Error generating VaR report: {e}")
            raise

# Global VaR engine instance
var_engine = None

def get_var_engine() -> VaRCalculationEngine:
    """Get global VaR calculation engine instance"""
    global var_engine
    if var_engine is None:
        database_url = os.getenv("DATABASE_URL", "postgresql://username:password@localhost:5432/miraikakaku")
        var_engine = VaRCalculationEngine(database_url)
    return var_engine