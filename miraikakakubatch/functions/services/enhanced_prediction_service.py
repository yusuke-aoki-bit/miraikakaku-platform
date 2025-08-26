# 強化された株価予測サービス（過去・未来予測）

import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from typing import List, Dict, Optional, Tuple
import json
import logging
from concurrent.futures import ThreadPoolExecutor, as_completed
import yfinance as yf

from database.models.stock_master import StockMaster
from database.models.stock_price_history import StockPriceHistory
from database.models.stock_predictions import StockPredictions
from database.database import get_db_session

logger = logging.getLogger(__name__)


class EnhancedPredictionService:
    """強化された株価予測サービス"""

    def __init__(self):
        self.model_versions = [
            "STATISTICAL_V2",
            "TREND_FOLLOWING_V1",
            "MEAN_REVERSION_V1",
            "ENSEMBLE_V1",
        ]

    def calculate_technical_indicators(
        self, prices: List[float], volumes: List[int] = None
    ) -> Dict:
        """テクニカル指標を計算"""
        if len(prices) < 20:
            return {}

        prices_array = np.array(prices)
        indicators = {}

        # 移動平均線
        if len(prices) >= 5:
            indicators["sma_5"] = np.mean(prices_array[-5:])
        if len(prices) >= 10:
            indicators["sma_10"] = np.mean(prices_array[-10:])
        if len(prices) >= 20:
            indicators["sma_20"] = np.mean(prices_array[-20:])

        # RSI計算
        if len(prices) >= 15:
            deltas = np.diff(prices_array)
            gains = np.where(deltas > 0, deltas, 0)
            losses = np.where(deltas < 0, -deltas, 0)

            avg_gains = np.mean(gains[-14:])
            avg_losses = np.mean(losses[-14:])

            if avg_losses != 0:
                rs = avg_gains / avg_losses
                indicators["rsi"] = 100 - (100 / (1 + rs))
            else:
                indicators["rsi"] = 100

        # ボラティリティ
        if len(prices) >= 10:
            returns = np.diff(np.log(prices_array))
            indicators["volatility"] = np.std(returns) * np.sqrt(
                252
            )  # 年率ボラティリティ

        # MACD（簡易版）
        if len(prices) >= 26:
            ema_12 = self._calculate_ema(prices_array, 12)
            ema_26 = self._calculate_ema(prices_array, 26)
            indicators["macd"] = ema_12 - ema_26

        # ボリンジャーバンド
        if len(prices) >= 20:
            sma_20 = np.mean(prices_array[-20:])
            std_20 = np.std(prices_array[-20:])
            indicators["bollinger_upper"] = sma_20 + (2 * std_20)
            indicators["bollinger_lower"] = sma_20 - (2 * std_20)
            indicators["bollinger_position"] = (
                prices_array[-1] - indicators["bollinger_lower"]
            ) / (indicators["bollinger_upper"] - indicators["bollinger_lower"])

        # 出来高指標
        if volumes and len(volumes) >= 10:
            volumes_array = np.array(volumes)
            indicators["volume_sma_10"] = np.mean(volumes_array[-10:])
            indicators["volume_ratio"] = volumes_array[-1] / indicators["volume_sma_10"]

        return indicators

    def _calculate_ema(self, prices: np.ndarray, period: int) -> float:
        """指数移動平均を計算"""
        alpha = 2 / (period + 1)
        ema = prices[0]
        for price in prices[1:]:
            ema = alpha * price + (1 - alpha) * ema
        return ema

    def generate_multiple_predictions(
        self, symbol: str, db: Session, days_ahead: int = 30
    ) -> Dict[str, int]:
        """複数モデルによる株価予測を生成"""
        results = {model: 0 for model in self.model_versions}

        try:
            # 過去データを取得
            historical_data = (
                db.query(StockPriceHistory)
                .filter(StockPriceHistory.symbol == symbol.upper())
                .order_by(StockPriceHistory.date.desc())
                .limit(100)
                .all()
            )

            if len(historical_data) < 30:
                logger.warning(f"Insufficient data for {symbol} predictions")
                return results

            # データを分析用に変換
            prices = [float(h.close_price) for h in reversed(historical_data)]
            volumes = [
                int(h.volume) if h.volume else 0 for h in reversed(historical_data)
            ]
            dates = [h.date for h in reversed(historical_data)]

            # テクニカル指標を計算
            indicators = self.calculate_technical_indicators(prices, volumes)

            # 各モデルで予測を生成
            for model_version in self.model_versions:
                predictions_created = self._generate_predictions_with_model(
                    symbol, db, prices, indicators, model_version, days_ahead
                )
                results[model_version] = predictions_created

            logger.info(f"Generated predictions for {symbol}: {results}")
            return results

        except Exception as e:
            logger.error(f"Error generating predictions for {symbol}: {str(e)}")
            return results

    def _generate_predictions_with_model(
        self,
        symbol: str,
        db: Session,
        prices: List[float],
        indicators: Dict,
        model_version: str,
        days_ahead: int,
    ) -> int:
        """特定モデルでの予測生成"""
        try:
            current_price = prices[-1]
            predictions_created = 0
            base_date = datetime.now().date()

            for i in range(1, days_ahead + 1):
                prediction_date = base_date + timedelta(days=i)

                # 既存予測をチェック
                existing = (
                    db.query(StockPredictions)
                    .filter(
                        and_(
                            StockPredictions.symbol == symbol.upper(),
                            StockPredictions.prediction_date == prediction_date,
                            StockPredictions.model_version == model_version,
                        )
                    )
                    .first()
                )

                if existing:
                    continue

                # モデル別予測計算
                prediction_result = self._calculate_prediction_by_model(
                    current_price, prices, indicators, model_version, i
                )

                if prediction_result is None:
                    continue

                predicted_price, confidence, factors = prediction_result

                # 予測データを保存
                prediction = StockPredictions(
                    symbol=symbol.upper(),
                    prediction_date=prediction_date,
                    predicted_price=predicted_price,
                    confidence_score=confidence,
                    model_version=model_version,
                    prediction_days=i,
                    prediction_factors=json.dumps(factors),
                    created_at=datetime.utcnow(),
                )

                db.add(prediction)
                predictions_created += 1

            if predictions_created > 0:
                db.commit()
                logger.info(
                    f"Created {predictions_created} predictions for {symbol} using {model_version}"
                )

            return predictions_created

        except Exception as e:
            logger.error(f"Error in {model_version} predictions for {symbol}: {str(e)}")
            db.rollback()
            return 0

    def _calculate_prediction_by_model(
        self,
        current_price: float,
        prices: List[float],
        indicators: Dict,
        model_version: str,
        days_ahead: int,
    ) -> Optional[Tuple[float, float, Dict]]:
        """モデル別の予測計算"""
        try:
            if model_version == "STATISTICAL_V2":
                return self._statistical_model_v2(
                    current_price, prices, indicators, days_ahead
                )
            elif model_version == "TREND_FOLLOWING_V1":
                return self._trend_following_model(
                    current_price, prices, indicators, days_ahead
                )
            elif model_version == "MEAN_REVERSION_V1":
                return self._mean_reversion_model(
                    current_price, prices, indicators, days_ahead
                )
            elif model_version == "ENSEMBLE_V1":
                return self._ensemble_model(
                    current_price, prices, indicators, days_ahead
                )
            else:
                return None

        except Exception as e:
            logger.error(f"Error in model {model_version}: {str(e)}")
            return None

    def _statistical_model_v2(
        self,
        current_price: float,
        prices: List[float],
        indicators: Dict,
        days_ahead: int,
    ) -> Tuple[float, float, Dict]:
        """統計モデル V2"""
        # 価格変動率の統計分析
        returns = np.diff(np.log(prices[-30:]))  # 過去30日のリターン
        mean_return = np.mean(returns)
        std_return = np.std(returns)

        # ドリフト項とランダムウォーク
        drift = mean_return * days_ahead
        shock = np.random.normal(0, std_return * np.sqrt(days_ahead))

        predicted_price = current_price * np.exp(drift + shock)

        # 信頼度計算（データ品質とボラティリティベース）
        data_quality = min(1.0, len(prices) / 50)
        volatility_penalty = max(0.3, 1.0 - (std_return * 2))
        time_decay = max(0.4, 1.0 - (days_ahead * 0.02))
        confidence = data_quality * volatility_penalty * time_decay

        factors = {
            "mean_return": mean_return,
            "volatility": std_return,
            "drift_component": drift,
            "random_component": shock,
            "data_quality": data_quality,
        }

        return predicted_price, confidence, factors

    def _trend_following_model(
        self,
        current_price: float,
        prices: List[float],
        indicators: Dict,
        days_ahead: int,
    ) -> Tuple[float, float, Dict]:
        """トレンドフォローイングモデル"""
        # 移動平均によるトレンド判定
        sma_5 = indicators.get("sma_5", current_price)
        sma_20 = indicators.get("sma_20", current_price)

        # トレンドの強度
        if sma_20 != 0:
            trend_strength = (sma_5 - sma_20) / sma_20
        else:
            trend_strength = 0

        # RSIによるモメンタム調整
        rsi = indicators.get("rsi", 50)
        momentum_factor = (rsi - 50) / 50  # -1 to 1の範囲

        # 予測価格計算
        trend_component = trend_strength * days_ahead * 0.1
        momentum_component = momentum_factor * 0.05

        predicted_price = current_price * (1 + trend_component + momentum_component)

        # 信頼度（トレンドの明確さに依存）
        trend_clarity = abs(trend_strength)
        confidence = min(0.9, 0.5 + trend_clarity)
        confidence *= max(0.4, 1.0 - (days_ahead * 0.03))

        factors = {
            "trend_strength": trend_strength,
            "momentum_factor": momentum_factor,
            "sma_5": sma_5,
            "sma_20": sma_20,
            "rsi": rsi,
        }

        return predicted_price, confidence, factors

    def _mean_reversion_model(
        self,
        current_price: float,
        prices: List[float],
        indicators: Dict,
        days_ahead: int,
    ) -> Tuple[float, float, Dict]:
        """平均回帰モデル"""
        # 長期平均価格
        long_term_mean = np.mean(prices[-50:]) if len(prices) >= 50 else np.mean(prices)

        # 現在価格の平均からの乖離
        deviation = (current_price - long_term_mean) / long_term_mean

        # ボリンジャーバンドポジション
        bb_position = indicators.get("bollinger_position", 0.5)

        # 平均回帰速度（乖離が大きいほど強い回帰力）
        reversion_speed = abs(deviation) * 0.1

        # 予測価格（平均に向かって回帰）
        reversion_component = -deviation * reversion_speed * days_ahead
        predicted_price = current_price * (1 + reversion_component)

        # ボリンジャーバンド調整
        if bb_position > 0.8:  # 上限近くにいる場合
            predicted_price *= 0.98
        elif bb_position < 0.2:  # 下限近くにいる場合
            predicted_price *= 1.02

        # 信頼度（乖離が大きいほど高い信頼度）
        confidence = min(0.85, 0.4 + abs(deviation))
        confidence *= max(0.3, 1.0 - (days_ahead * 0.04))

        factors = {
            "long_term_mean": long_term_mean,
            "deviation_from_mean": deviation,
            "reversion_speed": reversion_speed,
            "bollinger_position": bb_position,
        }

        return predicted_price, confidence, factors

    def _ensemble_model(
        self,
        current_price: float,
        prices: List[float],
        indicators: Dict,
        days_ahead: int,
    ) -> Tuple[float, float, Dict]:
        """アンサンブルモデル（複数モデルの組み合わせ）"""
        # 各モデルの予測を取得
        statistical = self._statistical_model_v2(
            current_price, prices, indicators, days_ahead
        )
        trend = self._trend_following_model(
            current_price, prices, indicators, days_ahead
        )
        reversion = self._mean_reversion_model(
            current_price, prices, indicators, days_ahead
        )

        # 重み付き平均（信頼度に基づく重み）
        models = [statistical, trend, reversion]
        weights = [model[1] for model in models]  # 信頼度を重みとして使用
        total_weight = sum(weights)

        if total_weight == 0:
            return current_price, 0.3, {"error": "All models failed"}

        # 重み付き予測価格
        weighted_price = (
            sum(model[0] * weight for model, weight in zip(models, weights))
            / total_weight
        )

        # アンサンブル信頼度（個別モデル信頼度の調和平均）
        ensemble_confidence = len(weights) / sum(
            1 / w if w > 0 else float("inf") for w in weights
        )
        ensemble_confidence = min(0.95, ensemble_confidence)

        factors = {
            "statistical_price": statistical[0],
            "statistical_confidence": statistical[1],
            "trend_price": trend[0],
            "trend_confidence": trend[1],
            "reversion_price": reversion[0],
            "reversion_confidence": reversion[1],
            "weights": weights,
            "ensemble_method": "weighted_average",
        }

        return weighted_price, ensemble_confidence, factors

    def update_historical_accuracy(self, symbol: str, db: Session) -> int:
        """過去予測の精度を実績と比較して更新"""
        try:
            # 実績が判明している過去予測を取得
            cutoff_date = (datetime.now() - timedelta(days=1)).date()

            predictions = (
                db.query(StockPredictions)
                .filter(
                    and_(
                        StockPredictions.symbol == symbol.upper(),
                        StockPredictions.prediction_date <= cutoff_date,
                        or_(
                            StockPredictions.actual_price.is_(None),
                            StockPredictions.accuracy_score.is_(None),
                        ),
                    )
                )
                .all()
            )

            updated_count = 0

            for prediction in predictions:
                # 実際の価格データを取得
                actual_data = (
                    db.query(StockPriceHistory)
                    .filter(
                        and_(
                            StockPriceHistory.symbol == symbol.upper(),
                            StockPriceHistory.date == prediction.prediction_date,
                        )
                    )
                    .first()
                )

                if actual_data:
                    actual_price = float(actual_data.close_price)
                    predicted_price = float(prediction.predicted_price)

                    # 精度計算（MAPE: Mean Absolute Percentage Error）
                    if actual_price != 0:
                        accuracy = (
                            1 - abs(predicted_price - actual_price) / actual_price
                        )
                        accuracy = max(0, min(1, accuracy))  # 0-1の範囲に制限
                    else:
                        accuracy = 0

                    # 予測データを更新
                    prediction.actual_price = actual_price
                    prediction.accuracy_score = accuracy
                    updated_count += 1

            if updated_count > 0:
                db.commit()
                logger.info(
                    f"Updated accuracy for {updated_count} predictions for {symbol}"
                )

            return updated_count

        except Exception as e:
            logger.error(f"Error updating historical accuracy for {symbol}: {str(e)}")
            db.rollback()
            return 0

    def batch_generate_enhanced_predictions(
        self, limit: int = 50, days_ahead: int = 30
    ) -> Dict:
        """強化された予測の一括生成"""
        results = {
            "symbols_processed": 0,
            "total_predictions": 0,
            "accuracy_updates": 0,
            "errors": 0,
            "model_results": {model: 0 for model in self.model_versions},
        }

        try:
            # アクティブな銘柄を取得
            with get_db_session() as db:
                symbols = (
                    db.query(StockMaster.symbol)
                    .filter(StockMaster.is_active == 1)
                    .limit(limit)
                    .all()
                )

                symbol_list = [s.symbol for s in symbols]

            # 並列処理で予測生成
            with ThreadPoolExecutor(max_workers=6) as executor:
                future_to_symbol = {
                    executor.submit(
                        self._process_single_symbol_enhanced, symbol, days_ahead
                    ): symbol
                    for symbol in symbol_list
                }

                for future in as_completed(future_to_symbol):
                    symbol = future_to_symbol[future]
                    try:
                        result = future.result()
                        results["symbols_processed"] += 1
                        results["accuracy_updates"] += result["accuracy_updates"]

                        for model, count in result["model_results"].items():
                            results["model_results"][model] += count
                            results["total_predictions"] += count

                        if sum(result["model_results"].values()) > 0:
                            logger.info(
                                f"Enhanced predictions for {symbol}: {result['model_results']}"
                            )

                    except Exception as e:
                        logger.error(
                            f"Error processing enhanced predictions for {symbol}: {str(e)}"
                        )
                        results["errors"] += 1

            logger.info(f"Batch enhanced prediction results: {results}")
            return results

        except Exception as e:
            logger.error(f"Error in batch enhanced prediction processing: {str(e)}")
            results["errors"] += 1
            return results

    def _process_single_symbol_enhanced(self, symbol: str, days_ahead: int) -> Dict:
        """単一銘柄の強化予測処理"""
        result = {
            "model_results": {model: 0 for model in self.model_versions},
            "accuracy_updates": 0,
        }

        try:
            with get_db_session() as db:
                # 複数モデル予測生成
                model_results = self.generate_multiple_predictions(
                    symbol, db, days_ahead
                )
                result["model_results"] = model_results

                # 精度更新
                result["accuracy_updates"] = self.update_historical_accuracy(symbol, db)

        except Exception as e:
            logger.error(
                f"Error processing enhanced predictions for {symbol}: {str(e)}"
            )

        return result
