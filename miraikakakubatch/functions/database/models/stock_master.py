# 共通のStockMasterモデルを使用
import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), "../../../../../shared"))

from models.stock_master import StockMaster

# 既存コードとの互換性のため、このファイル内でもStockMasterを再エクスポート
__all__ = ["StockMaster"]
