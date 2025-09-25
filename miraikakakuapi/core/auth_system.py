#!/usr/bin/env python3
"""
ユーザー認証・個人化システム
User Authentication & Personalization System

JWT認証とユーザープロファイル管理
"""

import jwt
import bcrypt
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text, JSON, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Session, relationship
from pydantic import BaseModel, EmailStr
import secrets
import logging
from .logging_config import setup_logging
from .database import get_db

logger = setup_logging(__name__)

# JWT設定
JWT_SECRET_KEY = secrets.token_urlsafe(32)
JWT_ALGORITHM = "HS256"
JWT_EXPIRATION_HOURS = 24

Base = declarative_base()

class User(Base):
    """ユーザーモデル"""
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    username = Column(String(50), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(100))

    # プロファイル情報
    bio = Column(Text)
    avatar_url = Column(String(500))
    timezone = Column(String(50), default="Asia/Tokyo")
    language = Column(String(10), default="ja")

    # 投資プロファイル
    investment_experience = Column(String(20))  # beginner, intermediate, advanced
    risk_tolerance = Column(String(20))  # conservative, moderate, aggressive
    investment_goals = Column(JSON)  # リスト形式
    preferred_sectors = Column(JSON)  # お気に入りセクター

    # アカウント設定
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    is_premium = Column(Boolean, default=False)

    # タイムスタンプ
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_login = Column(DateTime)

    # リレーション
    watchlists = relationship("Watchlist", back_populates="user", cascade="all, delete-orphan")
    alerts = relationship("PriceAlert", back_populates="user", cascade="all, delete-orphan")
    portfolios = relationship("Portfolio", back_populates="user", cascade="all, delete-orphan")

class Watchlist(Base):
    """ウォッチリストモデル"""
    __tablename__ = "watchlists"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    name = Column(String(100), nullable=False)
    description = Column(Text)
    symbols = Column(JSON)  # 銘柄リスト
    is_public = Column(Boolean, default=False)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    user = relationship("User", back_populates="watchlists")

class PriceAlert(Base):
    """価格アラートモデル"""
    __tablename__ = "price_alerts"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    symbol = Column(String(20), nullable=False)
    alert_type = Column(String(20), nullable=False)  # above, below, change_percent
    target_price = Column(String(20))  # 目標価格
    percentage_change = Column(String(10))  # パーセンテージ変化
    is_active = Column(Boolean, default=True)

    created_at = Column(DateTime, default=datetime.utcnow)
    triggered_at = Column(DateTime)

    user = relationship("User", back_populates="alerts")

class Portfolio(Base):
    """ポートフォリオモデル"""
    __tablename__ = "portfolios"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    name = Column(String(100), nullable=False)
    description = Column(Text)
    holdings = Column(JSON)  # 保有銘柄と数量
    total_value = Column(String(20))
    is_public = Column(Boolean, default=False)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    user = relationship("User", back_populates="portfolios")

# Pydantic モデル
class UserCreate(BaseModel):
    email: EmailStr
    username: str
    password: str
    full_name: Optional[str] = None

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserUpdate(BaseModel):
    full_name: Optional[str] = None
    bio: Optional[str] = None
    timezone: Optional[str] = None
    language: Optional[str] = None
    investment_experience: Optional[str] = None
    risk_tolerance: Optional[str] = None
    investment_goals: Optional[List[str]] = None
    preferred_sectors: Optional[List[str]] = None

class UserResponse(BaseModel):
    id: int
    email: str
    username: str
    full_name: Optional[str]
    bio: Optional[str]
    investment_experience: Optional[str]
    risk_tolerance: Optional[str]
    is_premium: bool
    created_at: datetime

class WatchlistCreate(BaseModel):
    name: str
    description: Optional[str] = None
    symbols: List[str]
    is_public: bool = False

class AlertCreate(BaseModel):
    symbol: str
    alert_type: str
    target_price: Optional[float] = None
    percentage_change: Optional[float] = None

@dataclass
class AuthToken:
    """認証トークン"""
    access_token: str
    token_type: str = "bearer"
    expires_in: int = JWT_EXPIRATION_HOURS * 3600

class AuthenticationSystem:
    """認証システム"""

    def __init__(self):
        self.password_context = bcrypt

    def hash_password(self, password: str) -> str:
        """パスワードをハッシュ化"""
        return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """パスワードを検証"""
        return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))

    def create_access_token(self, data: Dict[str, Any]) -> str:
        """JWTアクセストークンを作成"""
        to_encode = data.copy()
        expire = datetime.utcnow() + timedelta(hours=JWT_EXPIRATION_HOURS)
        to_encode.update({"exp": expire})

        return jwt.encode(to_encode, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)

    def verify_token(self, token: str) -> Optional[Dict[str, Any]]:
        """JWTトークンを検証"""
        try:
            payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
            return payload
        except jwt.ExpiredSignatureError:
            logger.warning("Token has expired")
            return None
        except jwt.JWTError as e:
            logger.warning(f"Token verification failed: {e}")
            return None

    def register_user(self, user_data: UserCreate, db: Session) -> Optional[User]:
        """ユーザーを登録"""
        try:
            # メールアドレスとユーザー名の重複チェック
            existing_user = db.query(User).filter(
                (User.email == user_data.email) | (User.username == user_data.username)
            ).first()

            if existing_user:
                if existing_user.email == user_data.email:
                    raise ValueError("Email already registered")
                else:
                    raise ValueError("Username already taken")

            # 新しいユーザーを作成
            hashed_password = self.hash_password(user_data.password)

            new_user = User(
                email=user_data.email,
                username=user_data.username,
                hashed_password=hashed_password,
                full_name=user_data.full_name
            )

            db.add(new_user)
            db.commit()
            db.refresh(new_user)

            logger.info(f"User registered successfully: {user_data.email}")
            return new_user

        except Exception as e:
            db.rollback()
            logger.error(f"User registration failed: {e}")
            raise

    def authenticate_user(self, login_data: UserLogin, db: Session) -> Optional[User]:
        """ユーザーを認証"""
        try:
            user = db.query(User).filter(User.email == login_data.email).first()

            if not user:
                return None

            if not self.verify_password(login_data.password, user.hashed_password):
                return None

            if not user.is_active:
                raise ValueError("Account is deactivated")

            # ログイン時刻を更新
            user.last_login = datetime.utcnow()
            db.commit()

            return user

        except Exception as e:
            logger.error(f"Authentication failed: {e}")
            raise

    def get_user_by_id(self, user_id: int, db: Session) -> Optional[User]:
        """IDでユーザーを取得"""
        return db.query(User).filter(User.id == user_id).first()

    def get_user_by_token(self, token: str, db: Session) -> Optional[User]:
        """トークンからユーザーを取得"""
        payload = self.verify_token(token)
        if not payload:
            return None

        user_id = payload.get("sub")
        if not user_id:
            return None

        return self.get_user_by_id(int(user_id), db)

    def update_user_profile(self, user_id: int, update_data: UserUpdate, db: Session) -> Optional[User]:
        """ユーザープロファイルを更新"""
        try:
            user = db.query(User).filter(User.id == user_id).first()
            if not user:
                return None

            update_dict = update_data.dict(exclude_unset=True)
            for field, value in update_dict.items():
                setattr(user, field, value)

            user.updated_at = datetime.utcnow()
            db.commit()
            db.refresh(user)

            return user

        except Exception as e:
            db.rollback()
            logger.error(f"Profile update failed: {e}")
            raise

class PersonalizationSystem:
    """個人化システム"""

    def __init__(self):
        pass

    def create_watchlist(self, user_id: int, watchlist_data: WatchlistCreate, db: Session) -> Watchlist:
        """ウォッチリストを作成"""
        try:
            watchlist = Watchlist(
                user_id=user_id,
                name=watchlist_data.name,
                description=watchlist_data.description,
                symbols=watchlist_data.symbols,
                is_public=watchlist_data.is_public
            )

            db.add(watchlist)
            db.commit()
            db.refresh(watchlist)

            return watchlist

        except Exception as e:
            db.rollback()
            logger.error(f"Watchlist creation failed: {e}")
            raise

    def get_user_watchlists(self, user_id: int, db: Session) -> List[Watchlist]:
        """ユーザーのウォッチリストを取得"""
        return db.query(Watchlist).filter(Watchlist.user_id == user_id).all()

    def create_price_alert(self, user_id: int, alert_data: AlertCreate, db: Session) -> PriceAlert:
        """価格アラートを作成"""
        try:
            alert = PriceAlert(
                user_id=user_id,
                symbol=alert_data.symbol,
                alert_type=alert_data.alert_type,
                target_price=str(alert_data.target_price) if alert_data.target_price else None,
                percentage_change=str(alert_data.percentage_change) if alert_data.percentage_change else None
            )

            db.add(alert)
            db.commit()
            db.refresh(alert)

            return alert

        except Exception as e:
            db.rollback()
            logger.error(f"Price alert creation failed: {e}")
            raise

    def get_user_alerts(self, user_id: int, db: Session) -> List[PriceAlert]:
        """ユーザーのアラートを取得"""
        return db.query(PriceAlert).filter(PriceAlert.user_id == user_id, PriceAlert.is_active == True).all()

    def get_personalized_recommendations(self, user_id: int, db: Session) -> Dict[str, Any]:
        """個人化された推奨情報を取得"""
        try:
            user = db.query(User).filter(User.id == user_id).first()
            if not user:
                return {}

            recommendations = {
                "trending_symbols": [],
                "recommended_sectors": [],
                "risk_appropriate_stocks": [],
                "educational_content": []
            }

            # リスク許容度に基づく推奨
            if user.risk_tolerance == "conservative":
                recommendations["recommended_sectors"] = ["utilities", "consumer_staples", "healthcare"]
                recommendations["educational_content"] = ["dividend_investing", "bond_basics"]
            elif user.risk_tolerance == "aggressive":
                recommendations["recommended_sectors"] = ["technology", "growth", "emerging_markets"]
                recommendations["educational_content"] = ["options_trading", "growth_investing"]
            else:
                recommendations["recommended_sectors"] = ["financials", "industrials", "consumer_discretionary"]
                recommendations["educational_content"] = ["portfolio_diversification", "index_investing"]

            # 投資経験に基づく推奨
            if user.investment_experience == "beginner":
                recommendations["educational_content"].extend(["investment_basics", "risk_management"])
            elif user.investment_experience == "advanced":
                recommendations["educational_content"].extend(["advanced_analysis", "derivatives"])

            return recommendations

        except Exception as e:
            logger.error(f"Failed to get recommendations for user {user_id}: {e}")
            return {}

# グローバルインスタンス
auth_system = AuthenticationSystem()
personalization_system = PersonalizationSystem()

def get_current_user(token: str, db: Session) -> Optional[User]:
    """現在のユーザーを取得（便利関数）"""
    return auth_system.get_user_by_token(token, db)