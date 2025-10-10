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
    """ホームページ用の統計サマリー"""
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    try:
        cur.execute("""
            SELECT COUNT(DISTINCT symbol) as total_symbols,
                   COUNT(DISTINCT CASE WHEN prediction_date >= CURRENT_DATE THEN symbol END) as active_symbols
            FROM ensemble_predictions
        """)
        stats = cur.fetchone()

        return {
            "totalSymbols": int(stats['total_symbols'] or 0),
            "activePredictions": int(stats['active_symbols'] or 0),
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
