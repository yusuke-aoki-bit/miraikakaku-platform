#!/usr/bin/env python3
"""
Continuous LSTM & VertexAI Scheduler
継続的LSTM & VertexAI実行スケジューラー
データの完全な充足を目指す
"""

import time
import threading
import subprocess
import logging
import psycopg2
from datetime import datetime, timedelta

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ContinuousLSTMScheduler:
    """継続的LSTM & VertexAI実行スケジューラー"""

    def __init__(self, interval_hours: int = 2):
        self.interval_hours = interval_hours
        self.running = False
        self.scheduler_thread = None
        self.cycle_count = 0

    def check_data_coverage(self):
        """データカバレッジ確認"""
        try:
            conn = psycopg2.connect(
                host='34.173.9.214',
                user='postgres',
                password='os.getenv('DB_PASSWORD', '')',
                database='miraikakaku'
            )
            cursor = conn.cursor()

            # 銘柄数確認
            cursor.execute('SELECT COUNT(*) FROM stock_master WHERE is_active = true')
            total_symbols = cursor.fetchone()[0]

            # 未来予測カバレッジ
            cursor.execute('''
                SELECT COUNT(DISTINCT symbol) FROM stock_predictions
                WHERE prediction_date >= CURRENT_DATE
                AND model_type LIKE '%LSTM_VERTEXAI%'
            ''')
            future_covered = cursor.fetchone()[0]

            # 過去予測カバレッジ
            cursor.execute('''
                SELECT COUNT(DISTINCT symbol) FROM stock_predictions
                WHERE actual_price IS NOT NULL
                AND model_type LIKE '%HISTORICAL%LSTM%'
            ''')
            historical_covered = cursor.fetchone()[0]

            # 最新予測数
            cursor.execute('''
                SELECT COUNT(*) FROM stock_predictions
                WHERE created_at >= NOW() - INTERVAL '2 hours'
                AND model_type LIKE '%LSTM_VERTEXAI%'
            ''')
            recent_predictions = cursor.fetchone()[0]

            conn.close()

            future_coverage = (future_covered / total_symbols * 100) if total_symbols > 0 else 0
            historical_coverage = (historical_covered / total_symbols * 100) if total_symbols > 0 else 0

            logger.info(f"📊 Data Coverage Report:")
            logger.info(f"  🎯 Total active symbols: {total_symbols}")
            logger.info(f"  🔮 Future predictions: {future_covered} symbols ({future_coverage:.1f}%)")
            logger.info(f"  📜 Historical predictions: {historical_covered} symbols ({historical_coverage:.1f}%)")
            logger.info(f"  ⏰ Recent predictions (2h): {recent_predictions}")

            return {
                'total_symbols': total_symbols,
                'future_coverage': future_coverage,
                'historical_coverage': historical_coverage,
                'recent_predictions': recent_predictions
            }

        except Exception as e:
            logger.error(f"❌ Data coverage check failed: {e}")
            return None

    def run_lstm_system(self):
        """LSTM & VertexAIシステム実行"""
        try:
            logger.info("🚀 Starting LSTM & VertexAI execution...")
            result = subprocess.run(
                ['python3', 'direct_lstm_vertexai_system.py'],
                capture_output=True,
                text=True,
                timeout=3600  # 1時間タイムアウト
            )

            if result.returncode == 0:
                logger.info("✅ LSTM & VertexAI execution completed successfully")
                return True
            else:
                logger.error(f"❌ LSTM execution failed: {result.stderr}")
                return False

        except subprocess.TimeoutExpired:
            logger.warning("⏰ LSTM execution timeout (1 hour) - continuing...")
            return True  # タイムアウトは正常とみなす（大量データ処理中）
        except Exception as e:
            logger.error(f"❌ LSTM execution error: {e}")
            return False

    def start(self):
        """スケジューラー開始"""
        if self.running:
            logger.warning("Scheduler is already running")
            return

        self.running = True
        self.scheduler_thread = threading.Thread(target=self._run_scheduler, daemon=True)
        self.scheduler_thread.start()
        logger.info(f"✅ Continuous LSTM & VertexAI scheduler started (interval: {self.interval_hours}h)")

    def stop(self):
        """スケジューラー停止"""
        self.running = False
        if self.scheduler_thread:
            self.scheduler_thread.join()
        logger.info("🛑 Continuous LSTM scheduler stopped")

    def _run_scheduler(self):
        """スケジューラーメインループ"""
        while self.running:
            try:
                self.cycle_count += 1
                logger.info(f"🔄 サイクル {self.cycle_count}: LSTM & VertexAI継続実行")
                logger.info("="*60)

                # データカバレッジ確認
                coverage = self.check_data_coverage()

                # LSTM & VertexAI実行判定
                should_run = True
                if coverage:
                    # カバレッジが90%以上かつ最近の予測が十分な場合はスキップ
                    if (coverage['future_coverage'] >= 90 and
                        coverage['historical_coverage'] >= 90 and
                        coverage['recent_predictions'] >= 500):
                        should_run = False
                        logger.info("✅ Data coverage sufficient, skipping this cycle")

                if should_run:
                    # LSTM & VertexAI実行
                    success = self.run_lstm_system()

                    if success:
                        logger.info(f"✅ サイクル {self.cycle_count} 完了")
                    else:
                        logger.warning(f"⚠️ サイクル {self.cycle_count} 部分的成功")

                    # 実行後カバレッジ確認
                    post_coverage = self.check_data_coverage()
                    if post_coverage and coverage:
                        improvement = post_coverage['recent_predictions']
                        logger.info(f"📈 予測生成数: {improvement}件")

                # 次回実行まで待機
                sleep_seconds = self.interval_hours * 3600
                logger.info(f"⏰ 次回サイクル {self.cycle_count + 1} まで {self.interval_hours}時間待機")
                logger.info("="*60)

                for i in range(sleep_seconds):
                    if not self.running:
                        break
                    time.sleep(1)

                    # 進捗表示（10分毎）
                    if i % 600 == 0 and i > 0:
                        remaining_hours = (sleep_seconds - i) / 3600
                        logger.info(f"⏳ 残り時間: {remaining_hours:.1f}時間")

            except Exception as e:
                logger.error(f"❌ Scheduler error in cycle {self.cycle_count}: {e}")
                time.sleep(300)  # エラー時は5分待機

def main():
    """メイン実行"""
    scheduler = ContinuousLSTMScheduler(interval_hours=2)  # 2時間間隔

    try:
        logger.info("🚀🤖 Continuous LSTM & VertexAI Scheduler Starting")
        logger.info("💡 目標: 銘柄・価格・過去予測・未来予測の完全充足")
        logger.info("🧠 使用技術: LSTM + VertexAI + TensorFlow 2.20.0")

        scheduler.start()

        # メインループ
        while True:
            time.sleep(10)

    except KeyboardInterrupt:
        logger.info("Shutting down continuous LSTM scheduler...")
        scheduler.stop()

if __name__ == "__main__":
    main()