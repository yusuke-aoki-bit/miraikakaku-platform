#!/usr/bin/env python3
"""
Miraikakaku バッチ処理メインエントリーポイント
"""

import schedule
import time
import logging
import threading
import os
from http.server import HTTPServer, BaseHTTPRequestHandler
import json
import sys
from urllib.parse import urlparse, parse_qs

# パスを追加してモジュールをインポート可能にする
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from services.simple_data_pipeline import SimpleDataPipelineService as DataPipelineService
    from services.advanced_ml_pipeline import MLPipelineService
    from services.vertex_ai_service import VertexAIService
except ImportError as e:
    logging.warning(f"一部のサービスをインポートできませんでした: {e}")
    # フォールバックでダミーサービスを定義
    class DataPipelineService:
        def execute(self):
            logging.info("データパイプライン実行（ダミー）")
            return {"processed_symbols": 0, "saved_records": 0, "generated_predictions": 0}
    
    class MLPipelineService:
        def train_models(self):
            logging.info("MLパイプライン実行（ダミー）")
    
    class VertexAIService:
        def run_batch_prediction(self):
            logging.info("Vertex AI推論実行（ダミー）")

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# HTTPサーバー用のハンドラー
class HealthHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/health':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            response = {"status": "healthy", "service": "miraikakaku-batch"}
            self.wfile.write(json.dumps(response).encode())
        elif self.path == '/':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            response = {"message": "Miraikakaku Batch Service", "version": "1.0.0"}
            self.wfile.write(json.dumps(response).encode())
        elif self.path == '/trigger/data_pipeline':
            try:
                run_data_pipeline()
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                response = {"status": "success", "message": "データパイプライン実行完了"}
                self.wfile.write(json.dumps(response).encode())
            except Exception as e:
                self.send_response(500)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                response = {"status": "error", "message": str(e)}
                self.wfile.write(json.dumps(response).encode())
        elif self.path == '/trigger/ml_pipeline':
            try:
                run_ml_pipeline()
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                response = {"status": "success", "message": "MLパイプライン実行完了"}
                self.wfile.write(json.dumps(response).encode())
            except Exception as e:
                self.send_response(500)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                response = {"status": "error", "message": str(e)}
                self.wfile.write(json.dumps(response).encode())
        elif self.path == '/trigger/vertex_ai':
            try:
                run_vertex_ai_inference()
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                response = {"status": "success", "message": "Vertex AI推論実行完了"}
                self.wfile.write(json.dumps(response).encode())
            except Exception as e:
                self.send_response(500)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                response = {"status": "error", "message": str(e)}
                self.wfile.write(json.dumps(response).encode())
        else:
            self.send_response(404)
            self.end_headers()
    
    def log_message(self, format, *args):
        # HTTPサーバーのログを抑制
        pass

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

def run_scheduler():
    """バックグラウンドでスケジューラーを実行"""
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

def main():
    """メイン関数 - HTTPサーバーとスケジューラーを並行実行"""
    port = int(os.getenv("PORT", 8080))
    
    # バックグラウンドでスケジューラーを開始
    scheduler_thread = threading.Thread(target=run_scheduler, daemon=True)
    scheduler_thread.start()
    
    # HTTPサーバーを開始
    server = HTTPServer(('0.0.0.0', port), HealthHandler)
    logger.info(f"HTTPサーバー開始 - ポート {port}")
    
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        logger.info("サーバー停止")
        server.shutdown()

if __name__ == "__main__":
    main()