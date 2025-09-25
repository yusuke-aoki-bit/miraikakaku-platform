"""
Compliance API Router
Phase 3.3 - Advanced Risk Management & Compliance

FastAPI endpoints for regulatory compliance management
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from fastapi.responses import JSONResponse
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta, timezone
from pydantic import BaseModel, Field
from decimal import Decimal

from middleware.tenant_auth import get_tenant_context, TenantContext
from services.compliance_engine import (
    get_compliance_engine,
    ComplianceEngine,
    ComplianceRegime,
    ComplianceStatus,
    RiskClassification,
    MiFIDIIRecord,
    DoddFrankRecord
)

router = APIRouter(prefix="/api/v1/compliance", tags=["Compliance"])

# Pydantic models for API requests/responses

class MiFIDIITransactionRequest(BaseModel):
    """MiFID II transaction submission request"""
    transaction_id: str = Field(..., description="Unique transaction identifier")
    user_id: str = Field(..., description="User performing the transaction")
    instrument_id: str = Field(..., description="Financial instrument identifier")
    transaction_type: str = Field(..., description="Transaction type: buy, sell, advice")
    quantity: Decimal = Field(..., description="Transaction quantity")
    price: Decimal = Field(..., description="Transaction price")
    client_classification: RiskClassification = Field(..., description="Client risk classification")
    execution_venue: str = Field(..., description="Execution venue")
    best_execution_analysis: Dict[str, Any] = Field(..., description="Best execution analysis data")
    suitability_assessment: Optional[Dict[str, Any]] = Field(None, description="Suitability assessment (for advice)")
    disclosure_provided: bool = Field(..., description="Whether cost disclosure was provided")

class DoddFrankSwapRequest(BaseModel):
    """Dodd-Frank swap submission request"""
    swap_id: str = Field(..., description="Unique swap identifier")
    counterparty_id: str = Field(..., description="Counterparty identifier")
    notional_amount: Decimal = Field(..., description="Swap notional amount")
    effective_date: datetime = Field(..., description="Swap effective date")
    maturity_date: datetime = Field(..., description="Swap maturity date")
    underlying_asset: str = Field(..., description="Underlying asset")
    swap_category: str = Field(..., description="Swap category")
    cleared: bool = Field(..., description="Whether swap is centrally cleared")
    clearing_house: Optional[str] = Field(None, description="Clearing house (if cleared)")
    margin_posted: Optional[Decimal] = Field(None, description="Posted margin amount")
    risk_metrics: Optional[Dict[str, Any]] = Field(None, description="Risk metrics data")

class ComplianceReportRequest(BaseModel):
    """Compliance report generation request"""
    regime: ComplianceRegime = Field(..., description="Regulatory regime")
    start_date: datetime = Field(..., description="Report start date")
    end_date: datetime = Field(..., description="Report end date")

class ComplianceViolationResponse(BaseModel):
    """Compliance violation response"""
    id: str
    regime: str
    rule_id: str
    severity: str
    description: str
    detected_at: datetime
    user_id: Optional[str] = None
    transaction_id: Optional[str] = None
    remediation_required: bool
    resolved: bool
    resolved_at: Optional[datetime] = None

@router.post("/mifid-ii/transaction")
async def submit_mifid_ii_transaction(
    request: MiFIDIITransactionRequest,
    context: TenantContext = Depends(get_tenant_context),
    compliance_engine: ComplianceEngine = Depends(get_compliance_engine)
):
    """
    Submit MiFID II transaction for compliance processing

    Processes the transaction against all relevant MiFID II regulations:
    - Best execution requirements
    - Suitability assessment (for advice transactions)
    - Cost disclosure obligations
    - Record keeping standards
    - Client classification validation
    """
    try:
        # Create MiFID II record
        mifid_record = MiFIDIIRecord(
            transaction_id=request.transaction_id,
            organization_id=context.organization_id,
            user_id=request.user_id,
            instrument_id=request.instrument_id,
            transaction_type=request.transaction_type,
            quantity=request.quantity,
            price=request.price,
            timestamp=datetime.now(timezone.utc),
            client_classification=request.client_classification,
            execution_venue=request.execution_venue,
            best_execution_analysis=request.best_execution_analysis,
            suitability_assessment=request.suitability_assessment or {},
            disclosure_provided=request.disclosure_provided
        )

        # Process compliance check
        compliance_status, violations = await compliance_engine.process_mifid_ii_transaction(mifid_record)

        # Convert violations to response format
        violation_responses = [
            ComplianceViolationResponse(
                id=v.id,
                regime=v.regime.value,
                rule_id=v.rule_id,
                severity=v.severity,
                description=v.description,
                detected_at=v.detected_at,
                user_id=v.user_id,
                transaction_id=v.transaction_id,
                remediation_required=v.remediation_required,
                resolved=v.resolved,
                resolved_at=v.resolved_at
            )
            for v in violations
        ]

        return {
            "transaction_id": request.transaction_id,
            "compliance_status": compliance_status.value,
            "violations": [v.dict() for v in violation_responses],
            "processed_at": datetime.now(timezone.utc).isoformat(),
            "regime": "mifid_ii"
        }

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error processing MiFID II transaction: {str(e)}"
        )

@router.post("/dodd-frank/swap")
async def submit_dodd_frank_swap(
    request: DoddFrankSwapRequest,
    context: TenantContext = Depends(get_tenant_context),
    compliance_engine: ComplianceEngine = Depends(get_compliance_engine)
):
    """
    Submit Dodd-Frank swap for compliance processing

    Processes the swap against all relevant Dodd-Frank regulations:
    - Swap data repository reporting
    - Central clearing requirements
    - Margin requirements for non-cleared swaps
    - Capital requirements
    - Risk retention obligations
    """
    try:
        # Create Dodd-Frank record
        dodd_frank_record = DoddFrankRecord(
            swap_id=request.swap_id,
            organization_id=context.organization_id,
            counterparty_id=request.counterparty_id,
            notional_amount=request.notional_amount,
            effective_date=request.effective_date,
            maturity_date=request.maturity_date,
            underlying_asset=request.underlying_asset,
            swap_category=request.swap_category,
            cleared=request.cleared,
            clearing_house=request.clearing_house,
            margin_posted=request.margin_posted,
            risk_metrics=request.risk_metrics or {}
        )

        # Process compliance check
        compliance_status, violations = await compliance_engine.process_dodd_frank_swap(dodd_frank_record)

        # Convert violations to response format
        violation_responses = [
            ComplianceViolationResponse(
                id=v.id,
                regime=v.regime.value,
                rule_id=v.rule_id,
                severity=v.severity,
                description=v.description,
                detected_at=v.detected_at,
                user_id=v.user_id,
                transaction_id=v.transaction_id,
                remediation_required=v.remediation_required,
                resolved=v.resolved,
                resolved_at=v.resolved_at
            )
            for v in violations
        ]

        return {
            "swap_id": request.swap_id,
            "compliance_status": compliance_status.value,
            "violations": [v.dict() for v in violation_responses],
            "processed_at": datetime.now(timezone.utc).isoformat(),
            "regime": "dodd_frank"
        }

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error processing Dodd-Frank swap: {str(e)}"
        )

@router.post("/reports/generate")
async def generate_compliance_report(
    request: ComplianceReportRequest,
    context: TenantContext = Depends(get_tenant_context),
    compliance_engine: ComplianceEngine = Depends(get_compliance_engine)
):
    """
    Generate comprehensive compliance report for specified regime and period

    Reports include:
    - Compliance rate statistics
    - Violation breakdown by severity
    - Rule-specific analysis
    - Remediation recommendations
    """
    try:
        # Validate date range
        if request.end_date <= request.start_date:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="End date must be after start date"
            )

        # Generate report
        report = await compliance_engine.generate_compliance_report(
            organization_id=context.organization_id,
            regime=request.regime,
            start_date=request.start_date,
            end_date=request.end_date
        )

        return report

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error generating compliance report: {str(e)}"
        )

@router.get("/dashboard")
async def get_compliance_dashboard(
    context: TenantContext = Depends(get_tenant_context),
    compliance_engine: ComplianceEngine = Depends(get_compliance_engine)
):
    """
    Get compliance dashboard data for organization

    Returns real-time compliance metrics:
    - Overall compliance rate
    - Active violations by severity
    - Recent compliance activity
    - Regime-specific breakdown
    """
    try:
        dashboard_data = await compliance_engine.get_compliance_dashboard_data(
            organization_id=context.organization_id
        )

        return dashboard_data

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error getting compliance dashboard: {str(e)}"
        )

@router.get("/violations")
async def get_compliance_violations(
    context: TenantContext = Depends(get_tenant_context),
    compliance_engine: ComplianceEngine = Depends(get_compliance_engine),
    regime: Optional[ComplianceRegime] = Query(None, description="Filter by regulatory regime"),
    severity: Optional[str] = Query(None, description="Filter by violation severity"),
    resolved: Optional[bool] = Query(None, description="Filter by resolution status"),
    limit: int = Query(50, description="Maximum number of violations to return"),
    offset: int = Query(0, description="Offset for pagination")
):
    """
    Get compliance violations for organization

    Supports filtering by:
    - Regulatory regime (MiFID II, Dodd-Frank, etc.)
    - Severity level (critical, high, medium, low)
    - Resolution status (resolved/active)
    """
    try:
        with compliance_engine.SessionLocal() as session:
            from services.compliance_engine import ComplianceViolationRecord

            query = session.query(ComplianceViolationRecord).filter(
                ComplianceViolationRecord.organization_id == context.organization_id
            )

            # Apply filters
            if regime:
                query = query.filter(ComplianceViolationRecord.regime == regime.value)

            if severity:
                query = query.filter(ComplianceViolationRecord.severity == severity)

            if resolved is not None:
                query = query.filter(ComplianceViolationRecord.resolved == resolved)

            # Order by detection date (most recent first)
            query = query.order_by(ComplianceViolationRecord.detected_at.desc())

            # Apply pagination
            violations = query.offset(offset).limit(limit).all()
            total_count = query.count()

            # Convert to response format
            violation_responses = [
                {
                    "id": str(v.id),
                    "regime": v.regime,
                    "rule_id": v.rule_id,
                    "severity": v.severity,
                    "description": v.description,
                    "detected_at": v.detected_at.isoformat(),
                    "user_id": str(v.user_id) if v.user_id else None,
                    "transaction_id": v.transaction_id,
                    "remediation_required": v.remediation_required,
                    "resolved": v.resolved,
                    "resolved_at": v.resolved_at.isoformat() if v.resolved_at else None,
                    "resolution_notes": v.resolution_notes
                }
                for v in violations
            ]

            return {
                "violations": violation_responses,
                "pagination": {
                    "total_count": total_count,
                    "limit": limit,
                    "offset": offset,
                    "has_more": offset + limit < total_count
                }
            }

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error getting compliance violations: {str(e)}"
        )

@router.put("/violations/{violation_id}/resolve")
async def resolve_violation(
    violation_id: str,
    resolution_notes: str,
    context: TenantContext = Depends(get_tenant_context),
    compliance_engine: ComplianceEngine = Depends(get_compliance_engine)
):
    """
    Resolve a compliance violation

    Marks the violation as resolved and adds resolution notes
    """
    try:
        with compliance_engine.SessionLocal() as session:
            from services.compliance_engine import ComplianceViolationRecord

            # Find violation
            violation = session.query(ComplianceViolationRecord).filter(
                ComplianceViolationRecord.id == violation_id,
                ComplianceViolationRecord.organization_id == context.organization_id
            ).first()

            if not violation:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Violation not found"
                )

            if violation.resolved:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Violation is already resolved"
                )

            # Mark as resolved
            violation.resolved = True
            violation.resolved_at = datetime.now(timezone.utc)
            violation.resolution_notes = resolution_notes

            session.commit()

            return {
                "message": "Violation resolved successfully",
                "violation_id": violation_id,
                "resolved_at": violation.resolved_at.isoformat()
            }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error resolving violation: {str(e)}"
        )

@router.get("/regimes")
async def get_supported_regimes():
    """
    Get list of supported regulatory regimes
    """
    regimes = [
        {
            "code": regime.value,
            "name": regime.name,
            "description": {
                ComplianceRegime.MIFID_II: "Markets in Financial Instruments Directive II (EU)",
                ComplianceRegime.DODD_FRANK: "Dodd-Frank Wall Street Reform Act (US)",
                ComplianceRegime.CFTC: "Commodity Futures Trading Commission (US)",
                ComplianceRegime.SEC: "Securities and Exchange Commission (US)",
                ComplianceRegime.ESMA: "European Securities and Markets Authority (EU)"
            }.get(regime, "")
        }
        for regime in ComplianceRegime
    ]

    return {
        "supported_regimes": regimes,
        "total_count": len(regimes)
    }

@router.get("/health")
async def compliance_health_check(
    compliance_engine: ComplianceEngine = Depends(get_compliance_engine)
):
    """Health check for compliance engine"""
    try:
        # Test database connection
        with compliance_engine.SessionLocal() as session:
            session.execute("SELECT 1")

        return {
            "status": "healthy",
            "service": "compliance_engine",
            "supported_regimes": len(ComplianceRegime),
            "mifid_ii_rules": len(compliance_engine.mifid_ii_rules),
            "dodd_frank_rules": len(compliance_engine.dodd_frank_rules),
            "timestamp": datetime.now(timezone.utc).isoformat()
        }

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Compliance engine unhealthy: {str(e)}"
        )