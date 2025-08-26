#!/usr/bin/env python3
"""
Google Cloud バッチ処理ステータス監視 - 運用状況の総合レポート
"""

import subprocess
import json
import logging
from datetime import datetime, timedelta

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def get_cloud_run_status():
    """Cloud Run サービス状況確認"""

    logger.info("🚀 Cloud Run サービス確認中...")

    try:
        cmd = ["gcloud", "run", "services", "list", "--format", "json"]
        result = subprocess.run(cmd, capture_output=True, text=True)

        if result.returncode == 0:
            services = json.loads(result.stdout)

            batch_services = [
                s
                for s in services
                if "batch" in s.get("metadata", {}).get("name", "").lower()
            ]

            logger.info(f"📊 バッチサービス: {len(batch_services)}個")

            for service in batch_services:
                name = service.get("metadata", {}).get("name", "Unknown")
                region = (
                    service.get("metadata", {})
                    .get("labels", {})
                    .get("cloud.googleapis.com/location", "Unknown")
                )
                url = service.get("status", {}).get("url", "No URL")

                # サービス状況確認
                try:
                    test_cmd = [
                        "curl",
                        "-s",
                        "-o",
                        "/dev/null",
                        "-w",
                        "%{http_code}",
                        url,
                        "-m",
                        "10",
                    ]
                    test_result = subprocess.run(
                        test_cmd, capture_output=True, text=True
                    )

                    status_code = test_result.stdout.strip()
                    status = (
                        "🟢 正常" if status_code == "200" else f"🔴 異常({status_code})"
                    )
                except BaseException:
                    status = "⚠️  不明"

                logger.info(f"  {name} ({region}): {status}")
                logger.info(f"    URL: {url}")

            return batch_services
        else:
            logger.error(f"サービス一覧取得失敗: {result.stderr}")

    except Exception as e:
        logger.error(f"Cloud Run確認エラー: {e}")

    return []


def get_scheduler_status():
    """Cloud Scheduler ジョブ状況確認"""

    logger.info("⏰ Cloud Scheduler ジョブ確認中...")

    try:
        cmd = [
            "gcloud",
            "scheduler",
            "jobs",
            "list",
            "--location=us-central1",
            "--format",
            "json",
        ]
        result = subprocess.run(cmd, capture_output=True, text=True)

        if result.returncode == 0:
            jobs = json.loads(result.stdout)

            batch_jobs = [j for j in jobs if "miraikakaku-batch" in j.get("name", "")]

            logger.info(f"📅 バッチスケジュール: {len(batch_jobs)}個")

            for job in batch_jobs:
                name = job.get("name", "").split("/")[-1]  # フルパスから名前のみ抽出
                schedule = job.get("schedule", "No schedule")
                state = job.get("state", "Unknown")

                state_emoji = "🟢" if state == "ENABLED" else "🔴"

                logger.info(f"  {name}: {state_emoji} {state}")
                logger.info(f"    スケジュール: {schedule}")

                # 最近の実行履歴確認
                try:
                    history_cmd = [
                        "gcloud",
                        "scheduler",
                        "jobs",
                        "run-history",
                        name,
                        "--location=us-central1",
                        "--limit=3",
                        "--format=json",
                    ]
                    history_result = subprocess.run(
                        history_cmd, capture_output=True, text=True, timeout=10
                    )

                    if history_result.returncode == 0:
                        executions = json.loads(history_result.stdout)
                        if executions:
                            latest = executions[0]
                            attempt_time = latest.get("attemptTime", "Unknown")
                            status = latest.get("status", "Unknown")
                            logger.info(f"    最新実行: {attempt_time} - {status}")
                except BaseException:
                    logger.info(f"    実行履歴: 取得不可")

            return batch_jobs
        else:
            logger.error(f"スケジューラー一覧取得失敗: {result.stderr}")

    except Exception as e:
        logger.error(f"Scheduler確認エラー: {e}")

    return []


def get_build_status():
    """最近のCloud Buildステータス確認"""

    logger.info("🔨 最近のビルド状況確認中...")

    try:
        cmd = ["gcloud", "builds", "list", "--limit=5", "--format=json"]
        result = subprocess.run(cmd, capture_output=True, text=True)

        if result.returncode == 0:
            builds = json.loads(result.stdout)

            logger.info(f"📦 最近のビルド: {len(builds)}個")

            for build in builds:
                build_id = build.get("id", "Unknown")[:8]  # 短縮ID
                status = build.get("status", "Unknown")
                create_time = build.get("createTime", "Unknown")

                status_emoji = {
                    "SUCCESS": "🟢",
                    "FAILURE": "🔴",
                    "WORKING": "🟡",
                    "TIMEOUT": "⏱️",
                    "CANCELLED": "⚪",
                }.get(status, "❓")

                logger.info(f"  {build_id}: {status_emoji} {status} ({create_time})")

            return builds
        else:
            logger.error(f"ビルド履歴取得失敗: {result.stderr}")

    except Exception as e:
        logger.error(f"Build確認エラー: {e}")

    return []


def check_database_connection():
    """データベース接続確認"""

    logger.info("🗄️  データベース接続確認中...")

    try:
        # 簡単なDB接続テスト
        from database.database import get_db
        from sqlalchemy import text

        db = next(get_db())
        result = db.execute(text("SELECT COUNT(*) FROM stock_master"))
        count = result.scalar()

        logger.info(f"✅ DB接続成功: stock_master {count:,}件")
        db.close()
        return True

    except Exception as e:
        logger.error(f"❌ DB接続失敗: {e}")
        return False


def generate_monitoring_report():
    """総合監視レポート生成"""

    logger.info("=" * 80)
    logger.info("📊 Google Cloud バッチ処理 総合ステータスレポート")
    logger.info(f"📅 レポート時刻: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    logger.info("=" * 80)

    # 1. Cloud Run サービス確認
    services = get_cloud_run_status()

    logger.info("")

    # 2. Cloud Scheduler ジョブ確認
    jobs = get_scheduler_status()

    logger.info("")

    # 3. 最近のビルド確認
    builds = get_build_status()

    logger.info("")

    # 4. データベース接続確認
    db_status = check_database_connection()

    logger.info("")
    logger.info("🎯 システム状況サマリー")
    logger.info("-" * 60)

    service_count = len(
        [
            s
            for s in services
            if "batch" in s.get("metadata", {}).get("name", "").lower()
        ]
    )
    job_count = len(jobs)
    recent_builds = len([b for b in builds if b.get("status") == "SUCCESS"])

    logger.info(f"  Cloud Run バッチサービス: {service_count}個稼働中")
    logger.info(f"  Cloud Scheduler ジョブ: {job_count}個設定済み")
    logger.info(f"  最近の成功ビルド: {recent_builds}個")
    logger.info(f"  データベース接続: {'✅ 正常' if db_status else '❌ 異常'}")

    # システム健全性スコア
    total_checks = 4
    passed_checks = (
        (1 if service_count > 0 else 0)
        + (1 if job_count > 0 else 0)
        + (1 if recent_builds > 0 else 0)
        + (1 if db_status else 0)
    )

    health_score = (passed_checks / total_checks) * 100

    logger.info(
        f"  システム健全性: {health_score:.0f}% ({passed_checks}/{total_checks})"
    )

    if health_score >= 75:
        logger.info("🟢 システム正常動作中")
    elif health_score >= 50:
        logger.info("🟡 一部問題あり - 確認推奨")
    else:
        logger.info("🔴 システム異常 - 緊急対応必要")

    logger.info("=" * 80)

    return {
        "services": service_count,
        "jobs": job_count,
        "successful_builds": recent_builds,
        "database_healthy": db_status,
        "health_score": health_score,
    }


if __name__ == "__main__":
    report = generate_monitoring_report()
    logger.info(f"✅ 監視レポート完了: 健全性 {report['health_score']:.0f}%")
