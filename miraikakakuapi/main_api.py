#!/usr/bin/env python3
"""
PostgreSQL専用統合API
PostgreSQL-Only Unified API

Enforces PostgreSQL architecture consistency as required by user
バッチで銘柄と価格と予測を行ってDBに保存、APIでDBから値を取得、フロントがAPIを叩いて描画する
"""
from fastapi import FastAPI, HTTPException, Query, Depends, WebSocket, Header
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import uvicorn
import logging
from datetime import datetime, timedelta
import os

# Import PostgreSQL-only database components
from functions.database.cloud_sql import CloudSQLManager, StockDataRepository, get_db
from sqlalchemy.orm import Session
from core.database_monitor import get_database_health, get_monitoring_summary
from core.performance_monitor import (
    performance_monitor, start_performance_monitoring,
    get_current_performance, get_performance_analytics, get_endpoint_performance
)
from core.notification_system import (
    notification_manager, handle_websocket_notifications,
    send_system_alert, get_notification_stats
)
from core.prediction_accuracy_system import (
    get_accuracy_analytics, train_symbol_models
)
from core.auth_system import (
    auth_system, personalization_system, get_current_user,
    UserCreate, UserLogin, UserUpdate, UserResponse, WatchlistCreate, AlertCreate, AuthToken
)

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# FastAPI app setup
app = FastAPI(
    title="MiraiKakaku PostgreSQL API",
    description="PostgreSQL-only production API enforcing architecture consistency",
    version="4.0.0"
)

# HTTP Bearer セキュリティ
security = HTTPBearer()

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global database manager (PostgreSQL only)
db_manager = CloudSQLManager()

# Data models
class StockPriceResponse(BaseModel):
    symbol: str
    date: str
    open_price: float
    high_price: float
    low_price: float
    close_price: float
    volume: int
    created_at: str

class StockPredictionResponse(BaseModel):
    symbol: str
    prediction_date: str
    predicted_price: float
    confidence_score: float
    model_name: str
    created_at: str

class HealthResponse(BaseModel):
    status: str
    version: str
    timestamp: str
    database_connected: bool
    database_type: str = "PostgreSQL"

class SystemStatusResponse(BaseModel):
    api_status: str
    database_status: str
    database_type: str = "PostgreSQL"
    total_stocks: int
    total_prices: int
    total_predictions: int
    last_updated: str

@app.get("/api/health", response_model=HealthResponse)
async def health_check():
    """ヘルスチェック (PostgreSQL接続状態確認)"""
    return HealthResponse(
        status="healthy" if db_manager.is_connected() else "unhealthy",
        version="3.0.0",
        timestamp=datetime.utcnow().isoformat(),
        database_connected=db_manager.is_connected(),
        database_type="PostgreSQL"
    )

@app.get("/api/database/health")
async def database_health():
    """データベース健全性チェック（監視強化版）"""
    health = get_database_health()
    return {
        "status": health.status,
        "connection_status": health.connection_status,
        "issues": health.issues,
        "recommendations": health.recommendations,
        "metrics": {
            "active_connections": health.metrics.active_connections if health.metrics else 0,
            "total_connections": health.metrics.total_connections if health.metrics else 0,
            "avg_query_duration": health.metrics.query_duration_avg if health.metrics else 0,
            "cpu_usage": health.metrics.cpu_usage if health.metrics else 0,
            "memory_usage": health.metrics.memory_usage if health.metrics else 0,
            "timestamp": health.metrics.timestamp.isoformat() if health.metrics else None
        } if health.metrics else None
    }

@app.get("/api/database/monitoring/summary")
async def monitoring_summary(hours: int = 24):
    """データベース監視サマリー"""
    return get_monitoring_summary(hours)

@app.get("/api/performance/current")
async def current_performance():
    """現在のパフォーマンス状況"""
    metrics = get_current_performance()
    if not metrics:
        return {"status": "no_data", "message": "Performance monitoring not started"}
    return metrics

@app.get("/api/performance/analytics")
async def performance_analytics(hours: int = 24):
    """パフォーマンス分析（指定時間内）"""
    return get_performance_analytics(hours)

@app.get("/api/performance/endpoints")
async def endpoint_performance(hours: int = 24):
    """エンドポイント別パフォーマンス分析"""
    return get_endpoint_performance(hours)

@app.get("/api/performance/export")
async def export_performance_data():
    """パフォーマンスデータをエクスポート"""
    try:
        filename = performance_monitor.export_metrics()
        return {
            "status": "success",
            "filename": filename,
            "message": "Performance metrics exported successfully"
        }
    except Exception as e:
        return {
            "status": "error",
            "message": f"Failed to export metrics: {e}"
        }

@app.websocket("/ws/notifications")
async def websocket_notifications(websocket: WebSocket):
    """WebSocket通知エンドポイント"""
    await handle_websocket_notifications(websocket)

@app.get("/api/notifications/active")
async def get_active_notifications():
    """アクティブな通知を取得"""
    return {
        "notifications": notification_manager.get_active_notifications(),
        "stats": get_notification_stats()
    }

@app.post("/api/notifications/test")
async def send_test_notification():
    """テスト通知を送信"""
    await send_system_alert(
        "テスト通知",
        "これはテスト通知です。システムが正常に動作しています。",
        data={"test": True}
    )
    return {"status": "success", "message": "Test notification sent"}

@app.get("/api/notifications/stats")
async def get_notification_statistics():
    """通知統計を取得"""
    return get_notification_stats()

@app.get("/api/ai/accuracy/analytics")
async def get_ai_accuracy_analytics(days: int = Query(default=30, ge=1, le=365)):
    """AI予測精度分析を取得"""
    return get_accuracy_analytics(days)

@app.post("/api/ai/models/train/{symbol}")
async def train_ai_models(symbol: str):
    """指定銘柄のAIモデルを学習"""
    return train_symbol_models(symbol)

@app.get("/api/ai/models/status")
async def get_ai_models_status():
    """AIモデルの状態を取得"""
    from core.prediction_accuracy_system import prediction_accuracy_system
    return {
        "loaded_models": len(prediction_accuracy_system.models),
        "available_model_types": list(prediction_accuracy_system.model_configs.keys()),
        "feature_columns": prediction_accuracy_system.feature_columns,
        "last_updated": datetime.utcnow().isoformat()
    }

# ===== 認証・ユーザー管理エンドポイント =====

def get_current_user_dependency(credentials: HTTPAuthorizationCredentials = Depends(security), db: Session = Depends(get_db)):
    """現在のユーザーを取得する依存関数"""
    token = credentials.credentials
    user = get_current_user(token, db)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid authentication credentials")
    return user

@app.post("/api/auth/register", response_model=dict)
async def register_user(user_data: UserCreate, db: Session = Depends(get_db)):
    """ユーザー登録"""
    try:
        user = auth_system.register_user(user_data, db)

        # JWTトークンを生成
        access_token = auth_system.create_access_token(data={"sub": str(user.id)})

        return {
            "access_token": access_token,
            "token_type": "bearer",
            "user": {
                "id": user.id,
                "email": user.email,
                "username": user.username,
                "full_name": user.full_name,
                "is_premium": user.is_premium
            }
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Registration error: {e}")
        raise HTTPException(status_code=500, detail="Registration failed")

@app.post("/api/auth/login", response_model=dict)
async def login_user(login_data: UserLogin, db: Session = Depends(get_db)):
    """ユーザーログイン"""
    try:
        user = auth_system.authenticate_user(login_data, db)
        if not user:
            raise HTTPException(status_code=401, detail="Invalid email or password")

        # JWTトークンを生成
        access_token = auth_system.create_access_token(data={"sub": str(user.id)})

        return {
            "access_token": access_token,
            "token_type": "bearer",
            "user": {
                "id": user.id,
                "email": user.email,
                "username": user.username,
                "full_name": user.full_name,
                "is_premium": user.is_premium,
                "last_login": user.last_login.isoformat() if user.last_login else None
            }
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Login error: {e}")
        raise HTTPException(status_code=500, detail="Login failed")

@app.get("/api/auth/me", response_model=dict)
async def get_current_user_info(current_user = Depends(get_current_user_dependency)):
    """現在のユーザー情報を取得"""
    return {
        "id": current_user.id,
        "email": current_user.email,
        "username": current_user.username,
        "full_name": current_user.full_name,
        "bio": current_user.bio,
        "investment_experience": current_user.investment_experience,
        "risk_tolerance": current_user.risk_tolerance,
        "investment_goals": current_user.investment_goals,
        "preferred_sectors": current_user.preferred_sectors,
        "is_premium": current_user.is_premium,
        "created_at": current_user.created_at.isoformat(),
        "last_login": current_user.last_login.isoformat() if current_user.last_login else None
    }

@app.put("/api/auth/profile", response_model=dict)
async def update_user_profile(
    profile_data: UserUpdate,
    current_user = Depends(get_current_user_dependency),
    db: Session = Depends(get_db)
):
    """ユーザープロファイルを更新"""
    try:
        updated_user = auth_system.update_user_profile(current_user.id, profile_data, db)
        if not updated_user:
            raise HTTPException(status_code=404, detail="User not found")

        return {
            "message": "Profile updated successfully",
            "user": {
                "id": updated_user.id,
                "email": updated_user.email,
                "username": updated_user.username,
                "full_name": updated_user.full_name,
                "bio": updated_user.bio,
                "investment_experience": updated_user.investment_experience,
                "risk_tolerance": updated_user.risk_tolerance,
                "investment_goals": updated_user.investment_goals,
                "preferred_sectors": updated_user.preferred_sectors
            }
        }
    except Exception as e:
        logger.error(f"Profile update error: {e}")
        raise HTTPException(status_code=500, detail="Profile update failed")

# ===== 個人化機能エンドポイント =====

@app.post("/api/user/watchlists", response_model=dict)
async def create_watchlist(
    watchlist_data: WatchlistCreate,
    current_user = Depends(get_current_user_dependency),
    db: Session = Depends(get_db)
):
    """ウォッチリストを作成"""
    try:
        watchlist = personalization_system.create_watchlist(current_user.id, watchlist_data, db)
        return {
            "id": watchlist.id,
            "name": watchlist.name,
            "description": watchlist.description,
            "symbols": watchlist.symbols,
            "is_public": watchlist.is_public,
            "created_at": watchlist.created_at.isoformat()
        }
    except Exception as e:
        logger.error(f"Watchlist creation error: {e}")
        raise HTTPException(status_code=500, detail="Watchlist creation failed")

@app.get("/api/user/watchlists", response_model=List[dict])
async def get_user_watchlists(
    current_user = Depends(get_current_user_dependency),
    db: Session = Depends(get_db)
):
    """ユーザーのウォッチリストを取得"""
    try:
        watchlists = personalization_system.get_user_watchlists(current_user.id, db)
        return [
            {
                "id": wl.id,
                "name": wl.name,
                "description": wl.description,
                "symbols": wl.symbols,
                "is_public": wl.is_public,
                "created_at": wl.created_at.isoformat(),
                "updated_at": wl.updated_at.isoformat()
            }
            for wl in watchlists
        ]
    except Exception as e:
        logger.error(f"Watchlists retrieval error: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve watchlists")

@app.post("/api/user/alerts", response_model=dict)
async def create_price_alert(
    alert_data: AlertCreate,
    current_user = Depends(get_current_user_dependency),
    db: Session = Depends(get_db)
):
    """価格アラートを作成"""
    try:
        alert = personalization_system.create_price_alert(current_user.id, alert_data, db)
        return {
            "id": alert.id,
            "symbol": alert.symbol,
            "alert_type": alert.alert_type,
            "target_price": alert.target_price,
            "percentage_change": alert.percentage_change,
            "is_active": alert.is_active,
            "created_at": alert.created_at.isoformat()
        }
    except Exception as e:
        logger.error(f"Alert creation error: {e}")
        raise HTTPException(status_code=500, detail="Alert creation failed")

@app.get("/api/user/alerts", response_model=List[dict])
async def get_user_alerts(
    current_user = Depends(get_current_user_dependency),
    db: Session = Depends(get_db)
):
    """ユーザーのアラートを取得"""
    try:
        alerts = personalization_system.get_user_alerts(current_user.id, db)
        return [
            {
                "id": alert.id,
                "symbol": alert.symbol,
                "alert_type": alert.alert_type,
                "target_price": alert.target_price,
                "percentage_change": alert.percentage_change,
                "is_active": alert.is_active,
                "created_at": alert.created_at.isoformat(),
                "triggered_at": alert.triggered_at.isoformat() if alert.triggered_at else None
            }
            for alert in alerts
        ]
    except Exception as e:
        logger.error(f"Alerts retrieval error: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve alerts")

@app.get("/api/user/recommendations", response_model=dict)
async def get_personalized_recommendations(
    current_user = Depends(get_current_user_dependency),
    db: Session = Depends(get_db)
):
    """個人化された推奨情報を取得"""
    try:
        recommendations = personalization_system.get_personalized_recommendations(current_user.id, db)
        return recommendations
    except Exception as e:
        logger.error(f"Recommendations error: {e}")
        raise HTTPException(status_code=500, detail="Failed to get recommendations")

@app.get("/api/system/status", response_model=SystemStatusResponse)
async def system_status(db: Session = Depends(get_db)):
    """システム状態取得 (PostgreSQL専用)"""
    try:
        # Get counts from PostgreSQL tables using raw SQL
        from sqlalchemy import text

        total_stocks_result = db.execute(text("SELECT COUNT(*) FROM stock_master WHERE is_active = true"))
        total_stocks = total_stocks_result.scalar() or 0

        total_prices_result = db.execute(text("SELECT COUNT(*) FROM stock_prices"))
        total_prices = total_prices_result.scalar() or 0

        total_predictions_result = db.execute(text("SELECT COUNT(*) FROM stock_predictions WHERE is_active = true"))
        total_predictions = total_predictions_result.scalar() or 0

        return SystemStatusResponse(
            api_status="operational",
            database_status="connected",
            database_type="PostgreSQL",
            total_stocks=total_stocks,
            total_prices=total_prices,
            total_predictions=total_predictions,
            last_updated=datetime.utcnow().isoformat()
        )
    except Exception as e:
        logger.error(f"System status error: {e}")
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

@app.get("/api/finance/stocks/{symbol}/price")
async def get_stock_prices(
    symbol: str,
    days: int = Query(default=730, ge=1, le=2000),
    db: Session = Depends(get_db)
):
    """株価データ取得 (PostgreSQL専用)"""
    try:
        from sqlalchemy import text

        # Calculate date range
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)

        # Query PostgreSQL for price data using raw SQL
        query = text("""
            SELECT id, symbol, date, open_price, high_price, low_price, close_price, volume, created_at
            FROM stock_prices
            WHERE symbol = :symbol
            AND date >= :start_date
            AND date <= :end_date
            ORDER BY date ASC
        """)

        result = db.execute(query, {
            "symbol": symbol,
            "start_date": start_date,
            "end_date": end_date
        })

        prices = result.fetchall()

        if not prices:
            raise HTTPException(status_code=404, detail=f"No price data found for {symbol}")

        # Convert to response format
        price_data = []
        for price in prices:
            price_data.append({
                "id": f"price_{price.id}",
                "symbol": price.symbol,
                "date": price.date.strftime("%Y-%m-%d"),
                "open_price": float(price.open_price) if price.open_price else 0.0,
                "high_price": float(price.high_price) if price.high_price else 0.0,
                "low_price": float(price.low_price) if price.low_price else 0.0,
                "close_price": float(price.close_price),
                "volume": price.volume or 0,
                "created_at": price.created_at.isoformat() if price.created_at else ""
            })

        logger.info(f"Retrieved {len(price_data)} price records for {symbol} from PostgreSQL")
        return price_data

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving prices for {symbol}: {e}")
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

@app.get("/api/finance/stocks/{symbol}/predictions")
async def get_stock_predictions(
    symbol: str,
    days: int = Query(default=180, ge=1, le=365),
    db: Session = Depends(get_db)
):
    """株価予測データ取得 (PostgreSQL専用)"""
    try:
        # Calculate date range for future predictions
        start_date = datetime.now()
        end_date = start_date + timedelta(days=days)

        # Query PostgreSQL for prediction data
        predictions = db.query(StockPredictions).filter(
            StockPredictions.symbol == symbol,
            StockPredictions.target_date >= start_date,
            StockPredictions.target_date <= end_date,
            StockPredictions.is_active == True
        ).order_by(StockPredictions.target_date.asc()).all()

        if not predictions:
            raise HTTPException(status_code=404, detail=f"No predictions found for {symbol}")

        # Convert to response format
        prediction_data = []
        for pred in predictions:
            prediction_data.append({
                "id": f"pred_{pred.id}",
                "symbol": pred.symbol,
                "prediction_date": pred.target_date.strftime("%Y-%m-%d"),
                "predicted_price": float(pred.predicted_price),
                "confidence_score": float(pred.confidence_score) if pred.confidence_score else 0.0,
                "model_name": pred.model_name or "Unknown",
                "created_at": pred.created_at.isoformat() if pred.created_at else ""
            })

        logger.info(f"Retrieved {len(prediction_data)} predictions for {symbol} from PostgreSQL")
        return prediction_data

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving predictions for {symbol}: {e}")
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

@app.get("/api/finance/stocks/{symbol}/predictions/history")
async def get_historical_predictions(
    symbol: str,
    days: int = Query(default=730, ge=1, le=2000),
    db: Session = Depends(get_db)
):
    """過去予測データ取得 (PostgreSQL専用)"""
    try:
        # Calculate date range for historical predictions
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)

        # Query PostgreSQL for historical predictions
        predictions = db.query(StockPredictions).filter(
            StockPredictions.symbol == symbol,
            StockPredictions.target_date >= start_date,
            StockPredictions.target_date <= end_date,
            StockPredictions.actual_price.isnot(None)  # Only predictions with actual outcomes
        ).order_by(StockPredictions.target_date.asc()).all()

        if not predictions:
            logger.info(f"No historical predictions found for {symbol}")
            return {"historical_predictions": []}

        # Convert to response format
        historical_data = []
        for pred in predictions:
            historical_data.append({
                "target_date": pred.target_date.strftime("%Y-%m-%d"),
                "predicted_price": float(pred.predicted_price),
                "actual_price": float(pred.actual_price),
                "confidence_score": float(pred.confidence_score) if pred.confidence_score else 0.0,
                "model_name": pred.model_name or "Unknown",
                "accuracy_score": float(pred.accuracy_score) if pred.accuracy_score else 0.0
            })

        logger.info(f"Retrieved {len(historical_data)} historical predictions for {symbol} from PostgreSQL")
        return {"historical_predictions": historical_data}

    except Exception as e:
        logger.error(f"Error retrieving historical predictions for {symbol}: {e}")
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

@app.get("/api/stocks/search")
async def search_stocks(
    q: str = Query(..., min_length=1),
    limit: int = Query(default=10, ge=1, le=50),
    db: Session = Depends(get_db)
):
    """株式検索 (PostgreSQL専用)"""
    try:
        # Search PostgreSQL for matching stocks
        stocks = db.query(StockMaster).filter(
            (StockMaster.symbol.ilike(f"%{q}%")) |
            (StockMaster.name.ilike(f"%{q}%")),
            StockMaster.is_active == True
        ).limit(limit).all()

        # Convert to response format
        results = []
        for stock in stocks:
            results.append({
                "symbol": stock.symbol,
                "name": stock.name,
                "sector": stock.sector,
                "market": stock.market,
                "country": stock.country,
                "currency": stock.currency
            })

        return {
            "query": q,
            "limit": limit,
            "results_count": len(results),
            "results": results,
            "status": "success"
        }

    except Exception as e:
        logger.error(f"Error searching stocks with query '{q}': {e}")
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

@app.on_event("startup")
async def startup_event():
    """起動時イベント (PostgreSQL接続確認)"""
    if not db_manager.is_connected():
        logger.error("PostgreSQL connection failed on startup!")
        raise RuntimeError(f"Database connection failed: {db_manager.get_connection_error()}")

    # パフォーマンス監視を開始
    start_performance_monitoring()
    logger.info("PostgreSQL-only API started successfully with performance monitoring")

@app.on_event("shutdown")
async def shutdown_event():
    """終了時イベント"""
    from core.performance_monitor import stop_performance_monitoring
    stop_performance_monitoring()
    db_manager.close_connection()
    logger.info("PostgreSQL-only API shutdown complete")

def main():
    """メイン実行関数"""
    port = int(os.getenv("PORT", 8084))
    logger.info(f"Starting PostgreSQL-only MiraiKakaku API on port {port}")

    # Verify PostgreSQL connection before starting
    if not db_manager.is_connected():
        logger.error("Cannot start API: PostgreSQL connection failed!")
        logger.error(f"Connection error: {db_manager.get_connection_error()}")
        return

    uvicorn.run(
        "postgresql_only_api:app",
        host="0.0.0.0",
        port=port,
        reload=False,
        log_level="info"
    )

if __name__ == "__main__":
    main()