from fastapi import Request, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from starlette.middleware.base import BaseHTTPMiddleware
from services.rbac_service import rbac_service, Permission
from database.models.users import User
from database.database import SessionLocal
import jwt
import os
from typing import Optional
import logging

logger = logging.getLogger(__name__)

class AuthMiddleware(BaseHTTPMiddleware):
    def __init__(self, app):
        super().__init__(app)
        self.jwt_secret = os.getenv("JWT_SECRET", "your-secret-key")
        self.jwt_algorithm = "HS256"
        
        # 認証不要のエンドポイント
        self.public_endpoints = {
            "/",
            "/health",
            "/docs",
            "/openapi.json",
            "/api/auth/login",
            "/api/auth/register"
        }
        
        # 認証不要のパスパターン（公開データ）
        self.public_path_patterns = [
            "/api/finance/stocks/",  # 株価データは公開
            "/api/finance/markets/", # 市場データは公開
            "/api/finance/rankings/", # ランキングデータは公開
        ]

    async def dispatch(self, request: Request, call_next):
        # 公開エンドポイントは認証をスキップ
        if (request.url.path in self.public_endpoints or 
            request.url.path.startswith("/static") or
            any(request.url.path.startswith(pattern) for pattern in self.public_path_patterns)):
            return await call_next(request)

        # Authorizationヘッダーをチェック
        authorization = request.headers.get("Authorization")
        
        if not authorization or not authorization.startswith("Bearer "):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="認証トークンが必要です",
                headers={"WWW-Authenticate": "Bearer"},
            )

        token = authorization.split(" ")[1]
        
        try:
            # JWTトークンを検証
            payload = jwt.decode(token, self.jwt_secret, algorithms=[self.jwt_algorithm])
            user_id = payload.get("sub")
            
            if not user_id:
                raise HTTPException(status_code=401, detail="無効なトークン")

            # ユーザー情報を取得
            db = SessionLocal()
            try:
                user = db.query(User).filter(User.id == int(user_id)).first()
                if not user or not user.is_active:
                    raise HTTPException(status_code=401, detail="ユーザーが見つからないか無効です")

                # RBAC権限チェック
                if not rbac_service.can_access_endpoint(user.role, request.url.path, request.method):
                    raise HTTPException(
                        status_code=status.HTTP_403_FORBIDDEN,
                        detail="このリソースへのアクセス権限がありません"
                    )

                # リクエストにユーザー情報を追加
                request.state.user = user
                
            finally:
                db.close()

        except jwt.ExpiredSignatureError:
            raise HTTPException(status_code=401, detail="トークンが期限切れです")
        except jwt.InvalidTokenError:
            raise HTTPException(status_code=401, detail="無効なトークンです")
        except Exception as e:
            logger.error(f"認証エラー: {e}")
            raise HTTPException(status_code=401, detail="認証に失敗しました")

        return await call_next(request)

def get_current_user(request: Request) -> Optional[User]:
    """現在のユーザーを取得"""
    return getattr(request.state, 'user', None)

def require_permission(permission: Permission):
    """特定の権限を要求するデコレータ"""
    def decorator(func):
        async def wrapper(*args, **kwargs):
            request = kwargs.get('request') or args[0] if args else None
            
            if not request or not hasattr(request.state, 'user'):
                raise HTTPException(status_code=401, detail="認証が必要です")
            
            user = request.state.user
            if not rbac_service.has_permission(user.role, permission):
                raise HTTPException(
                    status_code=403, 
                    detail=f"権限が不足しています: {permission.value}"
                )
            
            return await func(*args, **kwargs)
        return wrapper
    return decorator

def require_role(required_role: str):
    """特定のロール以上を要求するデコレータ"""
    def decorator(func):
        async def wrapper(*args, **kwargs):
            request = kwargs.get('request') or args[0] if args else None
            
            if not request or not hasattr(request.state, 'user'):
                raise HTTPException(status_code=401, detail="認証が必要です")
            
            user = request.state.user
            if not rbac_service.is_role_higher_or_equal(user.role, required_role):
                raise HTTPException(
                    status_code=403, 
                    detail=f"必要なロール: {required_role} 以上"
                )
            
            return await func(*args, **kwargs)
        return wrapper
    return decorator