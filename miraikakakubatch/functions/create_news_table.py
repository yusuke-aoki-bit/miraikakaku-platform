#!/usr/bin/env python3
"""
financial_newsテーブル作成スクリプト
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
            # financial_newsテーブル作成
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS financial_news (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    title VARCHAR(500) NOT NULL,
                    summary TEXT,
                    content TEXT,
                    category VARCHAR(50),
                    published_at DATETIME,
                    source_url VARCHAR(500),
                    sentiment_score DECIMAL(3,2),
                    impact_score DECIMAL(3,2),
                    source VARCHAR(100),
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                    INDEX idx_category (category),
                    INDEX idx_published_at (published_at),
                    INDEX idx_source (source)
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
            """)
            
            connection.commit()
            print("✅ financial_newsテーブル作成完了")
            
    except Exception as e:
        print(f"エラー: {e}")
        connection.rollback()
    finally:
        connection.close()

if __name__ == "__main__":
    main()