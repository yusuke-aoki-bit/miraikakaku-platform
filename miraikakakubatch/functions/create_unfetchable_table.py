#!/usr/bin/env python3
"""
実データが取得できない銘柄を記録するテーブルを作成
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
        # unfetchable_stocks テーブルを作成
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS unfetchable_stocks (
                id INT AUTO_INCREMENT PRIMARY KEY,
                symbol VARCHAR(20) NOT NULL UNIQUE,
                reason VARCHAR(100) NOT NULL,
                attempted_at DATETIME NOT NULL,
                attempt_count INT DEFAULT 1,
                notes TEXT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                INDEX idx_symbol (symbol),
                INDEX idx_attempted_at (attempted_at)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
        """)
        
        connection.commit()
        print("✅ unfetchable_stocks テーブルを作成しました")
        
        # 既存の統計を表示
        cursor.execute("SELECT COUNT(*) FROM unfetchable_stocks")
        count = cursor.fetchone()[0]
        print(f"📊 現在のunfetchable銘柄数: {count}")
        
finally:
    connection.close()