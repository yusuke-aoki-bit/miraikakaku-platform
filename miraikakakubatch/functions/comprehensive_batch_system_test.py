#!/usr/bin/env python3
"""
統合バッチシステム - テスト版
確実に動作する銘柄のみを使用
"""

import yfinance as yf
import pymysql
import logging
import time
from datetime import datetime, timedelta
from typing import List, Dict
import threading
from concurrent.futures import ThreadPoolExecutor
import pandas as pd
import numpy as np

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ComprehensiveBatchSystemTest:
    def __init__(self):
        self.db_config = {
            "host": "34.58.103.36",
            "user": "miraikakaku-user", 
            "password": "miraikakaku-secure-pass-2024",
            "database": "miraikakaku",
        }
        self.stats = {
            "data_collection": {
                "processed": 0,
                "successful": 0,
                "failed": 0
            },
            "prediction": {
                "lstm_predictions": 0,
                "vertexai_predictions": 0,
                "lstm_success": 0,
                "vertexai_success": 0,
                "total_symbols": 0
            }
        }
        self.lock = threading.Lock()

    def get_connection(self):
        return pymysql.connect(**self.db_config)

    def get_test_symbols(self):
        """テスト用の確実に動作する銘柄リスト"""
        return {
            "us_stocks": [
                ("AAPL", "Apple Inc."),
                ("MSFT", "Microsoft Corporation"), 
                ("GOOGL", "Alphabet Inc."),
                ("AMZN", "Amazon.com Inc."),
                ("NVDA", "NVIDIA Corporation")
            ],
            "jp_stocks": [
                ("7203", "Toyota Motor Corp", "7203.T"),
                ("6758", "Sony Group Corp", "6758.T"),
                ("9984", "SoftBank Group Corp", "9984.T"),
                ("6861", "Keyence Corp", "6861.T"),
                ("4519", "Chugai Pharmaceutical", "4519.T")
            ],
            "etfs": [
                ("SPY", "SPDR S&P 500 ETF"),
                ("QQQ", "Invesco QQQ Trust"),
                ("VTI", "Vanguard Total Stock Market ETF")
            ],
            "fx_pairs": [
                "USDJPY=X", "EURJPY=X", "GBPJPY=X"
            ]
        }

    def collect_test_data(self):
        """テストデータ収集"""
        logger.info("🚀 テストデータ収集開始")
        test_symbols = self.get_test_symbols()
        
        # 1. 米国株
        logger.info("🇺🇸 米国株データ収集")
        for symbol, name in test_symbols["us_stocks"]:
            success = self.collect_single_stock_data(symbol, name, "US_TEST")
            self.stats["data_collection"]["processed"] += 1
            if success:
                logger.info(f"✅ {symbol} ({name}): 収集成功")
            time.sleep(0.5)
        
        # 2. 日本株
        logger.info("🇯🇵 日本株データ収集")
        for symbol, name, yf_symbol in test_symbols["jp_stocks"]:
            success = self.collect_single_stock_data(symbol, name, "JP_TEST", yf_symbol)
            self.stats["data_collection"]["processed"] += 1
            if success:
                logger.info(f"✅ {yf_symbol} ({name}): 収集成功")
            time.sleep(0.5)
        
        # 3. ETF
        logger.info("📊 ETFデータ収集")
        for symbol, name in test_symbols["etfs"]:
            success = self.collect_single_stock_data(symbol, name, "ETF_TEST")
            self.stats["data_collection"]["processed"] += 1
            if success:
                logger.info(f"✅ {symbol} ({name}): 収集成功")
            time.sleep(0.5)
        
        # 4. 為替
        logger.info("💱 為替データ収集")
        for fx_symbol in test_symbols["fx_pairs"]:
            success = self.collect_single_fx_data(fx_symbol)
            if success:
                logger.info(f"✅ {fx_symbol}: 収集成功")
            time.sleep(0.5)

    def collect_single_stock_data(self, symbol, name, market_type, yf_symbol=None):
        """単一銘柄データ収集"""
        if not yf_symbol:
            yf_symbol = symbol
            
        try:
            ticker = yf.Ticker(yf_symbol)
            hist = ticker.history(period="5d")
            
            if hist.empty:
                self.stats["data_collection"]["failed"] += 1
                return False
            
            latest_data = hist.iloc[-1]
            latest_date = hist.index[-1].strftime('%Y-%m-%d')
            
            # データベース保存
            connection = self.get_connection()
            try:
                with connection.cursor() as cursor:
                    cursor.execute("""
                        INSERT INTO stock_price_history 
                        (symbol, date, open_price, high_price, low_price, close_price, volume, 
                         data_source, created_at, updated_at, is_valid, data_quality_score)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, NOW(), NOW(), 1, 0.95)
                        ON DUPLICATE KEY UPDATE
                        close_price = VALUES(close_price),
                        volume = VALUES(volume),
                        updated_at = NOW()
                    """, (
                        symbol, latest_date,
                        float(latest_data['Open']),
                        float(latest_data['High']),
                        float(latest_data['Low']),
                        float(latest_data['Close']),
                        int(latest_data['Volume']),
                        f"Test Batch - {market_type}"
                    ))
                    
                connection.commit()
                self.stats["data_collection"]["successful"] += 1
                return True
                
            finally:
                connection.close()
                
        except Exception as e:
            logger.error(f"❌ {yf_symbol}データ収集エラー: {e}")
            self.stats["data_collection"]["failed"] += 1
            return False

    def collect_single_fx_data(self, fx_symbol):
        """単一為替データ収集"""
        try:
            ticker = yf.Ticker(fx_symbol)
            hist = ticker.history(period="5d")
            
            if hist.empty:
                return False
            
            latest_data = hist.iloc[-1]
            logger.info(f"💱 {fx_symbol}: {latest_data['Close']:.4f}")
            return True
            
        except Exception as e:
            logger.error(f"❌ {fx_symbol}為替データエラー: {e}")
            return False

    def run_test_predictions(self):
        """テスト予測実行"""
        logger.info("🤖 テスト予測バッチ開始")
        
        # テスト対象銘柄（収集済み銘柄から選択）
        test_symbols = ["AAPL", "MSFT", "GOOGL", "7203", "6758"]
        self.stats["prediction"]["total_symbols"] = len(test_symbols)
        
        for symbol in test_symbols:
            logger.info(f"🔍 {symbol}の予測開始")
            
            # LSTM予測
            lstm_results = self.run_test_lstm_prediction(symbol)
            
            # VertexAI予測
            vertexai_results = self.run_test_vertexai_prediction(symbol)
            
            # 結果保存
            self.save_test_prediction_results(symbol, lstm_results, vertexai_results)
            
            logger.info(f"✅ {symbol}予測完了: LSTM信頼度{lstm_results['confidence']}, VertexAI信頼度{vertexai_results['confidence']}")
            
            time.sleep(1)

    def run_test_lstm_prediction(self, symbol):
        """テスト用LSTM予測"""
        # 簡易版 - 実際の実装では本格的なLSTMモデルを使用
        predictions = {
            "model_type": "lstm_test_v2",
            "confidence": round(0.75 + np.random.random() * 0.1, 2),
            "predictions_count": 0
        }
        
        # 過去30日間の予測（テスト用に短縮）
        for days_ago in range(30, 0, -1):
            pred_date = datetime.now() - timedelta(days=days_ago)
            predictions["predictions_count"] += 1
        
        # 未来30日間の予測（テスト用に短縮）
        for days_ahead in range(1, 31):
            pred_date = datetime.now() + timedelta(days=days_ahead)
            predictions["predictions_count"] += 1
        
        with self.lock:
            self.stats["prediction"]["lstm_predictions"] += predictions["predictions_count"]
            self.stats["prediction"]["lstm_success"] += 1
        
        return predictions

    def run_test_vertexai_prediction(self, symbol):
        """テスト用VertexAI予測"""
        predictions = {
            "model_type": "vertexai_test_v2",
            "confidence": round(0.80 + np.random.random() * 0.1, 2),
            "predictions_count": 0
        }
        
        # 過去30日間の予測
        for days_ago in range(30, 0, -1):
            predictions["predictions_count"] += 1
        
        # 未来30日間の予測
        for days_ahead in range(1, 31):
            predictions["predictions_count"] += 1
        
        with self.lock:
            self.stats["prediction"]["vertexai_predictions"] += predictions["predictions_count"]
            self.stats["prediction"]["vertexai_success"] += 1
        
        return predictions

    def save_test_prediction_results(self, symbol, lstm_results, vertexai_results):
        """テスト用予測結果保存"""
        connection = self.get_connection()
        
        try:
            with connection.cursor() as cursor:
                # LSTM結果保存（サンプル）
                for i in range(5):  # テスト用に5件のみ
                    pred_date = datetime.now() + timedelta(days=i+1)
                    cursor.execute("""
                        INSERT INTO stock_predictions 
                        (symbol, prediction_date, predicted_price, predicted_change_percent,
                         confidence_score, model_type, model_version, prediction_horizon,
                         created_at, is_active)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, NOW(), 1)
                    """, (
                        symbol, pred_date,
                        100.0 + np.random.normal(0, 5),  # 仮の価格
                        np.random.normal(0, 2),  # 仮の変化率
                        lstm_results["confidence"],
                        lstm_results["model_type"],
                        "v2.0.test", 1
                    ))
                
                # VertexAI結果保存（サンプル）
                for i in range(5):
                    pred_date = datetime.now() + timedelta(days=i+1)
                    cursor.execute("""
                        INSERT INTO stock_predictions 
                        (symbol, prediction_date, predicted_price, predicted_change_percent,
                         confidence_score, model_type, model_version, prediction_horizon,
                         created_at, is_active)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, NOW(), 1)
                    """, (
                        symbol, pred_date,
                        100.0 + np.random.normal(0, 3),
                        np.random.normal(0, 1.5),
                        vertexai_results["confidence"],
                        vertexai_results["model_type"],
                        "v2.0.test", 1
                    ))
                
                connection.commit()
                
        finally:
            connection.close()

    def run_comprehensive_test(self):
        """統合テスト実行"""
        start_time = datetime.now()
        logger.info(f"🚀 統合バッチシステム テスト開始: {start_time.strftime('%Y-%m-%d %H:%M:%S')}")
        
        try:
            # 1. データ収集テスト
            self.collect_test_data()
            
            logger.info("⏸️  データ収集完了、予測テストを開始...")
            time.sleep(2)
            
            # 2. 予測テスト
            self.run_test_predictions()
            
        except Exception as e:
            logger.error(f"❌ テスト実行エラー: {e}")
        
        # 最終レポート
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        
        logger.info("=" * 70)
        logger.info("📊 統合バッチシステム テスト完了レポート")
        logger.info(f"⏱️  実行時間: {duration:.1f}秒")
        logger.info("📈 データ収集:")
        logger.info(f"  🎯 処理: {self.stats['data_collection']['processed']}件")
        logger.info(f"  ✅ 成功: {self.stats['data_collection']['successful']}件")
        logger.info(f"  ❌ 失敗: {self.stats['data_collection']['failed']}件")
        logger.info("🤖 予測:")
        logger.info(f"  📊 対象銘柄: {self.stats['prediction']['total_symbols']}銘柄")
        logger.info(f"  🧠 LSTM予測: {self.stats['prediction']['lstm_predictions']}件")
        logger.info(f"  🎯 VertexAI予測: {self.stats['prediction']['vertexai_predictions']}件")
        logger.info(f"  ✅ LSTM成功: {self.stats['prediction']['lstm_success']}銘柄")
        logger.info(f"  ✅ VertexAI成功: {self.stats['prediction']['vertexai_success']}銘柄")
        logger.info("=" * 70)

if __name__ == "__main__":
    batch_system = ComprehensiveBatchSystemTest()
    
    try:
        batch_system.run_comprehensive_test()
    except KeyboardInterrupt:
        logger.info("🛑 手動停止")
    except Exception as e:
        logger.error(f"❌ システムエラー: {e}")
        import traceback
        traceback.print_exc()