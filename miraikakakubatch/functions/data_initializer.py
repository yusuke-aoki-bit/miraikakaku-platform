#!/usr/bin/env python3
"""
Cloud SQL データ初期化モジュール
4,168社の日本株データを投入
"""

import os
import logging
from datetime import datetime
from sqlalchemy import text

# ロギング設定
logger = logging.getLogger(__name__)

# 日本株データのインポート
import sys
sys.path.append('/app')

try:
    from database.cloud_sql import db_manager
    from comprehensive_japanese_stocks_enhanced import COMPREHENSIVE_JAPANESE_STOCKS
    INITIALIZATION_AVAILABLE = True
except ImportError as e:
    logger.warning(f"Initialization module import failed: {e}")
    INITIALIZATION_AVAILABLE = False
    COMPREHENSIVE_JAPANESE_STOCKS = {}

class CloudSQLInitializer:
    def __init__(self):
        self.db_manager = db_manager
        
    def initialize_stock_master_data(self):
        """株式マスターデータを初期化"""
        if not INITIALIZATION_AVAILABLE:
            logger.error("Initialization not available - missing dependencies")
            return False
            
        try:
            session = self.db_manager.get_session()
            if not session:
                logger.error("Database session not available")
                return False
            
            logger.info(f"株式マスターデータ初期化開始: {len(COMPREHENSIVE_JAPANESE_STOCKS)}社")
            
            # 既存の日本株データを削除
            result = session.execute(text("DELETE FROM stock_master WHERE country = 'Japan'"))
            deleted_count = result.rowcount
            logger.info(f"既存日本株データ削除: {deleted_count}件")
            
            # バッチ投入
            batch_size = 500
            batch_values = []
            total_inserted = 0
            
            for symbol, info in COMPREHENSIVE_JAPANESE_STOCKS.items():
                name_escaped = info['name'].replace("'", "''")
                batch_values.append(f"""(
                    '{symbol}',
                    '{name_escaped}',
                    '{info['sector']}',
                    '{info['market']}',
                    'Japan',
                    'JPY',
                    true,
                    NOW(),
                    NOW()
                )""")
                
                if len(batch_values) >= batch_size:
                    # バッチ実行
                    insert_sql = f"""
                    INSERT INTO stock_master 
                    (symbol, name, sector, market, country, currency, is_active, created_at, updated_at)
                    VALUES {','.join(batch_values)}
                    """
                    
                    session.execute(text(insert_sql))
                    session.commit()
                    
                    total_inserted += len(batch_values)
                    logger.info(f"投入進捗: {total_inserted}/{len(COMPREHENSIVE_JAPANESE_STOCKS)}")
                    batch_values = []
            
            # 残りのデータを投入
            if batch_values:
                insert_sql = f"""
                INSERT INTO stock_master 
                (symbol, name, sector, market, country, currency, is_active, created_at, updated_at)
                VALUES {','.join(batch_values)}
                """
                
                session.execute(text(insert_sql))
                session.commit()
                total_inserted += len(batch_values)
            
            # 検証
            result = session.execute(text("""
                SELECT market, COUNT(*) as count 
                FROM stock_master 
                WHERE country = 'Japan' 
                GROUP BY market
            """))
            
            logger.info("=== 投入結果検証 ===")
            grand_total = 0
            for row in result:
                logger.info(f"{row.market}: {row.count}社")
                grand_total += row.count
            
            logger.info(f"総投入数: {grand_total}社")
            session.close()
            
            if grand_total == len(COMPREHENSIVE_JAPANESE_STOCKS):
                logger.info("🎉 株式マスターデータ投入完了！")
                return True
            else:
                logger.error(f"データ不整合: 期待{len(COMPREHENSIVE_JAPANESE_STOCKS)}社 実際{grand_total}社")
                return False
                
        except Exception as e:
            logger.error(f"株式マスターデータ投入エラー: {e}")
            if 'session' in locals():
                session.rollback()
                session.close()
            return False
    
    def get_initialization_status(self):
        """初期化状況を取得"""
        try:
            if not INITIALIZATION_AVAILABLE:
                return {
                    "status": "unavailable",
                    "message": "Initialization module not available",
                    "japanese_stocks": 0
                }
            
            session = self.db_manager.get_session()
            if not session:
                return {
                    "status": "no_connection",
                    "message": "Database connection not available",
                    "japanese_stocks": 0
                }
            
            result = session.execute(text("""
                SELECT COUNT(*) as count 
                FROM stock_master 
                WHERE country = 'Japan'
            """))
            
            japanese_count = result.scalar()
            session.close()
            
            return {
                "status": "ready" if japanese_count > 0 else "empty",
                "message": f"Japanese stocks in database: {japanese_count}",
                "japanese_stocks": japanese_count,
                "available_stocks": len(COMPREHENSIVE_JAPANESE_STOCKS),
                "initialization_available": INITIALIZATION_AVAILABLE
            }
            
        except Exception as e:
            logger.error(f"Status check error: {e}")
            return {
                "status": "error",
                "message": str(e),
                "japanese_stocks": 0
            }

# グローバルインスタンス
initializer = CloudSQLInitializer() if INITIALIZATION_AVAILABLE else None