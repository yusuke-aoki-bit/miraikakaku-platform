#!/usr/bin/env python3
"""
取得できない銘柄の分析
"""

import pymysql

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
        # 未収集銘柄の特徴を分析
        cursor.execute("""
            SELECT 
                market,
                country,
                COUNT(*) as count,
                SUBSTRING(GROUP_CONCAT(sm.symbol ORDER BY sm.symbol), 1, 50) as sample_symbols
            FROM stock_master sm
            LEFT JOIN stock_price_history sph ON sm.symbol = sph.symbol
            WHERE sm.is_active = 1 AND sph.symbol IS NULL
            GROUP BY market, country
            ORDER BY count DESC
            LIMIT 20
        """)
        
        print("📊 未収集銘柄の分析:")
        print("-" * 80)
        print(f"{'Market':<15} {'Country':<20} {'Count':<10} {'Sample Symbols'}")
        print("-" * 80)
        
        total_uncovered = 0
        for row in cursor.fetchall():
            market, country, count, samples = row
            total_uncovered += count
            print(f"{market or 'UNKNOWN':<15} {country or 'UNKNOWN':<20} {count:<10} {samples[:50]}")
        
        # シンボルパターンの分析
        cursor.execute("""
            SELECT 
                CASE 
                    WHEN symbol REGEXP '^[0-9]{4}$' THEN '4桁数字(日本株式)'
                    WHEN symbol REGEXP '^[0-9]{1,3}[A-Z]$' THEN '数字+文字(特殊)'
                    WHEN symbol REGEXP '^[A-Z]{1,5}$' THEN '英字のみ(米国株式)'
                    WHEN symbol REGEXP '^[0-9]{5,}$' THEN '5桁以上数字'
                    WHEN symbol LIKE '%.%' THEN 'ドット含む(国際)'
                    ELSE 'その他'
                END as pattern,
                COUNT(*) as count
            FROM stock_master sm
            LEFT JOIN stock_price_history sph ON sm.symbol = sph.symbol
            WHERE sm.is_active = 1 AND sph.symbol IS NULL
            GROUP BY pattern
            ORDER BY count DESC
        """)
        
        print("\n📈 シンボルパターン別未収集数:")
        print("-" * 50)
        for row in cursor.fetchall():
            pattern, count = row
            percentage = (count / total_uncovered * 100) if total_uncovered > 0 else 0
            print(f"{pattern:<30} {count:>6} ({percentage:>5.1f}%)")
            
finally:
    connection.close()