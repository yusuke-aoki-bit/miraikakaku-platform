"""
Regulatory Reporting API Router
Phase 3.3 - Advanced Risk Management & Compliance

FastAPI endpoints for automated regulatory reporting
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from fastapi.responses import JSONResponse, FileResponse
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta, timezone
from pydantic import BaseModel, Field

from middleware.tenant_auth import get_tenant_context, TenantContext
from services.regulatory_reporting_engine import (
    get_reporting_engine,
    RegulatoryReportingEngine,
    ReportType,
    ReportStatus,
    ReportFormat
)

router = APIRouter(prefix="/api/v1/compliance/reporting", tags=["Regulatory Reporting"])

# Pydantic models for API requests/responses

class ReportGenerationRequest(BaseModel):
    """Request to generate a regulatory report"""
    report_type: ReportType = Field(..., description="Type of regulatory report")
    period_start: datetime = Field(..., description="Report period start date")
    period_end: datetime = Field(..., description="Report period end date")
    format: ReportFormat = Field(ReportFormat.JSON, description="Report output format")
    auto_submit: bool = Field(False, description="Automatically submit after generation")

class ReportSubmissionRequest(BaseModel):
    """Request to submit a generated report"""
    report_id: str = Field(..., description="ID of the report to submit")

class ReportStatusResponse(BaseModel):
    """Report status response"""
    report_id: str
    report_type: str
    status: str
    generated_at: datetime
    due_date: datetime
    submission_reference: Optional[str] = None
    acknowledgment_received: bool
    file_path: Optional[str] = None
    error_messages: List[str] = []

class UpcomingDeadlineResponse(BaseModel):
    """Upcoming deadline response"""
    report_type: str
    next_due_date: datetime
    frequency: str
    mandatory: bool
    jurisdiction: str
    auto_submit: bool
    days_until_due: int

@router.post("/generate")
async def generate_report(
    request: ReportGenerationRequest,
    context: TenantContext = Depends(get_tenant_context),
    reporting_engine: RegulatoryReportingEngine = Depends(get_reporting_engine)
):
    """
    Generate a regulatory report

    Supported report types:
    - MiFID II Transaction Reports (daily, T+1)
    - Dodd-Frank Swap Reports (daily, T+1)
    - EMIR Trade Reports (daily, T+1)
    - CFTC Position Reports (daily, T+1)
    - VaR Disclosure Reports (quarterly)
    - Stress Test Results (annual)

    Reports are generated in specified format and can be auto-submitted.
    """
    try:
        # Validate date range
        if request.period_end <= request.period_start:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Period end date must be after start date"
            )

        # Validate period is not too large
        if (request.period_end - request.period_start).days > 365:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Report period cannot exceed 365 days"
            )

        # Generate report
        report = await reporting_engine.generate_report(
            organization_id=context.organization_id,
            report_type=request.report_type,
            period_start=request.period_start,
            period_end=request.period_end,
            format=request.format,
            auto_submit=request.auto_submit
        )

        return {
            "report_id": report.report_id,
            "report_type": report.report_type.value,
            "status": report.status.value,
            "generated_at": report.generated_at.isoformat(),
            "due_date": report.due_date.isoformat(),
            "format": report.format.value,
            "file_path": report.file_path,
            "auto_submitted": request.auto_submit,
            "submission_reference": report.submission_reference
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error generating report: {str(e)}"
        )

@router.post("/submit")
async def submit_report(
    request: ReportSubmissionRequest,
    context: TenantContext = Depends(get_tenant_context),
    reporting_engine: RegulatoryReportingEngine = Depends(get_reporting_engine)
):
    """
    Submit a generated report to regulatory authorities

    Submits the report to the appropriate regulatory body based on:
    - Report type (MiFID II → ESMA, Dodd-Frank → CFTC/SEC)
    - Organization jurisdiction
    - Report content and format requirements

    Returns submission reference for tracking.
    """
    try:
        # Submit report
        success = await reporting_engine.submit_report(
            report_id=request.report_id,
            organization_id=context.organization_id
        )

        if not success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to submit report"
            )

        # Get updated status
        status_info = await reporting_engine.get_report_status(
            report_id=request.report_id,
            organization_id=context.organization_id
        )

        return {
            "message": "Report submitted successfully",
            "report_id": request.report_id,
            "submission_reference": status_info.get("submission_reference"),
            "submitted_at": datetime.now(timezone.utc).isoformat(),
            "status": status_info.get("status")
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error submitting report: {str(e)}"
        )

@router.get("/status/{report_id}", response_model=ReportStatusResponse)
async def get_report_status(
    report_id: str,
    context: TenantContext = Depends(get_tenant_context),
    reporting_engine: RegulatoryReportingEngine = Depends(get_reporting_engine)
):
    """
    Get the status of a specific report

    Returns detailed status information including:
    - Generation and submission status
    - Regulatory acknowledgment status
    - Error messages (if any)
    - File paths and references
    """
    try:
        status_info = await reporting_engine.get_report_status(
            report_id=report_id,
            organization_id=context.organization_id
        )

        if "error" in status_info:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=status_info["error"]
            )

        return ReportStatusResponse(
            report_id=status_info["report_id"],
            report_type=status_info["report_type"],
            status=status_info["status"],
            generated_at=datetime.fromisoformat(status_info["generated_at"]),
            due_date=datetime.fromisoformat(status_info["due_date"]),
            submission_reference=status_info.get("submission_reference"),
            acknowledgment_received=status_info.get("acknowledgment_received", False),
            file_path=status_info.get("file_path"),
            error_messages=status_info.get("error_messages", [])
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error getting report status: {str(e)}"
        )

@router.get("/deadlines", response_model=List[UpcomingDeadlineResponse])
async def get_upcoming_deadlines(
    context: TenantContext = Depends(get_tenant_context),
    reporting_engine: RegulatoryReportingEngine = Depends(get_reporting_engine),
    days_ahead: int = Query(30, description="Number of days ahead to look for deadlines")
):
    """
    Get upcoming regulatory reporting deadlines

    Returns all upcoming deadlines within the specified time frame:
    - Mandatory vs optional reports
    - Days until due
    - Auto-submission settings
    - Jurisdiction requirements

    Helps organizations stay compliant with regulatory timelines.
    """
    try:
        if days_ahead < 1 or days_ahead > 365:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Days ahead must be between 1 and 365"
            )

        deadlines = await reporting_engine.get_upcoming_deadlines(
            organization_id=context.organization_id,
            days_ahead=days_ahead
        )

        return [
            UpcomingDeadlineResponse(
                report_type=deadline["report_type"],
                next_due_date=datetime.fromisoformat(deadline["next_due_date"]),
                frequency=deadline["frequency"],
                mandatory=deadline["mandatory"],
                jurisdiction=deadline["jurisdiction"],
                auto_submit=deadline["auto_submit"],
                days_until_due=deadline["days_until_due"]
            )
            for deadline in deadlines
        ]

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error getting upcoming deadlines: {str(e)}"
        )

@router.get("/download/{report_id}")
async def download_report(
    report_id: str,
    context: TenantContext = Depends(get_tenant_context),
    reporting_engine: RegulatoryReportingEngine = Depends(get_reporting_engine)
):
    """
    Download a generated report file

    Returns the report file in its generated format:
    - XML for MiFID II/EMIR reports
    - JSON for Dodd-Frank reports
    - CSV for position reports
    - PDF for summary reports
    """
    try:
        # Get report status to verify file exists
        status_info = await reporting_engine.get_report_status(
            report_id=report_id,
            organization_id=context.organization_id
        )

        if "error" in status_info:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Report not found"
            )

        file_path = status_info.get("file_path")
        if not file_path:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Report file not available"
            )

        # Check if file exists
        import os
        if not os.path.exists(file_path):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Report file not found on disk"
            )

        # Determine content type based on file extension
        content_type_map = {
            ".json": "application/json",
            ".xml": "application/xml",
            ".csv": "text/csv",
            ".pdf": "application/pdf"
        }

        file_extension = os.path.splitext(file_path)[1].lower()
        content_type = content_type_map.get(file_extension, "application/octet-stream")

        # Generate download filename
        filename = f"{status_info['report_type']}_{report_id[:8]}{file_extension}"

        return FileResponse(
            path=file_path,
            media_type=content_type,
            filename=filename
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error downloading report: {str(e)}"
        )

@router.get("/reports")
async def list_reports(
    context: TenantContext = Depends(get_tenant_context),
    reporting_engine: RegulatoryReportingEngine = Depends(get_reporting_engine),
    report_type: Optional[ReportType] = Query(None, description="Filter by report type"),
    status_filter: Optional[ReportStatus] = Query(None, description="Filter by status"),
    days: int = Query(90, description="Number of days of history")
):
    """
    List generated reports for organization

    Returns paginated list of reports with filtering options:
    - By report type
    - By status (pending, submitted, acknowledged)
    - By time period

    Useful for audit trails and compliance tracking.
    """
    try:
        if days < 1 or days > 365:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Days must be between 1 and 365"
            )

        with reporting_engine.SessionLocal() as session:
            from services.regulatory_reporting_engine import RegulatoryReport

            query = session.query(RegulatoryReport).filter(
                RegulatoryReport.organization_id == context.organization_id,
                RegulatoryReport.created_at >= datetime.utcnow() - timedelta(days=days)
            )

            if report_type:
                query = query.filter(RegulatoryReport.report_type == report_type.value)

            if status_filter:
                query = query.filter(RegulatoryReport.status == status_filter.value)

            reports = query.order_by(RegulatoryReport.created_at.desc()).limit(100).all()

            report_list = []
            for report in reports:
                report_list.append({
                    "report_id": str(report.id),
                    "report_type": report.report_type,
                    "status": report.status,
                    "generated_at": report.generated_at.isoformat(),
                    "due_date": report.due_date.isoformat(),
                    "period_start": report.report_period_start.isoformat(),
                    "period_end": report.report_period_end.isoformat(),
                    "format": report.format,
                    "submission_reference": report.submission_reference,
                    "acknowledgment_received": report.acknowledgment_received
                })

            return {
                "reports": report_list,
                "total_count": len(report_list),
                "filters_applied": {
                    "report_type": report_type.value if report_type else None,
                    "status": status_filter.value if status_filter else None,
                    "days": days
                }
            }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error listing reports: {str(e)}"
        )

@router.get("/types")
async def get_report_types():
    """Get available regulatory report types"""

    report_types = []
    for report_type in ReportType:
        type_info = {
            "code": report_type.value,
            "name": report_type.name,
            "description": {
                ReportType.MIFID_II_TRANSACTION: "MiFID II transaction reporting (daily, T+1)",
                ReportType.DODD_FRANK_SWAP: "Dodd-Frank swap data repository reporting (daily, T+1)",
                ReportType.EMIR_TRADE: "EMIR trade reporting (daily, T+1)",
                ReportType.CFTC_POSITION: "CFTC position reporting (daily, T+1)",
                ReportType.VAR_DISCLOSURE: "Value at Risk disclosure (quarterly)",
                ReportType.STRESS_TEST_RESULTS: "Stress test results submission (annual)",
                ReportType.COMPLIANCE_SUMMARY: "Compliance summary report (monthly)"
            }.get(report_type, ""),
            "frequency": {
                ReportType.MIFID_II_TRANSACTION: "daily",
                ReportType.DODD_FRANK_SWAP: "daily",
                ReportType.EMIR_TRADE: "daily",
                ReportType.CFTC_POSITION: "daily",
                ReportType.VAR_DISCLOSURE: "quarterly",
                ReportType.STRESS_TEST_RESULTS: "annual",
                ReportType.COMPLIANCE_SUMMARY: "monthly"
            }.get(report_type, "unknown"),
            "mandatory": report_type in [
                ReportType.MIFID_II_TRANSACTION,
                ReportType.DODD_FRANK_SWAP,
                ReportType.EMIR_TRADE,
                ReportType.CFTC_POSITION
            ]
        }
        report_types.append(type_info)

    formats = [
        {
            "code": format.value,
            "name": format.name,
            "description": {
                ReportFormat.XML: "XML format for regulatory authorities",
                ReportFormat.JSON: "JSON format for API integration",
                ReportFormat.CSV: "CSV format for data analysis",
                ReportFormat.PDF: "PDF format for presentations",
                ReportFormat.SWIFT: "SWIFT format for financial messaging"
            }.get(format, "")
        }
        for format in ReportFormat
    ]

    return {
        "report_types": report_types,
        "formats": formats,
        "total_types": len(report_types)
    }

@router.get("/health")
async def reporting_health_check(
    reporting_engine: RegulatoryReportingEngine = Depends(get_reporting_engine)
):
    """Health check for regulatory reporting engine"""
    try:
        # Test database connection
        with reporting_engine.SessionLocal() as session:
            session.execute("SELECT 1")

        return {
            "status": "healthy",
            "service": "regulatory_reporting_engine",
            "supported_report_types": len(ReportType),
            "supported_formats": len(ReportFormat),
            "reporting_deadlines": len(reporting_engine.reporting_deadlines),
            "report_templates": len(reporting_engine.report_templates),
            "timestamp": datetime.now(timezone.utc).isoformat()
        }

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Regulatory reporting engine unhealthy: {str(e)}"
        )