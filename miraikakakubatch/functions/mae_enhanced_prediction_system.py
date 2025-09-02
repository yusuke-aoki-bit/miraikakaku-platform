#!/usr/bin/env python3
"""
MAE強化予測システム
過去データからのMAEを学習データとして活用する予測システム
"""

import pymysql
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional
import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import RandomForestRegressor
import warnings
warnings.filterwarnings('ignore')

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MAEEnhancedPredictionSystem:
    def __init__(self):
        self.db_config = {
            "host": "34.58.103.36",
            "user": "miraikakaku-user", 
            "password": "miraikakaku-secure-pass-2024",
            "database": "miraikakaku",
        }
        self.mae_history = {}  # 銘柄別MAE履歴
        self.prediction_models = {}  # 銘柄別予測モデル
        
    def get_connection(self):
        return pymysql.connect(**self.db_config)

    def calculate_historical_mae_features(self, symbol: str, days_back: int = 30) -> Dict:
        """
        特定銘柄の過去MAE特徴量を計算
        """
        connection = self.get_connection()
        
        try:
            with connection.cursor() as cursor:
                # 過去の予測データと実績データを取得
                cursor.execute("""
                    SELECT 
                        sp.prediction_date,
                        sp.predicted_price,
                        sp.model_type,
                        sp.confidence_score,
                        sph.close_price as actual_price
                    FROM stock_predictions sp
                    JOIN stock_price_history sph ON (
                        sp.symbol = sph.symbol 
                        AND DATE(sp.prediction_date) = DATE(sph.date)
                    )
                    WHERE sp.symbol = %s
                    AND sp.prediction_date >= DATE_SUB(NOW(), INTERVAL %s DAY)
                    AND sp.prediction_date < NOW()
                    ORDER BY sp.prediction_date DESC
                """, (symbol, days_back))
                
                historical_data = cursor.fetchall()
                
                if not historical_data:
                    return {
                        'recent_mae': 0.0,
                        'mae_trend': 0.0,
                        'prediction_count': 0,
                        'model_consistency': 0.0,
                        'confidence_correlation': 0.0
                    }
                
                # MAE計算と特徴量抽出
                mae_values = []
                confidences = []
                model_types = []
                dates = []
                
                for pred_date, pred_price, model_type, confidence, actual_price in historical_data:
                    mae = abs(pred_price - actual_price)
                    mae_values.append(mae)
                    confidences.append(confidence)
                    model_types.append(model_type)
                    dates.append(pred_date)
                
                # 特徴量計算
                recent_mae = np.mean(mae_values[-7:]) if len(mae_values) >= 7 else np.mean(mae_values)
                
                # MAE トレンド（最近7日 vs 前期間の比較）
                if len(mae_values) >= 14:
                    recent_period_mae = np.mean(mae_values[-7:])
                    previous_period_mae = np.mean(mae_values[-14:-7])
                    mae_trend = (recent_period_mae - previous_period_mae) / previous_period_mae
                else:
                    mae_trend = 0.0
                
                # モデル一貫性（同じモデルが連続して良い予測をしているか）
                model_consistency = len(set(model_types[-5:])) / 5.0 if len(model_types) >= 5 else 0.5
                
                # 信頼度とMAEの相関
                if len(mae_values) > 3:
                    confidence_correlation = np.corrcoef(confidences, mae_values)[0, 1]
                    if np.isnan(confidence_correlation):
                        confidence_correlation = 0.0
                else:
                    confidence_correlation = 0.0
                
                return {
                    'recent_mae': recent_mae,
                    'mae_trend': mae_trend,
                    'prediction_count': len(mae_values),
                    'model_consistency': 1.0 - model_consistency,  # 一貫性が高いほど良い
                    'confidence_correlation': -confidence_correlation  # 負の相関が良い（信頼度高い=MAE低い）
                }
                
        finally:
            connection.close()

    def get_market_context_features(self, symbol: str) -> Dict:
        """
        市場コンテキスト特徴量を取得
        """
        connection = self.get_connection()
        
        try:
            with connection.cursor() as cursor:
                # 最近の価格ボラティリティ
                cursor.execute("""
                    SELECT close_price, date
                    FROM stock_price_history
                    WHERE symbol = %s
                    AND date >= DATE_SUB(NOW(), INTERVAL 30 DAY)
                    ORDER BY date DESC
                    LIMIT 30
                """, (symbol,))
                
                price_data = cursor.fetchall()
                
                if len(price_data) < 5:
                    return {
                        'volatility': 0.0,
                        'price_trend': 0.0,
                        'recent_volume_trend': 0.0
                    }
                
                prices = [float(row[0]) for row in price_data]
                
                # ボラティリティ計算（標準偏差 / 平均）
                volatility = np.std(prices) / np.mean(prices) if np.mean(prices) > 0 else 0.0
                
                # 価格トレンド（最近5日 vs 前5日）
                if len(prices) >= 10:
                    recent_avg = np.mean(prices[:5])
                    previous_avg = np.mean(prices[5:10])
                    price_trend = (recent_avg - previous_avg) / previous_avg
                else:
                    price_trend = 0.0
                
                return {
                    'volatility': volatility,
                    'price_trend': price_trend,
                    'recent_volume_trend': 0.0  # 簡易実装（後で拡張可能）
                }
                
        finally:
            connection.close()

    def build_mae_enhanced_features(self, symbol: str) -> np.ndarray:
        """
        MAE強化特徴量ベクトル構築
        """
        # 過去MAE特徴量
        mae_features = self.calculate_historical_mae_features(symbol)
        
        # 市場コンテキスト特徴量
        market_features = self.get_market_context_features(symbol)
        
        # 特徴量ベクトル組み立て
        feature_vector = np.array([
            mae_features['recent_mae'],
            mae_features['mae_trend'],
            mae_features['prediction_count'],
            mae_features['model_consistency'],
            mae_features['confidence_correlation'],
            market_features['volatility'],
            market_features['price_trend'],
            market_features['recent_volume_trend']
        ])
        
        return feature_vector

    def train_mae_enhanced_model(self, symbol: str, historical_days: int = 60):
        """
        MAE強化モデルの訓練
        """
        logger.info(f"🧠 {symbol} のMAE強化モデル訓練開始")
        
        connection = self.get_connection()
        
        try:
            with connection.cursor() as cursor:
                # 訓練用データ取得
                cursor.execute("""
                    SELECT 
                        sph.date,
                        sph.close_price,
                        sph.open_price,
                        sph.high_price,
                        sph.low_price,
                        sph.volume
                    FROM stock_price_history sph
                    WHERE sph.symbol = %s
                    AND sph.date >= DATE_SUB(NOW(), INTERVAL %s DAY)
                    ORDER BY sph.date
                """, (symbol, historical_days))
                
                price_history = cursor.fetchall()
                
                if len(price_history) < 10:
                    logger.warning(f"⚠️ {symbol}: 訓練データ不足")
                    return None
                
                # 特徴量とターゲット準備
                X, y = self.prepare_training_data(symbol, price_history)
                
                if len(X) < 5:
                    logger.warning(f"⚠️ {symbol}: 特徴量データ不足")
                    return None
                
                # モデル訓練
                model = RandomForestRegressor(
                    n_estimators=50,
                    max_depth=10,
                    random_state=42,
                    n_jobs=-1
                )
                
                # 特徴量標準化
                scaler = StandardScaler()
                X_scaled = scaler.fit_transform(X)
                
                # モデル訓練
                model.fit(X_scaled, y)
                
                # モデル保存
                self.prediction_models[symbol] = {
                    'model': model,
                    'scaler': scaler,
                    'feature_names': [
                        'recent_mae', 'mae_trend', 'prediction_count', 
                        'model_consistency', 'confidence_correlation',
                        'volatility', 'price_trend', 'volume_trend',
                        'price_change_1d', 'price_change_7d', 'volume_ratio'
                    ],
                    'trained_at': datetime.now()
                }
                
                logger.info(f"✅ {symbol} モデル訓練完了")
                return model
                
        finally:
            connection.close()

    def prepare_training_data(self, symbol: str, price_history: List[Tuple]) -> Tuple[np.ndarray, np.ndarray]:
        """
        訓練データ準備
        """
        X = []
        y = []
        
        for i in range(7, len(price_history) - 1):  # 7日分の履歴 + 1日先の予測
            # 基本MAE特徴量
            mae_features = self.build_mae_enhanced_features(symbol)
            
            # 価格ベース特徴量
            current_price = float(price_history[i][1])
            prev_price_1d = float(price_history[i-1][1])
            prev_price_7d = float(price_history[i-7][1])
            
            price_change_1d = (current_price - prev_price_1d) / prev_price_1d
            price_change_7d = (current_price - prev_price_7d) / prev_price_7d
            
            current_volume = float(price_history[i][5])
            avg_volume_7d = np.mean([float(price_history[j][5]) for j in range(i-6, i+1)])
            volume_ratio = current_volume / avg_volume_7d if avg_volume_7d > 0 else 1.0
            
            # 特徴量ベクトル構築
            feature_vector = np.concatenate([
                mae_features,
                [price_change_1d, price_change_7d, volume_ratio]
            ])
            
            # ターゲット（翌日の価格）
            next_day_price = float(price_history[i+1][1])
            
            X.append(feature_vector)
            y.append(next_day_price)
        
        return np.array(X), np.array(y)

    def predict_with_mae_enhancement(self, symbol: str) -> Dict:
        """
        MAE強化予測実行
        """
        if symbol not in self.prediction_models:
            logger.warning(f"⚠️ {symbol}: モデル未訓練、訓練を実行中...")
            model = self.train_mae_enhanced_model(symbol)
            if model is None:
                return None
        
        model_info = self.prediction_models[symbol]
        model = model_info['model']
        scaler = model_info['scaler']
        
        # 現在の特徴量取得
        current_features = self.build_mae_enhanced_features(symbol)
        
        # 最新価格情報取得
        connection = self.get_connection()
        try:
            with connection.cursor() as cursor:
                cursor.execute("""
                    SELECT close_price, volume, date
                    FROM stock_price_history
                    WHERE symbol = %s
                    ORDER BY date DESC
                    LIMIT 7
                """, (symbol,))
                
                recent_data = cursor.fetchall()
                
                if len(recent_data) < 2:
                    return None
                
                current_price = float(recent_data[0][0])
                prev_price = float(recent_data[1][0])
                price_change_1d = (current_price - prev_price) / prev_price
                
                if len(recent_data) >= 7:
                    week_ago_price = float(recent_data[6][0])
                    price_change_7d = (current_price - week_ago_price) / week_ago_price
                else:
                    price_change_7d = 0.0
                
                current_volume = float(recent_data[0][1])
                avg_volume = np.mean([float(row[1]) for row in recent_data])
                volume_ratio = current_volume / avg_volume if avg_volume > 0 else 1.0
                
        finally:
            connection.close()
        
        # 完全な特徴量ベクトル構築
        full_features = np.concatenate([
            current_features,
            [price_change_1d, price_change_7d, volume_ratio]
        ])
        
        # 予測実行
        features_scaled = scaler.transform([full_features])
        predicted_price = model.predict(features_scaled)[0]
        
        # 予測信頼度計算（特徴量ベースの動的信頼度）
        mae_based_confidence = self.calculate_mae_based_confidence(symbol, current_features)
        
        result = {
            'symbol': symbol,
            'predicted_price': predicted_price,
            'current_price': current_price,
            'predicted_change': predicted_price - current_price,
            'predicted_change_percent': ((predicted_price - current_price) / current_price) * 100,
            'mae_enhanced_confidence': mae_based_confidence,
            'model_type': 'mae_enhanced_rf',
            'features_used': model_info['feature_names'],
            'prediction_timestamp': datetime.now()
        }
        
        return result

    def calculate_mae_based_confidence(self, symbol: str, features: np.ndarray) -> float:
        """
        MAEベースの動的信頼度計算
        """
        recent_mae = features[0]  # recent_mae特徴量
        mae_trend = features[1]   # mae_trend特徴量
        model_consistency = features[3]  # model_consistency特徴量
        
        # 基本信頼度（MAEが低いほど高い）
        if recent_mae > 0:
            base_confidence = 1.0 / (1.0 + recent_mae / 10.0)  # 10で正規化
        else:
            base_confidence = 0.9
        
        # トレンド調整（MAEが改善傾向なら信頼度向上）
        trend_adjustment = -mae_trend * 0.1  # トレンドが負（改善）なら正の調整
        
        # 一貫性調整
        consistency_adjustment = model_consistency * 0.1
        
        # 最終信頼度計算
        final_confidence = base_confidence + trend_adjustment + consistency_adjustment
        
        # 0.3-0.95の範囲に制限
        final_confidence = max(0.3, min(0.95, final_confidence))
        
        return round(final_confidence, 3)

    def run_mae_enhanced_batch_prediction(self, target_symbols: List[str] = None):
        """
        MAE強化バッチ予測実行
        """
        start_time = datetime.now()
        logger.info(f"🚀 MAE強化バッチ予測開始: {start_time.strftime('%Y-%m-%d %H:%M:%S')}")
        
        if target_symbols is None:
            # デフォルトターゲット銘柄
            target_symbols = ['AAPL', 'MSFT', 'GOOGL', '7203', '6758', 'NVDA', 'AMZN']
        
        results = []
        success_count = 0
        
        for symbol in target_symbols:
            logger.info(f"📊 {symbol} MAE強化予測実行中...")
            
            try:
                # モデル訓練（必要に応じて）
                if symbol not in self.prediction_models:
                    self.train_mae_enhanced_model(symbol)
                
                # MAE強化予測実行
                prediction_result = self.predict_with_mae_enhancement(symbol)
                
                if prediction_result:
                    results.append(prediction_result)
                    success_count += 1
                    
                    logger.info(f"✅ {symbol}: ¥{prediction_result['predicted_price']:.2f} "
                              f"({prediction_result['predicted_change_percent']:+.2f}%) "
                              f"[信頼度: {prediction_result['mae_enhanced_confidence']:.3f}]")
                    
                    # データベース保存
                    self.save_mae_enhanced_prediction(prediction_result)
                else:
                    logger.warning(f"⚠️ {symbol}: 予測失敗")
                    
            except Exception as e:
                logger.error(f"❌ {symbol} エラー: {e}")
        
        # 最終レポート
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        
        logger.info("=" * 80)
        logger.info("📊 MAE強化バッチ予測完了レポート")
        logger.info(f"⏱️  実行時間: {duration:.1f}秒")
        logger.info(f"🎯 対象銘柄: {len(target_symbols)}銘柄")
        logger.info(f"✅ 成功: {success_count}銘柄")
        logger.info(f"❌ 失敗: {len(target_symbols) - success_count}銘柄")
        logger.info("=" * 80)
        
        return results

    def save_mae_enhanced_prediction(self, prediction_result: Dict):
        """
        MAE強化予測結果保存
        """
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
                    prediction_result['prediction_timestamp'] + timedelta(days=1),  # 翌日予測
                    prediction_result['predicted_price'],
                    prediction_result['predicted_change_percent'],
                    prediction_result['mae_enhanced_confidence'],
                    prediction_result['model_type'],
                    'v3.0_mae_enhanced',
                    1,  # 1日先予測
                    f"MAE enhanced prediction using features: {', '.join(prediction_result['features_used'][:5])}"
                ))
                
                connection.commit()
                
        finally:
            connection.close()

if __name__ == "__main__":
    mae_predictor = MAEEnhancedPredictionSystem()
    
    try:
        # MAE強化予測システム実行
        results = mae_predictor.run_mae_enhanced_batch_prediction()
        
        # 結果サマリー表示
        if results:
            logger.info("🎯 予測結果サマリー:")
            for result in results:
                logger.info(f"  {result['symbol']}: "
                          f"現在¥{result['current_price']:.2f} → 予測¥{result['predicted_price']:.2f} "
                          f"({result['predicted_change_percent']:+.2f}%) "
                          f"[信頼度:{result['mae_enhanced_confidence']:.3f}]")
        
    except KeyboardInterrupt:
        logger.info("🛑 手動停止")
    except Exception as e:
        logger.error(f"❌ システムエラー: {e}")
        import traceback
        traceback.print_exc()