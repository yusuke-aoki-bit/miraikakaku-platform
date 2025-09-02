#!/usr/bin/env python3
import pymysql
from datetime import datetime, timedelta

db_config = {
    "host": "34.58.103.36",
    "user": "miraikakaku-user",
    "password": "miraikakaku-secure-pass-2024",
    "database": "miraikakaku",
    "charset": "utf8mb4"
}

connection = pymysql.connect(**db_config)

try:
    with connection.cursor() as cursor:
        # 最近10分のデータを確認
        cursor.execute("""
            SELECT 
                COUNT(*) as total_records,
                MAX(created_at) as latest_update,
                COUNT(DISTINCT symbol) as unique_symbols
            FROM stock_price_history 
            WHERE created_at > DATE_SUB(NOW(), INTERVAL 10 MINUTE)
        """)
        result = cursor.fetchone()
        
        print("📊 改善されたバッチジョブ実行結果:")
        print(f"✅ 過去10分で収集されたレコード数: {result[0]:,}")
        print(f"✅ 最終更新時刻: {result[1]}")
        print(f"✅ ユニーク銘柄数: {result[2]:,}")
        
        # データソース別の集計（最近10分）
        cursor.execute("""
            SELECT 
                COALESCE(data_source, 'unknown') as source,
                COUNT(*) as count,
                COUNT(DISTINCT symbol) as unique_symbols
            FROM stock_price_history 
            WHERE created_at > DATE_SUB(NOW(), INTERVAL 10 MINUTE)
            GROUP BY data_source
            ORDER BY count DESC
        """)
        
        print("\n📈 データソース別集計（過去10分）:")
        for row in cursor.fetchall():
            print(f"  - {row[0]}: {row[1]:,}件 ({row[2]:,}銘柄)")
        
        # 最新のデータサンプル
        cursor.execute("""
            SELECT symbol, data_source, date, close_price, created_at
            FROM stock_price_history 
            WHERE created_at > DATE_SUB(NOW(), INTERVAL 10 MINUTE)
            ORDER BY created_at DESC
            LIMIT 5
        """)
        
        print("\n📋 最新データサンプル:")
        for row in cursor.fetchall():
            print(f"  {row[0]} ({row[1]}): ${row[3]:.2f} - {row[2]} [{row[4]}]")
            
finally:
    connection.close()