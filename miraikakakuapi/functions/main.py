from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn
import os
import sys
from dotenv import load_dotenv

load_dotenv()

# Add shared directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'shared'))

# Import auth middleware (comment out for now to fix deployment)
# from middleware.auth_middleware import AuthMiddleware

app = FastAPI(
    title="Miraikakaku API",
    description="金融分析・株価予測API",
    version="1.0.0",
    openapi_url="/api/v1/openapi.json"
)

# CORS設定 - 本番環境用
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://miraikakaku-front-465603676610.us-central1.run.app",
        os.getenv("FRONTEND_URL", "https://miraikakaku-front-465603676610.us-central1.run.app"),
        # 開発時のみ有効（環境変数でコントロール）
        *([
            "http://localhost:3000",
            "http://localhost:3001", 
            "http://localhost:3002",
            "http://localhost:8080"
        ] if os.getenv("ENVIRONMENT") == "development" else [])
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)

# 認証ミドルウェア (一時的にコメントアウト)
# app.add_middleware(AuthMiddleware)

@app.on_event("startup")
async def startup_event():
    from database.database import init_database_async
    await init_database_async()

@app.get("/")
async def root():
    return {"message": "Miraikakaku API Server", "version": "1.0.0"}

@app.get("/health")
async def health_check():
    return {
        "status": "healthy", 
        "service": "miraikakaku-api",
        "environment": os.getenv("NODE_ENV", "development")
    }

@app.get("/api/finance/test/indices/{symbol}")
async def test_index_data(symbol: str, days: int = 30):
    """Test endpoint for major indices data"""
    import yfinance as yf
    import pandas as pd
    from datetime import datetime, timedelta
    
    try:
        # Major indices mapping
        INDICES = {
            "nikkei": "^N225",
            "topix": "^N225",  # Use Nikkei as TOPIX alternative for now
            "dow": "^DJI",
            "sp500": "^GSPC"
        }
        
        # Use mapped symbol or original
        yf_symbol = INDICES.get(symbol.lower(), symbol.upper())
        
        ticker = yf.Ticker(yf_symbol)
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        
        hist = ticker.history(start=start_date, end=end_date)
        
        if hist.empty:
            return {"error": f"No data found for {yf_symbol}"}
            
        data = []
        for date, row in hist.iterrows():
            data.append({
                "date": date.strftime("%Y-%m-%d"),
                "open": float(row['Open']),
                "high": float(row['High']),
                "low": float(row['Low']),
                "close": float(row['Close']),
                "volume": int(row['Volume']) if not pd.isna(row['Volume']) else 0
            })
            
        return {
            "symbol": yf_symbol,
            "name": symbol.upper(),
            "data": data,
            "count": len(data)
        }
        
    except Exception as e:
        return {"error": str(e)}

@app.get("/api/finance/test/indices/{symbol}/predictions")
async def test_index_predictions(symbol: str, days: int = 30):
    """Test endpoint for major indices predictions"""
    import yfinance as yf
    import pandas as pd
    import numpy as np
    from datetime import datetime, timedelta
    
    try:
        # Major indices mapping
        INDICES = {
            "nikkei": "^N225",
            "topix": "^N225",  # Use Nikkei as TOPIX alternative for now
            "dow": "^DJI",
            "sp500": "^GSPC"
        }
        
        # Use mapped symbol or original
        yf_symbol = INDICES.get(symbol.lower(), symbol.upper())
        
        ticker = yf.Ticker(yf_symbol)
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days*2)  # Get more data for prediction base
        
        hist = ticker.history(start=start_date, end=end_date)
        
        if hist.empty:
            return {"error": f"No data found for {yf_symbol}"}
        
        # Get actual prices
        actual_data = []
        for date, row in hist.tail(days).iterrows():
            actual_data.append({
                "date": date.strftime("%Y-%m-%d"),
                "value": float(row['Close']),
                "type": "actual"
            })
        
        # Generate mock historical predictions (shifted by 1-7 days from actual)
        historical_predictions = []
        for i, data_point in enumerate(actual_data):
            if i < 7:  # Only create historical predictions for first week
                predicted_value = data_point["value"] * (1 + np.random.normal(0, 0.02))  # ±2% variation
                historical_predictions.append({
                    "date": data_point["date"],
                    "value": round(float(predicted_value), 2),
                    "type": "historical_prediction",
                    "confidence": round(np.random.uniform(0.7, 0.95), 2)
                })
        
        # Generate future predictions
        future_predictions = []
        if actual_data:
            last_price = actual_data[-1]["value"]
            last_date = datetime.strptime(actual_data[-1]["date"], "%Y-%m-%d")
            
            for i in range(1, 8):  # 7 days of future predictions
                future_date = last_date + timedelta(days=i)
                # Mock trend with some randomness
                trend = np.random.normal(0.001, 0.01)  # Small upward trend with noise
                predicted_value = last_price * (1 + trend * i)
                
                future_predictions.append({
                    "date": future_date.strftime("%Y-%m-%d"),
                    "value": round(float(predicted_value), 2),
                    "type": "future_prediction",
                    "confidence": round(max(0.5, 0.9 - i * 0.05), 2)  # Decreasing confidence
                })
        
        return {
            "symbol": yf_symbol,
            "name": symbol.upper(),
            "data": {
                "actual": actual_data,
                "historical_predictions": historical_predictions,
                "future_predictions": future_predictions
            },
            "summary": {
                "actual_count": len(actual_data),
                "historical_predictions_count": len(historical_predictions),
                "future_predictions_count": len(future_predictions)
            }
        }
        
    except Exception as e:
        return {"error": str(e)}

# API Routes
from api.finance.routes import router as finance_router
from api.finance.routes_v2 import router as finance_v2_router
from api.forex.routes import router as forex_router
from api.websocket.routes import router as websocket_router
from api.user.routes import router as user_router
# from api.auth.routes import router as auth_router
# from api.admin.routes import router as admin_router

# app.include_router(auth_router, prefix="/api/auth", tags=["authentication"])
app.include_router(finance_router, prefix="/api/finance", tags=["finance"])
app.include_router(finance_v2_router, prefix="/api/finance", tags=["finance_v2"])
app.include_router(forex_router, prefix="/api/forex", tags=["forex"])
app.include_router(user_router, prefix="/api", tags=["users"])
# app.include_router(admin_router, prefix="/api/admin", tags=["administration"])
app.include_router(websocket_router, prefix="", tags=["websocket"])

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=int(os.getenv("PORT", 8000)),
        reload=True,
        log_level=os.getenv("LOG_LEVEL", "info").lower()
    )