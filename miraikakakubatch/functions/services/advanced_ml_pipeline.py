import pandas as pd
import numpy as np
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense, Dropout
from tensorflow.keras.optimizers import Adam
from tensorflow.keras.callbacks import EarlyStopping, ReduceLROnPlateau
from prophet import Prophet
from prophet.diagnostics import cross_validation, performance_metrics
from sklearn.preprocessing import MinMaxScaler
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sqlalchemy.orm import Session
from database.database import get_db_session
from database.models import StockPriceHistory, StockPredictions, AIInferenceLog
from datetime import datetime, timedelta
import joblib
import logging
import uuid
import json
from typing import Dict, List, Tuple, Optional
import warnings
warnings.filterwarnings('ignore')

logger = logging.getLogger(__name__)

class AdvancedMLPipeline:
    def __init__(self):
        self.db_session = get_db_session()
        self.scaler = MinMaxScaler()
        self.lstm_model = None
        self.prophet_model = None
        
    def prepare_lstm_data(self, symbol: str, lookback_days: int = 60) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
        """LSTM用のデータ準備"""
        try:
            # 過去1年のデータを取得
            start_date = datetime.utcnow() - timedelta(days=365)
            
            price_data = self.db_session.query(StockPriceHistory).filter(
                StockPriceHistory.symbol == symbol,
                StockPriceHistory.date >= start_date
            ).order_by(StockPriceHistory.date.asc()).all()
            
            if len(price_data) < lookback_days + 20:
                logger.warning(f"LSTM訓練データが不足: {symbol}")
                return None, None, None
            
            # 特徴量を準備（多次元）
            features = []
            for price in price_data:
                features.append([
                    float(price.close_price),
                    float(price.open_price or price.close_price),
                    float(price.high_price or price.close_price),
                    float(price.low_price or price.close_price),
                    float(price.volume or 0) / 1000000,  # 正規化
                ])
            
            features_array = np.array(features)
            
            # データを正規化
            scaled_features = self.scaler.fit_transform(features_array)
            
            # LSTM用のシーケンスデータを作成
            X, y = [], []
            for i in range(lookback_days, len(scaled_features)):
                X.append(scaled_features[i-lookback_days:i])
                y.append(scaled_features[i, 0])  # 終値のみを予測
            
            return np.array(X), np.array(y), scaled_features
            
        except Exception as e:
            logger.error(f"LSTM データ準備エラー {symbol}: {e}")
            return None, None, None

    def build_lstm_model(self, input_shape: Tuple[int, int]) -> Sequential:
        """LSTMモデルを構築"""
        model = Sequential([
            LSTM(100, return_sequences=True, input_shape=input_shape),
            Dropout(0.2),
            LSTM(100, return_sequences=True),
            Dropout(0.2),
            LSTM(50, return_sequences=False),
            Dropout(0.2),
            Dense(25),
            Dense(1)
        ])
        
        model.compile(
            optimizer=Adam(learning_rate=0.001),
            loss='mse',
            metrics=['mae']
        )
        
        return model

    def train_lstm_model(self, symbol: str) -> Optional[Dict[str, Any]]:
        """LSTM モデルを訓練"""
        try:
            logger.info(f"LSTM モデル訓練開始: {symbol}")
            
            X, y, scaled_data = self.prepare_lstm_data(symbol)
            if X is None:
                return None
            
            # 訓練・テストデータ分割
            split_index = int(len(X) * 0.8)
            X_train, X_test = X[:split_index], X[split_index:]
            y_train, y_test = y[:split_index], y[split_index:]
            
            # モデル構築
            model = self.build_lstm_model((X.shape[1], X.shape[2]))
            
            # コールバック設定
            callbacks = [
                EarlyStopping(patience=10, restore_best_weights=True),
                ReduceLROnPlateau(patience=5, factor=0.5)
            ]
            
            # 訓練実行
            history = model.fit(
                X_train, y_train,
                batch_size=32,
                epochs=100,
                validation_data=(X_test, y_test),
                callbacks=callbacks,
                verbose=0
            )
            
            # 予測と評価
            y_pred = model.predict(X_test, verbose=0)
            
            # 逆正規化
            y_test_original = self.scaler.inverse_transform(
                np.column_stack([y_test] + [np.zeros((len(y_test), 4))])
            )[:, 0]
            y_pred_original = self.scaler.inverse_transform(
                np.column_stack([y_pred.flatten()] + [np.zeros((len(y_pred), 4))])
            )[:, 0]
            
            # 評価指標
            mae = mean_absolute_error(y_test_original, y_pred_original)
            mse = mean_squared_error(y_test_original, y_pred_original)
            r2 = r2_score(y_test_original, y_pred_original)
            
            # 将来の予測を生成
            last_sequence = X[-1].reshape(1, X.shape[1], X.shape[2])
            future_predictions = []
            
            for i in range(7):  # 7日間の予測
                pred = model.predict(last_sequence, verbose=0)[0, 0]
                future_predictions.append(pred)
                
                # 次の予測のためにシーケンスを更新
                new_row = np.array([[pred, pred, pred, pred, 0]])  # 簡略化
                last_sequence = np.append(last_sequence[:, 1:, :], new_row.reshape(1, 1, 5), axis=1)
            
            # 逆正規化
            future_prices = self.scaler.inverse_transform(
                np.column_stack([future_predictions] + [np.zeros((len(future_predictions), 4))])
            )[:, 0]
            
            # 予測をデータベースに保存
            self.save_lstm_predictions(symbol, future_prices)
            
            logger.info(f"LSTM モデル訓練完了: {symbol}, MAE: {mae:.4f}, R²: {r2:.4f}")
            
            return {
                'model_type': 'lstm',
                'symbol': symbol,
                'mae': mae,
                'mse': mse,
                'r2_score': r2,
                'training_loss': history.history['loss'][-1],
                'validation_loss': history.history['val_loss'][-1],
                'future_predictions': future_prices.tolist(),
                'training_completed': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"LSTM 訓練エラー {symbol}: {e}")
            return None

    def train_prophet_model(self, symbol: str) -> Optional[Dict[str, Any]]:
        """Prophet モデルを訓練"""
        try:
            logger.info(f"Prophet モデル訓練開始: {symbol}")
            
            # データ取得
            start_date = datetime.utcnow() - timedelta(days=730)  # 2年分
            
            price_data = self.db_session.query(StockPriceHistory).filter(
                StockPriceHistory.symbol == symbol,
                StockPriceHistory.date >= start_date
            ).order_by(StockPriceHistory.date.asc()).all()
            
            if len(price_data) < 365:
                logger.warning(f"Prophet 訓練データが不足: {symbol}")
                return None
            
            # Prophet用データフォーマット
            df = pd.DataFrame([{
                'ds': price.date,
                'y': float(price.close_price)
            } for price in price_data])
            
            # 外部変数を追加（ボリューム、移動平均など）
            df['volume'] = [float(p.volume or 0) for p in price_data]
            df['high'] = [float(p.high_price or p.close_price) for p in price_data]
            df['low'] = [float(p.low_price or p.close_price) for p in price_data]
            
            # 移動平均を追加
            df['sma_5'] = df['y'].rolling(5).mean()
            df['sma_20'] = df['y'].rolling(20).mean()
            
            # Prophet モデル構築
            model = Prophet(
                daily_seasonality=True,
                weekly_seasonality=True,
                yearly_seasonality=True,
                changepoint_prior_scale=0.05,
                seasonality_prior_scale=10.0,
                holidays_prior_scale=10.0,
                seasonality_mode='multiplicative',
                interval_width=0.8
            )
            
            # 外部変数を追加
            model.add_regressor('volume')
            model.add_regressor('sma_5')
            model.add_regressor('sma_20')
            
            # モデル訓練
            model.fit(df.dropna())
            
            # 将来30日の予測
            future = model.make_future_dataframe(periods=30)
            
            # 外部変数を推定（最後の値を使用）
            last_volume = df['volume'].iloc[-1]
            last_sma5 = df['sma_5'].iloc[-1]
            last_sma20 = df['sma_20'].iloc[-1]
            
            future['volume'] = future['volume'].fillna(last_volume)
            future['sma_5'] = future['sma_5'].fillna(last_sma5)
            future['sma_20'] = future['sma_20'].fillna(last_sma20)
            
            # 予測実行
            forecast = model.predict(future)
            
            # 評価（クロスバリデーション）
            df_cv = cross_validation(model, initial='365 days', period='30 days', horizon='7 days')
            performance = performance_metrics(df_cv)
            
            # 将来予測を抽出
            future_predictions = forecast.tail(30)
            
            # データベースに予測を保存
            self.save_prophet_predictions(symbol, future_predictions)
            
            logger.info(f"Prophet モデル訓練完了: {symbol}")
            
            return {
                'model_type': 'prophet',
                'symbol': symbol,
                'mae': performance['mae'].mean(),
                'mape': performance['mape'].mean(),
                'rmse': np.sqrt(performance['mse'].mean()),
                'coverage': performance['coverage'].mean(),
                'future_predictions': future_predictions[['ds', 'yhat', 'yhat_lower', 'yhat_upper']].to_dict('records'),
                'training_completed': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Prophet 訓練エラー {symbol}: {e}")
            return None

    def save_lstm_predictions(self, symbol: str, predictions: np.ndarray):
        """LSTM予測をデータベースに保存"""
        try:
            for i, pred_price in enumerate(predictions):
                target_date = datetime.utcnow() + timedelta(days=i+1)
                
                prediction = StockPredictions(
                    symbol=symbol,
                    prediction_date=datetime.utcnow(),
                    target_date=target_date,
                    predicted_price=float(pred_price),
                    confidence_score=0.75,  # LSTM固定値
                    prediction_type="daily",
                    model_name="lstm",
                    model_version="2.0"
                )
                
                self.db_session.add(prediction)
            
            self.db_session.commit()
            logger.info(f"LSTM予測保存完了: {symbol}")
            
        except Exception as e:
            logger.error(f"LSTM予測保存エラー {symbol}: {e}")
            self.db_session.rollback()

    def save_prophet_predictions(self, symbol: str, forecast: pd.DataFrame):
        """Prophet予測をデータベースに保存"""
        try:
            for _, row in forecast.iterrows():
                # 信頼区間から信頼度を計算
                prediction_range = row['yhat_upper'] - row['yhat_lower']
                confidence = max(0.1, min(0.95, 1.0 - (prediction_range / row['yhat'])))
                
                prediction = StockPredictions(
                    symbol=symbol,
                    prediction_date=datetime.utcnow(),
                    target_date=row['ds'].to_pydatetime(),
                    predicted_price=float(row['yhat']),
                    confidence_score=confidence,
                    prediction_type="daily",
                    model_name="prophet",
                    model_version="2.0",
                    features_used=json.dumps({
                        'lower_bound': float(row['yhat_lower']),
                        'upper_bound': float(row['yhat_upper']),
                        'trend': float(row.get('trend', 0)),
                        'seasonal': float(row.get('seasonal', 0))
                    })
                )
                
                self.db_session.add(prediction)
            
            self.db_session.commit()
            logger.info(f"Prophet予測保存完了: {symbol}")
            
        except Exception as e:
            logger.error(f"Prophet予測保存エラー {symbol}: {e}")
            self.db_session.rollback()

    def ensemble_prediction(self, symbol: str) -> Optional[Dict[str, Any]]:
        """複数モデルのアンサンブル予測"""
        try:
            logger.info(f"アンサンブル予測開始: {symbol}")
            
            # LSTM予測を取得
            lstm_results = self.train_lstm_model(symbol)
            
            # Prophet予測を取得
            prophet_results = self.train_prophet_model(symbol)
            
            if not lstm_results or not prophet_results:
                logger.warning(f"アンサンブル用データが不足: {symbol}")
                return None
            
            # 重み付き平均でアンサンブル
            lstm_weight = 0.6  # LSTMの重み
            prophet_weight = 0.4  # Prophetの重み
            
            ensemble_predictions = []
            lstm_preds = lstm_results['future_predictions']
            prophet_preds = [p['yhat'] for p in prophet_results['future_predictions'][:len(lstm_preds)]]
            
            for i in range(min(len(lstm_preds), len(prophet_preds))):
                ensemble_price = (lstm_preds[i] * lstm_weight + prophet_preds[i] * prophet_weight)
                ensemble_predictions.append(ensemble_price)
            
            # アンサンブル予測を保存
            for i, pred_price in enumerate(ensemble_predictions):
                target_date = datetime.utcnow() + timedelta(days=i+1)
                
                prediction = StockPredictions(
                    symbol=symbol,
                    prediction_date=datetime.utcnow(),
                    target_date=target_date,
                    predicted_price=float(pred_price),
                    confidence_score=0.85,  # アンサンブルは高信頼度
                    prediction_type="daily",
                    model_name="ensemble",
                    model_version="1.0",
                    features_used=json.dumps({
                        'lstm_weight': lstm_weight,
                        'prophet_weight': prophet_weight,
                        'lstm_prediction': lstm_preds[i],
                        'prophet_prediction': prophet_preds[i]
                    })
                )
                
                self.db_session.add(prediction)
            
            self.db_session.commit()
            
            # 推論ログを記録
            self.log_inference(
                model_name="ensemble",
                symbol=symbol,
                input_data={"models": ["lstm", "prophet"]},
                output_data={"predictions": ensemble_predictions},
                confidence=0.85
            )
            
            logger.info(f"アンサンブル予測完了: {symbol}")
            
            return {
                'model_type': 'ensemble',
                'symbol': symbol,
                'lstm_results': lstm_results,
                'prophet_results': prophet_results,
                'ensemble_predictions': ensemble_predictions,
                'weights': {'lstm': lstm_weight, 'prophet': prophet_weight}
            }
            
        except Exception as e:
            logger.error(f"アンサンブル予測エラー {symbol}: {e}")
            return None

    def log_inference(self, model_name: str, symbol: str, input_data: dict, 
                     output_data: dict, confidence: float):
        """推論ログを記録"""
        try:
            log_entry = AIInferenceLog(
                request_id=str(uuid.uuid4()),
                model_name=model_name,
                model_version="2.0",
                input_data=json.dumps(input_data),
                output_data=json.dumps(output_data),
                confidence_score=confidence,
                is_successful=True,
                endpoint=f"/predict/{symbol}"
            )
            
            self.db_session.add(log_entry)
            self.db_session.commit()
            
        except Exception as e:
            logger.error(f"推論ログエラー: {e}")

    def evaluate_model_performance(self, symbol: str, days_back: int = 30) -> Dict[str, Any]:
        """モデル性能を評価"""
        try:
            # 検証期間の実際の価格を取得
            end_date = datetime.utcnow() - timedelta(days=1)
            start_date = end_date - timedelta(days=days_back)
            
            actual_prices = self.db_session.query(StockPriceHistory).filter(
                StockPriceHistory.symbol == symbol,
                StockPriceHistory.date >= start_date,
                StockPriceHistory.date <= end_date
            ).order_by(StockPriceHistory.date.asc()).all()
            
            # 対応する予測を取得
            predictions = self.db_session.query(StockPredictions).filter(
                StockPredictions.symbol == symbol,
                StockPredictions.target_date >= start_date,
                StockPredictions.target_date <= end_date
            ).all()
            
            # モデル別の性能を計算
            model_performance = {}
            
            for model_name in ['lstm', 'prophet', 'ensemble']:
                model_preds = [p for p in predictions if p.model_name == model_name]
                
                if model_preds and actual_prices:
                    # 日付でマッチング
                    matched_pairs = []
                    for pred in model_preds:
                        actual = next((p for p in actual_prices if p.date == pred.target_date.date()), None)
                        if actual:
                            matched_pairs.append((float(pred.predicted_price), float(actual.close_price)))
                    
                    if matched_pairs:
                        pred_values = [p[0] for p in matched_pairs]
                        actual_values = [p[1] for p in matched_pairs]
                        
                        mae = mean_absolute_error(actual_values, pred_values)
                        mape = np.mean(np.abs((np.array(actual_values) - np.array(pred_values)) / np.array(actual_values))) * 100
                        
                        model_performance[model_name] = {
                            'mae': mae,
                            'mape': mape,
                            'predictions_count': len(matched_pairs),
                            'avg_confidence': np.mean([p.confidence_score for p in model_preds if p.confidence_score])
                        }
            
            return {
                'symbol': symbol,
                'evaluation_period': f"{days_back} days",
                'model_performance': model_performance,
                'evaluated_at': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"モデル評価エラー {symbol}: {e}")
            return {}