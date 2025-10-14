#!/usr/bin/env python3
"""
Phase 7-10 データベーススキーマ適用スクリプト
"""

import psycopg2
import os
from pathlib import Path

# データベース接続情報
DB_CONFIG = {
    'host': 'localhost',
    'port': 5433,
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
    print(f"📄 適用中: {schema_file}")
    print(f"{'='*60}")

    # ファイル読み込み
    file_path = Path(schema_file)
    if not file_path.exists():
        print(f"❌ エラー: ファイルが見つかりません: {schema_file}")
        return False

    with open(file_path, 'r', encoding='utf-8') as f:
        sql = f.read()

    # SQL実行
    try:
        with conn.cursor() as cur:
            cur.execute(sql)
            conn.commit()
            print(f"✅ 成功: {schema_file} を適用しました")
            return True
    except Exception as e:
        conn.rollback()
        print(f"❌ エラー: {schema_file} の適用に失敗しました")
        print(f"   理由: {str(e)}")
        return False

def main():
    """メイン処理"""
    print("=" * 60)
    print("🚀 Phase 7-10 スキーマ適用スクリプト")
    print("=" * 60)

    # データベース接続
    print(f"\n📡 データベースに接続中...")
    print(f"   Host: {DB_CONFIG['host']}:{DB_CONFIG['port']}")
    print(f"   Database: {DB_CONFIG['dbname']}")

    try:
        conn = psycopg2.connect(**DB_CONFIG)
        print("✅ 接続成功\n")
    except Exception as e:
        print(f"❌ 接続失敗: {str(e)}")
        return 1

    # スキーマ適用
    success_count = 0
    failed_files = []

    for schema_file in SCHEMA_FILES:
        if apply_schema(conn, schema_file):
            success_count += 1
        else:
            failed_files.append(schema_file)

    # 結果サマリー
    print(f"\n{'='*60}")
    print(f"📊 適用結果")
    print(f"{'='*60}")
    print(f"✅ 成功: {success_count}/{len(SCHEMA_FILES)} ファイル")

    if failed_files:
        print(f"❌ 失敗: {len(failed_files)} ファイル")
        for f in failed_files:
            print(f"   - {f}")
    else:
        print("🎉 全てのスキーマが正常に適用されました！")

    # 接続クローズ
    conn.close()
    print("\n✅ データベース接続を閉じました")

    return 0 if not failed_files else 1

if __name__ == '__main__':
    exit(main())
