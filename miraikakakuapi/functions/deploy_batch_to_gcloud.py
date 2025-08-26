#!/usr/bin/env python3
"""
Cloud Run バッチ処理デプロイメント - スケーラブルな大量データ処理
"""

import subprocess
import logging
import sys
import os
import json

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def deploy_batch_jobs():
    """バッチ処理をCloud Runにデプロイ"""

    logger.info("🚀 Cloud Run バッチ処理デプロイメント開始")

    # 主要バッチ処理スクリプト
    batch_jobs = [
        {
            "name": "comprehensive-batch",
            "script": "comprehensive_batch.py",
            "description": "8380銘柄 2年間価格データ + 30日予測",
            "memory": "2Gi",
            "cpu": "2",
            "timeout": "3600s",
            "concurrency": "1",
        },
        {
            "name": "ultimate-100-point",
            "script": "ultimate_100_point_system.py",
            "description": "2000銘柄 10年間 + 365日予測",
            "memory": "4Gi",
            "cpu": "4",
            "timeout": "7200s",
            "concurrency": "1",
        },
        {
            "name": "turbo-expansion",
            "script": "turbo_expansion.py",
            "description": "89銘柄 高速データ拡張",
            "memory": "1Gi",
            "cpu": "1",
            "timeout": "1800s",
            "concurrency": "2",
        },
        {
            "name": "continuous-pipeline",
            "script": "continuous_247_pipeline.py",
            "description": "24/7 継続データパイプライン",
            "memory": "1Gi",
            "cpu": "1",
            "timeout": "86400s",
            "concurrency": "1",
        },
        {
            "name": "foreign-key-fix",
            "script": "fix_foreign_key_constraints.py",
            "description": "外部キー制約修正",
            "memory": "512Mi",
            "cpu": "0.5",
            "timeout": "1800s",
            "concurrency": "1",
        },
    ]

    project_id = "pricewise-huqkr"
    region = "us-central1"

    deployed_services = []

    for job in batch_jobs:
        try:
            logger.info(f"📦 デプロイ中: {job['name']} ({job['description']})")

            # Cloud Run サービス作成コマンド
            cmd = [
                "gcloud",
                "run",
                "deploy",
                job["name"],
                "--source",
                ".",
                "--platform",
                "managed",
                "--region",
                region,
                "--project",
                project_id,
                "--memory",
                job["memory"],
                "--cpu",
                job["cpu"],
                "--timeout",
                job["timeout"],
                "--concurrency",
                job["concurrency"],
                "--max-instances",
                "5",
                "--min-instances",
                "0",
                "--port",
                "8080",
                "--set-env-vars",
                f'BATCH_SCRIPT={job["script"]}',
                "--allow-unauthenticated",
                "--quiet",
            ]

            result = subprocess.run(cmd, capture_output=True, text=True, timeout=600)

            if result.returncode == 0:
                logger.info(f"  ✅ {job['name']} デプロイ成功")

                # サービスURLを取得
                url_cmd = [
                    "gcloud",
                    "run",
                    "services",
                    "describe",
                    job["name"],
                    "--region",
                    region,
                    "--format",
                    "value(status.url)",
                ]
                url_result = subprocess.run(url_cmd, capture_output=True, text=True)

                if url_result.returncode == 0:
                    service_url = url_result.stdout.strip()
                    deployed_services.append(
                        {
                            "name": job["name"],
                            "url": service_url,
                            "script": job["script"],
                            "description": job["description"],
                        }
                    )
                    logger.info(f"  🌐 URL: {service_url}")
                else:
                    logger.warning(f"  ⚠️  URL取得失敗: {job['name']}")
            else:
                logger.error(f"  ❌ {job['name']} デプロイ失敗:")
                logger.error(f"     STDOUT: {result.stdout}")
                logger.error(f"     STDERR: {result.stderr}")

        except subprocess.TimeoutExpired:
            logger.error(f"  ⏱️  {job['name']} デプロイタイムアウト")
        except Exception as e:
            logger.error(f"  💥 {job['name']} デプロイエラー: {e}")

    logger.info(f"🎯 デプロイ完了: {len(deployed_services)}/{len(batch_jobs)} サービス")

    # デプロイ済みサービス一覧
    if deployed_services:
        logger.info("📋 デプロイ済みサービス:")
        for service in deployed_services:
            logger.info(f"  🟢 {service['name']}: {service['description']}")
            logger.info(f"     URL: {service['url']}")

    return deployed_services


def setup_cloud_scheduler():
    """Cloud Scheduler で自動実行を設定"""

    logger.info("⏰ Cloud Scheduler 設定開始")

    # スケジューラージョブ
    scheduler_jobs = [
        {
            "name": "comprehensive-batch-daily",
            "schedule": "0 2 * * *",  # 毎日2時
            "target": "comprehensive-batch",
            "description": "日次包括バッチ処理",
        },
        {
            "name": "turbo-expansion-hourly",
            "schedule": "0 */6 * * *",  # 6時間毎
            "target": "turbo-expansion",
            "description": "6時間毎ターボ拡張",
        },
        {
            "name": "foreign-key-maintenance",
            "schedule": "30 1 * * *",  # 毎日1:30
            "target": "foreign-key-fix",
            "description": "外部キー制約メンテナンス",
        },
    ]

    region = "us-central1"
    created_jobs = []

    for job in scheduler_jobs:
        try:
            logger.info(f"📅 作成中: {job['name']}")

            cmd = [
                "gcloud",
                "scheduler",
                "jobs",
                "create",
                "http",
                job["name"],
                "--schedule",
                job["schedule"],
                "--uri",
                f"https://{job['target']}-123456789-uc.a.run.app",  # 実際のURLに置換
                "--http-method",
                "POST",
                "--location",
                region,
                "--description",
                job["description"],
            ]

            result = subprocess.run(cmd, capture_output=True, text=True)

            if result.returncode == 0:
                logger.info(f"  ✅ {job['name']} 作成成功")
                created_jobs.append(job["name"])
            else:
                logger.error(f"  ❌ {job['name']} 作成失敗: {result.stderr}")

        except Exception as e:
            logger.error(f"  💥 {job['name']} エラー: {e}")

    logger.info(f"⏰ スケジューラー設定完了: {len(created_jobs)} ジョブ")
    return created_jobs


def create_batch_dockerfile():
    """バッチ処理用のDockerfileを最適化"""

    dockerfile_content = """FROM python:3.11-slim

WORKDIR /app

# 必要なシステムパッケージをインストール
RUN apt-get update && apt-get install -y \\
    gcc \\
    && rm -rf /var/lib/apt/lists/*

# 要件をコピーしてインストール
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# アプリケーションファイルをコピー
COPY . .

# 環境変数
ENV PYTHONPATH=/app
ENV PORT=8080

# ヘルスチェック用のシンプルサーバーを含むエントリーポイント
COPY docker-entrypoint.py .
EXPOSE 8080

CMD ["python", "docker-entrypoint.py"]"""

    with open(
        "/mnt/c/Users/yuuku/cursor/miraikakaku/miraikakakuapi/functions/Dockerfile", "w"
    ) as f:
        f.write(dockerfile_content)

    logger.info("📄 最適化されたDockerfile作成完了")


def create_entrypoint():
    """Cloud Run用エントリーポイント作成"""

    entrypoint_content = '''#!/usr/bin/env python3
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

        batch_script = os.environ.get('BATCH_SCRIPT', 'comprehensive_batch.py')

        try:
            logger.info(f"🚀 バッチ処理開始: {batch_script}")

            # バッチスクリプト実行
            result = subprocess.run(
                [sys.executable, batch_script],
                capture_output=True,
                text=True,
                timeout=3600  # 1時間タイムアウト
            )

            if result.returncode == 0:
                response = {
                    'status': 'success',
                    'script': batch_script,
                    'stdout': result.stdout[-1000:],  # 最後の1000文字のみ
                    'message': f'Batch {batch_script} completed successfully'
                }
                self.send_response(200)
            else:
                response = {
                    'status': 'error',
                    'script': batch_script,
                    'stderr': result.stderr[-1000:],
                    'message': f'Batch {batch_script} failed'
                }
                self.send_response(500)

        except subprocess.TimeoutExpired:
            response = {
                'status': 'timeout',
                'script': batch_script,
                'message': f'Batch {batch_script} timed out'
            }
            self.send_response(408)
        except Exception as e:
            response = {
                'status': 'exception',
                'script': batch_script,
                'error': str(e),
                'message': f'Batch {batch_script} encountered an exception'
            }
            self.send_response(500)

        self.send_header('Content-type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(response).encode())

    def do_GET(self):
        """ヘルスチェック"""
        self.send_response(200)
        self.send_header('Content-type', 'text/plain')
        self.end_headers()
        self.wfile.write(b'Batch service is healthy')

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    server = HTTPServer(('', port), BatchHandler)

    logger.info(f"🌐 バッチサーバー開始 ポート:{port}")
    logger.info(f"📝 バッチスクリプト: {os.environ.get('BATCH_SCRIPT', 'comprehensive_batch.py')}")

    server.serve_forever()
'''

    with open(
        "/mnt/c/Users/yuuku/cursor/miraikakaku/miraikakakuapi/functions/docker-entrypoint.py",
        "w",
    ) as f:
        f.write(entrypoint_content)

    logger.info("🐳 Docker エントリーポイント作成完了")


if __name__ == "__main__":
    logger.info("=" * 80)
    logger.info("🚀 Google Cloud バッチ処理デプロイメント")
    logger.info("=" * 80)

    # 1. 必要ファイル作成
    create_batch_dockerfile()
    create_entrypoint()

    # 2. Cloud Run デプロイ
    deployed = deploy_batch_jobs()

    # 3. Cloud Scheduler 設定
    scheduled = setup_cloud_scheduler()

    logger.info("=" * 80)
    logger.info(
        f"✅ デプロイ完了: {len(deployed)} サービス, {len(scheduled)} スケジューラー"
    )
    logger.info("🎯 24/7 自動バッチ処理が開始されました")
    logger.info("=" * 80)
