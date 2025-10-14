"""
NewsAPI.org News Collector
日本株ニュース収集用（無料プラン: 100リクエスト/日）
"""

import os
import requests
from datetime import datetime, timedelta
from typing import List, Dict
import psycopg2
from textblob import TextBlob
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class NewsAPICollector:
    """NewsAPI.org を使用したニュース収集"""

    def __init__(self, api_key: str = None):
        """
        初期化

        Args:
            api_key: NewsAPI.org APIキー（未指定の場合は環境変数から取得）
        """
        self.api_key = api_key or os.getenv('NEWSAPI_KEY')
        if not self.api_key:
            raise ValueError("NewsAPI key is required. Set NEWSAPI_KEY environment variable.")

        self.base_url = "https://newsapi.org/v2/everything"
        self.headers = {"Authorization": f"Bearer {self.api_key}"}

        # 日本企業名の英語マッピング（NewsAPI.orgは英語記事が主）
        # シンボルベースのマッピング（文字化け対策）
        self.symbol_to_en = {
            '7203.T': 'Toyota',
            '6758.T': 'Sony',
            '9984.T': 'SoftBank',
            '7974.T': 'Nintendo',
            '7267.T': 'Honda',
            '7201.T': 'Nissan',
            '6752.T': 'Panasonic',
            '8306.T': 'MUFG',
            '8316.T': 'SMFG',
            '8411.T': 'Mizuho',
            '6861.T': 'Keyence',
            '9983.T': 'Fast Retailing',
            '8035.T': 'Tokyo Electron',
            '6367.T': 'Daikin',
            '4063.T': 'Shin-Etsu Chemical'
        }

        # 日本語名マッピング（バックアップ用）
        self.jp_to_en = {
            'トヨタ自動車': 'Toyota',
            'ソニーグループ': 'Sony',
            'ソフトバンクグループ': 'SoftBank',
            '任天堂': 'Nintendo',
            'ホンダ': 'Honda',
            '日産自動車': 'Nissan',
            'パナソニック': 'Panasonic',
            '三菱UFJフィナンシャル・グループ': 'MUFG',
            '三井住友フィナンシャルグループ': 'SMFG',
            'みずほフィナンシャルグループ': 'Mizuho',
            'キーエンス': 'Keyence',
            'ファーストリテイリング': 'Fast Retailing',
            '東京エレクトロン': 'Tokyo Electron',
            'ダイキン工業': 'Daikin',
            '信越化学工業': 'Shin-Etsu Chemical'
        }

    def get_company_news(
        self,
        company_name: str,
        symbol: str,
        days: int = 7,
        language: str = 'en'
    ) -> List[Dict]:
        """
        企業ニュースを取得

        Args:
            company_name: 企業名（日本語または英語）
            symbol: 銘柄コード
            days: 過去何日分のニュースを取得するか
            language: 言語コード（'ja' or 'en'）

        Returns:
            ニュース記事のリスト
        """
        try:
            # シンボルから英語名を取得（文字化け対策）
            # 優先順位: symbol → company_name (Japanese) → company_name (as-is)
            search_name = self.symbol_to_en.get(symbol)
            if not search_name:
                search_name = self.jp_to_en.get(company_name, company_name)

            logger.info(f"Symbol: {symbol}, Original name: {company_name}, Search name: {search_name}")

            # 日付範囲設定（無料プランは30日まで）
            to_date = datetime.now()
            from_date = to_date - timedelta(days=min(days, 30))

            # クエリパラメータ（企業名のみで検索、英語記事優先）
            params = {
                'q': search_name,  # 英語企業名で検索
                'language': 'en',  # 英語記事のみ（NewsAPI.orgの日本語カバレッジは低い）
                'sortBy': 'publishedAt',
                'from': from_date.strftime('%Y-%m-%d'),
                'to': to_date.strftime('%Y-%m-%d'),
                'pageSize': 100  # 最大100件
            }

            logger.info(f"Fetching news for {company_name} ({symbol}) from NewsAPI.org...")
            logger.info(f"Query params: {params}")

            response = requests.get(
                self.base_url,
                params=params,
                headers=self.headers,
                timeout=10
            )

            logger.info(f"API Response status: {response.status_code}")

            if response.status_code == 200:
                data = response.json()
                total_results = data.get('totalResults', 0)
                articles = data.get('articles', [])
                logger.info(f"Total results: {total_results}, Returned: {len(articles)} articles for {symbol}")
                return articles

            elif response.status_code == 426:
                logger.error("NewsAPI.org: Upgrade required (free plan limitation)")
                return []

            elif response.status_code == 429:
                logger.error("NewsAPI.org: Rate limit exceeded (100 requests/day)")
                return []

            else:
                logger.error(f"NewsAPI.org error: {response.status_code} - {response.text}")
                return []

        except Exception as e:
            logger.error(f"Error fetching news for {symbol}: {e}")
            return []

    def analyze_sentiment(self, text: str) -> float:
        """
        テキストのセンチメント分析

        Args:
            text: 分析するテキスト

        Returns:
            センチメントスコア（-1.0 ~ 1.0）
        """
        try:
            blob = TextBlob(text)
            return blob.sentiment.polarity
        except:
            return 0.0

    def process_articles(self, articles: List[Dict], symbol: str) -> List[Dict]:
        """
        記事を処理してセンチメント分析

        Args:
            articles: 記事リスト
            symbol: 銘柄コード

        Returns:
            処理済み記事リスト
        """
        processed = []

        for article in articles:
            try:
                # センチメント分析（タイトル + 説明文）
                title = article.get('title', '')
                description = article.get('description', '')
                content = f"{title}. {description}"

                sentiment_score = self.analyze_sentiment(content)

                # センチメント分類
                if sentiment_score > 0.1:
                    sentiment = 'positive'
                elif sentiment_score < -0.1:
                    sentiment = 'negative'
                else:
                    sentiment = 'neutral'

                processed_article = {
                    'symbol': symbol,
                    'title': title,
                    'description': description,
                    'url': article.get('url', ''),
                    'source': article.get('source', {}).get('name', 'NewsAPI'),
                    'published_at': article.get('publishedAt', ''),
                    'sentiment': sentiment,
                    'sentiment_score': sentiment_score
                }

                processed.append(processed_article)

            except Exception as e:
                logger.error(f"Error processing article: {e}")
                continue

        return processed

    def save_to_database(self, articles: List[Dict]) -> int:
        """
        記事をデータベースに保存

        Args:
            articles: 処理済み記事リスト

        Returns:
            保存した記事数
        """
        if not articles:
            return 0

        try:
            # Cloud SQL接続設定（api_predictions.pyと同じロジック）
            host = os.getenv('POSTGRES_HOST', 'localhost')
            config = {
                'database': os.getenv('POSTGRES_DB', 'miraikakaku'),
                'user': os.getenv('POSTGRES_USER', 'postgres'),
                'password': os.getenv('POSTGRES_PASSWORD', 'Miraikakaku2024!')
            }

            if host.startswith('/cloudsql/'):
                # Cloud SQL Unix socket
                config['host'] = host
            else:
                # TCP connection (local or external)
                config['host'] = host
                config['port'] = int(os.getenv('POSTGRES_PORT', 5433))

            conn = psycopg2.connect(**config)

            cur = conn.cursor()
            saved_count = 0

            for article in articles:
                try:
                    cur.execute("""
                        INSERT INTO stock_news (
                            symbol, title, summary, url, source,
                            published_at, sentiment_label, sentiment_score
                        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                        ON CONFLICT (symbol, url) DO UPDATE SET
                            sentiment_label = EXCLUDED.sentiment_label,
                            sentiment_score = EXCLUDED.sentiment_score,
                            updated_at = CURRENT_TIMESTAMP
                    """, (
                        article['symbol'],
                        article['title'],
                        article['description'],  # description → summary
                        article['url'],
                        article['source'],
                        article['published_at'],
                        article['sentiment'],  # sentiment → sentiment_label
                        article['sentiment_score']
                    ))
                    saved_count += 1

                except Exception as e:
                    logger.error(f"Error saving article: {e}")
                    continue

            conn.commit()
            cur.close()
            conn.close()

            logger.info(f"Saved {saved_count} articles to database")
            return saved_count

        except Exception as e:
            logger.error(f"Database error: {e}")
            return 0

    def collect_news_for_symbol(self, symbol: str, company_name: str, days: int = 7) -> Dict:
        """
        銘柄のニュースを収集・分析・保存

        Args:
            symbol: 銘柄コード
            company_name: 企業名
            days: 過去何日分

        Returns:
            実行結果
        """
        logger.info(f"Starting news collection for {symbol} - {company_name}")

        # ニュース取得
        articles = self.get_company_news(company_name, symbol, days)

        if not articles:
            return {
                'symbol': symbol,
                'company_name': company_name,
                'articles_found': 0,
                'articles_saved': 0,
                'status': 'no_articles'
            }

        # 記事処理
        processed = self.process_articles(articles, symbol)

        # データベース保存
        saved = self.save_to_database(processed)

        # センチメント統計
        sentiments = [a['sentiment_score'] for a in processed]
        avg_sentiment = sum(sentiments) / len(sentiments) if sentiments else 0

        return {
            'symbol': symbol,
            'company_name': company_name,
            'articles_found': len(articles),
            'articles_saved': saved,
            'avg_sentiment': avg_sentiment,
            'status': 'success'
        }


def main():
    """メイン関数（テスト用）"""

    # テスト用：トヨタ自動車のニュース収集
    collector = NewsAPICollector()

    # 日本株テスト
    japanese_stocks = [
        ('7203.T', 'トヨタ自動車'),
        ('9984.T', 'ソフトバンクグループ'),
        ('6758.T', 'ソニーグループ')
    ]

    results = []
    for symbol, company_name in japanese_stocks:
        result = collector.collect_news_for_symbol(symbol, company_name, days=7)
        results.append(result)
        print(f"\n{symbol} ({company_name}):")
        print(f"  Found: {result['articles_found']} articles")
        print(f"  Saved: {result['articles_saved']} articles")
        print(f"  Avg Sentiment: {result.get('avg_sentiment', 0):.4f}")

    print(f"\n=== Summary ===")
    print(f"Total symbols: {len(results)}")
    print(f"Total articles found: {sum(r['articles_found'] for r in results)}")
    print(f"Total articles saved: {sum(r['articles_saved'] for r in results)}")


if __name__ == '__main__':
    main()
