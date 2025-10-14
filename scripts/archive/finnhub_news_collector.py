#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Finnhub日本株ニュース収集モジュール
"""
import requests
import time
from datetime import datetime, timedelta
from psycopg2.extras import RealDictCursor
import os


def collect_jp_news_finnhub(conn, symbol, api_key):
    """
    Finnhub APIから日本株ニュースを収集

    Args:
        conn: Database connection
        symbol: Stock symbol (e.g., '7203.T')
        api_key: Finnhub API key

    Returns:
        dict: Collection results
    """
    cur = conn.cursor(cursor_factory=RealDictCursor)

    try:
        # 銘柄情報取得
        cur.execute("SELECT symbol, company_name FROM stock_master WHERE symbol = %s", (symbol,))
        stock = cur.fetchone()

        if not stock:
            return {"status": "error", "symbol": symbol, "message": f"Symbol {symbol} not found"}

        # 日付範囲
        from_date = (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d")
        to_date = datetime.now().strftime("%Y-%m-%d")

        # Finnhub Company News API
        news_params = {
            'symbol': symbol,
            'from': from_date,
            'to': to_date,
            'token': api_key
        }

        news_response = requests.get(
            'https://finnhub.io/api/v1/company-news',
            params=news_params,
            timeout=30
        )
        news_data = news_response.json()

        # Finnhub News Sentiment API
        sentiment_params = {
            'symbol': symbol,
            'token': api_key
        }

        sentiment_response = requests.get(
            'https://finnhub.io/api/v1/news-sentiment',
            params=sentiment_params,
            timeout=30
        )
        sentiment_data = sentiment_response.json()

        # センチメントスコア計算
        sentiment_score = 0.0
        bullish_pct = 0.0
        bearish_pct = 0.0

        if isinstance(sentiment_data, dict) and 'sentiment' in sentiment_data:
            bullish_pct = float(sentiment_data['sentiment'].get('bullishPercent', 0))
            bearish_pct = float(sentiment_data['sentiment'].get('bearishPercent', 0))
            # -1.0 to +1.0に正規化
            sentiment_score = (bullish_pct - bearish_pct)

        # ニュース記事を保存
        news_saved = 0
        news_errors = []

        if isinstance(news_data, list):
            for article in news_data:
                try:
                    # 個別記事のセンチメントスコア (全体のセンチメントを使用)
                    article_sentiment_score = sentiment_score

                    # sentiment_labelを決定
                    if sentiment_score > 0.1:
                        sentiment_label = 'bullish'
                    elif sentiment_score < -0.1:
                        sentiment_label = 'bearish'
                    else:
                        sentiment_label = 'neutral'

                    cur.execute("""
                        INSERT INTO stock_news (
                            symbol, title, url, source, published_at,
                            summary, sentiment_score, sentiment_label, relevance_score
                        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                        ON CONFLICT (symbol, url) DO NOTHING
                    """, (
                        symbol,
                        article.get('headline', '')[:500],  # タイトル上限500文字
                        article.get('url', ''),
                        article.get('source', 'Unknown'),
                        datetime.fromtimestamp(article.get('datetime', 0)),
                        article.get('summary', '')[:1000],  # サマリー上限1000文字
                        article_sentiment_score,
                        sentiment_label,
                        0.8  # デフォルトの関連性スコア
                    ))
                    news_saved += 1
                except Exception as e:
                    news_errors.append(str(e)[:100])

            conn.commit()

        return {
            "status": "success",
            "symbol": symbol,
            "company_name": stock['company_name'],
            "news_collected": news_saved,
            "feed_count": len(news_data) if isinstance(news_data, list) else 0,
            "sentiment_score": round(sentiment_score, 4),
            "bullish_percent": round(bullish_pct, 2),
            "bearish_percent": round(bearish_pct, 2),
            "articles_in_week": sentiment_data.get('buzz', {}).get('articlesInLastWeek', 0) if isinstance(sentiment_data, dict) else 0,
            "errors": news_errors[:3] if news_errors else []
        }

    except Exception as e:
        return {
            "status": "error",
            "symbol": symbol,
            "message": str(e)
        }
    finally:
        cur.close()


def collect_jp_news_batch(conn, symbols, api_key, delay=1.2):
    """
    複数の日本株のニュースを一括収集

    Args:
        conn: Database connection
        symbols: List of symbol dicts [{'symbol': '7203.T', 'company_name': '...'}]
        api_key: Finnhub API key
        delay: Delay between API calls in seconds (default: 1.2s for 60 calls/min limit)

    Returns:
        list: Collection results for each symbol
    """
    results = []

    for i, symbol_info in enumerate(symbols):
        symbol = symbol_info['symbol'] if isinstance(symbol_info, dict) else symbol_info

        print(f"[{i+1}/{len(symbols)}] Collecting news for {symbol}...")

        result = collect_jp_news_finnhub(conn, symbol, api_key)
        results.append(result)

        # APIレート制限対策: 遅延
        if i < len(symbols) - 1:
            time.sleep(delay)

    return results
