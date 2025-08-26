from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from database.database import get_db
from api.models.auth_models import LoginRequest, LoginResponse, UserResponse
from services.auth_service import AuthService
import jwt
import os

router = APIRouter()
security = HTTPBearer()


@router.post("/login", response_model=LoginResponse)
async def login(login_data: LoginRequest, db: Session = Depends(get_db)):
    """ユーザーログイン"""
    auth_service = AuthService(db)

    user = await auth_service.authenticate_user(login_data.email, login_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="メールアドレスまたはパスワードが正しくありません",
        )

    access_token = auth_service.create_access_token(user.id)

    return LoginResponse(
        access_token=access_token,
        token_type="bearer",
        expires_in=3600,
        user=UserResponse(
            id=str(user.id), email=user.email, name=user.name, role=user.role
        ),
    )


@router.get("/profile", response_model=UserResponse)
async def get_profile(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db),
):
    """ユーザープロファイル取得"""
    auth_service = AuthService(db)

    try:
        payload = jwt.decode(
            credentials.credentials,
            os.getenv("JWT_SECRET", "secret-key"),
            algorithms=["HS256"],
        )
        user_id = payload.get("sub")

        if not user_id:
            raise HTTPException(status_code=401, detail="無効なトークン")

        user = await auth_service.get_user_by_id(user_id)
        if not user:
            raise HTTPException(status_code=404, detail="ユーザーが見つかりません")

        return UserResponse(
            id=str(user.id), email=user.email, name=user.name, role=user.role
        )

    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="トークンが期限切れです")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="無効なトークンです")


@router.post("/logout")
async def logout():
    """ログアウト（クライアント側でトークン削除）"""
    return {"message": "ログアウトしました"}
