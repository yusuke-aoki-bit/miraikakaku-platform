#!/usr/bin/env python3
"""
最小限のAPIサーバー - UI/UXテスト用
本番データベースからリアルデータを取得
"""
from fastapi import FastAPI, HTTPException, Query, Depends
from fastapi.middleware.cors import CORSMiddleware
import pymysql
import uvicorn
import os
from dotenv import load_dotenv
from typing import List, Optional
from datetime import datetime, timedelta
import json

load_dotenv()

app = FastAPI(
    title="Miraikakaku Minimal API",
    description="金融データ取得API",
    version="1.0.0"
)

# CORS設定
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:3001", 
        "http://localhost:3002",
        "http://localhost:3003",
        "http://localhost:3004",
        "http://localhost:8080"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# データベース設定
DB_CONFIG = {
    'host': '34.58.103.36',
    'user': 'miraikakaku-user',
    'password': 'miraikakaku-secure-pass-2024',
    'database': 'miraikakaku'
}

def get_db_connection():
    """データベース接続を取得"""
    return pymysql.connect(**DB_CONFIG)

@app.get("/")
async def root():
    return {"message": "Miraikakaku Minimal API Server", "version": "1.0.0"}

@app.get("/health")
async def health_check():
    try:
        connection = get_db_connection()
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
            result = cursor.fetchone()
        connection.close()
        
        return {
            "status": "healthy",
            "service": "miraikakaku-minimal-api",
            "database": "connected",
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "service": "miraikakaku-minimal-api", 
            "database": "disconnected",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }

@app.get("/api/finance/rankings/growth-potential")
async def get_growth_potential_rankings(limit: int = Query(10, ge=1, le=50)):
    """成長ポテンシャルランキング - 本番データ"""
    connection = get_db_connection()
    try:
        with connection.cursor(pymysql.cursors.DictCursor) as cursor:
            # 文字コード問題を回避するため、バイナリ比較を使用
            query = """
            SELECT DISTINCT
                sm.symbol,
                sm.name as company_name,
                ph.close_price as current_price,
                sp.predicted_price,
                sp.confidence_score as confidence,
                ((sp.predicted_price - ph.close_price) / ph.close_price * 100) as growth_potential,
                COUNT(sp.id) as prediction_count
            FROM stock_master sm
            JOIN stock_price_history ph ON BINARY sm.symbol = BINARY ph.symbol
            JOIN stock_predictions sp ON BINARY sm.symbol = BINARY sp.symbol
            WHERE sm.is_active = 1 
            AND sp.is_active = 1
            AND ph.date >= DATE_SUB(CURDATE(), INTERVAL 7 DAY)
            AND sp.prediction_date >= CURDATE()
            GROUP BY sm.symbol, sm.name, ph.close_price, sp.predicted_price, sp.confidence_score
            HAVING growth_potential IS NOT NULL
            ORDER BY growth_potential DESC
            LIMIT %s
            """
            
            cursor.execute(query, (limit,))
            results = cursor.fetchall()
            
            return results
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"データ取得エラー: {str(e)}")
    finally:
        connection.close()

@app.get("/api/finance/rankings/composite")
async def get_composite_rankings(limit: int = Query(10, ge=1, le=50)):
    """総合ランキング - 本番データ"""
    connection = get_db_connection()
    try:
        with connection.cursor(pymysql.cursors.DictCursor) as cursor:
            query = """
            SELECT DISTINCT
                sm.symbol,
                sm.name as company_name,
                ph.close_price as current_price,
                sp.predicted_price,
                sp.confidence_score as confidence,
                ((sp.predicted_price - ph.close_price) / ph.close_price * 100) as growth_potential,
                (sp.confidence_score * 0.5 + GREATEST(0, (sp.predicted_price - ph.close_price) / ph.close_price) * 0.5) * 100 as composite_score,
                COUNT(sp.id) as prediction_count
            FROM stock_master sm
            JOIN stock_price_history ph ON sm.symbol = ph.symbol
            JOIN stock_predictions sp ON sm.symbol = sp.symbol
            WHERE sm.is_active = 1 
            AND sp.is_active = 1
            AND ph.date = (
                SELECT MAX(date) 
                FROM stock_price_history ph2 
                WHERE ph2.symbol = sm.symbol
            )
            AND sp.prediction_date >= CURDATE()
            GROUP BY sm.symbol, sm.name, ph.close_price, sp.predicted_price, sp.confidence_score
            HAVING composite_score IS NOT NULL
            ORDER BY composite_score DESC
            LIMIT %s
            """
            
            cursor.execute(query, (limit,))
            results = cursor.fetchall()
            
            return results
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"データ取得エラー: {str(e)}")
    finally:
        connection.close()

@app.get("/api/finance/stocks/search")
async def search_stocks(
    query: str = Query(..., min_length=1, description="検索クエリ"),
    limit: int = Query(10, ge=1, le=100, description="結果数制限"),
    currency: str = Query(None, description="通貨フィルター (JPY/USD)")
):
    """株式検索 - 企業名・セクター・業界での曖昧検索対応"""
    connection = get_db_connection()
    try:
        with connection.cursor(pymysql.cursors.DictCursor) as cursor:
            # 検索クエリを準備
            search_query = f"%{query}%"
            search_query_upper = f"%{query.upper()}%"
            
            # 基本クエリ
            base_sql = """
            SELECT 
                symbol, 
                name as company_name, 
                exchange, 
                sector, 
                industry, 
                currency,
                CASE 
                    WHEN symbol = %s THEN 1
                    WHEN symbol LIKE %s THEN 2
                    WHEN name LIKE %s THEN 3
                    WHEN name LIKE %s THEN 4
                    WHEN sector LIKE %s THEN 5
                    WHEN industry LIKE %s THEN 6
                    ELSE 7
                END as relevance_score
            FROM stock_master 
            WHERE is_active = 1 
            AND (
                symbol LIKE %s 
                OR name LIKE %s 
                OR name LIKE %s
                OR sector LIKE %s 
                OR industry LIKE %s
            )
            """
            
            params = [
                query.upper(),  # 完全一致チェック用
                search_query_upper,  # シンボル部分一致
                search_query_upper,  # 企業名大文字部分一致
                search_query,  # 企業名小文字部分一致  
                search_query_upper,  # セクター検索
                search_query_upper,  # 業界検索
                search_query_upper,  # 実際の検索条件
                search_query_upper,  # 企業名大文字
                search_query,  # 企業名小文字
                search_query_upper,  # セクター
                search_query_upper   # 業界
            ]
            
            # 通貨フィルターを追加
            if currency:
                base_sql += " AND currency = %s"
                params.append(currency)
            
            # ソートとリミット
            base_sql += """
            ORDER BY 
                relevance_score,
                CASE WHEN currency = 'JPY' THEN 1 ELSE 2 END,
                CHAR_LENGTH(symbol),
                symbol
            LIMIT %s
            """
            params.append(limit)
            
            cursor.execute(base_sql, params)
            results = cursor.fetchall()
            
            return results
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"検索エラー: {str(e)}")
    finally:
        connection.close()

@app.get("/api/finance/stocks/sectors")
async def get_sectors():
    """セクター一覧取得"""
    connection = get_db_connection()
    try:
        with connection.cursor(pymysql.cursors.DictCursor) as cursor:
            cursor.execute("""
                SELECT 
                    sector,
                    COUNT(*) as company_count,
                    COUNT(CASE WHEN currency = 'JPY' THEN 1 END) as jpy_count,
                    COUNT(CASE WHEN currency = 'USD' THEN 1 END) as usd_count
                FROM stock_master 
                WHERE is_active = 1 
                AND sector IS NOT NULL 
                AND sector != '-'
                AND sector != ''
                GROUP BY sector 
                HAVING company_count >= 5
                ORDER BY company_count DESC
                LIMIT 50
            """)
            
            results = cursor.fetchall()
            return results
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"セクターデータ取得エラー: {str(e)}")
    finally:
        connection.close()

@app.get("/api/finance/stocks/sector/{sector_id}")
async def get_stocks_by_sector(
    sector_id: str,
    limit: int = Query(20, ge=1, le=100, description="結果数制限"),
    currency: str = Query("JPY", description="通貨フィルター")
):
    """セクター別銘柄取得"""
    connection = get_db_connection()
    try:
        with connection.cursor(pymysql.cursors.DictCursor) as cursor:
            cursor.execute("""
                SELECT 
                    symbol, 
                    name as company_name, 
                    sector, 
                    industry, 
                    exchange, 
                    currency
                FROM stock_master 
                WHERE is_active = 1 
                AND sector = %s
                AND currency = %s
                ORDER BY symbol
                LIMIT %s
            """, (sector_id, currency, limit))
            
            results = cursor.fetchall()
            return results
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"セクター別データ取得エラー: {str(e)}")
    finally:
        connection.close()

@app.get("/api/finance/stocks/{symbol}/price")
async def get_stock_price(
    symbol: str,
    days: int = Query(30, ge=1, le=365, description="取得日数")
):
    """株価履歴取得 - 本番データ"""
    connection = get_db_connection()
    try:
        with connection.cursor(pymysql.cursors.DictCursor) as cursor:
            start_date = datetime.now() - timedelta(days=days)
            
            query = """
            SELECT symbol, date, open_price, high_price, low_price, 
                   close_price, adjusted_close, volume, data_source
            FROM stock_price_history
            WHERE symbol = %s AND date >= %s
            ORDER BY date DESC
            LIMIT %s
            """
            
            cursor.execute(query, (symbol.upper(), start_date, days))
            results = cursor.fetchall()
            
            if not results:
                raise HTTPException(status_code=404, detail="株価データが見つかりません")
            
            return results
            
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"データ取得エラー: {str(e)}")
    finally:
        connection.close()

@app.get("/api/finance/stocks/{symbol}/predictions")
async def get_stock_predictions(
    symbol: str,
    model_type: Optional[str] = Query(None, description="モデルタイプフィルター"),
    days: int = Query(7, ge=1, le=30, description="予測期間")
):
    """株価予測取得 - 本番データ"""
    connection = get_db_connection()
    try:
        with connection.cursor(pymysql.cursors.DictCursor) as cursor:
            where_clause = "WHERE symbol = %s AND is_active = 1"
            params = [symbol.upper()]
            
            if model_type:
                where_clause += " AND model_type = %s"
                params.append(model_type)
            
            query = f"""
            SELECT symbol, prediction_date, predicted_price, 
                   predicted_change, predicted_change_percent, 
                   confidence_score, model_type, model_version,
                   prediction_horizon, is_active
            FROM stock_predictions
            {where_clause}
            ORDER BY prediction_date ASC
            LIMIT %s
            """
            
            params.append(days)
            cursor.execute(query, params)
            results = cursor.fetchall()
            
            return results
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"予測データ取得エラー: {str(e)}")
    finally:
        connection.close()

@app.get("/database/stats")
async def get_database_stats():
    """データベース統計情報"""
    connection = get_db_connection()
    try:
        with connection.cursor(pymysql.cursors.DictCursor) as cursor:
            stats = {}
            
            # 銘柄統計
            cursor.execute("SELECT COUNT(*) as total FROM stock_master WHERE is_active = 1")
            stats['total_stocks'] = cursor.fetchone()['total']
            
            cursor.execute('SELECT COUNT(*) as usd_stocks FROM stock_master WHERE currency = "USD" AND is_active = 1')
            stats['usd_stocks'] = cursor.fetchone()['usd_stocks']
            
            cursor.execute('SELECT COUNT(*) as jpy_stocks FROM stock_master WHERE currency = "JPY" AND is_active = 1')
            stats['jpy_stocks'] = cursor.fetchone()['jpy_stocks']
            
            # 価格データ統計
            cursor.execute("SELECT COUNT(*) as total FROM stock_price_history")
            stats['price_records'] = cursor.fetchone()['total']
            
            # 予測データ統計
            cursor.execute("SELECT COUNT(*) as total FROM stock_predictions WHERE is_active = 1")
            stats['active_predictions'] = cursor.fetchone()['total']
            
            # 最新の日付
            cursor.execute("SELECT MAX(date) as latest_price_date FROM stock_price_history")
            stats['latest_price_date'] = cursor.fetchone()['latest_price_date']
            
            cursor.execute("SELECT MAX(prediction_date) as latest_prediction_date FROM stock_predictions WHERE is_active = 1")
            stats['latest_prediction_date'] = cursor.fetchone()['latest_prediction_date']
            
            return stats
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"統計取得エラー: {str(e)}")
    finally:
        connection.close()

if __name__ == "__main__":
    uvicorn.run(
        "minimal_api:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )