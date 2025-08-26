from typing import List, Dict, Any, Optional
from enum import Enum
import logging

logger = logging.getLogger(__name__)


class Permission(Enum):
    # 株式データ関連
    READ_STOCK_DATA = "read_stock_data"
    WRITE_STOCK_DATA = "write_stock_data"
    DELETE_STOCK_DATA = "delete_stock_data"

    # 予測関連
    READ_PREDICTIONS = "read_predictions"
    CREATE_PREDICTIONS = "create_predictions"
    DELETE_PREDICTIONS = "delete_predictions"

    # ユーザー管理
    READ_USERS = "read_users"
    CREATE_USERS = "create_users"
    UPDATE_USERS = "update_users"
    DELETE_USERS = "delete_users"

    # システム管理
    READ_SYSTEM_LOGS = "read_system_logs"
    MANAGE_SYSTEM = "manage_system"
    ACCESS_ADMIN_PANEL = "access_admin_panel"

    # ML関連
    TRAIN_MODELS = "train_models"
    DEPLOY_MODELS = "deploy_models"
    ACCESS_ML_PIPELINE = "access_ml_pipeline"


class Role(Enum):
    ADMIN = "admin"
    ANALYST = "analyst"
    USER = "user"
    READONLY = "readonly"


class RBACService:
    def __init__(self):
        self.role_permissions = self._initialize_role_permissions()

    def _initialize_role_permissions(self) -> Dict[Role, List[Permission]]:
        """ロール別権限を初期化"""
        return {
            Role.ADMIN: [
                # 全権限
                Permission.READ_STOCK_DATA,
                Permission.WRITE_STOCK_DATA,
                Permission.DELETE_STOCK_DATA,
                Permission.READ_PREDICTIONS,
                Permission.CREATE_PREDICTIONS,
                Permission.DELETE_PREDICTIONS,
                Permission.READ_USERS,
                Permission.CREATE_USERS,
                Permission.UPDATE_USERS,
                Permission.DELETE_USERS,
                Permission.READ_SYSTEM_LOGS,
                Permission.MANAGE_SYSTEM,
                Permission.ACCESS_ADMIN_PANEL,
                Permission.TRAIN_MODELS,
                Permission.DEPLOY_MODELS,
                Permission.ACCESS_ML_PIPELINE,
            ],
            Role.ANALYST: [
                # 分析関連権限
                Permission.READ_STOCK_DATA,
                Permission.WRITE_STOCK_DATA,
                Permission.READ_PREDICTIONS,
                Permission.CREATE_PREDICTIONS,
                Permission.TRAIN_MODELS,
                Permission.ACCESS_ML_PIPELINE,
            ],
            Role.USER: [
                # 基本ユーザー権限
                Permission.READ_STOCK_DATA,
                Permission.READ_PREDICTIONS,
            ],
            Role.READONLY: [
                # 読み取り専用
                Permission.READ_STOCK_DATA,
                Permission.READ_PREDICTIONS,
            ],
        }

    def has_permission(self, user_role: str, required_permission: Permission) -> bool:
        """ユーザーが特定の権限を持っているかチェック"""
        try:
            role = Role(user_role.lower())
            return required_permission in self.role_permissions.get(role, [])
        except ValueError:
            logger.warning(f"未知のロール: {user_role}")
            return False

    def has_any_permission(
        self, user_role: str, required_permissions: List[Permission]
    ) -> bool:
        """いずれかの権限を持っているかチェック"""
        return any(
            self.has_permission(user_role, perm) for perm in required_permissions
        )

    def has_all_permissions(
        self, user_role: str, required_permissions: List[Permission]
    ) -> bool:
        """すべての権限を持っているかチェック"""
        return all(
            self.has_permission(user_role, perm) for perm in required_permissions
        )

    def get_user_permissions(self, user_role: str) -> List[str]:
        """ユーザーの権限一覧を取得"""
        try:
            role = Role(user_role.lower())
            permissions = self.role_permissions.get(role, [])
            return [perm.value for perm in permissions]
        except ValueError:
            return []

    def can_access_endpoint(self, user_role: str, endpoint: str, method: str) -> bool:
        """エンドポイント/メソッドへのアクセス権限をチェック"""
        endpoint_permissions = {
            # 株式データエンドポイント
            ("GET", "/api/finance/stocks/search"): [Permission.READ_STOCK_DATA],
            ("GET", "/api/finance/stocks/{symbol}/price"): [Permission.READ_STOCK_DATA],
            ("GET", "/api/finance/stocks/{symbol}/predictions"): [
                Permission.READ_PREDICTIONS
            ],
            ("POST", "/api/finance/stocks/{symbol}/predict"): [
                Permission.CREATE_PREDICTIONS
            ],
            ("DELETE", "/api/finance/stocks/{symbol}/predictions/{id}"): [
                Permission.DELETE_PREDICTIONS
            ],
            # 管理エンドポイント
            ("GET", "/api/admin/users"): [Permission.READ_USERS],
            ("POST", "/api/admin/users"): [Permission.CREATE_USERS],
            ("PUT", "/api/admin/users/{id}"): [Permission.UPDATE_USERS],
            ("DELETE", "/api/admin/users/{id}"): [Permission.DELETE_USERS],
            ("GET", "/api/admin/system/logs"): [Permission.READ_SYSTEM_LOGS],
            ("POST", "/api/admin/system/restart"): [Permission.MANAGE_SYSTEM],
            # ML関連エンドポイント
            ("POST", "/api/ml/train"): [Permission.TRAIN_MODELS],
            ("POST", "/api/ml/deploy"): [Permission.DEPLOY_MODELS],
            ("GET", "/api/ml/pipeline/status"): [Permission.ACCESS_ML_PIPELINE],
        }

        # パスパラメータを正規化
        normalized_endpoint = self._normalize_endpoint_path(endpoint)
        key = (method.upper(), normalized_endpoint)

        required_permissions = endpoint_permissions.get(key, [])

        if not required_permissions:
            # 定義されていないエンドポイントは基本権限でアクセス可能
            return self.has_permission(user_role, Permission.READ_STOCK_DATA)

        return self.has_any_permission(user_role, required_permissions)

    def _normalize_endpoint_path(self, path: str) -> str:
        """エンドポイントパスを正規化（パスパラメータを{param}形式に）"""
        import re

        # UUIDやIDパターンを{id}に置換
        path = re.sub(r"/[a-f0-9-]{36}", "/{id}", path)  # UUID
        path = re.sub(r"/\d+", "/{id}", path)  # 数値ID
        # 株式シンボルパターンを{symbol}に置換
        path = re.sub(r"/[A-Z]{1,5}(?=/|$)", "/{symbol}", path)
        return path

    def get_role_hierarchy(self) -> Dict[Role, int]:
        """ロール階層を取得（数値が高いほど上位）"""
        return {Role.READONLY: 1, Role.USER: 2, Role.ANALYST: 3, Role.ADMIN: 4}

    def is_role_higher_or_equal(self, user_role: str, required_role: str) -> bool:
        """ユーザーロールが要求ロール以上かチェック"""
        try:
            hierarchy = self.get_role_hierarchy()
            user_level = hierarchy.get(Role(user_role.lower()), 0)
            required_level = hierarchy.get(Role(required_role.lower()), 999)
            return user_level >= required_level
        except ValueError:
            return False


# グローバルインスタンス
rbac_service = RBACService()
