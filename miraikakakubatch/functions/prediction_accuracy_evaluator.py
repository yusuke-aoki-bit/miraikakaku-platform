#!/usr/bin/env python3
"""
予測精度評価システム
平均絶対誤差(MAE)を使用してLSTM vs VertexAI予測精度を比較
"""

import psycopg2
import psycopg2.extras
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Tuple
import pandas as pd
import numpy as np

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class PredictionAccuracyEvaluator:
    def __init__(self):
        self.db_config = {
            "host": "34.173.9.214",
            "user": "postgres", 
            "password": "miraikakaku-postgres-secure-2024",
            "database": "miraikakaku",
        }
        self.accuracy_results = {
            "lstm": {
                "total_predictions": 0,
                "mae": 0.0,
                "symbols_evaluated": 0,
                "symbol_results": {}
            },
            "vertexai": {
                "total_predictions": 0,
                "mae": 0.0,
                "symbols_evaluated": 0,
                "symbol_results": {}
            }
        }

    def get_connection(self):
        return psycopg2.connect(**self.db_config)

    def get_past_predictions_with_actual_data(self, days_back=30):
        """
        過去の予測データと実際の価格データを取得
        """
        connection = self.get_connection()
        
        try:
            with connection.cursor() as cursor:
                # 過去の予測データで実際の価格データが存在するものを取得
                cursor.execute("""
                    SELECT 
                        sp.symbol,
                        sp.prediction_date,
                        sp.predicted_price,
                        sp.predicted_change_percent,
                        sp.confidence_score,
                        sp.model_type,
                        sp.created_at,
                        sph.close_price as actual_price,
                        sph.date as actual_date
                    FROM stock_predictions sp
                    JOIN stock_price_history sph ON (
                        sp.symbol = sph.symbol 
                        AND DATE(sp.prediction_date) = DATE(sph.date)
                    )
                    WHERE sp.prediction_date < NOW()
                    AND sp.prediction_date >= DATE_SUB(NOW(), INTERVAL %s DAY)
                    AND sp.model_type IN ('lstm_test_v2', 'vertexai_test_v2', 'lstm_v2', 'vertexai_v2')
                    ORDER BY sp.symbol, sp.prediction_date, sp.model_type
                """, (days_back,))
                
                results = cursor.fetchall()
                logger.info(f"📊 評価対象データ: {len(results)}件の予測-実績ペア")
                
                return results
                
        finally:
            connection.close()

    def calculate_mae_for_symbol(self, predictions: List[Tuple]) -> Dict:
        """
        単一銘柄のMAE計算
        """
        lstm_predictions = []
        vertexai_predictions = []
        
        for pred in predictions:
            symbol, pred_date, pred_price, pred_change, confidence, model_type, created_at, actual_price, actual_date = pred
            
            if model_type in ['lstm_test_v2', 'lstm_v2']:
                lstm_predictions.append({
                    'predicted': pred_price,
                    'actual': actual_price,
                    'date': pred_date,
                    'confidence': confidence
                })
            elif model_type in ['vertexai_test_v2', 'vertexai_v2']:
                vertexai_predictions.append({
                    'predicted': pred_price,
                    'actual': actual_price,
                    'date': pred_date,
                    'confidence': confidence
                })
        
        result = {
            'symbol': predictions[0][0] if predictions else None,
            'lstm': self._calculate_mae(lstm_predictions),
            'vertexai': self._calculate_mae(vertexai_predictions)
        }
        
        return result

    def _calculate_mae(self, predictions: List[Dict]) -> Dict:
        """
        MAE（平均絶対誤差）計算
        MAE = Σ|predicted - actual| / n
        """
        if not predictions:
            return {
                'mae': float('inf'),
                'count': 0,
                'avg_confidence': 0.0,
                'error_details': []
            }
        
        absolute_errors = []
        confidences = []
        error_details = []
        
        for pred in predictions:
            predicted = pred['predicted']
            actual = pred['actual']
            absolute_error = abs(predicted - actual)
            
            absolute_errors.append(absolute_error)
            confidences.append(pred['confidence'])
            error_details.append({
                'date': pred['date'],
                'predicted': predicted,
                'actual': actual,
                'absolute_error': absolute_error,
                'relative_error_percent': (absolute_error / actual) * 100 if actual != 0 else 0
            })
        
        mae = np.mean(absolute_errors)
        avg_confidence = np.mean(confidences)
        
        return {
            'mae': mae,
            'count': len(predictions),
            'avg_confidence': avg_confidence,
            'error_details': error_details,
            'median_error': np.median(absolute_errors),
            'std_error': np.std(absolute_errors)
        }

    def evaluate_all_predictions(self, days_back=30):
        """
        全予測データの精度評価
        """
        logger.info(f"🔍 過去{days_back}日間の予測精度評価開始")
        
        # 予測-実績データ取得
        prediction_data = self.get_past_predictions_with_actual_data(days_back)
        
        if not prediction_data:
            logger.warning("❌ 評価可能な予測データが見つかりません")
            return
        
        # 銘柄別にグループ化
        symbol_groups = {}
        for pred in prediction_data:
            symbol = pred[0]
            if symbol not in symbol_groups:
                symbol_groups[symbol] = []
            symbol_groups[symbol].append(pred)
        
        # 銘柄別精度評価
        all_lstm_errors = []
        all_vertexai_errors = []
        
        logger.info(f"📈 {len(symbol_groups)}銘柄の精度評価実施")
        
        for symbol, predictions in symbol_groups.items():
            symbol_result = self.calculate_mae_for_symbol(predictions)
            
            # 結果を蓄積
            if symbol_result['lstm']['count'] > 0:
                lstm_mae = symbol_result['lstm']['mae']
                all_lstm_errors.extend([detail['absolute_error'] for detail in symbol_result['lstm']['error_details']])
                self.accuracy_results['lstm']['symbol_results'][symbol] = symbol_result['lstm']
                self.accuracy_results['lstm']['symbols_evaluated'] += 1
                logger.info(f"  🧠 LSTM {symbol}: MAE={lstm_mae:.2f} ({symbol_result['lstm']['count']}件)")
            
            if symbol_result['vertexai']['count'] > 0:
                vertexai_mae = symbol_result['vertexai']['mae']
                all_vertexai_errors.extend([detail['absolute_error'] for detail in symbol_result['vertexai']['error_details']])
                self.accuracy_results['vertexai']['symbol_results'][symbol] = symbol_result['vertexai']
                self.accuracy_results['vertexai']['symbols_evaluated'] += 1
                logger.info(f"  🎯 VertexAI {symbol}: MAE={vertexai_mae:.2f} ({symbol_result['vertexai']['count']}件)")
        
        # 全体MAE計算
        if all_lstm_errors:
            self.accuracy_results['lstm']['mae'] = np.mean(all_lstm_errors)
            self.accuracy_results['lstm']['total_predictions'] = len(all_lstm_errors)
        
        if all_vertexai_errors:
            self.accuracy_results['vertexai']['mae'] = np.mean(all_vertexai_errors)
            self.accuracy_results['vertexai']['total_predictions'] = len(all_vertexai_errors)

    def save_accuracy_results(self):
        """
        精度評価結果をデータベースに保存
        """
        connection = self.get_connection()
        
        try:
            with connection.cursor() as cursor:
                # 精度評価テーブルが存在しない場合は作成
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS model_accuracy_evaluation (
                        id INT AUTO_INCREMENT PRIMARY KEY,
                        model_type VARCHAR(50),
                        symbol VARCHAR(20),
                        mae FLOAT,
                        prediction_count INT,
                        avg_confidence FLOAT,
                        median_error FLOAT,
                        std_error FLOAT,
                        evaluation_date DATETIME,
                        created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                
                # LSTM結果保存
                for symbol, result in self.accuracy_results['lstm']['symbol_results'].items():
                    cursor.execute("""
                        INSERT INTO model_accuracy_evaluation 
                        (model_type, symbol, mae, prediction_count, avg_confidence, 
                         median_error, std_error, evaluation_date)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, NOW())
                    """, (
                        'LSTM', symbol, result['mae'], result['count'], 
                        result['avg_confidence'], result['median_error'], result['std_error']
                    ))
                
                # VertexAI結果保存
                for symbol, result in self.accuracy_results['vertexai']['symbol_results'].items():
                    cursor.execute("""
                        INSERT INTO model_accuracy_evaluation 
                        (model_type, symbol, mae, prediction_count, avg_confidence, 
                         median_error, std_error, evaluation_date)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, NOW())
                    """, (
                        'VertexAI', symbol, result['mae'], result['count'], 
                        result['avg_confidence'], result['median_error'], result['std_error']
                    ))
                
                connection.commit()
                logger.info("✅ 精度評価結果をデータベースに保存完了")
                
        finally:
            connection.close()

    def generate_accuracy_report(self):
        """
        精度評価レポート生成
        """
        logger.info("=" * 80)
        logger.info("📊 予測精度評価レポート（平均絶対誤差 MAE）")
        logger.info("=" * 80)
        
        # 全体比較
        lstm_mae = self.accuracy_results['lstm']['mae']
        vertexai_mae = self.accuracy_results['vertexai']['mae']
        lstm_count = self.accuracy_results['lstm']['total_predictions']
        vertexai_count = self.accuracy_results['vertexai']['total_predictions']
        
        logger.info("🎯 全体精度比較:")
        logger.info(f"  🧠 LSTM:")
        logger.info(f"    MAE: {lstm_mae:.2f}")
        logger.info(f"    予測件数: {lstm_count:,}件")
        logger.info(f"    評価銘柄数: {self.accuracy_results['lstm']['symbols_evaluated']}銘柄")
        
        logger.info(f"  🎯 VertexAI:")
        logger.info(f"    MAE: {vertexai_mae:.2f}")
        logger.info(f"    予測件数: {vertexai_count:,}件")
        logger.info(f"    評価銘柄数: {self.accuracy_results['vertexai']['symbols_evaluated']}銘柄")
        
        # 勝者判定
        if lstm_mae < vertexai_mae:
            logger.info(f"🏆 勝者: LSTM (MAE差: {vertexai_mae - lstm_mae:.2f})")
        elif vertexai_mae < lstm_mae:
            logger.info(f"🏆 勝者: VertexAI (MAE差: {lstm_mae - vertexai_mae:.2f})")
        else:
            logger.info("🤝 同点")
        
        logger.info("")
        
        # 銘柄別詳細
        logger.info("📈 銘柄別精度詳細:")
        all_symbols = set(self.accuracy_results['lstm']['symbol_results'].keys()) | \
                     set(self.accuracy_results['vertexai']['symbol_results'].keys())
        
        for symbol in sorted(all_symbols):
            lstm_result = self.accuracy_results['lstm']['symbol_results'].get(symbol)
            vertexai_result = self.accuracy_results['vertexai']['symbol_results'].get(symbol)
            
            logger.info(f"  {symbol}:")
            if lstm_result:
                logger.info(f"    🧠 LSTM: MAE={lstm_result['mae']:.2f} ({lstm_result['count']}件)")
            if vertexai_result:
                logger.info(f"    🎯 VertexAI: MAE={vertexai_result['mae']:.2f} ({vertexai_result['count']}件)")
            
            # 銘柄別勝者
            if lstm_result and vertexai_result:
                if lstm_result['mae'] < vertexai_result['mae']:
                    logger.info(f"    🏆 {symbol}勝者: LSTM")
                elif vertexai_result['mae'] < lstm_result['mae']:
                    logger.info(f"    🏆 {symbol}勝者: VertexAI")
                else:
                    logger.info(f"    🤝 {symbol}: 同点")
        
        logger.info("=" * 80)

    def run_accuracy_evaluation(self, days_back=30):
        """
        精度評価実行
        """
        start_time = datetime.now()
        logger.info(f"🚀 予測精度評価開始: {start_time.strftime('%Y-%m-%d %H:%M:%S')}")
        
        try:
            # 精度評価実行
            self.evaluate_all_predictions(days_back)
            
            # 結果保存
            self.save_accuracy_results()
            
            # レポート生成
            self.generate_accuracy_report()
            
        except Exception as e:
            logger.error(f"❌ 精度評価エラー: {e}")
            import traceback
            traceback.print_exc()
        
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        logger.info(f"✅ 精度評価完了 (実行時間: {duration:.1f}秒)")

if __name__ == "__main__":
    evaluator = PredictionAccuracyEvaluator()
    
    try:
        # 過去30日間の予測精度を評価
        evaluator.run_accuracy_evaluation(days_back=30)
        
    except KeyboardInterrupt:
        logger.info("🛑 手動停止")
    except Exception as e:
        logger.error(f"❌ システムエラー: {e}")
        import traceback
        traceback.print_exc()