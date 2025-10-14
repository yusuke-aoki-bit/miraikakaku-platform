#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ニュースセンチメント分析モジュール
Alpha Vantage News & Sentiments APIを使用して株価予測に統合

機能:
1. ニュース記事の取得（Alpha Vantage API）
2. センチメント分析（API提供のスコア）
3. データベースへの保存
4. 銘柄別センチメント集計
"""

import os
import sys
import io
import requests
import time
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Tuple
import psycopg2
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv

# Windows encoding fix
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

load_dotenv()

# 設定
ALPHA_VANTAGE_API_KEY = os.getenv('ALPHA_VANTAGE_API_KEY', 'demo')
ALPHA_VANTAGE_BASE_URL = 'https://www.alphavantage.co/query'

DB_CONFIG = {
    'host': os.getenv('POSTGRES_HOST', 'localhost'),
    'port': int(os.getenv('POSTGRES_PORT', 5433)),
    'database': os.getenv('POSTGRES_DB', 'miraikakaku'),
    'user': os.getenv('POSTGRES_USER', 'postgres'),
    'password': os.getenv('POSTGRES_PASSWORD', 'Miraikakaku2024!')
}

class NewssentimentAnalyzer:
    """ニュースセンチメント分析クラス"""

    def __init__(self, api_key: str = ALPHA_VANTAGE_API_KEY):
        self.api_key = api_key
        self.base_url = ALPHA_VANTAGE_BASE_URL
        self.session = requests.Session()

    def fetch_news(self, symbol: str, time_from: Optional[str] = None,
                   limit: int = 50) -> List[Dict]:
        """
        Alpha Vantage News APIからニュースを取得

        Args:
            symbol: 株式シンボル (例: "AAPL", "9984.T")
            time_from: 取得開始日時 (YYYYMMDDTHHMM形式)
            limit: 取得件数

        Returns:
            ニュース記事のリスト
        """
        if not time_from:
            # デフォルトは7日前から
            time_from = (datetime.now() - timedelta(days=7)).strftime("%Y%m%dT0000")

        params = {
            'function': 'NEWS_SENTIMENT',
            'tickers': symbol,
            'time_from': time_from,
            'limit': limit,
            'apikey': self.api_key
        }

        try:
            response = self.session.get(self.base_url, params=params, timeout=30)
            response.raise_for_status()
            data = response.json()

            if 'feed' in data:
                return data['feed']
            elif 'Note' in data:
                print(f"API制限: {data['Note']}")
                return []
            else:
                print(f"予期しないレスポンス: {data}")
                return []

        except requests.exceptions.RequestException as e:
            print(f"APIリクエストエラー ({symbol}): {e}")
            return []
        except Exception as e:
            print(f"ニュース取得エラー ({symbol}): {e}")
            return []

    def parse_news_article(self, article: Dict, symbol: str) -> Optional[Dict]:
        """
        ニュース記事をパースして標準形式に変換

        Args:
            article: Alpha Vantage APIからの記事データ
            symbol: 対象銘柄シンボル

        Returns:
            パース済みニュースデータ
        """
        try:
            # 銘柄固有のセンチメントを抽出
            ticker_sentiment = None
            if 'ticker_sentiment' in article:
                for ts in article['ticker_sentiment']:
                    if ts.get('ticker') == symbol:
                        ticker_sentiment = ts
                        break

            # 記事全体のセンチメントをフォールバック
            if not ticker_sentiment and 'overall_sentiment_score' in article:
                ticker_sentiment = {
                    'ticker_sentiment_score': str(article['overall_sentiment_score']),
                    'ticker_sentiment_label': article.get('overall_sentiment_label', 'Neutral'),
                    'relevance_score': '0.5'  # デフォルト
                }

            if not ticker_sentiment:
                return None

            # センチメントスコアの変換
            sentiment_score = float(ticker_sentiment.get('ticker_sentiment_score', 0))
            sentiment_label = ticker_sentiment.get('ticker_sentiment_label', 'Neutral').lower()
            relevance_score = float(ticker_sentiment.get('relevance_score', 0))

            # 日時のパース
            published_at = datetime.strptime(
                article['time_published'],
                '%Y%m%dT%H%M%S'
            )

            # トピックの抽出
            topics = []
            if 'topics' in article:
                topics = [t['topic'] for t in article['topics']]

            return {
                'symbol': symbol,
                'title': article.get('title', ''),
                'url': article.get('url', ''),
                'source': article.get('source', 'Unknown'),
                'published_at': published_at,
                'summary': article.get('summary', ''),
                'sentiment_score': sentiment_score,
                'sentiment_label': sentiment_label,
                'relevance_score': relevance_score,
                'topics': topics
            }

        except Exception as e:
            print(f"記事パースエラー: {e}")
            return None

    def save_news_to_db(self, news_data: List[Dict], conn) -> int:
        """
        ニュースデータをデータベースに保存

        Args:
            news_data: ニュースデータのリスト
            conn: データベース接続

        Returns:
            保存件数
        """
        if not news_data:
            return 0

        cur = conn.cursor()
        saved_count = 0

        for news in news_data:
            try:
                cur.execute("""
                    INSERT INTO stock_news (
                        symbol, title, url, source, published_at,
                        summary, sentiment_score, sentiment_label,
                        relevance_score, topics
                    ) VALUES (
                        %(symbol)s, %(title)s, %(url)s, %(source)s, %(published_at)s,
                        %(summary)s, %(sentiment_score)s, %(sentiment_label)s,
                        %(relevance_score)s, %(topics)s
                    )
                    ON CONFLICT (symbol, url) DO UPDATE SET
                        sentiment_score = EXCLUDED.sentiment_score,
                        sentiment_label = EXCLUDED.sentiment_label,
                        relevance_score = EXCLUDED.relevance_score,
                        updated_at = NOW()
                """, news)
                saved_count += 1
            except psycopg2.IntegrityError:
                # 重複は無視
                conn.rollback()
                continue
            except Exception as e:
                print(f"保存エラー: {e}")
                conn.rollback()
                continue

        conn.commit()
        cur.close()
        return saved_count

    def calculate_sentiment_summary(self, symbol: str, conn) -> Optional[Dict]:
        """
        銘柄のセンチメントサマリーを計算

        Args:
            symbol: 銘柄シンボル
            conn: データベース接続

        Returns:
            センチメントサマリー
        """
        cur = conn.cursor(cursor_factory=RealDictCursor)

        try:
            cur.execute("""
                SELECT
                    COUNT(*) as news_count,
                    AVG(sentiment_score) as avg_sentiment,
                    COUNT(*) FILTER (WHERE sentiment_label = 'positive') as positive_count,
                    COUNT(*) FILTER (WHERE sentiment_label = 'negative') as negative_count,
                    COUNT(*) FILTER (WHERE sentiment_label = 'neutral') as neutral_count,
                    CASE
                        WHEN AVG(sentiment_score) > 0.3 THEN 'bullish'
                        WHEN AVG(sentiment_score) < -0.3 THEN 'bearish'
                        ELSE 'neutral'
                    END as sentiment_trend,
                    ABS(AVG(sentiment_score)) as sentiment_strength
                FROM stock_news
                WHERE symbol = %s
                  AND published_at >= CURRENT_DATE - INTERVAL '7 days'
            """, (symbol,))

            result = cur.fetchone()
            cur.close()

            if result and result['news_count'] > 0:
                return dict(result)
            return None

        except Exception as e:
            print(f"センチメント集計エラー ({symbol}): {e}")
            cur.close()
            return None

    def process_symbol(self, symbol: str, conn) -> Dict:
        """
        1銘柄のニュース分析を実行

        Args:
            symbol: 銘柄シンボル
            conn: データベース接続

        Returns:
            処理結果
        """
        result = {
            'symbol': symbol,
            'news_fetched': 0,
            'news_saved': 0,
            'sentiment_summary': None,
            'error': None
        }

        try:
            # ニュース取得
            articles = self.fetch_news(symbol)
            result['news_fetched'] = len(articles)

            if not articles:
                return result

            # パースと保存
            parsed_news = []
            for article in articles:
                parsed = self.parse_news_article(article, symbol)
                if parsed:
                    parsed_news.append(parsed)

            result['news_saved'] = self.save_news_to_db(parsed_news, conn)

            # センチメント集計
            if result['news_saved'] > 0:
                result['sentiment_summary'] = self.calculate_sentiment_summary(symbol, conn)

            # API制限を考慮して少し待機
            time.sleep(12)  # Alpha Vantageの無料版は5リクエスト/分

        except Exception as e:
            result['error'] = str(e)
            print(f"処理エラー ({symbol}): {e}")

        return result


def main():
    """メイン処理"""
    print("=" * 80)
    print("ニュースセンチメント分析システム")
    print("=" * 80)
    print()

    # データベース接続
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        analyzer = NewsSentimentAnalyzer()

        # アクティブ銘柄を取得
        cur = conn.cursor(cursor_factory=RealDictCursor)
        cur.execute("""
            SELECT symbol, company_name
            FROM stock_master
            WHERE is_active = TRUE
            ORDER BY symbol
            LIMIT 10  -- テスト用に10銘柄のみ
        """)
        symbols = cur.fetchall()
        cur.close()

        print(f"対象銘柄数: {len(symbols)}")
        print()

        # 統計
        total_fetched = 0
        total_saved = 0
        total_with_sentiment = 0

        # 各銘柄を処理
        for i, symbol_info in enumerate(symbols, 1):
            symbol = symbol_info['symbol']
            company_name = symbol_info['company_name']

            print(f"[{i}/{len(symbols)}] {symbol} - {company_name}")

            result = analyzer.process_symbol(symbol, conn)

            total_fetched += result['news_fetched']
            total_saved += result['news_saved']

            if result['sentiment_summary']:
                total_with_sentiment += 1
                summary = result['sentiment_summary']
                print(f"  ニュース: {result['news_saved']}件保存")
                print(f"  センチメント: {summary['sentiment_trend']} "
                      f"(スコア: {summary['avg_sentiment']:.3f}, "
                      f"強度: {summary['sentiment_strength']:.3f})")
                print(f"  内訳: Pos:{summary['positive_count']} "
                      f"Neg:{summary['negative_count']} "
                      f"Neu:{summary['neutral_count']}")
            else:
                print(f"  ニュースなし")

            if result['error']:
                print(f"  エラー: {result['error']}")

            print()

        # サマリー
        print("=" * 80)
        print("処理完了")
        print("=" * 80)
        print(f"対象銘柄: {len(symbols)}")
        print(f"ニュース取得: {total_fetched}件")
        print(f"ニュース保存: {total_saved}件")
        print(f"センチメント計算: {total_with_sentiment}銘柄")
        print()

        conn.close()

    except Exception as e:
        print(f"エラー: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
