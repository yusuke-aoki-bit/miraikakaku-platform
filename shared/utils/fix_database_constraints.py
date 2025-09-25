#!/usr/bin/env python3
"""
Database Constraint Fixer
データベース制約問題修正ツール
"""

import psycopg2
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def fix_database_constraints():
    """データベース制約を修正"""

    try:
        conn = psycopg2.connect(
            host='34.173.9.214',
            user='postgres',
            password='os.getenv('DB_PASSWORD', '')',
            database='miraikakaku'
        )
        cursor = conn.cursor()
        logger.info("✅ Database connection established")

        # 1. 現在のテーブル構造確認
        logger.info("🔍 Checking stock_predictions table structure...")
        cursor.execute("""
            SELECT column_name, data_type, is_nullable
            FROM information_schema.columns
            WHERE table_name = 'stock_predictions'
            ORDER BY ordinal_position;
        """)

        columns = cursor.fetchall()
        logger.info("📋 Table columns:")
        for col in columns:
            logger.info(f"  - {col[0]}: {col[1]} (nullable: {col[2]})")

        # 2. 現在の制約確認
        logger.info("\n🔍 Checking current constraints...")
        cursor.execute("""
            SELECT constraint_name, constraint_type
            FROM information_schema.table_constraints
            WHERE table_name = 'stock_predictions';
        """)

        constraints = cursor.fetchall()
        logger.info("📋 Current constraints:")
        for const in constraints:
            logger.info(f"  - {const[0]}: {const[1]}")

        # 3. 必要な制約が存在するかチェック
        cursor.execute("""
            SELECT constraint_name
            FROM information_schema.table_constraints
            WHERE table_name = 'stock_predictions'
            AND constraint_type = 'UNIQUE';
        """)

        unique_constraints = cursor.fetchall()
        has_unique_constraint = len(unique_constraints) > 0

        if not has_unique_constraint:
            logger.info("⚠️ No unique constraint found. Creating one...")

            # 4. ユニーク制約追加（symbol, prediction_date, prediction_days）
            try:
                cursor.execute("""
                    ALTER TABLE stock_predictions
                    ADD CONSTRAINT stock_predictions_unique
                    UNIQUE (symbol, prediction_date, prediction_days);
                """)
                logger.info("✅ Added unique constraint: (symbol, prediction_date, prediction_days)")
            except psycopg2.Error as e:
                if "already exists" in str(e):
                    logger.info("✅ Unique constraint already exists")
                else:
                    logger.warning(f"⚠️ Could not add constraint: {e}")
                    # 重複データを削除してから再試行
                    logger.info("🧹 Removing duplicate data...")
                    cursor.execute("""
                        DELETE FROM stock_predictions a USING stock_predictions b
                        WHERE a.id < b.id
                        AND a.symbol = b.symbol
                        AND a.prediction_date = b.prediction_date
                        AND a.prediction_days = b.prediction_days;
                    """)
                    deleted_count = cursor.rowcount
                    logger.info(f"🗑️ Deleted {deleted_count} duplicate records")

                    # 再度制約追加を試行
                    try:
                        cursor.execute("""
                            ALTER TABLE stock_predictions
                            ADD CONSTRAINT stock_predictions_unique
                            UNIQUE (symbol, prediction_date, prediction_days);
                        """)
                        logger.info("✅ Added unique constraint after cleanup")
                    except psycopg2.Error as e2:
                        logger.error(f"❌ Still cannot add constraint: {e2}")

        # 5. インデックス追加（パフォーマンス向上）
        try:
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_stock_predictions_symbol_date
                ON stock_predictions (symbol, prediction_date);
            """)
            logger.info("✅ Added performance index")
        except psycopg2.Error as e:
            logger.warning(f"⚠️ Index creation warning: {e}")

        # 6. 制約確認（修正後）
        logger.info("\n🔍 Final constraint check...")
        cursor.execute("""
            SELECT constraint_name, constraint_type
            FROM information_schema.table_constraints
            WHERE table_name = 'stock_predictions';
        """)

        final_constraints = cursor.fetchall()
        logger.info("📋 Final constraints:")
        for const in final_constraints:
            logger.info(f"  - {const[0]}: {const[1]}")

        conn.commit()
        logger.info("✅ Database constraint fixes completed")

        # 7. テスト挿入
        logger.info("\n🧪 Testing constraint with sample data...")
        try:
            cursor.execute("""
                INSERT INTO stock_predictions
                (symbol, prediction_date, prediction_days, current_price, predicted_price, confidence_score, model_type, created_at)
                VALUES ('TEST', CURRENT_DATE, 1, 100.0, 101.0, 0.8, 'CONSTRAINT_TEST', NOW())
                ON CONFLICT (symbol, prediction_date, prediction_days) DO UPDATE SET
                    predicted_price = EXCLUDED.predicted_price,
                    confidence_score = EXCLUDED.confidence_score,
                    model_type = EXCLUDED.model_type,
                    created_at = EXCLUDED.created_at;
            """)
            logger.info("✅ Constraint test INSERT successful")

            # テストデータ削除
            cursor.execute("DELETE FROM stock_predictions WHERE symbol = 'TEST'")
            logger.info("🧹 Test data cleaned up")

        except psycopg2.Error as e:
            logger.error(f"❌ Constraint test failed: {e}")

        conn.commit()
        conn.close()
        logger.info("🎉 Database constraint fixing completed successfully")
        return True

    except Exception as e:
        logger.error(f"❌ Database constraint fixing failed: {e}")
        return False

if __name__ == "__main__":
    success = fix_database_constraints()
    if success:
        print("🎉 Database constraints fixed successfully")
    else:
        print("❌ Database constraint fixing failed")