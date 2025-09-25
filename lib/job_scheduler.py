#!/usr/bin/env python3
"""
Continuous Batch Job Scheduler
継続的バッチジョブスケジューラー
"""

import time
import threading
import logging
from datetime import datetime, timedelta
from continuous_data_enrichment import ContinuousDataEnrichmentJob
from ai_prediction_engine import AIPredictionEngine
from prediction_validator import PredictionValidator

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class BatchJobScheduler:
    """バッチジョブスケジューラー"""

    def __init__(self, interval_hours: int = 2):
        self.interval_hours = interval_hours
        self.running = False
        self.scheduler_thread = None
        self.job_deployer = ContinuousDataEnrichmentJob()
        self.ai_engine = AIPredictionEngine()
        self.validator = PredictionValidator()
        self.cycle_count = 0

    def start(self):
        """スケジューラーを開始"""
        if self.running:
            logger.warning("Scheduler is already running")
            return

        self.running = True
        self.scheduler_thread = threading.Thread(target=self._run_scheduler, daemon=True)
        self.scheduler_thread.start()
        logger.info(f"✅ Batch job scheduler started (interval: {self.interval_hours}h)")

    def stop(self):
        """スケジューラーを停止"""
        self.running = False
        if self.scheduler_thread:
            self.scheduler_thread.join()
        logger.info("🛑 Batch job scheduler stopped")

    def _run_scheduler(self):
        """スケジューラーのメインループ"""
        while self.running:
            try:
                self.cycle_count += 1
                logger.info(f"🚀 サイクル {self.cycle_count}: スケジュールジョブ実行中...")

                # 1. データ収集ジョブ（毎回実行）
                logger.info("📊 データ収集ジョブ投入中...")
                self.job_deployer.deploy_continuous_jobs()

                # 2. AI予測ジョブ（偶数サイクル）
                if self.cycle_count % 2 == 0:
                    logger.info("🤖 AI予測ジョブ投入中...")
                    self.ai_engine.deploy_ai_prediction_job()

                # 3. 予測検証ジョブ（3の倍数サイクル）
                if self.cycle_count % 3 == 0:
                    logger.info("🔍 予測検証ジョブ投入中...")
                    self.validator.deploy_validation_job()

                # 次の実行まで待機
                sleep_seconds = self.interval_hours * 3600
                logger.info(f"⏰ 次回サイクル {self.cycle_count + 1} まで {self.interval_hours} 時間待機")

                for _ in range(sleep_seconds):
                    if not self.running:
                        break
                    time.sleep(1)

            except Exception as e:
                logger.error(f"❌ Scheduler error: {e}")
                time.sleep(300)  # エラー時は5分待機

def main():
    """メイン関数"""
    scheduler = BatchJobScheduler(interval_hours=2)  # 2時間間隔

    try:
        scheduler.start()

        # スケジューラーが動作し続けるように待機
        while True:
            time.sleep(10)

    except KeyboardInterrupt:
        logger.info("Shutting down scheduler...")
        scheduler.stop()

if __name__ == "__main__":
    main()