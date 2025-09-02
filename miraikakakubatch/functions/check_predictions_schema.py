#!/usr/bin/env python3
"""
stock_predictionsテーブルの存在確認とスキーマチェック
"""

import pymysql

db_config = {
    "host": "34.58.103.36",
    "user": "miraikakaku-user",
    "password": "miraikakaku-secure-pass-2024",
    "database": "miraikakaku",
    "charset": "utf8mb4"
}

def check_predictions_schema():
    connection = pymysql.connect(**db_config)
    
    try:
        with connection.cursor() as cursor:
            print("🔍 予測関連テーブルの確認")
            print("=" * 50)
            
            # 予測関連テーブル一覧
            cursor.execute("SHOW TABLES LIKE '%prediction%'")
            prediction_tables = cursor.fetchall()
            
            print("📊 予測関連テーブル:")
            if prediction_tables:
                for table in prediction_tables:
                    print(f"  - {table[0]}")
                    
                    # テーブル構造を確認
                    cursor.execute(f"DESCRIBE {table[0]}")
                    columns = cursor.fetchall()
                    print(f"    構造:")
                    for col in columns:
                        print(f"      {col[0]} {col[1]} {col[2]} {col[3]} {col[4]} {col[5]}")
                    print()
            else:
                print("  - 予測関連テーブルは存在しません")
            
            # 既存の関連テーブル確認
            print("\n🗄️ 既存の関連テーブル:")
            cursor.execute("SHOW TABLES")
            all_tables = [table[0] for table in cursor.fetchall()]
            
            relevant_tables = [t for t in all_tables if any(keyword in t.lower() 
                             for keyword in ['stock', 'price', 'prediction', 'forecast', 'model'])]
            
            for table in relevant_tables:
                cursor.execute(f"SELECT COUNT(*) FROM {table}")
                count = cursor.fetchone()[0]
                print(f"  - {table}: {count:,} records")
                
    finally:
        connection.close()

if __name__ == "__main__":
    check_predictions_schema()