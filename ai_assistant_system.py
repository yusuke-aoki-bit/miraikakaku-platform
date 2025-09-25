#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Miraikakaku AI Assistant System
高度なAI投資アドバイザー

機能:
- 自然言語による投資相談対応
- 市場分析と予測の説明
- ポートフォリオ最適化提案
- リスク分析とアラート
- 投資戦略カスタマイズ
- マルチモーダル分析（テキスト + データ）
"""

import os
import sys
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict
import re
import numpy as np
import pandas as pd

# データベース
import psycopg2
from psycopg2.extras import RealDictCursor

# 機械学習・統計
try:
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.metrics.pairwise import cosine_similarity
    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False

# ログ設定
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('ai_assistant.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

@dataclass
class UserQuery:
    """ユーザーの質問"""
    text: str
    user_id: Optional[str]
    timestamp: datetime
    context: Dict[str, Any]
    intent: Optional[str] = None
    entities: Optional[Dict[str, List[str]]] = None

@dataclass
class AssistantResponse:
    """AIアシスタントの回答"""
    response_text: str
    confidence: float
    response_type: str  # 'analysis', 'recommendation', 'explanation', 'alert'
    data_sources: List[str]
    suggested_actions: List[str]
    related_stocks: List[str]
    charts_data: Optional[Dict[str, Any]]
    timestamp: datetime
    reasoning: List[str]

@dataclass
class InvestmentProfile:
    """投資プロファイル"""
    user_id: str
    risk_tolerance: str  # 'conservative', 'moderate', 'aggressive'
    investment_horizon: str  # 'short', 'medium', 'long'
    preferred_sectors: List[str]
    capital_amount: Optional[float]
    experience_level: str  # 'beginner', 'intermediate', 'advanced'
    goals: List[str]
    constraints: List[str]

class NaturalLanguageProcessor:
    """自然言語処理エンジン"""

    def __init__(self):
        self.intent_patterns = {
            'price_inquiry': [
                r'.*価格.*', r'.*株価.*', r'.*いくら.*', r'.*値段.*',
                r'.*price.*', r'.*cost.*', r'.*worth.*'
            ],
            'prediction_request': [
                r'.*予測.*', r'.*予想.*', r'.*見通し.*', r'.*将来.*',
                r'.*prediction.*', r'.*forecast.*', r'.*future.*'
            ],
            'analysis_request': [
                r'.*分析.*', r'.*評価.*', r'.*どう思う.*', r'.*意見.*',
                r'.*analysis.*', r'.*analyze.*', r'.*opinion.*'
            ],
            'recommendation_request': [
                r'.*おすすめ.*', r'.*推奨.*', r'.*買う.*', r'.*売る.*',
                r'.*recommend.*', r'.*suggest.*', r'.*buy.*', r'.*sell.*'
            ],
            'portfolio_inquiry': [
                r'.*ポートフォリオ.*', r'.*資産配分.*', r'.*分散.*',
                r'.*portfolio.*', r'.*allocation.*', r'.*diversification.*'
            ],
            'risk_inquiry': [
                r'.*リスク.*', r'.*危険.*', r'.*安全.*', r'.*volatility.*',
                r'.*risk.*', r'.*safe.*', r'.*danger.*'
            ]
        }

        self.entity_patterns = {
            'stock_symbols': r'\b([A-Z]{1,5})\b',
            'companies': [
                'Apple', 'Google', 'Microsoft', 'Tesla', 'Amazon',
                'アップル', 'グーグル', 'マイクロソフト', 'テスラ', 'アマゾン'
            ],
            'numbers': r'\$?(\d{1,3}(?:,\d{3})*(?:\.\d{2})?)',
            'time_periods': [
                '今日', '明日', '来週', '来月', '今年',
                'today', 'tomorrow', 'next week', 'next month'
            ]
        }

        # TF-IDF for semantic similarity (if available)
        if SKLEARN_AVAILABLE:
            self.vectorizer = TfidfVectorizer(
                max_features=1000,
                stop_words='english',
                ngram_range=(1, 2)
            )
            self._trained = False

    def analyze_query(self, query: UserQuery) -> UserQuery:
        """クエリ分析"""
        logger.info(f"📝 クエリ分析: {query.text[:50]}...")

        # 意図分類
        query.intent = self._classify_intent(query.text)

        # エンティティ抽出
        query.entities = self._extract_entities(query.text)

        logger.info(f"🎯 分析結果: 意図={query.intent}, エンティティ={len(query.entities) if query.entities else 0}件")
        return query

    def _classify_intent(self, text: str) -> str:
        """意図分類"""
        text_lower = text.lower()

        for intent, patterns in self.intent_patterns.items():
            for pattern in patterns:
                if re.search(pattern, text_lower):
                    return intent

        return 'general_inquiry'

    def _extract_entities(self, text: str) -> Dict[str, List[str]]:
        """エンティティ抽出"""
        entities = {}

        # 株式シンボル
        symbols = re.findall(self.entity_patterns['stock_symbols'], text.upper())
        if symbols:
            entities['symbols'] = list(set(symbols))

        # 会社名
        companies = []
        for company in self.entity_patterns['companies']:
            if company.lower() in text.lower():
                companies.append(company)
        if companies:
            entities['companies'] = companies

        # 数値
        numbers = re.findall(self.entity_patterns['numbers'], text)
        if numbers:
            entities['numbers'] = numbers

        return entities

class MarketDataAnalyzer:
    """市場データ分析エンジン"""

    def __init__(self):
        self.db_config = {
            'host': "34.173.9.214",
            'database': "miraikakaku",
            'user': "postgres",
            'password': os.getenv('DB_PASSWORD')
        }

    def get_stock_analysis(self, symbol: str) -> Dict[str, Any]:
        """株式分析データ取得"""
        logger.info(f"📊 {symbol}の分析データ取得中...")

        try:
            conn = psycopg2.connect(**self.db_config)

            # 最新価格データ
            price_query = """
            SELECT date, close_price, volume,
                   close_price - LAG(close_price) OVER (ORDER BY date) as price_change
            FROM stock_prices
            WHERE symbol = %s
            ORDER BY date DESC
            LIMIT 30
            """

            price_df = pd.read_sql_query(price_query, conn, params=[symbol])

            # 予測データ
            prediction_query = """
            SELECT prediction_date, predicted_price, confidence_score
            FROM stock_predictions
            WHERE symbol = %s
            AND prediction_date >= CURRENT_DATE
            ORDER BY prediction_date ASC
            LIMIT 10
            """

            prediction_df = pd.read_sql_query(prediction_query, conn, params=[symbol])

            conn.close()

            if price_df.empty:
                return {'error': f'{symbol}のデータが見つかりません'}

            # 分析計算
            analysis = self._calculate_technical_indicators(price_df)
            analysis['predictions'] = prediction_df.to_dict('records') if not prediction_df.empty else []
            analysis['symbol'] = symbol
            analysis['last_updated'] = datetime.now().isoformat()

            return analysis

        except Exception as e:
            logger.error(f"分析データ取得エラー: {e}")
            return {'error': str(e)}

    def _calculate_technical_indicators(self, df: pd.DataFrame) -> Dict[str, Any]:
        """テクニカル指標計算"""
        if df.empty:
            return {}

        analysis = {}

        # 基本統計
        latest_price = df.iloc[0]['close_price']
        analysis['current_price'] = float(latest_price)
        analysis['price_change_1d'] = float(df.iloc[0]['price_change']) if df.iloc[0]['price_change'] else 0

        # 移動平均
        df['ma_5'] = df['close_price'].rolling(5).mean()
        df['ma_20'] = df['close_price'].rolling(20).mean()

        analysis['ma_5'] = float(df.iloc[0]['ma_5']) if not pd.isna(df.iloc[0]['ma_5']) else None
        analysis['ma_20'] = float(df.iloc[0]['ma_20']) if not pd.isna(df.iloc[0]['ma_20']) else None

        # ボラティリティ
        returns = df['close_price'].pct_change().dropna()
        analysis['volatility'] = float(returns.std()) * np.sqrt(252) if len(returns) > 1 else 0

        # RSI風指標
        gains = returns.where(returns > 0, 0)
        losses = -returns.where(returns < 0, 0)
        if len(gains) > 1 and len(losses) > 1:
            avg_gain = gains.mean()
            avg_loss = losses.mean()
            if avg_loss != 0:
                rs = avg_gain / avg_loss
                analysis['rsi_like'] = float(100 - (100 / (1 + rs)))
            else:
                analysis['rsi_like'] = 100

        # トレンド分析
        if len(df) >= 5:
            recent_trend = np.polyfit(range(5), df.iloc[:5]['close_price'].values, 1)[0]
            analysis['trend'] = 'up' if recent_trend > 0 else 'down'
            analysis['trend_strength'] = abs(float(recent_trend))

        return analysis

class InvestmentAdvisor:
    """投資アドバイザーエンジン"""

    def __init__(self):
        self.risk_profiles = {
            'conservative': {
                'volatility_threshold': 0.15,
                'recommended_allocation': {'stocks': 0.4, 'bonds': 0.5, 'cash': 0.1},
                'max_single_position': 0.05
            },
            'moderate': {
                'volatility_threshold': 0.25,
                'recommended_allocation': {'stocks': 0.6, 'bonds': 0.3, 'cash': 0.1},
                'max_single_position': 0.10
            },
            'aggressive': {
                'volatility_threshold': 0.35,
                'recommended_allocation': {'stocks': 0.8, 'bonds': 0.1, 'cash': 0.1},
                'max_single_position': 0.20
            }
        }

    def generate_recommendation(
        self,
        query: UserQuery,
        analysis_data: Dict[str, Any],
        user_profile: Optional[InvestmentProfile] = None
    ) -> List[str]:
        """投資推奨生成"""

        recommendations = []

        if 'error' in analysis_data:
            recommendations.append("申し訳ございませんが、現在データを取得できません。")
            return recommendations

        symbol = analysis_data.get('symbol', 'Unknown')
        current_price = analysis_data.get('current_price', 0)
        volatility = analysis_data.get('volatility', 0)
        trend = analysis_data.get('trend', 'neutral')

        # リスク評価
        risk_level = self._assess_risk_level(analysis_data, user_profile)

        if query.intent == 'recommendation_request':
            if trend == 'up' and risk_level == 'low':
                recommendations.append(f"{symbol}は上昇トレンドかつ低リスクで、投資検討に値します。")
            elif trend == 'down' or risk_level == 'high':
                recommendations.append(f"{symbol}は現在リスクが高いため、慎重な判断をお勧めします。")
            else:
                recommendations.append(f"{symbol}は中立的な状況です。他の投資機会と比較検討してください。")

        elif query.intent == 'risk_inquiry':
            if volatility > 0.3:
                recommendations.append(f"{symbol}は高ボラティリティ（{volatility:.1%}）のため、リスク管理が重要です。")
            else:
                recommendations.append(f"{symbol}は比較的安定的な値動き（ボラティリティ{volatility:.1%}）を示しています。")

        elif query.intent == 'prediction_request':
            predictions = analysis_data.get('predictions', [])
            if predictions:
                next_pred = predictions[0]
                recommendations.append(f"AIモデルは{symbol}の次期予測価格を${next_pred['predicted_price']:.2f}と予測しています。")
                recommendations.append(f"予測信頼度: {next_pred['confidence_score']:.1%}")

        # ポートフォリオ関連アドバイス
        if user_profile and query.intent == 'portfolio_inquiry':
            profile_rec = self._generate_portfolio_advice(user_profile, analysis_data)
            recommendations.extend(profile_rec)

        return recommendations

    def _assess_risk_level(
        self,
        analysis_data: Dict[str, Any],
        user_profile: Optional[InvestmentProfile]
    ) -> str:
        """リスクレベル評価"""
        volatility = analysis_data.get('volatility', 0)

        # デフォルト閾値
        thresholds = self.risk_profiles['moderate']

        if user_profile and user_profile.risk_tolerance in self.risk_profiles:
            thresholds = self.risk_profiles[user_profile.risk_tolerance]

        if volatility > thresholds['volatility_threshold']:
            return 'high'
        elif volatility < thresholds['volatility_threshold'] * 0.6:
            return 'low'
        else:
            return 'medium'

    def _generate_portfolio_advice(
        self,
        profile: InvestmentProfile,
        analysis_data: Dict[str, Any]
    ) -> List[str]:
        """ポートフォリオアドバイス生成"""
        advice = []

        risk_config = self.risk_profiles.get(profile.risk_tolerance, self.risk_profiles['moderate'])

        advice.append(f"あなたの{profile.risk_tolerance}リスクプロファイルに基づく推奨資産配分:")
        for asset, ratio in risk_config['recommended_allocation'].items():
            advice.append(f"- {asset}: {ratio:.0%}")

        advice.append(f"単一銘柄の最大投資比率: {risk_config['max_single_position']:.0%}")

        return advice

class AIAssistantEngine:
    """AIアシスタントメインエンジン"""

    def __init__(self):
        self.nlp = NaturalLanguageProcessor()
        self.market_analyzer = MarketDataAnalyzer()
        self.investment_advisor = InvestmentAdvisor()

        # 応答テンプレート
        self.response_templates = {
            'greeting': [
                "こんにちは！投資に関するご質問にお答えします。",
                "Miraikakaku AIアシスタントです。どのようなサポートをお求めですか？"
            ],
            'price_inquiry': [
                "最新の価格情報をお調べします。",
                "価格データを取得しています..."
            ],
            'analysis_complete': [
                "分析が完了しました。",
                "以下が分析結果です："
            ]
        }

    def process_query(
        self,
        query_text: str,
        user_id: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None
    ) -> AssistantResponse:
        """メインクエリ処理"""

        logger.info(f"🤖 AIアシスタント処理開始: {query_text[:50]}...")

        # クエリ準備
        query = UserQuery(
            text=query_text,
            user_id=user_id,
            timestamp=datetime.now(),
            context=context or {}
        )

        # 自然言語処理
        query = self.nlp.analyze_query(query)

        # レスポンス生成
        response = self._generate_response(query)

        logger.info(f"✅ 応答生成完了: 信頼度{response.confidence:.2f}")
        return response

    def _generate_response(self, query: UserQuery) -> AssistantResponse:
        """レスポンス生成"""

        response_text = ""
        confidence = 0.7
        suggested_actions = []
        related_stocks = []
        data_sources = []
        reasoning = []

        try:
            # 挨拶・一般的な質問
            if any(greeting in query.text.lower() for greeting in ['こんにちは', 'hello', 'hi', 'はじめまして']):
                response_text = "こんにちは！Miraikakaku AIアシスタントです。株式投資に関するご質問にお答えします。銘柄分析、市場予測、投資アドバイスなど、お気軽にお尋ねください。"
                confidence = 0.95

            # 株式関連の質問
            elif query.entities and 'symbols' in query.entities:
                symbol = query.entities['symbols'][0]
                related_stocks = [symbol]

                # 市場データ分析
                analysis_data = self.market_analyzer.get_stock_analysis(symbol)
                data_sources = ['market_data', 'predictions']

                if 'error' not in analysis_data:
                    # 基本情報
                    current_price = analysis_data.get('current_price', 0)
                    price_change = analysis_data.get('price_change_1d', 0)
                    volatility = analysis_data.get('volatility', 0)

                    response_text = f"{symbol}の分析結果：\n"
                    response_text += f"現在価格: ${current_price:.2f}\n"
                    response_text += f"1日変動: {price_change:+.2f} ({price_change/current_price*100:+.1f}%)\n"
                    response_text += f"年間ボラティリティ: {volatility:.1%}\n"

                    # トレンド情報
                    trend = analysis_data.get('trend')
                    if trend:
                        trend_desc = "上昇傾向" if trend == 'up' else "下降傾向"
                        response_text += f"短期トレンド: {trend_desc}\n"

                    # 投資アドバイス
                    recommendations = self.investment_advisor.generate_recommendation(
                        query, analysis_data
                    )

                    if recommendations:
                        response_text += "\n📋 投資アドバイス:\n"
                        for rec in recommendations:
                            response_text += f"• {rec}\n"

                    confidence = 0.85
                    reasoning = [
                        f"最新の市場データを分析",
                        f"テクニカル指標を計算",
                        f"AIモデルによる予測を考慮"
                    ]

                    # 推奨アクション
                    if query.intent == 'recommendation_request':
                        if analysis_data.get('trend') == 'up':
                            suggested_actions = ["詳細分析の実行", "リスク評価の確認", "ポートフォリオ影響の検討"]
                        else:
                            suggested_actions = ["市場動向の継続監視", "代替投資機会の探索"]

                else:
                    response_text = f"申し訳ございません。{symbol}のデータを取得できませんでした。"
                    confidence = 0.3

            # 一般的な投資相談
            elif query.intent == 'portfolio_inquiry':
                response_text = """ポートフォリオ最適化のための基本原則：

1. **分散投資**: リスクを複数の資産に分散
2. **資産配分**: 年齢と投資目標に応じた株式・債券の比率
3. **定期的なリバランス**: 目標配分の維持
4. **長期投資**: 市場の短期変動に惑わされない

具体的な銘柄についてお聞きになりたい場合は、銘柄コード（例：AAPL、GOOGL）を教えてください。"""
                confidence = 0.8
                suggested_actions = ["具体的な銘柄の相談", "リスク許容度の診断", "投資目標の設定"]

            elif query.intent == 'risk_inquiry':
                response_text = """投資リスク管理のポイント：

🔴 **高リスク要因**:
• 高ボラティリティ銘柄（年間30%以上の価格変動）
• 集中投資（単一銘柄への偏重）
• 短期売買

🟡 **リスク軽減策**:
• 分散投資によるリスク分散
• 損切りルールの設定
• 投資金額の適切な管理

具体的な銘柄のリスク評価については、銘柄コードをお教えください。"""
                confidence = 0.75

            else:
                # デフォルト応答
                response_text = """以下についてサポートできます：

📈 **市場分析**: 銘柄コード（AAPL、GOOGLなど）を教えてください
🎯 **投資アドバイス**: 「AAPLを買うべきですか？」のような質問
📊 **リスク分析**: 「TSLAのリスクは？」のような質問
💼 **ポートフォリオ相談**: 資産配分や分散投資について

何についてお知りになりたいですか？"""
                confidence = 0.6

        except Exception as e:
            logger.error(f"応答生成エラー: {e}")
            response_text = "申し訳ございません。処理中にエラーが発生しました。もう一度お試しください。"
            confidence = 0.2

        return AssistantResponse(
            response_text=response_text,
            confidence=confidence,
            response_type=query.intent or 'general',
            data_sources=data_sources,
            suggested_actions=suggested_actions,
            related_stocks=related_stocks,
            charts_data=None,
            timestamp=datetime.now(),
            reasoning=reasoning
        )

def main():
    """テスト実行"""
    logger.info("🤖 AIアシスタントシステム開始")

    assistant = AIAssistantEngine()

    # テストクエリ
    test_queries = [
        "こんにちは",
        "AAPLの株価はどうですか？",
        "TSLAを買うべきでしょうか？",
        "ポートフォリオの分散について教えてください",
        "MSFTのリスクを教えて",
        "投資初心者におすすめの銘柄は？"
    ]

    for query in test_queries:
        logger.info(f"\n{'='*50}")
        logger.info(f"質問: {query}")
        logger.info(f"{'='*50}")

        response = assistant.process_query(query)

        print(f"🤖 AIアシスタント:")
        print(response.response_text)
        print(f"\n信頼度: {response.confidence:.2f}")
        print(f"応答タイプ: {response.response_type}")

        if response.suggested_actions:
            print(f"推奨アクション: {', '.join(response.suggested_actions)}")

        if response.related_stocks:
            print(f"関連銘柄: {', '.join(response.related_stocks)}")

        print("\n" + "="*50 + "\n")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        logger.info("👋 AIアシスタント終了")
    except Exception as e:
        logger.error(f"実行エラー: {e}")
        sys.exit(1)