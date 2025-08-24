# 株式出来高予測サービス

import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from typing import List, Dict, Optional
import json
import logging
from concurrent.futures import ThreadPoolExecutor, as_completed

from database.models.stock_master import StockMaster
from database.models.stock_price_history import StockPriceHistory
from models.forex_models import StockVolumePredictions
from database.database import get_db_session

logger = logging.getLogger(__name__)

class VolumePredictionService:
    """株式出来高予測サービス"""
    
    def __init__(self):
        pass

    def analyze_volume_patterns(self, volumes: List[int], dates: List[datetime]) -> Dict:
        """出来高パターンを分析"""
        if not volumes or len(volumes) < 7:
            return {"error": "Insufficient data"}
        
        volumes_array = np.array(volumes)
        
        # 基本統計
        mean_volume = np.mean(volumes_array)
        std_volume = np.std(volumes_array)
        median_volume = np.median(volumes_array)
        
        # トレンド分析
        if len(volumes) >= 10:
            recent_avg = np.mean(volumes_array[-5:])
            older_avg = np.mean(volumes_array[-10:-5]) if len(volumes) >= 10 else mean_volume
            trend = (recent_avg - older_avg) / older_avg if older_avg != 0 else 0
        else:
            trend = 0
        
        # 周期性分析（曜日効果）
        weekday_volumes = {}
        for i, date in enumerate(dates):
            if i < len(volumes):
                weekday = date.weekday()  # 0=月曜日, 6=日曜日
                if weekday not in weekday_volumes:
                    weekday_volumes[weekday] = []
                weekday_volumes[weekday].append(volumes[i])
        
        weekday_averages = {k: np.mean(v) for k, v in weekday_volumes.items()}
        
        # ボラティリティ（変動率）
        if len(volumes) > 1:
            pct_changes = [(volumes[i] - volumes[i-1]) / volumes[i-1] 
                          for i in range(1, len(volumes)) if volumes[i-1] != 0]
            volatility = np.std(pct_changes) if pct_changes else 0
        else:
            volatility = 0
        
        return {
            "mean_volume": mean_volume,
            "std_volume": std_volume,
            "median_volume": median_volume,
            "trend": trend,
            "volatility": volatility,
            "weekday_averages": weekday_averages,
            "data_points": len(volumes)
        }

    def generate_volume_prediction(self, symbol: str, db: Session, days_ahead: int = 7) -> int:
        """個別銘柄の出来高予測を生成"""
        try:
            # 過去出来高データを取得
            historical_data = db.query(StockPriceHistory).filter(
                StockPriceHistory.symbol == symbol.upper(),
                StockPriceHistory.volume > 0
            ).order_by(StockPriceHistory.date.desc()).limit(30).all()
            
            if len(historical_data) < 7:
                logger.warning(f"Insufficient volume data for {symbol}")
                return 0
            
            # データを分析用に変換
            volumes = [int(h.volume) for h in reversed(historical_data)]
            dates = [h.date for h in reversed(historical_data)]
            
            # パターン分析
            analysis = self.analyze_volume_patterns(volumes, dates)
            if "error" in analysis:
                logger.warning(f"Volume analysis failed for {symbol}: {analysis['error']}")
                return 0
            
            predictions_created = 0
            base_date = datetime.now().date()
            
            for i in range(1, days_ahead + 1):
                prediction_date = base_date + timedelta(days=i)
                
                # 既存予測をチェック
                existing = db.query(StockVolumePredictions).filter(
                    StockVolumePredictions.symbol == symbol.upper(),
                    StockVolumePredictions.prediction_date == prediction_date
                ).first()
                
                if existing:
                    continue
                
                # 曜日効果を考慮
                weekday = prediction_date.weekday()
                weekday_factor = 1.0
                if weekday in analysis['weekday_averages']:
                    weekday_avg = analysis['weekday_averages'][weekday]
                    weekday_factor = weekday_avg / analysis['mean_volume'] if analysis['mean_volume'] != 0 else 1.0
                
                # トレンド効果
                trend_factor = 1 + (analysis['trend'] * i * 0.1)
                
                # ボラティリティを考慮したランダム要素
                random_factor = 1 + np.random.normal(0, analysis['volatility'] * 0.5)
                
                # 最終予測値
                predicted_volume = int(analysis['mean_volume'] * weekday_factor * trend_factor * random_factor)
                predicted_volume = max(0, predicted_volume)  # 負の値を防ぐ
                
                # 信頼度計算（データ量と予測期間を考慮）
                data_quality = min(1.0, len(historical_data) / 20)  # 20日分で最高品質
                time_decay = max(0.5, 1.0 - (i * 0.1))  # 時間とともに信頼度低下
                confidence = data_quality * time_decay
                
                # 上下限計算
                volatility_range = analysis['std_volume'] * (1 + i * 0.1)
                upper_bound = int(predicted_volume + volatility_range)
                lower_bound = int(max(0, predicted_volume - volatility_range))
                
                # 予測要因
                factors = {
                    "mean_volume": analysis['mean_volume'],
                    "trend": analysis['trend'],
                    "weekday_factor": weekday_factor,
                    "volatility": analysis['volatility'],
                    "prediction_horizon": i,
                    "data_quality": data_quality
                }
                
                prediction = StockVolumePredictions(
                    symbol=symbol.upper(),
                    prediction_date=prediction_date,
                    predicted_volume=predicted_volume,
                    confidence_score=confidence,
                    prediction_type='statistical',
                    model_version='v1.0',
                    prediction_horizon=i,
                    base_volume=int(analysis['mean_volume']),
                    upper_bound=upper_bound,
                    lower_bound=lower_bound,
                    prediction_factors=json.dumps(factors)
                )
                
                db.add(prediction)
                predictions_created += 1
            
            db.commit()
            logger.info(f"Created {predictions_created} volume predictions for {symbol}")
            return predictions_created
            
        except Exception as e:
            logger.error(f"Error generating volume predictions for {symbol}: {str(e)}")
            db.rollback()
            return 0

    def update_prediction_accuracy(self, symbol: str, db: Session) -> int:
        """予測精度を実績と比較して更新"""
        try:
            # 過去の予測で実績が判明しているものを取得
            cutoff_date = (datetime.now() - timedelta(days=1)).date()
            
            predictions = db.query(StockVolumePredictions).filter(
                StockVolumePredictions.symbol == symbol.upper(),
                StockVolumePredictions.prediction_date <= cutoff_date,
                StockVolumePredictions.actual_volume.is_(None)  # まだ更新されていない
            ).all()
            
            updated_count = 0
            
            for prediction in predictions:
                # 実際の出来高データを取得
                actual_data = db.query(StockPriceHistory).filter(
                    StockPriceHistory.symbol == symbol.upper(),
                    StockPriceHistory.date == prediction.prediction_date
                ).first()
                
                if actual_data and actual_data.volume:
                    actual_volume = int(actual_data.volume)
                    predicted_volume = prediction.predicted_volume
                    
                    # 精度計算（MAPE: Mean Absolute Percentage Error）
                    if actual_volume != 0:
                        accuracy = 1 - abs(predicted_volume - actual_volume) / actual_volume
                        accuracy = max(0, min(1, accuracy))  # 0-1の範囲に制限
                    else:
                        accuracy = 0
                    
                    # 予測データを更新
                    prediction.actual_volume = actual_volume
                    prediction.accuracy_score = accuracy
                    updated_count += 1
            
            if updated_count > 0:
                db.commit()
                logger.info(f"Updated accuracy for {updated_count} volume predictions for {symbol}")
            
            return updated_count
            
        except Exception as e:
            logger.error(f"Error updating prediction accuracy for {symbol}: {str(e)}")
            db.rollback()
            return 0

    def batch_generate_volume_predictions(self, limit: int = 100, days_ahead: int = 7) -> Dict[str, int]:
        """複数銘柄の出来高予測を並列生成"""
        results = {
            'predictions_created': 0,
            'symbols_processed': 0,
            'accuracy_updates': 0,
            'errors': 0
        }
        
        try:
            # アクティブな銘柄を取得
            with get_db_session() as db:
                symbols = db.query(StockMaster.symbol).filter(
                    StockMaster.is_active == 1
                ).limit(limit).all()
                
                symbol_list = [s.symbol for s in symbols]
            
            # 並列処理で予測生成
            with ThreadPoolExecutor(max_workers=4) as executor:
                future_to_symbol = {
                    executor.submit(self._process_single_symbol, symbol, days_ahead): symbol
                    for symbol in symbol_list
                }
                
                for future in as_completed(future_to_symbol):
                    symbol = future_to_symbol[future]
                    try:
                        result = future.result()
                        results['predictions_created'] += result['predictions_created']
                        results['accuracy_updates'] += result['accuracy_updates']
                        results['symbols_processed'] += 1
                        
                        if result['predictions_created'] > 0:
                            logger.info(f"Volume predictions for {symbol}: {result['predictions_created']} created")
                        
                    except Exception as e:
                        logger.error(f"Error processing volume predictions for {symbol}: {str(e)}")
                        results['errors'] += 1
            
            logger.info(f"Batch volume prediction results: {results}")
            return results
            
        except Exception as e:
            logger.error(f"Error in batch volume prediction processing: {str(e)}")
            results['errors'] += 1
            return results

    def _process_single_symbol(self, symbol: str, days_ahead: int) -> Dict[str, int]:
        """単一銘柄の出来高予測処理"""
        result = {'predictions_created': 0, 'accuracy_updates': 0}
        
        try:
            with get_db_session() as db:
                # 予測生成
                result['predictions_created'] = self.generate_volume_prediction(symbol, db, days_ahead)
                
                # 精度更新
                result['accuracy_updates'] = self.update_prediction_accuracy(symbol, db)
        
        except Exception as e:
            logger.error(f"Error processing volume predictions for {symbol}: {str(e)}")
        
        return result

    def get_volume_prediction_stats(self) -> Dict:
        """出来高予測の統計情報を取得"""
        try:
            with get_db_session() as db:
                # 総予測数
                total_predictions = db.query(StockVolumePredictions).count()
                
                # 精度が計算済みの予測数
                accuracy_calculated = db.query(StockVolumePredictions).filter(
                    StockVolumePredictions.accuracy_score.isnot(None)
                ).count()
                
                # 平均精度
                avg_accuracy = db.query(StockVolumePredictions.accuracy_score).filter(
                    StockVolumePredictions.accuracy_score.isnot(None)
                ).scalar()
                
                if avg_accuracy:
                    avg_accuracy = float(avg_accuracy)
                else:
                    avg_accuracy = 0
                
                # 銘柄数
                symbols_count = db.query(StockVolumePredictions.symbol).distinct().count()
                
                return {
                    "total_predictions": total_predictions,
                    "accuracy_calculated": accuracy_calculated,
                    "average_accuracy": round(avg_accuracy * 100, 2) if avg_accuracy else 0,
                    "symbols_with_predictions": symbols_count,
                    "accuracy_coverage": round((accuracy_calculated / total_predictions * 100), 2) if total_predictions > 0 else 0
                }
                
        except Exception as e:
            logger.error(f"Error getting volume prediction stats: {str(e)}")
            return {"error": str(e)}