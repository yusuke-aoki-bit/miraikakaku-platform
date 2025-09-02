#!/usr/bin/env python3
"""
実データ収集の進捗をモニタリング
"""

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
        print("🔍 実データ収集進捗レポート")
        print("=" * 60)
        
        # 全体的な統計
        cursor.execute("""
            SELECT 
                (SELECT COUNT(*) FROM stock_master WHERE is_active = 1) as total_active,
                (SELECT COUNT(DISTINCT sm.symbol) 
                 FROM stock_master sm 
                 JOIN stock_price_history sph ON sm.symbol = sph.symbol
                 WHERE sm.is_active = 1) as covered,
                (SELECT COUNT(*) FROM unfetchable_stocks) as unfetchable
        """)
        total_active, covered, unfetchable = cursor.fetchone()
        
        remaining = total_active - covered - unfetchable
        coverage_rate = (covered / total_active * 100) if total_active > 0 else 0
        effective_coverage = ((covered + unfetchable) / total_active * 100) if total_active > 0 else 0
        
        print(f"📊 全体統計:")
        print(f"  - 総銘柄数: {total_active:,}")
        print(f"  - データ収集済み: {covered:,}")
        print(f"  - 取得不可能(記録済み): {unfetchable:,}")
        print(f"  - 残り未処理: {remaining:,}")
        print(f"  - 実データカバー率: {coverage_rate:.1f}%")
        print(f"  - 実質カバー率: {effective_coverage:.1f}%")
        
        # 最近の活動
        cursor.execute("""
            SELECT COUNT(*) FROM stock_price_history 
            WHERE created_at > DATE_SUB(NOW(), INTERVAL 30 MINUTE)
        """)
        recent_records = cursor.fetchone()[0]
        
        cursor.execute("""
            SELECT COUNT(*) FROM unfetchable_stocks 
            WHERE attempted_at > DATE_SUB(NOW(), INTERVAL 30 MINUTE)
        """)
        recent_unfetchable = cursor.fetchone()[0]
        
        print(f"\n📈 過去30分の活動:")
        print(f"  - 新規データレコード: {recent_records:,}")
        print(f"  - 新規unfetchable記録: {recent_unfetchable:,}")
        
        # データソース別の最新統計
        cursor.execute("""
            SELECT 
                data_source, 
                COUNT(DISTINCT symbol) as symbols,
                COUNT(*) as records
            FROM stock_price_history 
            WHERE created_at > DATE_SUB(NOW(), INTERVAL 1 HOUR)
            GROUP BY data_source
            ORDER BY symbols DESC
            LIMIT 10
        """)
        
        print(f"\n🔄 過去1時間のデータソース別収集:")
        for row in cursor.fetchall():
            source, symbols, records = row
            print(f"  - {source}: {symbols}銘柄 ({records:,}レコード)")
        
        # unfetchable理由の統計
        cursor.execute("""
            SELECT reason, COUNT(*) as count 
            FROM unfetchable_stocks 
            GROUP BY reason 
            ORDER BY count DESC
            LIMIT 5
        """)
        
        print(f"\n🚫 取得不可能な理由 (TOP5):")
        for row in cursor.fetchall():
            reason, count = row
            print(f"  - {reason}: {count:,}件")
        
        # 100%達成までの予測
        if remaining > 0:
            print(f"\n🎯 100%達成に向けて:")
            print(f"  - 残り処理対象: {remaining:,}銘柄")
            print(f"  - 現在の実質カバー率: {effective_coverage:.1f}%")
            if effective_coverage < 100:
                print(f"  - 100%まで: あと{100 - effective_coverage:.1f}%")
        else:
            print(f"\n🎉 すべての銘柄が処理済みです！")
            print(f"  - 実データカバー率: {coverage_rate:.1f}%")
            print(f"  - 実質カバー率: {effective_coverage:.1f}%")
            
finally:
    connection.close()