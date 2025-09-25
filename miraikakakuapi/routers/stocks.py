from fastapi import APIRouter, Query, HTTPException, Depends
from fastapi.responses import JSONResponse
from typing import List, Dict, Optional
from ..services.stock_service import StockService
from ..services.prediction_service import PredictionService
from ..core.exceptions import APIError, ValidationError, StockNotFoundError
from ..core.logging_config import get_logger, log_business_event
from ..models.stock_models import (
    StockPriceResponse,
    StockSearchResponse,
    StockPredictionResponse,
    ErrorResponse
)

logger = get_logger(__name__)

router = APIRouter(prefix="/api", tags=["stocks"])

# Service instances
stock_service = StockService()
prediction_service = PredictionService()


@router.get(
    "/finance/stocks/{symbol}/price",
    response_model=StockPriceResponse,
    responses={
        400: {"model": ErrorResponse, "description": "バリデーションエラー"},
        404: {"model": ErrorResponse, "description": "株式銘柄が見つかりません"},
        500: {"model": ErrorResponse, "description": "サーバーエラー"}
    },
    summary="株価履歴取得",
    description="指定された銘柄の株価履歴データを取得します。最大3650日（約10年）まで指定可能です。"
)
async def get_stock_price_history(
    symbol: str,
    days: int = Query(
        730,
        description="取得する株価データの日数",
        ge=1,
        le=3650,
        example=30
    )
) -> StockPriceResponse:
    """Get historical stock price data with enhanced error handling."""
    try:
        # Validate symbol format
        if not symbol or not symbol.strip():
            raise ValidationError("Stock symbol cannot be empty", field="symbol")

        symbol = symbol.upper().strip()

        # Get price history from service
        price_history = await stock_service.get_stock_price_history(symbol, days)

        # Log successful request
        log_business_event(
            "price_history_requested",
            {"symbol": symbol, "days": days, "data_points": len(price_history)},
            symbol=symbol
        )

        return {
            "symbol": symbol,
            "days_requested": days,
            "data_points": len(price_history),
            "data": price_history,
            "status": "success"
        }

    except APIError:
        # Re-raise API errors to be handled by global handler
        raise
    except Exception as e:
        logger.error(f"Unexpected error in get_stock_price_history for {symbol}: {e}", exc_info=True)
        raise APIError(
            f"Failed to retrieve price history for {symbol}",
            category="system",
            status_code=500,
            details={"symbol": symbol, "days": days}
        )


@router.get(
    "/finance/stocks/search",
    response_model=StockSearchResponse,
    responses={
        400: {"model": ErrorResponse, "description": "バリデーションエラー"},
        500: {"model": ErrorResponse, "description": "サーバーエラー"}
    },
    summary="株式検索",
    description="株式銘柄を検索します。銘柄コードまたは会社名で検索できます。"
)
async def search_stocks(
    q: str = Query(
        ...,
        description="検索クエリ（銘柄コードまたは会社名）",
        min_length=1,
        max_length=50,
        example="AAPL"
    ),
    limit: int = Query(
        10,
        description="結果の最大件数",
        ge=1,
        le=50,
        example=10
    )
) -> StockSearchResponse:
    """Search for stocks by symbol or name with enhanced validation."""
    try:
        # Additional validation
        query = q.strip()
        if not query:
            raise ValidationError("Search query cannot be empty after trimming", field="q")

        # Perform search
        results = await stock_service.search_stocks(query, limit)

        # Log search request
        log_business_event(
            "stock_search_requested",
            {"query": query, "limit": limit, "results_count": len(results)}
        )

        return {
            "query": query,
            "limit": limit,
            "results_count": len(results),
            "results": results,
            "status": "success"
        }

    except APIError:
        # Re-raise API errors to be handled by global handler
        raise
    except Exception as e:
        logger.error(f"Unexpected error in search_stocks for query '{q}': {e}", exc_info=True)
        raise APIError(
            f"Failed to search stocks for query '{q}'",
            category="system",
            status_code=500,
            details={"query": q, "limit": limit}
        )

        return {
            "query": q,
            "limit": limit,
            "results": results
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in search_stocks for query '{q}': {e}")
        return {"query": q, "results": []}


@router.get("/stocks/{symbol}")
async def get_stock_data(symbol: str):
    """Get detailed stock information."""
    try:
        details = await stock_service.get_stock_details(symbol.upper())

        if not details:
            return {
                "symbol": symbol.upper(),
                "message": f"No data found for {symbol}",
                "data": None
            }

        return {
            "symbol": symbol.upper(),
            "data": details
        }

    except Exception as e:
        logger.error(f"Error in get_stock_data for {symbol}: {e}")
        return {
            "symbol": symbol.upper(),
            "message": f"Error retrieving data for {symbol}",
            "data": None
        }


@router.get("/finance/stocks/{symbol}/predictions")
async def get_stock_predictions(
    symbol: str,
    days: int = Query(180, description="Number of days into the future to predict")
):
    """Get AI-powered stock price predictions."""
    try:
        predictions = await prediction_service.get_predictions(symbol.upper(), days)

        return {
            "symbol": symbol.upper(),
            "days_requested": days,
            "predictions": predictions,
            "total_predictions": len(predictions)
        }

    except Exception as e:
        logger.error(f"Error in get_stock_predictions for {symbol}: {e}")
        return {
            "symbol": symbol.upper(),
            "predictions": [],
            "message": f"Error generating predictions for {symbol}"
        }


@router.get("/finance/stocks/{symbol}/predictions/history")
async def get_predictions_history(
    symbol: str,
    days: int = Query(30, description="History days")
):
    """Get historical prediction accuracy data."""
    try:
        historical_predictions = await prediction_service.get_historical_predictions(
            symbol.upper(), days
        )

        return {
            "symbol": symbol.upper(),
            "days_requested": days,
            "historical_predictions": historical_predictions,
            "total_records": len(historical_predictions)
        }

    except Exception as e:
        logger.error(f"Error in get_predictions_history for {symbol}: {e}")
        return {
            "symbol": symbol.upper(),
            "historical_predictions": [],
            "message": f"Error retrieving historical predictions for {symbol}"
        }


@router.get("/predictions/{symbol}")
async def get_predictions_legacy(symbol: str):
    """Legacy endpoint for predictions (maintained for compatibility)."""
    try:
        predictions = await prediction_service.get_predictions(symbol.upper(), 30)

        return {
            "symbol": symbol.upper(),
            "predictions": predictions[:10],  # Limit to 10 for legacy compatibility
            "confidence": "high" if predictions else "low"
        }

    except Exception as e:
        logger.error(f"Error in get_predictions_legacy for {symbol}: {e}")
        return {
            "symbol": symbol.upper(),
            "predictions": [],
            "confidence": "low"
        }


@router.get("/finance/rankings/growth-potential")
async def get_growth_rankings():
    """Get stocks ranked by growth potential."""
    try:
        rankings = await stock_service.get_growth_rankings()

        return {
            "rankings": rankings,
            "total_stocks": len(rankings),
            "last_updated": "2024-01-01T00:00:00Z"  # This would be dynamic in production
        }

    except Exception as e:
        logger.error(f"Error in get_growth_rankings: {e}")
        return {
            "rankings": [],
            "message": "Error retrieving growth rankings"
        }


@router.get("/symbols")
async def get_symbols():
    """Get list of available stock symbols."""
    try:
        symbols = await stock_service.get_validated_symbols()

        return {
            "symbols": symbols,
            "total_symbols": len(symbols),
            "categories": ["stocks", "etfs", "indices"]
        }

    except Exception as e:
        logger.error(f"Error in get_symbols: {e}")
        return {
            "symbols": [],
            "message": "Error retrieving available symbols"
        }


@router.get("/ai/factors/{symbol}")
async def get_ai_factors(symbol: str):
    """Get AI analysis factors for a stock."""
    try:
        factors = await prediction_service.get_ai_factors(symbol.upper())

        return {
            "symbol": symbol.upper(),
            "factors": factors,
            "analysis_date": "2024-01-01T00:00:00Z",  # This would be dynamic
            "total_factors": len(factors)
        }

    except Exception as e:
        logger.error(f"Error in get_ai_factors for {symbol}: {e}")
        return {
            "symbol": symbol.upper(),
            "factors": [],
            "message": f"Error retrieving AI factors for {symbol}"
        }


@router.get("/ai-factors/all")
async def get_ai_factors_all(
    symbol: str = Query(..., description="Stock symbol to analyze")
):
    """Get comprehensive AI factors analysis."""
    try:
        factors = await prediction_service.get_ai_factors(symbol.upper())

        # Enhanced response format for frontend compatibility
        enhanced_factors = []
        for factor in factors:
            enhanced_factors.append({
                "factor": factor.get("factor", "Unknown"),
                "score": factor.get("score", 0.5),
                "impact": factor.get("impact", "Neutral"),
                "reason": factor.get("reason", "No analysis available"),
                "confidence": min(factor.get("score", 0.5) + 0.1, 1.0),
                "category": "technical" if "technical" in factor.get("factor", "").lower() else "fundamental"
            })

        return {
            "symbol": symbol.upper(),
            "ai_factors": enhanced_factors,
            "overall_score": sum(f["score"] for f in enhanced_factors) / len(enhanced_factors) if enhanced_factors else 0.5,
            "analysis_timestamp": "2024-01-01T00:00:00Z",
            "model_version": "v7.0.0"
        }

    except Exception as e:
        logger.error(f"Error in get_ai_factors_all for {symbol}: {e}")
        return {
            "symbol": symbol.upper(),
            "ai_factors": [],
            "overall_score": 0.5,
            "message": f"Error retrieving comprehensive AI analysis for {symbol}"
        }