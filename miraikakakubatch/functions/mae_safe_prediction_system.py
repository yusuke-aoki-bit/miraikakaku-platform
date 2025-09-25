#!/usr/bin/env python3
"""
MAE安全予測システム
コレーション問題を回避しながらMAE学習を実装
"""

import psycopg2
import psycopg2.extras
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional
import numpy as np

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MAESafePredictionSystem:
    def __init__(self):
        self.db_config = {
            "host": "34.173.9.214",
            "user": "postgres", 
            "password": "miraikakaku-postgres-secure-2024",
            "database": "miraikakaku",
        }
        
    def get_connection(self):
        return psycopg2.connect(**self.db_config)

    def get_symbols_with_sufficient_data(self) -> List[str]:
        """十分なデータがある銘柄を取得"""
        connection = self.get_connection()
        
        try:
            with connection.cursor() as cursor:
                cursor.execute("""
                    SELECT symbol, COUNT(*) as count
                    FROM stock_price_history
                    GROUP BY symbol
                    HAVING COUNT(*) >= 3
                    ORDER BY COUNT(*) DESC
                    LIMIT 10
                """)
                
                results = cursor.fetchall()
                symbols = [row[0] for row in results]
                
                logger.info(f"📊 十分なデータがある銘柄: {len(symbols)}銘柄")
                for symbol, count in results:
                    logger.info(f"  {symbol}: {count}件")
                
                return symbols
                
        finally:
            connection.close()

    def get_historical_predictions_safe(self, symbol: str) -> List[Dict]:
        """安全に予測データを取得（コレーション問題回避）"""
        connection = self.get_connection()
        
        try:
            with connection.cursor() as cursor:
                # 1. 予測データ取得
                cursor.execute("""
                    SELECT prediction_date, predicted_price, model_type, confidence_score
                    FROM stock_predictions
                    WHERE symbol = %s
                    ORDER BY prediction_date DESC
                """, (symbol,))
                
                predictions = cursor.fetchall()
                
                # 2. 実績データ取得
                cursor.execute("""
                    SELECT date, close_price
                    FROM stock_price_history
                    WHERE symbol = %s
                    ORDER BY date DESC
                """, (symbol,))
                
                actuals = cursor.fetchall()
                
                # 3. マッチング
                actual_dict = {row[0].strftime('%Y-%m-%d'): float(row[1]) for row in actuals}
                
                matched_predictions = []
                for pred_date, pred_price, model_type, confidence in predictions:
                    pred_date_str = pred_date.strftime('%Y-%m-%d')
                    if pred_date_str in actual_dict:
                        actual_price = actual_dict[pred_date_str]
                        mae = abs(pred_price - actual_price)
                        
                        matched_predictions.append({
                            'date': pred_date,
                            'predicted': float(pred_price),
                            'actual': actual_price,
                            'mae': mae,
                            'model_type': model_type,
                            'confidence': float(confidence)
                        })
                
                logger.info(f"📈 {symbol}: {len(matched_predictions)}件の予測-実績ペア発見")
                return matched_predictions
                
        finally:
            connection.close()

    def calculate_mae_learning_features(self, symbol: str, matched_predictions: List[Dict]) -> Dict:
        """MAE学習特徴量計算"""
        if not matched_predictions:
            return {
                'avg_mae': 0.0,
                'mae_trend': 0.0,
                'best_model': 'unknown',
                'confidence_correlation': 0.0,
                'prediction_consistency': 0.5,
                'data_sufficiency': 0.0
            }
        
        # MAE統計
        mae_values = [pred['mae'] for pred in matched_predictions]
        avg_mae = np.mean(mae_values)
        
        # MAEトレンド（最近の予測は改善しているか）
        if len(mae_values) >= 4:
            recent_mae = np.mean(mae_values[:len(mae_values)//2])
            older_mae = np.mean(mae_values[len(mae_values)//2:])
            mae_trend = (older_mae - recent_mae) / older_mae if older_mae > 0 else 0.0
        else:
            mae_trend = 0.0
        
        # モデル別性能
        model_performance = {}
        for pred in matched_predictions:
            model = pred['model_type']
            if model not in model_performance:
                model_performance[model] = []
            model_performance[model].append(pred['mae'])
        
        # 最良モデル特定
        if model_performance:
            best_model = min(model_performance.keys(), key=lambda k: np.mean(model_performance[k]))
        else:
            best_model = 'unknown'
        
        # 信頼度とMAEの相関
        confidences = [pred['confidence'] for pred in matched_predictions]
        if len(mae_values) > 2 and np.std(confidences) > 0 and np.std(mae_values) > 0:
            confidence_correlation = np.corrcoef(confidences, mae_values)[0, 1]
            if np.isnan(confidence_correlation):
                confidence_correlation = 0.0
        else:
            confidence_correlation = 0.0
        
        # 予測一貫性
        mae_std = np.std(mae_values)
        prediction_consistency = 1.0 / (1.0 + mae_std / avg_mae) if avg_mae > 0 else 0.5
        
        # データ充実度
        data_sufficiency = min(1.0, len(matched_predictions) / 10.0)  # 10件で最大
        
        return {
            'avg_mae': avg_mae,
            'mae_trend': mae_trend,
            'best_model': best_model,
            'confidence_correlation': confidence_correlation,
            'prediction_consistency': prediction_consistency,
            'data_sufficiency': data_sufficiency,
            'sample_count': len(matched_predictions)
        }

    def create_mae_informed_prediction(self, symbol: str) -> Dict:
        """MAE情報を活用した予測作成"""
        # 1. 現在価格取得
        current_price = self.get_latest_price(symbol)
        if not current_price:
            return None
        
        # 2. 過去予測データ取得
        matched_predictions = self.get_historical_predictions_safe(symbol)
        
        # 3. MAE学習特徴量計算
        mae_features = self.calculate_mae_learning_features(symbol, matched_predictions)
        
        # 4. 基本予測作成（トレンド分析）
        base_prediction = self.create_trend_based_prediction(symbol, current_price)
        
        # 5. MAE学習による調整
        mae_adjusted_prediction, mae_confidence = self.apply_mae_learning_adjustment(
            base_prediction, current_price, mae_features
        )
        
        return {
            'symbol': symbol,
            'current_price': current_price,
            'base_prediction': base_prediction,
            'mae_adjusted_prediction': mae_adjusted_prediction,
            'mae_confidence': mae_confidence,
            'predicted_change_percent': ((mae_adjusted_prediction - current_price) / current_price) * 100,
            'mae_features': mae_features,
            'model_type': 'mae_learning_v1',
            'prediction_timestamp': datetime.now()
        }

    def get_latest_price(self, symbol: str) -> Optional[float]:
        """最新価格取得"""
        connection = self.get_connection()
        
        try:
            with connection.cursor() as cursor:
                cursor.execute("""
                    SELECT close_price
                    FROM stock_price_history
                    WHERE symbol = %s
                    ORDER BY date DESC
                    LIMIT 1
                """, (symbol,))
                
                result = cursor.fetchone()
                return float(result[0]) if result else None
                
        finally:
            connection.close()

    def create_trend_based_prediction(self, symbol: str, current_price: float) -> float:
        """トレンドベース基本予測"""
        connection = self.get_connection()
        
        try:
            with connection.cursor() as cursor:
                cursor.execute("""
                    SELECT close_price, date
                    FROM stock_price_history
                    WHERE symbol = %s
                    ORDER BY date DESC
                    LIMIT 10
                """, (symbol,))
                
                price_history = cursor.fetchall()
                
                if len(price_history) < 3:
                    # データ不足の場合は現在価格±1%
                    return current_price * (1 + np.random.uniform(-0.01, 0.01))
                
                prices = [float(row[0]) for row in price_history]
                
                # 単純移動平均とトレンド
                short_ma = np.mean(prices[:3])  # 3日移動平均
                long_ma = np.mean(prices[:min(7, len(prices))])  # 7日移動平均
                
                # トレンド方向
                trend_signal = (short_ma - long_ma) / long_ma if long_ma > 0 else 0.0
                
                # 基本予測（トレンド継続を仮定）
                base_prediction = current_price * (1 + trend_signal * 0.5)  # トレンドの50%継続
                
                return base_prediction
                
        finally:
            connection.close()

    def apply_mae_learning_adjustment(self, base_prediction: float, current_price: float, mae_features: Dict) -> Tuple[float, float]:
        """MAE学習による予測調整"""
        
        # MAE信頼度ベースライン計算
        avg_mae = mae_features['avg_mae']
        if avg_mae > 0:
            # MAEが小さいほど高信頼度
            mae_confidence_base = 1.0 / (1.0 + avg_mae / current_price)
        else:
            mae_confidence_base = 0.6  # デフォルト値
        
        # トレンド調整（MAEが改善傾向なら信頼度向上）
        mae_trend = mae_features['mae_trend']
        trend_adjustment = mae_trend * 0.2  # トレンド改善で最大20%信頼度向上
        
        # 一貫性調整
        consistency_adjustment = mae_features['prediction_consistency'] * 0.1
        
        # データ充実度調整
        sufficiency_adjustment = mae_features['data_sufficiency'] * 0.1
        
        # 最終信頼度
        final_confidence = mae_confidence_base + trend_adjustment + consistency_adjustment + sufficiency_adjustment
        final_confidence = max(0.3, min(0.9, final_confidence))  # 0.3-0.9の範囲に制限
        
        # 予測値調整（MAEの不確実性を反映）
        if avg_mae > 0:
            # MAEベースの調整範囲
            adjustment_range = min(avg_mae * 0.3, current_price * 0.03)  # MAEの30%または価格の3%
            
            # 信頼度が高いほど調整幅を小さく
            adjustment_factor = 1.0 - final_confidence
            actual_adjustment_range = adjustment_range * adjustment_factor
            
            # ランダム調整適用
            random_adjustment = np.random.uniform(-actual_adjustment_range, actual_adjustment_range)
            adjusted_prediction = base_prediction + random_adjustment
        else:
            adjusted_prediction = base_prediction
        
        return adjusted_prediction, round(final_confidence, 3)

    def save_mae_learning_prediction(self, prediction_result: Dict):
        """MAE学習予測結果保存"""
        connection = self.get_connection()
        
        try:
            with connection.cursor() as cursor:
                cursor.execute("""
                    INSERT INTO stock_predictions 
                    (symbol, prediction_date, predicted_price, predicted_change_percent,
                     confidence_score, model_type, model_version, prediction_horizon,
                     created_at, is_active, notes)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, NOW(), 1, %s)
                """, (
                    prediction_result['symbol'],
                    prediction_result['prediction_timestamp'] + timedelta(days=1),
                    prediction_result['mae_adjusted_prediction'],
                    prediction_result['predicted_change_percent'],
                    prediction_result['mae_confidence'],
                    prediction_result['model_type'],
                    'v1.0_mae_learning',
                    1,
                    f"MAE learning applied. Avg MAE: {prediction_result['mae_features']['avg_mae']:.2f}, "
                    f"Samples: {prediction_result['mae_features']['sample_count']}, "
                    f"Best model: {prediction_result['mae_features']['best_model']}"
                ))
                
                connection.commit()
                
        finally:
            connection.close()

    def run_mae_learning_predictions(self):
        """MAE学習予測実行"""
        start_time = datetime.now()
        logger.info(f"🚀 MAE学習予測システム開始: {start_time.strftime('%Y-%m-%d %H:%M:%S')}")
        
        # 対象銘柄取得
        target_symbols = self.get_symbols_with_sufficient_data()
        
        if not target_symbols:
            logger.error("❌ 対象銘柄が見つかりません")
            return
        
        results = []
        success_count = 0
        
        # 上位5銘柄で実行
        for symbol in target_symbols[:5]:
            logger.info(f"\n📊 {symbol} のMAE学習予測実行")
            
            try:
                prediction_result = self.create_mae_informed_prediction(symbol)
                
                if prediction_result:
                    results.append(prediction_result)
                    success_count += 1
                    
                    # 結果表示
                    mae_features = prediction_result['mae_features']
                    logger.info(f"✅ {symbol}:")
                    logger.info(f"  現在価格: ¥{prediction_result['current_price']:.2f}")
                    logger.info(f"  基本予測: ¥{prediction_result['base_prediction']:.2f}")
                    logger.info(f"  MAE調整: ¥{prediction_result['mae_adjusted_prediction']:.2f} "
                              f"({prediction_result['predicted_change_percent']:+.2f}%)")
                    logger.info(f"  MAE信頼度: {prediction_result['mae_confidence']:.3f}")
                    logger.info(f"  過去MAE: {mae_features['avg_mae']:.2f} "
                              f"(サンプル: {mae_features['sample_count']}件)")
                    logger.info(f"  最良モデル: {mae_features['best_model']}")
                    
                    # データベース保存
                    self.save_mae_learning_prediction(prediction_result)
                else:
                    logger.warning(f"⚠️ {symbol}: 予測作成失敗")
                    
            except Exception as e:
                logger.error(f"❌ {symbol} エラー: {e}")
        
        # 最終レポート
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        
        logger.info("\n" + "=" * 80)
        logger.info("📊 MAE学習予測システム完了レポート")
        logger.info(f"⏱️  実行時間: {duration:.1f}秒")
        logger.info(f"🎯 対象銘柄: {len(target_symbols[:5])}銘柄")
        logger.info(f"✅ 成功: {success_count}銘柄")
        
        if results:
            logger.info("🧠 MAE学習効果サマリー:")
            for result in results:
                base_change = ((result['base_prediction'] - result['current_price']) / result['current_price']) * 100
                mae_change = result['predicted_change_percent']
                mae_impact = mae_change - base_change
                
                logger.info(f"  {result['symbol']}: "
                          f"基本{base_change:+.2f}% → MAE学習{mae_change:+.2f}% "
                          f"(調整: {mae_impact:+.2f}%) "
                          f"[信頼度: {result['mae_confidence']:.3f}]")
        
        logger.info("=" * 80)
        
        return results

if __name__ == "__main__":
    mae_system = MAESafePredictionSystem()
    
    try:
        results = mae_system.run_mae_learning_predictions()
        
    except KeyboardInterrupt:
        logger.info("🛑 手動停止")
    except Exception as e:
        logger.error(f"❌ システムエラー: {e}")
        import traceback
        traceback.print_exc()