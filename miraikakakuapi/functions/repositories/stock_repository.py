from sqlalchemy.orm import Session
from database.models import StockMaster, StockPriceHistory, StockPredictions
from typing import List, Optional
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

class StockRepository:
    def __init__(self, db: Session):
        self.db = db

    # Stock Master 操作
    def get_stock_by_symbol(self, symbol: str) -> Optional[StockMaster]:
        """シンボルで株式を取得"""
        return self.db.query(StockMaster).filter(
            StockMaster.symbol == symbol.upper()
        ).first()

    def search_stocks(self, query: str, limit: int = 10) -> List[StockMaster]:
        """株式検索"""
        return self.db.query(StockMaster).filter(
            (StockMaster.symbol.contains(query.upper())) |
            (StockMaster.company_name.contains(query))
        ).filter(StockMaster.is_active == True).limit(limit).all()

    def get_all_active_stocks(self) -> List[StockMaster]:
        """アクティブな全株式を取得"""
        return self.db.query(StockMaster).filter(
            StockMaster.is_active == True
        ).all()

    def create_or_update_stock(self, stock_data: dict) -> StockMaster:
        """株式マスターを作成または更新"""
        existing = self.get_stock_by_symbol(stock_data['symbol'])
        
        if existing:
            for key, value in stock_data.items():
                if hasattr(existing, key):
                    setattr(existing, key, value)
            existing.updated_at = datetime.utcnow()
            stock = existing
        else:
            stock = StockMaster(**stock_data)
            self.db.add(stock)
        
        self.db.commit()
        self.db.refresh(stock)
        return stock

    # Stock Price History 操作
    def get_price_history(
        self, 
        symbol: str, 
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        limit: Optional[int] = None
    ) -> List[StockPriceHistory]:
        """株価履歴を取得"""
        query = self.db.query(StockPriceHistory).filter(
            StockPriceHistory.symbol == symbol.upper()
        )
        
        if start_date:
            query = query.filter(StockPriceHistory.date >= start_date)
        if end_date:
            query = query.filter(StockPriceHistory.date <= end_date)
            
        query = query.order_by(StockPriceHistory.date.desc())
        
        if limit:
            query = query.limit(limit)
            
        return query.all()

    def get_latest_price(self, symbol: str) -> Optional[StockPriceHistory]:
        """最新の株価を取得"""
        return self.db.query(StockPriceHistory).filter(
            StockPriceHistory.symbol == symbol.upper()
        ).order_by(StockPriceHistory.date.desc()).first()

    def bulk_insert_price_history(self, price_records: List[dict]) -> int:
        """株価履歴の一括挿入"""
        try:
            objects = [StockPriceHistory(**record) for record in price_records]
            self.db.bulk_save_objects(objects)
            self.db.commit()
            return len(objects)
        except Exception as e:
            logger.error(f"価格履歴一括挿入エラー: {e}")
            self.db.rollback()
            return 0

    # Stock Predictions 操作
    def get_predictions(
        self,
        symbol: str,
        model_name: Optional[str] = None,
        prediction_type: Optional[str] = None,
        start_date: Optional[datetime] = None,
        limit: Optional[int] = None
    ) -> List[StockPredictions]:
        """予測データを取得"""
        query = self.db.query(StockPredictions).filter(
            StockPredictions.symbol == symbol.upper()
        )
        
        if model_name:
            query = query.filter(StockPredictions.model_name == model_name)
        if prediction_type:
            query = query.filter(StockPredictions.prediction_type == prediction_type)
        if start_date:
            query = query.filter(StockPredictions.target_date >= start_date)
            
        query = query.order_by(StockPredictions.target_date.asc())
        
        if limit:
            query = query.limit(limit)
            
        return query.all()

    def create_prediction(self, prediction_data: dict) -> StockPredictions:
        """予測データを作成"""
        prediction = StockPredictions(**prediction_data)
        self.db.add(prediction)
        self.db.commit()
        self.db.refresh(prediction)
        return prediction

    def update_prediction_accuracy(
        self, 
        prediction_id: int, 
        actual_price: float,
        accuracy_score: float
    ) -> Optional[StockPredictions]:
        """予測精度を更新"""
        prediction = self.db.query(StockPredictions).filter(
            StockPredictions.id == prediction_id
        ).first()
        
        if prediction:
            prediction.actual_price = actual_price
            prediction.accuracy_score = accuracy_score
            prediction.is_validated = True
            self.db.commit()
            self.db.refresh(prediction)
            
        return prediction

    # 統計・集計メソッド
    def get_model_performance_stats(self, model_name: str) -> dict:
        """モデルの性能統計を取得"""
        validated_predictions = self.db.query(StockPredictions).filter(
            StockPredictions.model_name == model_name,
            StockPredictions.is_validated == True,
            StockPredictions.accuracy_score.isnot(None)
        ).all()
        
        if not validated_predictions:
            return {"error": "検証済み予測データがありません"}
        
        accuracy_scores = [p.accuracy_score for p in validated_predictions if p.accuracy_score]
        
        return {
            "model_name": model_name,
            "total_predictions": len(validated_predictions),
            "avg_accuracy": sum(accuracy_scores) / len(accuracy_scores) if accuracy_scores else 0,
            "min_accuracy": min(accuracy_scores) if accuracy_scores else 0,
            "max_accuracy": max(accuracy_scores) if accuracy_scores else 0,
        }