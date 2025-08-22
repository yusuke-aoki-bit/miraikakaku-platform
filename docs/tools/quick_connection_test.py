#!/usr/bin/env python3
"""
Cloud SQL接続クイックテスト
"""

import pymysql
import os
from dotenv import load_dotenv

# 環境変数読み込み
load_dotenv('.env.cloud_sql')

def test_basic_connection():
    """基本接続テスト"""
    host = "34.58.103.36"
    password = "Yuuku717"
    
    print(f"🔍 接続テスト開始...")
    print(f"Host: {host}")
    print(f"User: root")
    print(f"Password: {'*' * len(password)}")
    
    try:
        connection = pymysql.connect(
            host=host,
            user='root',
            password=password,
            charset='utf8mb4',
            connect_timeout=10
        )
        
        print("✅ 基本接続成功！")
        
        with connection.cursor() as cursor:
            cursor.execute("SHOW DATABASES")
            databases = cursor.fetchall()
            print(f"📊 利用可能データベース: {[db[0] for db in databases]}")
        
        connection.close()
        return True
        
    except Exception as e:
        print(f"❌ 接続エラー: {e}")
        return False

def test_database_connection():
    """データベース指定接続テスト"""
    host = "34.58.103.36"
    password = "Yuuku717"
    
    try:
        connection = pymysql.connect(
            host=host,
            user='root',
            password=password,
            database='miraikakaku_prod',
            charset='utf8mb4',
            connect_timeout=10
        )
        
        print("✅ データベース接続成功！")
        
        with connection.cursor() as cursor:
            cursor.execute("SELECT COUNT(*) FROM stock_master")
            count = cursor.fetchone()[0]
            print(f"📈 登録銘柄数: {count:,}")
            
            cursor.execute("SHOW TABLES")
            tables = cursor.fetchall()
            print(f"📋 テーブル一覧: {[table[0] for table in tables]}")
        
        connection.close()
        return True
        
    except Exception as e:
        print(f"❌ データベース接続エラー: {e}")
        return False

def test_new_password():
    """新しいパスワードでテスト"""
    host = "34.58.103.36"
    passwords = ["Yuuku717", "miraikakaku2024", "root123"]
    
    for password in passwords:
        print(f"\n🔑 パスワード '{password}' でテスト...")
        try:
            connection = pymysql.connect(
                host=host,
                user='root',
                password=password,
                charset='utf8mb4',
                connect_timeout=5
            )
            
            print(f"✅ パスワード '{password}' で接続成功！")
            connection.close()
            return password
            
        except Exception as e:
            print(f"❌ パスワード '{password}' 失敗: {e}")
    
    return None

if __name__ == "__main__":
    print("=" * 50)
    print("🚀 Cloud SQL接続診断ツール")
    print("=" * 50)
    
    # 基本接続テスト
    if test_basic_connection():
        # データベース接続テスト
        test_database_connection()
    else:
        # パスワード診断
        print("\n🔍 パスワード診断を実行...")
        working_password = test_new_password()
        if working_password:
            print(f"\n✅ 正しいパスワード発見: {working_password}")
        else:
            print("\n❌ 有効なパスワードが見つかりません")