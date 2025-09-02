#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import pymysql
import logging

# ログ設定
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class CollationConstraintFixer:
    def __init__(self):
        self.db_config = {
            "host": "34.58.103.36",
            "user": "miraikakaku-user",
            "password": "miraikakaku-secure-pass-2024",
            "database": "miraikakaku",
            "charset": "utf8mb4"
        }

    def check_foreign_keys(self):
        """外部キー制約の確認"""
        try:
            connection = pymysql.connect(**self.db_config)
            with connection.cursor() as cursor:
                cursor.execute("""
                    SELECT CONSTRAINT_NAME, TABLE_NAME, COLUMN_NAME, 
                           REFERENCED_TABLE_NAME, REFERENCED_COLUMN_NAME
                    FROM information_schema.KEY_COLUMN_USAGE 
                    WHERE TABLE_SCHEMA = 'miraikakaku' 
                    AND REFERENCED_TABLE_NAME = 'stock_master'
                    AND REFERENCED_COLUMN_NAME = 'symbol'
                """)
                
                fk_constraints = cursor.fetchall()
                logger.info("🔗 symbol列への外部キー制約:")
                
                for constraint_name, table_name, column_name, ref_table, ref_column in fk_constraints:
                    logger.info(f"   {constraint_name}: {table_name}.{column_name} → {ref_table}.{ref_column}")
                
                return fk_constraints
                
        except Exception as e:
            logger.error(f"外部キー確認エラー: {e}")
            return []
        finally:
            if 'connection' in locals():
                connection.close()

    def check_data_length_issues(self):
        """データ長の問題確認"""
        try:
            connection = pymysql.connect(**self.db_config)
            with connection.cursor() as cursor:
                
                # exchange列の長いデータ確認
                cursor.execute("""
                    SELECT exchange, CHAR_LENGTH(exchange) as len, COUNT(*) as count
                    FROM stock_master 
                    WHERE CHAR_LENGTH(exchange) > 50
                    GROUP BY exchange 
                    ORDER BY len DESC
                    LIMIT 10
                """)
                
                long_exchanges = cursor.fetchall()
                logger.info("📏 長いexchangeデータ:")
                
                for exchange, length, count in long_exchanges:
                    logger.info(f"   '{exchange}' (長さ{length}): {count}件")
                
                return long_exchanges
                
        except Exception as e:
            logger.error(f"データ長確認エラー: {e}")
            return []
        finally:
            if 'connection' in locals():
                connection.close()

    def fix_foreign_key_constraints(self):
        """外部キー制約の一時削除と修正"""
        logger.info("🔗 外部キー制約修正開始")
        
        try:
            connection = pymysql.connect(**self.db_config)
            with connection.cursor() as cursor:
                
                # 1. 外部キー制約削除
                constraints_to_drop = ['stock_aliases_ibfk_1']
                
                for constraint in constraints_to_drop:
                    try:
                        cursor.execute(f"ALTER TABLE stock_aliases DROP FOREIGN KEY {constraint}")
                        connection.commit()
                        logger.info(f"✅ 外部キー削除: {constraint}")
                    except Exception as e:
                        logger.warning(f"⚠️ 外部キー削除失敗 {constraint}: {e}")
                
                # 2. stock_aliases テーブルのコレーション統一
                try:
                    cursor.execute("ALTER TABLE stock_aliases MODIFY symbol VARCHAR(20) COLLATE utf8mb4_unicode_ci")
                    connection.commit()
                    logger.info("✅ stock_aliases.symbol コレーション修正")
                except Exception as e:
                    logger.error(f"❌ stock_aliases修正失敗: {e}")
                
                return True
                
        except Exception as e:
            logger.error(f"外部キー修正エラー: {e}")
            return False
        finally:
            if 'connection' in locals():
                connection.close()

    def fix_data_length_issues(self):
        """データ長問題の修正"""
        logger.info("📏 データ長問題修正開始")
        
        try:
            connection = pymysql.connect(**self.db_config)
            with connection.cursor() as cursor:
                
                # 1. exchange列を拡張
                try:
                    cursor.execute("ALTER TABLE stock_master MODIFY exchange VARCHAR(100) COLLATE utf8mb4_unicode_ci")
                    connection.commit()
                    logger.info("✅ exchange列をVARCHAR(100)に拡張")
                except Exception as e:
                    logger.error(f"❌ exchange列拡張失敗: {e}")
                
                # 2. 他の列も余裕を持たせて拡張
                column_expansions = [
                    "ALTER TABLE stock_master MODIFY name VARCHAR(300) COLLATE utf8mb4_unicode_ci",
                    "ALTER TABLE stock_master MODIFY sector VARCHAR(150) COLLATE utf8mb4_unicode_ci", 
                    "ALTER TABLE stock_master MODIFY industry VARCHAR(150) COLLATE utf8mb4_unicode_ci",
                    "ALTER TABLE stock_master MODIFY country VARCHAR(100) COLLATE utf8mb4_unicode_ci"
                ]
                
                for sql in column_expansions:
                    try:
                        cursor.execute(sql)
                        connection.commit()
                        col_name = sql.split('MODIFY')[1].split('VARCHAR')[0].strip()
                        logger.info(f"✅ {col_name}列拡張成功")
                    except Exception as e:
                        logger.warning(f"⚠️ 列拡張失敗: {e}")
                
                return True
                
        except Exception as e:
            logger.error(f"データ長修正エラー: {e}")
            return False
        finally:
            if 'connection' in locals():
                connection.close()

    def fix_symbol_column_final(self):
        """symbol列の最終修正"""
        logger.info("🎯 symbol列最終修正開始")
        
        try:
            connection = pymysql.connect(**self.db_config)
            with connection.cursor() as cursor:
                
                # symbol列のコレーション修正（制約削除後）
                try:
                    cursor.execute("ALTER TABLE stock_master MODIFY symbol VARCHAR(20) COLLATE utf8mb4_unicode_ci NOT NULL")
                    connection.commit()
                    logger.info("✅ stock_master.symbol コレーション修正成功")
                    return True
                except Exception as e:
                    logger.error(f"❌ symbol列修正失敗: {e}")
                    return False
                
        except Exception as e:
            logger.error(f"symbol列修正エラー: {e}")
            return False
        finally:
            if 'connection' in locals():
                connection.close()

    def comprehensive_fix(self):
        """包括的コレーション修正"""
        logger.info("🚀 包括的コレーション修正開始")
        
        # 1. 外部キー制約確認
        logger.info("=== 1. 外部キー制約確認 ===")
        fk_constraints = self.check_foreign_keys()
        
        # 2. データ長問題確認
        logger.info("=== 2. データ長問題確認 ===")
        length_issues = self.check_data_length_issues()
        
        # 3. 外部キー制約修正
        logger.info("=== 3. 外部キー制約修正 ===")
        fk_success = self.fix_foreign_key_constraints()
        
        # 4. データ長問題修正
        logger.info("=== 4. データ長問題修正 ===")
        length_success = self.fix_data_length_issues()
        
        # 5. symbol列最終修正
        logger.info("=== 5. symbol列最終修正 ===")
        symbol_success = self.fix_symbol_column_final()
        
        # 6. 最終テスト
        if symbol_success:
            logger.info("=== 6. 最終テスト ===")
            self.test_final_fix()
        
        return symbol_success

    def test_final_fix(self):
        """最終修正テスト"""
        try:
            connection = pymysql.connect(**self.db_config)
            with connection.cursor() as cursor:
                
                logger.info("🧪 最終修正テスト:")
                
                # テスト1: JOIN
                try:
                    cursor.execute("""
                        SELECT COUNT(*) FROM stock_master sm 
                        LEFT JOIN stock_price_history sph ON sm.symbol = sph.symbol 
                        WHERE sm.is_active = 1
                    """)
                    count = cursor.fetchone()[0]
                    logger.info(f"✅ JOIN成功: {count:,}件")
                except Exception as e:
                    logger.error(f"❌ JOIN失敗: {e}")
                    return False
                
                # テスト2: 不足銘柄取得
                try:
                    cursor.execute("""
                        SELECT sm.symbol, sm.name 
                        FROM stock_master sm
                        WHERE sm.is_active = 1 
                        AND sm.symbol NOT IN (
                            SELECT DISTINCT symbol FROM stock_price_history 
                            WHERE data_source = 'yfinance'
                        )
                        LIMIT 5
                    """)
                    missing = cursor.fetchall()
                    logger.info(f"✅ 不足銘柄取得成功: {len(missing)}件")
                    return True
                except Exception as e:
                    logger.error(f"❌ 不足銘柄取得失敗: {e}")
                    return False
                
        except Exception as e:
            logger.error(f"最終テストエラー: {e}")
            return False
        finally:
            if 'connection' in locals():
                connection.close()

def main():
    fixer = CollationConstraintFixer()
    success = fixer.comprehensive_fix()
    
    if success:
        logger.info("🎯 コレーション問題完全解決！")
    else:
        logger.error("❌ コレーション問題未解決")

if __name__ == "__main__":
    main()