"""
株価予測レポート生成システム
LSTMモデルの予測結果をもとに詳細な分析レポートを作成
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import json
import logging
from dataclasses import dataclass
import matplotlib.pyplot as plt
import seaborn as sns
import io
import base64

logger = logging.getLogger(__name__)

@dataclass
class StockAnalysis:
    """個別株式分析結果"""
    symbol: str
    current_price: float
    predicted_price: float
    confidence: float
    potential_return: float
    risk_level: str
    recommendation: str
    technical_indicators: Dict[str, Any]

@dataclass
class MarketSentiment:
    """市場センチメント分析"""
    overall_sentiment: str
    bullish_stocks: List[str]
    bearish_stocks: List[str]
    neutral_stocks: List[str]
    market_volatility: float
    fear_greed_index: float

class StockReportGenerator:
    """株価予測レポート生成クラス"""
    
    def __init__(self):
        self.report_template = {
            'executive_summary': {},
            'market_overview': {},
            'individual_analysis': [],
            'predictions_summary': {},
            'risk_assessment': {},
            'recommendations': [],
            'technical_analysis': {},
            'model_performance': {},
            'appendix': {}
        }
    
    def generate_comprehensive_report(
        self, 
        predictions: Dict[str, Dict], 
        market_data: Dict[str, pd.DataFrame],
        model_performance: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """
        包括的な株価分析レポートを生成
        
        Args:
            predictions: 各銘柄の予測結果
            market_data: 市場データ
            model_performance: モデル性能データ
            
        Returns:
            完全なレポートデータ
        """
        logger.info(f"Generating comprehensive report for {len(predictions)} stocks")
        
        report = self.report_template.copy()
        
        # 1. エグゼクティブサマリー
        report['executive_summary'] = self._generate_executive_summary(predictions, market_data)
        
        # 2. 市場概況
        report['market_overview'] = self._analyze_market_overview(market_data)
        
        # 3. 個別銘柄分析
        report['individual_analysis'] = self._analyze_individual_stocks(predictions, market_data)
        
        # 4. 予測サマリー
        report['predictions_summary'] = self._generate_predictions_summary(predictions)
        
        # 5. リスク評価
        report['risk_assessment'] = self._assess_portfolio_risk(predictions, market_data)
        
        # 6. 投資推奨
        report['recommendations'] = self._generate_investment_recommendations(predictions)
        
        # 7. テクニカル分析
        report['technical_analysis'] = self._perform_technical_analysis(market_data)
        
        # 8. モデル性能
        if model_performance:
            report['model_performance'] = model_performance
        
        # 9. 付録
        report['appendix'] = self._generate_appendix(predictions, market_data)
        
        # メタデータ追加
        report['metadata'] = {
            'generated_at': datetime.now().isoformat(),
            'report_version': '1.0',
            'model_version': 'LSTM_v1.0',
            'stocks_analyzed': len(predictions),
            'data_period': self._get_data_period(market_data),
            'disclaimer': 'This report is for informational purposes only and should not be considered as investment advice.'
        }
        
        logger.info("Comprehensive report generated successfully")
        return report
    
    def _generate_executive_summary(self, predictions: Dict, market_data: Dict) -> Dict:
        """エグゼクティブサマリー生成"""
        total_stocks = len(predictions)
        bullish_count = sum(1 for p in predictions.values() if p.get('potential_return', 0) > 2)
        bearish_count = sum(1 for p in predictions.values() if p.get('potential_return', 0) < -2)
        
        avg_return = np.mean([p.get('potential_return', 0) for p in predictions.values()])
        avg_confidence = np.mean([p.get('confidence_score', 0) for p in predictions.values()])
        
        top_performer = max(predictions.items(), key=lambda x: x[1].get('potential_return', 0))
        worst_performer = min(predictions.items(), key=lambda x: x[1].get('potential_return', 0))
        
        return {
            'key_insights': [
                f"分析対象: {total_stocks}銘柄",
                f"強気予測: {bullish_count}銘柄 ({bullish_count/total_stocks*100:.1f}%)",
                f"弱気予測: {bearish_count}銘柄 ({bearish_count/total_stocks*100:.1f}%)",
                f"平均期待リターン: {avg_return:.2f}%",
                f"予測信頼度: {avg_confidence:.1f}%"
            ],
            'market_outlook': self._determine_market_outlook(avg_return, bullish_count, total_stocks),
            'top_pick': {
                'symbol': top_performer[0],
                'expected_return': top_performer[1].get('potential_return', 0),
                'confidence': top_performer[1].get('confidence_score', 0)
            },
            'risk_warning': {
                'symbol': worst_performer[0],
                'expected_return': worst_performer[1].get('potential_return', 0),
                'risk_level': worst_performer[1].get('risk_level', 'unknown')
            }
        }
    
    def _analyze_market_overview(self, market_data: Dict) -> Dict:
        """市場概況分析"""
        market_analysis = {
            'indices_performance': {},
            'sector_analysis': {},
            'volatility_analysis': {},
            'volume_analysis': {}
        }
        
        # 主要指数の分析
        indices = ['^GSPC', '^IXIC', '^DJI', '^N225']
        for index in indices:
            if index in market_data:
                df = market_data[index]
                if not df.empty and 'Close' in df.columns:
                    recent_change = df['Close'].pct_change().iloc[-1] * 100
                    volatility = df['Close'].pct_change().std() * 100
                    
                    market_analysis['indices_performance'][index] = {
                        'recent_change': round(recent_change, 2),
                        'volatility': round(volatility, 2),
                        'trend': 'up' if recent_change > 0 else 'down'
                    }
        
        # セクター分析（簡易版）
        sectors = ['Technology', 'Financial Services', 'Healthcare', 'Consumer Discretionary']
        market_analysis['sector_analysis'] = {
            sector: {
                'performance': np.random.normal(1.5, 2.0),  # プレースホルダー
                'outlook': np.random.choice(['positive', 'neutral', 'negative'])
            } for sector in sectors
        }
        
        # 全体的な市場ボラティリティ
        if market_data:
            all_volatilities = []
            for df in market_data.values():
                if not df.empty and 'Close' in df.columns:
                    vol = df['Close'].pct_change().std()
                    if not np.isnan(vol):
                        all_volatilities.append(vol)
            
            if all_volatilities:
                market_analysis['volatility_analysis'] = {
                    'average_volatility': np.mean(all_volatilities) * 100,
                    'volatility_trend': 'increasing' if np.mean(all_volatilities) > 0.02 else 'stable',
                    'risk_environment': self._assess_risk_environment(np.mean(all_volatilities))
                }
        
        return market_analysis
    
    def _analyze_individual_stocks(self, predictions: Dict, market_data: Dict) -> List[Dict]:
        """個別銘柄分析"""
        analyses = []
        
        for symbol, prediction in predictions.items():
            analysis = {
                'symbol': symbol,
                'current_analysis': {
                    'current_price': prediction.get('current_price', 0),
                    'predicted_price': prediction.get('predicted_prices', [0])[-1],
                    'potential_return': prediction.get('potential_return', 0),
                    'confidence_score': prediction.get('confidence_score', 0),
                    'risk_level': prediction.get('risk_level', 'medium')
                },
                'technical_signals': self._get_technical_signals(symbol, market_data.get(symbol)),
                'prediction_details': {
                    'prediction_range': prediction.get('prediction_range', {}),
                    'prediction_days': prediction.get('prediction_days', 7),
                    'model_version': prediction.get('model_version', 'LSTM_v1.0')
                },
                'investment_recommendation': self._generate_stock_recommendation(prediction),
                'key_factors': self._identify_key_factors(symbol, prediction)
            }
            analyses.append(analysis)
        
        # リターン順でソート
        analyses.sort(key=lambda x: x['current_analysis']['potential_return'], reverse=True)
        return analyses
    
    def _generate_predictions_summary(self, predictions: Dict) -> Dict:
        """予測サマリー生成"""
        returns = [p.get('potential_return', 0) for p in predictions.values()]
        confidences = [p.get('confidence_score', 0) for p in predictions.values()]
        
        return {
            'return_distribution': {
                'mean': np.mean(returns),
                'std': np.std(returns),
                'min': np.min(returns),
                'max': np.max(returns),
                'quartiles': {
                    'q1': np.percentile(returns, 25),
                    'median': np.percentile(returns, 50),
                    'q3': np.percentile(returns, 75)
                }
            },
            'confidence_distribution': {
                'mean': np.mean(confidences),
                'std': np.std(confidences),
                'high_confidence_count': sum(1 for c in confidences if c > 80)
            },
            'prediction_categories': {
                'strong_buy': [s for s, p in predictions.items() if p.get('potential_return', 0) > 5],
                'buy': [s for s, p in predictions.items() if 2 < p.get('potential_return', 0) <= 5],
                'hold': [s for s, p in predictions.items() if -2 <= p.get('potential_return', 0) <= 2],
                'sell': [s for s, p in predictions.items() if p.get('potential_return', 0) < -2]
            }
        }
    
    def _assess_portfolio_risk(self, predictions: Dict, market_data: Dict) -> Dict:
        """ポートフォリオリスク評価"""
        risk_levels = [p.get('risk_level', 'medium') for p in predictions.values()]
        returns = [p.get('potential_return', 0) for p in predictions.values()]
        
        # VaR計算（簡易版）
        var_95 = np.percentile(returns, 5)  # 5%パーセンタイル
        var_99 = np.percentile(returns, 1)  # 1%パーセンタイル
        
        return {
            'risk_distribution': {
                'high_risk': sum(1 for r in risk_levels if r == 'high'),
                'medium_risk': sum(1 for r in risk_levels if r == 'medium'),
                'low_risk': sum(1 for r in risk_levels if r == 'low')
            },
            'value_at_risk': {
                'var_95': var_95,
                'var_99': var_99,
                'expected_shortfall': np.mean([r for r in returns if r <= var_95])
            },
            'portfolio_diversification': self._assess_diversification(predictions),
            'risk_recommendations': self._generate_risk_recommendations(predictions)
        }
    
    def _generate_investment_recommendations(self, predictions: Dict) -> List[Dict]:
        """投資推奨生成"""
        recommendations = []
        
        # トップピック（高リターン & 高信頼度）
        top_picks = sorted(
            [(s, p) for s, p in predictions.items()],
            key=lambda x: x[1].get('potential_return', 0) * (x[1].get('confidence_score', 0) / 100),
            reverse=True
        )[:3]
        
        for symbol, pred in top_picks:
            recommendations.append({
                'type': 'BUY',
                'symbol': symbol,
                'rationale': f"高いリターン期待({pred.get('potential_return', 0):.1f}%)と信頼度({pred.get('confidence_score', 0):.1f}%)",
                'target_price': pred.get('predicted_prices', [0])[-1],
                'risk_level': pred.get('risk_level', 'medium'),
                'time_horizon': f"{pred.get('prediction_days', 7)}日"
            })
        
        # 注意銘柄（高リスク）
        high_risk_stocks = [s for s, p in predictions.items() if p.get('risk_level') == 'high']
        if high_risk_stocks:
            recommendations.append({
                'type': 'CAUTION',
                'symbols': high_risk_stocks,
                'rationale': "高ボラティリティによる高リスク",
                'action': "ポジションサイズを小さくするか、損切りラインを設定"
            })
        
        return recommendations
    
    def _perform_technical_analysis(self, market_data: Dict) -> Dict:
        """テクニカル分析"""
        technical_summary = {
            'overall_trend': 'neutral',
            'support_resistance': {},
            'momentum_indicators': {},
            'volume_analysis': {}
        }
        
        # 簡易トレンド分析
        uptrend_count = 0
        total_analyzed = 0
        
        for symbol, df in market_data.items():
            if df.empty or 'Close' not in df.columns:
                continue
                
            total_analyzed += 1
            
            # 短期・長期移動平均比較
            if len(df) >= 50:
                ma_20 = df['Close'].rolling(20).mean().iloc[-1]
                ma_50 = df['Close'].rolling(50).mean().iloc[-1]
                current_price = df['Close'].iloc[-1]
                
                if current_price > ma_20 > ma_50:
                    uptrend_count += 1
        
        if total_analyzed > 0:
            uptrend_ratio = uptrend_count / total_analyzed
            if uptrend_ratio > 0.6:
                technical_summary['overall_trend'] = 'bullish'
            elif uptrend_ratio < 0.4:
                technical_summary['overall_trend'] = 'bearish'
        
        return technical_summary
    
    def _get_technical_signals(self, symbol: str, df: pd.DataFrame) -> Dict:
        """テクニカルシグナル取得"""
        if df is None or df.empty or 'Close' not in df.columns:
            return {'trend': 'unknown', 'signals': []}
        
        signals = []
        current_price = df['Close'].iloc[-1]
        
        # 移動平均分析
        if len(df) >= 20:
            ma_20 = df['Close'].rolling(20).mean().iloc[-1]
            if current_price > ma_20 * 1.02:
                signals.append("価格が20日移動平均を上回る")
            elif current_price < ma_20 * 0.98:
                signals.append("価格が20日移動平均を下回る")
        
        # ボリューム分析
        if len(df) >= 5 and 'Volume' in df.columns:
            recent_volume = df['Volume'].iloc[-5:].mean()
            avg_volume = df['Volume'].mean()
            if recent_volume > avg_volume * 1.5:
                signals.append("出来高が平均を大幅に上回る")
        
        return {
            'trend': self._determine_trend(df),
            'signals': signals,
            'strength': len(signals)
        }
    
    def _determine_trend(self, df: pd.DataFrame) -> str:
        """トレンド判定"""
        if len(df) < 10:
            return 'unknown'
        
        recent_prices = df['Close'].iloc[-10:]
        price_change = (recent_prices.iloc[-1] - recent_prices.iloc[0]) / recent_prices.iloc[0]
        
        if price_change > 0.05:
            return 'uptrend'
        elif price_change < -0.05:
            return 'downtrend'
        else:
            return 'sideways'
    
    def _generate_stock_recommendation(self, prediction: Dict) -> Dict:
        """個別銘柄推奨生成"""
        potential_return = prediction.get('potential_return', 0)
        confidence = prediction.get('confidence_score', 0)
        risk_level = prediction.get('risk_level', 'medium')
        
        if potential_return > 5 and confidence > 75:
            action = 'STRONG_BUY'
            rationale = "高いリターン期待と高信頼度"
        elif potential_return > 2 and confidence > 60:
            action = 'BUY'
            rationale = "ポジティブなリターン期待"
        elif potential_return > -2:
            action = 'HOLD'
            rationale = "中性的な見通し"
        else:
            action = 'SELL'
            rationale = "ネガティブなリターン期待"
        
        return {
            'action': action,
            'rationale': rationale,
            'confidence_level': 'high' if confidence > 75 else 'medium' if confidence > 50 else 'low',
            'risk_adjustment': f"リスクレベル: {risk_level}"
        }
    
    def _identify_key_factors(self, symbol: str, prediction: Dict) -> List[str]:
        """主要要因特定"""
        factors = []
        
        risk_level = prediction.get('risk_level', 'medium')
        potential_return = prediction.get('potential_return', 0)
        
        if risk_level == 'high':
            factors.append("高ボラティリティ")
        if abs(potential_return) > 5:
            factors.append("大きな価格変動予想")
        if prediction.get('confidence_score', 0) > 80:
            factors.append("高い予測信頼度")
        
        # 業界固有要因（プレースホルダー）
        if symbol in ['AAPL', 'GOOGL', 'MSFT']:
            factors.append("テクノロジーセクターの成長")
        elif symbol in ['JPM', 'V']:
            factors.append("金融政策の影響")
        
        return factors
    
    def _determine_market_outlook(self, avg_return: float, bullish_count: int, total_stocks: int) -> str:
        """市場見通し決定"""
        bullish_ratio = bullish_count / total_stocks if total_stocks > 0 else 0
        
        if avg_return > 3 and bullish_ratio > 0.6:
            return "非常に強気"
        elif avg_return > 1 and bullish_ratio > 0.5:
            return "強気"
        elif avg_return > -1 and bullish_ratio > 0.4:
            return "中立"
        elif avg_return > -3:
            return "弱気"
        else:
            return "非常に弱気"
    
    def _assess_risk_environment(self, avg_volatility: float) -> str:
        """リスク環境評価"""
        if avg_volatility > 0.04:
            return "高リスク"
        elif avg_volatility > 0.02:
            return "中リスク"
        else:
            return "低リスク"
    
    def _assess_diversification(self, predictions: Dict) -> Dict:
        """分散評価"""
        risk_levels = [p.get('risk_level', 'medium') for p in predictions.values()]
        returns = [p.get('potential_return', 0) for p in predictions.values()]
        
        return {
            'risk_concentration': max(risk_levels.count('high'), risk_levels.count('medium'), risk_levels.count('low')) / len(risk_levels),
            'return_correlation': 'low',  # プレースホルダー
            'diversification_score': min(100, (1 - np.std(returns) / np.mean(np.abs(returns))) * 100)
        }
    
    def _generate_risk_recommendations(self, predictions: Dict) -> List[str]:
        """リスク推奨生成"""
        recommendations = []
        
        high_risk_count = sum(1 for p in predictions.values() if p.get('risk_level') == 'high')
        if high_risk_count > len(predictions) * 0.3:
            recommendations.append("ポートフォリオのリスク集中度が高いため、分散投資を検討してください")
        
        low_confidence_count = sum(1 for p in predictions.values() if p.get('confidence_score', 0) < 60)
        if low_confidence_count > len(predictions) * 0.4:
            recommendations.append("予測信頼度が低い銘柄が多いため、ポジションサイズを調整してください")
        
        return recommendations
    
    def _get_data_period(self, market_data: Dict) -> str:
        """データ期間取得"""
        if not market_data:
            return "不明"
        
        for df in market_data.values():
            if not df.empty and hasattr(df.index, 'min'):
                start_date = df.index.min().strftime("%Y-%m-%d")
                end_date = df.index.max().strftime("%Y-%m-%d")
                return f"{start_date} to {end_date}"
        
        return "データ期間不明"
    
    def _generate_appendix(self, predictions: Dict, market_data: Dict) -> Dict:
        """付録生成"""
        return {
            'methodology': {
                'model_type': 'LSTM (Long Short-Term Memory)',
                'features_used': ['価格', 'ボリューム', '技術指標', 'ボラティリティ'],
                'training_period': '過去1年間のデータ',
                'prediction_horizon': '7日間'
            },
            'disclaimer': [
                "本レポートは情報提供のみを目的としており、投資助言ではありません",
                "予測結果は過去のデータに基づいており、将来の結果を保証するものではありません",
                "投資判断は自己責任で行ってください",
                "市場状況の急変により予測が外れる可能性があります"
            ],
            'data_sources': ['Yahoo Finance', 'その他公開市場データ'],
            'contact_info': {
                'system': 'Miraikakaku AI予測システム',
                'version': 'v1.0',
                'last_updated': datetime.now().strftime("%Y-%m-%d")
            }
        }
    
    def export_to_json(self, report: Dict, filepath: str = None) -> str:
        """レポートをJSONファイルとして出力"""
        if filepath is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filepath = f"stock_analysis_report_{timestamp}.json"
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
        
        logger.info(f"Report exported to {filepath}")
        return filepath