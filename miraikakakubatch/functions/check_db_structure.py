#!/usr/bin/env python3
"""
データベース構造確認・修正スクリプト
"""

import pymysql

def main():
    db_config = {
        "host": "34.58.103.36",
        "user": "miraikakaku-user", 
        "password": "miraikakaku-secure-pass-2024",
        "database": "miraikakaku",
    }
    
    connection = pymysql.connect(**db_config)
    
    try:
        with connection.cursor() as cursor:
            # テーブル一覧確認
            cursor.execute("SHOW TABLES")
            tables = cursor.fetchall()
            print("=== 既存テーブル ===")
            for table in tables:
                print(f"- {table[0]}")
            
            print("\n=== stock_master構造 ===")
            cursor.execute("DESCRIBE stock_master")
            columns = cursor.fetchall()
            for column in columns:
                print(f"- {column[0]}: {column[1]}")
                
            print("\n=== stock_price_history構造 ===") 
            cursor.execute("DESCRIBE stock_price_history")
            columns = cursor.fetchall()
            for column in columns:
                print(f"- {column[0]}: {column[1]}")
                
    except Exception as e:
        print(f"エラー: {e}")
    finally:
        connection.close()

if __name__ == "__main__":
    main()