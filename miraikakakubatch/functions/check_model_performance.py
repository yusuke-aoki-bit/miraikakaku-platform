#!/usr/bin/env python3
"""
モデル性能テーブルの構造確認スクリプト
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
            print("=== モデル性能テーブル構造確認 ===\n")
            
            # モデル性能テーブルの構造
            print("【model_performance テーブル構造】")
            cursor.execute("DESCRIBE model_performance")
            columns = cursor.fetchall()
            for column in columns:
                print(f"- {column[0]}: {column[1]}")
            
            print()
            
            # AI推論ログテーブルの構造
            print("【ai_inference_log テーブル構造】")
            cursor.execute("DESCRIBE ai_inference_log")
            columns = cursor.fetchall()
            for column in columns:
                print(f"- {column[0]}: {column[1]}")
                
    except Exception as e:
        print(f"エラー: {e}")
        import traceback
        traceback.print_exc()
    finally:
        connection.close()

if __name__ == "__main__":
    main()