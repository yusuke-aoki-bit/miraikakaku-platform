#!/usr/bin/env python3
"""
AI予測精度向上システム
AI Prediction Accuracy Improvement System

機械学習モデルの精度を継続的に改善し、最適化する
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Tuple, Optional, Any
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
import logging
from sqlalchemy.orm import Session
from sqlalchemy import text
import joblib
import json
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import StandardScaler, MinMaxScaler
from sklearn.model_selection import cross_val_score, TimeSeriesSplit
import warnings
warnings.filterwarnings('ignore')

from .logging_config import setup_logging
from .database import get_db

logger = setup_logging(__name__)

@dataclass
class ModelPerformance:
    """モデル性能指標"""
    model_name: str
    mae: float  # Mean Absolute Error
    mse: float  # Mean Squared Error
    rmse: float  # Root Mean Squared Error
    r2: float   # R-squared
    accuracy_percentage: float
    prediction_count: int
    last_updated: datetime

@dataclass
class PredictionAccuracy:
    """予測精度データ"""
    symbol: str
    prediction_date: datetime
    target_date: datetime
    predicted_price: float
    actual_price: float
    absolute_error: float
    percentage_error: float
    model_name: str

class PredictionAccuracySystem:
    """予測精度向上システム"""

    def __init__(self):
        self.models = {}
        self.scalers = {}
        self.feature_columns = [
            'open_price', 'high_price', 'low_price', 'close_price', 'volume',
            'ma_5', 'ma_10', 'ma_20', 'rsi', 'bollinger_upper', 'bollinger_lower'
        ]
        self.model_configs = {
            'random_forest': {
                'class': RandomForestRegressor,
                'params': {'n_estimators': 100, 'max_depth': 10, 'random_state': 42}
            },
            'gradient_boosting': {
                'class': GradientBoostingRegressor,
                'params': {'n_estimators': 100, 'max_depth': 6, 'random_state': 42}
            },
            'linear_regression': {
                'class': LinearRegression,
                'params': {}
            }
        }

    def calculate_technical_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        """テクニカル指標を計算"""
        try:
            # Moving Averages
            df['ma_5'] = df['close_price'].rolling(window=5).mean()
            df['ma_10'] = df['close_price'].rolling(window=10).mean()
            df['ma_20'] = df['close_price'].rolling(window=20).mean()

            # RSI
            delta = df['close_price'].diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
            rs = gain / loss
            df['rsi'] = 100 - (100 / (1 + rs))

            # Bollinger Bands
            rolling_mean = df['close_price'].rolling(window=20).mean()
            rolling_std = df['close_price'].rolling(window=20).std()
            df['bollinger_upper'] = rolling_mean + (rolling_std * 2)
            df['bollinger_lower'] = rolling_mean - (rolling_std * 2)

            # Volume indicators
            df['volume_ma'] = df['volume'].rolling(window=10).mean()
            df['volume_ratio'] = df['volume'] / df['volume_ma']

            return df.fillna(method='bfill').fillna(method='ffill')
        except Exception as e:
            logger.error(f"Error calculating technical indicators: {e}")
            return df

    def prepare_training_data(self, symbol: str, db: Session) -> Tuple[np.ndarray, np.ndarray]:
        """学習用データを準備"""
        try:
            # 価格履歴を取得
            query = text("""
                SELECT date, open_price, high_price, low_price, close_price, volume
                FROM stock_prices
                WHERE symbol = :symbol
                AND date >= CURRENT_DATE - INTERVAL '2 years'
                ORDER BY date ASC
            """)

            result = db.execute(query, {"symbol": symbol})
            data = result.fetchall()

            if len(data) < 50:
                logger.warning(f"Insufficient data for {symbol}: {len(data)} records")
                return None, None

            # DataFrameに変換
            df = pd.DataFrame(data, columns=['date', 'open_price', 'high_price', 'low_price', 'close_price', 'volume'])
            df['date'] = pd.to_datetime(df['date'])
            df = df.sort_values('date')

            # テクニカル指標を計算
            df = self.calculate_technical_indicators(df)

            # 特徴量とターゲットを準備
            features = []
            targets = []

            for i in range(20, len(df) - 1):  # 20日分の履歴を使用
                feature_row = []
                for col in self.feature_columns:
                    if col in df.columns:
                        feature_row.extend(df[col].iloc[i-5:i].values)  # 過去5日分
                    else:
                        feature_row.extend([0] * 5)  # デフォルト値

                features.append(feature_row)
                targets.append(df['close_price'].iloc[i + 1])  # 翌日の終値

            return np.array(features), np.array(targets)

        except Exception as e:
            logger.error(f"Error preparing training data for {symbol}: {e}")
            return None, None

    def train_models(self, symbol: str, db: Session) -> Dict[str, ModelPerformance]:
        """モデルを学習"""
        try:
            X, y = self.prepare_training_data(symbol, db)
            if X is None or len(X) < 30:
                logger.warning(f"Insufficient data to train models for {symbol}")
                return {}

            # データを訓練・テストに分割
            split_idx = int(len(X) * 0.8)
            X_train, X_test = X[:split_idx], X[split_idx:]
            y_train, y_test = y[:split_idx], y[split_idx:]

            # スケーリング
            scaler = StandardScaler()
            X_train_scaled = scaler.fit_transform(X_train)
            X_test_scaled = scaler.transform(X_test)

            results = {}

            for model_name, config in self.model_configs.items():
                try:
                    # モデルを作成・学習
                    model = config['class'](**config['params'])
                    model.fit(X_train_scaled, y_train)

                    # 予測
                    y_pred = model.predict(X_test_scaled)

                    # 性能指標を計算
                    mae = mean_absolute_error(y_test, y_pred)
                    mse = mean_squared_error(y_test, y_pred)
                    rmse = np.sqrt(mse)
                    r2 = r2_score(y_test, y_pred)

                    # 精度パーセンテージ（MAPE の逆）
                    mape = np.mean(np.abs((y_test - y_pred) / y_test)) * 100
                    accuracy = max(0, 100 - mape)

                    performance = ModelPerformance(
                        model_name=model_name,
                        mae=mae,
                        mse=mse,
                        rmse=rmse,
                        r2=r2,
                        accuracy_percentage=accuracy,
                        prediction_count=len(y_test),
                        last_updated=datetime.utcnow()
                    )

                    results[model_name] = performance

                    # モデルとスケーラーを保存
                    model_key = f"{symbol}_{model_name}"
                    self.models[model_key] = model
                    self.scalers[model_key] = scaler

                    logger.info(f"Trained {model_name} for {symbol}: Accuracy={accuracy:.2f}%, R2={r2:.3f}")

                except Exception as e:
                    logger.error(f"Error training {model_name} for {symbol}: {e}")

            return results

        except Exception as e:
            logger.error(f"Error in train_models for {symbol}: {e}")
            return {}

    def evaluate_predictions(self, symbol: str, db: Session, days_back: int = 30) -> List[PredictionAccuracy]:
        """既存の予測を評価"""
        try:
            # 過去の予測と実際の価格を取得
            query = text("""
                SELECT
                    sp.symbol,
                    sp.prediction_date,
                    sp.target_date,
                    sp.predicted_price,
                    sp.model_name,
                    pr.close_price as actual_price
                FROM stock_predictions sp
                JOIN stock_prices pr ON sp.symbol = pr.symbol
                    AND DATE(sp.target_date) = DATE(pr.date)
                WHERE sp.symbol = :symbol
                AND sp.target_date >= CURRENT_DATE - INTERVAL :days_back DAY
                AND sp.target_date <= CURRENT_DATE
                AND sp.predicted_price IS NOT NULL
                AND pr.close_price IS NOT NULL
                ORDER BY sp.target_date DESC
            """)

            result = db.execute(query, {"symbol": symbol, "days_back": days_back})
            predictions = result.fetchall()

            accuracy_data = []

            for pred in predictions:
                absolute_error = abs(pred.predicted_price - pred.actual_price)
                percentage_error = (absolute_error / pred.actual_price) * 100

                accuracy = PredictionAccuracy(
                    symbol=pred.symbol,
                    prediction_date=pred.prediction_date,
                    target_date=pred.target_date,
                    predicted_price=pred.predicted_price,
                    actual_price=pred.actual_price,
                    absolute_error=absolute_error,
                    percentage_error=percentage_error,
                    model_name=pred.model_name
                )

                accuracy_data.append(accuracy)

            return accuracy_data

        except Exception as e:
            logger.error(f"Error evaluating predictions for {symbol}: {e}")
            return []

    def get_model_rankings(self, db: Session) -> Dict[str, Any]:
        """モデルのランキングを取得"""
        try:
            query = text("""
                SELECT
                    model_name,
                    COUNT(*) as prediction_count,
                    AVG(ABS(predicted_price - actual_price) / actual_price * 100) as avg_error_pct,
                    AVG(predicted_price) as avg_predicted,
                    AVG(actual_price) as avg_actual
                FROM (
                    SELECT
                        sp.model_name,
                        sp.predicted_price,
                        pr.close_price as actual_price
                    FROM stock_predictions sp
                    JOIN stock_prices pr ON sp.symbol = pr.symbol
                        AND DATE(sp.target_date) = DATE(pr.date)
                    WHERE sp.target_date >= CURRENT_DATE - INTERVAL '30' DAY
                    AND sp.target_date <= CURRENT_DATE
                    AND sp.predicted_price IS NOT NULL
                    AND pr.close_price IS NOT NULL
                ) as predictions
                GROUP BY model_name
                HAVING COUNT(*) >= 10
                ORDER BY avg_error_pct ASC
            """)

            result = db.execute(query)
            rankings = result.fetchall()

            model_stats = {}
            for rank, row in enumerate(rankings, 1):
                accuracy = max(0, 100 - row.avg_error_pct)
                model_stats[row.model_name] = {
                    'rank': rank,
                    'accuracy_percentage': accuracy,
                    'avg_error_percentage': row.avg_error_pct,
                    'prediction_count': row.prediction_count,
                    'avg_predicted': row.avg_predicted,
                    'avg_actual': row.avg_actual
                }

            return model_stats

        except Exception as e:
            logger.error(f"Error getting model rankings: {e}")
            return {}

    def optimize_model_parameters(self, symbol: str, db: Session) -> Dict[str, Any]:
        """モデルパラメータを最適化"""
        try:
            X, y = self.prepare_training_data(symbol, db)
            if X is None or len(X) < 50:
                return {"error": "Insufficient data for optimization"}

            scaler = StandardScaler()
            X_scaled = scaler.fit_transform(X)

            best_results = {}

            # Random Forest の最適化
            rf_params = [
                {'n_estimators': 50, 'max_depth': 5},
                {'n_estimators': 100, 'max_depth': 10},
                {'n_estimators': 200, 'max_depth': 15}
            ]

            best_rf_score = -float('inf')
            best_rf_params = None

            for params in rf_params:
                model = RandomForestRegressor(**params, random_state=42)
                scores = cross_val_score(model, X_scaled, y, cv=3, scoring='neg_mean_absolute_error')
                avg_score = scores.mean()

                if avg_score > best_rf_score:
                    best_rf_score = avg_score
                    best_rf_params = params

            best_results['random_forest'] = {
                'params': best_rf_params,
                'score': -best_rf_score
            }

            logger.info(f"Optimized Random Forest for {symbol}: {best_rf_params}, Score: {-best_rf_score:.3f}")

            return best_results

        except Exception as e:
            logger.error(f"Error optimizing model parameters for {symbol}: {e}")
            return {"error": str(e)}

    def generate_ensemble_prediction(self, symbol: str, db: Session) -> Optional[float]:
        """アンサンブル予測を生成"""
        try:
            X, _ = self.prepare_training_data(symbol, db)
            if X is None or len(X) == 0:
                return None

            # 最新のデータポイントを使用
            latest_features = X[-1].reshape(1, -1)

            predictions = []
            weights = []

            for model_name in self.model_configs.keys():
                model_key = f"{symbol}_{model_name}"
                if model_key in self.models and model_key in self.scalers:
                    try:
                        scaler = self.scalers[model_key]
                        model = self.models[model_key]

                        scaled_features = scaler.transform(latest_features)
                        prediction = model.predict(scaled_features)[0]

                        predictions.append(prediction)

                        # モデルの重み（精度に基づく）
                        # 実装では、各モデルの過去の性能に基づいて重みを設定
                        weights.append(1.0)  # 簡易実装

                    except Exception as e:
                        logger.warning(f"Error predicting with {model_name}: {e}")

            if predictions:
                # 重み付き平均
                ensemble_prediction = np.average(predictions, weights=weights)
                return float(ensemble_prediction)

            return None

        except Exception as e:
            logger.error(f"Error generating ensemble prediction for {symbol}: {e}")
            return None

    def get_accuracy_report(self, db: Session, days: int = 30) -> Dict[str, Any]:
        """精度レポートを生成"""
        try:
            # 全体的な統計
            query = text("""
                SELECT
                    COUNT(*) as total_predictions,
                    AVG(ABS(predicted_price - actual_price) / actual_price * 100) as avg_error_pct,
                    MIN(prediction_date) as earliest_prediction,
                    MAX(prediction_date) as latest_prediction,
                    COUNT(DISTINCT symbol) as symbols_count
                FROM (
                    SELECT
                        sp.symbol,
                        sp.prediction_date,
                        sp.predicted_price,
                        pr.close_price as actual_price
                    FROM stock_predictions sp
                    JOIN stock_prices pr ON sp.symbol = pr.symbol
                        AND DATE(sp.target_date) = DATE(pr.date)
                    WHERE sp.target_date >= CURRENT_DATE - INTERVAL :days DAY
                    AND sp.target_date <= CURRENT_DATE
                    AND sp.predicted_price IS NOT NULL
                    AND pr.close_price IS NOT NULL
                ) as predictions
            """)

            result = db.execute(query, {"days": days})
            overall = result.fetchone()

            # モデル別統計
            model_rankings = self.get_model_rankings(db)

            # 銘柄別統計
            symbol_query = text("""
                SELECT
                    symbol,
                    COUNT(*) as prediction_count,
                    AVG(ABS(predicted_price - actual_price) / actual_price * 100) as avg_error_pct
                FROM (
                    SELECT
                        sp.symbol,
                        sp.predicted_price,
                        pr.close_price as actual_price
                    FROM stock_predictions sp
                    JOIN stock_prices pr ON sp.symbol = pr.symbol
                        AND DATE(sp.target_date) = DATE(pr.date)
                    WHERE sp.target_date >= CURRENT_DATE - INTERVAL :days DAY
                    AND sp.target_date <= CURRENT_DATE
                    AND sp.predicted_price IS NOT NULL
                    AND pr.close_price IS NOT NULL
                ) as predictions
                GROUP BY symbol
                HAVING COUNT(*) >= 5
                ORDER BY avg_error_pct ASC
                LIMIT 10
            """)

            symbol_result = db.execute(symbol_query, {"days": days})
            top_symbols = symbol_result.fetchall()

            return {
                "period_days": days,
                "overall": {
                    "total_predictions": overall.total_predictions if overall else 0,
                    "average_accuracy": max(0, 100 - (overall.avg_error_pct if overall and overall.avg_error_pct else 100)),
                    "symbols_analyzed": overall.symbols_count if overall else 0,
                    "date_range": {
                        "start": overall.earliest_prediction.isoformat() if overall and overall.earliest_prediction else None,
                        "end": overall.latest_prediction.isoformat() if overall and overall.latest_prediction else None
                    }
                },
                "model_rankings": model_rankings,
                "top_performing_symbols": [
                    {
                        "symbol": row.symbol,
                        "prediction_count": row.prediction_count,
                        "accuracy_percentage": max(0, 100 - row.avg_error_pct)
                    } for row in top_symbols
                ]
            }

        except Exception as e:
            logger.error(f"Error generating accuracy report: {e}")
            return {"error": str(e)}

# グローバルインスタンス
prediction_accuracy_system = PredictionAccuracySystem()

def get_accuracy_analytics(days: int = 30) -> Dict[str, Any]:
    """精度分析を取得（便利関数）"""
    try:
        with next(get_db()) as db:
            return prediction_accuracy_system.get_accuracy_report(db, days)
    except Exception as e:
        logger.error(f"Error getting accuracy analytics: {e}")
        return {"error": str(e)}

def train_symbol_models(symbol: str) -> Dict[str, Any]:
    """指定銘柄のモデルを学習（便利関数）"""
    try:
        with next(get_db()) as db:
            results = prediction_accuracy_system.train_models(symbol, db)
            return {
                "symbol": symbol,
                "models_trained": len(results),
                "results": {name: asdict(perf) for name, perf in results.items()}
            }
    except Exception as e:
        logger.error(f"Error training models for {symbol}: {e}")
        return {"error": str(e)}