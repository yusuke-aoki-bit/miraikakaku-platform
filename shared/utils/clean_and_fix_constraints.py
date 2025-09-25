#!/usr/bin/env python3
"""
Clean and Fix Database Constraints
重複データ除去と制約修正ツール
"""

import psycopg2
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def clean_and_fix_constraints():
    """重複データ除去して制約修正"""

    try:
        conn = psycopg2.connect(
            host='34.173.9.214',
            user='postgres',
            password='os.getenv('DB_PASSWORD', '')',
            database='miraikakaku'
        )
        conn.autocommit = True  # 自動コミットモード
        cursor = conn.cursor()
        logger.info("✅ Database connection established")

        # 1. 重複データ確認
        logger.info("🔍 Checking for duplicate data...")
        cursor.execute("""
            SELECT symbol, prediction_date, prediction_days, COUNT(*)
            FROM stock_predictions
            GROUP BY symbol, prediction_date, prediction_days
            HAVING COUNT(*) > 1
            LIMIT 10;
        """)

        duplicates = cursor.fetchall()
        logger.info(f"📊 Found {len(duplicates)} duplicate groups")
        for dup in duplicates[:5]:  # 最初の5つを表示
            logger.info(f"  - {dup[0]}, {dup[1]}, {dup[2]}: {dup[3]} records")

        if duplicates:
            # 2. 重複データ除去（最新のcreated_atを保持）
            logger.info("🧹 Removing duplicate data (keeping latest)...")
            cursor.execute("""
                DELETE FROM stock_predictions
                WHERE id IN (
                    SELECT id
                    FROM (
                        SELECT id,
                               ROW_NUMBER() OVER (
                                   PARTITION BY symbol, prediction_date, prediction_days
                                   ORDER BY created_at DESC, id DESC
                               ) as rn
                        FROM stock_predictions
                    ) t
                    WHERE t.rn > 1
                );
            """)

            deleted_count = cursor.rowcount
            logger.info(f"🗑️ Deleted {deleted_count} duplicate records")

            # 3. 重複確認（除去後）
            cursor.execute("""
                SELECT COUNT(*)
                FROM (
                    SELECT symbol, prediction_date, prediction_days, COUNT(*)
                    FROM stock_predictions
                    GROUP BY symbol, prediction_date, prediction_days
                    HAVING COUNT(*) > 1
                ) duplicates;
            """)

            remaining_duplicates = cursor.fetchone()[0]
            logger.info(f"📊 Remaining duplicates: {remaining_duplicates}")

        # 4. ユニーク制約追加
        logger.info("🔧 Adding unique constraint...")
        try:
            cursor.execute("""
                ALTER TABLE stock_predictions
                ADD CONSTRAINT stock_predictions_unique
                UNIQUE (symbol, prediction_date, prediction_days);
            """)
            logger.info("✅ Added unique constraint successfully")
        except psycopg2.Error as e:
            if "already exists" in str(e):
                logger.info("✅ Unique constraint already exists")
            else:
                logger.error(f"❌ Failed to add constraint: {e}")
                return False

        # 5. パフォーマンスインデックス追加
        logger.info("🚀 Adding performance indexes...")
        indexes = [
            ("idx_stock_predictions_symbol_date", "symbol, prediction_date"),
            ("idx_stock_predictions_created_at", "created_at"),
            ("idx_stock_predictions_model_type", "model_type")
        ]

        for idx_name, idx_columns in indexes:
            try:
                cursor.execute(f"""
                    CREATE INDEX IF NOT EXISTS {idx_name}
                    ON stock_predictions ({idx_columns});
                """)
                logger.info(f"✅ Added index: {idx_name}")
            except psycopg2.Error as e:
                logger.warning(f"⚠️ Index {idx_name} warning: {e}")

        # 6. 制約テスト
        logger.info("🧪 Testing constraints...")
        try:
            # 挿入テスト
            cursor.execute("""
                INSERT INTO stock_predictions
                (symbol, prediction_date, prediction_days, current_price, predicted_price, confidence_score, model_type, created_at)
                VALUES ('CONSTRAINT_TEST', CURRENT_DATE, 1, 100.0, 101.0, 0.8, 'TEST_MODEL', NOW())
                ON CONFLICT (symbol, prediction_date, prediction_days) DO UPDATE SET
                    predicted_price = EXCLUDED.predicted_price,
                    confidence_score = EXCLUDED.confidence_score,
                    model_type = EXCLUDED.model_type,
                    created_at = EXCLUDED.created_at;
            """)

            # 重複挿入テスト
            cursor.execute("""
                INSERT INTO stock_predictions
                (symbol, prediction_date, prediction_days, current_price, predicted_price, confidence_score, model_type, created_at)
                VALUES ('CONSTRAINT_TEST', CURRENT_DATE, 1, 105.0, 106.0, 0.9, 'TEST_MODEL_UPDATED', NOW())
                ON CONFLICT (symbol, prediction_date, prediction_days) DO UPDATE SET
                    predicted_price = EXCLUDED.predicted_price,
                    confidence_score = EXCLUDED.confidence_score,
                    model_type = EXCLUDED.model_type,
                    created_at = EXCLUDED.created_at;
            """)

            # テストデータ確認
            cursor.execute("""
                SELECT predicted_price, model_type
                FROM stock_predictions
                WHERE symbol = 'CONSTRAINT_TEST';
            """)
            test_result = cursor.fetchone()
            logger.info(f"✅ Constraint test result: price={test_result[0]}, model={test_result[1]}")

            # テストデータ削除
            cursor.execute("DELETE FROM stock_predictions WHERE symbol = 'CONSTRAINT_TEST'")
            logger.info("🧹 Test data cleaned up")

        except psycopg2.Error as e:
            logger.error(f"❌ Constraint test failed: {e}")
            return False

        # 7. 最終統計
        cursor.execute("SELECT COUNT(*) FROM stock_predictions")
        total_predictions = cursor.fetchone()[0]

        cursor.execute("""
            SELECT COUNT(DISTINCT symbol) FROM stock_predictions
            WHERE prediction_date >= CURRENT_DATE
        """)
        future_symbols = cursor.fetchone()[0]

        cursor.execute("""
            SELECT COUNT(*) FROM stock_predictions
            WHERE actual_price IS NOT NULL
        """)
        historical_predictions = cursor.fetchone()[0]

        logger.info("="*60)
        logger.info("🎉 Database Constraints Fixed Successfully")
        logger.info("="*60)
        logger.info(f"📊 Total predictions: {total_predictions:,}")
        logger.info(f"🔮 Future prediction symbols: {future_symbols}")
        logger.info(f"📜 Historical predictions: {historical_predictions}")
        logger.info("✅ Unique constraint: (symbol, prediction_date, prediction_days)")
        logger.info("🚀 Performance indexes: Added")
        logger.info("="*60)

        conn.close()
        return True

    except Exception as e:
        logger.error(f"❌ Database constraint fixing failed: {e}")
        return False

if __name__ == "__main__":
    success = clean_and_fix_constraints()
    if success:
        print("🎉 Database constraints cleaned and fixed successfully")
    else:
        print("❌ Database constraint fixing failed")