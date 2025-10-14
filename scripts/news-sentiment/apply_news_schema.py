#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ニュースセンチメント分析用データベーススキーマ適用スクリプト
Cloud SQLデータベースにschema_news_sentiment.sqlを適用
"""

import psycopg2
import sys
import io
import os
from dotenv import load_dotenv

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
load_dotenv()

DB_CONFIG = {
    'host': os.getenv('POSTGRES_HOST', 'localhost'),
    'port': int(os.getenv('POSTGRES_PORT', 5433)),
    'database': os.getenv('POSTGRES_DB', 'miraikakaku'),
    'user': os.getenv('POSTGRES_USER', 'postgres'),
    'password': os.getenv('POSTGRES_PASSWORD', 'Miraikakaku2024!')
}

def apply_schema():
    """スキーマファイルを読み込んでデータベースに適用"""
    print("=" * 80)
    print("ニュースセンチメント分析スキーマ適用")
    print("=" * 80)
    print()

    try:
        # スキーマファイル読み込み
        with open('schema_news_sentiment.sql', 'r', encoding='utf-8') as f:
            schema_sql = f.read()

        print("✓ スキーマファイル読み込み完了")
        print()

        # データベース接続
        print(f"データベース接続: {DB_CONFIG['host']}:{DB_CONFIG['port']}/{DB_CONFIG['database']}")
        conn = psycopg2.connect(**DB_CONFIG)
        conn.autocommit = False
        cur = conn.cursor()

        print("✓ データベース接続成功")
        print()

        # スキーマ適用
        print("-" * 80)
        print("スキーマ適用中...")
        print("-" * 80)

        try:
            cur.execute(schema_sql)
            conn.commit()
            print("✓ スキーマ適用成功")
        except Exception as e:
            conn.rollback()
            print(f"✗ スキーマ適用エラー: {e}")
            raise

        print()
        print("-" * 80)
        print("作成されたテーブルとビューの確認")
        print("-" * 80)

        # テーブル確認
        cur.execute("""
            SELECT table_name
            FROM information_schema.tables
            WHERE table_schema = 'public'
              AND table_name IN ('stock_news', 'stock_sentiment_summary', 'news_analysis_log')
            ORDER BY table_name
        """)

        tables = cur.fetchall()
        print("\n【テーブル】")
        for table in tables:
            print(f"  ✓ {table[0]}")

        # ensemble_predictionsの列確認
        cur.execute("""
            SELECT column_name, data_type
            FROM information_schema.columns
            WHERE table_name = 'ensemble_predictions'
              AND column_name IN ('news_sentiment', 'news_impact', 'sentiment_adjusted_prediction')
            ORDER BY column_name
        """)

        columns = cur.fetchall()
        print("\n【ensemble_predictionsへの追加列】")
        for col in columns:
            print(f"  ✓ {col[0]} ({col[1]})")

        # ビュー確認
        cur.execute("""
            SELECT table_name
            FROM information_schema.views
            WHERE table_schema = 'public'
              AND table_name IN ('latest_news_sentiment', 'sentiment_enhanced_predictions')
            ORDER BY table_name
        """)

        views = cur.fetchall()
        print("\n【ビュー】")
        for view in views:
            print(f"  ✓ {view[0]}")

        # 関数確認
        cur.execute("""
            SELECT routine_name
            FROM information_schema.routines
            WHERE routine_schema = 'public'
              AND routine_name IN ('calculate_sentiment_score', 'update_sentiment_summary')
            ORDER BY routine_name
        """)

        functions = cur.fetchall()
        print("\n【関数】")
        for func in functions:
            print(f"  ✓ {func[0]}")

        # トリガー確認
        cur.execute("""
            SELECT trigger_name, event_object_table
            FROM information_schema.triggers
            WHERE trigger_schema = 'public'
              AND trigger_name = 'trigger_update_sentiment_summary'
        """)

        triggers = cur.fetchall()
        print("\n【トリガー】")
        for trig in triggers:
            print(f"  ✓ {trig[0]} (on {trig[1]})")

        print()
        print("=" * 80)
        print("スキーマ適用完了")
        print("=" * 80)
        print()
        print("次のステップ:")
        print("1. Alpha Vantage APIキーを.envに設定")
        print("2. python news_sentiment_analyzer.py を実行してニュース収集")
        print("3. python generate_sentiment_enhanced_predictions.py で予測生成")

        cur.close()
        conn.close()

    except FileNotFoundError:
        print("エラー: schema_news_sentiment.sql が見つかりません")
        sys.exit(1)
    except psycopg2.Error as e:
        print(f"データベースエラー: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"エラー: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    apply_schema()
