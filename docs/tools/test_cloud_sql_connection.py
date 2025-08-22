#!/usr/bin/env python3
"""
Cloud SQL接続テスト（SQLite完全廃止版）
"""

import os
import sys
from dotenv import load_dotenv

# 環境変数読み込み
load_dotenv('.env.cloud_sql')

def test_api_connection():
    """API用Cloud SQL接続テスト"""
    print("🔍 API用Cloud SQL接続テスト...")
    try:
        sys.path.append('miraikakakuapi/functions')
        from database.cloud_sql_only import test_connection
        
        if test_connection():
            print("✅ API: Cloud SQL接続成功")
            return True
        else:
            print("❌ API: Cloud SQL接続失敗")
            return False
    except Exception as e:
        print(f"❌ API: 接続テストエラー: {e}")
        return False

def test_batch_connection():
    """Batch用Cloud SQL接続テスト"""
    print("🔍 Batch用Cloud SQL接続テスト...")
    try:
        sys.path.append('miraikakakubatch/functions')
        from database.cloud_sql_only import test_connection
        
        if test_connection():
            print("✅ Batch: Cloud SQL接続成功")
            return True
        else:
            print("❌ Batch: Cloud SQL接続失敗")
            return False
    except Exception as e:
        print(f"❌ Batch: 接続テストエラー: {e}")
        return False

def test_data_feed_connection():
    """Data Feed用Cloud SQL接続テスト"""
    print("🔍 Data Feed用Cloud SQL接続テスト...")
    try:
        import pymysql
        
        # 接続パラメータ
        host = os.getenv('CLOUD_SQL_HOST', '34.58.103.36')
        password = os.getenv('CLOUD_SQL_PASSWORD', 'Yuuku717')
        
        # 接続テスト
        connection = pymysql.connect(
            host=host,
            user='root',
            password=password,
            database='miraikakaku_prod',
            charset='utf8mb4'
        )
        
        with connection.cursor() as cursor:
            cursor.execute("SELECT COUNT(*) FROM stock_master")
            count = cursor.fetchone()[0]
            print(f"✅ Data Feed: Cloud SQL接続成功 ({count:,}銘柄)")
            
        connection.close()
        return True
        
    except Exception as e:
        print(f"❌ Data Feed: 接続テストエラー: {e}")
        return False

def check_sqlite_removal():
    """SQLiteファイル削除確認"""
    print("🔍 SQLiteファイル削除確認...")
    
    sqlite_files = [
        'miraikakakuapi/functions/miraikakaku.db',
        'miraikakakubatch/functions/miraikakaku.db',
        'miraikakaku.db'
    ]
    
    found_sqlite = False
    for sqlite_file in sqlite_files:
        if os.path.exists(sqlite_file):
            print(f"⚠️  SQLiteファイルが残存: {sqlite_file}")
            found_sqlite = True
    
    if not found_sqlite:
        print("✅ SQLiteファイル完全削除済み")
    
    return not found_sqlite

def main():
    """メイン実行"""
    print("=" * 50)
    print("🚀 Cloud SQL統合テスト（SQLite完全廃止版）")
    print("=" * 50)
    
    tests = [
        ("API接続", test_api_connection),
        ("Batch接続", test_batch_connection),
        ("Data Feed接続", test_data_feed_connection),
        ("SQLite削除確認", check_sqlite_removal)
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name}: 予期しないエラー: {e}")
            results.append((test_name, False))
    
    print("\n" + "=" * 50)
    print("📊 テスト結果サマリー")
    print("=" * 50)
    
    success_count = 0
    for test_name, success in results:
        status = "✅ 成功" if success else "❌ 失敗"
        print(f"{test_name}: {status}")
        if success:
            success_count += 1
    
    print(f"\n合計: {success_count}/{len(results)} テスト成功")
    
    if success_count == len(results):
        print("🎉 全てのテストが成功！Cloud SQL統合完了")
        return True
    else:
        print("⚠️  一部のテストが失敗しました")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)