#!/usr/bin/env python3
"""
Cloud Run APIサービス比較分析 - api vs api-enhanced の違いを詳細調査
"""

import subprocess
import json
import logging
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def compare_api_services():
    """両APIサービスの詳細比較"""

    logger.info("🔍 Cloud Run APIサービス比較分析")
    logger.info("=" * 80)

    services = ["miraikakaku-api", "miraikakaku-api-enhanced"]
    comparison = {}

    for service in services:
        try:
            # サービス詳細取得
            cmd = [
                "gcloud",
                "run",
                "services",
                "describe",
                service,
                "--region=us-central1",
                "--format=json",
            ]
            result = subprocess.run(cmd, capture_output=True, text=True)

            if result.returncode == 0:
                service_data = json.loads(result.stdout)

                spec = service_data.get("spec", {}).get("template", {}).get("spec", {})
                metadata = service_data.get("metadata", {})
                status = service_data.get("status", {})

                container = spec.get("containers", [{}])[0]

                comparison[service] = {
                    "creation_date": metadata.get("creationTimestamp", "Unknown"),
                    "generation": metadata.get("generation", 0),
                    "image": container.get("image", "Unknown"),
                    "cpu_limit": container.get("resources", {})
                    .get("limits", {})
                    .get("cpu", "Unknown"),
                    "memory_limit": container.get("resources", {})
                    .get("limits", {})
                    .get("memory", "Unknown"),
                    "timeout": spec.get("timeoutSeconds", "Unknown"),
                    "concurrency": spec.get("containerConcurrency", "Unknown"),
                    "service_url": status.get("url", "Unknown"),
                    "revision": status.get("latestReadyRevisionName", "Unknown"),
                    "port": container.get("ports", [{}])[0].get(
                        "containerPort", "Unknown"
                    ),
                }

                # 環境変数取得
                env_vars = container.get("env", [])
                comparison[service]["env_vars"] = {
                    env["name"]: env.get("value", "SET") for env in env_vars
                }

            else:
                logger.error(f"❌ {service} 詳細取得失敗: {result.stderr}")

        except Exception as e:
            logger.error(f"💥 {service} 分析エラー: {e}")

    # 比較結果表示
    logger.info("📊 APIサービス仕様比較")
    logger.info("-" * 80)

    if len(comparison) == 2:
        api_data = comparison.get("miraikakaku-api", {})
        enhanced_data = comparison.get("miraikakaku-api-enhanced", {})

        logger.info(f"{'項目':<20} {'api':<40} {'api-enhanced':<40}")
        logger.info("-" * 100)

        # 基本情報比較
        comparisons = [
            ("作成日", "creation_date"),
            ("世代", "generation"),
            ("コンテナイメージ", "image"),
            ("CPU制限", "cpu_limit"),
            ("メモリ制限", "memory_limit"),
            ("タイムアウト", "timeout"),
            ("同時実行数", "concurrency"),
            ("ポート", "port"),
            ("リビジョン", "revision"),
        ]

        for label, key in comparisons:
            api_val = str(api_data.get(key, "N/A"))
            enhanced_val = str(enhanced_data.get(key, "N/A"))

            # 違いがある場合はマーク
            diff_mark = " ⚠️" if api_val != enhanced_val else ""

            logger.info(f"{label:<20} {api_val:<40} {enhanced_val:<40}{diff_mark}")

        logger.info("")
        logger.info("🌐 URL比較")
        logger.info("-" * 80)
        logger.info(f"api:          {api_data.get('service_url', 'N/A')}")
        logger.info(f"api-enhanced: {enhanced_data.get('service_url', 'N/A')}")

        logger.info("")
        logger.info("🔧 環境変数比較")
        logger.info("-" * 80)

        # 環境変数の比較
        api_env = api_data.get("env_vars", {})
        enhanced_env = enhanced_data.get("env_vars", {})

        all_env_keys = set(api_env.keys()) | set(enhanced_env.keys())

        for env_key in sorted(all_env_keys):
            api_val = api_env.get(env_key, "未設定")
            enhanced_val = enhanced_env.get(env_key, "未設定")

            diff_mark = " ⚠️" if api_val != enhanced_val else ""

            logger.info(f"{env_key:<30} {api_val:<25} {enhanced_val:<25}{diff_mark}")

    return comparison


def test_api_functionality():
    """両APIサービスの機能テスト"""

    logger.info("")
    logger.info("🧪 API機能テスト")
    logger.info("-" * 80)

    services = [
        ("miraikakaku-api", "https://miraikakaku-api-465603676610.us-central1.run.app"),
        (
            "miraikakaku-api-enhanced",
            "https://miraikakaku-api-enhanced-465603676610.us-central1.run.app",
        ),
    ]

    for service_name, base_url in services:
        logger.info(f"{service_name}:")

        # ヘルスチェック
        try:
            health_cmd = ["curl", "-s", base_url, "-m", "10"]
            health_result = subprocess.run(health_cmd, capture_output=True, text=True)

            if health_result.returncode == 0:
                try:
                    response_data = json.loads(health_result.stdout)
                    logger.info(f"  ルート: ✅ {response_data.get('message', 'OK')}")
                except json.JSONDecodeError:
                    logger.info(f"  ルート: ✅ レスポンス取得成功")
            else:
                logger.error(f"  ルート: ❌ アクセス失敗")
        except Exception as e:
            logger.error(f"  ルート: 💥 エラー - {e}")

        # APIエンドポイントテスト
        endpoints = [
            ("/health", "ヘルスチェック"),
            ("/api/finance/symbols", "銘柄一覧"),
            ("/docs", "API文書"),
            ("/api/finance/stock/AAPL", "AAPL株価"),
        ]

        for endpoint, description in endpoints:
            try:
                test_url = base_url + endpoint
                test_cmd = [
                    "curl",
                    "-s",
                    "-o",
                    "/dev/null",
                    "-w",
                    "%{http_code}",
                    test_url,
                    "-m",
                    "5",
                ]
                test_result = subprocess.run(test_cmd, capture_output=True, text=True)

                status_code = test_result.stdout.strip()

                if status_code in ["200", "307"]:  # 307はリダイレクト
                    logger.info(f"  {description}: ✅ {status_code}")
                elif status_code == "404":
                    logger.warning(f"  {description}: ⚠️ {status_code} (未実装)")
                else:
                    logger.error(f"  {description}: ❌ {status_code}")

            except Exception as e:
                logger.error(f"  {description}: 💥 エラー - {e}")

        logger.info("")


def check_traffic_allocation():
    """トラフィック配分確認"""

    logger.info("🚦 トラフィック配分確認")
    logger.info("-" * 80)

    services = ["miraikakaku-api", "miraikakaku-api-enhanced"]

    for service in services:
        try:
            cmd = [
                "gcloud",
                "run",
                "services",
                "describe",
                service,
                "--region=us-central1",
                "--format=value(spec.traffic[].percent)",
            ]
            result = subprocess.run(cmd, capture_output=True, text=True)

            if result.returncode == 0:
                traffic = result.stdout.strip()
                logger.info(f"{service}: {traffic}% トラフィック")
            else:
                logger.error(f"{service}: トラフィック情報取得失敗")

        except Exception as e:
            logger.error(f"{service}: エラー - {e}")


if __name__ == "__main__":
    # 詳細比較実行
    comparison_data = compare_api_services()

    # 機能テスト
    test_api_functionality()

    # トラフィック確認
    check_traffic_allocation()

    logger.info("")
    logger.info("🎯 結論")
    logger.info("-" * 80)
    logger.info("両APIサービスの主な違いを特定しました。")
    logger.info("詳細は上記の比較結果をご確認ください。")
