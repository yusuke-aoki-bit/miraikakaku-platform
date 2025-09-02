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
        # 全銘柄数を確認
        cursor.execute("SELECT COUNT(*) FROM stock_master WHERE is_active = 1")
        total_stocks = cursor.fetchone()[0]
        
        # データが存在する銘柄数を確認
        cursor.execute("""
            SELECT COUNT(DISTINCT sm.symbol) 
            FROM stock_master sm 
            JOIN stock_price_history sph ON sm.symbol = sph.symbol
            WHERE sm.is_active = 1
        """)
        covered_stocks = cursor.fetchone()[0]
        
        # カバー率計算
        coverage_rate = (covered_stocks / total_stocks) * 100 if total_stocks > 0 else 0
        
        print(f"📊 データ収集カバレッジ状況:")
        print(f"✅ 総銘柄数: {total_stocks:,}")
        print(f"✅ データ収集済み: {covered_stocks:,}")
        print(f"📈 カバー率: {coverage_rate:.1f}%")
        print(f"🎯 未収集: {total_stocks - covered_stocks:,}銘柄")
        
        # データソース別の銘柄数
        cursor.execute("""
            SELECT data_source, COUNT(DISTINCT symbol) as unique_symbols
            FROM stock_price_history 
            GROUP BY data_source
            ORDER BY unique_symbols DESC
        """)
        
        print(f"\n📈 データソース別カバレッジ:")
        for row in cursor.fetchall():
            print(f"  - {row[0]}: {row[1]:,}銘柄")
        
        # 未収集の銘柄をサンプル表示
        cursor.execute("""
            SELECT sm.symbol, sm.name, sm.market, sm.country
            FROM stock_master sm
            LEFT JOIN stock_price_history sph ON sm.symbol = sph.symbol
            WHERE sm.is_active = 1 AND sph.symbol IS NULL
            ORDER BY sm.symbol
            LIMIT 20
        """)
        
        print(f"\n🔍 未収集銘柄（サンプル20件）:")
        for row in cursor.fetchall():
            print(f"  {row[0]} - {row[1]} ({row[2]}, {row[3]})")
        
        print(f"\n🚀 100%達成まで: あと{100 - coverage_rate:.1f}%")
        
finally:
    connection.close()