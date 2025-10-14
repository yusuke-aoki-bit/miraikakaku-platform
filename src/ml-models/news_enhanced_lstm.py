#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ニュースセンチメントを統合したLSTM予測モデル
"""
import numpy as np
import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers
from typing import Dict, Tuple, List
from datetime import datetime, timedelta
import psycopg2
from psycopg2.extras import RealDictCursor
from news_feature_extractor import NewsFeatureExtractor


class NewsEnhancedLSTM:
    """ニュースセンチメントを統合したLSTM株価予測モデル"""

    def __init__(
        self,
        db_config: Dict,
        price_sequence_length: int = 30,
        news_feature_dim: int = 9
    ):
        """
        Args:
            db_config: データベース設定
            price_sequence_length: 価格データの系列長
            news_feature_dim: ニュース特徴量の次元数
        """
        self.db_config = db_config
        self.price_sequence_length = price_sequence_length
        self.news_feature_dim = news_feature_dim
        self.model = None
        self.news_extractor = NewsFeatureExtractor(db_config)

    def build_model(self) -> keras.Model:
        """
        ニュース統合LSTMモデルを構築

        アーキテクチャ:
        1. 価格系列入力 → LSTM → Dense
        2. ニュース特徴入力 → Dense
        3. 1と2を結合 → Dense → 出力
        """
        # 価格系列入力
        price_input = keras.Input(
            shape=(self.price_sequence_length, 1),
            name='price_sequence'
        )

        # ニュース特徴入力
        news_input = keras.Input(
            shape=(self.news_feature_dim,),
            name='news_features'
        )

        # 価格系列処理
        x1 = layers.LSTM(64, return_sequences=True)(price_input)
        x1 = layers.Dropout(0.2)(x1)
        x1 = layers.LSTM(32)(x1)
        x1 = layers.Dense(16, activation='relu')(x1)

        # ニュース特徴処理
        x2 = layers.Dense(32, activation='relu')(news_input)
        x2 = layers.Dropout(0.2)(x2)
        x2 = layers.Dense(16, activation='relu')(x2)

        # 結合
        combined = layers.concatenate([x1, x2])
        combined = layers.Dense(32, activation='relu')(combined)
        combined = layers.Dropout(0.2)(combined)
        output = layers.Dense(1, name='price_prediction')(combined)

        # モデル構築
        model = keras.Model(
            inputs=[price_input, news_input],
            outputs=output,
            name='news_enhanced_lstm'
        )

        model.compile(
            optimizer=keras.optimizers.Adam(learning_rate=0.001),
            loss='mse',
            metrics=['mae']
        )

        self.model = model
        return model

    def prepare_training_data(
        self,
        symbol: str,
        start_date: datetime,
        end_date: datetime
    ) -> Tuple[Dict[str, np.ndarray], np.ndarray]:
        """
        学習データを準備

        Args:
            symbol: 銘柄コード
            start_date: 開始日
            end_date: 終了日

        Returns:
            tuple: (入力データ辞書, 目標値配列)
                入力: {'price_sequence': array, 'news_features': array}
                目標: 翌日の終値配列
        """
        conn = psycopg2.connect(**self.db_config)
        cur = conn.cursor(cursor_factory=RealDictCursor)

        # 価格データ取得
        cur.execute("""
            SELECT date, close_price
            FROM stock_prices
            WHERE symbol = %s
              AND date >= %s
              AND date <= %s
            ORDER BY date ASC
        """, (symbol, start_date - timedelta(days=self.price_sequence_length + 10), end_date))

        prices = cur.fetchall()
        cur.close()
        conn.close()

        if len(prices) < self.price_sequence_length + 1:
            raise ValueError(f"Not enough data for {symbol}")

        price_sequences = []
        news_features = []
        targets = []

        # 正規化用の統計
        price_values = [float(p['close_price']) for p in prices]
        price_mean = np.mean(price_values)
        price_std = np.std(price_values)

        for i in range(self.price_sequence_length, len(prices) - 1):
            # 価格系列（正規化）
            seq = price_values[i - self.price_sequence_length:i]
            normalized_seq = [(p - price_mean) / price_std for p in seq]
            price_sequences.append(normalized_seq)

            # ニュース特徴
            current_date = prices[i]['date']
            news_feat = self.news_extractor.extract_sentiment_features(
                symbol,
                datetime.combine(current_date, datetime.min.time()),
                lookback_days=7
            )

            news_vector = [
                news_feat['avg_sentiment'],
                news_feat['sentiment_std'],
                news_feat['bullish_ratio'],
                news_feat['bearish_ratio'],
                news_feat['neutral_ratio'],
                news_feat['news_count'] / 10.0,  # 正規化
                news_feat['sentiment_trend'],
                news_feat['max_sentiment'],
                news_feat['min_sentiment']
            ]
            news_features.append(news_vector)

            # 目標値（正規化）
            target_price = price_values[i + 1]
            normalized_target = (target_price - price_mean) / price_std
            targets.append(normalized_target)

        X_price = np.array(price_sequences).reshape(-1, self.price_sequence_length, 1)
        X_news = np.array(news_features)
        y = np.array(targets)

        return {'price_sequence': X_price, 'news_features': X_news}, y

    def train(
        self,
        symbol: str,
        start_date: datetime,
        end_date: datetime,
        epochs: int = 50,
        batch_size: int = 32,
        validation_split: float = 0.2
    ) -> Dict:
        """
        モデルを学習

        Args:
            symbol: 銘柄コード
            start_date: 学習開始日
            end_date: 学習終了日
            epochs: エポック数
            batch_size: バッチサイズ
            validation_split: 検証データの割合

        Returns:
            dict: 学習履歴
        """
        if self.model is None:
            self.build_model()

        X, y = self.prepare_training_data(symbol, start_date, end_date)

        history = self.model.fit(
            X, y,
            epochs=epochs,
            batch_size=batch_size,
            validation_split=validation_split,
            verbose=1
        )

        return history.history

    def predict(
        self,
        symbol: str,
        prediction_date: datetime = None
    ) -> Dict[str, float]:
        """
        予測を実行

        Args:
            symbol: 銘柄コード
            prediction_date: 予測基準日（Noneの場合は最新日）

        Returns:
            dict: 予測結果
                - predicted_price: 予測価格
                - confidence: 信頼度
                - current_price: 現在価格
                - news_sentiment: ニュースセンチメント
        """
        if self.model is None:
            raise ValueError("Model not trained yet")

        if prediction_date is None:
            prediction_date = datetime.now()

        conn = psycopg2.connect(**self.db_config)
        cur = conn.cursor(cursor_factory=RealDictCursor)

        # 最近の価格データ取得
        cur.execute("""
            SELECT date, close_price
            FROM stock_prices
            WHERE symbol = %s
              AND date <= %s
            ORDER BY date DESC
            LIMIT %s
        """, (symbol, prediction_date.date(), self.price_sequence_length))

        prices = list(reversed(cur.fetchall()))
        cur.close()
        conn.close()

        if len(prices) < self.price_sequence_length:
            raise ValueError(f"Not enough price data for {symbol}")

        # 価格系列準備
        price_values = [float(p['close_price']) for p in prices]
        price_mean = np.mean(price_values)
        price_std = np.std(price_values)

        normalized_seq = [(p - price_mean) / price_std for p in price_values]
        X_price = np.array(normalized_seq).reshape(1, self.price_sequence_length, 1)

        # ニュース特徴準備
        news_feat = self.news_extractor.get_latest_features(symbol)
        X_news = np.array([[
            news_feat['avg_sentiment'],
            news_feat['sentiment_std'],
            news_feat['bullish_ratio'],
            news_feat['bearish_ratio'],
            news_feat['neutral_ratio'],
            news_feat['news_count'] / 10.0,
            news_feat['sentiment_trend'],
            news_feat['max_sentiment'],
            news_feat['min_sentiment']
        ]])

        # 予測
        normalized_pred = self.model.predict(
            {'price_sequence': X_price, 'news_features': X_news},
            verbose=0
        )[0][0]

        # 逆正規化
        predicted_price = normalized_pred * price_std + price_mean
        current_price = price_values[-1]

        # 信頼度計算（ニュース件数とセンチメント標準偏差から）
        news_confidence = min(news_feat['news_count'] / 10.0, 1.0)
        sentiment_confidence = max(0.5, 1.0 - news_feat['sentiment_std'])
        confidence = 0.6 + 0.2 * news_confidence + 0.2 * sentiment_confidence

        return {
            'predicted_price': float(predicted_price),
            'confidence': float(confidence),
            'current_price': float(current_price),
            'news_sentiment': float(news_feat['avg_sentiment']),
            'news_count': int(news_feat['news_count']),
            'sentiment_trend': float(news_feat['sentiment_trend'])
        }

    def save_model(self, filepath: str):
        """モデルを保存"""
        if self.model is not None:
            self.model.save(filepath)

    def load_model(self, filepath: str):
        """モデルを読み込み"""
        self.model = keras.models.load_model(filepath)
