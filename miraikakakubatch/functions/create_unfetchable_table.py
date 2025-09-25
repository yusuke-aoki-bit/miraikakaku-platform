#!/usr/bin/env python3
"""
実データが取得できない銘柄を記録するテーブルを作成
"""

import psycopg2
import psycopg2.extras

db_config = {
    "host": "34.173.9.214",
    "user": "postgres",
    "password": "miraikakaku-postgres-secure-2024",
    "database": "miraikakaku",
    "port": 5432
}

connection = psycopg2.connect(**db_config)

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