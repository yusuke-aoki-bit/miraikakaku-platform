#!/usr/bin/env python3
"""
Cloud Run エントリーポイント - HTTPリクエストでバッチ処理を実行
"""

import os
import sys
import subprocess
import logging
from http.server import HTTPServer, BaseHTTPRequestHandler
import json

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class BatchHandler(BaseHTTPRequestHandler):
    def do_POST(self):
        """POSTリクエストでバッチ処理を実行"""

        batch_script = os.environ.get("BATCH_SCRIPT", "comprehensive_batch.py")

        try:
            logger.info(f"🚀 バッチ処理開始: {batch_script}")

            # バッチスクリプト実行
            result = subprocess.run(
                [sys.executable, batch_script],
                capture_output=True,
                text=True,
                timeout=3600,  # 1時間タイムアウト
            )

            if result.returncode == 0:
                response = {
                    "status": "success",
                    "script": batch_script,
                    "stdout": result.stdout[-1000:],  # 最後の1000文字のみ
                    "message": f"Batch {batch_script} completed successfully",
                }
                self.send_response(200)
            else:
                response = {
                    "status": "error",
                    "script": batch_script,
                    "stderr": result.stderr[-1000:],
                    "message": f"Batch {batch_script} failed",
                }
                self.send_response(500)

        except subprocess.TimeoutExpired:
            response = {
                "status": "timeout",
                "script": batch_script,
                "message": f"Batch {batch_script} timed out",
            }
            self.send_response(408)
        except Exception as e:
            response = {
                "status": "exception",
                "script": batch_script,
                "error": str(e),
                "message": f"Batch {batch_script} encountered an exception",
            }
            self.send_response(500)

        self.send_header("Content-type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps(response).encode())

    def do_GET(self):
        """ヘルスチェック"""
        self.send_response(200)
        self.send_header("Content-type", "text/plain")
        self.end_headers()
        self.wfile.write(b"Batch service is healthy")


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    server = HTTPServer(("", port), BatchHandler)

    logger.info(f"🌐 バッチサーバー開始 ポート:{port}")
    logger.info(
        f"📝 バッチスクリプト: {
            os.environ.get(
                'BATCH_SCRIPT',
                'comprehensive_batch.py')}"
    )

    server.serve_forever()
