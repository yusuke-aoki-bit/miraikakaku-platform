#!/usr/bin/env python3
import pymysql

db_config = {
    "host": "34.58.103.36",
    "user": "miraikakaku-user",
    "password": "miraikakaku-secure-pass-2024",
    "database": "miraikakaku",
    "charset": "utf8mb4"
}

connection = pymysql.connect(**db_config)

with connection.cursor() as cursor:
    cursor.execute("DESCRIBE stock_price_history")
    print("📊 stock_price_history テーブル構造:")
    for row in cursor.fetchall():
        print(f"  {row[0]}: {row[1]}")

connection.close()