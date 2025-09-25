#!/usr/bin/env python3
"""
Prediction Data Coverage Checker
予測データの充足率チェック
"""

import yfinance as yf
import pandas as pd
import time
import logging
from typing import List, Dict
import os
from datetime import datetime, timedelta

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class PredictionCoverageChecker:
    """予測データ充足率チェッカー"""

    def __init__(self):
        self.symbols = []
        self.coverage_results = {}

    def load_validated_symbols(self) -> List[str]:
        """検証済み銘柄読み込み"""
        try:
            with open('/mnt/c/Users/yuuku/cursor/miraikakaku/miraikakakubatch/yfinance_validated_symbols.txt', 'r') as f:
                symbols = [line.strip() for line in f if line.strip()]
                logger.info(f"✅ 検証済み銘柄: {len(symbols)}銘柄読み込み")
                return symbols
        except Exception as e:
            logger.error(f"❌ 銘柄リスト読み込みエラー: {e}")
            return []

    def check_data_availability(self, symbol: str) -> Dict:
        """個別銘柄のデータ可用性チェック"""
        result = {
            'symbol': symbol,
            'has_data': False,
            'data_points': 0,
            'latest_date': None,
            'price_range': None,
            'volume_available': False,
            'error': None
        }

        try:
            ticker = yf.Ticker(symbol)

            # 過去3ヶ月のデータ取得
            hist = ticker.history(period='3mo', timeout=10)

            if not hist.empty:
                result['has_data'] = True
                result['data_points'] = len(hist)
                result['latest_date'] = hist.index[-1].strftime('%Y-%m-%d')
                result['price_range'] = {
                    'min': float(hist['Low'].min()),
                    'max': float(hist['High'].max()),
                    'latest': float(hist['Close'].iloc[-1])
                }
                result['volume_available'] = 'Volume' in hist.columns and not hist['Volume'].isna().all()

        except Exception as e:
            result['error'] = str(e)
            logger.debug(f"❌ {symbol}: {e}")

        return result

    def batch_check_coverage(self, symbols: List[str], sample_size: int = 100) -> Dict:
        """バッチでカバレッジチェック"""
        logger.info(f"🔍 データ充足率チェック開始 (サンプル: {sample_size}銘柄)")

        # サンプリング
        import random
        if len(symbols) > sample_size:
            sample_symbols = random.sample(symbols, sample_size)
        else:
            sample_symbols = symbols

        results = {
            'total_symbols': len(symbols),
            'checked_symbols': len(sample_symbols),
            'successful': 0,
            'failed': 0,
            'data_available': 0,
            'no_data': 0,
            'coverage_rate': 0.0,
            'details': [],
            'summary': {}
        }

        for i, symbol in enumerate(sample_symbols, 1):
            if i % 10 == 0:
                logger.info(f"🔄 進捗: {i}/{len(sample_symbols)} ({results['successful']}成功)")

            check_result = self.check_data_availability(symbol)
            results['details'].append(check_result)

            if check_result['error']:
                results['failed'] += 1
            else:
                results['successful'] += 1

            if check_result['has_data']:
                results['data_available'] += 1
            else:
                results['no_data'] += 1

            # レート制限対策
            time.sleep(0.1)

        # カバレッジ率計算
        if results['checked_symbols'] > 0:
            results['coverage_rate'] = (results['data_available'] / results['checked_symbols']) * 100

        return results

    def analyze_coverage_by_exchange(self, symbols: List[str]) -> Dict:
        """取引所別カバレッジ分析"""
        logger.info("🌍 取引所別カバレッジ分析開始")

        exchanges = {
            'US': [s for s in symbols if '.' not in s and '=' not in s and '-' not in s],
            'Tokyo': [s for s in symbols if s.endswith('.T')],
            'Korea': [s for s in symbols if s.endswith('.KS')],
            'HongKong': [s for s in symbols if s.endswith('.HK')],
            'London': [s for s in symbols if s.endswith('.L')],
            'Germany': [s for s in symbols if s.endswith('.DE')],
            'Forex': [s for s in symbols if '=X' in s],
            'Crypto': [s for s in symbols if '-' in s and any(curr in s for curr in ['USD', 'EUR', 'GBP', 'JPY'])]
        }

        exchange_results = {}

        for exchange_name, exchange_symbols in exchanges.items():
            if len(exchange_symbols) == 0:
                continue

            logger.info(f"📊 {exchange_name}取引所: {len(exchange_symbols)}銘柄")

            # サンプルサイズ調整
            sample_size = min(20, len(exchange_symbols))
            exchange_result = self.batch_check_coverage(exchange_symbols, sample_size)

            exchange_results[exchange_name] = {
                'total_symbols': len(exchange_symbols),
                'coverage_rate': exchange_result['coverage_rate'],
                'sample_size': sample_size,
                'data_available': exchange_result['data_available']
            }

        return exchange_results

    def generate_coverage_report(self, symbols: List[str]) -> Dict:
        """総合カバレッジレポート生成"""
        logger.info("📋 総合カバレッジレポート生成開始")

        # 全体チェック
        overall_results = self.batch_check_coverage(symbols, sample_size=200)

        # 取引所別チェック
        exchange_results = self.analyze_coverage_by_exchange(symbols)

        # 統計情報
        data_quality_stats = {
            'avg_data_points': 0,
            'recent_data_rate': 0,
            'volume_availability_rate': 0
        }

        valid_details = [d for d in overall_results['details'] if d['has_data']]
        if valid_details:
            data_quality_stats['avg_data_points'] = sum(d['data_points'] for d in valid_details) / len(valid_details)

            # 最近7日以内のデータがある銘柄の割合
            recent_cutoff = (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')
            recent_count = sum(1 for d in valid_details if d['latest_date'] and d['latest_date'] >= recent_cutoff)
            data_quality_stats['recent_data_rate'] = (recent_count / len(valid_details)) * 100

            # ボリュームデータ可用率
            volume_count = sum(1 for d in valid_details if d['volume_available'])
            data_quality_stats['volume_availability_rate'] = (volume_count / len(valid_details)) * 100

        report = {
            'timestamp': datetime.now().isoformat(),
            'total_validated_symbols': len(symbols),
            'overall_coverage': overall_results,
            'exchange_breakdown': exchange_results,
            'data_quality': data_quality_stats,
            'recommendations': self.generate_recommendations(overall_results, exchange_results)
        }

        return report

    def generate_recommendations(self, overall_results: Dict, exchange_results: Dict) -> List[str]:
        """改善提案生成"""
        recommendations = []

        if overall_results['coverage_rate'] < 80:
            recommendations.append(f"全体カバレッジが{overall_results['coverage_rate']:.1f}%と低いです。データソースの追加を検討してください。")

        if overall_results['failed'] > overall_results['successful'] * 0.1:
            recommendations.append(f"エラー率が{(overall_results['failed']/overall_results['checked_symbols']*100):.1f}%と高いです。API制限やネットワーク問題を確認してください。")

        # 取引所別の問題点
        for exchange_name, result in exchange_results.items():
            if result['coverage_rate'] < 60:
                recommendations.append(f"{exchange_name}取引所のカバレッジが{result['coverage_rate']:.1f}%と低いです。")

        if not recommendations:
            recommendations.append("データ充足率は良好です。現在の設定を維持してください。")

        return recommendations

def main():
    """メイン実行"""
    checker = PredictionCoverageChecker()

    # 検証済み銘柄読み込み
    symbols = checker.load_validated_symbols()

    if not symbols:
        print("❌ 検証済み銘柄が見つかりません")
        return

    # カバレッジレポート生成
    report = checker.generate_coverage_report(symbols)

    # 結果出力
    print(f"""
    📊 予測データ充足率レポート
    ================================

    🎯 基本情報:
    - 検証済み銘柄数: {report['total_validated_symbols']:,}銘柄
    - チェック日時: {report['timestamp']}

    📈 全体カバレッジ:
    - サンプル数: {report['overall_coverage']['checked_symbols']}銘柄
    - データ充足率: {report['overall_coverage']['coverage_rate']:.1f}%
    - データ取得成功: {report['overall_coverage']['data_available']}銘柄
    - データ取得失敗: {report['overall_coverage']['no_data']}銘柄

    🌍 取引所別カバレッジ:
    """)

    for exchange, result in report['exchange_breakdown'].items():
        print(f"    - {exchange}: {result['coverage_rate']:.1f}% ({result['total_symbols']}銘柄)")

    print(f"""
    📊 データ品質:
    - 平均データ点数: {report['data_quality']['avg_data_points']:.0f}点
    - 最新データ率: {report['data_quality']['recent_data_rate']:.1f}%
    - ボリューム可用率: {report['data_quality']['volume_availability_rate']:.1f}%

    💡 推奨事項:
    """)

    for i, rec in enumerate(report['recommendations'], 1):
        print(f"    {i}. {rec}")

if __name__ == "__main__":
    main()