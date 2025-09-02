#!/usr/bin/env python3
"""
stock_predictionsテーブルのデータ確認スクリプト
Cloud SQL内で実行するため、バッチジョブとして起動
"""

import pymysql
from datetime import datetime

def check_predictions_table():
    db_config = {
        "host": "34.58.103.36",
        "user": "miraikakaku-user",
        "password": "miraikakaku-secure-pass-2024",
        "database": "miraikakaku",
        "charset": "utf8mb4"
    }
    
    try:
        connection = pymysql.connect(**db_config)
        cursor = connection.cursor()
        
        print("🔍 stock_predictionsテーブル確認")
        print("=" * 60)
        
        # 1. テーブルの存在確認
        cursor.execute("""
            SELECT COUNT(*) 
            FROM information_schema.tables 
            WHERE table_schema = 'miraikakaku' 
            AND table_name = 'stock_predictions'
        """)
        table_exists = cursor.fetchone()[0] > 0
        
        if not table_exists:
            print("❌ stock_predictionsテーブルが存在しません")
            
            # テーブル作成
            print("📊 テーブルを作成中...")
            create_sql = """
            CREATE TABLE IF NOT EXISTS stock_predictions (
                id BIGINT AUTO_INCREMENT PRIMARY KEY,
                symbol VARCHAR(20) NOT NULL,
                prediction_date DATE NOT NULL,
                target_date DATE NOT NULL,
                prediction_horizon_days INT NOT NULL,
                predicted_open DECIMAL(10,3),
                predicted_high DECIMAL(10,3),
                predicted_low DECIMAL(10,3),
                predicted_close DECIMAL(10,3),
                predicted_volume BIGINT,
                actual_open DECIMAL(10,3),
                actual_high DECIMAL(10,3),
                actual_low DECIMAL(10,3),
                actual_close DECIMAL(10,3),
                actual_volume BIGINT,
                accuracy_score DECIMAL(5,4),
                mse_score DECIMAL(10,6),
                mae_score DECIMAL(10,6),
                direction_accuracy DECIMAL(5,4),
                model_name VARCHAR(50) NOT NULL,
                model_version VARCHAR(20),
                confidence_score DECIMAL(5,4),
                features_used TEXT,
                training_data_start DATE,
                training_data_end DATE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                INDEX idx_symbol_date (symbol, prediction_date),
                INDEX idx_target_date (target_date),
                INDEX idx_model (model_name, model_version),
                INDEX idx_accuracy (accuracy_score),
                UNIQUE KEY unique_prediction (symbol, prediction_date, target_date, model_name)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
            """
            cursor.execute(create_sql)
            connection.commit()
            print("✅ テーブル作成完了")
        else:
            print("✅ stock_predictionsテーブルが存在します")
        
        # 2. データ件数確認
        cursor.execute("SELECT COUNT(*) FROM stock_predictions")
        total_count = cursor.fetchone()[0]
        print(f"\n📊 総レコード数: {total_count:,}件")
        
        if total_count > 0:
            # 3. モデル別統計
            cursor.execute("""
                SELECT 
                    model_name,
                    COUNT(*) as count,
                    AVG(confidence_score) as avg_confidence,
                    MIN(prediction_date) as first_date,
                    MAX(prediction_date) as last_date
                FROM stock_predictions
                GROUP BY model_name
            """)
            
            print("\n📈 モデル別統計:")
            for row in cursor.fetchall():
                model, count, confidence, first, last = row
                print(f"  - {model}: {count:,}件")
                if confidence:
                    print(f"    信頼度: {confidence:.2%}")
                print(f"    期間: {first} ～ {last}")
            
            # 4. 最新の予測データ
            cursor.execute("""
                SELECT 
                    symbol,
                    prediction_date,
                    target_date,
                    predicted_close,
                    confidence_score,
                    model_name
                FROM stock_predictions
                ORDER BY created_at DESC
                LIMIT 5
            """)
            
            print("\n🔮 最新の予測データ (上位5件):")
            for row in cursor.fetchall():
                symbol, pred_date, target_date, price, conf, model = row
                print(f"  {symbol}: {pred_date} → {target_date}")
                print(f"    予測価格: ${price:.2f}, 信頼度: {conf:.2%}, モデル: {model}")
            
            # 5. 銘柄カバレッジ
            cursor.execute("""
                SELECT COUNT(DISTINCT symbol) as unique_symbols
                FROM stock_predictions
            """)
            unique_symbols = cursor.fetchone()[0]
            print(f"\n📊 予測対象銘柄数: {unique_symbols:,}銘柄")
            
        else:
            print("\n⚠️ まだ予測データが投入されていません")
            print("\n💡 データ投入方法:")
            print("  1. prediction_generatorバッチを実行")
            print("  2. APIの/api/finance/stocks/{symbol}/predictionsを呼び出し")
            print("  3. 機械学習モデルのトレーニングバッチを実行")
        
        # 6. 関連テーブルの確認
        cursor.execute("""
            SELECT 
                (SELECT COUNT(DISTINCT symbol) FROM stock_price_history) as price_symbols,
                (SELECT COUNT(*) FROM stock_price_history WHERE date >= DATE_SUB(NOW(), INTERVAL 1 DAY)) as recent_prices
        """)
        price_symbols, recent_prices = cursor.fetchone()
        
        print(f"\n📈 関連データ:")
        print(f"  - 価格データあり銘柄: {price_symbols:,}")
        print(f"  - 24時間以内の価格: {recent_prices:,}件")
        
        connection.close()
        print("\n✅ 確認完了")
        
    except Exception as e:
        print(f"❌ エラー: {e}")
        return False
    
    return True

if __name__ == "__main__":
    check_predictions_table()