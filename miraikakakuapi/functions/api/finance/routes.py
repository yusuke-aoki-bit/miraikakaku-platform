from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from database.database import get_db
from database.models import StockMaster, StockPriceHistory, StockPredictions
from api.models.finance_models import StockPriceResponse, StockPredictionResponse, StockSearchResponse
from services.finance.finance_service import FinanceService
from typing import List, Optional
from datetime import datetime, timedelta

router = APIRouter()

@router.get("/stocks/search", response_model=List[StockSearchResponse])
async def search_stocks(
    query: str = Query(..., min_length=1, description="検索クエリ"),
    limit: int = Query(10, ge=1, le=100, description="結果数制限"),
    db: Session = Depends(get_db)
):
    """株式検索API"""
    try:
        stocks = db.query(StockMaster).filter(
            (StockMaster.symbol.contains(query.upper())) |
            (StockMaster.company_name.contains(query))
        ).filter(StockMaster.is_active == True).limit(limit).all()
        
        return [StockSearchResponse(
            symbol=stock.symbol,
            company_name=stock.company_name,
            exchange=stock.exchange,
            sector=stock.sector,
            industry=stock.industry
        ) for stock in stocks]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"検索エラー: {str(e)}")

@router.get("/stocks/{symbol}/price", response_model=List[StockPriceResponse])
async def get_stock_price(
    symbol: str,
    days: int = Query(30, ge=1, le=365, description="取得日数"),
    db: Session = Depends(get_db)
):
    """株価履歴取得API"""
    try:
        start_date = datetime.utcnow() - timedelta(days=days)
        
        prices = db.query(StockPriceHistory).filter(
            StockPriceHistory.symbol == symbol.upper(),
            StockPriceHistory.date >= start_date
        ).order_by(StockPriceHistory.date.desc()).all()
        
        if not prices:
            raise HTTPException(status_code=404, detail="株価データが見つかりません")
        
        return [StockPriceResponse(
            symbol=price.symbol,
            date=price.date,
            open_price=float(price.open_price) if price.open_price else None,
            high_price=float(price.high_price) if price.high_price else None,
            low_price=float(price.low_price) if price.low_price else None,
            close_price=float(price.close_price),
            volume=price.volume,
            data_source=price.data_source
        ) for price in prices]
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"データ取得エラー: {str(e)}")

@router.get("/stocks/{symbol}/predictions", response_model=List[StockPredictionResponse])
async def get_stock_predictions(
    symbol: str,
    model_name: Optional[str] = Query(None, description="モデル名フィルター"),
    days: int = Query(7, ge=1, le=30, description="予測期間"),
    db: Session = Depends(get_db)
):
    """株価予測取得API"""
    try:
        query_filter = db.query(StockPredictions).filter(
            StockPredictions.symbol == symbol.upper(),
            StockPredictions.target_date >= datetime.utcnow()
        )
        
        if model_name:
            query_filter = query_filter.filter(StockPredictions.model_name == model_name)
        
        predictions = query_filter.order_by(StockPredictions.target_date.asc()).limit(days).all()
        
        return [StockPredictionResponse(
            symbol=pred.symbol,
            prediction_date=pred.prediction_date,
            target_date=pred.target_date,
            predicted_price=float(pred.predicted_price),
            confidence_score=float(pred.confidence_score) if pred.confidence_score else None,
            model_name=pred.model_name,
            prediction_type=pred.prediction_type
        ) for pred in predictions]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"予測データ取得エラー: {str(e)}")

@router.post("/stocks/{symbol}/predict")
async def create_prediction(
    symbol: str,
    db: Session = Depends(get_db)
):
    """新しい株価予測を生成"""
    try:
        finance_service = FinanceService(db)
        result = await finance_service.create_prediction(symbol.upper())
        return {"message": "予測生成完了", "prediction_id": result.id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"予測生成エラー: {str(e)}")