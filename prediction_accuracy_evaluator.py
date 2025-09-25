#!/usr/bin/env python3
"""
MiraiKakaku予測精度評価システム
MAE、RMSE、MAPE等の指標を用いた予測モデルの性能評価
"""

import os
import sys
import logging
import psycopg2
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import json
from dataclasses import dataclass, asdict

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - PredictionEvaluator - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@dataclass
class AccuracyMetrics:
    """精度指標データクラス"""
    symbol: str
    evaluation_date: datetime
    mae: float  # Mean Absolute Error
    rmse: float  # Root Mean Squared Error
    mape: float  # Mean Absolute Percentage Error
    r2_score: float  # R-squared Score
    directional_accuracy: float  # 方向性精度（上昇/下降の的中率）
    sample_size: int
    confidence_level: float  # 予測の信頼度


class PredictionAccuracyEvaluator:
    """予測精度評価クラス"""

    def __init__(self):
        self.db_config = {
            'host': os.getenv('DB_HOST', '34.173.9.214'),
            'database': os.getenv('DB_NAME', 'miraikakaku'),
            'user': os.getenv('DB_USER', 'postgres'),
            'password': os.getenv('DB_PASSWORD', 'os.getenv('DB_PASSWORD', '')'),
            'port': int(os.getenv('DB_PORT', '5432'))
        }

        # 精度閾値の設定
        self.thresholds = {
            'excellent': {'mae': 2.0, 'mape': 2.0, 'r2': 0.9},
            'good': {'mae': 5.0, 'mape': 5.0, 'r2': 0.7},
            'acceptable': {'mae': 10.0, 'mape': 10.0, 'r2': 0.5},
            'poor': {'mae': float('inf'), 'mape': float('inf'), 'r2': 0.0}
        }

    def get_db_connection(self):
        """データベース接続"""
        return psycopg2.connect(**self.db_config)

    def calculate_mae(self, actual: np.array, predicted: np.array) -> float:
        """Mean Absolute Error計算"""
        return np.mean(np.abs(actual - predicted))

    def calculate_rmse(self, actual: np.array, predicted: np.array) -> float:
        """Root Mean Squared Error計算"""
        return np.sqrt(np.mean((actual - predicted) ** 2))

    def calculate_mape(self, actual: np.array, predicted: np.array) -> float:
        """Mean Absolute Percentage Error計算"""
        # ゼロ除算を避ける
        mask = actual != 0
        if not mask.any():
            return 100.0
        return np.mean(np.abs((actual[mask] - predicted[mask]) / actual[mask])) * 100

    def calculate_r2_score(self, actual: np.array, predicted: np.array) -> float:
        """R-squared Score計算"""
        if len(actual) < 2:
            return 0.0

        ss_res = np.sum((actual - predicted) ** 2)
        ss_tot = np.sum((actual - np.mean(actual)) ** 2)

        if ss_tot == 0:
            return 0.0

        return 1 - (ss_res / ss_tot)

    def calculate_directional_accuracy(self, actual: np.array, predicted: np.array,
                                      previous: np.array) -> float:
        """方向性精度計算（価格の上昇/下降の的中率）"""
        actual_direction = np.sign(actual - previous)
        predicted_direction = np.sign(predicted - previous)
        correct = np.sum(actual_direction == predicted_direction)
        return (correct / len(actual)) * 100 if len(actual) > 0 else 0.0

    def evaluate_symbol(self, symbol: str, days_back: int = 30) -> Optional[AccuracyMetrics]:
        """個別銘柄の予測精度評価"""
        conn = self.get_db_connection()
        try:
            with conn.cursor() as cursor:
                # 予測データと実際のデータを取得
                cursor.execute("""
                    SELECT
                        p.prediction_date::date as date,
                        p.predicted_price,
                        sp.close_price as actual_price,
                        LAG(sp.close_price) OVER (ORDER BY p.prediction_date) as previous_price
                    FROM stock_predictions p
                    INNER JOIN stock_prices sp
                        ON p.symbol = sp.symbol
                        AND p.prediction_date::date = sp.date
                    WHERE p.symbol = %s
                        AND p.prediction_date >= CURRENT_DATE - INTERVAL '%s days'
                        AND sp.close_price IS NOT NULL
                        AND p.predicted_price IS NOT NULL
                    ORDER BY p.prediction_date
                """, (symbol, days_back))

                results = cursor.fetchall()

                if len(results) < 2:
                    logger.warning(f"不十分なデータ: {symbol} ({len(results)}件)")
                    return None

                # データをNumPy配列に変換
                dates = [r[0] for r in results]
                predicted = np.array([float(r[1]) for r in results])
                actual = np.array([float(r[2]) for r in results])
                previous = np.array([float(r[3]) if r[3] else actual[i-1]
                                   for i, r in enumerate(results)])

                # 各種精度指標を計算
                mae = self.calculate_mae(actual, predicted)
                rmse = self.calculate_rmse(actual, predicted)
                mape = self.calculate_mape(actual, predicted)
                r2 = self.calculate_r2_score(actual, predicted)
                directional = self.calculate_directional_accuracy(actual, predicted, previous)

                # 信頼度スコアを計算
                confidence = self.calculate_confidence_score(mae, mape, r2)

                metrics = AccuracyMetrics(
                    symbol=symbol,
                    evaluation_date=datetime.now(),
                    mae=round(mae, 4),
                    rmse=round(rmse, 4),
                    mape=round(mape, 2),
                    r2_score=round(r2, 4),
                    directional_accuracy=round(directional, 2),
                    sample_size=len(results),
                    confidence_level=round(confidence, 2)
                )

                # 結果をデータベースに保存
                self.save_metrics_to_db(cursor, metrics)
                conn.commit()

                logger.info(f"✅ {symbol} 評価完了: MAE={mae:.2f}, MAPE={mape:.1f}%, R²={r2:.3f}")

                return metrics

        except Exception as e:
            logger.error(f"❌ 評価エラー {symbol}: {e}")
            return None
        finally:
            conn.close()

    def calculate_confidence_score(self, mae: float, mape: float, r2: float) -> float:
        """総合的な信頼度スコアを計算（0-100）"""
        # 各指標のスコアを計算
        mae_score = max(0, 100 - mae * 5)  # MAEが低いほど高スコア
        mape_score = max(0, 100 - mape * 2)  # MAPEが低いほど高スコア
        r2_score = r2 * 100  # R²は0-1なので100倍

        # 加重平均
        weights = {'mae': 0.3, 'mape': 0.4, 'r2': 0.3}
        confidence = (
            mae_score * weights['mae'] +
            mape_score * weights['mape'] +
            r2_score * weights['r2']
        )

        return min(100, max(0, confidence))

    def save_metrics_to_db(self, cursor, metrics: AccuracyMetrics):
        """精度評価結果をデータベースに保存"""
        # prediction_accuracyテーブルが存在しない場合は作成
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS prediction_accuracy (
                id SERIAL PRIMARY KEY,
                symbol VARCHAR(20) NOT NULL,
                evaluation_date TIMESTAMP NOT NULL,
                mae FLOAT,
                rmse FLOAT,
                mape FLOAT,
                r2_score FLOAT,
                directional_accuracy FLOAT,
                sample_size INTEGER,
                confidence_level FLOAT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(symbol, evaluation_date)
            )
        """)

        # メトリクスを挿入
        cursor.execute("""
            INSERT INTO prediction_accuracy
            (symbol, evaluation_date, mae, rmse, mape, r2_score,
             directional_accuracy, sample_size, confidence_level)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (symbol, evaluation_date) DO UPDATE SET
                mae = EXCLUDED.mae,
                rmse = EXCLUDED.rmse,
                mape = EXCLUDED.mape,
                r2_score = EXCLUDED.r2_score,
                directional_accuracy = EXCLUDED.directional_accuracy,
                sample_size = EXCLUDED.sample_size,
                confidence_level = EXCLUDED.confidence_level
        """, (
            metrics.symbol, metrics.evaluation_date,
            float(metrics.mae), float(metrics.rmse), float(metrics.mape),
            float(metrics.r2_score), float(metrics.directional_accuracy),
            int(metrics.sample_size), float(metrics.confidence_level)
        ))

    def evaluate_all_symbols(self, limit: int = 100) -> Dict[str, AccuracyMetrics]:
        """全銘柄の精度評価"""
        conn = self.get_db_connection()
        results = {}

        try:
            with conn.cursor() as cursor:
                # アクティブな銘柄を取得
                cursor.execute("""
                    SELECT DISTINCT s.symbol
                    FROM stock_predictions s
                    INNER JOIN stock_master m ON s.symbol = m.symbol
                    WHERE m.is_active = true
                        AND s.prediction_date >= CURRENT_DATE - INTERVAL '30 days'
                    LIMIT %s
                """, (limit,))

                symbols = [row[0] for row in cursor.fetchall()]

            logger.info(f"📊 {len(symbols)}銘柄の精度評価を開始")

            for symbol in symbols:
                metrics = self.evaluate_symbol(symbol)
                if metrics:
                    results[symbol] = metrics

            # サマリーレポート生成
            self.generate_summary_report(results)

            return results

        except Exception as e:
            logger.error(f"❌ 全体評価エラー: {e}")
            return results
        finally:
            conn.close()

    def generate_summary_report(self, results: Dict[str, AccuracyMetrics]) -> Dict:
        """評価結果のサマリーレポート生成"""
        if not results:
            return {}

        # 統計情報を集計
        all_metrics = list(results.values())

        summary = {
            'evaluation_date': datetime.now().isoformat(),
            'total_symbols': len(results),
            'average_metrics': {
                'mae': np.mean([m.mae for m in all_metrics]),
                'rmse': np.mean([m.rmse for m in all_metrics]),
                'mape': np.mean([m.mape for m in all_metrics]),
                'r2_score': np.mean([m.r2_score for m in all_metrics]),
                'directional_accuracy': np.mean([m.directional_accuracy for m in all_metrics])
            },
            'performance_distribution': {
                'excellent': 0,
                'good': 0,
                'acceptable': 0,
                'poor': 0
            },
            'top_performers': [],
            'improvement_needed': []
        }

        # パフォーマンス分類
        for symbol, metrics in results.items():
            if metrics.mae <= self.thresholds['excellent']['mae']:
                summary['performance_distribution']['excellent'] += 1
                summary['top_performers'].append({
                    'symbol': symbol,
                    'mae': metrics.mae,
                    'confidence': metrics.confidence_level
                })
            elif metrics.mae <= self.thresholds['good']['mae']:
                summary['performance_distribution']['good'] += 1
            elif metrics.mae <= self.thresholds['acceptable']['mae']:
                summary['performance_distribution']['acceptable'] += 1
            else:
                summary['performance_distribution']['poor'] += 1
                summary['improvement_needed'].append({
                    'symbol': symbol,
                    'mae': metrics.mae,
                    'mape': metrics.mape
                })

        # 上位/下位を制限
        summary['top_performers'] = sorted(
            summary['top_performers'],
            key=lambda x: x['confidence'],
            reverse=True
        )[:10]

        summary['improvement_needed'] = sorted(
            summary['improvement_needed'],
            key=lambda x: x['mae'],
            reverse=True
        )[:10]

        # レポートを保存
        report_path = f"prediction_accuracy_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_path, 'w') as f:
            json.dump(summary, f, indent=2, default=str)

        logger.info(f"""
📊 予測精度評価レポート
========================
評価銘柄数: {summary['total_symbols']}
平均MAE: {summary['average_metrics']['mae']:.2f}
平均MAPE: {summary['average_metrics']['mape']:.1f}%
平均R²: {summary['average_metrics']['r2_score']:.3f}
方向性精度: {summary['average_metrics']['directional_accuracy']:.1f}%

パフォーマンス分布:
- 優秀: {summary['performance_distribution']['excellent']}銘柄
- 良好: {summary['performance_distribution']['good']}銘柄
- 許容: {summary['performance_distribution']['acceptable']}銘柄
- 改善要: {summary['performance_distribution']['poor']}銘柄

レポート保存先: {report_path}
        """)

        return summary

    def create_realtime_dashboard(self):
        """リアルタイム精度ダッシュボード用データ生成"""
        conn = self.get_db_connection()
        try:
            with conn.cursor() as cursor:
                # 直近24時間の精度推移
                cursor.execute("""
                    SELECT
                        DATE_TRUNC('hour', evaluation_date) as hour,
                        AVG(mae) as avg_mae,
                        AVG(mape) as avg_mape,
                        AVG(r2_score) as avg_r2,
                        AVG(confidence_level) as avg_confidence,
                        COUNT(DISTINCT symbol) as symbol_count
                    FROM prediction_accuracy
                    WHERE evaluation_date >= NOW() - INTERVAL '24 hours'
                    GROUP BY hour
                    ORDER BY hour DESC
                """)

                hourly_data = cursor.fetchall()

                # 銘柄別ランキング
                cursor.execute("""
                    SELECT
                        symbol,
                        mae,
                        mape,
                        r2_score,
                        confidence_level
                    FROM prediction_accuracy
                    WHERE evaluation_date >= NOW() - INTERVAL '1 day'
                    ORDER BY confidence_level DESC
                    LIMIT 20
                """)

                top_symbols = cursor.fetchall()

                dashboard_data = {
                    'timestamp': datetime.now().isoformat(),
                    'hourly_trend': [
                        {
                            'hour': row[0].isoformat(),
                            'avg_mae': float(row[1]) if row[1] else 0,
                            'avg_mape': float(row[2]) if row[2] else 0,
                            'avg_r2': float(row[3]) if row[3] else 0,
                            'avg_confidence': float(row[4]) if row[4] else 0,
                            'symbol_count': row[5]
                        }
                        for row in hourly_data
                    ],
                    'top_performers': [
                        {
                            'symbol': row[0],
                            'mae': float(row[1]),
                            'mape': float(row[2]),
                            'r2_score': float(row[3]),
                            'confidence': float(row[4])
                        }
                        for row in top_symbols
                    ]
                }

                return dashboard_data

        except Exception as e:
            logger.error(f"ダッシュボードデータ生成エラー: {e}")
            return {}
        finally:
            conn.close()


def main():
    """メイン処理"""
    evaluator = PredictionAccuracyEvaluator()

    if len(sys.argv) > 1:
        if sys.argv[1] == "evaluate-all":
            # 全銘柄評価
            logger.info("🚀 全銘柄の予測精度評価を開始")
            results = evaluator.evaluate_all_symbols(limit=100)
            logger.info(f"✅ {len(results)}銘柄の評価完了")

        elif sys.argv[1] == "dashboard":
            # ダッシュボードデータ生成
            dashboard = evaluator.create_realtime_dashboard()
            print(json.dumps(dashboard, indent=2, default=str))

        else:
            # 個別銘柄評価
            symbol = sys.argv[1]
            logger.info(f"🎯 {symbol} の予測精度評価")
            metrics = evaluator.evaluate_symbol(symbol)
            if metrics:
                print(json.dumps(asdict(metrics), indent=2, default=str))
    else:
        # デフォルト: 主要銘柄の評価
        for symbol in ['AAPL', 'GOOGL', 'MSFT', 'TSLA', 'NVDA']:
            metrics = evaluator.evaluate_symbol(symbol)
            if metrics:
                print(f"{symbol}: MAE={metrics.mae:.2f}, MAPE={metrics.mape:.1f}%, "
                      f"R²={metrics.r2_score:.3f}, 信頼度={metrics.confidence_level:.1f}%")


if __name__ == "__main__":
    main()