#!/usr/bin/env python3
"""
予測精度評価システム - コレーション安全版
平均絶対誤差(MAE)を使用してLSTM vs VertexAI予測精度を比較
"""

import pymysql
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Tuple
import pandas as pd
import numpy as np

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class PredictionAccuracyEvaluatorSafe:
    def __init__(self):
        self.db_config = {
            "host": "34.58.103.36",
            "user": "miraikakaku-user", 
            "password": "miraikakaku-secure-pass-2024",
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
        return pymysql.connect(**self.db_config)

    def get_predictions_and_actual_data_separately(self):
        """
        予測データと実際データを別々に取得してコレーション問題を回避
        """
        connection = self.get_connection()
        
        try:
            with connection.cursor() as cursor:
                # 1. 予測データを取得
                cursor.execute("""
                    SELECT 
                        symbol, prediction_date, predicted_price, predicted_change_percent,
                        confidence_score, model_type, created_at
                    FROM stock_predictions
                    WHERE model_type IN ('lstm_test_accuracy', 'vertexai_test_accuracy', 'lstm_test_v2', 'vertexai_test_v2', 'lstm_v2', 'vertexai_v2')
                    AND prediction_date >= DATE_SUB(NOW(), INTERVAL 30 DAY)
                    ORDER BY symbol, prediction_date, model_type
                """)
                
                predictions = cursor.fetchall()
                logger.info(f"📊 取得した予測データ: {len(predictions)}件")
                
                # 2. 実際の価格データを取得
                cursor.execute("""
                    SELECT symbol, date, close_price
                    FROM stock_price_history
                    WHERE date >= DATE_SUB(NOW(), INTERVAL 30 DAY)
                    ORDER BY symbol, date
                """)
                
                actual_prices = cursor.fetchall()
                logger.info(f"📈 取得した実績データ: {len(actual_prices)}件")
                
                return predictions, actual_prices
                
        finally:
            connection.close()

    def match_predictions_with_actuals(self, predictions, actual_prices):
        """
        予測データと実績データをマッチング
        """
        # 実績データを辞書化（高速検索用）
        actual_dict = {}
        for symbol, date, close_price in actual_prices:
            key = f"{symbol}_{date.strftime('%Y-%m-%d')}"
            actual_dict[key] = close_price
        
        # 予測データと実績データをマッチング
        matched_data = []
        matched_count = 0
        
        for pred in predictions:
            symbol, pred_date, pred_price, pred_change, confidence, model_type, created_at = pred
            pred_date_str = pred_date.strftime('%Y-%m-%d')
            key = f"{symbol}_{pred_date_str}"
            
            if key in actual_dict:
                actual_price = actual_dict[key]
                matched_data.append({
                    'symbol': symbol,
                    'prediction_date': pred_date,
                    'predicted_price': pred_price,
                    'actual_price': actual_price,
                    'confidence': confidence,
                    'model_type': model_type,
                    'created_at': created_at
                })
                matched_count += 1
        
        logger.info(f"🔗 マッチング成功: {matched_count}件の予測-実績ペア")
        return matched_data

    def calculate_mae_by_model_and_symbol(self, matched_data):
        """
        モデル・銘柄別のMAE計算
        """
        # データをモデル・銘柄別にグループ化
        groups = {}
        
        for data in matched_data:
            symbol = data['symbol']
            model_type = data['model_type']
            key = f"{model_type}_{symbol}"
            
            if key not in groups:
                groups[key] = []
            
            groups[key].append(data)
        
        # 各グループのMAE計算
        results = {}
        
        for key, group_data in groups.items():
            model_type, symbol = key.split('_', 1)
            
            # MAE計算
            absolute_errors = []
            confidences = []
            error_details = []
            
            for data in group_data:
                predicted = data['predicted_price']
                actual = data['actual_price']
                absolute_error = abs(predicted - actual)
                relative_error = (absolute_error / actual) * 100 if actual != 0 else 0
                
                absolute_errors.append(absolute_error)
                confidences.append(data['confidence'])
                error_details.append({
                    'date': data['prediction_date'],
                    'predicted': predicted,
                    'actual': actual,
                    'absolute_error': absolute_error,
                    'relative_error_percent': relative_error
                })
            
            mae = np.mean(absolute_errors)
            
            results[key] = {
                'symbol': symbol,
                'model_type': model_type,
                'mae': mae,
                'count': len(absolute_errors),
                'avg_confidence': np.mean(confidences),
                'median_error': np.median(absolute_errors),
                'std_error': np.std(absolute_errors),
                'min_error': np.min(absolute_errors),
                'max_error': np.max(absolute_errors),
                'error_details': error_details
            }
            
            logger.info(f"📊 {model_type} {symbol}: MAE={mae:.2f} ({len(absolute_errors)}件)")
        
        return results

    def aggregate_results_by_model(self, detailed_results):
        """
        モデル別の全体結果集計
        """
        for key, result in detailed_results.items():
            model_type = result['model_type']
            symbol = result['symbol']
            
            if 'lstm' in model_type.lower():
                model_key = 'lstm'
            elif 'vertexai' in model_type.lower():
                model_key = 'vertexai'
            else:
                continue
            
            # 銘柄別結果保存
            self.accuracy_results[model_key]['symbol_results'][symbol] = result
            self.accuracy_results[model_key]['symbols_evaluated'] += 1
        
        # 全体MAE計算
        for model_key in ['lstm', 'vertexai']:
            all_errors = []
            total_predictions = 0
            
            for symbol, symbol_result in self.accuracy_results[model_key]['symbol_results'].items():
                for detail in symbol_result['error_details']:
                    all_errors.append(detail['absolute_error'])
                total_predictions += symbol_result['count']
            
            if all_errors:
                self.accuracy_results[model_key]['mae'] = np.mean(all_errors)
                self.accuracy_results[model_key]['total_predictions'] = total_predictions
            
            logger.info(f"🎯 {model_key.upper()} 全体MAE: {self.accuracy_results[model_key]['mae']:.2f} ({total_predictions}件)")

    def generate_comprehensive_accuracy_report(self):
        """
        包括的精度評価レポート生成
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
        
        logger.info(f"  🤖 VertexAI:")
        logger.info(f"    MAE: {vertexai_mae:.2f}")
        logger.info(f"    予測件数: {vertexai_count:,}件")
        logger.info(f"    評価銘柄数: {self.accuracy_results['vertexai']['symbols_evaluated']}銘柄")
        
        # 勝者判定
        if lstm_mae > 0 and vertexai_mae > 0:
            if lstm_mae < vertexai_mae:
                improvement = ((vertexai_mae - lstm_mae) / vertexai_mae) * 100
                logger.info(f"🏆 総合勝者: LSTM (精度向上: {improvement:.1f}%)")
            elif vertexai_mae < lstm_mae:
                improvement = ((lstm_mae - vertexai_mae) / lstm_mae) * 100
                logger.info(f"🏆 総合勝者: VertexAI (精度向上: {improvement:.1f}%)")
            else:
                logger.info("🤝 総合結果: 同点")
        
        logger.info("")
        
        # 銘柄別詳細比較
        logger.info("📈 銘柄別精度詳細比較:")
        all_symbols = set(self.accuracy_results['lstm']['symbol_results'].keys()) | \
                     set(self.accuracy_results['vertexai']['symbol_results'].keys())
        
        lstm_wins = 0
        vertexai_wins = 0
        ties = 0
        
        for symbol in sorted(all_symbols):
            lstm_result = self.accuracy_results['lstm']['symbol_results'].get(symbol)
            vertexai_result = self.accuracy_results['vertexai']['symbol_results'].get(symbol)
            
            logger.info(f"  📊 {symbol}:")
            if lstm_result:
                logger.info(f"    🧠 LSTM: MAE={lstm_result['mae']:.2f} (信頼度:{lstm_result['avg_confidence']:.2f}, {lstm_result['count']}件)")
            if vertexai_result:
                logger.info(f"    🤖 VertexAI: MAE={vertexai_result['mae']:.2f} (信頼度:{vertexai_result['avg_confidence']:.2f}, {vertexai_result['count']}件)")
            
            # 銘柄別勝者判定
            if lstm_result and vertexai_result:
                if lstm_result['mae'] < vertexai_result['mae']:
                    logger.info(f"    🏆 {symbol} 勝者: LSTM")
                    lstm_wins += 1
                elif vertexai_result['mae'] < lstm_result['mae']:
                    logger.info(f"    🏆 {symbol} 勝者: VertexAI")
                    vertexai_wins += 1
                else:
                    logger.info(f"    🤝 {symbol}: 同点")
                    ties += 1
        
        # 銘柄別勝敗サマリー
        total_comparisons = lstm_wins + vertexai_wins + ties
        if total_comparisons > 0:
            logger.info("")
            logger.info("🏁 銘柄別勝敗サマリー:")
            logger.info(f"  🧠 LSTM勝利: {lstm_wins}銘柄 ({lstm_wins/total_comparisons*100:.1f}%)")
            logger.info(f"  🤖 VertexAI勝利: {vertexai_wins}銘柄 ({vertexai_wins/total_comparisons*100:.1f}%)")
            logger.info(f"  🤝 同点: {ties}銘柄 ({ties/total_comparisons*100:.1f}%)")
        
        logger.info("=" * 80)

    def save_accuracy_results_safe(self):
        """
        精度評価結果をデータベースに安全に保存
        """
        connection = self.get_connection()
        
        try:
            with connection.cursor() as cursor:
                # テーブル作成
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
                        min_error FLOAT,
                        max_error FLOAT,
                        evaluation_date DATETIME,
                        created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                
                saved_count = 0
                
                # 結果保存
                for model_key in ['lstm', 'vertexai']:
                    for symbol, result in self.accuracy_results[model_key]['symbol_results'].items():
                        cursor.execute("""
                            INSERT INTO model_accuracy_evaluation 
                            (model_type, symbol, mae, prediction_count, avg_confidence, 
                             median_error, std_error, min_error, max_error, evaluation_date)
                            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, NOW())
                        """, (
                            model_key.upper(), symbol, result['mae'], result['count'], 
                            result['avg_confidence'], result['median_error'], result['std_error'],
                            result['min_error'], result['max_error']
                        ))
                        saved_count += 1
                
                connection.commit()
                logger.info(f"✅ 精度評価結果をデータベースに保存完了 ({saved_count}件)")
                
        finally:
            connection.close()

    def run_safe_accuracy_evaluation(self):
        """
        安全な精度評価実行
        """
        start_time = datetime.now()
        logger.info(f"🚀 予測精度評価開始 (安全版): {start_time.strftime('%Y-%m-%d %H:%M:%S')}")
        
        try:
            # 1. データ取得
            predictions, actual_prices = self.get_predictions_and_actual_data_separately()
            
            if not predictions:
                logger.warning("❌ 予測データが見つかりません")
                return
            
            if not actual_prices:
                logger.warning("❌ 実績データが見つかりません")
                return
            
            # 2. データマッチング
            matched_data = self.match_predictions_with_actuals(predictions, actual_prices)
            
            if not matched_data:
                logger.warning("❌ 予測と実績のマッチングデータがありません")
                return
            
            # 3. MAE計算
            detailed_results = self.calculate_mae_by_model_and_symbol(matched_data)
            
            # 4. 結果集計
            self.aggregate_results_by_model(detailed_results)
            
            # 5. 結果保存
            self.save_accuracy_results_safe()
            
            # 6. レポート生成
            self.generate_comprehensive_accuracy_report()
            
        except Exception as e:
            logger.error(f"❌ 精度評価エラー: {e}")
            import traceback
            traceback.print_exc()
        
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        logger.info(f"✅ 精度評価完了 (実行時間: {duration:.1f}秒)")

if __name__ == "__main__":
    evaluator = PredictionAccuracyEvaluatorSafe()
    
    try:
        evaluator.run_safe_accuracy_evaluation()
        
    except KeyboardInterrupt:
        logger.info("🛑 手動停止")
    except Exception as e:
        logger.error(f"❌ システムエラー: {e}")
        import traceback
        traceback.print_exc()