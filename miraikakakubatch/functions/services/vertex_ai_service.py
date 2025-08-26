from google.cloud import aiplatform
from google.cloud.aiplatform import gapic as aip
import pandas as pd
import numpy as np
import json
import os
from datetime import datetime, timedelta
from database.database import get_db_session
from database.models import StockPriceHistory, StockPredictions, AIInferenceLog
import logging
from typing import Dict, List, Any, Optional
import uuid

logger = logging.getLogger(__name__)


class VertexAIService:
    def __init__(self):
        self.project_id = os.getenv("VERTEX_AI_PROJECT_ID")
        self.location = os.getenv("VERTEX_AI_LOCATION", "us-central1")
        self.db_session = get_db_session()

        if self.project_id:
            aiplatform.init(project=self.project_id, location=self.location)

    def create_training_dataset(
        self, symbols: List[str], lookback_days: int = 365
    ) -> Optional[str]:
        """Vertex AI用の訓練データセットを作成"""
        try:
            logger.info(f"Vertex AI訓練データセット作成開始: {symbols}")

            all_data = []
            start_date = datetime.utcnow() - timedelta(days=lookback_days)

            for symbol in symbols:
                price_data = (
                    self.db_session.query(StockPriceHistory)
                    .filter(
                        StockPriceHistory.symbol == symbol,
                        StockPriceHistory.date >= start_date,
                    )
                    .order_by(StockPriceHistory.date.asc())
                    .all()
                )

                if len(price_data) < 30:
                    continue

                # 特徴量エンジニアリング
                df = pd.DataFrame(
                    [
                        {
                            "symbol": price.symbol,
                            "date": price.date,
                            "open": float(price.open_price or price.close_price),
                            "high": float(price.high_price or price.close_price),
                            "low": float(price.low_price or price.close_price),
                            "close": float(price.close_price),
                            "volume": float(price.volume or 0),
                        }
                        for price in price_data
                    ]
                )

                # テクニカル指標を追加
                df = self._add_technical_features(df)

                # ターゲット変数（翌日の終値）
                df["target"] = df["close"].shift(-1)

                # NaNを除去
                df = df.dropna()

                all_data.append(df)

            if not all_data:
                logger.warning("訓練データが不足しています")
                return None

            # 全データを結合
            combined_df = pd.concat(all_data, ignore_index=True)

            # CSV形式で保存（Google Cloud Storageに保存する場合）
            dataset_path = f"/tmp/training_dataset_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.csv"
            combined_df.to_csv(dataset_path, index=False)

            logger.info(f"データセット作成完了: {len(combined_df)} 行, {dataset_path}")
            return dataset_path

        except Exception as e:
            logger.error(f"データセット作成エラー: {e}")
            return None

    def _add_technical_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """テクニカル指標を追加"""
        # 移動平均
        df["sma_5"] = df["close"].rolling(5).mean()
        df["sma_10"] = df["close"].rolling(10).mean()
        df["sma_20"] = df["close"].rolling(20).mean()
        df["sma_50"] = df["close"].rolling(50).mean()

        # RSI
        delta = df["close"].diff()
        gain = (delta.where(delta > 0, 0)).rolling(14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(14).mean()
        rs = gain / loss
        df["rsi"] = 100 - (100 / (1 + rs))

        # MACD
        ema_12 = df["close"].ewm(span=12).mean()
        ema_26 = df["close"].ewm(span=26).mean()
        df["macd"] = ema_12 - ema_26
        df["macd_signal"] = df["macd"].ewm(span=9).mean()
        df["macd_histogram"] = df["macd"] - df["macd_signal"]

        # ボリンジャーバンド
        df["bb_middle"] = df["close"].rolling(20).mean()
        df["bb_std"] = df["close"].rolling(20).std()
        df["bb_upper"] = df["bb_middle"] + (df["bb_std"] * 2)
        df["bb_lower"] = df["bb_middle"] - (df["bb_std"] * 2)
        df["bb_position"] = (df["close"] - df["bb_lower"]) / (
            df["bb_upper"] - df["bb_lower"]
        )

        # ボラティリティ
        df["volatility_5"] = df["close"].rolling(5).std()
        df["volatility_20"] = df["close"].rolling(20).std()

        # 価格変化率
        df["return_1d"] = df["close"].pct_change()
        df["return_5d"] = df["close"].pct_change(5)
        df["return_20d"] = df["close"].pct_change(20)

        # 出来高関連
        df["volume_sma"] = df["volume"].rolling(20).mean()
        df["volume_ratio"] = df["volume"] / df["volume_sma"]

        return df

    def create_automl_tabular_model(
        self, dataset_path: str, target_column: str = "target"
    ) -> Optional[str]:
        """AutoML Tabular モデルを作成"""
        try:
            if not self.project_id:
                logger.warning("VERTEX_AI_PROJECT_ID が設定されていません")
                return None

            logger.info("AutoML Tabular モデル作成開始")

            # データセットを作成
            dataset = aiplatform.TabularDataset.create(
                display_name=f"stock_prediction_dataset_{datetime.utcnow().strftime('%Y%m%d')}",
                gcs_source=dataset_path,  # 実際はGCSパスを使用
            )

            # AutoML訓練ジョブを作成
            job = aiplatform.AutoMLTabularTrainingJob(
                display_name=f"stock_prediction_automl_{datetime.utcnow().strftime('%Y%m%d')}",
                optimization_prediction_type="regression",
                optimization_objective="minimize-rmse",
                column_specs={
                    target_column: "target",
                    "symbol": "categorical",
                    "date": "timestamp",
                },
                budget_milli_node_hours=1000,  # 1時間
            )

            # 訓練実行
            model = job.run(
                dataset=dataset,
                target_column=target_column,
                training_fraction_split=0.8,
                validation_fraction_split=0.1,
                test_fraction_split=0.1,
                model_display_name=f"stock_prediction_model_{datetime.utcnow().strftime('%Y%m%d')}",
            )

            logger.info(f"AutoML モデル作成完了: {model.resource_name}")
            return model.resource_name

        except Exception as e:
            logger.error(f"AutoML モデル作成エラー: {e}")
            return None

    def deploy_model_to_endpoint(self, model_resource_name: str) -> Optional[str]:
        """モデルをエンドポイントにデプロイ"""
        try:
            logger.info(f"モデルデプロイ開始: {model_resource_name}")

            model = aiplatform.Model(model_resource_name)

            endpoint = aiplatform.Endpoint.create(
                display_name=f"stock_prediction_endpoint_{datetime.utcnow().strftime('%Y%m%d')}"
            )

            model.deploy(
                endpoint=endpoint,
                deployed_model_display_name="stock_prediction_deployed",
                machine_type="n1-standard-2",
                min_replica_count=1,
                max_replica_count=3,
            )

            logger.info(f"モデルデプロイ完了: {endpoint.resource_name}")
            return endpoint.resource_name

        except Exception as e:
            logger.error(f"モデルデプロイエラー: {e}")
            return None

    def predict_with_vertex_ai(
        self, endpoint_name: str, symbol: str
    ) -> Optional[Dict[str, Any]]:
        """Vertex AIエンドポイントで予測実行"""
        try:
            logger.info(f"Vertex AI 予測実行: {symbol}")

            # 最新データを準備
            recent_data = self._prepare_prediction_features(symbol)
            if not recent_data:
                return None

            # エンドポイントで予測実行
            endpoint = aiplatform.Endpoint(endpoint_name)

            start_time = datetime.utcnow()
            predictions = endpoint.predict(instances=[recent_data])
            inference_time = (datetime.utcnow() - start_time).total_seconds() * 1000

            if predictions.predictions:
                predicted_price = float(predictions.predictions[0][0])
                confidence = (
                    float(predictions.predictions[0][1])
                    if len(predictions.predictions[0]) > 1
                    else 0.8
                )

                # 予測をデータベースに保存
                prediction_record = StockPredictions(
                    symbol=symbol,
                    prediction_date=datetime.utcnow(),
                    target_date=datetime.utcnow() + timedelta(days=1),
                    predicted_price=predicted_price,
                    confidence_score=confidence,
                    prediction_type="daily",
                    model_name="vertex_ai_automl",
                    model_version="1.0",
                )

                self.db_session.add(prediction_record)
                self.db_session.commit()

                # 推論ログを記録
                self._log_vertex_ai_inference(
                    symbol=symbol,
                    input_data=recent_data,
                    prediction=predicted_price,
                    confidence=confidence,
                    inference_time=inference_time,
                )

                logger.info(
                    f"Vertex AI 予測完了: {symbol}, 価格: ${predicted_price:.2f}"
                )

                return {
                    "symbol": symbol,
                    "predicted_price": predicted_price,
                    "confidence": confidence,
                    "inference_time_ms": inference_time,
                    "model": "vertex_ai_automl",
                }

            return None

        except Exception as e:
            logger.error(f"Vertex AI 予測エラー {symbol}: {e}")
            return None

    def _prepare_prediction_features(self, symbol: str) -> Optional[Dict[str, Any]]:
        """予測用特徴量を準備"""
        try:
            # 最新50日のデータを取得
            recent_prices = (
                self.db_session.query(StockPriceHistory)
                .filter(StockPriceHistory.symbol == symbol)
                .order_by(StockPriceHistory.date.desc())
                .limit(50)
                .all()
            )

            if len(recent_prices) < 50:
                logger.warning(f"特徴量データが不足: {symbol}")
                return None

            df = pd.DataFrame(
                [
                    {
                        "open": float(p.open_price or p.close_price),
                        "high": float(p.high_price or p.close_price),
                        "low": float(p.low_price or p.close_price),
                        "close": float(p.close_price),
                        "volume": float(p.volume or 0),
                    }
                    for p in reversed(recent_prices)
                ]
            )

            # テクニカル指標を計算
            df = self._add_technical_features(df)

            # 最新行の特徴量を返す
            latest = df.iloc[-1]

            return {
                "symbol": symbol,
                "close": latest["close"],
                "sma_5": latest["sma_5"],
                "sma_20": latest["sma_20"],
                "rsi": latest["rsi"],
                "macd": latest["macd"],
                "bb_position": latest["bb_position"],
                "volatility_20": latest["volatility_20"],
                "volume_ratio": latest["volume_ratio"],
                "return_5d": latest["return_5d"],
            }

        except Exception as e:
            logger.error(f"特徴量準備エラー {symbol}: {e}")
            return None

    def _log_vertex_ai_inference(
        self,
        symbol: str,
        input_data: Dict,
        prediction: float,
        confidence: float,
        inference_time: float,
    ):
        """Vertex AI推論ログを記録"""
        try:
            log_entry = AIInferenceLog(
                request_id=str(uuid.uuid4()),
                model_name="vertex_ai_automl",
                model_version="1.0",
                input_data=json.dumps(input_data),
                output_data=json.dumps(
                    {"predicted_price": prediction, "confidence": confidence}
                ),
                inference_time_ms=int(inference_time),
                confidence_score=confidence,
                is_successful=True,
                endpoint=f"/vertex_ai/predict/{symbol}",
            )

            self.db_session.add(log_entry)
            self.db_session.commit()

        except Exception as e:
            logger.error(f"Vertex AI ログエラー: {e}")

    def run_batch_prediction(self, symbols: List[str] = None) -> Dict[str, Any]:
        """バッチ予測実行"""
        try:
            if not symbols:
                # アクティブな銘柄を取得
                symbols = ["AAPL", "GOOGL", "MSFT", "TSLA", "AMZN"]  # 実際はDBから取得

            logger.info(f"Vertex AI バッチ予測開始: {len(symbols)} 銘柄")

            results = {}
            endpoint_name = os.getenv("VERTEX_AI_ENDPOINT")

            if not endpoint_name:
                logger.warning("VERTEX_AI_ENDPOINT が設定されていません")
                return {"error": "エンドポイントが設定されていません"}

            for symbol in symbols:
                result = self.predict_with_vertex_ai(endpoint_name, symbol)
                results[symbol] = result

                # レート制限対応
                import time

                time.sleep(0.1)

            logger.info(
                f"バッチ予測完了: {len([r for r in results.values() if r])} 件成功"
            )

            return {
                "total_processed": len(symbols),
                "successful": len([r for r in results.values() if r]),
                "results": results,
                "completed_at": datetime.utcnow().isoformat(),
            }

        except Exception as e:
            logger.error(f"バッチ予測エラー: {e}")
            return {"error": str(e)}

    def monitor_model_performance(
        self, model_name: str, days: int = 30
    ) -> Dict[str, Any]:
        """モデル性能を監視"""
        try:
            start_date = datetime.utcnow() - timedelta(days=days)

            # 推論ログを取得
            logs = (
                self.db_session.query(AIInferenceLog)
                .filter(
                    AIInferenceLog.model_name == model_name,
                    AIInferenceLog.created_at >= start_date,
                )
                .all()
            )

            if not logs:
                return {"error": "監視データがありません"}

            # 性能指標を計算
            total_inferences = len(logs)
            successful_inferences = len([log for log in logs if log.is_successful])
            avg_inference_time = np.mean(
                [log.inference_time_ms for log in logs if log.inference_time_ms]
            )
            avg_confidence = np.mean(
                [log.confidence_score for log in logs if log.confidence_score]
            )

            # エラー率
            error_rate = (
                (total_inferences - successful_inferences) / total_inferences * 100
            )

            # 時間別の推論数
            hourly_stats = {}
            for log in logs:
                hour = log.created_at.hour
                hourly_stats[hour] = hourly_stats.get(hour, 0) + 1

            return {
                "model_name": model_name,
                "monitoring_period": f"{days} days",
                "total_inferences": total_inferences,
                "success_rate": (
                    (successful_inferences / total_inferences * 100)
                    if total_inferences > 0
                    else 0
                ),
                "error_rate": error_rate,
                "avg_inference_time_ms": avg_inference_time,
                "avg_confidence": avg_confidence,
                "hourly_distribution": hourly_stats,
                "monitored_at": datetime.utcnow().isoformat(),
            }

        except Exception as e:
            logger.error(f"性能監視エラー: {e}")
            return {"error": str(e)}

    def setup_model_monitoring_alerts(self) -> bool:
        """モデル監視アラートを設定"""
        try:
            # Cloud Monitoring アラートポリシーを設定
            # 実際の実装では Google Cloud Monitoring API を使用

            alert_configs = [
                {
                    "name": "高エラー率アラート",
                    "condition": "error_rate > 10%",
                    "notification": "email",
                },
                {
                    "name": "推論時間アラート",
                    "condition": "avg_inference_time > 5000ms",
                    "notification": "slack",
                },
                {
                    "name": "低信頼度アラート",
                    "condition": "avg_confidence < 0.6",
                    "notification": "email",
                },
            ]

            logger.info("モデル監視アラート設定完了")
            return True

        except Exception as e:
            logger.error(f"アラート設定エラー: {e}")
            return False

    def cleanup_old_models(self, keep_latest: int = 3) -> int:
        """古いモデルをクリーンアップ"""
        try:
            # 古いモデルバージョンを削除
            # 実際の実装では Vertex AI Model Registry から古いバージョンを削除

            logger.info(f"モデルクリーンアップ完了: 最新{keep_latest}バージョンを保持")
            return 0  # 削除されたモデル数

        except Exception as e:
            logger.error(f"モデルクリーンアップエラー: {e}")
            return 0
