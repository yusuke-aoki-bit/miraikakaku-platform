#!/usr/bin/env python3
"""
大規模訓練データ生成システム
複数の銘柄に対して豊富な価格履歴と予測データを生成
"""

import pymysql
import pandas as pd
import numpy as np
import yfinance as yf
import logging
from datetime import datetime, timedelta
import random
import time
from typing import List, Dict, Tuple
import warnings
warnings.filterwarnings('ignore')

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class MassiveTrainingDataGenerator:
    def __init__(self):
        self.db_config = {
            "host": "34.58.103.36",
            "user": "miraikakaku-user", 
            "password": "miraikakaku-secure-pass-2024",
            "database": "miraikakaku",
        }
        self.batch_size = 50
        self.total_generated = 0
        
    def get_connection(self):
        return pymysql.connect(**self.db_config)

    def get_top_stocks_for_training(self, limit: int = 200) -> List[str]:
        """訓練用の主要銘柄を取得"""
        connection = self.get_connection()
        
        try:
            with connection.cursor() as cursor:
                # 既存の価格データがある銘柄を優先
                cursor.execute("""
                    SELECT DISTINCT sm.symbol, sm.name, sm.market, 
                           COUNT(sph.id) as price_count
                    FROM stock_master sm
                    LEFT JOIN stock_price_history sph ON sm.symbol = sph.symbol
                    WHERE sm.is_active = 1
                    GROUP BY sm.symbol, sm.name, sm.market
                    ORDER BY price_count DESC, sm.symbol
                    LIMIT %s
                """, (limit,))
                
                stocks = cursor.fetchall()
                symbols = [stock[0] for stock in stocks]
                
                logger.info(f"📊 訓練対象銘柄選出: {len(symbols)}銘柄")
                return symbols
                
        except Exception as e:
            logger.error(f"❌ 銘柄選出エラー: {e}")
            return []
        finally:
            connection.close()

    def generate_historical_prices(self, symbol: str, days_back: int = 365) -> bool:
        """指定銘柄の過去価格データを生成・補充"""
        connection = self.get_connection()
        
        try:
            # 既存データの最新日付を確認
            with connection.cursor() as cursor:
                cursor.execute("""
                    SELECT MAX(date) FROM stock_price_history 
                    WHERE symbol = %s
                """, (symbol,))
                
                latest_date = cursor.fetchone()[0]
                
                if latest_date:
                    start_date = latest_date + timedelta(days=1)
                else:
                    start_date = datetime.now() - timedelta(days=days_back)
                
                end_date = datetime.now()
                
                # 既に最新データがある場合はスキップ
                if start_date >= end_date:
                    return True
                
                # 合成データ生成（実際のAPIが使えない場合のフォールバック）
                current_date = start_date
                base_price = 100.0 + random.uniform(-20, 20)  # ベース価格
                
                price_data = []
                
                while current_date <= end_date:
                    # 価格変動シミュレーション
                    daily_change = random.uniform(-0.05, 0.05)  # -5%から+5%の変動
                    volume_base = random.randint(100000, 1000000)
                    
                    open_price = base_price * (1 + random.uniform(-0.01, 0.01))
                    close_price = base_price * (1 + daily_change)
                    high_price = max(open_price, close_price) * (1 + random.uniform(0, 0.02))
                    low_price = min(open_price, close_price) * (1 - random.uniform(0, 0.02))
                    volume = int(volume_base * (1 + abs(daily_change) * 10))
                    
                    price_data.append({
                        'symbol': symbol,
                        'date': current_date,
                        'open_price': round(open_price, 2),
                        'high_price': round(high_price, 2),
                        'low_price': round(low_price, 2),
                        'close_price': round(close_price, 2),
                        'volume': volume,
                        'adjusted_close': round(close_price, 2),
                        'data_source': 'synthetic_training',
                        'is_valid': 1,
                        'data_quality_score': random.uniform(0.8, 1.0)
                    })
                    
                    base_price = close_price  # 次の日のベース価格
                    current_date += timedelta(days=1)
                
                # バッチ挿入
                if price_data:
                    insert_query = """
                        INSERT INTO stock_price_history 
                        (symbol, date, open_price, high_price, low_price, close_price, 
                         volume, adjusted_close, data_source, is_valid, data_quality_score, created_at, updated_at)
                        VALUES (%(symbol)s, %(date)s, %(open_price)s, %(high_price)s, %(low_price)s, 
                                %(close_price)s, %(volume)s, %(adjusted_close)s, %(data_source)s, 
                                %(is_valid)s, %(data_quality_score)s, NOW(), NOW())
                        ON DUPLICATE KEY UPDATE
                        close_price = VALUES(close_price),
                        volume = VALUES(volume),
                        updated_at = NOW()
                    """
                    
                    cursor.executemany(insert_query, price_data)
                    connection.commit()
                    
                    logger.info(f"✅ {symbol}: {len(price_data)}件の価格データ生成完了")
                    return True
                
        except Exception as e:
            logger.error(f"❌ {symbol} 価格データ生成エラー: {e}")
            return False
        finally:
            connection.close()

    def generate_prediction_training_data(self, symbol: str, prediction_count: int = 50) -> bool:
        """指定銘柄の予測訓練データを生成"""
        connection = self.get_connection()
        
        try:
            with connection.cursor() as cursor:
                # 最新の価格データを取得
                cursor.execute("""
                    SELECT close_price FROM stock_price_history 
                    WHERE symbol = %s 
                    ORDER BY date DESC 
                    LIMIT 10
                """, (symbol,))
                
                recent_prices = cursor.fetchall()
                
                if not recent_prices:
                    logger.warning(f"⚠️ {symbol}: 価格データなし、予測データ生成をスキップ")
                    return False
                
                current_price = recent_prices[0][0]
                
                # 予測データを生成
                predictions = []
                
                for i in range(prediction_count):
                    # 予測日時（過去から現在まで分散）
                    days_ago = random.randint(1, 30)
                    prediction_date = datetime.now() - timedelta(days=days_ago)
                    
                    # 予測価格（現在価格を基準に変動）
                    price_change_pct = random.uniform(-0.10, 0.10)  # -10%から+10%
                    predicted_price = current_price * (1 + price_change_pct)
                    
                    # 信頼度スコア
                    confidence_score = random.uniform(0.6, 0.95)
                    
                    # モデル種別をランダム選択
                    model_types = ['lstm_training', 'random_forest_training', 'transformer_training', 'gru_training']
                    model_type = random.choice(model_types)
                    
                    predictions.append({
                        'symbol': symbol,
                        'prediction_date': prediction_date,
                        'predicted_price': round(predicted_price, 2),
                        'predicted_change': round(predicted_price - current_price, 2),
                        'predicted_change_percent': round(price_change_pct * 100, 2),
                        'confidence_score': round(confidence_score, 3),
                        'model_type': model_type,
                        'model_version': 'v3.0_training',
                        'prediction_horizon': random.choice([1, 3, 7, 14]),  # 予測期間（日）
                        'is_active': 1,
                        'is_accurate': None,  # 後で評価
                    })
                
                # 予測データを挿入
                if predictions:
                    insert_query = """
                        INSERT INTO stock_predictions 
                        (symbol, prediction_date, predicted_price, predicted_change, predicted_change_percent,
                         confidence_score, model_type, model_version, prediction_horizon, is_active, 
                         is_accurate, created_at)
                        VALUES (%(symbol)s, %(prediction_date)s, %(predicted_price)s, %(predicted_change)s, 
                                %(predicted_change_percent)s, %(confidence_score)s, %(model_type)s, 
                                %(model_version)s, %(prediction_horizon)s, %(is_active)s, %(is_accurate)s, NOW())
                    """
                    
                    cursor.executemany(insert_query, predictions)
                    connection.commit()
                    
                    logger.info(f"✅ {symbol}: {len(predictions)}件の予測データ生成完了")
                    return True
                    
        except Exception as e:
            logger.error(f"❌ {symbol} 予測データ生成エラー: {e}")
            return False
        finally:
            connection.close()

    def run_massive_data_generation(self, target_stocks: int = 100, predictions_per_stock: int = 30):
        """大規模訓練データ生成の実行"""
        logger.info("🚀 大規模訓練データ生成開始")
        start_time = time.time()
        
        # 対象銘柄取得
        symbols = self.get_top_stocks_for_training(target_stocks)
        
        if not symbols:
            logger.error("❌ 対象銘柄が見つかりません")
            return
        
        successful_prices = 0
        successful_predictions = 0
        
        # 各銘柄に対してデータ生成
        for i, symbol in enumerate(symbols, 1):
            logger.info(f"📈 [{i}/{len(symbols)}] {symbol} のデータ生成中...")
            
            # 価格データ生成
            if self.generate_historical_prices(symbol, days_back=180):
                successful_prices += 1
            
            # 予測データ生成
            if self.generate_prediction_training_data(symbol, predictions_per_stock):
                successful_predictions += 1
            
            # API制限を避けるため少し待機
            time.sleep(0.1)
            
            # 進捗表示
            if i % 10 == 0:
                progress = (i / len(symbols)) * 100
                logger.info(f"🔄 進捗: {progress:.1f}% ({i}/{len(symbols)})")
        
        execution_time = time.time() - start_time
        
        # 結果レポート
        logger.info("=" * 80)
        logger.info("📊 大規模訓練データ生成完了レポート")
        logger.info(f"⏱️  実行時間: {execution_time:.1f}秒")
        logger.info(f"🎯 対象銘柄数: {len(symbols)}")
        logger.info(f"✅ 価格データ生成成功: {successful_prices}銘柄")
        logger.info(f"✅ 予測データ生成成功: {successful_predictions}銘柄")
        logger.info(f"📈 推定総予測データ: {successful_predictions * predictions_per_stock:,}件")
        logger.info("=" * 80)

def main():
    generator = MassiveTrainingDataGenerator()
    
    # 大規模データ生成実行
    # - 上位100銘柄
    # - 1銘柄あたり30件の予測データ
    # - 過去180日分の価格データ
    generator.run_massive_data_generation(
        target_stocks=100,
        predictions_per_stock=30
    )

if __name__ == "__main__":
    main()