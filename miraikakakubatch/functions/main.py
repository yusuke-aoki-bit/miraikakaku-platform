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
    from services.simple_data_pipeline import (
        SimpleDataPipelineService as DataPipelineService,
    )
    from services.advanced_ml_pipeline import MLPipelineService
    from services.vertex_ai_service import VertexAIService
    from services.forex_data_service import ForexDataService
    from services.volume_prediction_service import VolumePredictionService
    from services.enhanced_prediction_service import EnhancedPredictionService
except ImportError as e:
    logging.warning(f"一部のサービスをインポートできませんでした: {e}")

    # フォールバックでダミーサービスを定義
    class DataPipelineService:
        def execute(self):
            logging.info("データパイプライン実行（ダミー）")
            return {
                "processed_symbols": 0,
                "saved_records": 0,
                "generated_predictions": 0,
            }

    class MLPipelineService:
        def train_models(self):
            logging.info("MLパイプライン実行（ダミー）")

    class VertexAIService:
        def run_batch_prediction(self):
            logging.info("Vertex AI推論実行（ダミー）")

    class ForexDataService:
        def batch_process_all_pairs(self, days_back=365, prediction_days=7):
            logging.info("為替データ処理実行（ダミー）")
            return {
                "rates_saved": 0,
                "rate_predictions": 0,
                "volume_predictions": 0,
                "errors": 0,
            }

    class VolumePredictionService:
        def batch_generate_volume_predictions(self, limit=100, days_ahead=7):
            logging.info("出来高予測実行（ダミー）")
            return {"predictions_created": 0, "symbols_processed": 0, "errors": 0}

    class EnhancedPredictionService:
        def batch_generate_enhanced_predictions(self, limit=50, days_ahead=30):
            logging.info("強化予測実行（ダミー）")
            return {"symbols_processed": 0, "total_predictions": 0, "errors": 0}


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# HTTPサーバー用のハンドラー
class HealthHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/health":
            self.send_response(200)
            self.send_header("Content-type", "application/json")
            self.end_headers()
            response = {"status": "healthy", "service": "miraikakaku-batch"}
            self.wfile.write(json.dumps(response).encode())
        elif self.path == "/":
            self.send_response(200)
            self.send_header("Content-type", "application/json")
            self.end_headers()
            response = {"message": "Miraikakaku Batch Service", "version": "1.0.0"}
            self.wfile.write(json.dumps(response).encode())
        elif self.path == "/trigger/data_pipeline":
            try:
                run_data_pipeline()
                self.send_response(200)
                self.send_header("Content-type", "application/json")
                self.end_headers()
                response = {
                    "status": "success",
                    "message": "データパイプライン実行完了",
                }
                self.wfile.write(json.dumps(response).encode())
            except Exception as e:
                self.send_response(500)
                self.send_header("Content-type", "application/json")
                self.end_headers()
                response = {"status": "error", "message": str(e)}
                self.wfile.write(json.dumps(response).encode())
        elif self.path == "/trigger/ml_pipeline":
            try:
                run_ml_pipeline()
                self.send_response(200)
                self.send_header("Content-type", "application/json")
                self.end_headers()
                response = {"status": "success", "message": "MLパイプライン実行完了"}
                self.wfile.write(json.dumps(response).encode())
            except Exception as e:
                self.send_response(500)
                self.send_header("Content-type", "application/json")
                self.end_headers()
                response = {"status": "error", "message": str(e)}
                self.wfile.write(json.dumps(response).encode())
        elif self.path == "/trigger/vertex_ai":
            try:
                run_vertex_ai_inference()
                self.send_response(200)
                self.send_header("Content-type", "application/json")
                self.end_headers()
                response = {"status": "success", "message": "Vertex AI推論実行完了"}
                self.wfile.write(json.dumps(response).encode())
            except Exception as e:
                self.send_response(500)
                self.send_header("Content-type", "application/json")
                self.end_headers()
                response = {"status": "error", "message": str(e)}
                self.wfile.write(json.dumps(response).encode())
        elif self.path == "/trigger/forex_data":
            try:
                result = run_forex_data_pipeline()
                self.send_response(200)
                self.send_header("Content-type", "application/json")
                self.end_headers()
                response = {
                    "status": "success",
                    "message": "為替データ処理完了",
                    "result": result,
                }
                self.wfile.write(json.dumps(response).encode())
            except Exception as e:
                self.send_response(500)
                self.send_header("Content-type", "application/json")
                self.end_headers()
                response = {"status": "error", "message": str(e)}
                self.wfile.write(json.dumps(response).encode())
        elif self.path == "/trigger/volume_predictions":
            try:
                result = run_volume_predictions()
                self.send_response(200)
                self.send_header("Content-type", "application/json")
                self.end_headers()
                response = {
                    "status": "success",
                    "message": "出来高予測処理完了",
                    "result": result,
                }
                self.wfile.write(json.dumps(response).encode())
            except Exception as e:
                self.send_response(500)
                self.send_header("Content-type", "application/json")
                self.end_headers()
                response = {"status": "error", "message": str(e)}
                self.wfile.write(json.dumps(response).encode())
        elif self.path == "/trigger/enhanced_predictions":
            try:
                result = run_enhanced_predictions()
                self.send_response(200)
                self.send_header("Content-type", "application/json")
                self.end_headers()
                response = {
                    "status": "success",
                    "message": "強化予測処理完了",
                    "result": result,
                }
                self.wfile.write(json.dumps(response).encode())
            except Exception as e:
                self.send_response(500)
                self.send_header("Content-type", "application/json")
                self.end_headers()
                response = {"status": "error", "message": str(e)}
                self.wfile.write(json.dumps(response).encode())
        elif self.path == "/trigger/comprehensive_batch":
            try:
                result = run_comprehensive_batch()
                self.send_response(200)
                self.send_header("Content-type", "application/json")
                self.end_headers()
                response = {
                    "status": "success",
                    "message": "包括的バッチ処理完了",
                    "result": result,
                }
                self.wfile.write(json.dumps(response).encode())
            except Exception as e:
                self.send_response(500)
                self.send_header("Content-type", "application/json")
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


def run_forex_data_pipeline():
    """為替データ収集・予測パイプライン"""
    try:
        forex_service = ForexDataService()
        result = forex_service.batch_process_all_pairs(days_back=365, prediction_days=7)
        logger.info(f"為替データ処理完了: {result}")
        return result
    except Exception as e:
        logger.error(f"為替データ処理エラー: {e}")
        return {"error": str(e)}


def run_volume_predictions():
    """出来高予測生成パイプライン"""
    try:
        volume_service = VolumePredictionService()
        result = volume_service.batch_generate_volume_predictions(
            limit=100, days_ahead=7
        )
        logger.info(f"出来高予測処理完了: {result}")
        return result
    except Exception as e:
        logger.error(f"出来高予測処理エラー: {e}")
        return {"error": str(e)}


def run_enhanced_predictions():
    """強化予測生成パイプライン"""
    try:
        prediction_service = EnhancedPredictionService()
        result = prediction_service.batch_generate_enhanced_predictions(
            limit=50, days_ahead=30
        )
        logger.info(f"強化予測処理完了: {result}")
        return result
    except Exception as e:
        logger.error(f"強化予測処理エラー: {e}")
        return {"error": str(e)}


def run_comprehensive_batch():
    """包括的バッチ処理（全機能を順次実行）"""
    try:
        logger.info("包括的バッチ処理開始")
        results = {}

        # 1. 基本データパイプライン
        logger.info("1/5: データパイプライン実行中...")
        run_data_pipeline()
        results["data_pipeline"] = "completed"

        # 2. 為替データ処理
        logger.info("2/5: 為替データ処理実行中...")
        forex_result = run_forex_data_pipeline()
        results["forex_data"] = forex_result

        # 3. 出来高予測
        logger.info("3/5: 出来高予測処理実行中...")
        volume_result = run_volume_predictions()
        results["volume_predictions"] = volume_result

        # 4. 強化予測
        logger.info("4/5: 強化予測処理実行中...")
        enhanced_result = run_enhanced_predictions()
        results["enhanced_predictions"] = enhanced_result

        # 5. ML推論
        logger.info("5/5: ML推論実行中...")
        run_vertex_ai_inference()
        results["vertex_ai"] = "completed"

        logger.info(f"包括的バッチ処理完了: {results}")
        return results

    except Exception as e:
        logger.error(f"包括的バッチ処理エラー: {e}")
        return {"error": str(e)}


def run_scheduler():
    """バックグラウンドでスケジューラーを実行"""
    # 毎日9時に包括的バッチ処理
    schedule.every().day.at("09:00").do(run_comprehensive_batch)

    # 毎日14時に為替データ更新
    schedule.every().day.at("14:00").do(run_forex_data_pipeline)

    # 毎日18時に出来高予測
    schedule.every().day.at("18:00").do(run_volume_predictions)

    # 毎日22時に強化予測
    schedule.every().day.at("22:00").do(run_enhanced_predictions)

    # 毎週月曜日にMLモデル再訓練
    schedule.every().monday.at("02:00").do(run_ml_pipeline)

    # 毎2時間でVertex AI推論（頻度を下げる）
    schedule.every(2).hours.do(run_vertex_ai_inference)

    logger.info("拡張バッチスケジューラー開始")
    logger.info("スケジュール:")
    logger.info("- 09:00: 包括的バッチ処理")
    logger.info("- 14:00: 為替データ更新")
    logger.info("- 18:00: 出来高予測")
    logger.info("- 22:00: 強化予測")
    logger.info("- 月曜02:00: MLモデル再訓練")
    logger.info("- 2時間毎: Vertex AI推論")

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
    server = HTTPServer(("0.0.0.0", port), HealthHandler)
    logger.info(f"HTTPサーバー開始 - ポート {port}")

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        logger.info("サーバー停止")
        server.shutdown()


if __name__ == "__main__":
    main()
