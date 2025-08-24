# 為替データ収集サービス

import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from typing import List, Dict, Optional
import json
import logging
from concurrent.futures import ThreadPoolExecutor, as_completed

from models.forex_models import ForexPairs, ForexRates, ForexPredictions, ForexVolumePredictions
from database.database import get_db_session

logger = logging.getLogger(__name__)

class ForexDataService:
    """為替データ収集・予測サービス"""
    
    def __init__(self):
        self.major_pairs = {
            'USDJPY': {'base': 'USD', 'quote': 'JPY', 'name': '米ドル/円', 'yahoo_symbol': 'USDJPY=X'},
            'EURUSD': {'base': 'EUR', 'quote': 'USD', 'name': 'ユーロ/米ドル', 'yahoo_symbol': 'EURUSD=X'},
            'GBPUSD': {'base': 'GBP', 'quote': 'USD', 'name': '英ポンド/米ドル', 'yahoo_symbol': 'GBPUSD=X'},
            'EURJPY': {'base': 'EUR', 'quote': 'JPY', 'name': 'ユーロ/円', 'yahoo_symbol': 'EURJPY=X'},
            'AUDUSD': {'base': 'AUD', 'quote': 'USD', 'name': '豪ドル/米ドル', 'yahoo_symbol': 'AUDUSD=X'},
            'USDCHF': {'base': 'USD', 'quote': 'CHF', 'name': '米ドル/スイスフラン', 'yahoo_symbol': 'USDCHF=X'},
            'USDCAD': {'base': 'USD', 'quote': 'CAD', 'name': '米ドル/カナダドル', 'yahoo_symbol': 'USDCAD=X'},
            'NZDUSD': {'base': 'NZD', 'quote': 'USD', 'name': 'NZドル/米ドル', 'yahoo_symbol': 'NZDUSD=X'},
        }

    def initialize_forex_pairs(self, db: Session):
        """通貨ペアマスターデータを初期化"""
        try:
            for pair_code, info in self.major_pairs.items():
                existing = db.query(ForexPairs).filter(ForexPairs.pair_code == pair_code).first()
                
                if not existing:
                    pair = ForexPairs(
                        pair_code=pair_code,
                        base_currency=info['base'],
                        quote_currency=info['quote'],
                        pair_name=info['name'],
                        yahoo_symbol=info['yahoo_symbol'],
                        is_active=True
                    )
                    db.add(pair)
                    logger.info(f"Added forex pair: {pair_code}")
            
            db.commit()
            logger.info(f"Initialized {len(self.major_pairs)} forex pairs")
            
        except Exception as e:
            logger.error(f"Error initializing forex pairs: {str(e)}")
            db.rollback()

    def fetch_forex_data(self, pair_code: str, days: int = 365) -> Optional[pd.DataFrame]:
        """単一通貨ペアのデータを取得"""
        try:
            if pair_code not in self.major_pairs:
                logger.error(f"Unknown forex pair: {pair_code}")
                return None
            
            yahoo_symbol = self.major_pairs[pair_code]['yahoo_symbol']
            ticker = yf.Ticker(yahoo_symbol)
            
            end_date = datetime.now()
            start_date = end_date - timedelta(days=days)
            
            hist = ticker.history(start=start_date, end=end_date)
            
            if hist.empty:
                logger.warning(f"No data found for {pair_code}")
                return None
            
            # データを整形
            hist['pair_code'] = pair_code
            hist['change_rate'] = hist['Close'].pct_change() * 100
            hist.reset_index(inplace=True)
            
            logger.info(f"Fetched {len(hist)} records for {pair_code}")
            return hist
            
        except Exception as e:
            logger.error(f"Error fetching data for {pair_code}: {str(e)}")
            return None

    def save_forex_rates(self, df: pd.DataFrame, db: Session):
        """為替レートデータを保存"""
        try:
            saved_count = 0
            
            for _, row in df.iterrows():
                # 既存データチェック
                existing = db.query(ForexRates).filter(
                    ForexRates.pair_code == row['pair_code'],
                    ForexRates.date == row['Date'].date()
                ).first()
                
                if existing:
                    # データ更新
                    existing.open_rate = float(row['Open'])
                    existing.high_rate = float(row['High'])
                    existing.low_rate = float(row['Low'])
                    existing.close_rate = float(row['Close'])
                    existing.volume = int(row['Volume']) if pd.notna(row['Volume']) else 0
                    existing.change_rate = float(row['change_rate']) if pd.notna(row['change_rate']) else 0
                else:
                    # 新規データ作成
                    rate = ForexRates(
                        pair_code=row['pair_code'],
                        date=row['Date'],
                        open_rate=float(row['Open']),
                        high_rate=float(row['High']),
                        low_rate=float(row['Low']),
                        close_rate=float(row['Close']),
                        volume=int(row['Volume']) if pd.notna(row['Volume']) else 0,
                        change_rate=float(row['change_rate']) if pd.notna(row['change_rate']) else 0,
                        data_source='yahoo_finance'
                    )
                    db.add(rate)
                    saved_count += 1
            
            db.commit()
            logger.info(f"Saved {saved_count} new forex rate records")
            return saved_count
            
        except Exception as e:
            logger.error(f"Error saving forex rates: {str(e)}")
            db.rollback()
            return 0

    def generate_rate_predictions(self, pair_code: str, db: Session, days_ahead: int = 7) -> int:
        """為替レート予測を生成"""
        try:
            # 過去データを取得
            historical_data = db.query(ForexRates).filter(
                ForexRates.pair_code == pair_code
            ).order_by(ForexRates.date.desc()).limit(30).all()
            
            if len(historical_data) < 10:
                logger.warning(f"Insufficient data for {pair_code} predictions")
                return 0
            
            # データを分析用に変換
            rates = [float(r.close_rate) for r in reversed(historical_data)]
            dates = [r.date for r in reversed(historical_data)]
            
            # 統計的分析
            mean_rate = np.mean(rates)
            std_rate = np.std(rates)
            
            # トレンド分析（短期移動平均vs長期移動平均）
            if len(rates) >= 20:
                sma_5 = np.mean(rates[-5:])
                sma_20 = np.mean(rates[-20:])
                trend = (sma_5 - sma_20) / sma_20 if sma_20 != 0 else 0
            else:
                trend = 0
            
            predictions_created = 0
            base_date = datetime.now().date()
            
            for i in range(1, days_ahead + 1):
                prediction_date = base_date + timedelta(days=i)
                
                # 既存予測をチェック
                existing = db.query(ForexPredictions).filter(
                    ForexPredictions.pair_code == pair_code,
                    ForexPredictions.prediction_date == prediction_date
                ).first()
                
                if existing:
                    continue
                
                # 簡易予測モデル（移動平均 + トレンド + ランダムウォーク）
                trend_factor = trend * i * 0.1  # トレンドの影響を時間で拡大
                volatility = std_rate * np.sqrt(i / 30)  # 時間とともに不確実性増加
                random_factor = np.random.normal(0, volatility * 0.5)
                
                predicted_rate = rates[-1] * (1 + trend_factor + random_factor)
                
                # 信頼度計算（日数が増えるほど低下）
                confidence = max(0.5, 0.95 - (i * 0.1))
                
                # 上下限計算
                upper_bound = predicted_rate + (volatility * 1.96)
                lower_bound = predicted_rate - (volatility * 1.96)
                
                # 予測要因
                factors = {
                    "trend_analysis": trend,
                    "volatility": std_rate,
                    "historical_mean": mean_rate,
                    "prediction_horizon": i
                }
                
                prediction = ForexPredictions(
                    pair_code=pair_code,
                    prediction_date=prediction_date,
                    predicted_rate=predicted_rate,
                    confidence_score=confidence,
                    prediction_type='statistical',
                    model_version='v1.0',
                    prediction_horizon=i,
                    upper_bound=upper_bound,
                    lower_bound=lower_bound,
                    prediction_factors=json.dumps(factors)
                )
                
                db.add(prediction)
                predictions_created += 1
            
            db.commit()
            logger.info(f"Created {predictions_created} rate predictions for {pair_code}")
            return predictions_created
            
        except Exception as e:
            logger.error(f"Error generating rate predictions for {pair_code}: {str(e)}")
            db.rollback()
            return 0

    def generate_volume_predictions(self, pair_code: str, db: Session, days_ahead: int = 7) -> int:
        """為替出来高予測を生成"""
        try:
            # 過去出来高データを取得
            historical_data = db.query(ForexRates).filter(
                ForexRates.pair_code == pair_code,
                ForexRates.volume > 0
            ).order_by(ForexRates.date.desc()).limit(30).all()
            
            if len(historical_data) < 5:
                logger.warning(f"Insufficient volume data for {pair_code}")
                return 0
            
            volumes = [int(r.volume) for r in reversed(historical_data)]
            mean_volume = np.mean(volumes)
            std_volume = np.std(volumes)
            
            predictions_created = 0
            base_date = datetime.now().date()
            
            for i in range(1, days_ahead + 1):
                prediction_date = base_date + timedelta(days=i)
                
                # 既存予測をチェック
                existing = db.query(ForexVolumePredictions).filter(
                    ForexVolumePredictions.pair_code == pair_code,
                    ForexVolumePredictions.prediction_date == prediction_date
                ).first()
                
                if existing:
                    continue
                
                # 出来高予測（周期性とトレンドを考慮）
                weekly_factor = 0.9 + (0.2 * np.sin(2 * np.pi * i / 7))  # 週次サイクル
                trend_factor = 1 + (np.random.normal(0, 0.05))  # 小さなトレンド変動
                
                predicted_volume = int(mean_volume * weekly_factor * trend_factor)
                
                # 信頼度計算
                confidence = max(0.6, 0.9 - (i * 0.05))
                
                # 上下限計算
                upper_bound = int(predicted_volume + std_volume)
                lower_bound = int(max(0, predicted_volume - std_volume))
                
                factors = {
                    "historical_average": mean_volume,
                    "weekly_cycle": weekly_factor,
                    "volatility": std_volume,
                    "prediction_horizon": i
                }
                
                prediction = ForexVolumePredictions(
                    pair_code=pair_code,
                    prediction_date=prediction_date,
                    predicted_volume=predicted_volume,
                    confidence_score=confidence,
                    prediction_type='statistical',
                    model_version='v1.0',
                    prediction_horizon=i,
                    base_volume=int(mean_volume),
                    upper_bound=upper_bound,
                    lower_bound=lower_bound,
                    prediction_factors=json.dumps(factors)
                )
                
                db.add(prediction)
                predictions_created += 1
            
            db.commit()
            logger.info(f"Created {predictions_created} volume predictions for {pair_code}")
            return predictions_created
            
        except Exception as e:
            logger.error(f"Error generating volume predictions for {pair_code}: {str(e)}")
            db.rollback()
            return 0

    def batch_process_all_pairs(self, days_back: int = 365, prediction_days: int = 7) -> Dict[str, int]:
        """全通貨ペアを並列処理"""
        results = {
            'rates_saved': 0,
            'rate_predictions': 0,
            'volume_predictions': 0,
            'errors': 0
        }
        
        try:
            with get_db_session() as db:
                # 通貨ペアマスターを初期化
                self.initialize_forex_pairs(db)
            
            # 並列処理でデータ取得
            with ThreadPoolExecutor(max_workers=4) as executor:
                future_to_pair = {
                    executor.submit(self._process_single_pair, pair_code, days_back, prediction_days): pair_code
                    for pair_code in self.major_pairs.keys()
                }
                
                for future in as_completed(future_to_pair):
                    pair_code = future_to_pair[future]
                    try:
                        result = future.result()
                        results['rates_saved'] += result['rates_saved']
                        results['rate_predictions'] += result['rate_predictions']
                        results['volume_predictions'] += result['volume_predictions']
                        
                        logger.info(f"Completed processing {pair_code}: {result}")
                        
                    except Exception as e:
                        logger.error(f"Error processing {pair_code}: {str(e)}")
                        results['errors'] += 1
            
            return results
            
        except Exception as e:
            logger.error(f"Error in batch processing: {str(e)}")
            results['errors'] += 1
            return results

    def _process_single_pair(self, pair_code: str, days_back: int, prediction_days: int) -> Dict[str, int]:
        """単一通貨ペアの処理"""
        result = {'rates_saved': 0, 'rate_predictions': 0, 'volume_predictions': 0}
        
        try:
            with get_db_session() as db:
                # データ取得と保存
                df = self.fetch_forex_data(pair_code, days_back)
                if df is not None:
                    result['rates_saved'] = self.save_forex_rates(df, db)
                
                # レート予測生成
                result['rate_predictions'] = self.generate_rate_predictions(pair_code, db, prediction_days)
                
                # 出来高予測生成
                result['volume_predictions'] = self.generate_volume_predictions(pair_code, db, prediction_days)
        
        except Exception as e:
            logger.error(f"Error processing {pair_code}: {str(e)}")
        
        return result