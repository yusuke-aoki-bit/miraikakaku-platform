import schedule
import time
import logging
from datetime import datetime
from services.advanced_ml_pipeline import AdvancedMLPipeline
from services.vertex_ai_service import VertexAIService
from database.database import get_db_session
from database.models import StockMaster
import threading
import asyncio

logger = logging.getLogger(__name__)


class MLPipelineScheduler:
    def __init__(self):
        self.ml_pipeline = AdvancedMLPipeline()
        self.vertex_ai_service = VertexAIService()
        self.db_session = get_db_session()
        self.is_running = False

    def start_scheduler(self):
        """スケジューラーを開始"""
        if self.is_running:
            logger.warning("スケジューラーは既に実行中です")
            return

        logger.info("MLパイプラインスケジューラー開始")
        self.is_running = True

        # スケジュール設定
        self._setup_schedules()

        # スケジューラーを別スレッドで実行
        scheduler_thread = threading.Thread(target=self._run_scheduler, daemon=True)
        scheduler_thread.start()

    def _setup_schedules(self):
        """スケジュール設定"""
        # 毎日午前2時: フルMLパイプライン実行
        schedule.every().day.at("02:00").do(self._run_daily_ml_pipeline)

        # 平日の市場開始前（午前8時）: 日次予測実行
        schedule.every().monday.at("08:00").do(self._run_daily_predictions)
        schedule.every().tuesday.at("08:00").do(self._run_daily_predictions)
        schedule.every().wednesday.at("08:00").do(self._run_daily_predictions)
        schedule.every().thursday.at("08:00").do(self._run_daily_predictions)
        schedule.every().friday.at("08:00").do(self._run_daily_predictions)

        # 毎時間: リアルタイム予測更新
        schedule.every().hour.do(self._run_hourly_predictions)

        # 毎週日曜日午前1時: モデル性能評価とクリーンアップ
        schedule.every().sunday.at("01:00").do(self._run_weekly_maintenance)

        # 毎月1日午前0時: Vertex AI訓練データセット更新
        schedule.every().month.do(self._run_monthly_vertex_ai_training)

    def _run_scheduler(self):
        """スケジューラーのメインループ"""
        logger.info("スケジューラーループ開始")

        while self.is_running:
            try:
                schedule.run_pending()
                time.sleep(60)  # 1分間隔でチェック
            except Exception as e:
                logger.error(f"スケジューラーエラー: {e}")
                time.sleep(300)  # エラー時は5分待機

    def _run_daily_ml_pipeline(self):
        """日次MLパイプライン実行"""
        try:
            logger.info("日次MLパイプライン実行開始")

            # アクティブな銘柄を取得
            active_symbols = self._get_active_symbols()

            # 各銘柄でMLパイプラインを実行
            for symbol in active_symbols:
                try:
                    # LSTMモデルで予測
                    lstm_result = self.ml_pipeline.predict_with_lstm(symbol)

                    # Prophetモデルで予測
                    prophet_result = self.ml_pipeline.predict_with_prophet(symbol)

                    # アンサンブル予測
                    ensemble_result = self.ml_pipeline.create_ensemble_prediction(
                        lstm_prediction=lstm_result, prophet_prediction=prophet_result
                    )

                    logger.info(
                        f"日次予測完了: {symbol} -> ${ensemble_result.get('predicted_price', 0):.2f}"
                    )

                except Exception as e:
                    logger.error(f"日次予測エラー {symbol}: {e}")

            logger.info("日次MLパイプライン実行完了")

        except Exception as e:
            logger.error(f"日次MLパイプラインエラー: {e}")

    def _run_daily_predictions(self):
        """日次予測実行"""
        try:
            logger.info("日次予測実行開始")

            # 主要銘柄で予測実行
            major_symbols = ["AAPL", "GOOGL", "MSFT", "TSLA", "AMZN", "NVDA", "META"]

            # Vertex AI バッチ予測実行
            vertex_results = self.vertex_ai_service.run_batch_prediction(major_symbols)

            # ローカルMLモデルでも予測実行
            for symbol in major_symbols[:3]:  # リソース制限により最初の3銘柄のみ
                lstm_result = self.ml_pipeline.predict_with_lstm(symbol)

            logger.info(
                f"日次予測完了: Vertex AI {vertex_results.get('successful', 0)} 件成功"
            )

        except Exception as e:
            logger.error(f"日次予測エラー: {e}")

    def _run_hourly_predictions(self):
        """時間毎予測実行"""
        try:
            logger.info("時間毎予測実行開始")

            # 主要5銘柄のみで軽量予測
            top_symbols = ["AAPL", "GOOGL", "MSFT", "TSLA", "AMZN"]

            for symbol in top_symbols:
                try:
                    # 簡単な予測のみ実行
                    result = self.ml_pipeline.predict_with_lstm(symbol, mode="fast")

                except Exception as e:
                    logger.error(f"時間毎予測エラー {symbol}: {e}")

            logger.info("時間毎予測完了")

        except Exception as e:
            logger.error(f"時間毎予測エラー: {e}")

    def _run_weekly_maintenance(self):
        """週次メンテナンス実行"""
        try:
            logger.info("週次メンテナンス開始")

            # モデル性能監視
            performance_results = []
            for model_name in ["lstm_v1", "prophet_v1", "vertex_ai_automl"]:
                performance = self.vertex_ai_service.monitor_model_performance(
                    model_name, days=7
                )
                performance_results.append(performance)

            # 古いモデルクリーンアップ
            cleaned_count = self.vertex_ai_service.cleanup_old_models(keep_latest=3)

            # 性能レポート生成
            self._generate_weekly_report(performance_results)

            logger.info(
                f"週次メンテナンス完了: {cleaned_count} 個のモデルクリーンアップ"
            )

        except Exception as e:
            logger.error(f"週次メンテナンスエラー: {e}")

    def _run_monthly_vertex_ai_training(self):
        """月次Vertex AI訓練実行"""
        try:
            logger.info("月次Vertex AI訓練開始")

            # 全アクティブ銘柄でデータセット作成
            active_symbols = self._get_active_symbols()

            # 大規模データセット作成（過去1年分）
            dataset_path = self.vertex_ai_service.create_training_dataset(
                symbols=active_symbols, lookback_days=365
            )

            if dataset_path:
                # AutoMLモデル作成
                model_resource = self.vertex_ai_service.create_automl_tabular_model(
                    dataset_path
                )

                if model_resource:
                    # モデルをエンドポイントにデプロイ
                    endpoint = self.vertex_ai_service.deploy_model_to_endpoint(
                        model_resource
                    )
                    logger.info(f"新しいVertex AIモデルデプロイ完了: {endpoint}")

            logger.info("月次Vertex AI訓練完了")

        except Exception as e:
            logger.error(f"月次Vertex AI訓練エラー: {e}")

    def _get_active_symbols(self) -> list:
        """アクティブな銘柄リストを取得"""
        try:
            stocks = (
                self.db_session.query(StockMaster)
                .filter(StockMaster.is_active == True)
                .limit(50)
                .all()
            )  # 最大50銘柄

            return [stock.symbol for stock in stocks]

        except Exception as e:
            logger.error(f"アクティブ銘柄取得エラー: {e}")
            return ["AAPL", "GOOGL", "MSFT", "TSLA", "AMZN"]  # フォールバック

    def _generate_weekly_report(self, performance_results: list):
        """週次パフォーマンスレポート生成"""
        try:
            report = {
                "report_date": datetime.utcnow().isoformat(),
                "period": "weekly",
                "models": performance_results,
                "summary": {
                    "total_models": len(performance_results),
                    "avg_accuracy": (
                        sum(p.get("avg_accuracy", 0) for p in performance_results)
                        / len(performance_results)
                        if performance_results
                        else 0
                    ),
                    "total_predictions": sum(
                        p.get("total_predictions", 0) for p in performance_results
                    ),
                },
            }

            logger.info(f"週次レポート生成: {report['summary']}")

        except Exception as e:
            logger.error(f"週次レポート生成エラー: {e}")

    def stop_scheduler(self):
        """スケジューラー停止"""
        self.is_running = False
        schedule.clear()
        logger.info("MLパイプラインスケジューラー停止")


# スケジューラーインスタンス
ml_scheduler = MLPipelineScheduler()

if __name__ == "__main__":
    ml_scheduler.start_scheduler()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        logger.info("キーボード割り込み検出")
        ml_scheduler.stop_scheduler()
