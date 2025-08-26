from fastapi import APIRouter, Depends, HTTPException, Query, Request
from sqlalchemy.orm import Session
from database.database import get_db
from database.models.users import User
from database.models import StockMaster, StockPredictions, AIInferenceLog
from api.models.admin_models import (
    UserCreateRequest,
    UserUpdateRequest,
    UserResponse,
    SystemStatsResponse,
    ModelPerformanceResponse,
)
from services.auth_service import AuthService
from services.rbac_service import Permission
from middleware.auth_middleware import (
    get_current_user,
    require_permission,
    require_role,
)
from typing import List
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)
router = APIRouter()


# ユーザー管理エンドポイント
@router.get("/users", response_model=List[UserResponse])
@require_permission(Permission.READ_USERS)
async def get_users(
    request: Request,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db),
):
    """ユーザー一覧取得"""
    users = db.query(User).offset(skip).limit(limit).all()
    return [
        UserResponse(
            id=str(user.id),
            email=user.email,
            name=user.name,
            role=user.role,
            is_active=user.is_active,
            created_at=user.created_at.isoformat(),
            last_login=(user.last_login.isoformat() if user.last_login else None),
        )
        for user in users
    ]


@router.post("/users", response_model=UserResponse)
@require_permission(Permission.CREATE_USERS)
async def create_user(
    request: Request, user_data: UserCreateRequest, db: Session = Depends(get_db)
):
    """新規ユーザー作成"""
    auth_service = AuthService(db)

    try:
        user = await auth_service.create_user(
            email=user_data.email,
            password=user_data.password,
            name=user_data.name,
            role=user_data.role,
        )

        return UserResponse(
            id=str(user.id),
            email=user.email,
            name=user.name,
            role=user.role,
            is_active=user.is_active,
            created_at=user.created_at.isoformat(),
        )

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.put("/users/{user_id}", response_model=UserResponse)
@require_permission(Permission.UPDATE_USERS)
async def update_user(
    request: Request,
    user_id: int,
    user_data: UserUpdateRequest,
    db: Session = Depends(get_db),
):
    """ユーザー情報更新"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="ユーザーが見つかりません")

    # 更新可能なフィールドのみ更新
    update_data = user_data.dict(exclude_unset=True)
    for field, value in update_data.items():
        if hasattr(user, field):
            setattr(user, field, value)

    user.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(user)

    return UserResponse(
        id=str(user.id),
        email=user.email,
        name=user.name,
        role=user.role,
        is_active=user.is_active,
        created_at=user.created_at.isoformat(),
        last_login=(user.last_login.isoformat() if user.last_login else None),
    )


@router.delete("/users/{user_id}")
@require_permission(Permission.DELETE_USERS)
async def delete_user(request: Request, user_id: int, db: Session = Depends(get_db)):
    """ユーザー削除"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="ユーザーが見つかりません")

    # 論理削除
    user.is_active = False
    user.updated_at = datetime.utcnow()
    db.commit()

    return {"message": "ユーザーを無効化しました"}


# システム統計エンドポイント
@router.get("/system/stats", response_model=SystemStatsResponse)
@require_permission(Permission.READ_SYSTEM_LOGS)
async def get_system_stats(request: Request, db: Session = Depends(get_db)):
    """システム統計取得"""
    try:
        # 基本統計
        total_users = db.query(User).filter(User.is_active is True).count()
        total_stocks = (
            db.query(StockMaster).filter(StockMaster.is_active is True).count()
        )
        total_predictions = db.query(StockPredictions).count()

        # 今日の活動
        today = datetime.utcnow().date()
        today_predictions = (
            db.query(StockPredictions)
            .filter(StockPredictions.prediction_date >= today)
            .count()
        )

        today_inferences = (
            db.query(AIInferenceLog).filter(AIInferenceLog.created_at >= today).count()
        )

        # 最近の活動
        recent_logins = (
            db.query(User)
            .filter(User.last_login >= datetime.utcnow() - timedelta(days=7))
            .count()
        )

        return SystemStatsResponse(
            total_users=total_users,
            total_stocks=total_stocks,
            total_predictions=total_predictions,
            today_predictions=today_predictions,
            today_inferences=today_inferences,
            recent_active_users=recent_logins,
            system_uptime="Available",
            last_updated=datetime.utcnow().isoformat(),
        )

    except Exception as e:
        logger.error(f"システム統計取得エラー: {e}")
        raise HTTPException(status_code=500, detail="統計データ取得に失敗しました")


@router.get("/models/performance", response_model=List[ModelPerformanceResponse])
@require_permission(Permission.ACCESS_ML_PIPELINE)
async def get_model_performance(
    request: Request, days: int = Query(30, ge=1, le=365), db: Session = Depends(get_db)
):
    """モデル性能統計取得"""
    try:
        start_date = datetime.utcnow() - timedelta(days=days)

        # モデル別の予測精度を計算
        models = db.query(StockPredictions.model_type).distinct().all()
        performance_data = []

        for (model_type,) in models:
            predictions = (
                db.query(StockPredictions)
                .filter(
                    StockPredictions.model_type == model_type,
                    StockPredictions.prediction_date >= start_date,
                    StockPredictions.is_active is True,
                )
                .all()
            )

            if predictions:
                avg_confidence = sum(
                    p.confidence_score for p in predictions if p.confidence_score
                ) / len(predictions)

                performance_data.append(
                    ModelPerformanceResponse(
                        model_name=model_type,
                        total_predictions=len(predictions),
                        avg_confidence=avg_confidence,
                        # confidence_scoreを精度の代替として使用
                        avg_accuracy=avg_confidence,
                        last_prediction=max(
                            p.prediction_date for p in predictions
                        ).isoformat(),
                    )
                )

        return performance_data

    except Exception as e:
        logger.error(f"モデル性能取得エラー: {e}")
        raise HTTPException(status_code=500, detail="性能データ取得に失敗しました")


@router.post("/system/restart")
@require_role("admin")
async def restart_system(request: Request):
    """システム再起動（開発用）"""
    current_user = get_current_user(request)
    logger.info(f"システム再起動要求: ユーザー {current_user.email}")

    # 実際の本番環境では適切な再起動処理を実装
    return {
        "message": "システム再起動を開始しました",
        "requested_by": current_user.email,
    }


@router.get("/logs/recent")
@require_permission(Permission.READ_SYSTEM_LOGS)
async def get_recent_logs(
    request: Request,
    limit: int = Query(100, ge=1, le=1000),
    level: str = Query("INFO", regex="^(DEBUG|INFO|WARNING|ERROR|CRITICAL)$"),
    db: Session = Depends(get_db),
):
    """最近のシステムログ取得"""
    try:
        logs = (
            db.query(AIInferenceLog)
            .order_by(AIInferenceLog.created_at.desc())
            .limit(limit)
            .all()
        )

        return [
            {
                "id": log.id,
                "request_id": log.request_id,
                # フォールバック対応
                "model_name": getattr(log, "model_name", "unknown"),
                "is_successful": log.is_successful,
                "inference_time_ms": log.inference_time_ms,
                "error_message": log.error_message,
                "created_at": log.created_at.isoformat(),
            }
            for log in logs
        ]

    except Exception as e:
        logger.error(f"ログ取得エラー: {e}")
        raise HTTPException(status_code=500, detail="ログ取得に失敗しました")
