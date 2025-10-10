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

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8080))
    uvicorn.run(app, host="0.0.0.0", port=port)
