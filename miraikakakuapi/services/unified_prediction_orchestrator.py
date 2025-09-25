#!/usr/bin/env python3
"""
Unified Prediction Orchestrator
LSTM & VertexAI 予測システムの統合オーケストレーター
"""

import os
import sys
import time
import logging
import subprocess
import schedule
import threading
from datetime import datetime, timedelta
from typing import Dict, Any

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class PredictionOrchestrator:
    """予測システム統合オーケストレーター"""

    def __init__(self):
        self.lstm_script = "separated_lstm_prediction_system.py"
        self.vertexai_script = "separated_vertexai_prediction_system.py"
        self.execution_log = []

    def log_execution(self, system_name: str, success: bool, duration: float, details: str = ""):
        """実行ログ記録"""
        log_entry = {
            'timestamp': datetime.now(),
            'system': system_name,
            'success': success,
            'duration_seconds': duration,
            'details': details
        }
        self.execution_log.append(log_entry)

        # 最新100件のみ保持
        if len(self.execution_log) > 100:
            self.execution_log = self.execution_log[-100:]

    def run_lstm_predictions(self):
        """LSTM予測システム実行"""
        logger.info("🚀 Starting LSTM Prediction System")
        start_time = time.time()

        try:
            result = subprocess.run([
                sys.executable, self.lstm_script
            ], capture_output=True, text=True, timeout=600)

            duration = time.time() - start_time
            success = result.returncode == 0

            if success:
                logger.info(f"✅ LSTM System completed successfully in {duration:.2f}s")
                self.log_execution("LSTM", True, duration, "Completed successfully")
            else:
                logger.error(f"❌ LSTM System failed: {result.stderr}")
                self.log_execution("LSTM", False, duration, f"Failed: {result.stderr[:200]}")

            return success

        except subprocess.TimeoutExpired:
            duration = time.time() - start_time
            logger.error(f"❌ LSTM System timed out after {duration:.2f}s")
            self.log_execution("LSTM", False, duration, "Timeout after 600s")
            return False
        except Exception as e:
            duration = time.time() - start_time
            logger.error(f"❌ LSTM System error: {e}")
            self.log_execution("LSTM", False, duration, f"Error: {str(e)}")
            return False

    def run_vertexai_predictions(self):
        """VertexAI予測システム実行"""
        logger.info("🤖 Starting VertexAI Prediction System")
        start_time = time.time()

        try:
            result = subprocess.run([
                sys.executable, self.vertexai_script
            ], capture_output=True, text=True, timeout=600)

            duration = time.time() - start_time
            success = result.returncode == 0

            if success:
                logger.info(f"✅ VertexAI System completed successfully in {duration:.2f}s")
                self.log_execution("VertexAI", True, duration, "Completed successfully")
            else:
                logger.error(f"❌ VertexAI System failed: {result.stderr}")
                self.log_execution("VertexAI", False, duration, f"Failed: {result.stderr[:200]}")

            return success

        except subprocess.TimeoutExpired:
            duration = time.time() - start_time
            logger.error(f"❌ VertexAI System timed out after {duration:.2f}s")
            self.log_execution("VertexAI", False, duration, "Timeout after 600s")
            return False
        except Exception as e:
            duration = time.time() - start_time
            logger.error(f"❌ VertexAI System error: {e}")
            self.log_execution("VertexAI", False, duration, f"Error: {str(e)}")
            return False

    def run_both_systems_parallel(self):
        """両システム並列実行"""
        logger.info("🚀 Starting Both Prediction Systems in Parallel")
        start_time = time.time()

        # 並列実行用スレッド
        lstm_thread = threading.Thread(target=self.run_lstm_predictions)
        vertexai_thread = threading.Thread(target=self.run_vertexai_predictions)

        # 結果格納用
        results = {'lstm': False, 'vertexai': False}

        def lstm_wrapper():
            results['lstm'] = self.run_lstm_predictions()

        def vertexai_wrapper():
            results['vertexai'] = self.run_vertexai_predictions()

        # スレッド再定義
        lstm_thread = threading.Thread(target=lstm_wrapper)
        vertexai_thread = threading.Thread(target=vertexai_wrapper)

        # 並列実行
        lstm_thread.start()
        vertexai_thread.start()

        # 完了待機
        lstm_thread.join()
        vertexai_thread.join()

        duration = time.time() - start_time
        success_count = sum(results.values())

        logger.info("=" * 60)
        logger.info("🎉 Parallel Prediction Execution Complete")
        logger.info(f"✅ LSTM Success: {results['lstm']}")
        logger.info(f"✅ VertexAI Success: {results['vertexai']}")
        logger.info(f"⏱️ Total Duration: {duration:.2f}s")
        logger.info(f"📊 Success Rate: {success_count}/2 ({success_count/2*100:.1f}%)")
        logger.info("=" * 60)

        return results

    def run_both_systems_sequential(self):
        """両システム順次実行"""
        logger.info("🚀 Starting Both Prediction Systems Sequentially")
        start_time = time.time()

        # LSTM実行
        lstm_success = self.run_lstm_predictions()

        # 短い間隔をあける
        time.sleep(5)

        # VertexAI実行
        vertexai_success = self.run_vertexai_predictions()

        duration = time.time() - start_time
        success_count = sum([lstm_success, vertexai_success])

        logger.info("=" * 60)
        logger.info("🎉 Sequential Prediction Execution Complete")
        logger.info(f"✅ LSTM Success: {lstm_success}")
        logger.info(f"✅ VertexAI Success: {vertexai_success}")
        logger.info(f"⏱️ Total Duration: {duration:.2f}s")
        logger.info(f"📊 Success Rate: {success_count}/2 ({success_count/2*100:.1f}%)")
        logger.info("=" * 60)

        return {'lstm': lstm_success, 'vertexai': vertexai_success}

    def get_execution_summary(self, hours=24):
        """実行サマリー取得"""
        cutoff_time = datetime.now() - timedelta(hours=hours)
        recent_logs = [log for log in self.execution_log if log['timestamp'] > cutoff_time]

        if not recent_logs:
            return "No recent executions found."

        lstm_logs = [log for log in recent_logs if log['system'] == 'LSTM']
        vertexai_logs = [log for log in recent_logs if log['system'] == 'VertexAI']

        lstm_success_rate = sum(1 for log in lstm_logs if log['success']) / max(1, len(lstm_logs)) * 100
        vertexai_success_rate = sum(1 for log in vertexai_logs if log['success']) / max(1, len(vertexai_logs)) * 100

        avg_lstm_duration = sum(log['duration_seconds'] for log in lstm_logs) / max(1, len(lstm_logs))
        avg_vertexai_duration = sum(log['duration_seconds'] for log in vertexai_logs) / max(1, len(vertexai_logs))

        summary = f"""
📊 Execution Summary (Last {hours} hours)

🧠 LSTM System:
  • Executions: {len(lstm_logs)}
  • Success Rate: {lstm_success_rate:.1f}%
  • Avg Duration: {avg_lstm_duration:.1f}s

🤖 VertexAI System:
  • Executions: {len(vertexai_logs)}
  • Success Rate: {vertexai_success_rate:.1f}%
  • Avg Duration: {avg_vertexai_duration:.1f}s

📈 Overall:
  • Total Executions: {len(recent_logs)}
  • Combined Success Rate: {(lstm_success_rate + vertexai_success_rate) / 2:.1f}%
"""
        return summary

    def setup_schedule(self):
        """スケジュール設定"""
        # 毎2時間実行（並列）
        schedule.every(2).hours.do(self.run_both_systems_parallel)

        # 毎日6時に順次実行（確実性重視）
        schedule.every().day.at("06:00").do(self.run_both_systems_sequential)

        logger.info("📅 Schedule configured:")
        logger.info("  🔄 Parallel execution: Every 2 hours")
        logger.info("  📋 Sequential execution: Daily at 6:00 AM")

    def run_scheduler(self):
        """スケジューラー実行"""
        logger.info("🕒 Starting Prediction Scheduler")

        while True:
            try:
                schedule.run_pending()
                time.sleep(60)  # 1分間隔でチェック
            except KeyboardInterrupt:
                logger.info("🛑 Scheduler stopped by user")
                break
            except Exception as e:
                logger.error(f"❌ Scheduler error: {e}")
                time.sleep(300)  # エラー時は5分待機

def main():
    """メイン実行"""
    orchestrator = PredictionOrchestrator()

    if len(sys.argv) > 1:
        command = sys.argv[1].lower()

        if command == "lstm":
            orchestrator.run_lstm_predictions()
        elif command == "vertexai":
            orchestrator.run_vertexai_predictions()
        elif command == "parallel":
            orchestrator.run_both_systems_parallel()
        elif command == "sequential":
            orchestrator.run_both_systems_sequential()
        elif command == "schedule":
            orchestrator.setup_schedule()
            orchestrator.run_scheduler()
        elif command == "summary":
            print(orchestrator.get_execution_summary())
        else:
            print("Usage: python unified_prediction_orchestrator.py [lstm|vertexai|parallel|sequential|schedule|summary]")
    else:
        # デフォルト: 並列実行
        orchestrator.run_both_systems_parallel()

if __name__ == "__main__":
    main()