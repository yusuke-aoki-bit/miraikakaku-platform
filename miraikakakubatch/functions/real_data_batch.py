#!/usr/bin/env python3
"""
実データ用AI判断根拠・テーマインサイト生成バッチ（同期版）
既存の予測データに基づいて実用的な判断根拠を生成
"""

import sys
import os
import logging
import traceback
import numpy as np
import pandas as pd
import yfinance as yf
from datetime import datetime, timedelta, date
from typing import List, Dict, Optional

# ログ設定
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# パスを追加
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from database.cloud_sql_only import CloudSQLConnection
    from sqlalchemy import text
    from sqlalchemy.exc import IntegrityError
except ImportError as e:
    logger.error(f"インポートエラー: {e}")
    sys.exit(1)


class RealTimeAnalyzer:
    """リアルタイム市場分析エンジン"""

    def __init__(self):
        self.market_sectors = {
            "technology": [
                "AAPL",
                "MSFT",
                "GOOGL",
                "NVDA",
                "AMZN",
                "META",
                "CRM",
                "ADBE",
            ],
            "finance": ["JPM", "BAC", "WFC", "GS", "MS", "V", "MA", "AXP"],
            "healthcare": ["JNJ", "UNH", "PFE", "ABBV", "TMO", "ABT", "DHR", "BMY"],
            "energy": ["XOM", "CVX", "COP", "EOG", "PSX", "VLO", "MPC", "OXY"],
            "consumer": ["TSLA", "HD", "MCD", "SBUX", "NKE", "LOW", "TJX", "COST"],
            "industrial": ["BA", "CAT", "GE", "RTX", "LMT", "UPS", "DE", "MMM"],
            "materials": ["LIN", "APD", "SHW", "ECL", "FCX", "NEM", "DOW", "DD"],
        }

    def get_technical_analysis(self, symbol: str, price_data: List[Dict]) -> Dict:
        """テクニカル分析を実行"""
        try:
            if len(price_data) < 20:
                return {"RSI": 50.0, "trend_strength": 0.0, "volume_ratio": 1.0}

            # 価格データをDataFrameに変換
            df = pd.DataFrame(price_data)
            df["close"] = pd.to_numeric(df["close_price"])
            df["volume"] = pd.to_numeric(df["volume"])

            # RSI計算
            delta = df["close"].diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
            rs = gain / loss
            rsi = 100 - (100 / (1 + rs))

            # トレンド分析
            sma_20 = df["close"].rolling(window=20).mean()
            current_price = df["close"].iloc[-1]
            trend_strength = (current_price - sma_20.iloc[-1]) / sma_20.iloc[-1] * 100

            # ボリューム分析
            avg_volume = df["volume"].rolling(window=20).mean()
            volume_ratio = df["volume"].iloc[-1] / avg_volume.iloc[-1]

            return {
                "RSI": float(rsi.iloc[-1]) if not pd.isna(rsi.iloc[-1]) else 50.0,
                "trend_strength": (
                    float(trend_strength) if not pd.isna(trend_strength) else 0.0
                ),
                "volume_ratio": (
                    float(volume_ratio) if not pd.isna(volume_ratio) else 1.0
                ),
            }

        except Exception as e:
            logger.error(f"Technical analysis error for {symbol}: {e}")
            return {"RSI": 50.0, "trend_strength": 0.0, "volume_ratio": 1.0}

    def get_fundamental_analysis(self, symbol: str) -> Dict:
        """ファンダメンタル分析"""
        try:
            ticker = yf.Ticker(symbol)
            info = ticker.info

            return {
                "pe_ratio": info.get("trailingPE", 0),
                "revenue_growth": info.get("revenueGrowth", 0),
                "earnings_growth": info.get("earningsGrowth", 0),
                "analyst_recommendation": info.get("recommendationMean", 3.0),
            }
        except Exception as e:
            logger.error(f"Fundamental analysis error for {symbol}: {e}")
            return {"pe_ratio": 0, "revenue_growth": 0, "analyst_recommendation": 3.0}

    def generate_decision_factors(
        self, symbol: str, technical: Dict, fundamental: Dict
    ) -> List[Dict]:
        """実データに基づくAI判断根拠生成"""
        factors = []

        # テクニカル要因
        rsi = technical.get("RSI", 50)
        if rsi < 30:
            factors.append(
                {
                    "factor_type": "technical",
                    "factor_name": "RSI過売りシグナル",
                    "description": f"RSI指標が{rsi:.1f}と30を下回り、過売り状態から反発の可能性を示唆",
                    "influence_score": 0.85,
                    "confidence": 0.78,
                }
            )
        elif rsi > 70:
            factors.append(
                {
                    "factor_type": "technical",
                    "factor_name": "RSI過買いシグナル",
                    "description": f"RSI指標が{rsi:.1f}と70を上回り、過買い状態で調整の可能性",
                    "influence_score": 0.82,
                    "confidence": 0.75,
                }
            )

        # トレンド要因
        trend_strength = technical.get("trend_strength", 0)
        if abs(trend_strength) > 2:
            direction = "上昇" if trend_strength > 0 else "下落"
            factors.append(
                {
                    "factor_type": "technical",
                    "factor_name": f"明確な{direction}トレンド",
                    "description": f"20日移動平均線から{abs(trend_strength):.1f}%乖離し、{direction}トレンドが継続",
                    "influence_score": min(0.9, 0.6 + abs(trend_strength) * 0.05),
                    "confidence": 0.82,
                }
            )

        # ボリューム要因
        volume_ratio = technical.get("volume_ratio", 1.0)
        if volume_ratio > 1.5:
            factors.append(
                {
                    "factor_type": "technical",
                    "factor_name": "異常出来高",
                    "description": f"平均比{volume_ratio:.1f}倍の異常出来高で、機関投資家の動向を反映",
                    "influence_score": 0.75,
                    "confidence": 0.70,
                }
            )

        # ファンダメンタル要因
        earnings_growth = fundamental.get("earnings_growth", 0)
        if earnings_growth and earnings_growth > 0.1:
            factors.append(
                {
                    "factor_type": "fundamental",
                    "factor_name": "利益成長加速",
                    "description": f"前年同期比{earnings_growth*100:.1f}%の利益成長で業績改善継続",
                    "influence_score": 0.92,
                    "confidence": 0.88,
                }
            )

        # 最低2個の要因を保証
        if len(factors) < 2:
            factors.extend(
                [
                    {
                        "factor_type": "pattern",
                        "factor_name": "市場環境連動",
                        "description": "全体市場との相関性を考慮した価格動向予測",
                        "influence_score": 0.65,
                        "confidence": 0.60,
                    },
                    {
                        "factor_type": "technical",
                        "factor_name": "モメンタム分析",
                        "description": "短期・中期の価格モメンタムを総合評価",
                        "influence_score": 0.72,
                        "confidence": 0.68,
                    },
                ]
            )

        return factors[:5]


def generate_real_ai_decision_factors():
    """実データベースのAI判断根拠生成"""
    db_manager = CloudSQLConnection()
    db = db_manager.get_session()
    analyzer = RealTimeAnalyzer()

    try:
        # テーブル作成
        db.execute(
            text(
                """
            CREATE TABLE IF NOT EXISTS ai_decision_factors (
                id BIGINT AUTO_INCREMENT PRIMARY KEY,
                prediction_id BIGINT NOT NULL,
                factor_type ENUM('technical', 'fundamental', 'sentiment', 'news', 'pattern') NOT NULL,
                factor_name VARCHAR(100) NOT NULL,
                influence_score DECIMAL(5,2) NOT NULL,
                description TEXT,
                confidence DECIMAL(5,2),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                INDEX idx_prediction_id (prediction_id),
                INDEX idx_factor_type (factor_type)
            );
        """
            )
        )
        db.commit()

        # 判断根拠が未生成の予測データを取得
        result = db.execute(
            text(
                """
            SELECT sp.id, sp.symbol, sp.predicted_price, sp.confidence_score, sp.current_price
            FROM stock_predictions sp
            LEFT JOIN ai_decision_factors adf ON sp.id = adf.prediction_id
            WHERE adf.prediction_id IS NULL
            AND sp.created_at >= DATE_SUB(NOW(), INTERVAL 7 DAY)
            ORDER BY sp.created_at DESC
            LIMIT 100
        """
            )
        ).fetchall()

        if not result:
            logger.warning("No predictions without decision factors found")
            return 0

        logger.info(f"Processing {len(result)} predictions for AI decision factors...")

        created_count = 0
        for prediction in result:
            try:
                # 価格履歴データ取得
                price_result = db.execute(
                    text(
                        """
                    SELECT date, close_price, volume 
                    FROM stock_prices 
                    WHERE symbol = :symbol 
                    ORDER BY date DESC 
                    LIMIT 50
                """
                    ),
                    {"symbol": prediction.symbol},
                ).fetchall()

                if not price_result:
                    continue

                # 価格データを辞書形式に変換
                price_data = [
                    {"close_price": row.close_price, "volume": row.volume}
                    for row in price_result
                ]

                # テクニカル・ファンダメンタル分析実行
                technical = analyzer.get_technical_analysis(
                    prediction.symbol, price_data
                )
                fundamental = analyzer.get_fundamental_analysis(prediction.symbol)

                # AI判断根拠生成
                factors = analyzer.generate_decision_factors(
                    prediction.symbol, technical, fundamental
                )

                # データベースに挿入
                for factor in factors:
                    db.execute(
                        text(
                            """
                        INSERT INTO ai_decision_factors 
                        (prediction_id, factor_type, factor_name, description, influence_score, confidence)
                        VALUES (:prediction_id, :factor_type, :factor_name, :description, :influence_score, :confidence)
                    """
                        ),
                        {
                            "prediction_id": prediction.id,
                            "factor_type": factor["factor_type"],
                            "factor_name": factor["factor_name"],
                            "description": factor["description"],
                            "influence_score": factor["influence_score"],
                            "confidence": factor["confidence"],
                        },
                    )
                    created_count += 1

                if created_count % 25 == 0:
                    logger.info(f"Created {created_count} decision factors...")

            except Exception as e:
                logger.error(f"Error processing prediction {prediction.id}: {e}")
                continue

        db.commit()
        logger.info(f"✅ Created {created_count} real AI decision factors")
        return created_count

    except Exception as e:
        logger.error(f"❌ Error in generate_real_ai_decision_factors: {e}")
        logger.error(traceback.format_exc())
        return 0
    finally:
        db.close()


def generate_real_theme_insights():
    """実市場データに基づくテーマ別インサイト生成"""
    db_manager = CloudSQLConnection()
    db = db_manager.get_session()
    analyzer = RealTimeAnalyzer()

    try:
        # テーブル作成
        db.execute(
            text(
                """
            CREATE TABLE IF NOT EXISTS theme_insights (
                id BIGINT AUTO_INCREMENT PRIMARY KEY,
                theme_name VARCHAR(50) NOT NULL,
                theme_category ENUM('technology', 'energy', 'finance', 'healthcare', 'consumer', 'industrial', 'materials') NOT NULL,
                insight_date DATE NOT NULL,
                title VARCHAR(200) NOT NULL,
                summary TEXT NOT NULL,
                key_metrics JSON,
                related_symbols JSON,
                trend_direction ENUM('bullish', 'bearish', 'neutral') DEFAULT 'neutral',
                impact_score DECIMAL(3,1),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                INDEX idx_theme_date (theme_name, insight_date),
                INDEX idx_category (theme_category)
            );
        """
            )
        )
        db.commit()

        created_count = 0
        insight_date = date.today()

        # 各セクターの実績分析
        for sector, symbols in analyzer.market_sectors.items():
            try:
                sector_performance = []
                valid_symbols = []

                # セクター主要銘柄の実績取得
                for symbol in symbols[:5]:
                    price_result = db.execute(
                        text(
                            """
                        SELECT close_price, date FROM stock_prices 
                        WHERE symbol = :symbol 
                        ORDER BY date DESC 
                        LIMIT 30
                    """
                        ),
                        {"symbol": symbol},
                    ).fetchall()

                    if len(price_result) >= 2:
                        current = float(price_result[0].close_price)
                        month_ago = float(price_result[-1].close_price)
                        performance = (current - month_ago) / month_ago * 100
                        sector_performance.append(performance)
                        valid_symbols.append(symbol)

                if not sector_performance:
                    continue

                # セクター分析
                avg_performance = np.mean(sector_performance)
                volatility = np.std(sector_performance)

                # トレンド判定
                if avg_performance > 2.0:
                    trend = "bullish"
                    trend_desc = "強気"
                elif avg_performance < -2.0:
                    trend = "bearish"
                    trend_desc = "弱気"
                else:
                    trend = "neutral"
                    trend_desc = "中立"

                # インサイト生成
                theme_name = f"{sector.title()} Sector"
                title = f"{sector.title()}セクター月次分析 - {trend_desc}基調"

                summary = f"""
{sector.title()}セクターの主要{len(valid_symbols)}銘柄を分析した結果、月間平均リターンは{avg_performance:.1f}%となりました。
セクター内のボラティリティは{volatility:.1f}%で、{"安定した" if volatility < 5 else "変動の大きな"}動きを示しています。
{"成長期待が継続" if trend == "bullish" else "慎重な投資判断が必要" if trend == "bearish" else "横ばい推移が予想"}されます。
                """.strip()

                key_metrics = {
                    "average_performance": f"{avg_performance:.1f}%",
                    "volatility": f"{volatility:.1f}%",
                    "analyzed_stocks": len(valid_symbols),
                }

                impact_score = min(10.0, abs(avg_performance) + volatility * 0.5)

                # 既存チェック
                existing = db.execute(
                    text(
                        """
                    SELECT id FROM theme_insights 
                    WHERE theme_name = :theme_name AND insight_date = :insight_date
                """
                    ),
                    {"theme_name": theme_name, "insight_date": insight_date},
                ).fetchone()

                if existing:
                    continue

                # インサイト保存
                db.execute(
                    text(
                        """
                    INSERT INTO theme_insights 
                    (theme_name, theme_category, insight_date, title, summary, 
                     key_metrics, related_symbols, trend_direction, impact_score)
                    VALUES (:theme_name, :theme_category, :insight_date, :title, :summary,
                            :key_metrics, :related_symbols, :trend_direction, :impact_score)
                """
                    ),
                    {
                        "theme_name": theme_name,
                        "theme_category": sector,
                        "insight_date": insight_date,
                        "title": title,
                        "summary": summary,
                        "key_metrics": str(key_metrics).replace("'", '"'),
                        "related_symbols": str(valid_symbols).replace("'", '"'),
                        "trend_direction": trend,
                        "impact_score": impact_score,
                    },
                )

                created_count += 1
                logger.info(
                    f"Created insight: {sector.title()} - {trend} ({avg_performance:.1f}%)"
                )

            except Exception as e:
                logger.error(f"Error processing sector {sector}: {e}")
                continue

        db.commit()
        logger.info(f"✅ Created {created_count} real theme insights")
        return created_count

    except Exception as e:
        logger.error(f"❌ Error in generate_real_theme_insights: {e}")
        logger.error(traceback.format_exc())
        return 0
    finally:
        db.close()


def main():
    """メイン実行関数"""
    logger.info("🚀 Real Data Batch Generator Starting...")
    logger.info("=" * 60)

    try:
        # 1. AI判断根拠生成
        logger.info("1. Generating real AI decision factors...")
        factor_count = generate_real_ai_decision_factors()

        # 2. テーマインサイト生成
        logger.info("\n2. Generating real theme insights...")
        insight_count = generate_real_theme_insights()

        # 結果サマリー
        logger.info("\n" + "=" * 60)
        logger.info("✅ Real data generation completed!")
        logger.info(f"📊 Generated:")
        logger.info(f"   - AI decision factors: {factor_count}")
        logger.info(f"   - Theme insights: {insight_count}")
        logger.info("=" * 60)

        return 0

    except Exception as e:
        logger.error(f"\n❌ Error during real data generation: {e}")
        logger.error(traceback.format_exc())
        return 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
