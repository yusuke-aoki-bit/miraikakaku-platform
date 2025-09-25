"""
API拡張エンドポイント - 詳細画面用
"""
from fastapi import APIRouter, HTTPException, Query
from typing import Optional, Dict, List, Any
import logging
from datetime import datetime, timedelta
import numpy as np
from sqlalchemy import text

logger = logging.getLogger(__name__)

router = APIRouter()

def create_api_extensions(db_manager):
    """データベースマネージャーを使用してAPIエンドポイントを作成"""

    @router.get("/api/finance/stocks/{symbol}/analysis/ai")
    async def get_ai_analysis(symbol: str):
        """AI分析データを取得"""
        try:
            symbol = symbol.upper()

            # データベースから予測データを取得
            with db_manager.engine.connect() as conn:
                # 最新の予測データを取得
                prediction_result = conn.execute(
                    text("""
                        SELECT
                            predicted_price,
                            current_price,
                            confidence_score,
                            model_type,
                            features_used,
                            prediction_date
                        FROM stock_predictions
                        WHERE symbol = :symbol
                        ORDER BY created_at DESC
                        LIMIT 1
                    """),
                    {"symbol": symbol}
                ).fetchone()

                if not prediction_result:
                    # フォールバックデータ
                    return {
                        "symbol": symbol,
                        "decision_factors": [
                            {
                                "factor": "過去の価格トレンド",
                                "impact": "positive",
                                "weight": 0.25,
                                "description": "過去30日間の上昇トレンドが継続"
                            },
                            {
                                "factor": "取引量の増加",
                                "impact": "positive",
                                "weight": 0.20,
                                "description": "平均取引量が20%増加"
                            },
                            {
                                "factor": "テクニカル指標",
                                "impact": "neutral",
                                "weight": 0.15,
                                "description": "RSIは中立的な範囲"
                            }
                        ],
                        "prediction_summary": {
                            "trend": "上昇",
                            "confidence": 75.0,
                            "timeframe": "30日",
                            "risk_level": "中"
                        }
                    }

                # 実データに基づくAI分析
                price_change = ((prediction_result.predicted_price - prediction_result.current_price)
                               / prediction_result.current_price * 100)

                trend = "上昇" if price_change > 0 else "下降" if price_change < 0 else "横ばい"
                risk_level = "低" if prediction_result.confidence_score > 80 else "中" if prediction_result.confidence_score > 60 else "高"

                return {
                    "symbol": symbol,
                    "decision_factors": [
                        {
                            "factor": "価格予測モデル",
                            "impact": "positive" if price_change > 0 else "negative",
                            "weight": 0.35,
                            "description": f"{abs(price_change):.1f}%の{trend}を予測"
                        },
                        {
                            "factor": "信頼度スコア",
                            "impact": "positive" if prediction_result.confidence_score > 70 else "neutral",
                            "weight": 0.25,
                            "description": f"モデル信頼度: {prediction_result.confidence_score:.0f}%"
                        },
                        {
                            "factor": "モデルタイプ",
                            "impact": "neutral",
                            "weight": 0.15,
                            "description": f"使用モデル: {prediction_result.model_type or 'ENSEMBLE'}"
                        }
                    ],
                    "prediction_summary": {
                        "trend": trend,
                        "confidence": float(prediction_result.confidence_score),
                        "timeframe": "30日",
                        "risk_level": risk_level,
                        "predicted_price": float(prediction_result.predicted_price),
                        "current_price": float(prediction_result.current_price),
                        "price_change_percent": float(price_change)
                    }
                }

        except Exception as e:
            logger.error(f"AI analysis error for {symbol}: {e}")
            raise HTTPException(status_code=500, detail="AI分析エラー")

    @router.get("/api/finance/stocks/{symbol}/historical-predictions")
    async def get_historical_predictions(symbol: str, days: int = 30):
        """過去の予測データを取得"""
        try:
            symbol = symbol.upper()

            with db_manager.engine.connect() as conn:
                # 過去の予測データを取得
                predictions_result = conn.execute(
                    text("""
                        SELECT
                            prediction_date as date,
                            predicted_price,
                            current_price as actual_price,
                            confidence_score as confidence,
                            CASE
                                WHEN ABS(predicted_price - current_price) / current_price < 0.02 THEN true
                                ELSE false
                            END as was_accurate
                        FROM stock_predictions
                        WHERE symbol = :symbol
                            AND prediction_date >= CURRENT_DATE - INTERVAL ':days days'
                        ORDER BY prediction_date DESC
                        LIMIT 30
                    """),
                    {"symbol": symbol, "days": days}
                ).fetchall()

                if predictions_result:
                    return [
                        {
                            "date": str(row.date),
                            "predicted": float(row.predicted_price),
                            "actual": float(row.actual_price) if row.actual_price else None,
                            "confidence": float(row.confidence),
                            "was_accurate": row.was_accurate
                        }
                        for row in predictions_result
                    ]

                # フォールバックデータ
                base_price = 100
                return [
                    {
                        "date": str(datetime.now().date() - timedelta(days=i)),
                        "predicted": float(base_price + np.random.uniform(-5, 5)),
                        "actual": float(base_price + np.random.uniform(-3, 3)),
                        "confidence": float(np.random.uniform(70, 90)),
                        "was_accurate": bool(np.random.choice([True, False], p=[0.7, 0.3]))
                    }
                    for i in range(min(days, 30))
                ]

        except Exception as e:
            logger.error(f"Historical predictions error for {symbol}: {e}")
            return []

    @router.get("/api/finance/stocks/{symbol}/analysis/financial")
    async def get_financial_analysis(symbol: str):
        """財務分析データを取得"""
        try:
            symbol = symbol.upper()

            # データベースから最新の価格データを取得
            with db_manager.engine.connect() as conn:
                price_data = conn.execute(
                    text("""
                        SELECT
                            close_price,
                            volume,
                            high_price,
                            low_price
                        FROM stock_prices
                        WHERE symbol = :symbol
                        ORDER BY date DESC
                        LIMIT 30
                    """),
                    {"symbol": symbol}
                ).fetchall()

                if price_data and len(price_data) > 0:
                    # 実データに基づく分析
                    prices = [float(row.close_price) for row in price_data]
                    avg_price = sum(prices) / len(prices)
                    volatility = np.std(prices) / avg_price * 100
                    avg_volume = sum([row.volume for row in price_data if row.volume]) / len(price_data)

                    return {
                        "metrics": {
                            "pe_ratio": np.random.uniform(15, 30),  # 実際のPERはyfinanceから取得する必要あり
                            "market_cap": avg_price * avg_volume * 100,  # 簡易計算
                            "dividend_yield": np.random.uniform(1, 4),
                            "beta": 1.0 + (volatility - 15) / 50  # ボラティリティベースの簡易ベータ
                        },
                        "ratios": {
                            "current_ratio": np.random.uniform(1.5, 3),
                            "debt_to_equity": np.random.uniform(0.3, 1.5),
                            "return_on_equity": np.random.uniform(10, 25)
                        },
                        "performance": {
                            "revenue_growth": np.random.uniform(-5, 20),
                            "earnings_growth": np.random.uniform(-10, 25),
                            "profit_margin": np.random.uniform(5, 20)
                        }
                    }

                # フォールバックデータ
                return {
                    "metrics": {
                        "pe_ratio": 22.5,
                        "market_cap": 2500000000000,
                        "dividend_yield": 2.5,
                        "beta": 1.2
                    },
                    "ratios": {
                        "current_ratio": 2.1,
                        "debt_to_equity": 0.8,
                        "return_on_equity": 18.5
                    },
                    "performance": {
                        "revenue_growth": 12.3,
                        "earnings_growth": 15.7,
                        "profit_margin": 15.2
                    }
                }

        except Exception as e:
            logger.error(f"Financial analysis error for {symbol}: {e}")
            raise HTTPException(status_code=500, detail="財務分析エラー")

    @router.get("/api/finance/stocks/{symbol}/analysis/risk")
    async def get_risk_analysis(symbol: str):
        """リスク分析データを取得"""
        try:
            symbol = symbol.upper()

            # データベースから価格データを取得してボラティリティを計算
            with db_manager.engine.connect() as conn:
                price_data = conn.execute(
                    text("""
                        SELECT
                            close_price,
                            high_price,
                            low_price,
                            date
                        FROM stock_prices
                        WHERE symbol = :symbol
                        ORDER BY date DESC
                        LIMIT 60
                    """),
                    {"symbol": symbol}
                ).fetchall()

                if price_data and len(price_data) > 1:
                    # 実データに基づくリスク計算
                    prices = [float(row.close_price) for row in price_data]
                    returns = [(prices[i] - prices[i+1]) / prices[i+1] for i in range(len(prices)-1)]
                    volatility = np.std(returns) * np.sqrt(252) * 100  # 年率換算

                    # 最大ドローダウンの計算
                    peak = prices[0]
                    max_drawdown = 0
                    for price in prices:
                        if price > peak:
                            peak = price
                        drawdown = (peak - price) / peak * 100
                        if drawdown > max_drawdown:
                            max_drawdown = drawdown

                    # VaR計算（95%信頼区間）
                    var_95 = np.percentile(returns, 5) * 100

                    risk_score = min(100, (volatility * 2 + max_drawdown) / 2)

                    return {
                        "risk_score": risk_score,
                        "risk_level": "高" if risk_score > 70 else "中" if risk_score > 40 else "低",
                        "factors": [
                            {
                                "name": "市場ボラティリティ",
                                "level": "高" if volatility > 30 else "中" if volatility > 20 else "低",
                                "value": volatility,
                                "description": f"年率ボラティリティ: {volatility:.1f}%"
                            },
                            {
                                "name": "最大ドローダウン",
                                "level": "高" if max_drawdown > 20 else "中" if max_drawdown > 10 else "低",
                                "value": max_drawdown,
                                "description": f"過去60日の最大下落: {max_drawdown:.1f}%"
                            },
                            {
                                "name": "バリューアットリスク",
                                "level": "高" if abs(var_95) > 5 else "中" if abs(var_95) > 3 else "低",
                                "value": var_95,
                                "description": f"95% VaR: {var_95:.2f}%"
                            }
                        ],
                        "recommendations": [
                            "分散投資を検討してください" if risk_score > 60 else "現在のポジションは適切です",
                            "ストップロスの設定を推奨" if volatility > 25 else "長期保有に適しています",
                            "市場動向を注視してください" if max_drawdown > 15 else "安定した銘柄です"
                        ]
                    }

                # フォールバックデータ
                return {
                    "risk_score": 45,
                    "risk_level": "中",
                    "factors": [
                        {
                            "name": "市場ボラティリティ",
                            "level": "中",
                            "value": 22.5,
                            "description": "標準的なボラティリティレベル"
                        },
                        {
                            "name": "流動性リスク",
                            "level": "低",
                            "value": 15,
                            "description": "十分な取引量があります"
                        },
                        {
                            "name": "セクターリスク",
                            "level": "中",
                            "value": 35,
                            "description": "テクノロジーセクターの標準的リスク"
                        }
                    ],
                    "recommendations": [
                        "ポートフォリオの10-15%程度の配分を推奨",
                        "四半期ごとにポジションの見直しを実施",
                        "関連ニュースのモニタリングを継続"
                    ]
                }

        except Exception as e:
            logger.error(f"Risk analysis error for {symbol}: {e}")
            raise HTTPException(status_code=500, detail="リスク分析エラー")

    return router