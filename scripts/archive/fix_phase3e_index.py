#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Phase 3-E インデックス修正スクリプト
idx_ensemble_predictions_date_symbol インデックスを修正
"""
import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()

DB_CONFIG = {
    'host': 'localhost',
    'port': 5433,
    'database': 'miraikakaku',
    'user': 'postgres',
    'password': os.getenv('POSTGRES_PASSWORD', 'Miraikakaku2024!')
}

def main():
    print("=" * 80)
    print("Phase 3-E: インデックス修正")
    print("=" * 80)
    print()

    try:
        # データベース接続 (AUTOCOMMIT required for CREATE INDEX CONCURRENTLY)
        conn = psycopg2.connect(**DB_CONFIG)
        conn.set_isolation_level(psycopg2.extensions.ISOLATION_LEVEL_AUTOCOMMIT)
        cur = conn.cursor()

        print("1. 既存のインデックス確認")
        cur.execute("""
            SELECT indexname
            FROM pg_indexes
            WHERE tablename = 'ensemble_predictions'
              AND indexname = 'idx_ensemble_predictions_date_symbol'
        """)
        existing = cur.fetchone()

        if existing:
            print(f"   ✅ インデックス既に存在: {existing[0]}")
            print("   → スキップします")
        else:
            print("   ⚠️  インデックス未作成")
            print()
            print("2. インデックス作成")
            print("   SQL: CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_ensemble_predictions_date_symbol")
            print("        ON ensemble_predictions (prediction_date DESC, symbol);")
            print()

            try:
                cur.execute("""
                    CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_ensemble_predictions_date_symbol
                    ON ensemble_predictions (prediction_date DESC, symbol)
                """)
                print("   ✅ インデックス作成成功")
            except Exception as e:
                print(f"   ❌ エラー: {e}")

        print()
        print("3. 作成確認")
        cur.execute("""
            SELECT indexname, indexdef
            FROM pg_indexes
            WHERE tablename = 'ensemble_predictions'
              AND indexname = 'idx_ensemble_predictions_date_symbol'
        """)
        result = cur.fetchone()

        if result:
            print(f"   ✅ インデックス確認: {result[0]}")
            print(f"   定義: {result[1]}")
        else:
            print("   ❌ インデックスが見つかりません")

        cur.close()
        conn.close()

    except Exception as e:
        print(f"\nエラー: {e}")
        import traceback
        traceback.print_exc()

    print()
    print("=" * 80)
    print("完了")
    print("=" * 80)

if __name__ == "__main__":
    main()
