#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
yfinanceベースの日本株ニュース収集モジュール
"""
import yfinance as yf
import time
from datetime import datetime
from psycopg2.extras import RealDictCursor
from textblob import TextBlob


def collect_jp_news_yfinance(conn, symbol):
    """
    yfinanceから日本株のニュースを収集

    Args:
        conn: Database connection
        symbol: Stock symbol (e.g., '7203.T')

    Returns:
        dict: Collection results
    """
    cur = conn.cursor(cursor_factory=RealDictCursor)

    try:
        # 銘柄情報取得
        cur.execute("SELECT symbol, company_name FROM stock_master WHERE symbol = %s", (symbol,))
        stock = cur.fetchone()

        if not stock:
            return {"status": "error", "symbol": symbol, "message": f"Symbol {symbol} not found in database"}

        # yfinanceでニュース取得
        ticker = yf.Ticker(symbol)

        # yfinanceのnewsプロパティを安全に取得
        try:
            news_items = ticker.news
        except Exception as news_error:
            return {
                "status": "error",
                "symbol": symbol,
                "message": f"Failed to fetch news: {str(news_error)}"
            }

        if not news_items or len(news_items) == 0:
            return {
                "status": "success",
                "symbol": symbol,
                "company_name": stock['company_name'],
                "news_collected": 0,
                "message": "No news available"
            }

        # ニュース記事を保存
        news_saved = 0
        news_errors = []

        for article in news_items:
            try:
                # yfinance の新しい構造に対応: content ネストあり
                if 'content' in article:
                    content = article['content']
                    title = content.get('title', '')
                    publisher = content.get('provider', {}).get('displayName', 'Unknown')
                    # pubDate を使用 (ISO 8601形式)
                    pub_date_str = content.get('pubDate', '')
                    if pub_date_str:
                        from datetime import datetime
                        published_at = datetime.fromisoformat(pub_date_str.replace('Z', '+00:00'))
                    else:
                        published_at = datetime.now()

                    # URLを取得
                    link = content.get('canonicalUrl', {}).get('url', '')
                else:
                    # 古い構造に対応（フォールバック）
                    title = article.get('title', '')
                    link = article.get('link', '')
                    publisher = article.get('publisher', 'Unknown')
                    publish_time = article.get('providerPublishTime', 0)

                    # UNIXタイムスタンプを日時に変換
                    if publish_time:
                        published_at = datetime.fromtimestamp(publish_time)
                    else:
                        published_at = datetime.now()

                # センチメント分析（英語タイトルの場合）
                sentiment_score = 0.0
                sentiment_label = 'neutral'

                if title:
                    try:
                        blob = TextBlob(title)
                        polarity = blob.sentiment.polarity  # -1.0 to +1.0
                        sentiment_score = polarity

                        if polarity > 0.1:
                            sentiment_label = 'bullish'
                        elif polarity < -0.1:
                            sentiment_label = 'bearish'
                    except:
                        pass

                # データベースに保存
                cur.execute("""
                    INSERT INTO stock_news (
                        symbol, title, url, source, published_at,
                        summary, sentiment_score, sentiment_label, relevance_score
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                    ON CONFLICT (symbol, url) DO NOTHING
                """, (
                    symbol,
                    title[:500],  # 最大500文字
                    link,
                    publisher,
                    published_at,
                    '',  # yfinanceにsummaryがない場合は空
                    sentiment_score,
                    sentiment_label,
                    0.9  # デフォルトの関連性スコア
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
            "total_available": len(news_items),
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


def collect_jp_news_batch(conn, symbols, delay=1.0):
    """
    複数の日本株のニュースを一括収集

    Args:
        conn: Database connection
        symbols: List of symbol dicts [{'symbol': '7203.T', 'company_name': '...'}]
        delay: Delay between API calls in seconds (default: 1.0s)

    Returns:
        list: Collection results for each symbol
    """
    results = []

    for i, symbol_info in enumerate(symbols):
        symbol = symbol_info['symbol'] if isinstance(symbol_info, dict) else symbol_info

        print(f"[{i+1}/{len(symbols)}] Collecting news for {symbol}...")

        result = collect_jp_news_yfinance(conn, symbol)
        results.append(result)

        # レート制限対策: 遅延
        if i < len(symbols) - 1:
            time.sleep(delay)

    return results
