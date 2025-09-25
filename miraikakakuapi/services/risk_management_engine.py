"""
Advanced Risk Management Engine
Phase 3.3 - 高度リスク管理・コンプライアンス

Comprehensive risk assessment and management system for enterprise clients
"""

import uuid
import numpy as np
import pandas as pd
import logging
from datetime import datetime, timezone, timedelta
from typing import Dict, List, Optional, Any, Tuple, Union
from dataclasses import dataclass, asdict
from enum import Enum
import asyncio
from concurrent.futures import ThreadPoolExecutor
import json
import warnings

from sqlalchemy import create_engine, Column, String, Float, DateTime, Boolean, Integer, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session

# Suppress warnings for cleaner output
warnings.filterwarnings('ignore', category=FutureWarning)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

Base = declarative_base()

class RiskLevel(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class RiskCategory(Enum):
    MARKET = "market"
    CREDIT = "credit"
    LIQUIDITY = "liquidity"
    OPERATIONAL = "operational"
    REGULATORY = "regulatory"
    CONCENTRATION = "concentration"

class VaRMethod(Enum):
    HISTORICAL = "historical"
    PARAMETRIC = "parametric"
    MONTE_CARLO = "monte_carlo"

@dataclass
class Portfolio:
    portfolio_id: str
    organization_id: str
    name: str
    positions: List[Dict[str, Any]]
    total_value: float
    currency: str = "USD"
    benchmark: Optional[str] = None

@dataclass
class RiskMetrics:
    portfolio_id: str
    calculated_at: datetime
    var_1d_95: float  # 1-day 95% VaR
    var_1d_99: float  # 1-day 99% VaR
    var_10d_95: float  # 10-day 95% VaR
    cvar_95: float  # Conditional VaR (Expected Shortfall)
    volatility: float
    beta: float
    sharpe_ratio: float
    max_drawdown: float
    concentration_risk: float
    liquidity_score: float
    risk_level: RiskLevel

@dataclass
class StressTestScenario:
    scenario_id: str
    name: str
    description: str
    market_shocks: Dict[str, float]  # asset_class -> shock_percentage
    probability: float
    severity: str

@dataclass
class StressTestResult:
    scenario_id: str
    portfolio_id: str
    scenario_name: str
    potential_loss: float
    loss_percentage: float
    affected_positions: List[str]
    risk_level: RiskLevel
    calculated_at: datetime

class RiskAlert(Base):
    """リスクアラート"""
    __tablename__ = 'risk_alerts'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    organization_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    portfolio_id = Column(String(100), nullable=False, index=True)
    alert_type = Column(String(50), nullable=False)
    risk_category = Column(String(50), nullable=False)
    risk_level = Column(String(20), nullable=False)
    threshold_value = Column(Float)
    current_value = Column(Float)
    message = Column(String(500))
    is_active = Column(Boolean, default=True, index=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    acknowledged_at = Column(DateTime(timezone=True))
    resolved_at = Column(DateTime(timezone=True))
    metadata = Column(JSON)

class RiskCalculation(Base):
    """リスク計算履歴"""
    __tablename__ = 'risk_calculations'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    organization_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    portfolio_id = Column(String(100), nullable=False, index=True)
    calculation_type = Column(String(50), nullable=False)  # var, stress_test, etc.
    method = Column(String(50))
    parameters = Column(JSON)
    results = Column(JSON, nullable=False)
    calculated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), index=True)
    calculation_time_ms = Column(Integer)

class RiskManagementEngine:
    """高度リスク管理エンジン"""

    def __init__(self, database_url: str = None):
        self.database_url = database_url
        if database_url:
            self.engine = create_engine(database_url)
            self.SessionLocal = sessionmaker(bind=self.engine)
            Base.metadata.create_all(bind=self.engine)

        # Initialize calculation parameters
        self.confidence_levels = [0.95, 0.99]
        self.time_horizons = [1, 10, 30]  # days
        self.lookback_periods = [252, 504, 756]  # trading days (1, 2, 3 years)

        # Thread pool for parallel calculations
        self.executor = ThreadPoolExecutor(max_workers=4)

        # Predefined stress test scenarios
        self.stress_scenarios = self._initialize_stress_scenarios()

        logger.info("✅ Risk Management Engine initialized")

    def _initialize_stress_scenarios(self) -> List[StressTestScenario]:
        """Initialize predefined stress test scenarios"""
        scenarios = [
            StressTestScenario(
                scenario_id="black_monday_1987",
                name="Black Monday 1987",
                description="Market crash similar to October 1987",
                market_shocks={
                    "equities": -0.22,  # -22%
                    "bonds": 0.05,      # +5%
                    "commodities": -0.15,
                    "currencies": -0.10
                },
                probability=0.01,
                severity="extreme"
            ),
            StressTestScenario(
                scenario_id="financial_crisis_2008",
                name="Financial Crisis 2008",
                description="Credit crisis and market collapse",
                market_shocks={
                    "equities": -0.35,
                    "bonds": -0.20,
                    "real_estate": -0.40,
                    "commodities": -0.30,
                    "credit_spreads": 0.50
                },
                probability=0.005,
                severity="extreme"
            ),
            StressTestScenario(
                scenario_id="covid_2020",
                name="COVID-19 Pandemic",
                description="Global pandemic market shock",
                market_shocks={
                    "equities": -0.30,
                    "bonds": 0.10,
                    "commodities": -0.25,
                    "travel_hospitality": -0.50,
                    "technology": -0.10
                },
                probability=0.02,
                severity="severe"
            ),
            StressTestScenario(
                scenario_id="interest_rate_shock",
                name="Interest Rate Shock",
                description="Sudden 300bp rate increase",
                market_shocks={
                    "bonds": -0.25,
                    "equities": -0.15,
                    "real_estate": -0.20,
                    "interest_rates": 0.03
                },
                probability=0.05,
                severity="moderate"
            ),
            StressTestScenario(
                scenario_id="geopolitical_crisis",
                name="Geopolitical Crisis",
                description="Major geopolitical event",
                market_shocks={
                    "equities": -0.20,
                    "commodities": 0.15,
                    "currencies": -0.15,
                    "energy": 0.30,
                    "defense": 0.10
                },
                probability=0.03,
                severity="high"
            )
        ]

        return scenarios

    async def calculate_portfolio_risk(self, portfolio: Portfolio) -> RiskMetrics:
        """Calculate comprehensive risk metrics for portfolio"""
        start_time = datetime.now()

        try:
            # Get historical data for portfolio positions
            historical_returns = await self._get_portfolio_historical_returns(portfolio)

            if historical_returns.empty:
                logger.warning(f"No historical data for portfolio {portfolio.portfolio_id}")
                return self._create_default_risk_metrics(portfolio.portfolio_id)

            # Calculate VaR using multiple methods
            var_metrics = await self._calculate_var_metrics(historical_returns)

            # Calculate other risk metrics
            volatility = self._calculate_volatility(historical_returns)
            beta = await self._calculate_beta(historical_returns, portfolio.benchmark)
            sharpe_ratio = self._calculate_sharpe_ratio(historical_returns)
            max_drawdown = self._calculate_max_drawdown(historical_returns)
            concentration_risk = self._calculate_concentration_risk(portfolio)
            liquidity_score = await self._calculate_liquidity_score(portfolio)

            # Determine overall risk level
            risk_level = self._determine_risk_level(var_metrics, volatility, concentration_risk)

            risk_metrics = RiskMetrics(
                portfolio_id=portfolio.portfolio_id,
                calculated_at=datetime.now(timezone.utc),
                var_1d_95=var_metrics['var_1d_95'],
                var_1d_99=var_metrics['var_1d_99'],
                var_10d_95=var_metrics['var_10d_95'],
                cvar_95=var_metrics['cvar_95'],
                volatility=volatility,
                beta=beta,
                sharpe_ratio=sharpe_ratio,
                max_drawdown=max_drawdown,
                concentration_risk=concentration_risk,
                liquidity_score=liquidity_score,
                risk_level=risk_level
            )

            # Store calculation in database
            if self.database_url:
                await self._store_risk_calculation(
                    portfolio.organization_id,
                    portfolio.portfolio_id,
                    "comprehensive_risk",
                    "integrated",
                    asdict(risk_metrics),
                    int((datetime.now() - start_time).total_seconds() * 1000)
                )

            # Check for risk alerts
            await self._check_risk_thresholds(portfolio.organization_id, portfolio.portfolio_id, risk_metrics)

            logger.info(f"✅ Risk metrics calculated for portfolio {portfolio.portfolio_id}")
            return risk_metrics

        except Exception as e:
            logger.error(f"❌ Error calculating risk metrics: {e}")
            raise

    async def _calculate_var_metrics(self, returns: pd.Series) -> Dict[str, float]:
        """Calculate Value at Risk using multiple methods"""

        var_metrics = {}

        # Historical VaR
        var_95_1d = np.percentile(returns, 5)  # 95% confidence, 1-day
        var_99_1d = np.percentile(returns, 1)  # 99% confidence, 1-day
        var_95_10d = var_95_1d * np.sqrt(10)  # Scale to 10-day

        # Conditional VaR (Expected Shortfall)
        cvar_95 = returns[returns <= var_95_1d].mean()

        # Parametric VaR (assuming normal distribution)
        mean_return = returns.mean()
        std_return = returns.std()
        z_95 = 1.645  # 95% confidence z-score
        z_99 = 2.326  # 99% confidence z-score

        parametric_var_95_1d = mean_return - z_95 * std_return
        parametric_var_99_1d = mean_return - z_99 * std_return

        # Use more conservative estimate
        var_metrics['var_1d_95'] = min(var_95_1d, parametric_var_95_1d)
        var_metrics['var_1d_99'] = min(var_99_1d, parametric_var_99_1d)
        var_metrics['var_10d_95'] = var_95_10d
        var_metrics['cvar_95'] = cvar_95 if not np.isnan(cvar_95) else var_95_1d

        return var_metrics

    def _calculate_volatility(self, returns: pd.Series) -> float:
        """Calculate annualized volatility"""
        daily_vol = returns.std()
        annual_vol = daily_vol * np.sqrt(252)  # 252 trading days
        return float(annual_vol)

    async def _calculate_beta(self, returns: pd.Series, benchmark: Optional[str]) -> float:
        """Calculate beta against benchmark"""
        if not benchmark:
            return 1.0

        try:
            # In real implementation, fetch benchmark returns
            # For now, simulate market beta calculation
            market_vol = returns.std() * 0.8  # Assume market is less volatile
            correlation = np.corrcoef(returns, np.random.normal(0, market_vol, len(returns)))[0, 1]
            beta = correlation * (returns.std() / market_vol)
            return float(beta) if not np.isnan(beta) else 1.0
        except:
            return 1.0

    def _calculate_sharpe_ratio(self, returns: pd.Series, risk_free_rate: float = 0.02) -> float:
        """Calculate Sharpe ratio"""
        try:
            excess_returns = returns.mean() * 252 - risk_free_rate  # Annualized excess return
            volatility = returns.std() * np.sqrt(252)  # Annualized volatility
            sharpe = excess_returns / volatility if volatility > 0 else 0
            return float(sharpe) if not np.isnan(sharpe) else 0.0
        except:
            return 0.0

    def _calculate_max_drawdown(self, returns: pd.Series) -> float:
        """Calculate maximum drawdown"""
        try:
            cumulative = (1 + returns).cumprod()
            running_max = cumulative.expanding().max()
            drawdown = (cumulative - running_max) / running_max
            max_dd = drawdown.min()
            return float(abs(max_dd)) if not np.isnan(max_dd) else 0.0
        except:
            return 0.0

    def _calculate_concentration_risk(self, portfolio: Portfolio) -> float:
        """Calculate concentration risk using Herfindahl-Hirschman Index"""
        try:
            if not portfolio.positions:
                return 0.0

            weights = []
            total_value = sum(pos.get('value', 0) for pos in portfolio.positions)

            for position in portfolio.positions:
                weight = position.get('value', 0) / total_value if total_value > 0 else 0
                weights.append(weight)

            # HHI calculation
            hhi = sum(w**2 for w in weights)

            # Normalize to 0-1 scale (1 = maximum concentration)
            n = len(weights)
            normalized_hhi = (hhi - 1/n) / (1 - 1/n) if n > 1 else 0

            return float(normalized_hhi)
        except:
            return 0.0

    async def _calculate_liquidity_score(self, portfolio: Portfolio) -> float:
        """Calculate portfolio liquidity score"""
        try:
            if not portfolio.positions:
                return 1.0

            # Simulate liquidity scoring based on asset classes
            liquidity_scores = {
                'cash': 1.0,
                'government_bonds': 0.9,
                'corporate_bonds': 0.7,
                'large_cap_stocks': 0.8,
                'small_cap_stocks': 0.5,
                'real_estate': 0.3,
                'private_equity': 0.1,
                'commodities': 0.6
            }

            weighted_liquidity = 0
            total_value = sum(pos.get('value', 0) for pos in portfolio.positions)

            for position in portfolio.positions:
                asset_class = position.get('asset_class', 'large_cap_stocks')
                liquidity = liquidity_scores.get(asset_class, 0.5)
                weight = position.get('value', 0) / total_value if total_value > 0 else 0
                weighted_liquidity += liquidity * weight

            return float(weighted_liquidity)
        except:
            return 0.5

    def _determine_risk_level(self, var_metrics: Dict[str, float], volatility: float, concentration_risk: float) -> RiskLevel:
        """Determine overall risk level"""
        # Risk scoring based on multiple factors
        risk_score = 0

        # VaR contribution (0-40 points)
        var_1d_95 = abs(var_metrics['var_1d_95'])
        if var_1d_95 > 0.05:  # >5% daily loss
            risk_score += 40
        elif var_1d_95 > 0.03:  # >3% daily loss
            risk_score += 25
        elif var_1d_95 > 0.02:  # >2% daily loss
            risk_score += 15
        else:
            risk_score += 5

        # Volatility contribution (0-30 points)
        if volatility > 0.4:  # >40% annual volatility
            risk_score += 30
        elif volatility > 0.25:  # >25% annual volatility
            risk_score += 20
        elif volatility > 0.15:  # >15% annual volatility
            risk_score += 10
        else:
            risk_score += 5

        # Concentration risk contribution (0-30 points)
        if concentration_risk > 0.8:
            risk_score += 30
        elif concentration_risk > 0.6:
            risk_score += 20
        elif concentration_risk > 0.4:
            risk_score += 10
        else:
            risk_score += 5

        # Determine risk level
        if risk_score >= 75:
            return RiskLevel.CRITICAL
        elif risk_score >= 55:
            return RiskLevel.HIGH
        elif risk_score >= 35:
            return RiskLevel.MEDIUM
        else:
            return RiskLevel.LOW

    async def run_stress_tests(self, portfolio: Portfolio, scenarios: Optional[List[str]] = None) -> List[StressTestResult]:
        """Run stress tests on portfolio"""
        try:
            if scenarios is None:
                test_scenarios = self.stress_scenarios
            else:
                test_scenarios = [s for s in self.stress_scenarios if s.scenario_id in scenarios]

            results = []

            for scenario in test_scenarios:
                result = await self._execute_stress_test(portfolio, scenario)
                results.append(result)

                # Store result in database
                if self.database_url:
                    await self._store_risk_calculation(
                        portfolio.organization_id,
                        portfolio.portfolio_id,
                        "stress_test",
                        scenario.scenario_id,
                        asdict(result),
                        None
                    )

            logger.info(f"✅ Stress tests completed for portfolio {portfolio.portfolio_id}")
            return results

        except Exception as e:
            logger.error(f"❌ Error running stress tests: {e}")
            raise

    async def _execute_stress_test(self, portfolio: Portfolio, scenario: StressTestScenario) -> StressTestResult:
        """Execute single stress test scenario"""
        try:
            total_loss = 0
            affected_positions = []

            for position in portfolio.positions:
                asset_class = position.get('asset_class', 'equities')
                position_value = position.get('value', 0)

                # Apply shock based on asset class
                shock = 0
                for shock_asset, shock_value in scenario.market_shocks.items():
                    if shock_asset in asset_class.lower() or asset_class.lower() in shock_asset:
                        shock = shock_value
                        break

                if shock == 0 and 'equities' in scenario.market_shocks:
                    shock = scenario.market_shocks['equities']  # Default to equity shock

                position_loss = position_value * abs(shock) if shock < 0 else 0
                total_loss += position_loss

                if position_loss > 0:
                    affected_positions.append(position.get('symbol', position.get('id', 'unknown')))

            loss_percentage = total_loss / portfolio.total_value if portfolio.total_value > 0 else 0

            # Determine risk level based on loss
            if loss_percentage > 0.25:  # >25% loss
                risk_level = RiskLevel.CRITICAL
            elif loss_percentage > 0.15:  # >15% loss
                risk_level = RiskLevel.HIGH
            elif loss_percentage > 0.08:  # >8% loss
                risk_level = RiskLevel.MEDIUM
            else:
                risk_level = RiskLevel.LOW

            return StressTestResult(
                scenario_id=scenario.scenario_id,
                portfolio_id=portfolio.portfolio_id,
                scenario_name=scenario.name,
                potential_loss=total_loss,
                loss_percentage=loss_percentage,
                affected_positions=affected_positions,
                risk_level=risk_level,
                calculated_at=datetime.now(timezone.utc)
            )

        except Exception as e:
            logger.error(f"❌ Error executing stress test {scenario.scenario_id}: {e}")
            raise

    async def _get_portfolio_historical_returns(self, portfolio: Portfolio) -> pd.Series:
        """Get historical returns for portfolio (simulated for demo)"""
        # In real implementation, this would fetch actual historical data
        # For now, simulate returns based on portfolio composition

        days = 252  # 1 year of trading days
        base_volatility = 0.15  # 15% annual volatility

        # Adjust volatility based on portfolio composition
        if portfolio.positions:
            avg_risk = sum(self._get_asset_risk_factor(pos.get('asset_class', 'equities'))
                          for pos in portfolio.positions) / len(portfolio.positions)
            volatility = base_volatility * avg_risk
        else:
            volatility = base_volatility

        # Generate synthetic returns
        daily_vol = volatility / np.sqrt(252)
        returns = np.random.normal(0.0008, daily_vol, days)  # ~20% annual return, realistic volatility

        # Add some autocorrelation and fat tails
        for i in range(1, len(returns)):
            returns[i] += 0.05 * returns[i-1]  # Slight momentum

        # Add occasional large moves (fat tails)
        extreme_days = np.random.choice(days, size=int(days * 0.05), replace=False)
        returns[extreme_days] *= np.random.choice([-2, 2], size=len(extreme_days))

        return pd.Series(returns)

    def _get_asset_risk_factor(self, asset_class: str) -> float:
        """Get risk factor for asset class"""
        risk_factors = {
            'cash': 0.1,
            'government_bonds': 0.3,
            'corporate_bonds': 0.5,
            'large_cap_stocks': 1.0,
            'small_cap_stocks': 1.5,
            'emerging_markets': 2.0,
            'commodities': 1.3,
            'real_estate': 0.8,
            'private_equity': 2.5,
            'crypto': 3.0
        }
        return risk_factors.get(asset_class.lower(), 1.0)

    async def _check_risk_thresholds(self, organization_id: str, portfolio_id: str, metrics: RiskMetrics):
        """Check if risk metrics exceed thresholds and create alerts"""
        if not self.database_url:
            return

        alerts_to_create = []

        # VaR threshold alerts
        if abs(metrics.var_1d_95) > 0.05:  # >5% daily VaR
            alerts_to_create.append({
                'alert_type': 'var_threshold',
                'risk_category': RiskCategory.MARKET.value,
                'risk_level': RiskLevel.HIGH.value,
                'threshold_value': 0.05,
                'current_value': abs(metrics.var_1d_95),
                'message': f'Daily VaR 95% ({abs(metrics.var_1d_95):.2%}) exceeds threshold (5%)'
            })

        # Volatility threshold alerts
        if metrics.volatility > 0.35:  # >35% annual volatility
            alerts_to_create.append({
                'alert_type': 'volatility_threshold',
                'risk_category': RiskCategory.MARKET.value,
                'risk_level': RiskLevel.MEDIUM.value,
                'threshold_value': 0.35,
                'current_value': metrics.volatility,
                'message': f'Portfolio volatility ({metrics.volatility:.2%}) exceeds threshold (35%)'
            })

        # Concentration risk alerts
        if metrics.concentration_risk > 0.7:  # High concentration
            alerts_to_create.append({
                'alert_type': 'concentration_risk',
                'risk_category': RiskCategory.CONCENTRATION.value,
                'risk_level': RiskLevel.HIGH.value,
                'threshold_value': 0.7,
                'current_value': metrics.concentration_risk,
                'message': f'Portfolio concentration risk ({metrics.concentration_risk:.2%}) is high'
            })

        # Liquidity alerts
        if metrics.liquidity_score < 0.3:  # Low liquidity
            alerts_to_create.append({
                'alert_type': 'liquidity_risk',
                'risk_category': RiskCategory.LIQUIDITY.value,
                'risk_level': RiskLevel.MEDIUM.value,
                'threshold_value': 0.3,
                'current_value': metrics.liquidity_score,
                'message': f'Portfolio liquidity score ({metrics.liquidity_score:.2%}) is low'
            })

        # Create alerts in database
        if alerts_to_create:
            with self.SessionLocal() as session:
                for alert_data in alerts_to_create:
                    alert = RiskAlert(
                        organization_id=uuid.UUID(organization_id),
                        portfolio_id=portfolio_id,
                        **alert_data
                    )
                    session.add(alert)
                session.commit()

            logger.info(f"Created {len(alerts_to_create)} risk alerts for portfolio {portfolio_id}")

    async def _store_risk_calculation(self, organization_id: str, portfolio_id: str,
                                     calculation_type: str, method: str, results: Dict[str, Any],
                                     calculation_time_ms: Optional[int]):
        """Store risk calculation in database"""
        if not self.database_url:
            return

        with self.SessionLocal() as session:
            calculation = RiskCalculation(
                organization_id=uuid.UUID(organization_id),
                portfolio_id=portfolio_id,
                calculation_type=calculation_type,
                method=method,
                results=results,
                calculation_time_ms=calculation_time_ms
            )
            session.add(calculation)
            session.commit()

    def _create_default_risk_metrics(self, portfolio_id: str) -> RiskMetrics:
        """Create default risk metrics when data is unavailable"""
        return RiskMetrics(
            portfolio_id=portfolio_id,
            calculated_at=datetime.now(timezone.utc),
            var_1d_95=0.02,  # 2% default VaR
            var_1d_99=0.03,  # 3% default VaR
            var_10d_95=0.06,  # 6% default 10-day VaR
            cvar_95=0.025,   # 2.5% default CVaR
            volatility=0.15,  # 15% default volatility
            beta=1.0,        # Market beta
            sharpe_ratio=0.5, # Moderate Sharpe ratio
            max_drawdown=0.1, # 10% default drawdown
            concentration_risk=0.3, # Moderate concentration
            liquidity_score=0.7,   # Good liquidity
            risk_level=RiskLevel.MEDIUM
        )

    async def get_risk_dashboard_data(self, organization_id: str, portfolio_ids: List[str] = None) -> Dict[str, Any]:
        """Get comprehensive risk dashboard data"""
        try:
            if not self.database_url:
                return {"error": "Database not available"}

            with self.SessionLocal() as session:
                # Get active alerts
                alerts_query = session.query(RiskAlert).filter_by(
                    organization_id=uuid.UUID(organization_id),
                    is_active=True
                )
                if portfolio_ids:
                    alerts_query = alerts_query.filter(RiskAlert.portfolio_id.in_(portfolio_ids))

                active_alerts = alerts_query.order_by(RiskAlert.created_at.desc()).limit(50).all()

                # Get recent risk calculations
                calc_query = session.query(RiskCalculation).filter_by(
                    organization_id=uuid.UUID(organization_id)
                )
                if portfolio_ids:
                    calc_query = calc_query.filter(RiskCalculation.portfolio_id.in_(portfolio_ids))

                recent_calculations = calc_query.order_by(
                    RiskCalculation.calculated_at.desc()
                ).limit(100).all()

                # Aggregate data
                dashboard_data = {
                    "organization_id": organization_id,
                    "generated_at": datetime.now(timezone.utc).isoformat(),
                    "alerts": {
                        "total_active": len(active_alerts),
                        "by_risk_level": {},
                        "by_category": {},
                        "recent": []
                    },
                    "risk_calculations": {
                        "total_recent": len(recent_calculations),
                        "avg_calculation_time": 0,
                        "by_type": {}
                    },
                    "summary": {
                        "portfolios_monitored": len(set(calc.portfolio_id for calc in recent_calculations)),
                        "last_calculation": None
                    }
                }

                # Process alerts
                for alert in active_alerts:
                    risk_level = alert.risk_level
                    dashboard_data["alerts"]["by_risk_level"][risk_level] = dashboard_data["alerts"]["by_risk_level"].get(risk_level, 0) + 1

                    risk_category = alert.risk_category
                    dashboard_data["alerts"]["by_category"][risk_category] = dashboard_data["alerts"]["by_category"].get(risk_category, 0) + 1

                    if len(dashboard_data["alerts"]["recent"]) < 10:
                        dashboard_data["alerts"]["recent"].append({
                            "id": str(alert.id),
                            "portfolio_id": alert.portfolio_id,
                            "alert_type": alert.alert_type,
                            "risk_level": alert.risk_level,
                            "message": alert.message,
                            "created_at": alert.created_at.isoformat()
                        })

                # Process calculations
                calculation_times = [calc.calculation_time_ms for calc in recent_calculations if calc.calculation_time_ms]
                if calculation_times:
                    dashboard_data["risk_calculations"]["avg_calculation_time"] = sum(calculation_times) / len(calculation_times)

                for calc in recent_calculations:
                    calc_type = calc.calculation_type
                    dashboard_data["risk_calculations"]["by_type"][calc_type] = dashboard_data["risk_calculations"]["by_type"].get(calc_type, 0) + 1

                if recent_calculations:
                    dashboard_data["summary"]["last_calculation"] = recent_calculations[0].calculated_at.isoformat()

                return dashboard_data

        except Exception as e:
            logger.error(f"❌ Error getting risk dashboard data: {e}")
            return {"error": str(e)}

# Global instance
risk_engine: Optional[RiskManagementEngine] = None

def get_risk_engine(database_url: str = None) -> RiskManagementEngine:
    """Get global risk management engine instance"""
    global risk_engine
    if risk_engine is None:
        risk_engine = RiskManagementEngine(database_url)
    return risk_engine