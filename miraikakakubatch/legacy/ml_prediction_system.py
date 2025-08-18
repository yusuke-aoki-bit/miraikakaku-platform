#!/usr/bin/env python3
"""
Miraikakaku ML Prediction System
自動機械学習による株価予測システム

主要機能:
1. 価格データの自動収集・前処理
2. 複数の機械学習モデルの自動トレーニング
3. モデル性能評価・最適化
4. 予測結果の自動生成・保存
5. モデルの定期リトレーニング
"""

import numpy as np
import pandas as pd
import yfinance as yf
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.linear_model import LinearRegression, Ridge
from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.preprocessing import StandardScaler, RobustScaler
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense, Dropout
import joblib
import json
import logging
from datetime import datetime, timedelta
import os
import asyncio
from typing import Dict, List, Tuple, Optional
import warnings
warnings.filterwarnings('ignore')

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MLPredictionSystem:
    """機械学習予測システム"""
    
    def __init__(self):
        self.config = {
            # データ取得設定
            'price_history_days': 730,  # 2年分のデータ
            'prediction_days': 30,      # 30日先まで予測
            'training_ratio': 0.8,      # 80%をトレーニングに使用
            'validation_ratio': 0.2,    # 20%をバリデーションに使用
            
            # 特徴量設定
            'technical_indicators': [
                'sma_5', 'sma_10', 'sma_20', 'sma_50',
                'ema_12', 'ema_26',
                'rsi', 'macd', 'bb_upper', 'bb_lower',
                'volume_sma', 'price_change', 'volatility'
            ],
            
            # モデル設定
            'models': {
                'random_forest': {
                    'class': RandomForestRegressor,
                    'params': {
                        'n_estimators': [50, 100, 200],
                        'max_depth': [10, 20, None],
                        'min_samples_split': [2, 5, 10]
                    }
                },
                'gradient_boosting': {
                    'class': GradientBoostingRegressor,
                    'params': {
                        'n_estimators': [100, 200],
                        'learning_rate': [0.05, 0.1, 0.2],
                        'max_depth': [3, 5, 7]
                    }
                },
                'ridge_regression': {
                    'class': Ridge,
                    'params': {
                        'alpha': [0.1, 1.0, 10.0, 100.0]
                    }
                }
            },
            
            # 保存パス
            'models_dir': 'ml_models',
            'predictions_dir': 'ml_predictions',
            'reports_dir': 'ml_reports',
            
            # 更新頻度
            'retrain_threshold_days': 7,  # 週1回リトレーニング
            'min_accuracy_threshold': 0.75  # 最低精度要求
        }
        
        self.models = {}
        self.scalers = {}
        self.feature_columns = []
        self.trained_symbols = set()
        
        # ディレクトリ作成
        for dir_path in [self.config['models_dir'], self.config['predictions_dir'], self.config['reports_dir']]:
            os.makedirs(dir_path, exist_ok=True)
            
    async def run_ml_training_batch(self, symbols: List[str]) -> Dict:
        """機械学習バッチトレーニング"""
        logger.info(f"🤖 ML バッチトレーニング開始: {len(symbols)}銘柄")
        
        results = {
            'timestamp': datetime.now().isoformat(),
            'symbols_processed': 0,
            'models_trained': 0,
            'predictions_generated': 0,
            'errors': []
        }
        
        for symbol in symbols:
            try:
                # データ取得・前処理
                data = await self.fetch_and_preprocess_data(symbol)
                if data is None or len(data) < 100:  # 最低100日分のデータが必要
                    continue
                
                # モデルトレーニング
                model_results = await self.train_models(symbol, data)
                
                # 予測生成
                if model_results['best_model'] is not None:
                    predictions = await self.generate_predictions(symbol, data, model_results['best_model'])
                    await self.save_predictions(symbol, predictions)
                    results['predictions_generated'] += 1
                
                results['symbols_processed'] += 1
                results['models_trained'] += len(model_results['trained_models'])
                
                # 進捗ログ
                if results['symbols_processed'] % 10 == 0:
                    logger.info(f"進捗: {results['symbols_processed']}/{len(symbols)} 銘柄処理完了")
                    
            except Exception as e:
                logger.error(f"ML処理エラー [{symbol}]: {e}")
                results['errors'].append(f"{symbol}: {str(e)}")
                
        # 結果レポート生成
        await self.generate_ml_report(results)
        
        logger.info(f"✅ ML バッチトレーニング完了: {results['symbols_processed']}銘柄処理")
        return results
        
    async def fetch_and_preprocess_data(self, symbol: str) -> Optional[pd.DataFrame]:
        """データ取得・前処理"""
        try:
            # yfinanceから価格データ取得
            ticker = yf.Ticker(symbol)
            end_date = datetime.now()
            start_date = end_date - timedelta(days=self.config['price_history_days'])
            
            hist = ticker.history(start=start_date, end=end_date, interval="1d")
            
            if hist.empty:
                logger.warning(f"データ取得失敗: {symbol}")
                return None
                
            # 基本的なデータクリーニング
            hist = hist.dropna()
            
            # テクニカル指標追加
            data = self.calculate_technical_indicators(hist)
            
            # 特徴量とターゲット準備
            data = self.prepare_features_target(data)
            
            return data.dropna()
            
        except Exception as e:
            logger.error(f"データ前処理エラー [{symbol}]: {e}")
            return None
            
    def calculate_technical_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        """テクニカル指標計算"""
        data = df.copy()
        
        # 移動平均線
        data['sma_5'] = data['Close'].rolling(window=5).mean()
        data['sma_10'] = data['Close'].rolling(window=10).mean()
        data['sma_20'] = data['Close'].rolling(window=20).mean()
        data['sma_50'] = data['Close'].rolling(window=50).mean()
        
        # 指数移動平均線
        data['ema_12'] = data['Close'].ewm(span=12).mean()
        data['ema_26'] = data['Close'].ewm(span=26).mean()
        
        # RSI
        delta = data['Close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss
        data['rsi'] = 100 - (100 / (1 + rs))
        
        # MACD
        data['macd'] = data['ema_12'] - data['ema_26']
        
        # ボリンジャーバンド
        bb_period = 20
        bb_std = 2
        bb_ma = data['Close'].rolling(window=bb_period).mean()
        bb_std_val = data['Close'].rolling(window=bb_period).std()
        data['bb_upper'] = bb_ma + (bb_std_val * bb_std)
        data['bb_lower'] = bb_ma - (bb_std_val * bb_std)
        
        # ボリューム指標
        data['volume_sma'] = data['Volume'].rolling(window=20).mean()
        
        # 価格変動
        data['price_change'] = data['Close'].pct_change()
        data['volatility'] = data['price_change'].rolling(window=20).std()
        
        return data
        
    def prepare_features_target(self, data: pd.DataFrame) -> pd.DataFrame:
        """特徴量・ターゲット準備"""
        # 特徴量選択
        feature_columns = [col for col in self.config['technical_indicators'] if col in data.columns]
        
        # ターゲット: 5日後の終値
        data['target'] = data['Close'].shift(-5)
        
        # 特徴量のみのデータフレーム作成
        features_data = data[feature_columns + ['target']].copy()
        
        self.feature_columns = feature_columns
        
        return features_data
        
    async def train_models(self, symbol: str, data: pd.DataFrame) -> Dict:
        """モデルトレーニング"""
        logger.info(f"🔧 モデルトレーニング開始: {symbol}")
        
        # データ分割
        X = data[self.feature_columns].values
        y = data['target'].values
        
        # NaN除去
        mask = ~np.isnan(y)
        X, y = X[mask], y[mask]
        
        if len(X) < 50:  # 最低データ数チェック
            logger.warning(f"データ不足: {symbol} ({len(X)}件)")
            return {'best_model': None, 'trained_models': []}
        
        # トレーニング・テストデータ分割
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=1-self.config['training_ratio'], random_state=42
        )
        
        # スケーリング
        scaler = RobustScaler()
        X_train_scaled = scaler.fit_transform(X_train)
        X_test_scaled = scaler.transform(X_test)
        
        self.scalers[symbol] = scaler
        
        # モデルトレーニング・評価
        model_results = []
        trained_models = []
        
        for model_name, model_config in self.config['models'].items():
            try:
                # グリッドサーチでハイパーパラメータ最適化
                model = model_config['class']()
                grid_search = GridSearchCV(
                    model, model_config['params'], 
                    cv=3, scoring='neg_mean_absolute_error',
                    n_jobs=-1
                )
                
                grid_search.fit(X_train_scaled, y_train)
                best_model = grid_search.best_estimator_
                
                # テストデータで評価
                y_pred = best_model.predict(X_test_scaled)
                
                mae = mean_absolute_error(y_test, y_pred)
                mse = mean_squared_error(y_test, y_pred)
                r2 = r2_score(y_test, y_pred)
                
                accuracy = max(0, 1 - (mae / np.mean(y_test)))  # 相対誤差基準の精度
                
                model_result = {
                    'model_name': model_name,
                    'model': best_model,
                    'mae': mae,
                    'mse': mse,
                    'r2': r2,
                    'accuracy': accuracy,
                    'best_params': grid_search.best_params_
                }
                
                model_results.append(model_result)
                trained_models.append(model_name)
                
                logger.info(f"  {model_name}: MAE={mae:.4f}, R2={r2:.4f}, 精度={accuracy:.3%}")
                
            except Exception as e:
                logger.error(f"モデルトレーニングエラー [{model_name}]: {e}")
                
        # 最適モデル選択
        if model_results:
            best_model_result = max(model_results, key=lambda x: x['accuracy'])
            
            if best_model_result['accuracy'] >= self.config['min_accuracy_threshold']:
                # モデル保存
                model_file = os.path.join(self.config['models_dir'], f"{symbol}_{best_model_result['model_name']}.joblib")
                joblib.dump(best_model_result['model'], model_file)
                
                scaler_file = os.path.join(self.config['models_dir'], f"{symbol}_scaler.joblib")
                joblib.dump(scaler, scaler_file)
                
                logger.info(f"✅ 最適モデル保存: {best_model_result['model_name']} (精度: {best_model_result['accuracy']:.3%})")
                
                return {
                    'best_model': best_model_result,
                    'trained_models': trained_models,
                    'all_results': model_results
                }
            else:
                logger.warning(f"精度不足: {symbol} (最大精度: {best_model_result['accuracy']:.3%})")
                
        return {'best_model': None, 'trained_models': trained_models}
        
    async def generate_predictions(self, symbol: str, data: pd.DataFrame, best_model_result: Dict) -> Dict:
        """予測生成"""
        try:
            # 最新データで予測
            latest_data = data.tail(1)
            X_latest = latest_data[self.feature_columns].values
            
            if symbol in self.scalers:
                X_latest_scaled = self.scalers[symbol].transform(X_latest)
                
                # 予測実行
                prediction = best_model_result['model'].predict(X_latest_scaled)[0]
                current_price = latest_data['target'].iloc[0] if not pd.isna(latest_data['target'].iloc[0]) else data['Close'].iloc[-1]
                
                # 予測期間の価格推移生成 (簡易版)
                predictions = []
                base_price = current_price
                
                for i in range(self.config['prediction_days']):
                    # 簡易な価格推移モデル (実際にはより複雑な予測が必要)
                    daily_change = np.random.normal(0, 0.02)  # 日次変動
                    trend_factor = (prediction - base_price) / base_price * 0.1  # トレンド要因
                    
                    predicted_price = base_price * (1 + trend_factor + daily_change)
                    
                    predictions.append({
                        'date': (datetime.now() + timedelta(days=i+1)).strftime('%Y-%m-%d'),
                        'predicted_price': round(predicted_price, 2),
                        'confidence': max(0.5, best_model_result['accuracy'] * 0.9),  # 信頼度
                        'model_used': best_model_result['model_name']
                    })
                    
                    base_price = predicted_price
                    
                return {
                    'symbol': symbol,
                    'predictions': predictions,
                    'model_accuracy': best_model_result['accuracy'],
                    'model_name': best_model_result['model_name'],
                    'generated_at': datetime.now().isoformat()
                }
                
        except Exception as e:
            logger.error(f"予測生成エラー [{symbol}]: {e}")
            
        return {'symbol': symbol, 'predictions': [], 'error': 'prediction_failed'}
        
    async def save_predictions(self, symbol: str, predictions: Dict):
        """予測結果保存"""
        try:
            prediction_file = os.path.join(
                self.config['predictions_dir'], 
                f"{symbol}_predictions_{datetime.now().strftime('%Y%m%d')}.json"
            )
            
            with open(prediction_file, 'w', encoding='utf-8') as f:
                json.dump(predictions, f, indent=2, ensure_ascii=False)
                
            logger.debug(f"予測保存完了: {prediction_file}")
            
        except Exception as e:
            logger.error(f"予測保存エラー [{symbol}]: {e}")
            
    async def train_lstm_model(self, symbol: str, data: pd.DataFrame) -> Optional[Dict]:
        """LSTM深層学習モデルトレーニング (高度版)"""
        try:
            # データ準備
            sequence_length = 60  # 60日分のシーケンス
            price_data = data['Close'].values.reshape(-1, 1)
            
            # スケーリング
            scaler = StandardScaler()
            scaled_data = scaler.fit_transform(price_data)
            
            # シーケンスデータ作成
            X, y = [], []
            for i in range(sequence_length, len(scaled_data)):
                X.append(scaled_data[i-sequence_length:i, 0])
                y.append(scaled_data[i, 0])
                
            X, y = np.array(X), np.array(y)
            X = X.reshape((X.shape[0], X.shape[1], 1))
            
            if len(X) < 100:  # 最低データ数
                return None
                
            # トレーニング・テストデータ分割
            split_idx = int(len(X) * self.config['training_ratio'])
            X_train, X_test = X[:split_idx], X[split_idx:]
            y_train, y_test = y[:split_idx], y[split_idx:]
            
            # LSTMモデル構築
            model = Sequential([
                LSTM(50, return_sequences=True, input_shape=(sequence_length, 1)),
                Dropout(0.2),
                LSTM(50, return_sequences=False),
                Dropout(0.2),
                Dense(25),
                Dense(1)
            ])
            
            model.compile(optimizer='adam', loss='mean_squared_error')
            
            # トレーニング
            model.fit(X_train, y_train, batch_size=32, epochs=50, verbose=0)
            
            # 評価
            y_pred = model.predict(X_test)
            mae = mean_absolute_error(y_test, y_pred)
            
            # モデル保存
            model_path = os.path.join(self.config['models_dir'], f"{symbol}_lstm.h5")
            model.save(model_path)
            
            scaler_path = os.path.join(self.config['models_dir'], f"{symbol}_lstm_scaler.joblib")
            joblib.dump(scaler, scaler_path)
            
            return {
                'model_type': 'lstm',
                'mae': mae,
                'accuracy': max(0, 1 - mae),
                'model_path': model_path,
                'scaler_path': scaler_path
            }
            
        except Exception as e:
            logger.error(f"LSTM訓練エラー [{symbol}]: {e}")
            return None
            
    async def generate_ml_report(self, results: Dict):
        """ML レポート生成"""
        try:
            report = {
                'training_summary': results,
                'model_performance': {
                    'total_symbols': results['symbols_processed'],
                    'successful_predictions': results['predictions_generated'],
                    'success_rate': results['predictions_generated'] / max(1, results['symbols_processed']),
                    'error_rate': len(results['errors']) / max(1, results['symbols_processed'])
                },
                'timestamp': datetime.now().isoformat(),
                'next_training': (datetime.now() + timedelta(days=self.config['retrain_threshold_days'])).isoformat()
            }
            
            report_file = os.path.join(
                self.config['reports_dir'],
                f"ml_training_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            )
            
            with open(report_file, 'w', encoding='utf-8') as f:
                json.dump(report, f, indent=2, ensure_ascii=False)
                
            logger.info(f"📋 MLレポート生成: {report_file}")
            logger.info(f"   成功率: {report['model_performance']['success_rate']:.1%}")
            logger.info(f"   エラー率: {report['model_performance']['error_rate']:.1%}")
            
        except Exception as e:
            logger.error(f"レポート生成エラー: {e}")
            
    async def cleanup_old_models(self, days: int = 30):
        """古いモデル・予測ファイルクリーンアップ"""
        try:
            cutoff_time = datetime.now() - timedelta(days=days)
            
            for directory in [self.config['models_dir'], self.config['predictions_dir']]:
                for filename in os.listdir(directory):
                    file_path = os.path.join(directory, filename)
                    if os.path.getmtime(file_path) < cutoff_time.timestamp():
                        os.remove(file_path)
                        logger.debug(f"古いファイル削除: {filename}")
                        
        except Exception as e:
            logger.error(f"クリーンアップエラー: {e}")

# バッチ処理統合用クラス
class MLBatchIntegration:
    """MLシステムのバッチ処理統合"""
    
    def __init__(self):
        self.ml_system = MLPredictionSystem()
        
    async def run_daily_ml_tasks(self) -> Dict:
        """日次ML処理"""
        logger.info("🤖 日次ML処理開始")
        
        # 主要銘柄の予測更新
        major_symbols = ['AAPL', 'GOOGL', 'MSFT', 'TSLA', 'NVDA', '7203.T', '9984.T', '6758.T']
        results = await self.ml_system.run_ml_training_batch(major_symbols)
        
        return results
        
    async def run_weekly_ml_tasks(self) -> Dict:
        """週次ML処理"""
        logger.info("🤖 週次ML処理開始")
        
        # 全銘柄のモデル更新
        # (実装時は、APIから銘柄リストを取得)
        all_symbols = await self._get_all_symbols()
        
        results = await self.ml_system.run_ml_training_batch(all_symbols[:100])  # 最初の100銘柄
        
        # 古いファイルクリーンアップ
        await self.ml_system.cleanup_old_models()
        
        return results
        
    async def _get_all_symbols(self) -> List[str]:
        """全銘柄リスト取得"""
        try:
            import requests
            response = requests.get('http://localhost:8000/api/finance/stocks/search?query=', timeout=10)
            if response.status_code == 200:
                # 実装時はAPIから銘柄リストを取得
                pass
        except:
            pass
            
        # フォールバック: サンプル銘柄
        return ['AAPL', 'GOOGL', 'MSFT', 'TSLA', 'NVDA', 'META', 'AMZN', '7203.T', '9984.T']

async def main():
    """テスト用メイン処理"""
    ml_batch = MLBatchIntegration()
    
    # テスト実行
    results = await ml_batch.run_daily_ml_tasks()
    print(f"ML処理結果: {results}")

if __name__ == "__main__":
    asyncio.run(main())