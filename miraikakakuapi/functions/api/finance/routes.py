from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import text
from database.database import get_db
from database.models import StockMaster, StockPriceHistory, StockPredictions
from api.models.finance_models import (
    StockPriceResponse,
    StockPredictionResponse,
    StockSearchResponse,
)
from services.finance_service import FinanceService
from config import MLConfig, APIConfig, FinanceConfig
from typing import List, Optional
from datetime import datetime, timedelta
import yfinance as yf
import pandas as pd
import logging

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/ml-readiness")
async def get_ml_readiness(db: Session = Depends(get_db)):
    """機械学習の準備状況を評価"""
    try:
        # データ件数取得
        prices_count = db.execute(text("SELECT COUNT(*) FROM stock_prices")).scalar()
        predictions_count = db.execute(
            text("SELECT COUNT(*) FROM stock_predictions")
        ).scalar()
        symbols_with_prices = db.execute(
            text("SELECT COUNT(DISTINCT symbol) FROM stock_prices")
        ).scalar()
        symbols_with_predictions = db.execute(
            text("SELECT COUNT(DISTINCT symbol) FROM stock_predictions")
        ).scalar()

        # スコア計算（0-100）
        score = 0

        # 価格データ（最大スコア）
        if prices_count > MLConfig.PRICE_DATA_THRESHOLD:
            score += FinanceConfig.PRICE_DATA_MAX_SCORE
        elif prices_count > MLConfig.PRICE_DATA_THRESHOLD // 2:
            score += FinanceConfig.PRICE_DATA_MAX_SCORE * 0.75
        elif prices_count > MLConfig.MIN_TRAINING_SAMPLES:
            score += FinanceConfig.PRICE_DATA_MAX_SCORE * 0.5
        elif prices_count > 100:
            score += FinanceConfig.PRICE_DATA_MAX_SCORE * 0.25

        # 予測データ（最大スコア）
        if predictions_count > MLConfig.PREDICTION_DATA_THRESHOLD:
            score += FinanceConfig.PREDICTION_DATA_MAX_SCORE
        elif predictions_count > MLConfig.PREDICTION_DATA_THRESHOLD // 2:
            score += FinanceConfig.PREDICTION_DATA_MAX_SCORE * 0.83
        elif predictions_count > MLConfig.MIN_TRAINING_SAMPLES:
            score += FinanceConfig.PREDICTION_DATA_MAX_SCORE * 0.67
        elif predictions_count > 100:
            score += FinanceConfig.PREDICTION_DATA_MAX_SCORE * 0.33

        # 銘柄カバレッジ（最大スコア）
        if symbols_with_prices > 100:
            score += FinanceConfig.SYMBOL_COVERAGE_MAX_SCORE // 2
        elif symbols_with_prices > 50:
            score += FinanceConfig.SYMBOL_COVERAGE_MAX_SCORE // 4

        if symbols_with_predictions > 100:
            score += FinanceConfig.SYMBOL_COVERAGE_MAX_SCORE // 2
        elif symbols_with_predictions > 50:
            score += FinanceConfig.SYMBOL_COVERAGE_MAX_SCORE // 4

        # データの多様性（最大スコア）
        if symbols_with_prices > 10 and symbols_with_predictions > 10:
            score += FinanceConfig.DATA_DIVERSITY_MAX_SCORE
        elif symbols_with_prices > 5 and symbols_with_predictions > 5:
            score += FinanceConfig.DATA_DIVERSITY_MAX_SCORE // 2

        # 推奨アクション
        recommendations = []
        if prices_count < MLConfig.PRICE_DATA_THRESHOLD:
            recommendations.append(
                f"価格データを{MLConfig.PRICE_DATA_THRESHOLD:,}件以上に増やしてください"
            )
        if predictions_count < MLConfig.PREDICTION_DATA_THRESHOLD:
            recommendations.append(
                f"予測データを{MLConfig.PREDICTION_DATA_THRESHOLD:,}件以上に増やしてください"
            )
        if symbols_with_prices < 100:
            recommendations.append("より多くの銘柄データを収集してください")

        return {
            "ml_readiness_score": score,
            "max_score": (
                FinanceConfig.PRICE_DATA_MAX_SCORE
                + FinanceConfig.PREDICTION_DATA_MAX_SCORE
                + FinanceConfig.SYMBOL_COVERAGE_MAX_SCORE
                + FinanceConfig.DATA_DIVERSITY_MAX_SCORE
            ),
            "data_stats": {
                "price_records": prices_count,
                "prediction_records": predictions_count,
                "symbols_with_prices": symbols_with_prices,
                "symbols_with_predictions": symbols_with_predictions,
            },
            "recommendations": recommendations,
            "is_ready": score >= FinanceConfig.ML_READINESS_THRESHOLD,
            "timestamp": datetime.now().isoformat(),
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/stocks/search", response_model=List[StockSearchResponse])
async def search_stocks(
    query: str = Query(..., min_length=1, description="検索クエリ"),
    limit: int = Query(
        APIConfig.DEFAULT_PAGE_SIZE // 2,
        ge=1,
        le=APIConfig.MAX_PAGE_SIZE,
        description="結果数制限",
    ),
    db: Session = Depends(get_db),
):
    """株式検索API"""
    try:
        stocks = (
            db.query(StockMaster)
            .filter(
                (StockMaster.symbol.contains(query.upper()))
                | (StockMaster.name.contains(query))
            )
            .filter(StockMaster.is_active == 1)
            .limit(limit)
            .all()
        )

        return [
            StockSearchResponse(
                symbol=stock.symbol,
                company_name=stock.name,
                exchange=stock.market or "Unknown",  # marketをexchangeとしてマッピング
                sector=stock.sector or "Unknown",
                industry=None,  # industryカラムは存在しない
            )
            for stock in stocks
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"検索エラー: {str(e)}")


@router.get("/stocks/{symbol}/price", response_model=List[StockPriceResponse])
async def get_stock_price(
    symbol: str,
    days: int = Query(
        FinanceConfig.DEFAULT_PREDICTION_DAYS * 4,
        ge=1,
        le=FinanceConfig.PRICE_HISTORY_DAYS,
        description="取得日数",
    ),
    db: Session = Depends(get_db),
):
    """株価履歴取得API"""
    try:
        start_date = datetime.utcnow() - timedelta(days=days)

        prices = (
            db.query(StockPriceHistory)
            .filter(
                StockPriceHistory.symbol == symbol.upper(),
                StockPriceHistory.date >= start_date,
            )
            .order_by(StockPriceHistory.date.desc())
            .all()
        )

        if not prices:
            raise HTTPException(status_code=404, detail="株価データが見つかりません")

        return [
            StockPriceResponse(
                symbol=price.symbol,
                date=price.date,
                open_price=float(price.open_price) if price.open_price else None,
                high_price=float(price.high_price) if price.high_price else None,
                low_price=float(price.low_price) if price.low_price else None,
                close_price=float(price.close_price),
                volume=price.volume,
                data_source="database",
            )
            for price in prices
        ]
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"データ取得エラー: {str(e)}")


@router.get(
    "/stocks/{symbol}/predictions", response_model=List[StockPredictionResponse]
)
async def get_stock_predictions(
    symbol: str,
    model_type: Optional[str] = Query(None, description="モデルタイプフィルター"),
    days: int = Query(
        FinanceConfig.DEFAULT_PREDICTION_DAYS,
        ge=1,
        le=FinanceConfig.MAX_PREDICTION_DAYS,
        description="予測期間",
    ),
    db: Session = Depends(get_db),
):
    """株価予測取得API"""
    try:
        query_filter = db.query(StockPredictions).filter(
            StockPredictions.symbol == symbol.upper()
        )

        if model_type:
            query_filter = query_filter.filter(
                StockPredictions.model_version == model_type
            )

        predictions = (
            query_filter.order_by(StockPredictions.prediction_date.desc())
            .limit(days)
            .all()
        )

        return [
            StockPredictionResponse(
                symbol=pred.symbol,
                prediction_date=pred.prediction_date,
                predicted_price=float(pred.predicted_price),
                confidence_score=(
                    float(pred.confidence_score) if pred.confidence_score else None
                ),
                model_type=pred.model_version,
                prediction_horizon=pred.prediction_days,
                is_active=True,
            )
            for pred in predictions
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"予測データ取得エラー: {str(e)}")


@router.get("/stocks/{symbol}/historical-predictions")
async def get_historical_predictions(
    symbol: str,
    days: int = Query(
        FinanceConfig.DEFAULT_PREDICTION_DAYS * 4,
        ge=1,
        le=FinanceConfig.PRICE_HISTORY_DAYS,
        description="取得日数",
    ),
    db: Session = Depends(get_db),
):
    """過去の予測データと実績の比較"""
    try:
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=days)

        # 過去の予測データを取得
        predictions = (
            db.query(StockPredictions)
            .filter(
                StockPredictions.symbol == symbol.upper(),
                StockPredictions.prediction_date >= start_date,
                StockPredictions.prediction_date <= end_date,
            )
            .order_by(StockPredictions.prediction_date.desc())
            .all()
        )

        # 実際の株価データも取得して精度を計算
        actual_prices = (
            db.query(StockPriceHistory)
            .filter(
                StockPriceHistory.symbol == symbol.upper(),
                StockPriceHistory.date >= start_date,
                StockPriceHistory.date <= end_date,
            )
            .all()
        )

        # 日付別の実際の価格をマップ化
        actual_price_map = {
            price.date: float(price.close_price) for price in actual_prices
        }

        result = []
        for pred in predictions:
            prediction_date = (
                pred.prediction_date.date()
                if hasattr(pred.prediction_date, "date")
                else pred.prediction_date
            )
            actual_price = actual_price_map.get(prediction_date)

            if actual_price:
                predicted_price = float(pred.predicted_price)
                accuracy = max(
                    0, 1 - abs(predicted_price - actual_price) / actual_price
                )

                result.append(
                    {
                        "date": prediction_date.isoformat(),
                        "predicted_price": predicted_price,
                        "actual_price": actual_price,
                        "accuracy": accuracy,
                        "confidence": (
                            float(pred.confidence_score)
                            if pred.confidence_score
                            else 0.5
                        ),
                    }
                )

        return result
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"過去予測データ取得エラー: {str(e)}"
        )


@router.post("/stocks/{symbol}/predict")
async def create_prediction(symbol: str, db: Session = Depends(get_db)):
    """新しい株価予測を生成"""
    try:
        finance_service = FinanceService(db)
        result = await finance_service.create_prediction(symbol.upper())
        return {"message": "予測生成完了", "prediction_id": result.id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"予測生成エラー: {str(e)}")


@router.get("/rankings/accuracy")
async def get_accuracy_rankings(
    limit: int = Query(
        APIConfig.DEFAULT_PAGE_SIZE // 2,
        ge=1,
        le=FinanceConfig.VOLUME_RANKING_LIMIT,
        description="結果数制限",
    ),
    db: Session = Depends(get_db),
):
    """予測精度ランキング"""
    try:
        # 各銘柄の予測精度を計算
        stocks = (
            db.query(StockMaster)
            .filter(StockMaster.is_active == 1)
            .limit(FinanceConfig.VOLUME_RANKING_LIMIT)
            .all()
        )
        rankings = []

        for stock in stocks:
            # 過去30日の予測精度を計算
            end_date = datetime.utcnow()
            start_date = end_date - timedelta(
                days=FinanceConfig.DEFAULT_PREDICTION_DAYS * 4
            )

            predictions = (
                db.query(StockPredictions)
                .filter(
                    StockPredictions.symbol == stock.symbol,
                    StockPredictions.prediction_date >= start_date,
                    StockPredictions.prediction_date <= end_date,
                    StockPredictions.id.isnot(None),
                )
                .all()
            )

            if predictions:
                total_accuracy = sum(
                    float(p.confidence_score) for p in predictions if p.confidence_score
                )
                avg_accuracy = total_accuracy / len(predictions) if predictions else 0

                rankings.append(
                    {
                        "symbol": stock.symbol,
                        "company_name": stock.name,
                        "accuracy_score": round(
                            avg_accuracy * FinanceConfig.PERCENTAGE_MULTIPLIER, 2
                        ),
                        "prediction_count": len(predictions),
                    }
                )

        # 精度でソート
        rankings.sort(key=lambda x: x["accuracy_score"], reverse=True)
        return rankings[:limit]
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"精度ランキング取得エラー: {str(e)}"
        )


@router.get("/rankings/growth-potential")
async def get_growth_potential_rankings(
    limit: int = Query(
        APIConfig.DEFAULT_PAGE_SIZE // 2,
        ge=1,
        le=FinanceConfig.VOLUME_RANKING_LIMIT,
        description="結果数制限",
    ),
    db: Session = Depends(get_db),
):
    """成長ポテンシャルランキング"""
    try:
        stocks = (
            db.query(StockMaster)
            .filter(StockMaster.is_active == 1)
            .limit(FinanceConfig.VOLUME_RANKING_LIMIT)
            .all()
        )
        rankings = []

        for stock in stocks:
            # 最新の予測価格と現在価格を比較
            latest_prediction = (
                db.query(StockPredictions)
                .filter(
                    StockPredictions.symbol == stock.symbol,
                    StockPredictions.id.isnot(None),
                )
                .order_by(StockPredictions.prediction_date.desc())
                .first()
            )

            current_price = (
                db.query(StockPriceHistory)
                .filter(StockPriceHistory.symbol == stock.symbol)
                .order_by(StockPriceHistory.date.desc())
                .first()
            )

            if latest_prediction and current_price:
                predicted_price = float(latest_prediction.predicted_price)
                current_price_val = float(current_price.close_price)
                growth_potential = (
                    (predicted_price - current_price_val) / current_price_val
                ) * FinanceConfig.PERCENTAGE_MULTIPLIER

                rankings.append(
                    {
                        "symbol": stock.symbol,
                        "company_name": stock.name,
                        "current_price": current_price_val,
                        "predicted_price": predicted_price,
                        "growth_potential": round(growth_potential, 2),
                        "confidence": (
                            float(latest_prediction.confidence_score)
                            if latest_prediction.confidence_score
                            else 0.5
                        ),
                    }
                )

        # 成長ポテンシャルでソート
        rankings.sort(key=lambda x: x["growth_potential"], reverse=True)
        return rankings[:limit]
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"成長ポテンシャルランキング取得エラー: {str(e)}"
        )


@router.get("/rankings/composite")
async def get_composite_rankings(
    limit: int = Query(
        APIConfig.DEFAULT_PAGE_SIZE // 2,
        ge=1,
        le=FinanceConfig.VOLUME_RANKING_LIMIT,
        description="結果数制限",
    ),
    db: Session = Depends(get_db),
):
    """総合ランキング（精度と成長ポテンシャルの組み合わせ）"""
    try:
        stocks = (
            db.query(StockMaster)
            .filter(StockMaster.is_active == 1)
            .limit(FinanceConfig.VOLUME_RANKING_LIMIT)
            .all()
        )
        rankings = []

        for stock in stocks:
            # 予測精度を計算
            end_date = datetime.utcnow()
            start_date = end_date - timedelta(
                days=FinanceConfig.DEFAULT_PREDICTION_DAYS * 4
            )

            predictions = (
                db.query(StockPredictions)
                .filter(
                    StockPredictions.symbol == stock.symbol,
                    StockPredictions.prediction_date >= start_date,
                    StockPredictions.prediction_date <= end_date,
                    StockPredictions.id.isnot(None),
                )
                .all()
            )

            accuracy_score = 0
            if predictions:
                total_accuracy = sum(
                    float(p.confidence_score) for p in predictions if p.confidence_score
                )
                accuracy_score = total_accuracy / len(predictions)

            # 成長ポテンシャル計算
            latest_prediction = (
                db.query(StockPredictions)
                .filter(
                    StockPredictions.symbol == stock.symbol,
                    StockPredictions.id.isnot(None),
                )
                .order_by(StockPredictions.prediction_date.desc())
                .first()
            )

            current_price = (
                db.query(StockPriceHistory)
                .filter(StockPriceHistory.symbol == stock.symbol)
                .order_by(StockPriceHistory.date.desc())
                .first()
            )

            growth_potential = 0
            if latest_prediction and current_price:
                predicted_price = float(latest_prediction.predicted_price)
                current_price_val = float(current_price.close_price)
                growth_potential = (
                    predicted_price - current_price_val
                ) / current_price_val

            # 総合スコア計算（精度と成長ポテンシャルの平均）
            composite_score = (accuracy_score * 0.5) + (max(0, growth_potential) * 0.5)

            rankings.append(
                {
                    "symbol": stock.symbol,
                    "company_name": stock.name,
                    "composite_score": round(
                        composite_score * FinanceConfig.PERCENTAGE_MULTIPLIER, 2
                    ),
                    "accuracy_score": round(
                        accuracy_score * FinanceConfig.PERCENTAGE_MULTIPLIER, 2
                    ),
                    "growth_potential": (
                        round(growth_potential * FinanceConfig.PERCENTAGE_MULTIPLIER, 2)
                        if growth_potential
                        else 0
                    ),
                    "prediction_count": len(predictions),
                }
            )

        # 総合スコアでソート
        rankings.sort(key=lambda x: x["composite_score"], reverse=True)
        return rankings[:limit]
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"総合ランキング取得エラー: {str(e)}"
        )


@router.get("/stocks/{symbol}/indicators")
async def get_technical_indicators(
    symbol: str,
    days: int = Query(
        FinanceConfig.DEFAULT_PREDICTION_DAYS * 4,
        ge=FinanceConfig.DEFAULT_PREDICTION_DAYS,
        le=FinanceConfig.PRICE_HISTORY_DAYS,
        description="計算期間",
    ),
    db: Session = Depends(get_db),
):
    """テクニカル指標取得API"""
    try:
        # 株価データ取得
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(
            days=days + FinanceConfig.DEFAULT_PREDICTION_DAYS * 4
        )  # 計算に必要な追加データ

        prices = (
            db.query(StockPriceHistory)
            .filter(
                StockPriceHistory.symbol == symbol.upper(),
                StockPriceHistory.date >= start_date,
            )
            .order_by(StockPriceHistory.date.asc())
            .all()
        )

        if len(prices) < FinanceConfig.MIN_STOCK_DATA_FOR_CALCULATION:
            raise HTTPException(status_code=404, detail="十分な株価データがありません")

        # 価格配列を準備
        closes = [float(p.close_price) for p in prices]
        volumes = [int(p.volume) if p.volume else 0 for p in prices]

        # テクニカル指標計算
        indicators = {}

        # 移動平均線
        if len(closes) >= 5:
            sma_5 = sum(closes[-5:]) / 5
            indicators["sma_5"] = round(sma_5, 2)

        if len(closes) >= FinanceConfig.SMA_SHORT_PERIOD:
            period = FinanceConfig.SMA_SHORT_PERIOD
            sma_20 = sum(closes[-period:]) / period
            indicators["sma_20"] = round(sma_20, 2)

        if len(closes) >= FinanceConfig.SMA_LONG_PERIOD:
            period = FinanceConfig.SMA_LONG_PERIOD
            sma_50 = sum(closes[-period:]) / period
            indicators["sma_50"] = round(sma_50, 2)

        # RSI計算
        if len(closes) >= FinanceConfig.RSI_PERIOD:
            gains = []
            losses = []
            for i in range(1, min(FinanceConfig.RSI_PERIOD + 1, len(closes))):
                change = closes[-(i)] - closes[-(i + 1)]
                if change > 0:
                    gains.append(change)
                    losses.append(0)
                else:
                    gains.append(0)
                    losses.append(abs(change))

            avg_gain = sum(gains) / len(gains) if gains else 0
            avg_loss = sum(losses) / len(losses) if losses else 0.01
            multiplier = FinanceConfig.PERCENTAGE_MULTIPLIER
            rs = avg_gain / avg_loss if avg_loss != 0 else multiplier
            rsi = multiplier - (multiplier / (1 + rs))
            indicators["rsi"] = round(rsi, 2)

        # ボリンジャーバンド
        if len(closes) >= FinanceConfig.SMA_SHORT_PERIOD:
            period = FinanceConfig.SMA_SHORT_PERIOD
            sma_20 = sum(closes[-period:]) / period
            variance = sum((x - sma_20) ** 2 for x in closes[-period:]) / period
            std_dev = variance**0.5

            indicators["bollinger_upper"] = round(sma_20 + (2 * std_dev), 2)
            indicators["bollinger_middle"] = round(sma_20, 2)
            indicators["bollinger_lower"] = round(sma_20 - (2 * std_dev), 2)

        # MACD計算
        if len(closes) >= FinanceConfig.MACD_SLOW_PERIOD:
            # 指数移動平均計算
            ema_12 = closes[-1]
            ema_26 = closes[-1]

            alpha_12 = 2 / (FinanceConfig.MACD_FAST_PERIOD + 1)
            alpha_26 = 2 / (FinanceConfig.MACD_SLOW_PERIOD + 1)

            for i in range(min(FinanceConfig.MACD_SLOW_PERIOD, len(closes))):
                price = closes[-(i + 1)]
                ema_12 = (price * alpha_12) + (ema_12 * (1 - alpha_12))
                ema_26 = (price * alpha_26) + (ema_26 * (1 - alpha_26))

            macd_line = ema_12 - ema_26
            indicators["macd"] = round(macd_line, 4)

        # 出来高移動平均
        if len(volumes) >= FinanceConfig.SMA_SHORT_PERIOD:
            period = FinanceConfig.SMA_SHORT_PERIOD
            volume_avg = sum(volumes[-period:]) / period
            indicators["volume_avg"] = int(volume_avg)
            indicators["volume_ratio"] = round(
                volumes[-1] / volume_avg if volume_avg > 0 else 1, 2
            )

        # 価格変動率
        if len(closes) >= 2:
            daily_change = (
                (closes[-1] - closes[-2]) / closes[-2]
            ) * FinanceConfig.PERCENTAGE_MULTIPLIER
            indicators["daily_change_pct"] = round(daily_change, 2)

        if len(closes) >= 7:
            weekly_change = (
                (closes[-1] - closes[-7]) / closes[-7]
            ) * FinanceConfig.PERCENTAGE_MULTIPLIER
            indicators["weekly_change_pct"] = round(weekly_change, 2)

        # 現在価格情報
        current_price = prices[-1]
        indicators.update(
            {
                "symbol": symbol.upper(),
                "current_price": float(current_price.close_price),
                "current_volume": (
                    int(current_price.volume) if current_price.volume else 0
                ),
                "last_updated": current_price.date.isoformat(),
                "data_points": len(prices),
            }
        )

        return indicators

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"テクニカル指標計算エラー: {str(e)}"
        )


@router.get("/stocks/{symbol}/volume")
async def get_volume_data(
    symbol: str,
    limit: int = Query(
        FinanceConfig.DEFAULT_PREDICTION_DAYS * 4,
        ge=1,
        le=FinanceConfig.PRICE_HISTORY_DAYS,
        description="取得する日数",
    ),
    db: Session = Depends(get_db),
):
    """出来高データ取得API"""
    try:
        # データベースから出来高データを取得
        prices = (
            db.query(StockPriceHistory)
            .filter(StockPriceHistory.symbol == symbol.upper())
            .order_by(StockPriceHistory.date.desc())
            .limit(limit)
            .all()
        )

        if not prices:
            # データベースにない場合は Yahoo Finance から取得
            try:
                ticker = yf.Ticker(symbol.upper())
                hist = ticker.history(period=f"{limit}d")

                if hist.empty:
                    raise HTTPException(
                        status_code=404, detail="出来高データが見つかりません"
                    )

                volume_data = []
                for date, row in hist.iterrows():
                    volume_data.append(
                        {
                            "date": date.strftime("%Y-%m-%d"),
                            "symbol": symbol.upper(),
                            "volume": (
                                int(row["Volume"]) if pd.notna(row["Volume"]) else 0
                            ),
                            "close_price": float(row["Close"]),
                            "price_change": 0,  # 前日比は別途計算
                            "source": "yahoo_finance",
                        }
                    )

                return {
                    "status": "success",
                    "data": volume_data[:limit],
                    "count": len(volume_data),
                }
            except Exception as yf_error:
                logger.warning(f"Yahoo Finance error for {symbol}: {str(yf_error)}")
                raise HTTPException(
                    status_code=404, detail="出来高データを取得できませんでした"
                )

        # データベースからのデータを整形
        volume_data = []
        for i, price in enumerate(prices):
            prev_price = (
                prices[i + 1].close_price if i + 1 < len(prices) else price.close_price
            )
            price_change = (
                (float(price.close_price) - float(prev_price)) / float(prev_price) * 100
                if float(prev_price) != 0
                else 0
            )

            volume_data.append(
                {
                    "date": price.date.isoformat(),
                    "symbol": price.symbol,
                    "volume": int(price.volume) if price.volume else 0,
                    "close_price": float(price.close_price),
                    "price_change": round(price_change, 2),
                    "source": "database",
                }
            )

        # 日付順にソート（新しい順）
        volume_data.sort(key=lambda x: x["date"], reverse=True)

        return {"status": "success", "data": volume_data, "count": len(volume_data)}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Volume data error for {symbol}: {str(e)}")
        raise HTTPException(status_code=500, detail="出来高データ取得エラー")


@router.get("/stocks/{symbol}/volume-predictions")
async def get_volume_predictions(
    symbol: str,
    days: int = Query(
        FinanceConfig.DEFAULT_PREDICTION_DAYS,
        ge=1,
        le=FinanceConfig.MAX_PREDICTION_DAYS,
        description="予測する日数",
    ),
    db: Session = Depends(get_db),
):
    """出来高予測API（簡易実装）"""
    try:
        # 過去の出来高データを取得
        historical_prices = (
            db.query(StockPriceHistory)
            .filter(StockPriceHistory.symbol == symbol.upper())
            .order_by(StockPriceHistory.date.desc())
            .limit(FinanceConfig.DEFAULT_PREDICTION_DAYS * 4)
            .all()
        )

        if len(historical_prices) < 5:
            raise HTTPException(
                status_code=404, detail="出来高予測に必要な履歴データが不足しています"
            )

        # 平均出来高を計算
        volumes = [int(p.volume) if p.volume else 0 for p in historical_prices]
        avg_volume = sum(volumes) / len(volumes) if volumes else 0

        # 出来高のボラティリティを計算
        volume_variance = sum((v - avg_volume) ** 2 for v in volumes) / len(volumes)
        volume_std = volume_variance**0.5

        # 予測データを生成
        predictions = []
        base_date = datetime.now()

        for i in range(1, days + 1):
            future_date = base_date + timedelta(days=i)

            # 簡易的な出来高予測（移動平均ベース）
            trend_factor = 0.95 + (0.1 * (i % 3))  # 周期的な変動を想定
            volatility_factor = 1 + (
                (volume_std / avg_volume) * (0.5 - abs(0.5 - (i / days)))
            )

            predicted_volume = int(avg_volume * trend_factor * volatility_factor)
            confidence = max(
                FinanceConfig.MIN_CONFIDENCE,
                FinanceConfig.DEFAULT_CONFIDENCE_BASE
                - (i * FinanceConfig.CONFIDENCE_DECAY_RATE),
            )  # 日数が増えるほど信頼度低下

            predictions.append(
                {
                    "date": future_date.strftime("%Y-%m-%d"),
                    "symbol": symbol.upper(),
                    "predicted_volume": predicted_volume,
                    "confidence": confidence,
                    "base_volume": int(avg_volume),
                    "factors": [
                        "historical_average",
                        "volume_volatility",
                        "market_trend",
                    ],
                }
            )

        return {
            "status": "success",
            "data": {
                "symbol": symbol.upper(),
                "predictions": predictions,
                "base_statistics": {
                    "average_volume": int(avg_volume),
                    "volume_std": int(volume_std),
                    "data_points": len(historical_prices),
                },
                "note": (
                    "これは統計的な出来高予測モデルです。"
                    "実際の取引判断には使用しないでください。"
                ),
            },
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Volume prediction error for {symbol}: {str(e)}")
        raise HTTPException(status_code=500, detail="出来高予測エラー")


@router.get("/volume-rankings")
async def get_volume_rankings(
    limit: int = Query(
        APIConfig.DEFAULT_PAGE_SIZE // 2,
        ge=1,
        le=FinanceConfig.VOLUME_RANKING_LIMIT,
        description="結果数制限",
    ),
    db: Session = Depends(get_db),
):
    """出来高ランキング取得API"""
    try:
        # 最新の出来高データを取得
        latest_date = (
            db.query(StockPriceHistory.date)
            .order_by(StockPriceHistory.date.desc())
            .first()
        )

        if not latest_date:
            raise HTTPException(status_code=404, detail="出来高データが見つかりません")

        # 最新日の出来高ランキング
        volume_rankings = db.execute(
            text(
                """
            SELECT
                sp.symbol,
                sm.name as company_name,
                sp.volume,
                sp.close_price,
                LAG(sp.close_price) OVER (
                    PARTITION BY sp.symbol ORDER BY sp.date
                ) as prev_close,
                sp.date
            FROM stock_prices sp
            JOIN stock_master sm ON sp.symbol = sm.symbol
            WHERE sp.date = :latest_date
            AND sp.volume > 0
            ORDER BY sp.volume DESC
            LIMIT :limit_val
        """
            ),
            {"latest_date": latest_date[0], "limit_val": limit},
        ).fetchall()

        rankings = []
        for row in volume_rankings:
            price_change = 0
            if row.prev_close and float(row.prev_close) != 0:
                price_change = (
                    (float(row.close_price) - float(row.prev_close))
                    / float(row.prev_close)
                    * FinanceConfig.PERCENTAGE_MULTIPLIER
                )

            rankings.append(
                {
                    "symbol": row.symbol,
                    "company_name": row.company_name,
                    "volume": int(row.volume),
                    "close_price": float(row.close_price),
                    "price_change": round(price_change, 2),
                    "date": row.date.isoformat(),
                }
            )

        return {
            "status": "success",
            "data": rankings,
            "date": latest_date[0].isoformat(),
            "count": len(rankings),
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Volume rankings error: {str(e)}")
        raise HTTPException(status_code=500, detail="出来高ランキング取得エラー")
