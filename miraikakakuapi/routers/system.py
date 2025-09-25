from fastapi import APIRouter, Depends
from typing import Dict, Any
from ..services.system_service import SystemService
from ..core.logging_config import get_logger
from ..models.stock_models import HealthCheckResponse, ErrorResponse
# from .auth import get_current_user  # コメントアウト（認証が未実装のため）

logger = get_logger(__name__)

router = APIRouter(prefix="/api/system", tags=["system"])

# Service instance
system_service = SystemService()


@router.get(
    "/health",
    response_model=HealthCheckResponse,
    responses={
        503: {"model": ErrorResponse, "description": "サービス利用不可"}
    },
    summary="システムヘルスチェック",
    description="システム全体の健全性をチェックし、データベース、キャッシュ、システムリソースの状態を返します。"
)
async def get_system_health() -> HealthCheckResponse:
    """Get comprehensive system health status."""
    try:
        health_data = await system_service.get_system_health()
        return health_data

    except Exception as e:
        logger.error(f"Error getting system health: {e}")
        return {
            "overall": {
                "status": "error",
                "error": str(e),
                "timestamp": "2024-01-01T00:00:00Z"
            }
        }


@router.get(
    "/metrics",
    response_model=Dict[str, Any],
    responses={
        500: {"model": ErrorResponse, "description": "メトリクス取得エラー"}
    },
    summary="システムメトリクス取得",
    description="詳細なシステムメトリクスとパフォーマンスデータを取得します。"
)
async def get_system_metrics() -> Dict[str, Any]:
    """Get detailed system metrics and performance data."""
    try:
        metrics = await system_service.get_system_metrics()
        return metrics

    except Exception as e:
        logger.error(f"Error getting system metrics: {e}")
        return {
            "error": str(e),
            "timestamp": "2024-01-01T00:00:00Z"
        }


@router.get(
    "/jobs",
    response_model=Dict[str, Any],
    responses={
        500: {"model": ErrorResponse, "description": "ジョブ情報取得エラー"}
    },
    summary="バックグラウンドジョブ情報取得",
    description="実行中のバックグラウンドジョブとプロセスの情報を取得します。"
)
async def get_system_jobs() -> Dict[str, Any]:
    """Get information about background jobs and processes."""
    try:
        jobs = await system_service.get_system_jobs()

        return {
            "jobs": jobs,
            "total_jobs": len(jobs),
            "timestamp": "2024-01-01T00:00:00Z"
        }

    except Exception as e:
        logger.error(f"Error getting system jobs: {e}")
        return {
            "jobs": [],
            "error": str(e),
            "timestamp": "2024-01-01T00:00:00Z"
        }


@router.get(
    "/status",
    response_model=Dict[str, Any],
    responses={
        500: {"model": ErrorResponse, "description": "ステータス取得エラー"}
    },
    summary="APIステータス取得",
    description="基本的なAPI情報とステータスを取得します。"
)
async def get_api_status() -> Dict[str, Any]:
    """Get basic API status information."""
    try:
        return {
            "status": "healthy",
            "version": "7.0.0",
            "api": "Miraikakaku Stock Analysis API",
            "endpoints": {
                "stocks": "/api/finance/stocks/",
                "predictions": "/api/finance/stocks/{symbol}/predictions",
                "search": "/api/finance/stocks/search",
                "auth": "/api/auth/",
                "system": "/api/system/"
            },
            "features": [
                "Real-time stock data",
                "AI-powered predictions",
                "Historical analysis",
                "Portfolio management",
                "System monitoring"
            ]
        }

    except Exception as e:
        logger.error(f"Error getting API status: {e}")
        return {
            "status": "error",
            "error": str(e)
        }