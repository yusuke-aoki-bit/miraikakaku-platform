#!/usr/bin/env python3
"""
Phase 7-10 データベーススキーマ適用スクリプト (Cloud SQL直接接続版)
"""

import psycopg2
from pathlib import Path
import sys

# Cloud SQL接続情報（PUBLIC IP）
DB_CONFIG = {
    'host': '34.72.126.164',  # Cloud SQL Public IP
    'port': 5432,
    'dbname': 'miraikakaku',
    'user': 'postgres',
    'password': 'Miraikakaku2024!'
}

# 適用するスキーマファイル（順序重要）
SCHEMA_FILES = [
    'create_auth_schema.sql',         # Phase 6/7: 認証システム
    'create_watchlist_schema.sql',    # Phase 8: ウォッチリスト
    'schema_portfolio.sql',           # Phase 9: ポートフォリオ
    'create_alerts_schema.sql'        # Phase 10: アラート
]

def apply_schema(conn, schema_file):
    """スキーマファイルを適用"""
    print(f"\n{'='*60}")
    print(f"適用中: {schema_file}")
    print(f"{'='*60}")

    # ファイル読み込み
    file_path = Path(schema_file)
    if not file_path.exists():
        print(f"エラー: ファイルが見つかりません: {schema_file}")
        return False

    with open(file_path, 'r', encoding='utf-8') as f:
        sql = f.read()

    # SQL実行
    try:
        with conn.cursor() as cur:
            # 複数のSQL文を分割して実行
            cur.execute(sql)
            conn.commit()
            print(f"成功: {schema_file} を適用しました")
            return True
    except Exception as e:
        conn.rollback()
        print(f"エラー: {schema_file} の適用に失敗しました")
        print(f"理由: {str(e)}")
        return False

def main():
    """メイン処理"""
    print("=" * 60)
    print("Phase 7-10 スキーマ適用スクリプト (Cloud SQL)")
    print("=" * 60)

    # データベース接続
    print(f"\nデータベースに接続中...")
    print(f"Host: {DB_CONFIG['host']}:{DB_CONFIG['port']}")
    print(f"Database: {DB_CONFIG['dbname']}")

    try:
        conn = psycopg2.connect(**DB_CONFIG)
        print("接続成功\n")
    except Exception as e:
        print(f"接続失敗: {str(e)}")
        print("\nヒント:")
        print("- Cloud SQLのPublic IPが正しいか確認")
        print("- ファイアウォールルールで接続元IPが許可されているか確認")
        print("- Cloud SQL Proxyを使用することも検討してください")
        return 1

    # スキーマ適用
    success_count = 0
    failed_files = []

    for schema_file in SCHEMA_FILES:
        if apply_schema(conn, schema_file):
            success_count += 1
        else:
            failed_files.append(schema_file)

    # 適用後のテーブル確認
    print(f"\n{'='*60}")
    print("テーブル一覧確認")
    print(f"{'='*60}")

    try:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT table_name
                FROM information_schema.tables
                WHERE table_schema = 'public'
                AND table_name IN ('users', 'user_sessions', 'watchlist', 'portfolio_holdings', 'price_alerts')
                ORDER BY table_name;
            """)
            tables = cur.fetchall()
            print(f"\nPhase 7-10関連テーブル: {len(tables)}個")
            for t in tables:
                print(f"  - {t[0]}")
    except Exception as e:
        print(f"テーブル確認エラー: {str(e)}")

    # 結果サマリー
    print(f"\n{'='*60}")
    print(f"適用結果")
    print(f"{'='*60}")
    print(f"成功: {success_count}/{len(SCHEMA_FILES)} ファイル")

    if failed_files:
        print(f"失敗: {len(failed_files)} ファイル")
        for f in failed_files:
            print(f"  - {f}")
    else:
        print("全てのスキーマが正常に適用されました!")

    # 接続クローズ
    conn.close()
    print("\nデータベース接続を閉じました")

    return 0 if not failed_files else 1

if __name__ == '__main__':
    sys.exit(main())
