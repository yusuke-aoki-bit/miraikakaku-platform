from sqlalchemy.orm import Session
from database.models.users import User
from datetime import datetime, timedelta
import jwt
import bcrypt
import os
from typing import Optional


class AuthService:
    def __init__(self, db: Session):
        self.db = db
        self.jwt_secret = os.getenv("JWT_SECRET", "secret-key")
        self.jwt_algorithm = "HS256"
        self.access_token_expire_hours = 24

    async def authenticate_user(self, email: str, password: str) -> Optional[User]:
        """ユーザー認証"""
        user = self.db.query(User).filter(User.email == email).first()

        if not user:
            return None

        if not self.verify_password(password, user.hashed_password):
            return None

        # 最終ログイン時刻を更新
        user.last_login = datetime.utcnow()
        self.db.commit()

        return user

    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """パスワード検証"""
        return bcrypt.checkpw(
            plain_password.encode("utf-8"), hashed_password.encode("utf-8")
        )

    def hash_password(self, password: str) -> str:
        """パスワードハッシュ化"""
        salt = bcrypt.gensalt()
        return bcrypt.hashpw(password.encode("utf-8"), salt).decode("utf-8")

    def create_access_token(self, user_id: int) -> str:
        """アクセストークン生成"""
        expire = datetime.utcnow() + timedelta(hours=self.access_token_expire_hours)
        payload = {
            "sub": str(user_id),
            "exp": expire,
            "iat": datetime.utcnow(),
            "type": "access",
        }
        return jwt.encode(payload, self.jwt_secret, algorithm=self.jwt_algorithm)

    async def get_user_by_id(self, user_id: str) -> Optional[User]:
        """IDでユーザーを取得"""
        return self.db.query(User).filter(User.id == int(user_id)).first()

    async def create_user(
        self, email: str, password: str, name: str, role: str = "user"
    ) -> User:
        """新規ユーザー作成"""
        # 既存ユーザーチェック
        existing_user = self.db.query(User).filter(User.email == email).first()
        if existing_user:
            raise ValueError("このメールアドレスは既に登録されています")

        # パスワードハッシュ化
        hashed_password = self.hash_password(password)

        # ユーザー作成
        user = User(
            email=email,
            hashed_password=hashed_password,
            name=name,
            role=role,
            is_active=True,
        )

        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)

        return user
