#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import pymysql
import logging

# ログ設定
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class CollationProblemInvestigator:
    def __init__(self):
        self.db_config = {
            "host": "34.58.103.36",
            "user": "miraikakaku-user",
            "password": "miraikakaku-secure-pass-2024",
            "database": "miraikakaku",
            "charset": "utf8mb4"
        }

    def check_database_collation(self):
        """データベース全体のコレーション確認"""
        try:
            connection = pymysql.connect(**self.db_config)
            with connection.cursor() as cursor:
                # データベースのデフォルトコレーション
                cursor.execute("SELECT DEFAULT_COLLATION_NAME FROM information_schema.SCHEMATA WHERE SCHEMA_NAME = 'miraikakaku'")
                db_collation = cursor.fetchone()
                
                logger.info(f"📊 データベースコレーション: {db_collation[0] if db_collation else 'N/A'}")
                
                # 全テーブルのコレーション確認
                cursor.execute("""
                    SELECT TABLE_NAME, TABLE_COLLATION 
                    FROM information_schema.TABLES 
                    WHERE TABLE_SCHEMA = 'miraikakaku'
                    ORDER BY TABLE_NAME
                """)
                
                tables = cursor.fetchall()
                logger.info("📋 テーブル別コレーション:")
                for table_name, collation in tables:
                    logger.info(f"   {table_name}: {collation}")
                
                return tables
                
        except Exception as e:
            logger.error(f"データベースコレーション確認エラー: {e}")
            return []
        finally:
            if 'connection' in locals():
                connection.close()

    def check_column_collations(self):
        """列レベルのコレーション詳細確認"""
        try:
            connection = pymysql.connect(**self.db_config)
            with connection.cursor() as cursor:
                # 重要テーブルの列コレーション確認
                important_tables = ['stock_master', 'stock_price_history', 'stock_predictions']
                
                for table in important_tables:
                    logger.info(f"\n🔍 {table} テーブルの列コレーション:")
                    
                    cursor.execute(f"""
                        SELECT COLUMN_NAME, DATA_TYPE, COLLATION_NAME 
                        FROM information_schema.COLUMNS 
                        WHERE TABLE_SCHEMA = 'miraikakaku' 
                        AND TABLE_NAME = '{table}'
                        AND COLLATION_NAME IS NOT NULL
                        ORDER BY ORDINAL_POSITION
                    """)
                    
                    columns = cursor.fetchall()
                    for col_name, data_type, collation in columns:
                        logger.info(f"   {col_name} ({data_type}): {collation}")
                        
                        # コレーション不一致の検出
                        if collation and 'utf8mb4_0900_ai_ci' in collation:
                            logger.warning(f"⚠️ MySQL 8.0デフォルトコレーション検出: {col_name}")
                        elif collation and 'utf8mb4_unicode_ci' in collation:
                            logger.info(f"✅ 古いMySQLコレーション: {col_name}")
                
        except Exception as e:
            logger.error(f"列コレーション確認エラー: {e}")
        finally:
            if 'connection' in locals():
                connection.close()

    def test_problematic_queries(self):
        """問題のあるクエリのテスト"""
        try:
            connection = pymysql.connect(**self.db_config)
            with connection.cursor() as cursor:
                
                logger.info("🧪 問題クエリのテスト:")
                
                # Test 1: 基本的なJOIN
                try:
                    cursor.execute("""
                        SELECT COUNT(*) FROM stock_master sm 
                        LEFT JOIN stock_price_history sph ON sm.symbol = sph.symbol 
                        LIMIT 1
                    """)
                    result = cursor.fetchone()
                    logger.info("✅ Test 1 (基本JOIN): 成功")
                except Exception as e:
                    logger.error(f"❌ Test 1 (基本JOIN): {e}")
                
                # Test 2: NOT IN サブクエリ
                try:
                    cursor.execute("""
                        SELECT COUNT(*) FROM stock_master 
                        WHERE symbol NOT IN (
                            SELECT DISTINCT symbol FROM stock_price_history 
                            WHERE data_source = 'yfinance'
                        ) LIMIT 1
                    """)
                    result = cursor.fetchone()
                    logger.info("✅ Test 2 (NOT IN): 成功")
                except Exception as e:
                    logger.error(f"❌ Test 2 (NOT IN): {e}")
                
                # Test 3: 直接比較
                try:
                    cursor.execute("""
                        SELECT sm.symbol FROM stock_master sm, stock_price_history sph 
                        WHERE sm.symbol = sph.symbol LIMIT 1
                    """)
                    result = cursor.fetchone()
                    logger.info("✅ Test 3 (直接比較): 成功")
                except Exception as e:
                    logger.error(f"❌ Test 3 (直接比較): {e}")
                
                # Test 4: COLLATE指定
                try:
                    cursor.execute("""
                        SELECT COUNT(*) FROM stock_master sm 
                        LEFT JOIN stock_price_history sph 
                        ON sm.symbol COLLATE utf8mb4_unicode_ci = sph.symbol COLLATE utf8mb4_unicode_ci
                        LIMIT 1
                    """)
                    result = cursor.fetchone()
                    logger.info("✅ Test 4 (COLLATE指定): 成功")
                except Exception as e:
                    logger.error(f"❌ Test 4 (COLLATE指定): {e}")
                
        except Exception as e:
            logger.error(f"クエリテストエラー: {e}")
        finally:
            if 'connection' in locals():
                connection.close()

    def check_mysql_version(self):
        """MySQL版本とデフォルト設定確認"""
        try:
            connection = pymysql.connect(**self.db_config)
            with connection.cursor() as cursor:
                # MySQL版本
                cursor.execute("SELECT VERSION()")
                version = cursor.fetchone()[0]
                logger.info(f"🐬 MySQL版本: {version}")
                
                # デフォルトコレーション設定
                cursor.execute("SHOW VARIABLES LIKE 'collation%'")
                collation_vars = cursor.fetchall()
                
                logger.info("⚙️ コレーション設定:")
                for var_name, value in collation_vars:
                    logger.info(f"   {var_name}: {value}")
                
                # 文字セット設定
                cursor.execute("SHOW VARIABLES LIKE 'character%'")
                charset_vars = cursor.fetchall()
                
                logger.info("🔤 文字セット設定:")
                for var_name, value in charset_vars:
                    logger.info(f"   {var_name}: {value}")
                
        except Exception as e:
            logger.error(f"MySQL設定確認エラー: {e}")
        finally:
            if 'connection' in locals():
                connection.close()

    def generate_collation_fix_sql(self):
        """コレーション修正SQLの生成"""
        try:
            connection = pymysql.connect(**self.db_config)
            with connection.cursor() as cursor:
                
                logger.info("🔧 コレーション修正SQL生成:")
                
                # 重要テーブルの修正SQL生成
                important_tables = ['stock_master', 'stock_price_history', 'stock_predictions']
                
                fix_sql = []
                
                for table in important_tables:
                    cursor.execute(f"""
                        SELECT COLUMN_NAME, DATA_TYPE, COLLATION_NAME 
                        FROM information_schema.COLUMNS 
                        WHERE TABLE_SCHEMA = 'miraikakaku' 
                        AND TABLE_NAME = '{table}'
                        AND COLLATION_NAME IS NOT NULL
                        ORDER BY ORDINAL_POSITION
                    """)
                    
                    columns = cursor.fetchall()
                    
                    for col_name, data_type, collation in columns:
                        if collation and 'utf8mb4_0900_ai_ci' in collation:
                            # MySQL 8.0 → 古いコレーションへの変更SQL
                            fix_sql.append(f"ALTER TABLE {table} MODIFY {col_name} {data_type} COLLATE utf8mb4_unicode_ci;")
                
                # 生成されたSQL出力
                if fix_sql:
                    logger.info("🔧 生成された修正SQL:")
                    for sql in fix_sql:
                        logger.info(f"   {sql}")
                else:
                    logger.info("ℹ️ 修正が必要な列は見つかりませんでした")
                
                return fix_sql
                
        except Exception as e:
            logger.error(f"修正SQL生成エラー: {e}")
            return []
        finally:
            if 'connection' in locals():
                connection.close()

    def full_investigation(self):
        """完全なコレーション調査"""
        logger.info("🔍 コレーション問題完全調査開始")
        
        # 1. データベースレベル確認
        logger.info("\n=== 1. データベースレベル調査 ===")
        self.check_database_collation()
        
        # 2. 列レベル確認
        logger.info("\n=== 2. 列レベル調査 ===")
        self.check_column_collations()
        
        # 3. MySQL設定確認
        logger.info("\n=== 3. MySQL設定調査 ===")
        self.check_mysql_version()
        
        # 4. 問題クエリテスト
        logger.info("\n=== 4. 問題クエリテスト ===")
        self.test_problematic_queries()
        
        # 5. 修正SQL生成
        logger.info("\n=== 5. 修正SQL生成 ===")
        fix_sql = self.generate_collation_fix_sql()
        
        logger.info("\n🎯 コレーション調査完了")
        return fix_sql

def main():
    logger.info("🔍 コレーション問題調査開始")
    
    investigator = CollationProblemInvestigator()
    fix_sql = investigator.full_investigation()
    
    if fix_sql:
        logger.info(f"✅ 調査完了 - {len(fix_sql)}個の修正SQL生成")
    else:
        logger.info("ℹ️ 調査完了 - 修正不要")

if __name__ == "__main__":
    main()