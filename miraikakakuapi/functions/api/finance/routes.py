from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import text
from database.database import get_db
from database.models import StockMaster, StockPriceHistory, StockPredictions
from api.models.finance_models import StockPriceResponse, StockPredictionResponse, StockSearchResponse
from services.finance_service import FinanceService
from typing import List, Optional
from datetime import datetime, timedelta

router = APIRouter()

@router.get("/ml-readiness")
async def get_ml_readiness(db: Session = Depends(get_db)):
    """機械学習の準備状況を評価"""
    try:
        # データ件数取得
        prices_count = db.execute(text("SELECT COUNT(*) FROM stock_prices")).scalar()
        predictions_count = db.execute(text("SELECT COUNT(*) FROM stock_predictions")).scalar()
        symbols_with_prices = db.execute(text("SELECT COUNT(DISTINCT symbol) FROM stock_prices")).scalar()
        symbols_with_predictions = db.execute(text("SELECT COUNT(DISTINCT symbol) FROM stock_predictions")).scalar()
        
        # スコア計算（0-100）
        score = 0
        
        # 価格データ（最大40点）
        if prices_count > 10000:
            score += 40
        elif prices_count > 5000:
            score += 30
        elif prices_count > 1000:
            score += 20
        elif prices_count > 100:
            score += 10
        
        # 予測データ（最大30点）
        if predictions_count > 5000:
            score += 30
        elif predictions_count > 2500:
            score += 25
        elif predictions_count > 1000:
            score += 20
        elif predictions_count > 100:
            score += 10
        
        # 銘柄カバレッジ（最大20点）
        if symbols_with_prices > 100:
            score += 10
        elif symbols_with_prices > 50:
            score += 5
        
        if symbols_with_predictions > 100:
            score += 10
        elif symbols_with_predictions > 50:
            score += 5
        
        # データの多様性（最大10点）
        if symbols_with_prices > 10 and symbols_with_predictions > 10:
            score += 10
        elif symbols_with_prices > 5 and symbols_with_predictions > 5:
            score += 5
        
        # 推奨アクション
        recommendations = []
        if prices_count < 10000:
            recommendations.append("価格データを10,000件以上に増やしてください")
        if predictions_count < 5000:
            recommendations.append("予測データを5,000件以上に増やしてください")
        if symbols_with_prices < 100:
            recommendations.append("より多くの銘柄データを収集してください")
        
        return {
            "ml_readiness_score": score,
            "max_score": 100,
            "data_stats": {
                "price_records": prices_count,
                "prediction_records": predictions_count,
                "symbols_with_prices": symbols_with_prices,
                "symbols_with_predictions": symbols_with_predictions
            },
            "recommendations": recommendations,
            "is_ready": score >= 70,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

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
        ).filter(StockMaster.is_active == 1).limit(limit).all()
        
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
            data_source="database"
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
            StockPredictions.symbol == symbol.upper()
        )
        
        if model_type:
            query_filter = query_filter.filter(StockPredictions.model_version == model_type)
        
        predictions = query_filter.order_by(StockPredictions.prediction_date.desc()).limit(days).all()
        
        return [StockPredictionResponse(
            symbol=pred.symbol,
            prediction_date=pred.prediction_date,
            predicted_price=float(pred.predicted_price),
            confidence_score=float(pred.confidence_score) if pred.confidence_score else None,
            model_type=pred.model_version,
            prediction_horizon=pred.prediction_days,
            is_active=True
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
        stocks = db.query(StockMaster).filter(StockMaster.is_active == 1).limit(50).all()
        rankings = []
        
        for stock in stocks:
            # 過去30日の予測精度を計算
            end_date = datetime.utcnow()
            start_date = end_date - timedelta(days=30)
            
            predictions = db.query(StockPredictions).filter(
                StockPredictions.symbol == stock.symbol,
                StockPredictions.prediction_date >= start_date,
                StockPredictions.prediction_date <= end_date,
                StockPredictions.id.isnot(None)
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
        stocks = db.query(StockMaster).filter(StockMaster.is_active == 1).limit(50).all()
        rankings = []
        
        for stock in stocks:
            # 最新の予測価格と現在価格を比較
            latest_prediction = db.query(StockPredictions).filter(
                StockPredictions.symbol == stock.symbol,
                StockPredictions.id.isnot(None)
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
        stocks = db.query(StockMaster).filter(StockMaster.is_active == 1).limit(50).all()
        rankings = []
        
        for stock in stocks:
            # 予測精度を計算
            end_date = datetime.utcnow()
            start_date = end_date - timedelta(days=30)
            
            predictions = db.query(StockPredictions).filter(
                StockPredictions.symbol == stock.symbol,
                StockPredictions.prediction_date >= start_date,
                StockPredictions.prediction_date <= end_date,
                StockPredictions.id.isnot(None)
            ).all()
            
            accuracy_score = 0
            if predictions:
                total_accuracy = sum(float(p.confidence_score) for p in predictions if p.confidence_score)
                accuracy_score = total_accuracy / len(predictions)
            
            # 成長ポテンシャル計算
            latest_prediction = db.query(StockPredictions).filter(
                StockPredictions.symbol == stock.symbol,
                StockPredictions.id.isnot(None)
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

@router.get("/stocks/{symbol}/indicators")
async def get_technical_indicators(
    symbol: str,
    days: int = Query(30, ge=7, le=365, description="計算期間"),
    db: Session = Depends(get_db)
):
    """テクニカル指標取得API"""
    try:
        # 株価データ取得
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=days + 30)  # 計算に必要な追加データ
        
        prices = db.query(StockPriceHistory).filter(
            StockPriceHistory.symbol == symbol.upper(),
            StockPriceHistory.date >= start_date
        ).order_by(StockPriceHistory.date.asc()).all()
        
        if len(prices) < 20:
            raise HTTPException(status_code=404, detail="十分な株価データがありません")
        
        # 価格配列を準備
        closes = [float(p.close_price) for p in prices]
        highs = [float(p.high_price) if p.high_price else float(p.close_price) for p in prices]
        lows = [float(p.low_price) if p.low_price else float(p.close_price) for p in prices]
        volumes = [int(p.volume) if p.volume else 0 for p in prices]
        
        # テクニカル指標計算
        indicators = {}
        
        # 移動平均線
        if len(closes) >= 5:
            sma_5 = sum(closes[-5:]) / 5
            indicators['sma_5'] = round(sma_5, 2)
        
        if len(closes) >= 20:
            sma_20 = sum(closes[-20:]) / 20
            indicators['sma_20'] = round(sma_20, 2)
            
        if len(closes) >= 50:
            sma_50 = sum(closes[-50:]) / 50
            indicators['sma_50'] = round(sma_50, 2)
        
        # RSI計算
        if len(closes) >= 14:
            gains = []
            losses = []
            for i in range(1, min(15, len(closes))):
                change = closes[-(i)] - closes[-(i+1)]
                if change > 0:
                    gains.append(change)
                    losses.append(0)
                else:
                    gains.append(0)
                    losses.append(abs(change))
            
            avg_gain = sum(gains) / len(gains) if gains else 0
            avg_loss = sum(losses) / len(losses) if losses else 0.01
            rs = avg_gain / avg_loss if avg_loss != 0 else 100
            rsi = 100 - (100 / (1 + rs))
            indicators['rsi'] = round(rsi, 2)
        
        # ボリンジャーバンド
        if len(closes) >= 20:
            sma_20 = sum(closes[-20:]) / 20
            variance = sum((x - sma_20) ** 2 for x in closes[-20:]) / 20
            std_dev = variance ** 0.5
            
            indicators['bollinger_upper'] = round(sma_20 + (2 * std_dev), 2)
            indicators['bollinger_middle'] = round(sma_20, 2)
            indicators['bollinger_lower'] = round(sma_20 - (2 * std_dev), 2)
        
        # MACD計算
        if len(closes) >= 26:
            # 指数移動平均計算
            ema_12 = closes[-1]
            ema_26 = closes[-1]
            
            alpha_12 = 2 / (12 + 1)
            alpha_26 = 2 / (26 + 1)
            
            for i in range(min(26, len(closes))):
                price = closes[-(i+1)]
                ema_12 = (price * alpha_12) + (ema_12 * (1 - alpha_12))
                ema_26 = (price * alpha_26) + (ema_26 * (1 - alpha_26))
            
            macd_line = ema_12 - ema_26
            indicators['macd'] = round(macd_line, 4)
        
        # 出来高移動平均
        if len(volumes) >= 20:
            volume_avg = sum(volumes[-20:]) / 20
            indicators['volume_avg'] = int(volume_avg)
            indicators['volume_ratio'] = round(volumes[-1] / volume_avg if volume_avg > 0 else 1, 2)
        
        # 価格変動率
        if len(closes) >= 2:
            daily_change = ((closes[-1] - closes[-2]) / closes[-2]) * 100
            indicators['daily_change_pct'] = round(daily_change, 2)
        
        if len(closes) >= 7:
            weekly_change = ((closes[-1] - closes[-7]) / closes[-7]) * 100
            indicators['weekly_change_pct'] = round(weekly_change, 2)
        
        # 現在価格情報
        current_price = prices[-1]
        indicators.update({
            'symbol': symbol.upper(),
            'current_price': float(current_price.close_price),
            'current_volume': int(current_price.volume) if current_price.volume else 0,
            'last_updated': current_price.date.isoformat(),
            'data_points': len(prices)
        })
        
        return indicators
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"テクニカル指標計算エラー: {str(e)}")