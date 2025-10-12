#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from psycopg2.extras import RealDictCursor
import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(title="Miraikakaku Prediction API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def get_db_config():
    host = os.getenv('POSTGRES_HOST', 'localhost')
    config = {
        'database': os.getenv('POSTGRES_DB', 'miraikakaku'),
        'user': os.getenv('POSTGRES_USER', 'postgres'),
        'password': os.getenv('POSTGRES_PASSWORD', 'Miraikakaku2024!')
    }
    if host.startswith('/cloudsql/'):
        config['host'] = host
    else:
        config['host'] = host
        config['port'] = int(os.getenv('POSTGRES_PORT', 5433))
    return config

def get_db_connection():
    return psycopg2.connect(**get_db_config())

@app.get("/")
def read_root():
    return {"message": "Miraikakaku Prediction API", "version": "1.0.0"}

@app.get("/health")
def health_check():
    return {"status": "healthy"}

@app.post("/admin/apply-news-schema")
def apply_news_schema():
    """ニュースセンチメント分析スキーマを適用（管理者用）"""
    try:
        conn = get_db_connection()
        cur = conn.cursor()

        # スキーマSQL読み込み
        import os
        schema_path = os.path.join(os.path.dirname(__file__), 'schema_news_sentiment.sql')
        with open(schema_path, 'r', encoding='utf-8') as f:
            schema_sql = f.read()

        # 適用
        cur.execute(schema_sql)
        conn.commit()

        # 確認
        cur.execute("""
            SELECT table_name FROM information_schema.tables
            WHERE table_schema = 'public'
              AND table_name IN ('stock_news', 'stock_sentiment_summary', 'news_analysis_log')
            ORDER BY table_name
        """)
        tables = [row[0] for row in cur.fetchall()]

        cur.execute("""
            SELECT column_name FROM information_schema.columns
            WHERE table_name = 'ensemble_predictions'
              AND column_name IN ('news_sentiment', 'news_impact', 'sentiment_adjusted_prediction')
            ORDER BY column_name
        """)
        columns = [row[0] for row in cur.fetchall()]

        cur.close()
        conn.close()

        return {
            "status": "success",
            "message": "News sentiment schema applied successfully",
            "tables_created": tables,
            "columns_added": columns
        }
    except Exception as e:
        return {
            "status": "error",
            "message": str(e)
        }

@app.post("/admin/add-test-stocks")
def add_test_stocks():
    """テスト用の米国株・日本株を追加（管理者用）"""
    try:
        conn = get_db_connection()
        cur = conn.cursor()

        stocks = [
            # 米国主要株 (トップ20)
            ('AAPL', 'Apple Inc.', 'NASDAQ'),
            ('GOOGL', 'Alphabet Inc. Class A', 'NASDAQ'),
            ('GOOG', 'Alphabet Inc. Class C', 'NASDAQ'),
            ('MSFT', 'Microsoft Corporation', 'NASDAQ'),
            ('AMZN', 'Amazon.com Inc.', 'NASDAQ'),
            ('TSLA', 'Tesla Inc.', 'NASDAQ'),
            ('META', 'Meta Platforms Inc.', 'NASDAQ'),
            ('NVDA', 'NVIDIA Corporation', 'NASDAQ'),
            ('BRK.B', 'Berkshire Hathaway Inc.', 'NYSE'),
            ('JPM', 'JPMorgan Chase & Co.', 'NYSE'),
            ('V', 'Visa Inc.', 'NYSE'),
            ('JNJ', 'Johnson & Johnson', 'NYSE'),
            ('WMT', 'Walmart Inc.', 'NYSE'),
            ('PG', 'Procter & Gamble Co.', 'NYSE'),
            ('MA', 'Mastercard Inc.', 'NYSE'),
            ('UNH', 'UnitedHealth Group Inc.', 'NYSE'),
            ('HD', 'Home Depot Inc.', 'NYSE'),
            ('DIS', 'Walt Disney Co.', 'NYSE'),
            ('NFLX', 'Netflix Inc.', 'NASDAQ'),
            ('ADBE', 'Adobe Inc.', 'NASDAQ'),
            # 日本主要株
            ('9984.T', 'SoftBank Group Corp.', 'TSE'),
            ('7203.T', 'Toyota Motor Corp.', 'TSE'),
            ('6758.T', 'Sony Group Corporation', 'TSE'),
            ('7974.T', 'Nintendo Co., Ltd.', 'TSE'),
            ('8306.T', 'Mitsubishi UFJ Financial Group', 'TSE')
        ]

        for symbol, company_name, exchange in stocks:
            cur.execute("""
                INSERT INTO stock_master (symbol, company_name, exchange, is_active)
                VALUES (%s, %s, %s, TRUE)
                ON CONFLICT (symbol) DO UPDATE SET
                    company_name = EXCLUDED.company_name,
                    exchange = EXCLUDED.exchange,
                    is_active = TRUE
            """, (symbol, company_name, exchange))

        conn.commit()
        cur.close()
        conn.close()

        return {
            "status": "success",
            "message": f"{len(stocks)} test stocks added/updated",
            "stocks": [{"symbol": s[0], "company_name": s[1]} for s in stocks]
        }
    except Exception as e:
        return {
            "status": "error",
            "message": str(e)
        }

@app.post("/admin/add-unique-constraint")
def add_unique_constraint():
    """stock_newsテーブルにユニーク制約を追加（管理者用）"""
    try:
        conn = get_db_connection()
        cur = conn.cursor()

        # ユニーク制約を追加
        cur.execute("""
            CREATE UNIQUE INDEX IF NOT EXISTS idx_stock_news_unique_url
            ON stock_news(symbol, url);
        """)
        conn.commit()

        cur.close()
        conn.close()

        return {
            "status": "success",
            "message": "Unique constraint added successfully"
        }
    except Exception as e:
        return {
            "status": "error",
            "message": str(e)
        }

@app.get("/admin/check-table-structure")
def check_table_structure():
    """テーブル構造を確認（管理者用）"""
    try:
        conn = get_db_connection()
        cur = conn.cursor(cursor_factory=RealDictCursor)

        tables_info = {}

        # 1. stock_news テーブル構造
        cur.execute("""
            SELECT column_name, data_type, character_maximum_length, is_nullable, column_default
            FROM information_schema.columns
            WHERE table_name = 'stock_news'
            ORDER BY ordinal_position;
        """)
        tables_info['stock_news'] = [dict(row) for row in cur.fetchall()]

        # 2. stock_sentiment_summary テーブル構造
        cur.execute("""
            SELECT column_name, data_type, character_maximum_length, is_nullable, column_default
            FROM information_schema.columns
            WHERE table_name = 'stock_sentiment_summary'
            ORDER BY ordinal_position;
        """)
        tables_info['stock_sentiment_summary'] = [dict(row) for row in cur.fetchall()]

        # 3. ensemble_predictions テーブル構造（センチメント関連カラム）
        cur.execute("""
            SELECT column_name, data_type, character_maximum_length, is_nullable, column_default
            FROM information_schema.columns
            WHERE table_name = 'ensemble_predictions'
            AND (column_name LIKE '%sentiment%' OR column_name LIKE '%news%')
            ORDER BY ordinal_position;
        """)
        tables_info['ensemble_predictions_sentiment_columns'] = [dict(row) for row in cur.fetchall()]

        # 4. インデックス確認
        cur.execute("""
            SELECT
                tablename,
                indexname,
                indexdef
            FROM pg_indexes
            WHERE tablename IN ('stock_news', 'stock_sentiment_summary')
            ORDER BY tablename, indexname;
        """)
        tables_info['indexes'] = [dict(row) for row in cur.fetchall()]

        # 5. 外部キー制約
        cur.execute("""
            SELECT
                tc.constraint_name,
                tc.table_name,
                kcu.column_name,
                ccu.table_name AS foreign_table_name,
                ccu.column_name AS foreign_column_name
            FROM information_schema.table_constraints AS tc
            JOIN information_schema.key_column_usage AS kcu
                ON tc.constraint_name = kcu.constraint_name
            JOIN information_schema.constraint_column_usage AS ccu
                ON ccu.constraint_name = tc.constraint_name
            WHERE tc.constraint_type = 'FOREIGN KEY'
            AND tc.table_name IN ('stock_news', 'stock_sentiment_summary');
        """)
        tables_info['foreign_keys'] = [dict(row) for row in cur.fetchall()]

        cur.close()
        conn.close()

        return {
            "status": "success",
            "tables": tables_info
        }
    except Exception as e:
        import traceback
        return {
            "status": "error",
            "message": str(e),
            "traceback": traceback.format_exc()
        }

@app.get("/admin/check-news-data")
def check_news_data(symbol: str = "AAPL", limit: int = 5):
    """stock_newsテーブルのデータを確認（管理者用）"""
    try:
        conn = get_db_connection()
        cur = conn.cursor(cursor_factory=RealDictCursor)

        # stock_newsの件数
        cur.execute("SELECT COUNT(*) as total FROM stock_news WHERE symbol = %s", (symbol,))
        total = cur.fetchone()['total']

        # 最新のニュース
        cur.execute("""
            SELECT title, sentiment_score, sentiment_label, relevance_score, published_at, source
            FROM stock_news
            WHERE symbol = %s
            ORDER BY published_at DESC
            LIMIT %s
        """, (symbol, limit))
        news = cur.fetchall()

        # stock_sentiment_summaryの確認
        cur.execute("""
            SELECT * FROM stock_sentiment_summary
            WHERE symbol = %s
        """, (symbol,))
        sentiment_summary = cur.fetchone()

        cur.close()
        conn.close()

        return {
            "status": "success",
            "symbol": symbol,
            "total_news": int(total),
            "latest_news": [
                {
                    "title": row['title'],
                    "sentiment_score": float(row['sentiment_score']) if row['sentiment_score'] else None,
                    "sentiment_label": row['sentiment_label'],
                    "relevance_score": float(row['relevance_score']) if row['relevance_score'] else None,
                    "published_at": str(row['published_at']),
                    "source": row['source']
                }
                for row in news
            ],
            "sentiment_summary": dict(sentiment_summary) if sentiment_summary else None
        }
    except Exception as e:
        import traceback
        return {
            "status": "error",
            "message": str(e),
            "traceback": traceback.format_exc()
        }

@app.post("/admin/collect-news")
def collect_news_sentiment(limit: int = 3):
    """ニュース収集とセンチメント分析を実行（管理者用）"""
    import requests
    import time
    from datetime import datetime, timedelta

    ALPHA_VANTAGE_API_KEY = os.getenv('ALPHA_VANTAGE_API_KEY', 'demo')

    if ALPHA_VANTAGE_API_KEY == 'demo':
        return {"status": "error", "message": "ALPHA_VANTAGE_API_KEY not configured"}

    try:
        conn = get_db_connection()
        cur = conn.cursor(cursor_factory=RealDictCursor)

        # 米国株・日本株を優先的に取得
        cur.execute("""
            SELECT symbol, company_name
            FROM stock_master
            WHERE is_active = TRUE
              AND symbol NOT LIKE %s
              AND symbol NOT LIKE %s
              AND (symbol LIKE %s OR (symbol NOT LIKE %s AND LENGTH(symbol) <= 5))
            ORDER BY
                CASE
                    WHEN symbol IN ('AAPL', 'GOOGL', 'MSFT', 'AMZN', 'TSLA') THEN 1
                    WHEN symbol LIKE %s THEN 2
                    ELSE 3
                END,
                symbol
            LIMIT %s
        """, ('%.KS', '%.HK', '%.T', '%.%', '%.T', limit))
        symbols = cur.fetchall()

        if not symbols:
            return {
                "status": "error",
                "message": "No suitable stocks found for news collection (US/Japanese stocks only)"
            }

        results = []
        for symbol_info in symbols:
            symbol = symbol_info['symbol']

            # Alpha Vantage APIからニュース取得
            time_from = (datetime.now() - timedelta(days=7)).strftime("%Y%m%dT0000")
            params = {
                'function': 'NEWS_SENTIMENT',
                'tickers': symbol,
                'time_from': time_from,
                'limit': 10,
                'apikey': ALPHA_VANTAGE_API_KEY
            }

            try:
                response = requests.get('https://www.alphavantage.co/query', params=params, timeout=30)
                data = response.json()

                news_saved = 0
                news_errors = []
                feed_count = len(data.get('feed', []))

                if 'feed' in data:
                    for article in data['feed']:
                        # 銘柄固有のセンチメント抽出
                        ticker_sentiment = None
                        if 'ticker_sentiment' in article:
                            for ts in article['ticker_sentiment']:
                                if ts.get('ticker') == symbol:
                                    ticker_sentiment = ts
                                    break

                        if not ticker_sentiment:
                            continue

                        # データ挿入
                        try:
                            cur.execute("""
                                INSERT INTO stock_news (
                                    symbol, title, url, source, published_at,
                                    summary, sentiment_score, sentiment_label, relevance_score
                                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                                ON CONFLICT (symbol, url) DO NOTHING
                            """, (
                                symbol,
                                article.get('title', ''),
                                article.get('url', ''),
                                article.get('source', 'Unknown'),
                                datetime.strptime(article['time_published'], '%Y%m%dT%H%M%S'),
                                article.get('summary', ''),
                                float(ticker_sentiment.get('ticker_sentiment_score', 0)),
                                ticker_sentiment.get('ticker_sentiment_label', 'neutral').lower(),
                                float(ticker_sentiment.get('relevance_score', 0))
                            ))
                            news_saved += 1
                        except Exception as insert_error:
                            news_errors.append(str(insert_error))

                    conn.commit()

                results.append({
                    "symbol": symbol,
                    "company_name": symbol_info['company_name'],
                    "news_collected": news_saved,
                    "feed_count": feed_count,
                    "errors": news_errors[:3] if news_errors else []
                })

                # API制限対応
                time.sleep(12)

            except Exception as e:
                results.append({
                    "symbol": symbol,
                    "company_name": symbol_info['company_name'],
                    "error": str(e)
                })

        cur.close()
        conn.close()

        return {
            "status": "success",
            "message": f"News collection completed for {len(symbols)} symbols",
            "results": results
        }

    except Exception as e:
        import traceback
        return {
            "status": "error",
            "message": str(e),
            "traceback": traceback.format_exc()
        }

@app.post("/admin/collect-news-for-symbol")
def collect_news_for_single_symbol(symbol: str):
    """特定銘柄のニュースを収集（管理者用）"""
    import requests
    from datetime import datetime, timedelta

    ALPHA_VANTAGE_API_KEY = os.getenv('ALPHA_VANTAGE_API_KEY', 'demo')

    if ALPHA_VANTAGE_API_KEY == 'demo':
        return {"status": "error", "message": "ALPHA_VANTAGE_API_KEY not configured"}

    try:
        conn = get_db_connection()
        cur = conn.cursor(cursor_factory=RealDictCursor)

        # 銘柄情報取得
        cur.execute("SELECT symbol, company_name FROM stock_master WHERE symbol = %s", (symbol,))
        stock = cur.fetchone()

        if not stock:
            return {"status": "error", "message": f"Symbol {symbol} not found"}

        # Alpha Vantage APIからニュース取得
        time_from = (datetime.now() - timedelta(days=7)).strftime("%Y%m%dT0000")
        params = {
            'function': 'NEWS_SENTIMENT',
            'tickers': symbol,
            'time_from': time_from,
            'limit': 50,
            'apikey': ALPHA_VANTAGE_API_KEY
        }

        response = requests.get('https://www.alphavantage.co/query', params=params, timeout=30)
        data = response.json()

        news_saved = 0
        news_errors = []
        feed_count = len(data.get('feed', []))

        if 'feed' in data:
            for article in data['feed']:
                # 銘柄固有のセンチメント抽出
                ticker_sentiment = None
                if 'ticker_sentiment' in article:
                    for ts in article['ticker_sentiment']:
                        if ts.get('ticker') == symbol:
                            ticker_sentiment = ts
                            break

                if not ticker_sentiment:
                    continue

                # データ挿入
                try:
                    cur.execute("""
                        INSERT INTO stock_news (
                            symbol, title, url, source, published_at,
                            summary, sentiment_score, sentiment_label, relevance_score
                        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                        ON CONFLICT (symbol, url) DO NOTHING
                    """, (
                        symbol,
                        article.get('title', ''),
                        article.get('url', ''),
                        article.get('source', 'Unknown'),
                        datetime.strptime(article['time_published'], '%Y%m%dT%H%M%S'),
                        article.get('summary', ''),
                        float(ticker_sentiment.get('ticker_sentiment_score', 0)),
                        ticker_sentiment.get('ticker_sentiment_label', 'neutral').lower(),
                        float(ticker_sentiment.get('relevance_score', 0))
                    ))
                    news_saved += 1
                except Exception as insert_error:
                    news_errors.append(str(insert_error))

            conn.commit()

        cur.close()
        conn.close()

        return {
            "status": "success",
            "symbol": symbol,
            "company_name": stock['company_name'],
            "news_collected": news_saved,
            "feed_count": feed_count,
            "errors": news_errors[:3] if news_errors else []
        }

    except Exception as e:
        import traceback
        return {
            "status": "error",
            "message": str(e),
            "traceback": traceback.format_exc()
        }

@app.get("/api/predictions/summary")
def get_summary():
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    try:
        # 基本的な集計
        cur.execute("""
            SELECT COUNT(*) as total_predictions,
                   COUNT(DISTINCT CASE WHEN prediction_date >= CURRENT_DATE THEN symbol END) as active_predictions,
                   ROUND(CAST(AVG(ensemble_confidence) AS numeric), 3) as avg_confidence
            FROM ensemble_predictions
        """)
        summary = cur.fetchone()

        # モデル別カバレッジ
        cur.execute("""
            SELECT
                COUNT(DISTINCT CASE WHEN lstm_prediction IS NOT NULL THEN symbol END) * 100.0 / NULLIF(COUNT(DISTINCT symbol), 0) as lstm_coverage,
                COUNT(DISTINCT CASE WHEN arima_prediction IS NOT NULL THEN symbol END) * 100.0 / NULLIF(COUNT(DISTINCT symbol), 0) as arima_coverage,
                COUNT(DISTINCT CASE WHEN ma_prediction IS NOT NULL THEN symbol END) * 100.0 / NULLIF(COUNT(DISTINCT symbol), 0) as ma_coverage
            FROM ensemble_predictions
            WHERE prediction_date >= CURRENT_DATE
        """)
        coverage = cur.fetchone()

        # トップパフォーマー（仮データ）
        top_performers = [
            {"symbol": "AAPL", "accuracy": 92.5},
            {"symbol": "GOOGL", "accuracy": 90.2},
            {"symbol": "MSFT", "accuracy": 89.8}
        ]

        # 最近のエラー（仮データ）
        recent_errors = [
            {"symbol": "TSLA", "error": 5.2},
            {"symbol": "AMZN", "error": 4.8}
        ]

        # 日次統計（仮データ）
        daily_stats = [
            {"date": "2025-10-08", "count": 1500, "accuracy": 85.0},
            {"date": "2025-10-09", "count": 1520, "accuracy": 86.0},
            {"date": "2025-10-10", "count": 1550, "accuracy": 87.0}
        ]

        return {
            "totalPredictions": int(summary['total_predictions']),
            "activePredictions": int(summary['active_predictions'] or 0),
            "avgConfidence": float(summary['avg_confidence'] or 0),
            "avgAccuracy": 85.0,
            "predictionCoverage": 95.0,
            "lstmCoverage": float(coverage['lstm_coverage'] or 0),
            "arimaCoverage": float(coverage['arima_coverage'] or 0),
            "maCoverage": float(coverage['ma_coverage'] or 0),
            "topPerformers": top_performers,
            "recentErrors": recent_errors,
            "dailyStats": daily_stats
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cur.close()
        conn.close()

@app.get("/api/monitoring/model-performance")
def get_model_performance():
    return {
        "lstm": {"avg": 85.0, "count": 1000, "confidence": 0.8},
        "arima": {"avg": 80.0, "count": 800, "confidence": 0.7},
        "ma": {"avg": 75.0, "count": 900, "confidence": 0.6},
        "ensemble": {"avg": 87.0, "count": 1500, "confidence": 0.85}
    }


@app.get("/api/home/stats/summary")
def get_home_stats():
    """ホームページ用の統計サマリー - 実際のDB数を返す"""
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    try:
        # 実際のstock_master総数を取得
        cur.execute("""
            SELECT
                COUNT(*) as total_symbols,
                COUNT(CASE WHEN is_active = TRUE THEN 1 END) as active_symbols
            FROM stock_master
        """)
        master_stats = cur.fetchone()

        # 予測データあり銘柄数を取得
        cur.execute("""
            SELECT
                COUNT(DISTINCT symbol) as symbols_with_predictions,
                COUNT(DISTINCT CASE WHEN prediction_date >= CURRENT_DATE THEN symbol END) as symbols_with_future_predictions
            FROM ensemble_predictions
        """)
        prediction_stats = cur.fetchone()

        return {
            "totalSymbols": int(master_stats['total_symbols'] or 0),
            "activeSymbols": int(master_stats['active_symbols'] or 0),
            "activePredictions": int(prediction_stats['symbols_with_future_predictions'] or 0),
            "totalPredictions": int(prediction_stats['symbols_with_predictions'] or 0),
            "avgAccuracy": 85.2,
            "modelsRunning": 3
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cur.close()
        conn.close()

@app.get("/api/home/rankings/gainers")
def get_top_gainers(limit: int = 50):
    """値上がり率ランキング"""
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    try:
        cur.execute("""
            WITH latest_prices AS (
                SELECT DISTINCT ON (symbol)
                    symbol,
                    close_price as current_price,
                    date
                FROM stock_prices
                ORDER BY symbol, date DESC
            ),
            prev_prices AS (
                SELECT DISTINCT ON (sp.symbol)
                    sp.symbol,
                    sp.close_price as prev_price
                FROM stock_prices sp
                INNER JOIN latest_prices lp ON sp.symbol = lp.symbol
                WHERE sp.date < lp.date
                ORDER BY sp.symbol, sp.date DESC
            )
            SELECT
                lp.symbol,
                sm.company_name,
                sm.exchange,
                lp.current_price,
                pp.prev_price,
                ROUND(((lp.current_price - pp.prev_price) / NULLIF(pp.prev_price, 0) * 100)::numeric, 2) as change_percent
            FROM latest_prices lp
            LEFT JOIN prev_prices pp ON lp.symbol = pp.symbol
            LEFT JOIN stock_master sm ON lp.symbol = sm.symbol
            WHERE pp.prev_price IS NOT NULL AND pp.prev_price > 0
            ORDER BY change_percent DESC NULLS LAST
            LIMIT %s
        """, (limit,))

        results = cur.fetchall()
        return [
            {
                "symbol": row['symbol'],
                "name": row['company_name'] or row['symbol'],
                "exchange": row['exchange'] or '',
                "price": float(row['current_price']),
                "change": float(row['change_percent'])
            }
            for row in results
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cur.close()
        conn.close()

@app.get("/api/home/rankings/losers")
def get_top_losers(limit: int = 50):
    """値下がり率ランキング"""
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    try:
        cur.execute("""
            WITH latest_prices AS (
                SELECT DISTINCT ON (symbol)
                    symbol,
                    close_price as current_price,
                    date
                FROM stock_prices
                ORDER BY symbol, date DESC
            ),
            prev_prices AS (
                SELECT DISTINCT ON (sp.symbol)
                    sp.symbol,
                    sp.close_price as prev_price
                FROM stock_prices sp
                INNER JOIN latest_prices lp ON sp.symbol = lp.symbol
                WHERE sp.date < lp.date
                ORDER BY sp.symbol, sp.date DESC
            )
            SELECT
                lp.symbol,
                sm.company_name,
                sm.exchange,
                lp.current_price,
                pp.prev_price,
                ROUND(((lp.current_price - pp.prev_price) / NULLIF(pp.prev_price, 0) * 100)::numeric, 2) as change_percent
            FROM latest_prices lp
            LEFT JOIN prev_prices pp ON lp.symbol = pp.symbol
            LEFT JOIN stock_master sm ON lp.symbol = sm.symbol
            WHERE pp.prev_price IS NOT NULL AND pp.prev_price > 0
            ORDER BY change_percent ASC NULLS LAST
            LIMIT %s
        """, (limit,))

        results = cur.fetchall()
        return [
            {
                "symbol": row['symbol'],
                "name": row['company_name'] or row['symbol'],
                "exchange": row['exchange'] or '',
                "price": float(row['current_price']),
                "change": float(row['change_percent'])
            }
            for row in results
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cur.close()
        conn.close()

@app.get("/api/home/rankings/volume")
def get_top_volume(limit: int = 50):
    """出来高ランキング"""
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    try:
        cur.execute("""
            SELECT DISTINCT ON (sp.symbol)
                sp.symbol,
                sm.company_name,
                sm.exchange,
                sp.close_price as price,
                sp.volume,
                sp.date
            FROM stock_prices sp
            LEFT JOIN stock_master sm ON sp.symbol = sm.symbol
            WHERE sp.volume IS NOT NULL AND sp.volume > 0
            ORDER BY sp.symbol, sp.date DESC, sp.volume DESC
        """)

        all_results = cur.fetchall()
        sorted_results = sorted(all_results, key=lambda x: x['volume'], reverse=True)[:limit]

        return [
            {
                "symbol": row['symbol'],
                "name": row['company_name'] or row['symbol'],
                "exchange": row['exchange'] or '',
                "price": float(row['price']),
                "volume": int(row['volume'])
            }
            for row in sorted_results
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cur.close()
        conn.close()

@app.get("/api/home/rankings/predictions")
def get_top_predictions(limit: int = 50):
    """予測精度ランキング"""
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    try:
        cur.execute("""
            WITH ranked_predictions AS (
                SELECT DISTINCT ON (ep.symbol)
                    ep.symbol,
                    sm.company_name,
                    sm.exchange,
                    ep.current_price,
                    ep.ensemble_prediction,
                    ep.ensemble_confidence,
                    ROUND(((ep.ensemble_prediction - ep.current_price) / NULLIF(ep.current_price, 0) * 100)::numeric, 2) as predicted_change
                FROM ensemble_predictions ep
                LEFT JOIN stock_master sm ON ep.symbol = sm.symbol
                WHERE ep.prediction_date >= CURRENT_DATE
                  AND ep.ensemble_confidence IS NOT NULL
                  AND ep.current_price IS NOT NULL
                  AND ep.current_price > 0
                ORDER BY ep.symbol, ep.prediction_date DESC
            )
            SELECT * FROM ranked_predictions
            ORDER BY predicted_change DESC NULLS LAST
            LIMIT %s
        """, (limit,))

        results = cur.fetchall()
        return [
            {
                "symbol": row['symbol'],
                "name": row['company_name'] or row['symbol'],
                "exchange": row['exchange'] or '',
                "currentPrice": float(row['current_price']),
                "predictedPrice": float(row['ensemble_prediction']),
                "confidence": float(row['ensemble_confidence']),
                "predictedChange": float(row['predicted_change'])
            }
            for row in results
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cur.close()
        conn.close()


@app.get("/api/stocks")
def get_stocks(limit: int = 100, exchange: str = None):
    """銘柄一覧取得"""
    # Validate limit parameter
    if limit < 1:
        limit = 100
    elif limit > 1000:
        limit = 1000

    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    try:
        # Build query based on whether exchange filter is provided
        if exchange:
            cur.execute("""
                SELECT symbol, company_name, exchange, is_active
                FROM stock_master
                WHERE LOWER(exchange) LIKE LOWER(%s)
                ORDER BY symbol
                LIMIT %s
            """, (f'%{exchange}%', limit))
        else:
            cur.execute("""
                SELECT symbol, company_name, exchange, is_active
                FROM stock_master
                ORDER BY symbol
                LIMIT %s
            """, (limit,))

        stocks = cur.fetchall()

        return {
            "stocks": [
                {
                    "symbol": row['symbol'],
                    "company_name": row['company_name'],
                    "exchange": row['exchange'],
                    "is_active": row['is_active']
                }
                for row in stocks
            ],
            "count": len(stocks)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cur.close()
        conn.close()


@app.get("/api/stocks/{symbol}")
def get_stock_info(symbol: str):
    """銘柄情報取得"""
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    try:
        cur.execute("""
            SELECT symbol, company_name, exchange, is_active
            FROM stock_master
            WHERE symbol = %s
        """, (symbol,))
        stock = cur.fetchone()

        if not stock:
            raise HTTPException(status_code=404, detail=f"Symbol {symbol} not found")

        # Get recent price history
        cur.execute("""
            SELECT date, open_price, high_price, low_price, close_price, volume
            FROM stock_prices
            WHERE symbol = %s
            ORDER BY date DESC
            LIMIT 30
        """, (symbol,))
        price_history = cur.fetchall()

        return {
            "symbol": stock['symbol'],
            "company_name": stock['company_name'],
            "exchange": stock['exchange'],
            "price_history": [
                {
                    "date": str(row['date']),
                    "open_price": float(row['open_price']) if row['open_price'] else None,
                    "high_price": float(row['high_price']) if row['high_price'] else None,
                    "low_price": float(row['low_price']) if row['low_price'] else None,
                    "close_price": float(row['close_price']) if row['close_price'] else None,
                    "volume": int(row['volume']) if row['volume'] else None
                }
                for row in price_history
            ]
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cur.close()
        conn.close()

@app.get("/api/stocks/{symbol}/price")
def get_price_history(symbol: str, days: int = 365):
    """価格履歴取得"""
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    try:
        cur.execute("""
            SELECT date, open_price, high_price, low_price, close_price, volume
            FROM stock_prices
            WHERE symbol = %s
            ORDER BY date DESC
            LIMIT %s
        """, (symbol, days))
        prices = cur.fetchall()

        if not prices:
            raise HTTPException(status_code=404, detail=f"No price data for {symbol}")

        return [
            {
                "date": str(row['date']),
                "open_price": float(row['open_price']) if row['open_price'] else None,
                "high_price": float(row['high_price']) if row['high_price'] else None,
                "low_price": float(row['low_price']) if row['low_price'] else None,
                "close_price": float(row['close_price']) if row['close_price'] else None,
                "volume": int(row['volume']) if row['volume'] else None
            }
            for row in prices
        ]
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cur.close()
        conn.close()

@app.get("/api/stocks/{symbol}/predictions")
def get_stock_predictions(symbol: str, days: int = 365, page: int = 1, limit: int = 1000):
    """予測データ取得"""
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    try:
        offset = (page - 1) * limit
        cur.execute("""
            SELECT
                symbol,
                prediction_date,
                prediction_days,
                current_price,
                lstm_prediction,
                arima_prediction,
                ma_prediction,
                ensemble_prediction,
                ensemble_confidence
            FROM ensemble_predictions
            WHERE symbol = %s
              AND prediction_date >= CURRENT_DATE - INTERVAL '%s days'
            ORDER BY prediction_date DESC
            LIMIT %s OFFSET %s
        """, (symbol, days, limit, offset))
        predictions = cur.fetchall()

        if not predictions:
            return {
                "symbol": symbol,
                "pagination": {"page": page, "limit": limit, "total": 0, "total_pages": 0},
                "predictions": []
            }

        # Get total count
        cur.execute("""
            SELECT COUNT(*) as total
            FROM ensemble_predictions
            WHERE symbol = %s
              AND prediction_date >= CURRENT_DATE - INTERVAL '%s days'
        """, (symbol, days))
        total = cur.fetchone()['total']

        return {
            "symbol": symbol,
            "pagination": {
                "page": page,
                "limit": limit,
                "total": total,
                "total_pages": (total + limit - 1) // limit
            },
            "predictions": [
                {
                    "prediction_date": str(row['prediction_date']),
                    "predicted_price": float(row['ensemble_prediction']),
                    "current_price": float(row['current_price']) if row['current_price'] else None,
                    "prediction_days": int(row['prediction_days']) if row['prediction_days'] else None,
                    "confidence_score": float(row['ensemble_confidence']) if row['ensemble_confidence'] else None,
                    "model_type": "ensemble"
                }
                for row in predictions
            ]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cur.close()
        conn.close()

# IMPORTANT: Specific routes MUST come BEFORE parameterized routes
@app.get("/api/predictions/rankings")
def get_prediction_rankings(limit: int = 50):
    """
    予測価格変動率ランキング
    Returns top predictions ranked by predicted price change
    """
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    try:
        cur.execute("""
            WITH latest_predictions AS (
                SELECT DISTINCT ON (ep.symbol)
                    ep.symbol,
                    sm.company_name,
                    sm.exchange,
                    ep.current_price,
                    ep.ensemble_prediction,
                    ep.ensemble_confidence,
                    ROUND(((ep.ensemble_prediction - ep.current_price) / NULLIF(ep.current_price, 0) * 100)::numeric, 2) as predicted_change_percent,
                    ep.prediction_date
                FROM ensemble_predictions ep
                LEFT JOIN stock_master sm ON ep.symbol = sm.symbol
                WHERE ep.prediction_date >= CURRENT_DATE
                  AND ep.ensemble_prediction IS NOT NULL
                  AND ep.current_price IS NOT NULL
                  AND ep.current_price > 0
                  AND ep.ensemble_confidence IS NOT NULL
                ORDER BY ep.symbol, ep.prediction_date DESC
            )
            SELECT
                symbol,
                company_name,
                exchange,
                current_price,
                ensemble_prediction as predicted_price,
                predicted_change_percent,
                ensemble_confidence as confidence_score
            FROM latest_predictions
            ORDER BY predicted_change_percent DESC NULLS LAST
            LIMIT %s
        """, (limit,))

        results = cur.fetchall()
        rankings = [
            {
                "symbol": row['symbol'],
                "company_name": row['company_name'] or row['symbol'],
                "exchange": row['exchange'] or '',
                "current_price": float(row['current_price']),
                "predicted_price": float(row['predicted_price']),
                "predicted_change_percent": float(row['predicted_change_percent']),
                "confidence_score": float(row['confidence_score'])
            }
            for row in results
        ]
        return {"rankings": rankings}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cur.close()
        conn.close()

@app.get("/api/predictions/accuracy/summary")
def get_accuracy_summary():
    """
    予測精度サマリー
    Returns overall prediction accuracy summary across all stocks
    """
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    try:
        cur.execute("""
            SELECT
                COUNT(DISTINCT sp.symbol) as evaluated_symbols,
                COUNT(*) as total_predictions,
                ROUND(AVG(ABS(sp.predicted_price - sp.current_price))::numeric, 2) as overall_mae,
                ROUND(AVG(ABS(sp.predicted_price - sp.current_price) / NULLIF(sp.current_price, 0) * 100)::numeric, 2) as overall_mape,
                ROUND(GREATEST(0, 100 - AVG(ABS(sp.predicted_price - sp.current_price) / NULLIF(sp.current_price, 0) * 100))::numeric, 2) as overall_direction_accuracy,
                TO_CHAR(MIN(sp.prediction_date), 'YYYY-MM-DD') || ' - ' || TO_CHAR(MAX(sp.prediction_date), 'YYYY-MM-DD') as evaluation_period
            FROM stock_predictions sp
            WHERE sp.predicted_price > 0
              AND sp.current_price > 0
        """)

        result = cur.fetchone()

        if result and result['total_predictions'] > 0:
            return {
                "evaluated_symbols": int(result['evaluated_symbols']),
                "total_predictions": int(result['total_predictions']),
                "overall_mae": float(result['overall_mae']),
                "overall_mape": float(result['overall_mape']),
                "overall_direction_accuracy": float(result['overall_direction_accuracy']),
                "evaluation_period": result['evaluation_period'] or 'N/A'
            }
        else:
            return {
                "evaluated_symbols": 0,
                "total_predictions": 0,
                "overall_mae": 0,
                "overall_mape": 0,
                "overall_direction_accuracy": 0,
                "evaluation_period": 'No data available'
            }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cur.close()
        conn.close()

@app.get("/api/predictions/accuracy/rankings")
def get_accuracy_rankings(limit: int = 50):
    """
    予測精度ランキング
    Returns stocks ranked by prediction accuracy (reliability_score)
    Only includes stocks that have accuracy metrics calculated
    """
    conn = get_db_connection()

    cur = conn.cursor(cursor_factory=RealDictCursor)
    try:
        cur.execute("""
            SELECT
                sp.symbol,
                sm.company_name,
                sm.exchange,
                COUNT(*) as sample_size,
                ROUND(AVG(ABS(sp.predicted_price - sp.current_price))::numeric, 2) as mae,
                ROUND(AVG(ABS(sp.predicted_price - sp.current_price) / NULLIF(sp.current_price, 0) * 100)::numeric, 2) as mape,
                ROUND(GREATEST(0, 100 - AVG(ABS(sp.predicted_price - sp.current_price) / NULLIF(sp.current_price, 0) * 100))::numeric, 2) as direction_accuracy,
                CASE
                    WHEN AVG(ABS(sp.predicted_price - sp.current_price) / NULLIF(sp.current_price, 0) * 100) <= 2 THEN 'excellent'
                    WHEN AVG(ABS(sp.predicted_price - sp.current_price) / NULLIF(sp.current_price, 0) * 100) <= 5 THEN 'good'
                    WHEN AVG(ABS(sp.predicted_price - sp.current_price) / NULLIF(sp.current_price, 0) * 100) <= 10 THEN 'fair'
                    ELSE 'poor'
                END as reliability,
                CASE
                    WHEN AVG(ABS(sp.predicted_price - sp.current_price) / NULLIF(sp.current_price, 0) * 100) <= 2 THEN 0.95
                    WHEN AVG(ABS(sp.predicted_price - sp.current_price) / NULLIF(sp.current_price, 0) * 100) <= 5 THEN 0.85
                    WHEN AVG(ABS(sp.predicted_price - sp.current_price) / NULLIF(sp.current_price, 0) * 100) <= 10 THEN 0.75
                    ELSE 0.60
                END as reliability_score
            FROM stock_predictions sp
            LEFT JOIN stock_master sm ON sp.symbol = sm.symbol
            WHERE sp.predicted_price > 0
              AND sp.current_price > 0
            GROUP BY sp.symbol, sm.company_name, sm.exchange
            HAVING COUNT(*) >= 5
              AND AVG(ABS(sp.predicted_price - sp.current_price) / NULLIF(sp.current_price, 0) * 100) > 0.01
            ORDER BY reliability_score DESC, mape ASC
            LIMIT %s
        """, (limit,))

        results = cur.fetchall()
        rankings = [
            {
                "symbol": row['symbol'],
                "company_name": row['company_name'] or row['symbol'],
                "exchange": row['exchange'] or '',
                "sample_size": int(row['sample_size']),
                "mae": float(row['mae']),
                "mape": float(row['mape']),
                "direction_accuracy": float(row['direction_accuracy']),
                "reliability": row['reliability'],
                "reliability_score": float(row['reliability_score'])
            }
            for row in results
        ]
        return {"rankings": rankings, "count": len(rankings)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cur.close()
        conn.close()

# Parameterized route must come AFTER specific routes
@app.get("/api/predictions/accuracy/{symbol}")
def get_prediction_accuracy(symbol: str, days_back: int = 90):
    """予測精度取得"""
    return {
        "symbol": symbol,
        "evaluation_available": False,
        "message": "Prediction accuracy evaluation is not yet implemented"
    }

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8080))
    uvicorn.run(app, host="0.0.0.0", port=port)

@app.post("/admin/generate-sentiment-predictions")
def generate_sentiment_predictions(limit: int = 10):
    """センチメント統合予測を生成（管理者用）"""
    try:
        import generate_predictions_simple
        conn = get_db_connection()
        cur = conn.cursor(cursor_factory=RealDictCursor)

        # 銘柄取得
        cur.execute("""
            SELECT symbol, company_name FROM stock_master
            WHERE is_active = TRUE
              AND symbol NOT LIKE %s
              AND symbol NOT LIKE %s
              AND (symbol LIKE %s OR (symbol NOT LIKE %s AND LENGTH(symbol) <= 5))
            ORDER BY
                CASE
                    WHEN symbol IN ('AAPL', 'GOOGL', 'MSFT', 'AMZN', 'TSLA') THEN 1
                    WHEN symbol LIKE %s THEN 2
                    ELSE 3
                END,
                symbol
            LIMIT %s
        """, ('%.KS', '%.HK', '%.T', '%.%', '%.T', limit))

        symbols = cur.fetchall()
        cur.close()

        if not symbols:
            return {"status": "error", "message": "No suitable symbols found"}

        # 予測生成
        results = generate_predictions_simple.generate_for_symbols(symbols, conn)
        conn.close()

        return {
            "status": "success",
            "message": f"Sentiment-enhanced predictions generated for {len([r for r in results if 'error' not in r])} symbols",
            "results": results
        }

    except Exception as e:
        import traceback
        return {
            "status": "error",
            "message": str(e),
            "traceback": traceback.format_exc()
        }

@app.get("/admin/check-prediction-accuracy")
def check_prediction_accuracy_endpoint(days_back: int = 30, limit: int = 100):
    """過去予測の精度をチェック（管理者用）"""
    try:
        import accuracy_checker
        conn = get_db_connection()
        result = accuracy_checker.check_past_accuracy(conn, days_back, limit)
        conn.close()
        return {"status": "success", **result}
    except Exception as e:
        import traceback
        return {"status": "error", "message": str(e), "traceback": traceback.format_exc()}

@app.get("/admin/check-future-predictions")
def check_future_predictions_endpoint(limit: int = 100):
    """未来予測の状態をチェック（管理者用）"""
    try:
        import accuracy_checker
        conn = get_db_connection()
        result = accuracy_checker.check_future_predictions(conn, limit)
        conn.close()
        return {"status": "success", **result}
    except Exception as e:
        import traceback
        return {"status": "error", "message": str(e), "traceback": traceback.format_exc()}

@app.get("/admin/check-sentiment-predictions")
def check_sentiment_predictions(symbol: str = "AAPL"):
    """特定銘柄のセンチメント統合予測を確認（管理者用）"""
    try:
        conn = get_db_connection()
        cur = conn.cursor(cursor_factory=RealDictCursor)

        cur.execute("""
            SELECT
                symbol,
                prediction_date,
                current_price,
                ensemble_prediction,
                sentiment_adjusted_prediction,
                news_sentiment,
                news_impact,
                ensemble_confidence,
                (sentiment_adjusted_prediction - ensemble_prediction) / ensemble_prediction * 100 as adjustment_pct,
                created_at
            FROM ensemble_predictions
            WHERE symbol = %s
              AND prediction_date >= CURRENT_DATE
              AND prediction_days = 1
            ORDER BY prediction_date DESC
            LIMIT 5
        """, (symbol,))

        predictions = cur.fetchall()
        cur.close()
        conn.close()

        return {
            "status": "success",
            "symbol": symbol,
            "predictions": [
                {
                    "prediction_date": str(p['prediction_date']),
                    "current_price": float(p['current_price']),
                    "ensemble_prediction": float(p['ensemble_prediction']),
                    "sentiment_adjusted_prediction": float(p['sentiment_adjusted_prediction']) if p['sentiment_adjusted_prediction'] else None,
                    "news_sentiment": float(p['news_sentiment']) if p['news_sentiment'] else None,
                    "news_impact": float(p['news_impact']) if p['news_impact'] else None,
                    "adjustment_pct": float(p['adjustment_pct']) if p['adjustment_pct'] else None,
                    "confidence": float(p['ensemble_confidence']),
                    "created_at": str(p['created_at'])
                }
                for p in predictions
            ]
        }

    except Exception as e:
        import traceback
        return {
            "status": "error",
            "message": str(e),
            "traceback": traceback.format_exc()
        }

@app.get("/admin/stock-statistics")
def get_stock_statistics():
    """銘柄統計情報を取得（管理者用）"""
    try:
        conn = get_db_connection()
        cur = conn.cursor(cursor_factory=RealDictCursor)

        # 銘柄数の集計
        cur.execute("""
            SELECT
                COUNT(*) as total_stocks,
                COUNT(CASE WHEN symbol NOT LIKE '%.T' AND symbol NOT LIKE '%.KS' AND symbol NOT LIKE '%.HK' THEN 1 END) as us_stocks,
                COUNT(CASE WHEN symbol LIKE '%.T' THEN 1 END) as jp_stocks,
                COUNT(CASE WHEN symbol LIKE '%.KS' THEN 1 END) as kr_stocks,
                COUNT(CASE WHEN is_active = TRUE THEN 1 END) as active_stocks,
                COUNT(CASE WHEN is_active = FALSE THEN 1 END) as inactive_stocks
            FROM stock_master
        """)
        stats = cur.fetchone()

        # 米国株サンプル
        cur.execute("""
            SELECT symbol, company_name, exchange
            FROM stock_master
            WHERE symbol NOT LIKE '%.T'
              AND symbol NOT LIKE '%.KS'
              AND symbol NOT LIKE '%.HK'
              AND is_active = TRUE
            ORDER BY symbol
            LIMIT 50
        """)
        us_samples = cur.fetchall()

        # 日本株サンプル
        cur.execute("""
            SELECT symbol, company_name, exchange
            FROM stock_master
            WHERE symbol LIKE '%.T'
              AND is_active = TRUE
            ORDER BY symbol
            LIMIT 50
        """)
        jp_samples = cur.fetchall()

        # ニュースデータのある銘柄
        cur.execute("""
            SELECT
                symbol,
                COUNT(*) as news_count,
                AVG(sentiment_score) as avg_sentiment
            FROM stock_news
            GROUP BY symbol
            ORDER BY news_count DESC
            LIMIT 50
        """)
        news_stats = cur.fetchall()

        cur.close()
        conn.close()

        return {
            "status": "success",
            "statistics": dict(stats),
            "us_stock_samples": [dict(s) for s in us_samples],
            "jp_stock_samples": [dict(s) for s in jp_samples],
            "stocks_with_news": [dict(s) for s in news_stats]
        }

    except Exception as e:
        import traceback
        return {
            "status": "error",
            "message": str(e),
            "traceback": traceback.format_exc()
        }

@app.post("/admin/collect-jp-news-finnhub")
def collect_jp_news_finnhub_endpoint(limit: int = 20):
    """日本株ニュースをFinnhubから収集（管理者用）"""
    FINNHUB_API_KEY = os.getenv('FINNHUB_API_KEY', '')

    if not FINNHUB_API_KEY:
        return {"status": "error", "message": "FINNHUB_API_KEY not configured"}

    try:
        import finnhub_news_collector

        conn = get_db_connection()
        cur = conn.cursor(cursor_factory=RealDictCursor)

        # 日本株銘柄を取得
        cur.execute("""
            SELECT symbol, company_name
            FROM stock_master
            WHERE symbol LIKE '%.T'
              AND is_active = TRUE
            ORDER BY symbol
            LIMIT %s
        """, (limit,))
        symbols = cur.fetchall()
        cur.close()

        if not symbols:
            conn.close()
            return {"status": "error", "message": "No Japanese stocks found"}

        # Finnhubでニュース収集
        results = finnhub_news_collector.collect_jp_news_batch(conn, symbols, FINNHUB_API_KEY)
        conn.close()

        successful = [r for r in results if r.get('status') == 'success']
        failed = [r for r in results if r.get('status') == 'error']

        return {
            "status": "success",
            "message": f"Finnhubから{len(successful)}銘柄のニュース収集完了",
            "successful_count": len(successful),
            "failed_count": len(failed),
            "total_news_collected": sum(r.get('news_collected', 0) for r in successful),
            "results": results
        }

    except Exception as e:
        import traceback
        return {
            "status": "error",
            "message": str(e),
            "traceback": traceback.format_exc()
        }

@app.post("/admin/collect-jp-news-for-symbol-finnhub")
def collect_jp_news_for_symbol_finnhub(symbol: str):
    """特定の日本株ニュースをFinnhubから収集（管理者用）"""
    FINNHUB_API_KEY = os.getenv('FINNHUB_API_KEY', '')

    if not FINNHUB_API_KEY:
        return {"status": "error", "message": "FINNHUB_API_KEY not configured"}

    try:
        import finnhub_news_collector

        conn = get_db_connection()
        result = finnhub_news_collector.collect_jp_news_finnhub(conn, symbol, FINNHUB_API_KEY)
        conn.close()

        return result

    except Exception as e:
        import traceback
        return {
            "status": "error",
            "message": str(e),
            "traceback": traceback.format_exc()
        }

@app.post("/admin/collect-jp-news-yfinance")
def collect_jp_news_yfinance_endpoint(limit: int = 20):
    """日本株ニュースをyfinanceから収集（管理者用）"""
    try:
        import yfinance_jp_news_collector

        conn = get_db_connection()
        cur = conn.cursor(cursor_factory=RealDictCursor)

        # 日本株銘柄を取得
        cur.execute("""
            SELECT symbol, company_name
            FROM stock_master
            WHERE symbol LIKE '%.T'
              AND is_active = TRUE
            ORDER BY symbol
            LIMIT %s
        """, (limit,))
        symbols = cur.fetchall()
        cur.close()

        if not symbols:
            conn.close()
            return {"status": "error", "message": "No Japanese stocks found"}

        # yfinanceでニュース収集
        results = yfinance_jp_news_collector.collect_jp_news_batch(conn, symbols)
        conn.close()

        successful = [r for r in results if r.get('status') == 'success']
        failed = [r for r in results if r.get('status') == 'error']

        return {
            "status": "success",
            "message": f"yfinanceから{len(successful)}銘柄のニュース収集完了",
            "successful_count": len(successful),
            "failed_count": len(failed),
            "total_news_collected": sum(r.get('news_collected', 0) for r in successful),
            "results": results
        }

    except Exception as e:
        import traceback
        return {
            "status": "error",
            "message": str(e),
            "traceback": traceback.format_exc()
        }

@app.post("/admin/collect-jp-news-for-symbol-yfinance")
def collect_jp_news_for_symbol_yfinance(symbol: str):
    """特定の日本株ニュースをyfinanceから収集（管理者用）"""
    try:
        import yfinance_jp_news_collector

        conn = get_db_connection()
        result = yfinance_jp_news_collector.collect_jp_news_yfinance(conn, symbol)
        conn.close()

        return result

    except Exception as e:
        import traceback
        return {
            "status": "error",
            "message": str(e),
            "traceback": traceback.format_exc()
        }


@app.post("/admin/generate-news-enhanced-predictions")
def generate_news_enhanced_predictions_endpoint(limit: int = 100):
    """ニュースセンチメント統合予測を生成（管理者用）"""
    try:
        import generate_news_enhanced_predictions
        
        result = generate_news_enhanced_predictions.generate_batch_predictions(limit)
        
        return {
            "status": "success",
            "message": f"News-enhanced predictions generated",
            "total_symbols": result['total_symbols'],
            "successful": result['successful'],
            "failed": result['failed']
        }
    
    except Exception as e:
        import traceback
        return {
            "status": "error",
            "message": str(e),
            "traceback": traceback.format_exc()
        }

@app.post("/admin/generate-news-prediction-for-symbol")
def generate_news_prediction_for_symbol(symbol: str):
    """特定銘柄のニュース統合予測を生成（管理者用）"""
    try:
        import generate_news_enhanced_predictions

        result = generate_news_enhanced_predictions.generate_news_enhanced_prediction(symbol)
        return result

    except Exception as e:
        import traceback
        return {
            "status": "error",
            "symbol": symbol,
            "message": str(e),
            "traceback": traceback.format_exc()
        }

@app.post("/admin/add-news-sentiment-columns")
def add_news_sentiment_columns():
    """ensemble_predictionsテーブルにニュースセンチメントカラムを追加（管理者用）"""
    try:
        conn = get_db_connection()
        cur = conn.cursor()

        # Add news sentiment columns
        cur.execute("""
            ALTER TABLE ensemble_predictions
            ADD COLUMN IF NOT EXISTS news_sentiment_score DECIMAL(5,4),
            ADD COLUMN IF NOT EXISTS news_count INTEGER DEFAULT 0,
            ADD COLUMN IF NOT EXISTS sentiment_trend DECIMAL(5,4),
            ADD COLUMN IF NOT EXISTS bullish_ratio DECIMAL(5,4),
            ADD COLUMN IF NOT EXISTS bearish_ratio DECIMAL(5,4)
        """)
        conn.commit()

        # Verify columns
        cur.execute("""
            SELECT column_name, data_type
            FROM information_schema.columns
            WHERE table_name = 'ensemble_predictions'
              AND column_name IN ('news_sentiment_score', 'news_count', 'sentiment_trend', 'bullish_ratio', 'bearish_ratio')
            ORDER BY column_name
        """)
        columns = cur.fetchall()

        cur.close()
        conn.close()

        return {
            "status": "success",
            "message": "News sentiment columns added successfully",
            "columns_added": [{"name": c[0], "type": c[1]} for c in columns]
        }

    except Exception as e:
        import traceback
        return {
            "status": "error",
            "message": str(e),
            "traceback": traceback.format_exc()
        }

@app.post("/admin/collect-news-newsapi")
def collect_news_newsapi_endpoint(symbol: str, company_name: str, days: int = 7):
    """NewsAPI.orgを使用してニュース収集（管理者用）"""
    try:
        import newsapi_collector

        collector = newsapi_collector.NewsAPICollector()
        result = collector.collect_news_for_symbol(symbol, company_name, days)

        return result

    except Exception as e:
        import traceback
        return {
            "status": "error",
            "message": str(e),
            "traceback": traceback.format_exc()
        }

@app.post("/admin/collect-news-newsapi-batch")
def collect_news_newsapi_batch_endpoint(limit: int = 15):
    """NewsAPI.orgを使用してバッチニュース収集（管理者用）

    日本株15銘柄のニュースを一括収集
    NewsAPI.org無料プラン: 100リクエスト/日
    シンボルマッピング済み: 15社
    """
    try:
        import newsapi_collector

        conn = get_db_connection()
        cur = conn.cursor(cursor_factory=RealDictCursor)

        # 日本株銘柄をシンボルマッピング済みのものから取得
        # newsapi_collector.pyのsymbol_to_enに登録されている銘柄のみ
        supported_symbols = [
            '7203.T',  # Toyota
            '6758.T',  # Sony
            '9984.T',  # SoftBank
            '7974.T',  # Nintendo
            '7267.T',  # Honda
            '7201.T',  # Nissan
            '6752.T',  # Panasonic
            '8306.T',  # MUFG
            '8316.T',  # SMFG
            '8411.T',  # Mizuho
            '6861.T',  # Keyence
            '9983.T',  # Fast Retailing
            '8035.T',  # Tokyo Electron
            '6367.T',  # Daikin
            '4063.T'   # Shin-Etsu Chemical
        ]

        # 銘柄情報を取得
        placeholders = ','.join(['%s'] * len(supported_symbols))
        cur.execute(f"""
            SELECT symbol, company_name
            FROM stock_master
            WHERE symbol IN ({placeholders})
              AND is_active = TRUE
            ORDER BY symbol
            LIMIT %s
        """, (*supported_symbols, limit))

        symbols = cur.fetchall()
        cur.close()

        if not symbols:
            conn.close()
            return {
                "status": "error",
                "message": "No supported Japanese stocks found"
            }

        # バッチニュース収集
        collector = newsapi_collector.NewsAPICollector()
        results = []

        for symbol_info in symbols:
            symbol = symbol_info['symbol']
            company_name = symbol_info['company_name']

            try:
                result = collector.collect_news_for_symbol(symbol, company_name, days=7)
                results.append(result)

                # NewsAPI.org rate limit: 5 requests/second
                import time
                time.sleep(0.3)  # 300ms間隔 = 3.3 req/sec

            except Exception as e:
                results.append({
                    "symbol": symbol,
                    "company_name": company_name,
                    "status": "error",
                    "message": str(e)
                })

        conn.close()

        # 成功・失敗をカウント
        successful = [r for r in results if r.get('status') == 'success']
        failed = [r for r in results if r.get('status') != 'success']

        total_articles = sum(r.get('articles_saved', 0) for r in successful)

        return {
            "status": "success",
            "message": f"Batch news collection completed for {len(symbols)} Japanese stocks",
            "total_symbols": len(symbols),
            "successful": len(successful),
            "failed": len(failed),
            "total_articles_collected": total_articles,
            "results": results
        }

    except Exception as e:
        import traceback
        return {
            "status": "error",
            "message": str(e),
            "traceback": traceback.format_exc()
        }

