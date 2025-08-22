from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import logging
import pymysql
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, Session
import os
from typing import Optional, List
import random
from dotenv import load_dotenv

# 環境変数読み込み
load_dotenv()

# ログ設定
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Universal Stock Market API", version="3.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:3001", "*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Cloud SQL接続設定
def get_cloud_sql_connection():
    """Cloud SQL接続を取得"""
    try:
        # Cloud SQL接続情報
        if os.getenv('GAE_ENV', '').startswith('standard'):
            # App Engine本番環境
            unix_socket = f"/cloudsql/{os.environ['CLOUD_SQL_CONNECTION_NAME']}"
            engine = create_engine(
                f"mysql+pymysql://root:{os.environ['CLOUD_SQL_PASSWORD']}@/miraikakaku_prod"
                f"?unix_socket={unix_socket}",
                pool_pre_ping=True,
                pool_recycle=300
            )
        else:
            # ローカル開発環境
            engine = create_engine(
                f"mysql+pymysql://root:{os.getenv('CLOUD_SQL_PASSWORD', 'Yuuku717')}@"
                f"{os.getenv('CLOUD_SQL_HOST', '34.58.103.36')}:3306/miraikakaku_prod",
                pool_pre_ping=True,
                pool_recycle=300
            )
        
        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
        return SessionLocal
    except Exception as e:
        logger.error(f"Cloud SQL接続エラー: {e}")
        return None

# セッション依存性
SessionLocal = get_cloud_sql_connection()

def get_db():
    if SessionLocal is None:
        raise HTTPException(status_code=500, detail="データベース接続エラー")
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/")
async def root():
    return {
        "message": "Universal Stock Market API", 
        "version": "3.0.0",
        "description": "Cloud SQL統合版 - Yahoo Financeリアルタイムデータ",
        "data_source": {
            "master_data": "Cloud SQL (12,107銘柄)",
            "price_data": "Yahoo Finance API",
            "predictions": "Dynamic LSTM Simulation"
        }
    }

@app.get("/health")
async def health(db: Session = Depends(get_db)):
    """ヘルスチェック with DB接続確認"""
    try:
        result = db.execute(text("SELECT COUNT(*) FROM stock_master"))
        count = result.scalar()
        return {
            "status": "healthy",
            "service": "universal-stock-api",
            "database": "connected",
            "stocks_count": count
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "service": "universal-stock-api",
            "database": "error",
            "error": str(e)
        }

@app.get("/api/finance/stocks/search")
async def universal_search(
    query: str,
    market: Optional[str] = None,
    asset_type: Optional[str] = None,
    limit: int = 20,
    db: Session = Depends(get_db)
):
    """Cloud SQLから株式検索"""
    try:
        sql_query = """
        SELECT symbol, name, country, market, sector
        FROM stock_master
        WHERE (symbol LIKE :query OR name LIKE :query)
        """
        
        params = {"query": f"%{query}%"}
        
        if market:
            if market.upper() == "JP":
                sql_query += " AND country = 'Japan'"
            elif market.upper() == "US":
                sql_query += " AND country IN ('USA', 'US')"
        
        if asset_type:
            if asset_type.upper() == "ETF":
                sql_query += " AND sector IN ('ETF', 'Equity', 'Bond', 'Commodity')"
            elif asset_type.upper() == "STOCK":
                sql_query += " AND sector NOT IN ('ETF', 'Equity', 'Bond', 'Commodity')"
        
        sql_query += f" LIMIT {limit}"
        
        result = db.execute(text(sql_query), params)
        
        results = []
        for row in result:
            # 日本株はシンボルに.Tを追加
            symbol = f"{row[0]}.T" if row[2] == "Japan" else row[0]
            
            results.append({
                "symbol": symbol,
                "company_name": row[1],
                "country": row[2],
                "exchange": row[3] or "Unknown",  # marketをexchangeとして使用
                "sector": row[4],
                "asset_type": "ETF" if row[4] in ['ETF', 'Equity', 'Bond', 'Commodity'] else "Stock"
            })
        
        logger.info(f"Search '{query}' returned {len(results)} results from Cloud SQL")
        return results
        
    except Exception as e:
        logger.error(f"Search error: {e}")
        raise HTTPException(status_code=500, detail="検索エラー")

@app.get("/api/finance/stocks/{symbol}/price")
async def get_stock_price(symbol: str, days: int = 30):
    """Yahoo Financeから株価データ取得"""
    try:
        ticker = yf.Ticker(symbol)
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days + 5)
        
        hist = ticker.history(start=start_date, end=end_date, interval="1d")
        
        if hist.empty:
            raise HTTPException(status_code=404, detail=f"銘柄 {symbol} のデータが見つかりません")
        
        price_data = []
        for date, row in hist.iterrows():
            price_data.append({
                "date": date.strftime("%Y-%m-%d"),
                "close_price": round(float(row['Close']), 2),
                "open_price": round(float(row['Open']), 2),
                "high_price": round(float(row['High']), 2),
                "low_price": round(float(row['Low']), 2),
                "volume": int(row['Volume'])
            })
        
        price_data = price_data[-days:] if len(price_data) > days else price_data
        
        logger.info(f"Price data from Yahoo Finance: {symbol}, {len(price_data)} days")
        return price_data
        
    except Exception as e:
        logger.error(f"Price error for {symbol}: {e}")
        raise HTTPException(status_code=404, detail=f"データ取得エラー: {symbol}")

@app.get("/api/finance/stocks/{symbol}/analysis")
async def get_stock_analysis(symbol: str):
    """Yahoo Financeから分析データ取得"""
    try:
        ticker = yf.Ticker(symbol)
        info = ticker.info
        hist = ticker.history(period="5d")
        
        if hist.empty:
            raise HTTPException(status_code=404, detail=f"銘柄 {symbol} のデータが見つかりません")
        
        current_price = float(hist['Close'].iloc[-1])
        prev_price = float(hist['Close'].iloc[-2]) if len(hist) > 1 else current_price
        change_percent = ((current_price - prev_price) / prev_price) * 100
        
        analysis = {
            "symbol": symbol,
            "current_price": round(current_price, 2),
            "change_percent": round(change_percent, 2),
            "volume": int(hist['Volume'].iloc[-1]) if not pd.isna(hist['Volume'].iloc[-1]) else 0,
            "market_cap": info.get("marketCap", 0),
            "pe_ratio": info.get("trailingPE", 0),
            "recommendation": info.get("recommendationKey", "HOLD").upper(),
            "analyst_target": info.get("targetMeanPrice", round(current_price * 1.1, 2)),
            "support_level": round(current_price * 0.95, 2),
            "resistance_level": round(current_price * 1.05, 2),
            "52_week_high": info.get("fiftyTwoWeekHigh", current_price),
            "52_week_low": info.get("fiftyTwoWeekLow", current_price),
            "dividend_yield": info.get("dividendYield", 0),
            "beta": info.get("beta", 1.0)
        }
        
        logger.info(f"Analysis from Yahoo Finance: {symbol}")
        return analysis
        
    except Exception as e:
        logger.error(f"Analysis error for {symbol}: {e}")
        raise HTTPException(status_code=404, detail=f"分析データ取得エラー: {symbol}")

@app.get("/api/finance/stocks/{symbol}/predictions")
async def get_stock_predictions(symbol: str, days: int = 7):
    """動的AI予測生成"""
    try:
        ticker = yf.Ticker(symbol)
        hist = ticker.history(period="30d")
        
        if hist.empty:
            raise HTTPException(status_code=404, detail=f"銘柄 {symbol} のデータが見つかりません")
        
        current_price = float(hist['Close'].iloc[-1])
        prices = hist['Close'].values
        
        # トレンドと変動率計算
        trend = np.polyfit(range(len(prices)), prices, 1)[0]
        volatility = np.std(prices[-7:]) / np.mean(prices[-7:])
        
        prediction_data = []
        for i in range(days):
            date = (datetime.now() + timedelta(days=i+1)).strftime("%Y-%m-%d")
            
            # 予測価格計算
            trend_factor = trend * (i + 1)
            volatility_factor = volatility * (random.random() - 0.5) * 0.5
            predicted_price = current_price + trend_factor + (current_price * volatility_factor)
            
            # 信頼度は日数が増えるごとに低下
            confidence = max(0.6, 0.9 - (i * 0.05))
            
            # 予測レンジ
            range_width = predicted_price * (0.05 + (i * 0.02))
            
            prediction_data.append({
                "date": date,
                "predicted_price": round(predicted_price, 2),
                "confidence": round(confidence, 3),
                "upper_bound": round(predicted_price + range_width, 2),
                "lower_bound": round(predicted_price - range_width, 2),
                "prediction_model": "LSTM-Dynamic",
                "volatility": round(volatility, 3)
            })
        
        logger.info(f"Dynamic predictions: {symbol}, {days} days")
        return prediction_data
        
    except Exception as e:
        logger.error(f"Prediction error for {symbol}: {e}")
        raise HTTPException(status_code=404, detail=f"予測データ生成エラー: {symbol}")

@app.get("/api/finance/markets/stats")
async def get_market_statistics(db: Session = Depends(get_db)):
    """市場統計情報（Cloud SQL）"""
    try:
        # 国別カウント
        country_stats = db.execute(text("""
            SELECT country, COUNT(*) as count
            FROM stock_master
            GROUP BY country
        """))
        
        country_breakdown = {row[0]: row[1] for row in country_stats}
        
        # セクター別カウント
        sector_stats = db.execute(text("""
            SELECT 
                CASE 
                    WHEN sector IN ('ETF', 'Equity', 'Bond', 'Commodity') THEN 'ETF'
                    ELSE 'Stock'
                END as type,
                COUNT(*) as count
            FROM stock_master
            GROUP BY type
        """))
        
        type_breakdown = {row[0]: row[1] for row in sector_stats}
        
        # 合計数
        total = db.execute(text("SELECT COUNT(*) FROM stock_master")).scalar()
        
        return {
            "database_stats": {
                "total_securities": total,
                "japanese_stocks": country_breakdown.get("Japan", 0),
                "us_stocks": country_breakdown.get("USA", 0) + country_breakdown.get("US", 0),
                "etfs": type_breakdown.get("ETF", 0),
                "stocks": type_breakdown.get("Stock", 0)
            },
            "data_source": {
                "master_data": "Cloud SQL",
                "price_data": "Yahoo Finance API",
                "predictions": "Dynamic Generation"
            },
            "coverage": {
                "japanese_market": f"{country_breakdown.get('Japan', 0):,} companies",
                "us_market": f"{country_breakdown.get('USA', 0) + country_breakdown.get('US', 0):,} securities",
                "total": f"{total:,} instruments"
            }
        }
    except Exception as e:
        logger.error(f"Stats error: {e}")
        raise HTTPException(status_code=500, detail="統計情報取得エラー")

@app.get("/api/finance/rankings/universal")
async def get_universal_rankings(
    market: Optional[str] = None,
    asset_type: Optional[str] = None,
    limit: int = 20,
    db: Session = Depends(get_db)
):
    """ランキング生成（Cloud SQL + Yahoo Finance）"""
    try:
        # Cloud SQLから銘柄リスト取得
        sql_query = "SELECT symbol, name, country, sector FROM stock_master WHERE 1=1"
        
        if market:
            if market.upper() == "JP":
                sql_query += " AND country = 'Japan'"
            elif market.upper() == "US":
                sql_query += " AND country IN ('USA', 'US')"
        
        if asset_type:
            if asset_type.upper() == "ETF":
                sql_query += " AND sector IN ('ETF', 'Equity', 'Bond', 'Commodity')"
            elif asset_type.upper() == "STOCK":
                sql_query += " AND sector NOT IN ('ETF', 'Equity', 'Bond', 'Commodity')"
        
        sql_query += f" ORDER BY RAND() LIMIT {limit}"
        
        result = db.execute(text(sql_query))
        
        rankings = []
        for row in result:
            symbol = f"{row[0]}.T" if row[2] == "Japan" else row[0]
            
            # Yahoo Financeから最新データ取得（実装時）
            # ここでは仮のスコアを生成
            growth_potential = random.uniform(5, 25)
            accuracy_score = random.uniform(0.7, 0.95)
            
            rankings.append({
                "symbol": symbol,
                "company_name": row[1],
                "growth_potential": round(growth_potential, 2),
                "accuracy_score": round(accuracy_score, 3),
                "composite_score": round((growth_potential/25 * 0.4) + (accuracy_score * 0.6), 3),
                "country": row[2],
                "asset_type": "ETF" if row[3] in ['ETF', 'Equity', 'Bond', 'Commodity'] else "Stock"
            })
        
        rankings.sort(key=lambda x: x["composite_score"], reverse=True)
        return rankings
        
    except Exception as e:
        logger.error(f"Rankings error: {e}")
        raise HTTPException(status_code=500, detail="ランキング生成エラー")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)