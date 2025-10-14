"""
Custom LSTM Model Training System
Phase 12: Machine Learning Integration
"""

import numpy as np
import pandas as pd
import tensorflow as tf
from tensorflow import keras
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense, Dropout, BatchNormalization
from tensorflow.keras.optimizers import Adam
from tensorflow.keras.callbacks import EarlyStopping, ModelCheckpoint, ReduceLROnPlateau
from sklearn.preprocessing import MinMaxScaler
from sklearn.model_selection import TimeSeriesSplit
import psycopg2
from psycopg2.extras import RealDictCursor
import os
from datetime import datetime, timedelta
import json
import pickle

# Database configuration
DB_CONFIG = {
    'host': os.getenv('POSTGRES_HOST', 'localhost'),
    'port': int(os.getenv('POSTGRES_PORT', 5432)),
    'dbname': os.getenv('POSTGRES_DB', 'miraikakaku'),
    'user': os.getenv('POSTGRES_USER', 'postgres'),
    'password': os.getenv('POSTGRES_PASSWORD', 'Miraikakaku2024!')
}


class CustomLSTMTrainer:
    """
    カスタムLSTMモデルトレーニングシステム

    Features:
    - 複数の技術指標を使用した特徴量エンジニアリング
    - ハイパーパラメータ最適化
    - クロスバリデーション
    - モデルのバージョン管理
    """

    def __init__(
        self,
        symbol: str,
        lookback_days: int = 60,
        prediction_days: int = 7
    ):
        self.symbol = symbol
        self.lookback_days = lookback_days
        self.prediction_days = prediction_days
        self.scaler = MinMaxScaler(feature_range=(0, 1))
        self.model = None
        self.history = None

    def fetch_training_data(self, start_date: str = None, end_date: str = None):
        """
        トレーニングデータを取得

        Args:
            start_date: 開始日（デフォルト: 3年前）
            end_date: 終了日（デフォルト: 今日）

        Returns:
            DataFrame with price history and technical indicators
        """
        conn = psycopg2.connect(**DB_CONFIG)
        cur = conn.cursor(cursor_factory=RealDictCursor)

        if not start_date:
            start_date = (datetime.now() - timedelta(days=3*365)).strftime('%Y-%m-%d')
        if not end_date:
            end_date = datetime.now().strftime('%Y-%m-%d')

        query = """
            SELECT
                date,
                open_price,
                high_price,
                low_price,
                close_price,
                volume
            FROM stock_prices
            WHERE symbol = %s
              AND date BETWEEN %s AND %s
            ORDER BY date ASC
        """

        cur.execute(query, (self.symbol, start_date, end_date))
        data = cur.fetchall()
        cur.close()
        conn.close()

        df = pd.DataFrame(data)

        if len(df) < self.lookback_days:
            raise ValueError(f"Insufficient data: {len(df)} days (need at least {self.lookback_days})")

        return df

    def calculate_technical_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        技術指標を計算

        Indicators:
        - SMA (Simple Moving Average): 5, 10, 20, 50
        - EMA (Exponential Moving Average): 12, 26
        - RSI (Relative Strength Index)
        - MACD (Moving Average Convergence Divergence)
        - Bollinger Bands
        - Volume indicators
        """
        # 移動平均
        df['SMA_5'] = df['close_price'].rolling(window=5).mean()
        df['SMA_10'] = df['close_price'].rolling(window=10).mean()
        df['SMA_20'] = df['close_price'].rolling(window=20).mean()
        df['SMA_50'] = df['close_price'].rolling(window=50).mean()

        # 指数移動平均
        df['EMA_12'] = df['close_price'].ewm(span=12, adjust=False).mean()
        df['EMA_26'] = df['close_price'].ewm(span=26, adjust=False).mean()

        # MACD
        df['MACD'] = df['EMA_12'] - df['EMA_26']
        df['MACD_signal'] = df['MACD'].ewm(span=9, adjust=False).mean()
        df['MACD_hist'] = df['MACD'] - df['MACD_signal']

        # RSI
        delta = df['close_price'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss
        df['RSI'] = 100 - (100 / (1 + rs))

        # Bollinger Bands
        df['BB_middle'] = df['close_price'].rolling(window=20).mean()
        bb_std = df['close_price'].rolling(window=20).std()
        df['BB_upper'] = df['BB_middle'] + (bb_std * 2)
        df['BB_lower'] = df['BB_middle'] - (bb_std * 2)

        # ボラティリティ
        df['volatility'] = df['close_price'].rolling(window=20).std()

        # 出来高指標
        df['volume_SMA_20'] = df['volume'].rolling(window=20).mean()
        df['volume_ratio'] = df['volume'] / df['volume_SMA_20']

        # 価格変動率
        df['returns'] = df['close_price'].pct_change()
        df['returns_5'] = df['close_price'].pct_change(periods=5)

        # NaNを削除
        df = df.dropna()

        return df

    def prepare_sequences(self, df: pd.DataFrame):
        """
        LSTM用のシーケンスデータを準備

        Returns:
            X: (samples, timesteps, features)
            y: (samples, prediction_days)
        """
        # 特徴量を選択
        feature_columns = [
            'open_price', 'high_price', 'low_price', 'close_price', 'volume',
            'SMA_5', 'SMA_10', 'SMA_20', 'SMA_50',
            'EMA_12', 'EMA_26', 'MACD', 'MACD_signal', 'MACD_hist',
            'RSI', 'BB_middle', 'BB_upper', 'BB_lower',
            'volatility', 'volume_ratio', 'returns', 'returns_5'
        ]

        data = df[feature_columns].values

        # 正規化
        data_scaled = self.scaler.fit_transform(data)

        X, y = [], []

        for i in range(self.lookback_days, len(data_scaled) - self.prediction_days):
            X.append(data_scaled[i - self.lookback_days:i])

            # 予測ターゲット: 終値の将来値
            future_prices = df['close_price'].iloc[i:i + self.prediction_days].values
            y.append(future_prices)

        return np.array(X), np.array(y)

    def build_model(self, input_shape, output_shape):
        """
        LSTMモデルを構築

        Architecture:
        - LSTM layers with dropout
        - Batch normalization
        - Dense output layer
        """
        model = Sequential([
            LSTM(128, return_sequences=True, input_shape=input_shape),
            Dropout(0.2),
            BatchNormalization(),

            LSTM(64, return_sequences=True),
            Dropout(0.2),
            BatchNormalization(),

            LSTM(32, return_sequences=False),
            Dropout(0.2),
            BatchNormalization(),

            Dense(32, activation='relu'),
            Dropout(0.2),

            Dense(output_shape)
        ])

        model.compile(
            optimizer=Adam(learning_rate=0.001),
            loss='mse',
            metrics=['mae', 'mape']
        )

        return model

    def train(
        self,
        epochs: int = 100,
        batch_size: int = 32,
        validation_split: float = 0.2
    ):
        """
        モデルをトレーニング

        Args:
            epochs: エポック数
            batch_size: バッチサイズ
            validation_split: 検証データの割合

        Returns:
            Training history
        """
        print(f"🚀 Training LSTM model for {self.symbol}...")

        # データ取得
        print("📊 Fetching training data...")
        df = self.fetch_training_data()

        # 技術指標計算
        print("📈 Calculating technical indicators...")
        df = self.calculate_technical_indicators(df)

        # シーケンスデータ準備
        print("🔄 Preparing sequences...")
        X, y = self.prepare_sequences(df)

        print(f"✅ Data prepared: X shape = {X.shape}, y shape = {y.shape}")

        # モデル構築
        print("🏗️  Building model...")
        self.model = self.build_model(
            input_shape=(X.shape[1], X.shape[2]),
            output_shape=y.shape[1]
        )

        print(self.model.summary())

        # コールバック
        callbacks = [
            EarlyStopping(
                monitor='val_loss',
                patience=15,
                restore_best_weights=True,
                verbose=1
            ),
            ReduceLROnPlateau(
                monitor='val_loss',
                factor=0.5,
                patience=5,
                min_lr=0.00001,
                verbose=1
            ),
            ModelCheckpoint(
                filepath=f'models/{self.symbol}_best_model.h5',
                monitor='val_loss',
                save_best_only=True,
                verbose=1
            )
        ]

        # トレーニング
        print("🎯 Training...")
        self.history = self.model.fit(
            X, y,
            epochs=epochs,
            batch_size=batch_size,
            validation_split=validation_split,
            callbacks=callbacks,
            verbose=1
        )

        print("✅ Training complete!")

        return self.history

    def evaluate(self, X_test, y_test):
        """
        モデルを評価
        """
        if self.model is None:
            raise ValueError("Model not trained yet")

        loss, mae, mape = self.model.evaluate(X_test, y_test, verbose=0)

        print(f"📊 Evaluation Results:")
        print(f"  Loss (MSE): {loss:.4f}")
        print(f"  MAE: {mae:.4f}")
        print(f"  MAPE: {mape:.2f}%")

        return {
            'loss': float(loss),
            'mae': float(mae),
            'mape': float(mape)
        }

    def predict(self, recent_data: pd.DataFrame):
        """
        予測を実行

        Args:
            recent_data: 最近のlookback_days分のデータ

        Returns:
            Predicted prices for next prediction_days
        """
        if self.model is None:
            raise ValueError("Model not trained yet")

        # 技術指標計算
        df = self.calculate_technical_indicators(recent_data)

        # 特徴量を選択
        feature_columns = [
            'open_price', 'high_price', 'low_price', 'close_price', 'volume',
            'SMA_5', 'SMA_10', 'SMA_20', 'SMA_50',
            'EMA_12', 'EMA_26', 'MACD', 'MACD_signal', 'MACD_hist',
            'RSI', 'BB_middle', 'BB_upper', 'BB_lower',
            'volatility', 'volume_ratio', 'returns', 'returns_5'
        ]

        data = df[feature_columns].values[-self.lookback_days:]
        data_scaled = self.scaler.transform(data)

        # 予測
        X = np.array([data_scaled])
        predictions = self.model.predict(X, verbose=0)

        return predictions[0]

    def save_model(self, filepath: str = None):
        """
        モデルを保存
        """
        if filepath is None:
            filepath = f'models/{self.symbol}_lstm_model.h5'

        os.makedirs(os.path.dirname(filepath), exist_ok=True)

        self.model.save(filepath)

        # スケーラーも保存
        scaler_path = filepath.replace('.h5', '_scaler.pkl')
        with open(scaler_path, 'wb') as f:
            pickle.dump(self.scaler, f)

        # メタデータを保存
        metadata = {
            'symbol': self.symbol,
            'lookback_days': self.lookback_days,
            'prediction_days': self.prediction_days,
            'trained_at': datetime.now().isoformat()
        }

        metadata_path = filepath.replace('.h5', '_metadata.json')
        with open(metadata_path, 'w') as f:
            json.dump(metadata, f, indent=2)

        print(f"✅ Model saved to {filepath}")

    def load_model(self, filepath: str):
        """
        モデルを読み込み
        """
        self.model = keras.models.load_model(filepath)

        # スケーラーを読み込み
        scaler_path = filepath.replace('.h5', '_scaler.pkl')
        with open(scaler_path, 'rb') as f:
            self.scaler = pickle.load(f)

        # メタデータを読み込み
        metadata_path = filepath.replace('.h5', '_metadata.json')
        with open(metadata_path, 'r') as f:
            metadata = json.load(f)

        print(f"✅ Model loaded from {filepath}")
        print(f"   Trained at: {metadata['trained_at']}")

        return metadata


def train_multiple_symbols(symbols: list, epochs: int = 50):
    """
    複数銘柄のモデルを一括トレーニング
    """
    results = {}

    for symbol in symbols:
        print(f"\n{'='*60}")
        print(f"Training model for {symbol}")
        print(f"{'='*60}\n")

        try:
            trainer = CustomLSTMTrainer(symbol=symbol, lookback_days=60, prediction_days=7)
            history = trainer.train(epochs=epochs, batch_size=32, validation_split=0.2)
            trainer.save_model()

            results[symbol] = {
                'status': 'success',
                'final_loss': float(history.history['loss'][-1]),
                'final_val_loss': float(history.history['val_loss'][-1]),
                'min_val_loss': float(min(history.history['val_loss']))
            }

        except Exception as e:
            print(f"❌ Error training {symbol}: {e}")
            results[symbol] = {
                'status': 'failed',
                'error': str(e)
            }

    return results


if __name__ == "__main__":
    # テスト: 主要銘柄でトレーニング
    test_symbols = ['7203.T', '9984.T', 'AAPL', 'MSFT', 'TSLA']

    print("🚀 Starting Custom LSTM Training System")
    print(f"Training {len(test_symbols)} symbols...")

    results = train_multiple_symbols(test_symbols, epochs=50)

    print("\n" + "="*60)
    print("Training Results Summary")
    print("="*60)

    for symbol, result in results.items():
        if result['status'] == 'success':
            print(f"✅ {symbol}: Val Loss = {result['min_val_loss']:.4f}")
        else:
            print(f"❌ {symbol}: {result['error']}")
