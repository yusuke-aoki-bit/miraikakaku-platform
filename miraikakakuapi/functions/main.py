from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from middleware.auth_middleware import AuthMiddleware
import uvicorn
import os
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(
    title="Miraikakaku API",
    description="金融分析・株価予測API",
    version="1.0.0",
    openapi_url="/api/v1/openapi.json"
)

# CORS設定
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:8080",
        os.getenv("FRONTEND_URL", "http://localhost:3000")
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 認証ミドルウェア
app.add_middleware(AuthMiddleware)

@app.on_event("startup")
async def startup_event():
    from database.database import init_database
    await init_database()

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

# API Routes
from api.finance.routes import router as finance_router
from api.websocket.routes import router as websocket_router
from api.auth.routes import router as auth_router
from api.admin.routes import router as admin_router

app.include_router(auth_router, prefix="/api/auth", tags=["authentication"])
app.include_router(finance_router, prefix="/api/finance", tags=["finance"])
app.include_router(admin_router, prefix="/api/admin", tags=["administration"])
app.include_router(websocket_router, prefix="", tags=["websocket"])

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=int(os.getenv("PORT", 8000)),
        reload=True,
        log_level=os.getenv("LOG_LEVEL", "info").lower()
    )