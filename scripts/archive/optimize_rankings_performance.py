#!/usr/bin/env python3
"""
TOP画面ランキング表示の最適化スクリプト

問題: TOP画面のランキングAPIが遅い（各0.37-0.39秒、合計約2秒）
原因: 全銘柄をスキャンする複雑なCTEクエリ、インデックス不足
解決: マテリアライズドビューの作成、インデックスの追加
"""

import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()

def get_db_config():
    host = os.getenv('POSTGRES_HOST', 'localhost')
    config = {
        'database': os.getenv('POSTGRES_DB', 'miraikakaku'),
        'user': os.getenv('POSTGRES_USER', 'postgres'),
        'password': os.getenv('POSTGRES_PASSWORD', 'Miraikakaku2024!')
    }
    if host.startswith('/cloudsql/'):
        config['host'] = host
    else:
        config['host'] = host
        config['port'] = int(os.getenv('POSTGRES_PORT', 5433))
    return config

def check_existing_indexes(conn):
    """既存のインデックスを確認"""
    cur = conn.cursor()

    print("=== 既存のインデックス確認 ===\n")

    # stock_prices テーブルのインデックス
    cur.execute("""
        SELECT indexname, indexdef
        FROM pg_indexes
        WHERE tablename = 'stock_prices'
        ORDER BY indexname
    """)

    indexes = cur.fetchall()
    print(f"stock_prices テーブルのインデックス数: {len(indexes)}")
    for idx_name, idx_def in indexes:
        print(f"  - {idx_name}")

    print()
    cur.close()

def create_optimized_indexes(conn):
    """最適化されたインデックスを作成"""
    cur = conn.cursor()

    print("=== インデックス作成 ===\n")

    indexes_to_create = [
        # 最新価格取得用の複合インデックス (DISTINCT ON最適化)
        (
            "idx_stock_prices_symbol_date_desc",
            """CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_stock_prices_symbol_date_desc
               ON stock_prices (symbol, date DESC)"""
        ),
        # 出来高ランキング用
        (
            "idx_stock_prices_volume_desc",
            """CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_stock_prices_volume_desc
               ON stock_prices (volume DESC NULLS LAST) WHERE volume IS NOT NULL AND volume > 0"""
        ),
        # 日付範囲検索用
        (
            "idx_stock_prices_date",
            """CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_stock_prices_date
               ON stock_prices (date)"""
        ),
    ]

    for idx_name, sql in indexes_to_create:
        try:
            print(f"作成中: {idx_name}...")
            cur.execute(sql)
            conn.commit()
            print(f"  ✅ {idx_name} 作成完了")
        except Exception as e:
            conn.rollback()
            if "already exists" in str(e):
                print(f"  ℹ️  {idx_name} はすでに存在します")
            else:
                print(f"  ❌ エラー: {e}")

    print()
    cur.close()

def create_materialized_views(conn):
    """マテリアライズドビューを作成"""
    cur = conn.cursor()

    print("=== マテリアライズドビュー作成 ===\n")

    # 1. 最新価格ビュー
    print("作成中: mv_latest_prices...")
    try:
        cur.execute("""
            CREATE MATERIALIZED VIEW IF NOT EXISTS mv_latest_prices AS
            SELECT DISTINCT ON (symbol)
                symbol,
                close_price as current_price,
                date
            FROM stock_prices
            ORDER BY symbol, date DESC
        """)

        cur.execute("""
            CREATE UNIQUE INDEX IF NOT EXISTS idx_mv_latest_prices_symbol
            ON mv_latest_prices (symbol)
        """)

        conn.commit()
        print("  ✅ mv_latest_prices 作成完了")
    except Exception as e:
        conn.rollback()
        if "already exists" in str(e):
            print("  ℹ️  mv_latest_prices はすでに存在します")
        else:
            print(f"  ❌ エラー: {e}")

    # 2. 前日価格ビュー
    print("作成中: mv_prev_prices...")
    try:
        cur.execute("""
            CREATE MATERIALIZED VIEW IF NOT EXISTS mv_prev_prices AS
            SELECT DISTINCT ON (sp.symbol)
                sp.symbol,
                sp.close_price as prev_price,
                sp.date as prev_date
            FROM stock_prices sp
            INNER JOIN mv_latest_prices lp ON sp.symbol = lp.symbol
            WHERE sp.date < lp.date
            ORDER BY sp.symbol, sp.date DESC
        """)

        cur.execute("""
            CREATE UNIQUE INDEX IF NOT EXISTS idx_mv_prev_prices_symbol
            ON mv_prev_prices (symbol)
        """)

        conn.commit()
        print("  ✅ mv_prev_prices 作成完了")
    except Exception as e:
        conn.rollback()
        if "already exists" in str(e):
            print("  ℹ️  mv_prev_prices はすでに存在します")
        else:
            print(f"  ❌ エラー: {e}")

    # 3. 値上がり率ランキングビュー
    print("作成中: mv_gainers_ranking...")
    try:
        cur.execute("""
            CREATE MATERIALIZED VIEW IF NOT EXISTS mv_gainers_ranking AS
            SELECT
                lp.symbol,
                sm.company_name,
                sm.exchange,
                lp.current_price,
                pp.prev_price,
                ROUND(((lp.current_price - pp.prev_price) / NULLIF(pp.prev_price, 0) * 100)::numeric, 2) as change_percent
            FROM mv_latest_prices lp
            LEFT JOIN mv_prev_prices pp ON lp.symbol = pp.symbol
            LEFT JOIN stock_master sm ON lp.symbol = sm.symbol
            WHERE pp.prev_price IS NOT NULL AND pp.prev_price > 0
            ORDER BY change_percent DESC NULLS LAST
        """)

        cur.execute("""
            CREATE INDEX IF NOT EXISTS idx_mv_gainers_ranking_change
            ON mv_gainers_ranking (change_percent DESC NULLS LAST)
        """)

        conn.commit()
        print("  ✅ mv_gainers_ranking 作成完了")
    except Exception as e:
        conn.rollback()
        if "already exists" in str(e):
            print("  ℹ️  mv_gainers_ranking はすでに存在します")
        else:
            print(f"  ❌ エラー: {e}")

    # 4. 値下がり率ランキングビュー
    print("作成中: mv_losers_ranking...")
    try:
        cur.execute("""
            CREATE MATERIALIZED VIEW IF NOT EXISTS mv_losers_ranking AS
            SELECT
                lp.symbol,
                sm.company_name,
                sm.exchange,
                lp.current_price,
                pp.prev_price,
                ROUND(((lp.current_price - pp.prev_price) / NULLIF(pp.prev_price, 0) * 100)::numeric, 2) as change_percent
            FROM mv_latest_prices lp
            LEFT JOIN mv_prev_prices pp ON lp.symbol = pp.symbol
            LEFT JOIN stock_master sm ON lp.symbol = sm.symbol
            WHERE pp.prev_price IS NOT NULL AND pp.prev_price > 0
            ORDER BY change_percent ASC NULLS LAST
        """)

        cur.execute("""
            CREATE INDEX IF NOT EXISTS idx_mv_losers_ranking_change
            ON mv_losers_ranking (change_percent ASC NULLS LAST)
        """)

        conn.commit()
        print("  ✅ mv_losers_ranking 作成完了")
    except Exception as e:
        conn.rollback()
        if "already exists" in str(e):
            print("  ℹ️  mv_losers_ranking はすでに存在します")
        else:
            print(f"  ❌ エラー: {e}")

    print()
    cur.close()

def create_refresh_function(conn):
    """マテリアライズドビューを更新する関数を作成"""
    cur = conn.cursor()

    print("=== 更新関数作成 ===\n")

    try:
        cur.execute("""
            CREATE OR REPLACE FUNCTION refresh_ranking_views()
            RETURNS void AS $$
            BEGIN
                REFRESH MATERIALIZED VIEW CONCURRENTLY mv_latest_prices;
                REFRESH MATERIALIZED VIEW CONCURRENTLY mv_prev_prices;
                REFRESH MATERIALIZED VIEW CONCURRENTLY mv_gainers_ranking;
                REFRESH MATERIALIZED VIEW CONCURRENTLY mv_losers_ranking;
            END;
            $$ LANGUAGE plpgsql;
        """)

        conn.commit()
        print("  ✅ refresh_ranking_views() 関数作成完了")
        print("  使用方法: SELECT refresh_ranking_views();")
    except Exception as e:
        conn.rollback()
        print(f"  ❌ エラー: {e}")

    print()
    cur.close()

def refresh_views(conn):
    """マテリアライズドビューを更新"""
    cur = conn.cursor()

    print("=== マテリアライズドビュー更新 ===\n")

    views = [
        "mv_latest_prices",
        "mv_prev_prices",
        "mv_gainers_ranking",
        "mv_losers_ranking"
    ]

    for view in views:
        try:
            print(f"更新中: {view}...")
            cur.execute(f"REFRESH MATERIALIZED VIEW CONCURRENTLY {view}")
            conn.commit()
            print(f"  ✅ {view} 更新完了")
        except Exception as e:
            conn.rollback()
            print(f"  ❌ エラー: {e}")

    print()
    cur.close()

def analyze_tables(conn):
    """テーブルを分析して統計情報を更新"""
    cur = conn.cursor()

    print("=== テーブル分析 ===\n")

    tables = ["stock_prices", "stock_master", "ensemble_predictions"]

    for table in tables:
        try:
            print(f"分析中: {table}...")
            cur.execute(f"ANALYZE {table}")
            conn.commit()
            print(f"  ✅ {table} 分析完了")
        except Exception as e:
            conn.rollback()
            print(f"  ❌ エラー: {e}")

    print()
    cur.close()

def main():
    print("=" * 60)
    print("TOP画面ランキング表示の最適化")
    print("=" * 60)
    print()

    try:
        conn = psycopg2.connect(**get_db_config())

        # 1. 既存インデックス確認
        check_existing_indexes(conn)

        # 2. インデックス作成
        create_optimized_indexes(conn)

        # 3. マテリアライズドビュー作成
        create_materialized_views(conn)

        # 4. 更新関数作成
        create_refresh_function(conn)

        # 5. ビュー更新
        refresh_views(conn)

        # 6. テーブル分析
        analyze_tables(conn)

        conn.close()

        print("=" * 60)
        print("最適化完了！")
        print("=" * 60)
        print()
        print("次のステップ:")
        print("1. api_predictions.py のランキングエンドポイントを修正")
        print("2. マテリアライズドビューを使用するようにクエリを変更")
        print("3. Cloud Schedulerでビュー更新ジョブを設定（毎日実行）")
        print()

    except Exception as e:
        print(f"エラーが発生しました: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
