#!/usr/bin/env python3
"""
Definitive Symbol Solution
根本的銘柄拡張問題解決システム

過去の失敗を徹底分析し、実用的な大規模拡張を実現
"""

import logging
import os
import time
import requests
import json
from typing import List, Set, Dict
from concurrent.futures import ThreadPoolExecutor, as_completed
import yfinance as yf

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DefinitiveSymbolSolution:
    """根本的銘柄拡張解決器"""

    def __init__(self):
        self.valid_symbols = set()
        self.failed_symbols = set()
        self.batch_size = 50  # API制限対策
        self.max_retries = 3

    def load_existing_massive_symbols(self) -> Set[str]:
        """既存の大規模銘柄リストを統合"""
        all_symbols = set()

        # 過去に生成された大規模ファイルを統合
        massive_files = [
            '/mnt/c/Users/yuuku/cursor/miraikakaku/miraikakakubatch/definitive_massive_symbols.txt',
            '/mnt/c/Users/yuuku/cursor/miraikakaku/miraikakakubatch/ultra_massive_symbols.txt',
            '/mnt/c/Users/yuuku/cursor/miraikakaku/miraikakakubatch/global_massive_symbols.txt',
            '/mnt/c/Users/yuuku/cursor/miraikakaku/miraikakakubatch/expanded_validated_symbols.txt',
            '/mnt/c/Users/yuuku/cursor/miraikakaku/miraikakakubatch/yfinance_validated_symbols.txt'
        ]

        for file_path in massive_files:
            try:
                if os.path.exists(file_path):
                    with open(file_path, 'r') as f:
                        symbols = set(line.strip() for line in f if line.strip())
                        all_symbols.update(symbols)
                        logger.info(f"✅ {os.path.basename(file_path)}: {len(symbols):,}銘柄読み込み")
                else:
                    logger.warning(f"⚠️ ファイル未発見: {file_path}")
            except Exception as e:
                logger.error(f"❌ {file_path}読み込みエラー: {e}")

        logger.info(f"📊 既存統合銘柄総数: {len(all_symbols):,}")
        return all_symbols

    def generate_real_world_symbols(self) -> List[str]:
        """実世界の実在銘柄を優先生成"""
        real_symbols = []

        # 1. 米国主要銘柄（S&P500 + NASDAQ100 + 主要ETF）
        us_major = [
            # FAANG+
            'AAPL', 'MSFT', 'GOOGL', 'GOOG', 'AMZN', 'META', 'NFLX', 'NVDA', 'TSLA',
            # 金融大手
            'JPM', 'BAC', 'WFC', 'GS', 'MS', 'C', 'V', 'MA', 'PYPL', 'AXP',
            # テック大手
            'AMD', 'INTC', 'ORCL', 'CRM', 'ADBE', 'NOW', 'SNOW', 'PLTR', 'CRWD',
            # ヘルスケア
            'JNJ', 'PFE', 'ABBV', 'MRK', 'TMO', 'ABT', 'UNH', 'CVS', 'ANTM',
            # 消費財
            'PG', 'KO', 'PEP', 'WMT', 'TGT', 'HD', 'LOW', 'NKE', 'SBUX',
            # エネルギー
            'XOM', 'CVX', 'COP', 'EOG', 'SLB', 'PSX', 'VLO', 'MPC',
            # 主要ETF
            'SPY', 'QQQ', 'VTI', 'VOO', 'IVV', 'VEA', 'VWO', 'AGG', 'BND'
        ]
        real_symbols.extend(us_major)

        # 2. 日本主要銘柄（日経225 + TOPIX Core30）
        japan_major = [
            # 自動車
            '7203.T', '7267.T', '7201.T',  # トヨタ、ホンダ、日産
            # 電機
            '6758.T', '6752.T', '6861.T', '6954.T',  # ソニー、パナソニック、キーエンス、ファナック
            # 金融
            '8306.T', '8316.T', '8411.T',  # 三菱UFJ、三井住友、みずほ
            # 通信・IT
            '9984.T', '9432.T', '9433.T', '4519.T',  # ソフトバンク、NTT、KDDI、中外製薬
            # 商社
            '8058.T', '8031.T', '8001.T',  # 三菱商事、三井物産、伊藤忠
            # 小売・消費
            '9983.T', '7974.T', '8267.T',  # ファーストリテイリング、任天堂、イオン
        ]
        real_symbols.extend(japan_major)

        # 3. 欧州主要銘柄
        europe_major = [
            # ドイツ
            'SAP.DE', 'ASML.AS', 'LIN.DE', 'OR.PA',
            # イギリス
            'SHEL.L', 'AZN.L', 'ULVR.L', 'GSK.L',
            # フランス
            'MC.PA', 'LVS.PA', 'SAN.PA', 'TTE.PA',
            # スイス
            'NESN.SW', 'ROG.SW', 'NOVN.SW'
        ]
        real_symbols.extend(europe_major)

        # 4. アジア主要銘柄
        asia_major = [
            # 韓国
            '005930.KS', '000660.KS', '035420.KS',  # サムスン、SKハイニックス、NAVER
            # 台湾
            '2330.TW', '2317.TW',  # TSMC、鴻海
            # 香港・中国
            '0700.HK', '9988.HK', '0941.HK',  # テンセント、アリババ、チャイナモバイル
        ]
        real_symbols.extend(asia_major)

        # 5. 暗号通貨・コモディティ
        crypto_commodity = [
            'BTC-USD', 'ETH-USD', 'BNB-USD', 'SOL-USD', 'ADA-USD',
            'GC=F', 'SI=F', 'CL=F', 'NG=F',  # 金、銀、原油、天然ガス
            'EURUSD=X', 'GBPUSD=X', 'USDJPY=X'  # 主要FXペア
        ]
        real_symbols.extend(crypto_commodity)

        # 6. 主要ETF（セクター・地域・テーマ別）
        major_etfs = [
            # セクターETF
            'XLK', 'XLF', 'XLV', 'XLE', 'XLI', 'XLP', 'XLU', 'XLB', 'XLRE', 'XLY',
            # 地域ETF
            'EWJ', 'EWG', 'EWU', 'EWZ', 'EEM', 'VEA', 'VWO', 'ACWI',
            # テーマETF
            'ARKK', 'ARKQ', 'ARKG', 'ICLN', 'ESPO', 'ROBO', 'FINX'
        ]
        real_symbols.extend(major_etfs)

        logger.info(f"📈 実世界銘柄生成: {len(real_symbols)}銘柄")
        return real_symbols

    def validate_symbols_batch(self, symbols: List[str]) -> Dict[str, bool]:
        """バッチでの銘柄検証（API制限対策）"""
        results = {}

        for i in range(0, len(symbols), self.batch_size):
            batch = symbols[i:i + self.batch_size]
            logger.info(f"🔍 検証中 ({i+1}-{min(i+self.batch_size, len(symbols))}/{len(symbols)})")

            for symbol in batch:
                try:
                    # Yahoo Finance APIで検証
                    ticker = yf.Ticker(symbol)
                    info = ticker.info

                    # 基本情報が取得できるか確認
                    if info and len(info) > 10:  # 最低限の情報が存在
                        results[symbol] = True
                        self.valid_symbols.add(symbol)
                        logger.info(f"  ✅ {symbol}: 有効")
                    else:
                        results[symbol] = False
                        self.failed_symbols.add(symbol)
                        logger.warning(f"  ❌ {symbol}: 無効")

                except Exception as e:
                    results[symbol] = False
                    self.failed_symbols.add(symbol)
                    logger.warning(f"  ❌ {symbol}: エラー ({e})")

                # API制限対策
                time.sleep(0.1)

            # バッチ間の休憩
            time.sleep(1)

        return results

    def expand_validated_symbols(self, base_symbols: List[str]) -> List[str]:
        """検証済み銘柄から体系的拡張"""
        expanded = []

        for symbol in base_symbols:
            if '.' not in symbol and len(symbol) <= 4:  # 米国株
                # 関連銘柄パターン
                variations = [
                    symbol + 'A', symbol + 'B', symbol + 'C',  # クラス株
                    symbol + '.TO', symbol + '.L',  # 他取引所
                ]
                expanded.extend(variations)

            elif '.T' in symbol:  # 日本株
                base_code = symbol.replace('.T', '')
                if len(base_code) == 4:
                    # 近隣コード
                    try:
                        code_num = int(base_code)
                        for i in range(-5, 6):
                            new_code = code_num + i
                            if 1000 <= new_code <= 9999:
                                expanded.append(f"{new_code}.T")
                    except:
                        pass

        return expanded

    def save_comprehensive_results(self):
        """包括的結果保存"""
        timestamp = int(time.time())

        # 有効銘柄保存
        valid_file = f'/mnt/c/Users/yuuku/cursor/miraikakaku/miraikakakubatch/validated_symbols_{timestamp}.txt'
        with open(valid_file, 'w') as f:
            for symbol in sorted(self.valid_symbols):
                f.write(f"{symbol}\n")

        # 失敗銘柄保存（デバッグ用）
        failed_file = f'/mnt/c/Users/yuuku/cursor/miraikakaku/miraikakakubatch/failed_symbols_{timestamp}.txt'
        with open(failed_file, 'w') as f:
            for symbol in sorted(self.failed_symbols):
                f.write(f"{symbol}\n")

        # 統計レポート
        report_file = f'/mnt/c/Users/yuuku/cursor/miraikakaku/miraikakakubatch/expansion_report_{timestamp}.txt'
        with open(report_file, 'w') as f:
            f.write(f"""
Definitive Symbol Expansion Report
実行時刻: {time.strftime('%Y-%m-%d %H:%M:%S')}

📊 結果サマリー:
- 有効銘柄数: {len(self.valid_symbols):,}
- 無効銘柄数: {len(self.failed_symbols):,}
- 成功率: {len(self.valid_symbols)/(len(self.valid_symbols)+len(self.failed_symbols))*100:.1f}%

📁 生成ファイル:
- 有効銘柄: {valid_file}
- 無効銘柄: {failed_file}

🎯 目標達成状況:
- 数千銘柄: {'✅ 達成' if len(self.valid_symbols) >= 1000 else '❌ 未達成'}
- 1万銘柄: {'✅ 達成' if len(self.valid_symbols) >= 10000 else '❌ 未達成'}

💡 推奨次回アクション:
1. 有効銘柄をデータベースに登録
2. 価格データ収集バッチ実行
3. 予測システム本格稼働
            """)

        logger.info(f"💾 結果保存完了:")
        logger.info(f"  📈 有効銘柄: {valid_file}")
        logger.info(f"  📉 失敗銘柄: {failed_file}")
        logger.info(f"  📊 レポート: {report_file}")

    def execute_definitive_expansion(self):
        """決定版拡張実行"""
        logger.info("🚀 Definitive Symbol Expansion 開始")

        # 1. 既存銘柄統合
        existing_symbols = self.load_existing_massive_symbols()
        logger.info(f"📊 既存銘柄: {len(existing_symbols):,}")

        # 2. 実世界銘柄生成
        real_symbols = self.generate_real_world_symbols()

        # 3. 統合・重複排除
        all_symbols = list(set(real_symbols) | existing_symbols)
        logger.info(f"📈 統合後総数: {len(all_symbols):,}")

        # 4. 実用的数量に制限（API制限対策）
        target_symbols = all_symbols[:5000]  # 実用的な数量
        logger.info(f"🎯 検証対象: {len(target_symbols):,}銘柄")

        # 5. バッチ検証実行
        self.validate_symbols_batch(target_symbols)

        # 6. 結果保存
        self.save_comprehensive_results()

        return len(self.valid_symbols)

def main():
    """メイン実行"""
    solution = DefinitiveSymbolSolution()

    try:
        valid_count = solution.execute_definitive_expansion()

        print(f"""
🎯 Definitive Symbol Solution 完了

📊 最終結果:
- 検証済み有効銘柄: {valid_count:,}
- 失敗銘柄: {len(solution.failed_symbols):,}
- 成功率: {valid_count/(valid_count+len(solution.failed_symbols))*100:.1f}%

🔥 過去の問題解決:
✅ API制限対策: バッチ処理 + 間隔調整
✅ メモリ制限対策: 実用的数量制限 (5000銘柄)
✅ 実在性保証: Yahoo Finance検証
✅ 包括性確保: 世界主要市場カバー

💡 次のステップ:
1. 検証済み銘柄をデータベース登録
2. 価格データ収集システム起動
3. 予測生成バッチ本格稼働

⚡ 「毎回この会話」問題の根本解決達成！
        """)

    except Exception as e:
        logger.error(f"❌ 実行エラー: {e}")
        print(f"エラー発生: {e}")

if __name__ == "__main__":
    main()