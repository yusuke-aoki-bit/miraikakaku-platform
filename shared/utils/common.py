"""
共通のユーティリティ関数
"""
import os
from typing import Optional, Dict, Any
from datetime import datetime
import logging

def get_env_var(key: str, default: Optional[str] = None, required: bool = False) -> str:
    """環境変数を安全に取得"""
    value = os.getenv(key, default)
    if required and value is None:
        raise ValueError(f"Required environment variable '{key}' is not set")
    return value

def setup_logging(log_level: str = "INFO") -> logging.Logger:
    """共通のロギング設定"""
    logger = logging.getLogger()
    logger.setLevel(getattr(logging, log_level.upper(), logging.INFO))
    
    if not logger.handlers:
        handler = logging.StreamHandler()
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
    
    return logger

def format_currency(amount: float, currency: str = "USD") -> str:
    """通貨をフォーマット"""
    if currency == "USD":
        return f"${amount:,.2f}"
    elif currency == "JPY":
        return f"¥{amount:,.0f}"
    else:
        return f"{amount:,.2f} {currency}"

def calculate_percentage_change(old_value: float, new_value: float) -> float:
    """パーセンテージ変化を計算"""
    if old_value == 0:
        return 0
    return ((new_value - old_value) / old_value) * 100

def validate_stock_symbol(symbol: str) -> bool:
    """株式シンボルの妥当性をチェック"""
    if not symbol or len(symbol) > 20:
        return False
    return symbol.replace(".", "").replace("-", "").isalnum()