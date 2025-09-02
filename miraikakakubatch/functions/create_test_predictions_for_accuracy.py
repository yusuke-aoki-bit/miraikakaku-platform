#!/usr/bin/env python3
"""
精度評価用テスト予測データ生成
実際の価格データがある過去の日付で予測データを作成
"""

import pymysql
import logging
from datetime import datetime, timedelta
import numpy as np

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TestPredictionCreator:
    def __init__(self):
        self.db_config = {
            "host": "34.58.103.36",
            "user": "miraikakaku-user", 
            "password": "miraikakaku-secure-pass-2024",
            "database": "miraikakaku",
        }

    def get_connection(self):
        return pymysql.connect(**self.db_config)

    def get_recent_price_data(self):
        """最近の価格データを取得"""
        connection = self.get_connection()
        
        try:
            with connection.cursor() as cursor:
                cursor.execute("""
                    SELECT DISTINCT symbol, date, close_price
                    FROM stock_price_history
                    WHERE date >= DATE_SUB(NOW(), INTERVAL 10 DAY)
                    AND symbol IN ('AAPL', 'MSFT', 'GOOGL', '7203', '6758')
                    ORDER BY symbol, date DESC
                """)
                
                results = cursor.fetchall()
                logger.info(f"📊 取得した価格データ: {len(results)}件")
                return results
                
        finally:
            connection.close()

    def create_test_predictions(self, price_data):
        """テスト用予測データ作成"""
        connection = self.get_connection()
        
        try:
            with connection.cursor() as cursor:
                # 既存のテスト予測データを削除
                cursor.execute("""
                    DELETE FROM stock_predictions 
                    WHERE model_type IN ('lstm_test_accuracy', 'vertexai_test_accuracy')
                """)
                
                created_count = 0
                
                for symbol, date, actual_price in price_data:
                    # LSTM予測（実際価格に±5%のノイズ）
                    lstm_noise = np.random.normal(0, 0.05)  # 5%のノイズ
                    lstm_predicted = actual_price * (1 + lstm_noise)
                    lstm_confidence = 0.75 + np.random.random() * 0.1
                    
                    cursor.execute("""
                        INSERT INTO stock_predictions 
                        (symbol, prediction_date, predicted_price, predicted_change_percent,
                         confidence_score, model_type, model_version, prediction_horizon,
                         created_at, is_active)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, 1)
                    """, (
                        symbol, date, lstm_predicted, lstm_noise * 100,
                        lstm_confidence, 'lstm_test_accuracy', 'v_accuracy_test', -1,
                        date - timedelta(hours=1)  # 予測は実際の価格より1時間前に作成されたことにする
                    ))
                    
                    # VertexAI予測（実際価格に±3%のノイズ、LSTMより精度良く設定）
                    vertexai_noise = np.random.normal(0, 0.03)  # 3%のノイズ
                    vertexai_predicted = actual_price * (1 + vertexai_noise)
                    vertexai_confidence = 0.80 + np.random.random() * 0.1
                    
                    cursor.execute("""
                        INSERT INTO stock_predictions 
                        (symbol, prediction_date, predicted_price, predicted_change_percent,
                         confidence_score, model_type, model_version, prediction_horizon,
                         created_at, is_active)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, 1)
                    """, (
                        symbol, date, vertexai_predicted, vertexai_noise * 100,
                        vertexai_confidence, 'vertexai_test_accuracy', 'v_accuracy_test', -1,
                        date - timedelta(hours=1)
                    ))
                    
                    created_count += 2  # LSTM + VertexAI
                
                connection.commit()
                logger.info(f"✅ テスト予測データ作成完了: {created_count}件")
                
        finally:
            connection.close()

    def verify_test_data(self):
        """テストデータ検証"""
        connection = self.get_connection()
        
        try:
            with connection.cursor() as cursor:
                # 作成された予測データ確認
                cursor.execute("""
                    SELECT model_type, COUNT(*) as count
                    FROM stock_predictions 
                    WHERE model_type IN ('lstm_test_accuracy', 'vertexai_test_accuracy')
                    GROUP BY model_type
                """)
                
                results = cursor.fetchall()
                logger.info("📊 作成されたテスト予測データ:")
                for model_type, count in results:
                    logger.info(f"  {model_type}: {count}件")
                
                # サンプル表示
                cursor.execute("""
                    SELECT symbol, prediction_date, predicted_price, model_type
                    FROM stock_predictions 
                    WHERE model_type IN ('lstm_test_accuracy', 'vertexai_test_accuracy')
                    ORDER BY symbol, prediction_date, model_type
                    LIMIT 10
                """)
                
                samples = cursor.fetchall()
                logger.info("📋 テスト予測データサンプル:")
                for sample in samples:
                    logger.info(f"  {sample[0]} {sample[1]} ¥{sample[2]:.2f} [{sample[3]}]")
                
        finally:
            connection.close()

    def create_accuracy_test_data(self):
        """精度テスト用データ作成"""
        start_time = datetime.now()
        logger.info(f"🚀 精度テスト用予測データ作成開始: {start_time.strftime('%Y-%m-%d %H:%M:%S')}")
        
        try:
            # 1. 最近の価格データ取得
            price_data = self.get_recent_price_data()
            
            if not price_data:
                logger.error("❌ 価格データが見つかりません")
                return
            
            # 2. テスト予測データ作成
            self.create_test_predictions(price_data)
            
            # 3. データ検証
            self.verify_test_data()
            
        except Exception as e:
            logger.error(f"❌ テストデータ作成エラー: {e}")
            import traceback
            traceback.print_exc()
        
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        logger.info(f"✅ テストデータ作成完了 (実行時間: {duration:.1f}秒)")

if __name__ == "__main__":
    creator = TestPredictionCreator()
    
    try:
        creator.create_accuracy_test_data()
        
    except KeyboardInterrupt:
        logger.info("🛑 手動停止")
    except Exception as e:
        logger.error(f"❌ システムエラー: {e}")
        import traceback
        traceback.print_exc()