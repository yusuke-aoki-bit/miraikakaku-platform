#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ニュースデータからAI学習用特徴量を抽出するモジュール
"""
import psycopg2
from psycopg2.extras import RealDictCursor
from datetime import datetime, timedelta
import numpy as np
from typing import Dict, List, Tuple


class NewsFeatureExtractor:
    """ニュースデータから機械学習用の特徴量を抽出"""

    def __init__(self, db_config: Dict):
        """
        Args:
            db_config: データベース接続設定
        """
        self.db_config = db_config

    def get_db_connection(self):
        """データベース接続を取得"""
        return psycopg2.connect(**self.db_config)

    def extract_sentiment_features(
        self,
        symbol: str,
        target_date: datetime,
        lookback_days: int = 7
    ) -> Dict[str, float]:
        """
        指定銘柄・日付のセンチメント特徴量を抽出

        Args:
            symbol: 銘柄コード (例: '7203.T')
            target_date: 対象日付
            lookback_days: 過去何日分のニュースを見るか

        Returns:
            dict: センチメント特徴量
                - avg_sentiment: 平均センチメントスコア
                - sentiment_std: センチメント標準偏差
                - bullish_ratio: 強気ニュースの割合
                - bearish_ratio: 弱気ニュースの割合
                - neutral_ratio: 中立ニュースの割合
                - news_count: ニュース件数
                - sentiment_trend: センチメント傾向（最近3日 vs 過去4日）
                - max_sentiment: 最大センチメント
                - min_sentiment: 最小センチメント
        """
        conn = self.get_db_connection()
        cur = conn.cursor(cursor_factory=RealDictCursor)

        start_date = target_date - timedelta(days=lookback_days)

        # 期間内のニュースを取得
        cur.execute("""
            SELECT
                sentiment_score,
                sentiment_label,
                published_at,
                relevance_score
            FROM stock_news
            WHERE symbol = %s
              AND published_at >= %s
              AND published_at <= %s
            ORDER BY published_at DESC
        """, (symbol, start_date, target_date))

        news_items = cur.fetchall()
        cur.close()
        conn.close()

        if not news_items or len(news_items) == 0:
            # ニュースがない場合はゼロベクトル
            return {
                'avg_sentiment': 0.0,
                'sentiment_std': 0.0,
                'bullish_ratio': 0.0,
                'bearish_ratio': 0.0,
                'neutral_ratio': 0.0,
                'news_count': 0,
                'sentiment_trend': 0.0,
                'max_sentiment': 0.0,
                'min_sentiment': 0.0
            }

        # センチメントスコアを抽出
        sentiments = [float(n['sentiment_score']) for n in news_items]
        labels = [n['sentiment_label'] for n in news_items]

        # 基本統計
        avg_sentiment = np.mean(sentiments)
        sentiment_std = np.std(sentiments) if len(sentiments) > 1 else 0.0
        max_sentiment = np.max(sentiments)
        min_sentiment = np.min(sentiments)

        # ラベル分布
        total_count = len(labels)
        bullish_count = labels.count('bullish')
        bearish_count = labels.count('bearish')
        neutral_count = labels.count('neutral')

        bullish_ratio = bullish_count / total_count if total_count > 0 else 0.0
        bearish_ratio = bearish_count / total_count if total_count > 0 else 0.0
        neutral_ratio = neutral_count / total_count if total_count > 0 else 0.0

        # センチメント傾向（最近 vs 過去）
        recent_days = min(3, len(sentiments) // 2)
        if len(sentiments) >= 2:
            recent_sentiment = np.mean(sentiments[:recent_days])
            past_sentiment = np.mean(sentiments[recent_days:])
            sentiment_trend = recent_sentiment - past_sentiment
        else:
            sentiment_trend = 0.0

        return {
            'avg_sentiment': float(avg_sentiment),
            'sentiment_std': float(sentiment_std),
            'bullish_ratio': float(bullish_ratio),
            'bearish_ratio': float(bearish_ratio),
            'neutral_ratio': float(neutral_ratio),
            'news_count': int(total_count),
            'sentiment_trend': float(sentiment_trend),
            'max_sentiment': float(max_sentiment),
            'min_sentiment': float(min_sentiment)
        }

    def create_training_dataset(
        self,
        symbols: List[str],
        start_date: datetime,
        end_date: datetime,
        lookback_days: int = 7
    ) -> Tuple[np.ndarray, np.ndarray]:
        """
        複数銘柄の学習データセットを作成

        Args:
            symbols: 銘柄コードのリスト
            start_date: 開始日
            end_date: 終了日
            lookback_days: ニュース取得期間

        Returns:
            tuple: (特徴量行列, ラベルベクトル)
                特徴量: [avg_sentiment, sentiment_std, bullish_ratio, ...]
                ラベル: 翌日の価格変化率
        """
        conn = self.get_db_connection()
        cur = conn.cursor(cursor_factory=RealDictCursor)

        X = []  # 特徴量
        y = []  # ラベル（価格変化率）

        for symbol in symbols:
            # 価格データを取得
            cur.execute("""
                SELECT date, close_price
                FROM stock_prices
                WHERE symbol = %s
                  AND date >= %s
                  AND date <= %s
                ORDER BY date ASC
            """, (symbol, start_date, end_date))

            prices = cur.fetchall()

            for i in range(len(prices) - 1):
                current_date = prices[i]['date']
                current_price = float(prices[i]['close_price'])
                next_price = float(prices[i + 1]['close_price'])

                # センチメント特徴量を抽出
                features = self.extract_sentiment_features(
                    symbol,
                    datetime.combine(current_date, datetime.min.time()),
                    lookback_days
                )

                # 特徴量ベクトル
                feature_vector = [
                    features['avg_sentiment'],
                    features['sentiment_std'],
                    features['bullish_ratio'],
                    features['bearish_ratio'],
                    features['neutral_ratio'],
                    features['news_count'],
                    features['sentiment_trend'],
                    features['max_sentiment'],
                    features['min_sentiment']
                ]

                # ラベル: 翌日の価格変化率
                price_change = (next_price - current_price) / current_price

                X.append(feature_vector)
                y.append(price_change)

        cur.close()
        conn.close()

        return np.array(X), np.array(y)

    def get_latest_features(self, symbol: str) -> Dict[str, float]:
        """
        最新のセンチメント特徴量を取得（予測用）

        Args:
            symbol: 銘柄コード

        Returns:
            dict: 最新のセンチメント特徴量
        """
        return self.extract_sentiment_features(
            symbol,
            datetime.now(),
            lookback_days=7
        )


def create_feature_vector_for_symbol(symbol: str, db_config: Dict) -> np.ndarray:
    """
    単一銘柄の特徴量ベクトルを作成（予測用ヘルパー関数）

    Args:
        symbol: 銘柄コード
        db_config: データベース設定

    Returns:
        np.ndarray: 特徴量ベクトル (9次元)
    """
    extractor = NewsFeatureExtractor(db_config)
    features = extractor.get_latest_features(symbol)

    return np.array([
        features['avg_sentiment'],
        features['sentiment_std'],
        features['bullish_ratio'],
        features['bearish_ratio'],
        features['neutral_ratio'],
        features['news_count'],
        features['sentiment_trend'],
        features['max_sentiment'],
        features['min_sentiment']
    ])
