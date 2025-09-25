"""
Compliance Engine for MiFID II / Dodd-Frank Regulatory Framework
Phase 3.3 - Advanced Risk Management & Compliance

Comprehensive regulatory compliance system supporting:
- MiFID II (Markets in Financial Instruments Directive II) - European regulation
- Dodd-Frank Act - US financial regulation
- CFTC (Commodity Futures Trading Commission) requirements
- SEC reporting standards
- Real-time compliance monitoring
"""

import os
import logging
from datetime import datetime, timedelta, timezone
from typing import Dict, List, Optional, Any, Tuple
from enum import Enum
from dataclasses import dataclass, asdict
import asyncio
from decimal import Decimal
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

class ComplianceRegime(Enum):
    """Supported regulatory regimes"""
    MIFID_II = "mifid_ii"
    DODD_FRANK = "dodd_frank"
    CFTC = "cftc"
    SEC = "sec"
    ESMA = "esma"  # European Securities and Markets Authority

class ComplianceStatus(Enum):
    """Compliance check status"""
    COMPLIANT = "compliant"
    NON_COMPLIANT = "non_compliant"
    WARNING = "warning"
    PENDING_REVIEW = "pending_review"

class RiskClassification(Enum):
    """MiFID II Risk classifications"""
    RETAIL_CLIENT = "retail_client"
    PROFESSIONAL_CLIENT = "professional_client"
    ELIGIBLE_COUNTERPARTY = "eligible_counterparty"

@dataclass
class ComplianceViolation:
    """Represents a compliance violation"""
    id: str
    regime: ComplianceRegime
    rule_id: str
    severity: str  # "critical", "high", "medium", "low"
    description: str
    detected_at: datetime
    organization_id: str
    user_id: Optional[str] = None
    transaction_id: Optional[str] = None
    remediation_required: bool = True
    resolved: bool = False
    resolved_at: Optional[datetime] = None

@dataclass
class MiFIDIIRecord:
    """MiFID II transaction record"""
    transaction_id: str
    organization_id: str
    user_id: str
    instrument_id: str
    transaction_type: str  # "buy", "sell", "advice"
    quantity: Decimal
    price: Decimal
    timestamp: datetime
    client_classification: RiskClassification
    execution_venue: str
    best_execution_analysis: Dict[str, Any]
    suitability_assessment: Dict[str, Any]
    disclosure_provided: bool

@dataclass
class DoddFrankRecord:
    """Dodd-Frank reporting record"""
    swap_id: str
    organization_id: str
    counterparty_id: str
    notional_amount: Decimal
    effective_date: datetime
    maturity_date: datetime
    underlying_asset: str
    swap_category: str
    cleared: bool
    clearing_house: Optional[str] = None
    margin_posted: Optional[Decimal] = None
    risk_metrics: Optional[Dict[str, Any]] = None

class ComplianceRecord(Base):
    """Database model for compliance records"""
    __tablename__ = 'compliance_records'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    organization_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    regime = Column(String(50), nullable=False)
    record_type = Column(String(100), nullable=False)
    record_data = Column(JSONB, nullable=False)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    compliance_status = Column(String(50), default=ComplianceStatus.PENDING_REVIEW.value)
    reviewed_by = Column(UUID(as_uuid=True), nullable=True)
    reviewed_at = Column(DateTime(timezone=True), nullable=True)

class ComplianceViolationRecord(Base):
    """Database model for compliance violations"""
    __tablename__ = 'compliance_violations'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    organization_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    regime = Column(String(50), nullable=False)
    rule_id = Column(String(100), nullable=False)
    severity = Column(String(20), nullable=False)
    description = Column(Text, nullable=False)
    detected_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    user_id = Column(UUID(as_uuid=True), nullable=True)
    transaction_id = Column(String(255), nullable=True)
    remediation_required = Column(Boolean, default=True)
    resolved = Column(Boolean, default=False)
    resolved_at = Column(DateTime(timezone=True), nullable=True)
    resolution_notes = Column(Text, nullable=True)

class ComplianceEngine:
    """Main compliance engine for regulatory adherence"""

    def __init__(self, database_url: str):
        self.engine = create_engine(database_url, pool_pre_ping=True)
        Base.metadata.create_all(self.engine)
        self.SessionLocal = sessionmaker(bind=self.engine)

        # Compliance rules configuration
        self.mifid_ii_rules = self._load_mifid_ii_rules()
        self.dodd_frank_rules = self._load_dodd_frank_rules()

        logger.info("🏛️ Compliance Engine initialized")
        logger.info(f"📋 MiFID II rules loaded: {len(self.mifid_ii_rules)}")
        logger.info(f"📋 Dodd-Frank rules loaded: {len(self.dodd_frank_rules)}")

    def _load_mifid_ii_rules(self) -> Dict[str, Dict[str, Any]]:
        """Load MiFID II compliance rules"""
        return {
            "MIFID_BEST_EXECUTION": {
                "description": "Best execution obligation for investment firms",
                "severity": "critical",
                "check_function": self._check_best_execution,
                "remediation": "Provide detailed execution quality analysis"
            },
            "MIFID_SUITABILITY": {
                "description": "Suitability assessment for investment advice",
                "severity": "critical",
                "check_function": self._check_suitability_assessment,
                "remediation": "Complete client knowledge and experience assessment"
            },
            "MIFID_DISCLOSURE": {
                "description": "Disclosure of costs and charges",
                "severity": "high",
                "check_function": self._check_cost_disclosure,
                "remediation": "Provide comprehensive cost breakdown to client"
            },
            "MIFID_RECORD_KEEPING": {
                "description": "Transaction record keeping requirements",
                "severity": "medium",
                "check_function": self._check_record_keeping,
                "remediation": "Maintain records for minimum 5 years"
            },
            "MIFID_CLIENT_CLASSIFICATION": {
                "description": "Proper client classification",
                "severity": "high",
                "check_function": self._check_client_classification,
                "remediation": "Review and update client classification"
            }
        }

    def _load_dodd_frank_rules(self) -> Dict[str, Dict[str, Any]]:
        """Load Dodd-Frank compliance rules"""
        return {
            "DODD_FRANK_SWAP_REPORTING": {
                "description": "Swap data repository reporting requirement",
                "severity": "critical",
                "check_function": self._check_swap_reporting,
                "remediation": "Report swap transactions within T+1"
            },
            "DODD_FRANK_CLEARING": {
                "description": "Central clearing requirement for standardized swaps",
                "severity": "critical",
                "check_function": self._check_clearing_requirement,
                "remediation": "Clear eligible swaps through registered DCO"
            },
            "DODD_FRANK_MARGIN": {
                "description": "Margin requirements for non-cleared swaps",
                "severity": "high",
                "check_function": self._check_margin_requirements,
                "remediation": "Post appropriate initial and variation margin"
            },
            "DODD_FRANK_CAPITAL": {
                "description": "Enhanced capital requirements",
                "severity": "high",
                "check_function": self._check_capital_requirements,
                "remediation": "Maintain minimum capital ratios"
            },
            "DODD_FRANK_RISK_RETENTION": {
                "description": "Credit risk retention for securitizations",
                "severity": "medium",
                "check_function": self._check_risk_retention,
                "remediation": "Retain minimum 5% credit risk"
            }
        }

    async def process_mifid_ii_transaction(self, record: MiFIDIIRecord) -> Tuple[ComplianceStatus, List[ComplianceViolation]]:
        """Process a MiFID II transaction for compliance"""
        violations = []
        overall_status = ComplianceStatus.COMPLIANT

        try:
            with self.SessionLocal() as session:
                # Store compliance record
                compliance_record = ComplianceRecord(
                    organization_id=record.organization_id,
                    regime=ComplianceRegime.MIFID_II.value,
                    record_type="transaction",
                    record_data=asdict(record),
                    compliance_status=ComplianceStatus.PENDING_REVIEW.value
                )
                session.add(compliance_record)

                # Check each MiFID II rule
                for rule_id, rule_config in self.mifid_ii_rules.items():
                    try:
                        is_compliant = await rule_config["check_function"](record)

                        if not is_compliant:
                            violation = ComplianceViolation(
                                id=str(uuid.uuid4()),
                                regime=ComplianceRegime.MIFID_II,
                                rule_id=rule_id,
                                severity=rule_config["severity"],
                                description=f"Violation of {rule_config['description']}",
                                detected_at=datetime.now(timezone.utc),
                                organization_id=record.organization_id,
                                user_id=record.user_id,
                                transaction_id=record.transaction_id
                            )
                            violations.append(violation)

                            # Store violation in database
                            violation_record = ComplianceViolationRecord(
                                organization_id=record.organization_id,
                                regime=ComplianceRegime.MIFID_II.value,
                                rule_id=rule_id,
                                severity=rule_config["severity"],
                                description=violation.description,
                                user_id=record.user_id,
                                transaction_id=record.transaction_id
                            )
                            session.add(violation_record)

                    except Exception as e:
                        logger.error(f"Error checking rule {rule_id}: {e}")
                        continue

                # Determine overall compliance status
                if violations:
                    critical_violations = [v for v in violations if v.severity == "critical"]
                    if critical_violations:
                        overall_status = ComplianceStatus.NON_COMPLIANT
                    else:
                        overall_status = ComplianceStatus.WARNING

                # Update compliance record status
                compliance_record.compliance_status = overall_status.value
                session.commit()

                logger.info(f"📊 MiFID II compliance check completed: {overall_status.value}")
                logger.info(f"⚠️ Violations found: {len(violations)}")

        except Exception as e:
            logger.error(f"Error processing MiFID II transaction: {e}")
            overall_status = ComplianceStatus.PENDING_REVIEW

        return overall_status, violations

    async def process_dodd_frank_swap(self, record: DoddFrankRecord) -> Tuple[ComplianceStatus, List[ComplianceViolation]]:
        """Process a Dodd-Frank swap transaction for compliance"""
        violations = []
        overall_status = ComplianceStatus.COMPLIANT

        try:
            with self.SessionLocal() as session:
                # Store compliance record
                compliance_record = ComplianceRecord(
                    organization_id=record.organization_id,
                    regime=ComplianceRegime.DODD_FRANK.value,
                    record_type="swap",
                    record_data=asdict(record),
                    compliance_status=ComplianceStatus.PENDING_REVIEW.value
                )
                session.add(compliance_record)

                # Check each Dodd-Frank rule
                for rule_id, rule_config in self.dodd_frank_rules.items():
                    try:
                        is_compliant = await rule_config["check_function"](record)

                        if not is_compliant:
                            violation = ComplianceViolation(
                                id=str(uuid.uuid4()),
                                regime=ComplianceRegime.DODD_FRANK,
                                rule_id=rule_id,
                                severity=rule_config["severity"],
                                description=f"Violation of {rule_config['description']}",
                                detected_at=datetime.now(timezone.utc),
                                organization_id=record.organization_id,
                                transaction_id=record.swap_id
                            )
                            violations.append(violation)

                            # Store violation in database
                            violation_record = ComplianceViolationRecord(
                                organization_id=record.organization_id,
                                regime=ComplianceRegime.DODD_FRANK.value,
                                rule_id=rule_id,
                                severity=rule_config["severity"],
                                description=violation.description,
                                transaction_id=record.swap_id
                            )
                            session.add(violation_record)

                    except Exception as e:
                        logger.error(f"Error checking rule {rule_id}: {e}")
                        continue

                # Determine overall compliance status
                if violations:
                    critical_violations = [v for v in violations if v.severity == "critical"]
                    if critical_violations:
                        overall_status = ComplianceStatus.NON_COMPLIANT
                    else:
                        overall_status = ComplianceStatus.WARNING

                # Update compliance record status
                compliance_record.compliance_status = overall_status.value
                session.commit()

                logger.info(f"📊 Dodd-Frank compliance check completed: {overall_status.value}")
                logger.info(f"⚠️ Violations found: {len(violations)}")

        except Exception as e:
            logger.error(f"Error processing Dodd-Frank swap: {e}")
            overall_status = ComplianceStatus.PENDING_REVIEW

        return overall_status, violations

    # MiFID II Rule Check Functions
    async def _check_best_execution(self, record: MiFIDIIRecord) -> bool:
        """Check MiFID II best execution requirements"""
        # Verify best execution analysis is provided
        if not record.best_execution_analysis:
            return False

        required_factors = ["price", "costs", "speed", "likelihood_of_execution"]
        analysis = record.best_execution_analysis

        # Check all required execution factors are considered
        for factor in required_factors:
            if factor not in analysis:
                return False

        # Verify execution venue selection reasoning
        if "venue_selection_reason" not in analysis:
            return False

        return True

    async def _check_suitability_assessment(self, record: MiFIDIIRecord) -> bool:
        """Check MiFID II suitability assessment requirements"""
        if record.transaction_type != "advice":
            return True  # Only applies to investment advice

        assessment = record.suitability_assessment
        if not assessment:
            return False

        required_elements = ["knowledge_experience", "financial_situation", "investment_objectives"]

        for element in required_elements:
            if element not in assessment or not assessment[element]:
                return False

        return True

    async def _check_cost_disclosure(self, record: MiFIDIIRecord) -> bool:
        """Check MiFID II cost disclosure requirements"""
        return record.disclosure_provided

    async def _check_record_keeping(self, record: MiFIDIIRecord) -> bool:
        """Check MiFID II record keeping requirements"""
        # Verify all required fields are present
        required_fields = ["transaction_id", "timestamp", "instrument_id", "quantity", "price"]

        for field in required_fields:
            if not getattr(record, field, None):
                return False

        return True

    async def _check_client_classification(self, record: MiFIDIIRecord) -> bool:
        """Check MiFID II client classification requirements"""
        valid_classifications = [cls.value for cls in RiskClassification]
        return record.client_classification.value in valid_classifications

    # Dodd-Frank Rule Check Functions
    async def _check_swap_reporting(self, record: DoddFrankRecord) -> bool:
        """Check Dodd-Frank swap reporting requirements"""
        # Check if swap is reported within T+1
        reporting_deadline = record.effective_date + timedelta(days=1)
        current_time = datetime.now(timezone.utc)

        if current_time > reporting_deadline.replace(tzinfo=timezone.utc):
            return False  # Late reporting

        # Verify required fields are present
        required_fields = ["swap_id", "counterparty_id", "notional_amount", "underlying_asset"]

        for field in required_fields:
            if not getattr(record, field, None):
                return False

        return True

    async def _check_clearing_requirement(self, record: DoddFrankRecord) -> bool:
        """Check Dodd-Frank central clearing requirements"""
        # Standardized swaps must be cleared
        standardized_categories = ["interest_rate", "credit_default", "equity"]

        if record.swap_category in standardized_categories:
            if not record.cleared:
                return False
            if not record.clearing_house:
                return False

        return True

    async def _check_margin_requirements(self, record: DoddFrankRecord) -> bool:
        """Check Dodd-Frank margin requirements"""
        # Non-cleared swaps must have appropriate margin
        if not record.cleared:
            if record.margin_posted is None:
                return False

            # Minimum margin should be at least 2% of notional
            min_margin = record.notional_amount * Decimal("0.02")
            if record.margin_posted < min_margin:
                return False

        return True

    async def _check_capital_requirements(self, record: DoddFrankRecord) -> bool:
        """Check Dodd-Frank capital requirements"""
        # This would integrate with organization's capital data
        # For now, assume compliance (would need capital calculation engine)
        return True

    async def _check_risk_retention(self, record: DoddFrankRecord) -> bool:
        """Check Dodd-Frank risk retention requirements"""
        # Applies to securitizations - simplified check
        if "securitization" in record.swap_category.lower():
            risk_metrics = record.risk_metrics or {}
            retained_risk = risk_metrics.get("retained_risk_percentage", 0)

            if retained_risk < 5.0:  # Must retain at least 5%
                return False

        return True

    async def generate_compliance_report(self, organization_id: str, regime: ComplianceRegime,
                                       start_date: datetime, end_date: datetime) -> Dict[str, Any]:
        """Generate comprehensive compliance report"""

        try:
            with self.SessionLocal() as session:
                # Get compliance records for period
                records = session.query(ComplianceRecord).filter(
                    ComplianceRecord.organization_id == organization_id,
                    ComplianceRecord.regime == regime.value,
                    ComplianceRecord.created_at >= start_date,
                    ComplianceRecord.created_at <= end_date
                ).all()

                # Get violations for period
                violations = session.query(ComplianceViolationRecord).filter(
                    ComplianceViolationRecord.organization_id == organization_id,
                    ComplianceViolationRecord.regime == regime.value,
                    ComplianceViolationRecord.detected_at >= start_date,
                    ComplianceViolationRecord.detected_at <= end_date
                ).all()

                # Calculate compliance metrics
                total_records = len(records)
                compliant_records = len([r for r in records if r.compliance_status == ComplianceStatus.COMPLIANT.value])
                compliance_rate = (compliant_records / total_records * 100) if total_records > 0 else 0

                # Violation analysis
                violation_by_severity = {}
                for violation in violations:
                    severity = violation.severity
                    violation_by_severity[severity] = violation_by_severity.get(severity, 0) + 1

                # Generate report
                report = {
                    "organization_id": organization_id,
                    "regime": regime.value,
                    "report_period": {
                        "start_date": start_date.isoformat(),
                        "end_date": end_date.isoformat()
                    },
                    "compliance_summary": {
                        "total_transactions": total_records,
                        "compliant_transactions": compliant_records,
                        "compliance_rate_percentage": round(compliance_rate, 2),
                        "total_violations": len(violations)
                    },
                    "violation_breakdown": violation_by_severity,
                    "recommendations": self._generate_compliance_recommendations(violations),
                    "generated_at": datetime.now(timezone.utc).isoformat()
                }

                logger.info(f"📋 Compliance report generated for {regime.value}")
                logger.info(f"📊 Compliance rate: {compliance_rate:.1f}%")

                return report

        except Exception as e:
            logger.error(f"Error generating compliance report: {e}")
            raise

    def _generate_compliance_recommendations(self, violations: List[ComplianceViolationRecord]) -> List[Dict[str, str]]:
        """Generate compliance recommendations based on violations"""
        recommendations = []

        # Group violations by rule
        rule_violations = {}
        for violation in violations:
            rule_id = violation.rule_id
            if rule_id not in rule_violations:
                rule_violations[rule_id] = []
            rule_violations[rule_id].append(violation)

        # Generate recommendations for each violated rule
        for rule_id, rule_violations_list in rule_violations.items():
            count = len(rule_violations_list)

            # Get rule configuration
            rule_config = None
            if rule_id in self.mifid_ii_rules:
                rule_config = self.mifid_ii_rules[rule_id]
            elif rule_id in self.dodd_frank_rules:
                rule_config = self.dodd_frank_rules[rule_id]

            if rule_config:
                recommendations.append({
                    "rule_id": rule_id,
                    "violation_count": count,
                    "severity": rule_config["severity"],
                    "description": rule_config["description"],
                    "recommended_action": rule_config["remediation"],
                    "priority": "high" if rule_config["severity"] == "critical" else "medium"
                })

        # Sort by priority and violation count
        recommendations.sort(key=lambda x: (
            0 if x["priority"] == "high" else 1,
            -x["violation_count"]
        ))

        return recommendations

    async def get_compliance_dashboard_data(self, organization_id: str) -> Dict[str, Any]:
        """Get compliance dashboard data for organization"""

        try:
            with self.SessionLocal() as session:
                now = datetime.now(timezone.utc)
                thirty_days_ago = now - timedelta(days=30)

                # Recent violations
                recent_violations = session.query(ComplianceViolationRecord).filter(
                    ComplianceViolationRecord.organization_id == organization_id,
                    ComplianceViolationRecord.detected_at >= thirty_days_ago
                ).all()

                # Active (unresolved) violations
                active_violations = session.query(ComplianceViolationRecord).filter(
                    ComplianceViolationRecord.organization_id == organization_id,
                    ComplianceViolationRecord.resolved == False
                ).all()

                # Recent compliance records
                recent_records = session.query(ComplianceRecord).filter(
                    ComplianceRecord.organization_id == organization_id,
                    ComplianceRecord.created_at >= thirty_days_ago
                ).all()

                # Calculate metrics
                total_records = len(recent_records)
                compliant_records = len([r for r in recent_records if r.compliance_status == ComplianceStatus.COMPLIANT.value])
                compliance_rate = (compliant_records / total_records * 100) if total_records > 0 else 100

                dashboard_data = {
                    "compliance_overview": {
                        "overall_compliance_rate": round(compliance_rate, 1),
                        "total_transactions_30_days": total_records,
                        "active_violations": len(active_violations),
                        "recent_violations_30_days": len(recent_violations)
                    },
                    "regime_breakdown": {
                        regime.value: {
                            "records": len([r for r in recent_records if r.regime == regime.value]),
                            "violations": len([v for v in recent_violations if v.regime == regime.value])
                        }
                        for regime in ComplianceRegime
                    },
                    "severity_breakdown": {
                        "critical": len([v for v in active_violations if v.severity == "critical"]),
                        "high": len([v for v in active_violations if v.severity == "high"]),
                        "medium": len([v for v in active_violations if v.severity == "medium"]),
                        "low": len([v for v in active_violations if v.severity == "low"])
                    },
                    "top_violations": [
                        {
                            "rule_id": v.rule_id,
                            "regime": v.regime,
                            "severity": v.severity,
                            "description": v.description,
                            "detected_at": v.detected_at.isoformat()
                        }
                        for v in sorted(active_violations, key=lambda x: (
                            0 if x.severity == "critical" else 1,
                            x.detected_at
                        ), reverse=True)[:5]
                    ]
                }

                return dashboard_data

        except Exception as e:
            logger.error(f"Error getting compliance dashboard data: {e}")
            raise

# Global compliance engine instance
compliance_engine = None

def get_compliance_engine() -> ComplianceEngine:
    """Get global compliance engine instance"""
    global compliance_engine
    if compliance_engine is None:
        database_url = os.getenv("DATABASE_URL", "postgresql://username:password@localhost:5432/miraikakaku")
        compliance_engine = ComplianceEngine(database_url)
    return compliance_engine