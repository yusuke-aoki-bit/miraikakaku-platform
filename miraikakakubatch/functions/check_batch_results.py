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
        # 最近のデータ収集状況を確認
        cursor.execute("""
            SELECT 
                COUNT(*) as total_records,
                MAX(created_at) as latest_update,
                COUNT(DISTINCT symbol) as unique_symbols
            FROM stock_price_history 
            WHERE created_at > DATE_SUB(NOW(), INTERVAL 24 HOUR)
        """)
        result = cursor.fetchone()
        
        print("📊 バッチジョブ実行結果:")
        print(f"✅ 過去24時間で収集されたレコード数: {result[0]:,}")
        print(f"✅ 最終更新時刻: {result[1]}")
        print(f"✅ ユニーク銘柄数: {result[2]:,}")
        
        # データソース別の集計
        cursor.execute("""
            SELECT 
                COALESCE(data_source, 'unknown') as source,
                COUNT(*) as count
            FROM stock_price_history 
            WHERE created_at > DATE_SUB(NOW(), INTERVAL 24 HOUR)
            GROUP BY data_source
        """)
        
        print("\n📈 データソース別集計:")
        for row in cursor.fetchall():
            print(f"  - {row[0]}: {row[1]:,}件")
            
finally:
    connection.close()