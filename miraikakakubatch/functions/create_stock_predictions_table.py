#!/usr/bin/env python3
"""
stock_predictionsテーブルの作成
株価予測データを格納するためのテーブル構造を定義・作成
"""

import pymysql
from datetime import datetime

db_config = {
    "host": "34.58.103.36",
    "user": "miraikakaku-user",
    "password": "miraikakaku-secure-pass-2024",
    "database": "miraikakaku",
    "charset": "utf8mb4"
}

def create_stock_predictions_table():
    """stock_predictionsテーブルを作成"""
    
    # テーブル作成SQL
    create_table_sql = """
    CREATE TABLE IF NOT EXISTS stock_predictions (
        id BIGINT AUTO_INCREMENT PRIMARY KEY,
        symbol VARCHAR(20) NOT NULL,
        prediction_date DATE NOT NULL,
        target_date DATE NOT NULL,
        prediction_horizon_days INT NOT NULL,
        
        -- 予測価格データ
        predicted_open DECIMAL(10,3),
        predicted_high DECIMAL(10,3),
        predicted_low DECIMAL(10,3),
        predicted_close DECIMAL(10,3),
        predicted_volume BIGINT,
        
        -- 実際の価格データ（後から更新）
        actual_open DECIMAL(10,3),
        actual_high DECIMAL(10,3),
        actual_low DECIMAL(10,3),
        actual_close DECIMAL(10,3),
        actual_volume BIGINT,
        
        -- 予測精度メトリクス
        accuracy_score DECIMAL(5,4),
        mse_score DECIMAL(10,6),
        mae_score DECIMAL(10,6),
        direction_accuracy DECIMAL(5,4),
        
        -- モデル情報
        model_name VARCHAR(50) NOT NULL,
        model_version VARCHAR(20),
        confidence_score DECIMAL(5,4),
        
        -- メタ情報
        features_used TEXT,
        training_data_start DATE,
        training_data_end DATE,
        
        -- システム情報
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
        
        -- インデックス
        INDEX idx_symbol_date (symbol, prediction_date),
        INDEX idx_target_date (target_date),
        INDEX idx_model (model_name, model_version),
        INDEX idx_accuracy (accuracy_score),
        
        -- ユニーク制約
        UNIQUE KEY unique_prediction (symbol, prediction_date, target_date, model_name)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
    """
    
    try:
        connection = pymysql.connect(**db_config)
        
        with connection.cursor() as cursor:
            print("📊 stock_predictionsテーブルを作成中...")
            
            # テーブル作成
            cursor.execute(create_table_sql)
            
            # 作成結果確認
            cursor.execute("DESCRIBE stock_predictions")
            columns = cursor.fetchall()
            
            print("✅ stock_predictionsテーブル作成完了！")
            print("\n🗄️ テーブル構造:")
            print("-" * 80)
            print(f"{'カラム名':<25} {'型':<20} {'NULL':<6} {'キー':<8} {'デフォルト':<15}")
            print("-" * 80)
            
            for col in columns:
                field, type_, null, key, default, extra = col
                print(f"{field:<25} {type_:<20} {null:<6} {key:<8} {str(default):<15}")
            
            # インデックス確認
            cursor.execute("SHOW INDEX FROM stock_predictions")
            indexes = cursor.fetchall()
            
            print(f"\n🔍 インデックス情報:")
            unique_indexes = set()
            for idx in indexes:
                if idx[1] not in unique_indexes:
                    key_name = idx[2]
                    column_name = idx[4]
                    unique = "YES" if idx[1] == 0 else "NO"
                    print(f"  - {key_name} on {column_name} (Unique: {unique})")
                    unique_indexes.add(idx[1])
            
            connection.commit()
            
            print(f"\n📋 テーブルの用途:")
            print("  - 機械学習モデルによる株価予測結果を格納")
            print("  - 予測精度の追跡とモデル評価")
            print("  - 複数モデルの予測結果比較")
            print("  - 予測と実際の価格の差分分析")
            
    except Exception as e:
        print(f"❌ エラー: {e}")
        return False
    
    finally:
        if 'connection' in locals():
            connection.close()
    
    return True

def create_prediction_accuracy_view():
    """予測精度確認用のビューも作成"""
    
    view_sql = """
    CREATE OR REPLACE VIEW prediction_accuracy_summary AS
    SELECT 
        model_name,
        model_version,
        COUNT(*) as total_predictions,
        AVG(accuracy_score) as avg_accuracy,
        AVG(direction_accuracy) as avg_direction_accuracy,
        AVG(confidence_score) as avg_confidence,
        MIN(prediction_date) as first_prediction,
        MAX(prediction_date) as last_prediction
    FROM stock_predictions 
    WHERE accuracy_score IS NOT NULL
    GROUP BY model_name, model_version
    ORDER BY avg_accuracy DESC
    """
    
    try:
        connection = pymysql.connect(**db_config)
        
        with connection.cursor() as cursor:
            cursor.execute(view_sql)
            print("✅ prediction_accuracy_summaryビュー作成完了！")
            
            connection.commit()
            
    except Exception as e:
        print(f"❌ ビュー作成エラー: {e}")
    
    finally:
        if 'connection' in locals():
            connection.close()

if __name__ == "__main__":
    print("🚀 stock_predictionsテーブル作成スクリプト")
    print("=" * 60)
    
    if create_stock_predictions_table():
        create_prediction_accuracy_view()
        print("\n🎉 すべての作業が完了しました！")
    else:
        print("\n❌ テーブル作成に失敗しました")