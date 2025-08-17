import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import mean_absolute_error, mean_squared_error
from sqlalchemy.orm import Session
from database.database import get_db_session
from database.models import StockPriceHistory, StockPredictions
from datetime import datetime, timedelta
import joblib
import logging
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)

class MLPipelineService:
    def __init__(self):
        self.db_session = get_db_session()
        self.model = None
        self.scaler = None
        
    def train_models(self):
        """機械学習モデルの訓練"""
        logger.info("MLパイプライン開始")
        
        try:
            # 主要銘柄のモデルを訓練
            symbols = ['AAPL', 'GOOGL', 'MSFT', 'TSLA', 'AMZN']
            
            for symbol in symbols:
                logger.info(f"モデル訓練開始: {symbol}")
                if self.train_symbol_model(symbol):
                    logger.info(f"モデル訓練完了: {symbol}")
                else:
                    logger.error(f"モデル訓練失敗: {symbol}")
                    
        except Exception as e:
            logger.error(f"MLパイプラインエラー: {e}")
        finally:
            self.db_session.close()
            
    def train_symbol_model(self, symbol: str) -> bool:
        """個別銘柄のモデル訓練"""
        try:
            # 履歴データを取得（過去6ヶ月）
            start_date = datetime.utcnow() - timedelta(days=180)
            
            price_data = self.db_session.query(StockPriceHistory).filter(
                StockPriceHistory.symbol == symbol,
                StockPriceHistory.date >= start_date
            ).order_by(StockPriceHistory.date.asc()).all()
            
            if len(price_data) < 30:
                logger.warning(f"訓練データが不足: {symbol}")
                return False
            
            # 特徴量エンジニアリング
            df = self.prepare_features(price_data)
            
            if len(df) < 20:
                logger.warning(f"特徴量データが不足: {symbol}")
                return False
            
            # モデル訓練
            X, y = self.create_features_and_targets(df)
            
            if len(X) == 0:
                logger.warning(f"訓練データなし: {symbol}")
                return False
            
            X_train, X_test, y_train, y_test = train_test_split(
                X, y, test_size=0.2, random_state=42
            )
            
            # スケーリング
            scaler = StandardScaler()
            X_train_scaled = scaler.fit_transform(X_train)
            X_test_scaled = scaler.transform(X_test)
            
            # Random Forest モデル
            model = RandomForestRegressor(
                n_estimators=100,
                max_depth=10,
                random_state=42
            )
            model.fit(X_train_scaled, y_train)
            
            # 評価
            y_pred = model.predict(X_test_scaled)
            mae = mean_absolute_error(y_test, y_pred)
            mse = mean_squared_error(y_test, y_pred)
            
            logger.info(f"モデル性能 {symbol}: MAE={mae:.4f}, MSE={mse:.4f}")
            
            # 予測生成
            self.generate_predictions(symbol, model, scaler, df.tail(10))
            
            return True
            
        except Exception as e:
            logger.error(f"モデル訓練エラー {symbol}: {e}")
            return False
            
    def prepare_features(self, price_data: List) -> pd.DataFrame:
        """価格データから特徴量を準備"""
        data = []
        for price in price_data:
            data.append({
                'date': price.date,
                'open': float(price.open_price or price.close_price),
                'high': float(price.high_price or price.close_price),
                'low': float(price.low_price or price.close_price),
                'close': float(price.close_price),
                'volume': int(price.volume or 0)
            })
            
        df = pd.DataFrame(data)
        
        # 技術指標を計算
        df['sma_5'] = df['close'].rolling(window=5).mean()
        df['sma_20'] = df['close'].rolling(window=20).mean()
        df['rsi'] = self.calculate_rsi(df['close'])
        df['volatility'] = df['close'].rolling(window=10).std()
        df['price_change'] = df['close'].pct_change()
        
        return df.dropna()
        
    def calculate_rsi(self, prices: pd.Series, period: int = 14) -> pd.Series:
        """RSI（相対強度指数）を計算"""
        delta = prices.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        rs = gain / loss
        return 100 - (100 / (1 + rs))
        
    def create_features_and_targets(self, df: pd.DataFrame):
        """特徴量とターゲットを作成"""
        features = ['sma_5', 'sma_20', 'rsi', 'volatility', 'price_change', 'volume']
        
        X = df[features].values[:-1]  # 最後の行以外
        y = df['close'].values[1:]    # 次の日の終値
        
        # NaNを除去
        mask = ~np.isnan(X).any(axis=1) & ~np.isnan(y)
        X = X[mask]
        y = y[mask]
        
        return X, y
        
    def generate_predictions(self, symbol: str, model, scaler, recent_data: pd.DataFrame):
        """予測を生成してデータベースに保存"""
        try:
            if len(recent_data) == 0:
                return
                
            features = ['sma_5', 'sma_20', 'rsi', 'volatility', 'price_change', 'volume']
            latest_features = recent_data[features].iloc[-1:].values
            
            if np.isnan(latest_features).any():
                logger.warning(f"特徴量にNaNが含まれています: {symbol}")
                return
            
            latest_features_scaled = scaler.transform(latest_features)
            predicted_price = model.predict(latest_features_scaled)[0]
            
            # 信頼度スコアを計算（簡易版）
            recent_volatility = recent_data['volatility'].iloc[-1]
            confidence = max(0.3, min(0.9, 1.0 - recent_volatility / recent_data['close'].iloc[-1]))
            
            # 予測をデータベースに保存
            prediction = StockPredictions(
                symbol=symbol,
                prediction_date=datetime.utcnow(),
                target_date=datetime.utcnow() + timedelta(days=1),
                predicted_price=predicted_price,
                confidence_score=confidence,
                prediction_type="daily",
                model_name="random_forest",
                model_version="1.0",
                features_used=str(features)
            )
            
            self.db_session.add(prediction)
            self.db_session.commit()
            
            logger.info(f"予測生成完了: {symbol}, 予測価格: ${predicted_price:.2f}")
            
        except Exception as e:
            logger.error(f"予測生成エラー {symbol}: {e}")
            self.db_session.rollback()