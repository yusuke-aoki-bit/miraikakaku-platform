#!/usr/bin/env python3
"""直接実行テスト用スクリプト"""

import pymysql
import random
import numpy as np
from datetime import datetime, timedelta
import logging

# ログ設定
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def main():
    logger.info("🚀 直接実行テスト開始")
    
    # データベース接続設定
    db_config = {
        "host": "34.58.103.36",
        "user": "miraikakaku-user",
        "password": "miraikakaku-secure-pass-2024",
        "database": "miraikakaku",
        "charset": "utf8mb4"
    }
    
    try:
        logger.info("📊 データベース接続中...")
        connection = pymysql.connect(**db_config)
        logger.info("✅ データベース接続成功")
        
        with connection.cursor() as cursor:
            # 銘柄データ取得 (collation問題回避)
            logger.info("📋 銘柄データ取得中...")
            cursor.execute("""
                SELECT symbol, name FROM stock_master 
                WHERE is_active = 1 
                ORDER BY symbol
                LIMIT 10
            """)
            
            stocks = cursor.fetchall()
            logger.info(f"💫 対象銘柄: {len(stocks)}件")
            
            if not stocks:
                logger.warning("⚠️ 銘柄データが見つかりません")
                return
            
            # テストデータ生成
            logger.info("🎲 テストデータ生成中...")
            models = ['test_lstm', 'test_transformer', 'test_ensemble']
            total_generated = 0
            
            for i, stock in enumerate(stocks):
                symbol = stock[0]
                logger.info(f"📈 処理中: {symbol}")
                
                # 各銘柄に5件の予測データ
                predictions = []
                for j in range(5):
                    horizon = random.choice([1, 3, 7])
                    prediction_date = datetime.now() - timedelta(days=random.randint(0, 7))
                    
                    base_price = random.uniform(500, 3000)
                    volatility = random.uniform(0.01, 0.03)
                    price_change = random.gauss(0, volatility)
                    predicted_price = max(10, base_price * (1 + price_change))
                    
                    confidence = random.uniform(0.70, 0.85)
                    model_type = random.choice(models)
                    
                    predictions.append((
                        symbol, 
                        prediction_date.strftime('%Y-%m-%d %H:%M:%S'),
                        round(predicted_price, 2),
                        round(predicted_price - base_price, 2),
                        round(((predicted_price - base_price) / base_price) * 100, 2),
                        round(confidence, 3), 
                        model_type, 
                        'test_v1.0', 
                        horizon, 
                        1,
                        'DirectTest'
                    ))
                
                # データ挿入
                if predictions:
                    cursor.executemany("""
                        INSERT INTO stock_predictions 
                        (symbol, prediction_date, predicted_price, predicted_change, 
                         predicted_change_percent, confidence_score, model_type, 
                         model_version, prediction_horizon, is_active, notes, created_at)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, NOW())
                    """, predictions)
                    
                    connection.commit()
                    total_generated += len(predictions)
                    logger.info(f"✅ {symbol}: {len(predictions)}件挿入")
            
            logger.info(f"🎯 完了: 合計 {total_generated}件のテストデータを生成")
            
            # 生成結果確認
            cursor.execute("""
                SELECT COUNT(*) as count, model_type 
                FROM stock_predictions 
                WHERE notes = 'DirectTest' 
                GROUP BY model_type
            """)
            
            results = cursor.fetchall()
            logger.info("📊 生成結果:")
            for result in results:
                logger.info(f"  - {result[1]}: {result[0]}件")
                
    except Exception as e:
        logger.error(f"❌ エラー: {e}")
        return
    finally:
        if 'connection' in locals():
            connection.close()
            logger.info("🔐 データベース接続終了")

if __name__ == "__main__":
    main()