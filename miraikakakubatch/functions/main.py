#!/usr/bin/env python3
"""
Miraikakaku バッチ処理メインエントリーポイント
"""

import schedule
import time
import logging
from services.data_pipeline_robust import DataPipelineService
from services.ml_pipeline import MLPipelineService
from services.vertex_ai_service import VertexAIService

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def run_data_pipeline():
    """定期データ取得パイプライン"""
    try:
        pipeline = DataPipelineService()
        pipeline.execute()
        logger.info("データパイプライン実行完了")
    except Exception as e:
        logger.error(f"データパイプライン実行エラー: {e}")

def run_ml_pipeline():
    """機械学習パイプライン実行"""
    try:
        ml_pipeline = MLPipelineService()
        ml_pipeline.train_models()
        logger.info("MLパイプライン実行完了")
    except Exception as e:
        logger.error(f"MLパイプライン実行エラー: {e}")

def run_vertex_ai_inference():
    """Vertex AI推論実行"""
    try:
        vertex_service = VertexAIService()
        vertex_service.run_batch_prediction()
        logger.info("Vertex AI推論完了")
    except Exception as e:
        logger.error(f"Vertex AI推論エラー: {e}")

def main():
    """メインスケジューラー"""
    # 毎日9時にデータ取得
    schedule.every().day.at("09:00").do(run_data_pipeline)
    
    # 毎週月曜日にMLモデル再訓練
    schedule.every().monday.at("02:00").do(run_ml_pipeline)
    
    # 毎時間Vertex AI推論
    schedule.every().hour.do(run_vertex_ai_inference)
    
    logger.info("バッチスケジューラー開始")
    
    while True:
        schedule.run_pending()
        time.sleep(60)

if __name__ == "__main__":
    main()