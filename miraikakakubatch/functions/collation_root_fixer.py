#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import psycopg2
import psycopg2.extras
import logging
from datetime import datetime

# ログ設定
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class CollationRootFixer:
    def __init__(self):
        self.db_config = {
            "host": "34.173.9.214",
            "user": "postgres",
            "password": "miraikakaku-postgres-secure-2024",
            "database": "miraikakaku",
            "port": 5432
        }

    def fix_stock_master_collation(self):
        """stock_masterテーブルのコレーション修正"""
        logger.info("🔧 stock_masterコレーション修正開始")
        
        # 修正するカラムと正確な定義
        column_fixes = [
            "ALTER TABLE stock_master MODIFY symbol VARCHAR(20) COLLATE utf8mb4_unicode_ci NOT NULL",
            "ALTER TABLE stock_master MODIFY name VARCHAR(255) COLLATE utf8mb4_unicode_ci NULL",
            "ALTER TABLE stock_master MODIFY exchange VARCHAR(50) COLLATE utf8mb4_unicode_ci NULL",
            "ALTER TABLE stock_master MODIFY market VARCHAR(50) COLLATE utf8mb4_unicode_ci NULL", 
            "ALTER TABLE stock_master MODIFY sector VARCHAR(100) COLLATE utf8mb4_unicode_ci NULL",
            "ALTER TABLE stock_master MODIFY industry VARCHAR(100) COLLATE utf8mb4_unicode_ci NULL",
            "ALTER TABLE stock_master MODIFY country VARCHAR(50) COLLATE utf8mb4_unicode_ci NULL",
            "ALTER TABLE stock_master MODIFY website VARCHAR(255) COLLATE utf8mb4_unicode_ci NULL",
            "ALTER TABLE stock_master MODIFY description TEXT COLLATE utf8mb4_unicode_ci NULL",
            "ALTER TABLE stock_master MODIFY currency VARCHAR(10) COLLATE utf8mb4_unicode_ci NULL"
        ]
        
        try:
            connection = psycopg2.connect(**self.db_config)
            with connection.cursor() as cursor:
                
                success_count = 0
                for i, sql in enumerate(column_fixes, 1):
                    try:
                        logger.info(f"🔧 修正 {i}/{len(column_fixes)}: {sql.split('MODIFY')[1].split('COLLATE')[0].strip()}")
                        cursor.execute(sql)
                        connection.commit()
                        success_count += 1
                        logger.info(f"✅ 修正 {i} 成功")
                    except Exception as e:
                        logger.error(f"❌ 修正 {i} 失敗: {e}")
                        connection.rollback()
                        continue
                
                logger.info(f"🎯 stock_master修正完了: {success_count}/{len(column_fixes)}成功")
                return success_count > 0
                
        except Exception as e:
            logger.error(f"stock_master修正エラー: {e}")
            return False
        finally:
            if 'connection' in locals():
                connection.close()

    def test_collation_fix(self):
        """コレーション修正効果のテスト"""
        logger.info("🧪 コレーション修正効果テスト")
        
        try:
            connection = psycopg2.connect(**self.db_config)
            with connection.cursor() as cursor:
                
                # Test 1: 基本JOIN
                try:
                    cursor.execute("""
                        SELECT COUNT(*) FROM stock_master sm 
                        LEFT JOIN stock_price_history sph ON sm.symbol = sph.symbol 
                        WHERE sm.is_active = 1
                    """)
                    count = cursor.fetchone()[0]
                    logger.info(f"✅ 基本JOIN成功: {count:,}件")
                except Exception as e:
                    logger.error(f"❌ 基本JOIN失敗: {e}")
                    return False
                
                # Test 2: 不足銘柄取得
                try:
                    cursor.execute("""
                        SELECT sm.symbol, sm.name, sm.country
                        FROM stock_master sm
                        WHERE sm.is_active = 1 
                        AND sm.symbol NOT IN (
                            SELECT DISTINCT symbol FROM stock_price_history 
                            WHERE data_source = 'yfinance'
                        )
                        ORDER BY 
                            CASE WHEN sm.country = 'US' THEN 1 ELSE 2 END,
                            sm.symbol
                        LIMIT 20
                    """)
                    missing_symbols = cursor.fetchall()
                    logger.info(f"✅ 不足銘柄取得成功: {len(missing_symbols)}件")
                    
                    if missing_symbols:
                        logger.info("📋 不足銘柄例:")
                        for symbol, name, country in missing_symbols[:5]:
                            logger.info(f"   {symbol} ({country}): {name}")
                    
                    return len(missing_symbols) > 0
                    
                except Exception as e:
                    logger.error(f"❌ 不足銘柄取得失敗: {e}")
                    return False
                
        except Exception as e:
            logger.error(f"テストエラー: {e}")
            return False
        finally:
            if 'connection' in locals():
                connection.close()

    def verify_collation_consistency(self):
        """コレーション一貫性の確認"""
        try:
            connection = psycopg2.connect(**self.db_config)
            with connection.cursor() as cursor:
                
                # 重要テーブルのコレーション確認
                tables = ['stock_master', 'stock_price_history', 'stock_predictions']
                
                logger.info("📊 修正後コレーション確認:")
                
                for table in tables:
                    cursor.execute(f"""
                        SELECT COLUMN_NAME, COLLATION_NAME 
                        FROM information_schema.COLUMNS 
                        WHERE TABLE_SCHEMA = 'miraikakaku' 
                        AND TABLE_NAME = '{table}'
                        AND COLUMN_NAME = 'symbol'
                    """)
                    
                    result = cursor.fetchone()
                    if result:
                        col_name, collation = result
                        logger.info(f"   {table}.{col_name}: {collation}")
                        
                        if 'utf8mb4_unicode_ci' in collation:
                            logger.info(f"      ✅ 統一コレーション")
                        else:
                            logger.warning(f"      ⚠️ 不一致コレーション")
                
        except Exception as e:
            logger.error(f"コレーション確認エラー: {e}")
        finally:
            if 'connection' in locals():
                connection.close()

def main():
    logger.info("🔧 コレーション根本修正開始")
    
    fixer = CollationRootFixer()
    
    # 修正実行
    success = fixer.fix_stock_master_collation()
    
    if success:
        logger.info("✅ 修正完了 - 効果テスト中...")
        fixer.verify_collation_consistency()
        test_success = fixer.test_collation_fix()
        
        if test_success:
            logger.info("🎯 コレーション修正成功！JOIN問題解決")
        else:
            logger.warning("⚠️ 修正したが、まだ問題が残存")
    else:
        logger.error("❌ コレーション修正失敗")

if __name__ == "__main__":
    main()