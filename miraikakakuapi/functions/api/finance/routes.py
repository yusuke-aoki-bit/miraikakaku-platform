from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from database.database import get_db
from database.models import StockMaster, StockPriceHistory, StockPredictions
from api.models.finance_models import StockPriceResponse, StockPredictionResponse, StockSearchResponse
from services.finance_service import FinanceService
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
            (StockMaster.name.contains(query))
        ).filter(StockMaster.is_active == True).limit(limit).all()
        
        return [StockSearchResponse(
            symbol=stock.symbol,
            company_name=stock.name,
            exchange=stock.market or "Unknown",  # marketをexchangeとしてマッピング
            sector=stock.sector or "Unknown",
            industry=None  # industryカラムは存在しない
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
    model_type: Optional[str] = Query(None, description="モデルタイプフィルター"),
    days: int = Query(7, ge=1, le=30, description="予測期間"),
    db: Session = Depends(get_db)
):
    """株価予測取得API"""
    try:
        query_filter = db.query(StockPredictions).filter(
            StockPredictions.symbol == symbol.upper(),
            StockPredictions.is_active == True
        )
        
        if model_type:
            query_filter = query_filter.filter(StockPredictions.model_type == model_type)
        
        predictions = query_filter.order_by(StockPredictions.prediction_date.desc()).limit(days).all()
        
        return [StockPredictionResponse(
            symbol=pred.symbol,
            prediction_date=pred.prediction_date,
            predicted_price=float(pred.predicted_price),
            confidence_score=float(pred.confidence_score) if pred.confidence_score else None,
            model_type=pred.model_type,
            prediction_horizon=pred.prediction_horizon,
            is_active=pred.is_active
        ) for pred in predictions]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"予測データ取得エラー: {str(e)}")

@router.get("/stocks/{symbol}/historical-predictions")
async def get_historical_predictions(
    symbol: str,
    days: int = Query(30, ge=1, le=365, description="取得日数"),
    db: Session = Depends(get_db)
):
    """過去の予測データと実績の比較"""
    try:
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=days)
        
        # 過去の予測データを取得
        predictions = db.query(StockPredictions).filter(
            StockPredictions.symbol == symbol.upper(),
            StockPredictions.prediction_date >= start_date,
            StockPredictions.prediction_date <= end_date
        ).order_by(StockPredictions.prediction_date.desc()).all()
        
        # 実際の株価データも取得して精度を計算
        actual_prices = db.query(StockPriceHistory).filter(
            StockPriceHistory.symbol == symbol.upper(),
            StockPriceHistory.date >= start_date,
            StockPriceHistory.date <= end_date
        ).all()
        
        # 日付別の実際の価格をマップ化
        actual_price_map = {price.date: float(price.close_price) for price in actual_prices}
        
        result = []
        for pred in predictions:
            prediction_date = pred.prediction_date.date() if hasattr(pred.prediction_date, 'date') else pred.prediction_date
            actual_price = actual_price_map.get(prediction_date)
            
            if actual_price:
                predicted_price = float(pred.predicted_price)
                accuracy = max(0, 1 - abs(predicted_price - actual_price) / actual_price)
                
                result.append({
                    "date": prediction_date.isoformat(),
                    "predicted_price": predicted_price,
                    "actual_price": actual_price,
                    "accuracy": accuracy,
                    "confidence": float(pred.confidence_score) if pred.confidence_score else 0.5
                })
        
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"過去予測データ取得エラー: {str(e)}")

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

@router.get("/rankings/accuracy")
async def get_accuracy_rankings(
    limit: int = Query(10, ge=1, le=50, description="結果数制限"),
    db: Session = Depends(get_db)
):
    """予測精度ランキング"""
    try:
        # 各銘柄の予測精度を計算
        stocks = db.query(StockMaster).filter(StockMaster.is_active == True).limit(50).all()
        rankings = []
        
        for stock in stocks:
            # 過去30日の予測精度を計算
            end_date = datetime.utcnow()
            start_date = end_date - timedelta(days=30)
            
            predictions = db.query(StockPredictions).filter(
                StockPredictions.symbol == stock.symbol,
                StockPredictions.prediction_date >= start_date,
                StockPredictions.prediction_date <= end_date,
                StockPredictions.is_active == True
            ).all()
            
            if predictions:
                total_accuracy = sum(float(p.confidence_score) for p in predictions if p.confidence_score)
                avg_accuracy = total_accuracy / len(predictions) if predictions else 0
                
                rankings.append({
                    "symbol": stock.symbol,
                    "company_name": stock.name,
                    "accuracy_score": round(avg_accuracy * 100, 2),
                    "prediction_count": len(predictions)
                })
        
        # 精度でソート
        rankings.sort(key=lambda x: x["accuracy_score"], reverse=True)
        return rankings[:limit]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"精度ランキング取得エラー: {str(e)}")

@router.get("/rankings/growth-potential")
async def get_growth_potential_rankings(
    limit: int = Query(10, ge=1, le=50, description="結果数制限"),
    db: Session = Depends(get_db)
):
    """成長ポテンシャルランキング"""
    try:
        stocks = db.query(StockMaster).filter(StockMaster.is_active == True).limit(50).all()
        rankings = []
        
        for stock in stocks:
            # 最新の予測価格と現在価格を比較
            latest_prediction = db.query(StockPredictions).filter(
                StockPredictions.symbol == stock.symbol,
                StockPredictions.is_active == True
            ).order_by(StockPredictions.prediction_date.desc()).first()
            
            current_price = db.query(StockPriceHistory).filter(
                StockPriceHistory.symbol == stock.symbol
            ).order_by(StockPriceHistory.date.desc()).first()
            
            if latest_prediction and current_price:
                predicted_price = float(latest_prediction.predicted_price)
                current_price_val = float(current_price.close_price)
                growth_potential = ((predicted_price - current_price_val) / current_price_val) * 100
                
                rankings.append({
                    "symbol": stock.symbol,
                    "company_name": stock.name,
                    "current_price": current_price_val,
                    "predicted_price": predicted_price,
                    "growth_potential": round(growth_potential, 2),
                    "confidence": float(latest_prediction.confidence_score) if latest_prediction.confidence_score else 0.5
                })
        
        # 成長ポテンシャルでソート
        rankings.sort(key=lambda x: x["growth_potential"], reverse=True)
        return rankings[:limit]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"成長ポテンシャルランキング取得エラー: {str(e)}")

@router.get("/rankings/composite")
async def get_composite_rankings(
    limit: int = Query(10, ge=1, le=50, description="結果数制限"),
    db: Session = Depends(get_db)
):
    """総合ランキング（精度と成長ポテンシャルの組み合わせ）"""
    try:
        stocks = db.query(StockMaster).filter(StockMaster.is_active == True).limit(50).all()
        rankings = []
        
        for stock in stocks:
            # 予測精度を計算
            end_date = datetime.utcnow()
            start_date = end_date - timedelta(days=30)
            
            predictions = db.query(StockPredictions).filter(
                StockPredictions.symbol == stock.symbol,
                StockPredictions.prediction_date >= start_date,
                StockPredictions.prediction_date <= end_date,
                StockPredictions.is_active == True
            ).all()
            
            accuracy_score = 0
            if predictions:
                total_accuracy = sum(float(p.confidence_score) for p in predictions if p.confidence_score)
                accuracy_score = total_accuracy / len(predictions)
            
            # 成長ポテンシャル計算
            latest_prediction = db.query(StockPredictions).filter(
                StockPredictions.symbol == stock.symbol,
                StockPredictions.is_active == True
            ).order_by(StockPredictions.prediction_date.desc()).first()
            
            current_price = db.query(StockPriceHistory).filter(
                StockPriceHistory.symbol == stock.symbol
            ).order_by(StockPriceHistory.date.desc()).first()
            
            growth_potential = 0
            if latest_prediction and current_price:
                predicted_price = float(latest_prediction.predicted_price)
                current_price_val = float(current_price.close_price)
                growth_potential = ((predicted_price - current_price_val) / current_price_val)
            
            # 総合スコア計算（精度 50%、成長ポテンシャル 50%）
            composite_score = (accuracy_score * 0.5) + (max(0, growth_potential) * 0.5)
            
            rankings.append({
                "symbol": stock.symbol,
                "company_name": stock.name,
                "composite_score": round(composite_score * 100, 2),
                "accuracy_score": round(accuracy_score * 100, 2),
                "growth_potential": round(growth_potential * 100, 2) if growth_potential else 0,
                "prediction_count": len(predictions)
            })
        
        # 総合スコアでソート
        rankings.sort(key=lambda x: x["composite_score"], reverse=True)
        return rankings[:limit]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"総合ランキング取得エラー: {str(e)}")