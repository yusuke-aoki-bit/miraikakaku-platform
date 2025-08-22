# Cloud SQL専用データベース設定（SQLiteフォールバックなし）
from .cloud_sql_only import get_db, get_engine, init_database, test_connection

# エンジンをエクスポート（互換性のため）
engine = get_engine()

# SessionLocalはget_dbを使用
SessionLocal = None  # 直接使用は非推奨

async def init_database_async():
    """非同期データベース初期化（互換性のため）"""
    init_database()