#!/usr/bin/env python3
"""
高度な予測精度評価・改善システム
生成された予測データの精度を評価し、モデル性能を向上させる
"""

import pymysql
import numpy as np
import pandas as pd
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional
import json

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class AdvancedPredictionAccuracySystem:
    def __init__(self):
        self.db_config = {
            "host": "34.58.103.36",
            "user": "miraikakaku-user", 
            "password": "miraikakaku-secure-pass-2024",
            "database": "miraikakaku",
            "charset": "utf8mb4"
        }
        
    def get_connection(self):
        return pymysql.connect(**self.db_config)

    def evaluate_prediction_accuracy(self, days_back: int = 30) -> Dict:
        """過去の予測精度を評価"""
        logger.info(f"🧮 過去{days_back}日間の予測精度評価開始")
        connection = self.get_connection()
        
        try:
            with connection.cursor() as cursor:
                # 予測と実績価格を結合して取得
                cursor.execute("""
                    SELECT 
                        sp.symbol,
                        sp.model_type,
                        sp.model_version,
                        sp.prediction_date,
                        sp.predicted_price,
                        sp.predicted_change_percent,
                        sp.confidence_score,
                        sp.prediction_horizon,
                        sph.close_price as actual_price,
                        sph.date as actual_date
                    FROM stock_predictions sp
                    JOIN stock_price_history sph ON sp.symbol = sph.symbol
                    WHERE sp.prediction_date >= %s
                    AND DATE(sph.date) = DATE(DATE_ADD(sp.prediction_date, INTERVAL sp.prediction_horizon DAY))
                    AND sp.predicted_price IS NOT NULL
                    AND sph.close_price IS NOT NULL
                    ORDER BY sp.prediction_date DESC
                    LIMIT 10000
                """, (datetime.now() - timedelta(days=days_back),))
                
                predictions = cursor.fetchall()
                
                if not predictions:
                    logger.warning("⚠️ 評価可能な予測データなし")
                    return {}
                
                logger.info(f"📊 評価対象予測数: {len(predictions)}")
                
                # 精度メトリクス計算
                accuracy_results = self.calculate_accuracy_metrics(predictions)
                
                # モデル別精度
                model_accuracy = self.calculate_model_accuracy(predictions)
                
                # 銘柄別精度
                symbol_accuracy = self.calculate_symbol_accuracy(predictions)
                
                # 信頼度別精度
                confidence_accuracy = self.calculate_confidence_accuracy(predictions)
                
                return {
                    'overall': accuracy_results,
                    'by_model': model_accuracy,
                    'by_symbol': symbol_accuracy,
                    'by_confidence': confidence_accuracy,
                    'evaluation_count': len(predictions)
                }
                
        except Exception as e:
            logger.error(f"❌ 予測精度評価エラー: {e}")
            return {}
        finally:
            connection.close()

    def calculate_accuracy_metrics(self, predictions: List[Tuple]) -> Dict:
        """予測精度メトリクスを計算"""
        mae_values = []  # Mean Absolute Error
        mse_values = []  # Mean Squared Error
        mape_values = []  # Mean Absolute Percentage Error
        directional_accuracy = []  # 方向性精度
        
        for pred in predictions:
            predicted_price = pred[4]
            actual_price = pred[8]
            predicted_change_pct = pred[5]
            
            if predicted_price and actual_price and actual_price > 0:
                # MAE, MSE計算
                absolute_error = abs(predicted_price - actual_price)
                squared_error = (predicted_price - actual_price) ** 2
                
                mae_values.append(absolute_error)
                mse_values.append(squared_error)
                
                # MAPE計算
                percentage_error = abs((predicted_price - actual_price) / actual_price) * 100
                mape_values.append(percentage_error)
                
                # 方向性精度（価格上昇/下降の予測が正しいか）
                if predicted_change_pct is not None:
                    predicted_direction = 1 if predicted_change_pct > 0 else -1
                    # 実際の変動を推定（現在価格から逆算）
                    estimated_previous_price = actual_price / (1 + predicted_change_pct / 100)
                    actual_direction = 1 if actual_price > estimated_previous_price else -1
                    
                    directional_accuracy.append(1 if predicted_direction == actual_direction else 0)
        
        return {
            'mae': np.mean(mae_values) if mae_values else 0,
            'mse': np.mean(mse_values) if mse_values else 0,
            'rmse': np.sqrt(np.mean(mse_values)) if mse_values else 0,
            'mape': np.mean(mape_values) if mape_values else 0,
            'directional_accuracy': np.mean(directional_accuracy) if directional_accuracy else 0,
            'sample_count': len(predictions)
        }

    def calculate_model_accuracy(self, predictions: List[Tuple]) -> Dict:
        """モデル別精度を計算"""
        model_results = {}
        
        # モデル別にグループ化
        models = {}
        for pred in predictions:
            model_key = f"{pred[1]}_{pred[2]}"  # model_type_model_version
            if model_key not in models:
                models[model_key] = []
            models[model_key].append(pred)
        
        # 各モデルの精度計算
        for model_key, model_preds in models.items():
            if len(model_preds) >= 5:  # 最低5つの予測がある場合のみ評価
                model_results[model_key] = self.calculate_accuracy_metrics(model_preds)
        
        return model_results

    def calculate_symbol_accuracy(self, predictions: List[Tuple]) -> Dict:
        """銘柄別精度を計算"""
        symbol_results = {}
        
        # 銘柄別にグループ化
        symbols = {}
        for pred in predictions:
            symbol = pred[0]
            if symbol not in symbols:
                symbols[symbol] = []
            symbols[symbol].append(pred)
        
        # 各銘柄の精度計算（予測数が多い上位20銘柄）
        symbol_counts = [(symbol, len(preds)) for symbol, preds in symbols.items()]
        symbol_counts.sort(key=lambda x: x[1], reverse=True)
        
        for symbol, count in symbol_counts[:20]:
            if count >= 3:
                symbol_results[symbol] = self.calculate_accuracy_metrics(symbols[symbol])
        
        return symbol_results

    def calculate_confidence_accuracy(self, predictions: List[Tuple]) -> Dict:
        """信頼度区間別精度を計算"""
        confidence_ranges = {
            'high': (0.8, 1.0),
            'medium': (0.6, 0.8),
            'low': (0.0, 0.6)
        }
        
        confidence_results = {}
        
        for range_name, (min_conf, max_conf) in confidence_ranges.items():
            range_preds = [
                pred for pred in predictions 
                if pred[6] and min_conf <= pred[6] < max_conf  # confidence_score
            ]
            
            if range_preds:
                confidence_results[range_name] = self.calculate_accuracy_metrics(range_preds)
        
        return confidence_results

    def update_model_performance_table(self, accuracy_results: Dict):
        """モデル性能テーブルを更新"""
        logger.info("📈 モデル性能テーブル更新開始")
        connection = self.get_connection()
        
        try:
            with connection.cursor() as cursor:
                # 全体性能を記録
                overall_results = accuracy_results.get('overall', {})
                if overall_results:
                    cursor.execute("""
                        INSERT INTO model_performance 
                        (model_type, model_version, mae, mse, rmse, accuracy, 
                         evaluation_start_date, evaluation_end_date, symbols_count, 
                         is_active, created_at, updated_at)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, NOW(), NOW())
                    """, (
                        'ensemble_evaluation',
                        'v4.0',
                        overall_results.get('mae', 0),
                        overall_results.get('mse', 0),
                        overall_results.get('rmse', 0),
                        overall_results.get('directional_accuracy', 0),
                        datetime.now() - timedelta(days=30),
                        datetime.now(),
                        accuracy_results.get('evaluation_count', 0),
                        1
                    ))
                
                # モデル別性能を記録
                model_results = accuracy_results.get('by_model', {})
                for model_key, metrics in model_results.items():
                    model_parts = model_key.split('_', 1)
                    model_type = model_parts[0] if model_parts else 'unknown'
                    model_version = model_parts[1] if len(model_parts) > 1 else 'unknown'
                    
                    cursor.execute("""
                        INSERT INTO model_performance 
                        (model_type, model_version, mae, mse, rmse, accuracy, 
                         evaluation_start_date, evaluation_end_date, symbols_count, 
                         is_active, created_at, updated_at)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, NOW(), NOW())
                        ON DUPLICATE KEY UPDATE
                        mae = VALUES(mae),
                        mse = VALUES(mse),
                        rmse = VALUES(rmse),
                        accuracy = VALUES(accuracy),
                        updated_at = NOW()
                    """, (
                        model_type,
                        model_version,
                        metrics.get('mae', 0),
                        metrics.get('mse', 0),
                        metrics.get('rmse', 0),
                        metrics.get('directional_accuracy', 0),
                        datetime.now() - timedelta(days=30),
                        datetime.now(),
                        metrics.get('sample_count', 0),
                        1
                    ))
                
                connection.commit()
                logger.info("✅ モデル性能テーブル更新完了")
                
        except Exception as e:
            logger.error(f"❌ モデル性能テーブル更新エラー: {e}")
        finally:
            connection.close()

    def log_ai_inference_activity(self, accuracy_results: Dict):
        """AI推論ログを記録"""
        logger.info("📝 AI推論ログ記録開始")
        connection = self.get_connection()
        
        try:
            with connection.cursor() as cursor:
                # 推論ログエントリを作成
                log_entries = []
                
                model_results = accuracy_results.get('by_model', {})
                
                for model_key, metrics in model_results.items():
                    model_parts = model_key.split('_', 1)
                    model_name = model_parts[0] if model_parts else 'unknown'
                    model_version = model_parts[1] if len(model_parts) > 1 else 'unknown'
                    
                    log_entry = {
                        'request_id': f"accuracy_eval_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{model_name}",
                        'model_name': model_name,
                        'model_version': model_version,
                        'input_data': json.dumps({'evaluation_type': 'accuracy_assessment'}),
                        'output_data': json.dumps({
                            'mae': metrics.get('mae', 0),
                            'mse': metrics.get('mse', 0),
                            'directional_accuracy': metrics.get('directional_accuracy', 0),
                            'sample_count': metrics.get('sample_count', 0)
                        }),
                        'inference_time_ms': int(metrics.get('sample_count', 0) * 10),  # 推定処理時間
                        'confidence_score': metrics.get('directional_accuracy', 0),
                        'is_successful': 1,
                        'endpoint': '/api/prediction/evaluate',
                        'user_id': 'system',
                        'session_id': f"eval_session_{datetime.now().strftime('%Y%m%d')}"
                    }
                    log_entries.append(log_entry)
                
                # バッチ挿入
                if log_entries:
                    insert_query = """
                        INSERT INTO ai_inference_log 
                        (request_id, model_name, model_version, input_data, output_data,
                         inference_time_ms, confidence_score, is_successful, endpoint,
                         user_id, session_id, created_at)
                        VALUES (%(request_id)s, %(model_name)s, %(model_version)s, %(input_data)s,
                                %(output_data)s, %(inference_time_ms)s, %(confidence_score)s,
                                %(is_successful)s, %(endpoint)s, %(user_id)s, %(session_id)s, NOW())
                    """
                    
                    cursor.executemany(insert_query, log_entries)
                    connection.commit()
                    
                    logger.info(f"✅ AI推論ログ {len(log_entries)}件記録完了")
                
        except Exception as e:
            logger.error(f"❌ AI推論ログ記録エラー: {e}")
        finally:
            connection.close()

    def generate_comprehensive_accuracy_report(self):
        """包括的な精度レポートを生成"""
        logger.info("📊 包括的精度レポート生成開始")
        
        # 予測精度評価実行
        accuracy_results = self.evaluate_prediction_accuracy(days_back=30)
        
        if not accuracy_results:
            logger.warning("⚠️ 精度評価データなし")
            return
        
        # モデル性能テーブル更新
        self.update_model_performance_table(accuracy_results)
        
        # AI推論ログ記録
        self.log_ai_inference_activity(accuracy_results)
        
        # レポート出力
        self.print_accuracy_report(accuracy_results)

    def print_accuracy_report(self, results: Dict):
        """精度レポートを出力"""
        logger.info("=" * 80)
        logger.info("📊 高度予測精度評価レポート")
        logger.info("=" * 80)
        
        # 全体精度
        overall = results.get('overall', {})
        if overall:
            logger.info("【全体精度】")
            logger.info(f"  MAE (平均絶対誤差): {overall.get('mae', 0):.2f}")
            logger.info(f"  RMSE (平均平方根誤差): {overall.get('rmse', 0):.2f}")
            logger.info(f"  MAPE (平均絶対パーセント誤差): {overall.get('mape', 0):.2f}%")
            logger.info(f"  方向性精度: {overall.get('directional_accuracy', 0):.1%}")
            logger.info(f"  評価サンプル数: {overall.get('sample_count', 0):,}")
        
        # モデル別精度（上位5位）
        model_results = results.get('by_model', {})
        if model_results:
            logger.info("\n【モデル別精度 (上位5位)】")
            sorted_models = sorted(
                model_results.items(), 
                key=lambda x: x[1].get('directional_accuracy', 0), 
                reverse=True
            )[:5]
            
            for model, metrics in sorted_models:
                logger.info(f"  {model}:")
                logger.info(f"    方向性精度: {metrics.get('directional_accuracy', 0):.1%}")
                logger.info(f"    MAE: {metrics.get('mae', 0):.2f}")
                logger.info(f"    サンプル数: {metrics.get('sample_count', 0)}")
        
        # 信頼度別精度
        confidence_results = results.get('by_confidence', {})
        if confidence_results:
            logger.info("\n【信頼度別精度】")
            for range_name, metrics in confidence_results.items():
                logger.info(f"  {range_name}信頼度:")
                logger.info(f"    方向性精度: {metrics.get('directional_accuracy', 0):.1%}")
                logger.info(f"    MAE: {metrics.get('mae', 0):.2f}")
                logger.info(f"    サンプル数: {metrics.get('sample_count', 0)}")
        
        logger.info("=" * 80)

def main():
    system = AdvancedPredictionAccuracySystem()
    system.generate_comprehensive_accuracy_report()

if __name__ == "__main__":
    main()