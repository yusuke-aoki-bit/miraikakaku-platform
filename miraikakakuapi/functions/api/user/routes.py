from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, date
import logging

from database.database import get_db
from database.models.user_models import (
    UserProfiles, UserWatchlists, UserPortfolios, 
    AiDecisionFactors, PredictionContests, UserContestPredictions, ThemeInsights
)
from database.models.stock_predictions import StockPredictions
from .models import *

logger = logging.getLogger(__name__)
router = APIRouter()

# ユーザープロファイル関連エンドポイント
@router.post("/users/profile", response_model=UserProfileResponse)
async def create_user_profile(profile: UserProfileCreate, db: Session = Depends(get_db)):
    """ユーザープロファイルを作成"""
    try:
        # 既存ユーザーチェック
        existing_user = db.query(UserProfiles).filter(UserProfiles.user_id == profile.user_id).first()
        if existing_user:
            raise HTTPException(status_code=400, detail="ユーザーは既に存在します")
        
        db_user = UserProfiles(**profile.dict())
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        
        return UserProfileResponse.from_orm(db_user)
    except Exception as e:
        logger.error(f"ユーザープロファイル作成エラー: {e}")
        raise HTTPException(status_code=500, detail=f"プロファイル作成エラー: {str(e)}")

@router.get("/users/{user_id}/profile", response_model=UserProfileResponse)
async def get_user_profile(user_id: str, db: Session = Depends(get_db)):
    """ユーザープロファイルを取得"""
    try:
        user = db.query(UserProfiles).filter(UserProfiles.user_id == user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="ユーザーが見つかりません")
        
        return UserProfileResponse.from_orm(user)
    except Exception as e:
        logger.error(f"ユーザープロファイル取得エラー: {e}")
        raise HTTPException(status_code=500, detail=f"プロファイル取得エラー: {str(e)}")

@router.put("/users/{user_id}/profile", response_model=UserProfileResponse)
async def update_user_profile(user_id: str, profile_update: UserProfileUpdate, db: Session = Depends(get_db)):
    """ユーザープロファイルを更新"""
    try:
        user = db.query(UserProfiles).filter(UserProfiles.user_id == user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="ユーザーが見つかりません")
        
        update_data = profile_update.dict(exclude_unset=True)
        for key, value in update_data.items():
            setattr(user, key, value)
        
        user.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(user)
        
        return UserProfileResponse.from_orm(user)
    except Exception as e:
        logger.error(f"ユーザープロファイル更新エラー: {e}")
        raise HTTPException(status_code=500, detail=f"プロファイル更新エラー: {str(e)}")

# AI判断根拠エンドポイント
@router.get("/predictions/{prediction_id}/factors", response_model=List[AiDecisionFactorResponse])
async def get_ai_decision_factors(prediction_id: int, db: Session = Depends(get_db)):
    """AI予測の判断根拠を取得"""
    try:
        factors = db.query(AiDecisionFactors).filter(
            AiDecisionFactors.prediction_id == prediction_id
        ).order_by(AiDecisionFactors.influence_score.desc()).all()
        
        return [AiDecisionFactorResponse.from_orm(factor) for factor in factors]
    except Exception as e:
        logger.error(f"AI判断根拠取得エラー: {e}")
        raise HTTPException(status_code=500, detail=f"判断根拠取得エラー: {str(e)}")

@router.get("/ai-factors/all", response_model=List[AiDecisionFactorResponse])
async def get_all_ai_factors(limit: int = 100, offset: int = 0, db: Session = Depends(get_db)):
    """全てのAI決定要因を取得（汎用エンドポイント）"""
    try:
        factors = db.query(AiDecisionFactors).order_by(
            AiDecisionFactors.created_at.desc()
        ).offset(offset).limit(limit).all()
        
        return [AiDecisionFactorResponse.from_orm(factor) for factor in factors]
    except Exception as e:
        logger.error(f"AI決定要因一覧取得エラー: {e}")
        raise HTTPException(status_code=500, detail=f"決定要因取得エラー: {str(e)}")

@router.get("/ai-factors/symbol/{symbol}", response_model=List[AiDecisionFactorResponse])
async def get_symbol_ai_factors(symbol: str, limit: int = 50, db: Session = Depends(get_db)):
    """特定銘柄の全AI決定要因を取得"""
    try:
        # 銘柄の予測IDを取得
        prediction_ids = db.query(StockPredictions.id).filter(
            StockPredictions.symbol == symbol
        ).subquery()
        
        factors = db.query(AiDecisionFactors).filter(
            AiDecisionFactors.prediction_id.in_(prediction_ids)
        ).order_by(AiDecisionFactors.influence_score.desc()).limit(limit).all()
        
        return [AiDecisionFactorResponse.from_orm(factor) for factor in factors]
    except Exception as e:
        logger.error(f"銘柄別AI決定要因取得エラー: {e}")
        raise HTTPException(status_code=500, detail=f"決定要因取得エラー: {str(e)}")

@router.get("/stocks/{symbol}/predictions/enhanced", response_model=List[EnhancedPredictionResponse])
async def get_enhanced_predictions(symbol: str, db: Session = Depends(get_db)):
    """判断根拠付きの強化予測データを取得"""
    try:
        # 予測データを取得
        predictions = db.query(StockPredictions).filter(
            StockPredictions.symbol == symbol
        ).order_by(StockPredictions.prediction_date.desc()).limit(7).all()
        
        enhanced_predictions = []
        for prediction in predictions:
            # 各予測の判断根拠を取得
            factors = db.query(AiDecisionFactors).filter(
                AiDecisionFactors.prediction_id == prediction.id
            ).order_by(AiDecisionFactors.influence_score.desc()).limit(3).all()
            
            enhanced_predictions.append(EnhancedPredictionResponse(
                id=prediction.id,
                symbol=prediction.symbol,
                prediction_date=prediction.prediction_date,
                predicted_price=prediction.predicted_price,
                confidence_score=prediction.confidence_score,
                model_version=prediction.model_version,
                decision_factors=[AiDecisionFactorResponse.from_orm(f) for f in factors]
            ))
        
        return enhanced_predictions
    except Exception as e:
        logger.error(f"強化予測データ取得エラー: {e}")
        raise HTTPException(status_code=500, detail=f"強化予測データ取得エラー: {str(e)}")

# ウォッチリスト関連エンドポイント
@router.post("/users/{user_id}/watchlist", response_model=WatchlistResponse)
async def add_to_watchlist(user_id: str, watchlist_item: WatchlistCreate, db: Session = Depends(get_db)):
    """ウォッチリストに銘柄を追加"""
    try:
        # ユーザー存在確認
        user = db.query(UserProfiles).filter(UserProfiles.user_id == user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="ユーザーが見つかりません")
        
        # 既存項目チェック
        existing = db.query(UserWatchlists).filter(
            UserWatchlists.user_id == user_id,
            UserWatchlists.symbol == watchlist_item.symbol
        ).first()
        
        if existing:
            raise HTTPException(status_code=400, detail="この銘柄は既にウォッチリストに追加されています")
        
        db_watchlist = UserWatchlists(user_id=user_id, **watchlist_item.dict())
        db.add(db_watchlist)
        db.commit()
        db.refresh(db_watchlist)
        
        return WatchlistResponse.from_orm(db_watchlist)
    except Exception as e:
        logger.error(f"ウォッチリスト追加エラー: {e}")
        raise HTTPException(status_code=500, detail=f"ウォッチリスト追加エラー: {str(e)}")

@router.get("/users/{user_id}/watchlist", response_model=List[WatchlistResponse])
async def get_user_watchlist(user_id: str, db: Session = Depends(get_db)):
    """ユーザーのウォッチリストを取得"""
    try:
        watchlist = db.query(UserWatchlists).filter(
            UserWatchlists.user_id == user_id
        ).order_by(UserWatchlists.priority.desc(), UserWatchlists.added_at.desc()).all()
        
        return [WatchlistResponse.from_orm(item) for item in watchlist]
    except Exception as e:
        logger.error(f"ウォッチリスト取得エラー: {e}")
        raise HTTPException(status_code=500, detail=f"ウォッチリスト取得エラー: {str(e)}")

# ポートフォリオ関連エンドポイント
@router.get("/users/{user_id}/portfolio", response_model=List[PortfolioResponse])
async def get_user_portfolio(user_id: str, db: Session = Depends(get_db)):
    """ユーザーのポートフォリオを取得"""
    try:
        portfolio = db.query(UserPortfolios).filter(
            UserPortfolios.user_id == user_id,
            UserPortfolios.is_active == True
        ).all()
        
        return [PortfolioResponse.from_orm(item) for item in portfolio]
    except Exception as e:
        logger.error(f"ポートフォリオ取得エラー: {e}")
        raise HTTPException(status_code=500, detail=f"ポートフォリオ取得エラー: {str(e)}")

# コンテスト関連エンドポイント
@router.get("/contests/active", response_model=List[PredictionContestResponse])
async def get_active_contests(db: Session = Depends(get_db)):
    """アクティブな予測コンテストを取得"""
    try:
        contests = db.query(PredictionContests).filter(
            PredictionContests.status == 'active'
        ).order_by(PredictionContests.prediction_deadline.desc()).all()
        
        return [PredictionContestResponse.from_orm(contest) for contest in contests]
    except Exception as e:
        logger.error(f"アクティブコンテスト取得エラー: {e}")
        raise HTTPException(status_code=500, detail=f"コンテスト取得エラー: {str(e)}")

@router.post("/contests/{contest_id}/predict", response_model=ContestPredictionResponse)
async def submit_contest_prediction(contest_id: int, prediction: ContestPredictionCreate, db: Session = Depends(get_db)):
    """コンテストに予測を投稿"""
    try:
        # コンテスト存在確認
        contest = db.query(PredictionContests).filter(PredictionContests.id == contest_id).first()
        if not contest:
            raise HTTPException(status_code=404, detail="コンテストが見つかりません")
        
        if contest.status != 'active':
            raise HTTPException(status_code=400, detail="このコンテストは終了しています")
        
        # 既存予測チェック
        existing = db.query(UserContestPredictions).filter(
            UserContestPredictions.contest_id == contest_id,
            UserContestPredictions.user_id == prediction.user_id
        ).first()
        
        if existing:
            raise HTTPException(status_code=400, detail="このコンテストには既に予測を投稿済みです")
        
        db_prediction = UserContestPredictions(contest_id=contest_id, **prediction.dict())
        db.add(db_prediction)
        db.commit()
        db.refresh(db_prediction)
        
        return ContestPredictionResponse.from_orm(db_prediction)
    except Exception as e:
        logger.error(f"コンテスト予測投稿エラー: {e}")
        raise HTTPException(status_code=500, detail=f"予測投稿エラー: {str(e)}")

# テーマ別インサイト関連エンドポイント
@router.get("/insights/themes", response_model=List[str])
async def get_available_themes(db: Session = Depends(get_db)):
    """利用可能なテーマ一覧を取得"""
    try:
        themes = db.query(ThemeInsights.theme_name).distinct().all()
        return [theme[0] for theme in themes]
    except Exception as e:
        logger.error(f"テーマ一覧取得エラー: {e}")
        raise HTTPException(status_code=500, detail=f"テーマ一覧取得エラー: {str(e)}")

@router.get("/insights/themes/{theme_name}", response_model=List[ThemeInsightResponse])
async def get_theme_insights(theme_name: str, limit: int = 10, db: Session = Depends(get_db)):
    """特定テーマのインサイトを取得"""
    try:
        insights = db.query(ThemeInsights).filter(
            ThemeInsights.theme_name == theme_name
        ).order_by(ThemeInsights.insight_date.desc()).limit(limit).all()
        
        return [ThemeInsightResponse.from_orm(insight) for insight in insights]
    except Exception as e:
        logger.error(f"テーマインサイト取得エラー: {e}")
        raise HTTPException(status_code=500, detail=f"インサイト取得エラー: {str(e)}")

@router.get("/insights/all", response_model=List[ThemeInsightResponse])
async def get_all_insights(limit: int = 100, offset: int = 0, db: Session = Depends(get_db)):
    """全てのテーマ洞察を取得（汎用エンドポイント）"""
    try:
        insights = db.query(ThemeInsights).order_by(
            ThemeInsights.created_at.desc()
        ).offset(offset).limit(limit).all()
        
        return [ThemeInsightResponse.from_orm(insight) for insight in insights]
    except Exception as e:
        logger.error(f"テーマ洞察一覧取得エラー: {e}")
        raise HTTPException(status_code=500, detail=f"洞察取得エラー: {str(e)}")

@router.get("/insights/latest", response_model=List[ThemeInsightResponse])
async def get_latest_insights(days: int = 7, limit: int = 50, db: Session = Depends(get_db)):
    """最新のテーマ洞察を取得"""
    try:
        from datetime import datetime, timedelta
        cutoff_date = datetime.now() - timedelta(days=days)
        
        insights = db.query(ThemeInsights).filter(
            ThemeInsights.created_at >= cutoff_date
        ).order_by(ThemeInsights.impact_score.desc()).limit(limit).all()
        
        return [ThemeInsightResponse.from_orm(insight) for insight in insights]
    except Exception as e:
        logger.error(f"最新テーマ洞察取得エラー: {e}")
        raise HTTPException(status_code=500, detail=f"洞察取得エラー: {str(e)}")

@router.get("/insights/categories/{category}", response_model=List[ThemeInsightResponse])
async def get_category_insights(category: str, limit: int = 10, db: Session = Depends(get_db)):
    """カテゴリ別インサイトを取得"""
    try:
        insights = db.query(ThemeInsights).filter(
            ThemeInsights.theme_category == category
        ).order_by(ThemeInsights.insight_date.desc()).limit(limit).all()
        
        return [ThemeInsightResponse.from_orm(insight) for insight in insights]
    except Exception as e:
        logger.error(f"カテゴリインサイト取得エラー: {e}")
        raise HTTPException(status_code=500, detail=f"インサイト取得エラー: {str(e)}")