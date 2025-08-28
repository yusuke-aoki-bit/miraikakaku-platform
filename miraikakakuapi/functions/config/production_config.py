"""
Production Configuration Constants
本番環境用の設定定数
"""

import os
from typing import List


class DatabaseConfig:
    """データベース設定"""

    CONNECTION_POOL_SIZE = int(os.getenv("DB_POOL_SIZE", "20"))
    CONNECTION_POOL_MAX_OVERFLOW = int(os.getenv("DB_POOL_MAX_OVERFLOW", "10"))
    CONNECTION_TIMEOUT = int(os.getenv("DB_CONNECTION_TIMEOUT", "30"))


class CacheConfig:
    """キャッシュ設定"""

    DEFAULT_TIMEOUT = int(os.getenv("CACHE_TIMEOUT", "300"))  # 5分
    PRICE_DATA_TIMEOUT = int(os.getenv("CACHE_PRICE_TIMEOUT", "60"))  # 1分
    PREDICTION_TIMEOUT = int(
        os.getenv(
            "CACHE_PREDICTION_TIMEOUT",
            "1800"))  # 30分
    ML_MODEL_TIMEOUT = int(os.getenv("CACHE_ML_TIMEOUT", "3600"))  # 1時間


class MLConfig:
    """機械学習設定"""

    PRICE_DATA_THRESHOLD = int(os.getenv("ML_PRICE_THRESHOLD", "10000"))
    PREDICTION_DATA_THRESHOLD = int(
        os.getenv("ML_PREDICTION_THRESHOLD", "5000"))
    MIN_TRAINING_SAMPLES = int(os.getenv("ML_MIN_SAMPLES", "1000"))
    MODEL_CONFIDENCE_THRESHOLD = float(
        os.getenv("ML_CONFIDENCE_THRESHOLD", "0.7"))


class APIConfig:
    """API設定"""

    MAX_REQUESTS_PER_MINUTE = int(os.getenv("API_RATE_LIMIT", "1000"))
    DEFAULT_PAGE_SIZE = int(os.getenv("API_PAGE_SIZE", "20"))
    MAX_PAGE_SIZE = int(os.getenv("API_MAX_PAGE_SIZE", "100"))
    REQUEST_TIMEOUT = int(os.getenv("API_TIMEOUT", "30"))


class SecurityConfig:
    """セキュリティ設定"""

    ALLOWED_ORIGINS: List[str] = [
        origin.strip()
        for origin in os.getenv("CORS_ALLOWED_ORIGINS", "").split(",")
        if origin.strip()
    ]
    JWT_EXPIRATION_HOURS = int(os.getenv("JWT_EXPIRATION_HOURS", "24"))
    PASSWORD_MIN_LENGTH = int(os.getenv("PASSWORD_MIN_LENGTH", "8"))
    MAX_LOGIN_ATTEMPTS = int(os.getenv("MAX_LOGIN_ATTEMPTS", "5"))
    LOCKOUT_DURATION_MINUTES = int(os.getenv("LOCKOUT_DURATION", "15"))


class FinanceConfig:
    """ファイナンス設定"""

    DEFAULT_PREDICTION_DAYS = int(os.getenv("DEFAULT_PREDICTION_DAYS", "7"))
    MAX_PREDICTION_DAYS = int(os.getenv("MAX_PREDICTION_DAYS", "30"))
    PRICE_HISTORY_DAYS = int(os.getenv("PRICE_HISTORY_DAYS", "365"))

    # 技術指標設定
    RSI_PERIOD = int(os.getenv("RSI_PERIOD", "14"))
    MACD_FAST_PERIOD = int(os.getenv("MACD_FAST", "12"))
    MACD_SLOW_PERIOD = int(os.getenv("MACD_SLOW", "26"))
    MACD_SIGNAL_PERIOD = int(os.getenv("MACD_SIGNAL", "9"))
    SMA_SHORT_PERIOD = int(os.getenv("SMA_SHORT", "20"))
    SMA_LONG_PERIOD = int(os.getenv("SMA_LONG", "50"))

    # ボラティリティ閾値
    HIGH_VOLATILITY_THRESHOLD = float(os.getenv("HIGH_VOLATILITY", "0.05"))
    LOW_VOLATILITY_THRESHOLD = float(os.getenv("LOW_VOLATILITY", "0.01"))

    # ML判定閾値
    ML_READINESS_THRESHOLD = int(os.getenv("ML_READINESS_SCORE", "70"))
    MIN_STOCK_DATA_FOR_CALCULATION = int(os.getenv("MIN_STOCK_DATA", "20"))
    VOLUME_RANKING_LIMIT = int(os.getenv("VOLUME_RANKING_LIMIT", "50"))

    # スコア計算設定
    PRICE_DATA_MAX_SCORE = 40
    PREDICTION_DATA_MAX_SCORE = 30
    SYMBOL_COVERAGE_MAX_SCORE = 20
    DATA_DIVERSITY_MAX_SCORE = 10

    # 信頼度とパーセンテージ設定
    DEFAULT_CONFIDENCE_BASE = 90
    CONFIDENCE_DECAY_RATE = 5
    MIN_CONFIDENCE = 50
    PERCENTAGE_MULTIPLIER = 100


class ForexConfig:
    """外国為替設定"""

    # デフォルト設定
    DEFAULT_HISTORY_DAYS = int(os.getenv("FOREX_DEFAULT_HISTORY_DAYS", "30"))
    MAX_HISTORY_DAYS = int(os.getenv("FOREX_MAX_HISTORY_DAYS", "365"))
    DEFAULT_PREDICTION_LIMIT = int(os.getenv("FOREX_PREDICTION_LIMIT", "7"))
    MAX_PREDICTION_LIMIT = int(os.getenv("FOREX_MAX_PREDICTION_LIMIT", "30"))

    # スプレッド設定
    DEFAULT_SPREAD_PERCENTAGE = float(
        os.getenv("FOREX_SPREAD_PERCENTAGE", "0.0001")
    )  # 0.01%

    # ボラティリティ設定
    BASE_VOLATILITY_PERCENTAGE = float(
        os.getenv("FOREX_BASE_VOLATILITY", "0.01"))  # 1%
    VOLATILITY_INCREASE_RATE = float(
        os.getenv("FOREX_VOLATILITY_INCREASE", "0.1"))
    VOLATILITY_BASE_FACTOR = float(os.getenv("FOREX_VOLATILITY_BASE", "0.8"))

    # 予測設定
    TREND_FACTOR_BASE = float(os.getenv("FOREX_TREND_FACTOR", "0.001"))
    PREDICTION_CONFIDENCE_BASE = int(os.getenv("FOREX_CONFIDENCE_BASE", "95"))
    PREDICTION_CONFIDENCE_DECAY = int(os.getenv("FOREX_CONFIDENCE_DECAY", "2"))

    # 時間枠設定 (月日数)
    MONTH_DAYS = int(os.getenv("FOREX_MONTH_DAYS", "30"))


class WebSocketConfig:
    """WebSocket設定"""

    # 更新間隔 (秒)
    DEFAULT_UPDATE_INTERVAL = int(os.getenv("WS_UPDATE_INTERVAL", "5"))
    SYMBOL_UPDATE_INTERVAL = int(os.getenv("WS_SYMBOL_UPDATE_INTERVAL", "3"))

    # 接続設定
    MAX_CONNECTIONS = int(os.getenv("WS_MAX_CONNECTIONS", "1000"))
    CONNECTION_TIMEOUT = int(os.getenv("WS_TIMEOUT", "300"))  # 5分

    # プロダクション環境でのモックデータ無効化
    ENABLE_MOCK_DATA = os.getenv(
        "WS_ENABLE_MOCK_DATA",
        "false").lower() == "true"


class LoggingConfig:
    """ロギング設定"""

    ENABLE_DEBUG = os.getenv("ENABLE_DEBUG_LOGGING", "false").lower() == "true"
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
    LOG_FORMAT = os.getenv(
        "LOG_FORMAT", "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    MAX_LOG_FILE_SIZE = int(os.getenv("MAX_LOG_SIZE", "10485760"))  # 10MB


class MonitoringConfig:
    """監視設定"""

    HEALTH_CHECK_TIMEOUT = int(os.getenv("HEALTH_CHECK_TIMEOUT", "5"))
    METRICS_COLLECTION_INTERVAL = int(os.getenv("METRICS_INTERVAL", "60"))
    ERROR_ALERT_THRESHOLD = int(os.getenv("ERROR_ALERT_THRESHOLD", "10"))


class BusinessConfig:
    """ビジネスロジック設定"""

    # ユーザー設定
    DEFAULT_INVESTMENT_STYLE = os.getenv(
        "DEFAULT_INVESTMENT_STYLE", "moderate")
    DEFAULT_RISK_TOLERANCE = os.getenv("DEFAULT_RISK_TOLERANCE", "medium")

    # ポートフォリオ設定
    MIN_PORTFOLIO_VALUE = float(os.getenv("MIN_PORTFOLIO_VALUE", "1000.0"))
    MAX_PORTFOLIO_POSITIONS = int(os.getenv("MAX_PORTFOLIO_POSITIONS", "50"))

    # ウォッチリスト設定
    MAX_WATCHLIST_ITEMS = int(os.getenv("MAX_WATCHLIST_ITEMS", "100"))

    # コンテスト設定
    DEFAULT_CONTEST_DURATION_DAYS = int(
        os.getenv("CONTEST_DURATION_DAYS", "7"))
    MAX_PREDICTIONS_PER_USER = int(os.getenv("MAX_PREDICTIONS_PER_USER", "10"))


# 環境確認
def validate_production_config():
    """本番環境設定の妥当性を確認"""
    required_vars = [
        "DATABASE_URL",
        "CORS_ALLOWED_ORIGINS",
        "JWT_SECRET_KEY",
    ]

    missing = []
    for var in required_vars:
        if not os.getenv(var):
            missing.append(var)

    if missing:
        raise ValueError(f"必須の環境変数が設定されていません: {', '.join(missing)}")

    # セキュリティチェック
    if not SecurityConfig.ALLOWED_ORIGINS:
        raise ValueError("CORS_ALLOWED_ORIGINSが設定されていません")

    if "*" in SecurityConfig.ALLOWED_ORIGINS:
        raise ValueError("本番環境でCORS_ALLOWED_ORIGINSに'*'は使用できません")
