"""
Automated Regulatory Reporting Engine
Phase 3.3 - Advanced Risk Management & Compliance

Comprehensive regulatory reporting system supporting:
- MiFID II transaction reporting (RTS 22/23/24)
- Dodd-Frank swap reporting (SDR)
- EMIR trade reporting (EU)
- CFTC position reporting (US)
- Automated report generation and submission
- Regulatory deadline tracking
"""

import os
import logging
from datetime import datetime, timedelta, timezone
from typing import Dict, List, Optional, Any, Tuple
from enum import Enum
from dataclasses import dataclass, asdict
import asyncio
import json
import xml.etree.ElementTree as ET
from decimal import Decimal
import uuid

from sqlalchemy import create_engine, Column, String, Float, DateTime, Integer, Boolean, Text, DECIMAL
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.dialects.postgresql import UUID, JSONB

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

Base = declarative_base()

class ReportType(Enum):
    """Types of regulatory reports"""
    MIFID_II_TRANSACTION = "mifid_ii_transaction"
    DODD_FRANK_SWAP = "dodd_frank_swap"
    EMIR_TRADE = "emir_trade"
    CFTC_POSITION = "cftc_position"
    VAR_DISCLOSURE = "var_disclosure"
    STRESS_TEST_RESULTS = "stress_test_results"
    COMPLIANCE_SUMMARY = "compliance_summary"

class ReportStatus(Enum):
    """Report processing status"""
    PENDING = "pending"
    GENERATED = "generated"
    SUBMITTED = "submitted"
    ACKNOWLEDGED = "acknowledged"
    REJECTED = "rejected"
    EXPIRED = "expired"

class ReportFormat(Enum):
    """Report output formats"""
    XML = "xml"
    JSON = "json"
    CSV = "csv"
    PDF = "pdf"
    SWIFT = "swift"

@dataclass
class ReportingDeadline:
    """Regulatory reporting deadline"""
    report_type: ReportType
    regime: str
    frequency: str  # "daily", "weekly", "monthly", "quarterly", "annual"
    deadline_time: str  # "T+1", "end_of_month", etc.
    jurisdiction: str
    mandatory: bool
    description: str

@dataclass
class ReportTemplate:
    """Template for generating reports"""
    template_id: str
    report_type: ReportType
    version: str
    format: ReportFormat
    required_fields: List[str]
    validation_rules: Dict[str, Any]
    template_content: str
    created_at: datetime
    updated_at: datetime

@dataclass
class GeneratedReport:
    """Generated regulatory report"""
    report_id: str
    organization_id: str
    report_type: ReportType
    report_period_start: datetime
    report_period_end: datetime
    generated_at: datetime
    due_date: datetime
    status: ReportStatus
    format: ReportFormat
    file_path: Optional[str] = None
    submission_reference: Optional[str] = None
    acknowledgment_received: bool = False
    error_messages: List[str] = None

class RegulatoryReport(Base):
    """Database model for regulatory reports"""
    __tablename__ = 'regulatory_reports'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    organization_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    report_type = Column(String(100), nullable=False)
    report_period_start = Column(DateTime(timezone=True), nullable=False)
    report_period_end = Column(DateTime(timezone=True), nullable=False)
    generated_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    due_date = Column(DateTime(timezone=True), nullable=False)
    status = Column(String(50), default=ReportStatus.PENDING.value)
    format = Column(String(20), nullable=False)
    file_path = Column(String(500), nullable=True)
    submission_reference = Column(String(255), nullable=True)
    acknowledgment_received = Column(Boolean, default=False)
    error_messages = Column(JSONB, default=list)
    report_data = Column(JSONB, nullable=False)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow)

class ReportingSchedule(Base):
    """Database model for reporting schedules"""
    __tablename__ = 'reporting_schedules'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    organization_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    report_type = Column(String(100), nullable=False)
    frequency = Column(String(50), nullable=False)
    enabled = Column(Boolean, default=True)
    last_generated = Column(DateTime(timezone=True), nullable=True)
    next_due_date = Column(DateTime(timezone=True), nullable=False)
    auto_submit = Column(Boolean, default=False)
    notification_settings = Column(JSONB, default=dict)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow)

class RegulatoryReportingEngine:
    """Main regulatory reporting engine"""

    def __init__(self, database_url: str):
        self.engine = create_engine(database_url, pool_pre_ping=True)
        Base.metadata.create_all(self.engine)
        self.SessionLocal = sessionmaker(bind=self.engine)

        # Initialize reporting deadlines and templates
        self.reporting_deadlines = self._initialize_reporting_deadlines()
        self.report_templates = self._initialize_report_templates()

        logger.info("📊 Regulatory Reporting Engine initialized")
        logger.info(f"📋 Reporting deadlines loaded: {len(self.reporting_deadlines)}")
        logger.info(f"📄 Report templates loaded: {len(self.report_templates)}")

    def _initialize_reporting_deadlines(self) -> Dict[ReportType, ReportingDeadline]:
        """Initialize regulatory reporting deadlines"""

        deadlines = {
            ReportType.MIFID_II_TRANSACTION: ReportingDeadline(
                report_type=ReportType.MIFID_II_TRANSACTION,
                regime="MiFID II",
                frequency="daily",
                deadline_time="T+1",
                jurisdiction="EU",
                mandatory=True,
                description="Transaction reporting under MiFID II RTS 22"
            ),

            ReportType.DODD_FRANK_SWAP: ReportingDeadline(
                report_type=ReportType.DODD_FRANK_SWAP,
                regime="Dodd-Frank",
                frequency="daily",
                deadline_time="T+1",
                jurisdiction="US",
                mandatory=True,
                description="Swap data repository reporting under Dodd-Frank"
            ),

            ReportType.EMIR_TRADE: ReportingDeadline(
                report_type=ReportType.EMIR_TRADE,
                regime="EMIR",
                frequency="daily",
                deadline_time="T+1",
                jurisdiction="EU",
                mandatory=True,
                description="Trade reporting under EMIR regulation"
            ),

            ReportType.CFTC_POSITION: ReportingDeadline(
                report_type=ReportType.CFTC_POSITION,
                regime="CFTC",
                frequency="daily",
                deadline_time="T+1",
                jurisdiction="US",
                mandatory=True,
                description="Position reporting to CFTC"
            ),

            ReportType.VAR_DISCLOSURE: ReportingDeadline(
                report_type=ReportType.VAR_DISCLOSURE,
                regime="Basel III",
                frequency="quarterly",
                deadline_time="end_of_quarter_plus_45_days",
                jurisdiction="Global",
                mandatory=False,
                description="VaR disclosure for market risk"
            ),

            ReportType.STRESS_TEST_RESULTS: ReportingDeadline(
                report_type=ReportType.STRESS_TEST_RESULTS,
                regime="CCAR/EBA",
                frequency="annual",
                deadline_time="end_of_year_plus_90_days",
                jurisdiction="US/EU",
                mandatory=False,
                description="Stress test results submission"
            )
        }

        return deadlines

    def _initialize_report_templates(self) -> Dict[str, ReportTemplate]:
        """Initialize report templates"""

        templates = {}

        # MiFID II Transaction Report Template
        mifid_template = ReportTemplate(
            template_id="mifid_ii_transaction_v1",
            report_type=ReportType.MIFID_II_TRANSACTION,
            version="1.0",
            format=ReportFormat.XML,
            required_fields=[
                "transaction_reference_number",
                "trading_date",
                "trading_time",
                "instrument_identification",
                "buy_sell_indicator",
                "quantity",
                "price",
                "venue_of_execution",
                "investment_firm_id"
            ],
            validation_rules={
                "quantity": {"type": "decimal", "min": 0},
                "price": {"type": "decimal", "min": 0},
                "trading_date": {"type": "date", "format": "YYYY-MM-DD"},
                "buy_sell_indicator": {"type": "enum", "values": ["B", "S"]}
            },
            template_content=self._get_mifid_xml_template(),
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc)
        )
        templates[mifid_template.template_id] = mifid_template

        # Dodd-Frank Swap Report Template
        dodd_frank_template = ReportTemplate(
            template_id="dodd_frank_swap_v1",
            report_type=ReportType.DODD_FRANK_SWAP,
            version="1.0",
            format=ReportFormat.JSON,
            required_fields=[
                "unique_swap_identifier",
                "counterparty_id",
                "notional_amount",
                "effective_date",
                "maturity_date",
                "underlying_asset",
                "cleared_indicator",
                "clearing_house"
            ],
            validation_rules={
                "notional_amount": {"type": "decimal", "min": 0},
                "cleared_indicator": {"type": "boolean"},
                "effective_date": {"type": "date"},
                "maturity_date": {"type": "date"}
            },
            template_content=self._get_dodd_frank_json_template(),
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc)
        )
        templates[dodd_frank_template.template_id] = dodd_frank_template

        return templates

    def _get_mifid_xml_template(self) -> str:
        """Get MiFID II XML template"""
        return """<?xml version="1.0" encoding="UTF-8"?>
<Document xmlns="urn:iso:std:iso:20022:tech:xsd:auth.036.001.02">
    <FinInstrmRptgTxRpt>
        <GrpHdr>
            <MsgId>{message_id}</MsgId>
            <CreDtTm>{creation_datetime}</CreDtTm>
            <RptgNtty>
                <LEI>{lei}</LEI>
            </RptgNtty>
        </GrpHdr>
        <Tx>
            <TxId>{transaction_id}</TxId>
            <ExctgPty>
                <LEI>{executing_entity_lei}</LEI>
            </ExctgPty>
            <InvstmtPtyInd>{investment_party_indicator}</InvstmtPtyInd>
            <SubmitgPty>
                <LEI>{submitting_entity_lei}</LEI>
            </SubmitgPty>
            <Buyr>
                <LEI>{buyer_lei}</LEI>
            </Buyr>
            <Sellr>
                <LEI>{seller_lei}</LEI>
            </Sellr>
            <TradDt>{trade_date}</TradDt>
            <TradgTm>{trading_time}</TradgTm>
            <FinInstrm>
                <ISIN>{isin}</ISIN>
            </FinInstrm>
            <BuySellInd>{buy_sell_indicator}</BuySellInd>
            <Qty>{quantity}</Qty>
            <Pric>
                <Pdg>{price}</Pdg>
            </Pric>
            <TradVn>{venue_code}</TradVn>
        </Tx>
    </FinInstrmRptgTxRpt>
</Document>"""

    def _get_dodd_frank_json_template(self) -> str:
        """Get Dodd-Frank JSON template"""
        return """{
    "header": {
        "message_type": "swap_report",
        "version": "1.0",
        "timestamp": "{timestamp}",
        "reporting_entity": "{reporting_entity_id}"
    },
    "swap_data": {
        "unique_swap_identifier": "{unique_swap_identifier}",
        "counterparty_1_id": "{counterparty_1_id}",
        "counterparty_2_id": "{counterparty_2_id}",
        "notional_amount": {notional_amount},
        "currency": "{currency}",
        "effective_date": "{effective_date}",
        "maturity_date": "{maturity_date}",
        "underlying_asset": "{underlying_asset}",
        "swap_category": "{swap_category}",
        "cleared": {cleared_indicator},
        "clearing_house": "{clearing_house}",
        "margin_posted": {margin_posted}
    }
}"""

    async def generate_report(
        self,
        organization_id: str,
        report_type: ReportType,
        period_start: datetime,
        period_end: datetime,
        format: ReportFormat = ReportFormat.JSON,
        auto_submit: bool = False
    ) -> GeneratedReport:
        """Generate a regulatory report"""

        logger.info(f"📊 Generating {report_type.value} report for period {period_start} to {period_end}")

        try:
            # Get data for the report
            report_data = await self._collect_report_data(
                organization_id, report_type, period_start, period_end
            )

            # Calculate due date
            due_date = self._calculate_due_date(report_type, period_end)

            # Generate report content
            report_content = await self._generate_report_content(
                report_type, report_data, format
            )

            # Create report record
            report = GeneratedReport(
                report_id=str(uuid.uuid4()),
                organization_id=organization_id,
                report_type=report_type,
                report_period_start=period_start,
                report_period_end=period_end,
                generated_at=datetime.now(timezone.utc),
                due_date=due_date,
                status=ReportStatus.GENERATED,
                format=format,
                file_path=f"reports/{organization_id}/{report_type.value}_{period_start.strftime('%Y%m%d')}_{period_end.strftime('%Y%m%d')}.{format.value}"
            )

            # Save report content to file
            await self._save_report_file(report, report_content)

            # Store in database
            await self._store_report_record(report, report_data)

            # Auto-submit if requested
            if auto_submit:
                await self.submit_report(report.report_id, organization_id)

            logger.info(f"✅ Report generated successfully: {report.report_id}")

            return report

        except Exception as e:
            logger.error(f"❌ Error generating report: {e}")
            raise

    async def _collect_report_data(
        self,
        organization_id: str,
        report_type: ReportType,
        period_start: datetime,
        period_end: datetime
    ) -> Dict[str, Any]:
        """Collect data for report generation"""

        try:
            with self.SessionLocal() as session:
                data = {}

                if report_type == ReportType.MIFID_II_TRANSACTION:
                    # Collect MiFID II transaction data
                    from services.compliance_engine import ComplianceRecord

                    records = session.query(ComplianceRecord).filter(
                        ComplianceRecord.organization_id == organization_id,
                        ComplianceRecord.regime == "mifid_ii",
                        ComplianceRecord.created_at >= period_start,
                        ComplianceRecord.created_at <= period_end
                    ).all()

                    data["transactions"] = [
                        {
                            "transaction_id": record.record_data.get("transaction_id"),
                            "timestamp": record.created_at.isoformat(),
                            "instrument_id": record.record_data.get("instrument_id"),
                            "quantity": record.record_data.get("quantity"),
                            "price": record.record_data.get("price"),
                            "execution_venue": record.record_data.get("execution_venue"),
                            "transaction_type": record.record_data.get("transaction_type")
                        }
                        for record in records
                    ]

                elif report_type == ReportType.VAR_DISCLOSURE:
                    # Collect VaR data
                    from services.var_calculation_engine import VaRCalculation

                    var_records = session.query(VaRCalculation).filter(
                        VaRCalculation.organization_id == organization_id,
                        VaRCalculation.created_at >= period_start,
                        VaRCalculation.created_at <= period_end
                    ).all()

                    data["var_metrics"] = [
                        {
                            "portfolio_id": record.portfolio_id,
                            "method": record.method,
                            "confidence_level": record.confidence_level,
                            "var_amount": float(record.var_amount),
                            "expected_shortfall": float(record.expected_shortfall),
                            "calculation_date": record.created_at.isoformat()
                        }
                        for record in var_records
                    ]

                elif report_type == ReportType.STRESS_TEST_RESULTS:
                    # Collect stress test data
                    from services.stress_testing_engine import StressTestRecord

                    stress_records = session.query(StressTestRecord).filter(
                        StressTestRecord.organization_id == organization_id,
                        StressTestRecord.created_at >= period_start,
                        StressTestRecord.created_at <= period_end
                    ).all()

                    data["stress_tests"] = [
                        {
                            "portfolio_id": record.portfolio_id,
                            "scenario_name": record.scenario_name,
                            "severity": record.severity,
                            "absolute_loss": float(record.absolute_loss),
                            "percentage_loss": record.percentage_loss,
                            "test_date": record.created_at.isoformat()
                        }
                        for record in stress_records
                    ]

                return data

        except Exception as e:
            logger.error(f"Error collecting report data: {e}")
            raise

    def _calculate_due_date(self, report_type: ReportType, period_end: datetime) -> datetime:
        """Calculate report due date based on regulatory requirements"""

        if report_type not in self.reporting_deadlines:
            # Default to T+5 business days
            return period_end + timedelta(days=7)

        deadline = self.reporting_deadlines[report_type]

        if deadline.deadline_time == "T+1":
            return period_end + timedelta(days=1)
        elif deadline.deadline_time == "end_of_month":
            next_month = period_end.replace(day=28) + timedelta(days=4)
            return next_month - timedelta(days=next_month.day - 1)
        elif deadline.deadline_time == "end_of_quarter_plus_45_days":
            # Calculate end of quarter
            quarter_end_month = 3 * ((period_end.month - 1) // 3) + 3
            quarter_end = period_end.replace(month=quarter_end_month, day=1) + timedelta(days=32)
            quarter_end = quarter_end.replace(day=1) - timedelta(days=1)
            return quarter_end + timedelta(days=45)
        else:
            # Default fallback
            return period_end + timedelta(days=7)

    async def _generate_report_content(
        self,
        report_type: ReportType,
        data: Dict[str, Any],
        format: ReportFormat
    ) -> str:
        """Generate report content in specified format"""

        try:
            if format == ReportFormat.JSON:
                return json.dumps(data, indent=2, default=str)

            elif format == ReportFormat.XML:
                # Generate XML content (simplified)
                root = ET.Element("RegulatoryReport")
                ET.SubElement(root, "ReportType").text = report_type.value
                ET.SubElement(root, "GeneratedAt").text = datetime.now(timezone.utc).isoformat()

                data_element = ET.SubElement(root, "Data")
                self._dict_to_xml(data, data_element)

                return ET.tostring(root, encoding='unicode')

            elif format == ReportFormat.CSV:
                # Generate CSV content (simplified)
                csv_lines = []
                if "transactions" in data:
                    csv_lines.append("TransactionID,Timestamp,InstrumentID,Quantity,Price,Venue,Type")
                    for tx in data["transactions"]:
                        csv_lines.append(f"{tx['transaction_id']},{tx['timestamp']},{tx['instrument_id']},{tx['quantity']},{tx['price']},{tx.get('execution_venue', '')},{tx.get('transaction_type', '')}")

                return "\n".join(csv_lines)

            else:
                # Default to JSON
                return json.dumps(data, indent=2, default=str)

        except Exception as e:
            logger.error(f"Error generating report content: {e}")
            raise

    def _dict_to_xml(self, data: Dict[str, Any], parent: ET.Element):
        """Convert dictionary to XML elements"""
        for key, value in data.items():
            if isinstance(value, dict):
                child = ET.SubElement(parent, key)
                self._dict_to_xml(value, child)
            elif isinstance(value, list):
                for item in value:
                    child = ET.SubElement(parent, key)
                    if isinstance(item, dict):
                        self._dict_to_xml(item, child)
                    else:
                        child.text = str(item)
            else:
                ET.SubElement(parent, key).text = str(value)

    async def _save_report_file(self, report: GeneratedReport, content: str):
        """Save report content to file"""

        try:
            # Create directory if it doesn't exist
            os.makedirs(os.path.dirname(report.file_path), exist_ok=True)

            # Write report content
            with open(report.file_path, 'w', encoding='utf-8') as f:
                f.write(content)

            logger.info(f"💾 Report saved to {report.file_path}")

        except Exception as e:
            logger.error(f"Error saving report file: {e}")
            raise

    async def _store_report_record(self, report: GeneratedReport, data: Dict[str, Any]):
        """Store report record in database"""

        try:
            with self.SessionLocal() as session:
                report_record = RegulatoryReport(
                    organization_id=report.organization_id,
                    report_type=report.report_type.value,
                    report_period_start=report.report_period_start,
                    report_period_end=report.report_period_end,
                    generated_at=report.generated_at,
                    due_date=report.due_date,
                    status=report.status.value,
                    format=report.format.value,
                    file_path=report.file_path,
                    report_data=data
                )

                session.add(report_record)
                session.commit()

                logger.info(f"💾 Report record stored in database")

        except Exception as e:
            logger.error(f"Error storing report record: {e}")
            raise

    async def submit_report(self, report_id: str, organization_id: str) -> bool:
        """Submit report to regulatory authority (simulation)"""

        logger.info(f"📤 Submitting report {report_id}")

        try:
            with self.SessionLocal() as session:
                report = session.query(RegulatoryReport).filter(
                    RegulatoryReport.id == report_id,
                    RegulatoryReport.organization_id == organization_id
                ).first()

                if not report:
                    raise ValueError(f"Report {report_id} not found")

                # Simulate submission to regulatory authority
                # In a real implementation, this would integrate with regulatory APIs
                submission_reference = f"SUB_{report_id[:8]}_{datetime.now().strftime('%Y%m%d%H%M%S')}"

                # Update report status
                report.status = ReportStatus.SUBMITTED.value
                report.submission_reference = submission_reference
                report.updated_at = datetime.now(timezone.utc)

                session.commit()

                logger.info(f"✅ Report submitted with reference: {submission_reference}")

                return True

        except Exception as e:
            logger.error(f"❌ Error submitting report: {e}")
            return False

    async def get_report_status(self, report_id: str, organization_id: str) -> Dict[str, Any]:
        """Get report status and details"""

        try:
            with self.SessionLocal() as session:
                report = session.query(RegulatoryReport).filter(
                    RegulatoryReport.id == report_id,
                    RegulatoryReport.organization_id == organization_id
                ).first()

                if not report:
                    return {"error": "Report not found"}

                return {
                    "report_id": str(report.id),
                    "report_type": report.report_type,
                    "status": report.status,
                    "generated_at": report.generated_at.isoformat(),
                    "due_date": report.due_date.isoformat(),
                    "submission_reference": report.submission_reference,
                    "acknowledgment_received": report.acknowledgment_received,
                    "file_path": report.file_path,
                    "error_messages": report.error_messages
                }

        except Exception as e:
            logger.error(f"Error getting report status: {e}")
            raise

    async def get_upcoming_deadlines(
        self,
        organization_id: str,
        days_ahead: int = 30
    ) -> List[Dict[str, Any]]:
        """Get upcoming reporting deadlines"""

        try:
            with self.SessionLocal() as session:
                deadline_date = datetime.now(timezone.utc) + timedelta(days=days_ahead)

                schedules = session.query(ReportingSchedule).filter(
                    ReportingSchedule.organization_id == organization_id,
                    ReportingSchedule.enabled == True,
                    ReportingSchedule.next_due_date <= deadline_date
                ).all()

                deadlines = []
                for schedule in schedules:
                    deadline_info = self.reporting_deadlines.get(ReportType(schedule.report_type))

                    deadlines.append({
                        "report_type": schedule.report_type,
                        "next_due_date": schedule.next_due_date.isoformat(),
                        "frequency": schedule.frequency,
                        "mandatory": deadline_info.mandatory if deadline_info else False,
                        "jurisdiction": deadline_info.jurisdiction if deadline_info else "Unknown",
                        "auto_submit": schedule.auto_submit,
                        "days_until_due": (schedule.next_due_date - datetime.now(timezone.utc)).days
                    })

                # Sort by due date
                deadlines.sort(key=lambda x: x["next_due_date"])

                return deadlines

        except Exception as e:
            logger.error(f"Error getting upcoming deadlines: {e}")
            raise

# Global reporting engine instance
reporting_engine = None

def get_reporting_engine() -> RegulatoryReportingEngine:
    """Get global regulatory reporting engine instance"""
    global reporting_engine
    if reporting_engine is None:
        database_url = os.getenv("DATABASE_URL", "postgresql://username:password@localhost:5432/miraikakaku")
        reporting_engine = RegulatoryReportingEngine(database_url)
    return reporting_engine