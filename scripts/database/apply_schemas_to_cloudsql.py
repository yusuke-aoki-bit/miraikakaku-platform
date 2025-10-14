#!/usr/bin/env python3
"""
Cloud SQLにスキーマを適用するスクリプト
Phase 8-10のテーブルを作成します
"""

import os
import sys
import psycopg2
from psycopg2 import sql

# Cloud SQL接続情報（環境変数またはデフォルト値）
DB_HOST = os.getenv('CLOUDSQL_HOST', '/cloudsql/pricewise-huqkr:us-central1:miraikakaku-postgres')
DB_PORT = os.getenv('CLOUDSQL_PORT', '5432')
DB_USER = os.getenv('CLOUDSQL_USER', 'postgres')
DB_PASS = os.getenv('CLOUDSQL_PASSWORD', 'Miraikakaku2024!')
DB_NAME = os.getenv('CLOUDSQL_DB', 'miraikakaku')

# Unix socketが使えない場合はTCP接続を試行
if not os.path.exists('/cloudsql'):
    DB_HOST = os.getenv('CLOUDSQL_HOST', '10.108.0.3')  # Internal IP

print("=" * 60)
print("Phase 7-10 データベーススキーマ適用")
print("=" * 60)
print(f"データベース: {DB_NAME}")
print(f"ホスト: {DB_HOST}")
print()

def execute_sql_file(cursor, filepath, description):
    """SQLファイルを実行"""
    print(f"=== {description} ===")
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            sql_content = f.read()

        cursor.execute(sql_content)
        print(f"✅ {description} - 成功")
        return True
    except Exception as e:
        print(f"❌ {description} - 失敗")
        print(f"エラー: {str(e)}")
        return False

def main():
    try:
        # データベース接続
        print("データベースに接続中...")
        conn = psycopg2.connect(
            host=DB_HOST,
            port=DB_PORT,
            user=DB_USER,
            password=DB_PASS,
            database=DB_NAME
        )
        conn.autocommit = False  # トランザクション管理
        cursor = conn.cursor()
        print("✅ 接続成功\n")

        # スキーマファイルのリスト
        schemas = [
            ('create_watchlist_schema.sql', 'ウォッチリストスキーマ (Phase 8)'),
            ('apply_portfolio_schema.sql', 'ポートフォリオスキーマ (Phase 9)'),
            ('create_alerts_schema.sql', 'アラートスキーマ (Phase 10)'),
        ]

        success_count = 0
        total_count = len(schemas)

        for filepath, description in schemas:
            if execute_sql_file(cursor, filepath, description):
                conn.commit()  # 各スキーマごとにコミット
                success_count += 1
            else:
                conn.rollback()
            print()

        # 結果サマリー
        print("=" * 60)
        print("スキーマ適用結果")
        print("=" * 60)
        print(f"成功: {success_count}/{total_count}")
        print(f"失敗: {total_count - success_count}/{total_count}")

        if success_count == total_count:
            print("\n✅ 全てのスキーマが正常に適用されました！")

            # テーブル確認
            print("\n作成されたテーブルを確認中...")
            cursor.execute("""
                SELECT table_name
                FROM information_schema.tables
                WHERE table_schema = 'public'
                AND table_name IN ('user_watchlists', 'portfolio_holdings', 'portfolio_snapshots', 'price_alerts')
                ORDER BY table_name
            """)
            tables = cursor.fetchall()

            print("\n作成されたテーブル:")
            for table in tables:
                print(f"  - {table[0]}")

            return 0
        else:
            print("\n⚠️ 一部のスキーマ適用に失敗しました")
            return 1

    except psycopg2.Error as e:
        print(f"\n❌ データベースエラー: {e}")
        return 1
    except FileNotFoundError as e:
        print(f"\n❌ ファイルが見つかりません: {e}")
        print("スクリプトを正しいディレクトリから実行してください")
        return 1
    except Exception as e:
        print(f"\n❌ 予期しないエラー: {e}")
        return 1
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'conn' in locals():
            conn.close()
        print("\nデータベース接続を閉じました")

if __name__ == "__main__":
    sys.exit(main())
