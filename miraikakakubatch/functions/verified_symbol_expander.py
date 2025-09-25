#!/usr/bin/env python3
"""
実在銘柄拡張システム
既存の365銘柄をベースに、検証済みの実在銘柄のみを追加
"""

import yfinance as yf
import pandas as pd
import requests
import time
import logging
from typing import List, Set, Dict
from datetime import datetime, timedelta
import os
import json

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class VerifiedSymbolExpander:
    """検証済み実在銘柄を拡張するクラス"""

    def __init__(self):
        self.existing_symbols = self.load_existing_symbols()
        self.new_symbols = set()

    def load_existing_symbols(self) -> Set[str]:
        """既存の検証済み銘柄を読み込み"""
        try:
            with open('/mnt/c/Users/yuuku/cursor/miraikakaku/miraikakakubatch/real_data_source_symbols.txt', 'r') as f:
                symbols = set(line.strip() for line in f if line.strip())
            logger.info(f"既存銘柄数: {len(symbols)}")
            return symbols
        except Exception as e:
            logger.error(f"既存銘柄読み込みエラー: {e}")
            return set()

    def get_sp500_complete_list(self) -> List[str]:
        """S&P 500完全リストを取得"""
        try:
            url = 'https://en.wikipedia.org/wiki/List_of_S%26P_500_companies'
            tables = pd.read_html(url)
            sp500_df = tables[0]
            symbols = sp500_df['Symbol'].tolist()
            # 無効文字を修正
            clean_symbols = []
            for s in symbols:
                if isinstance(s, str):
                    # 一部の銘柄は.が含まれているので-に変換
                    clean_symbols.append(s.replace('.', '-'))

            logger.info(f"S&P 500完全リスト: {len(clean_symbols)}銘柄")
            return clean_symbols
        except Exception as e:
            logger.error(f"S&P 500取得エラー: {e}")
            return []

    def get_nasdaq100_complete_list(self) -> List[str]:
        """NASDAQ 100完全リストを取得"""
        try:
            # Invesco QQQ Trust (QQQ) の保有銘柄情報から取得
            nasdaq100_major = [
                'AAPL', 'MSFT', 'GOOGL', 'GOOG', 'AMZN', 'NVDA', 'TSLA', 'META',
                'AVGO', 'PEP', 'COST', 'COMCAST', 'NFLX', 'ADBE', 'CISCO', 'TMUS',
                'INTC', 'TXN', 'QCOM', 'HON', 'INTU', 'AMGN', 'AMAT', 'ISRG',
                'BKNG', 'ADP', 'GILD', 'VRTX', 'SBUX', 'MDLZ', 'ADI', 'LRCX',
                'PYPL', 'REGN', 'SNPS', 'KLAC', 'CDNS', 'CSX', 'ORLY', 'CTAS',
                'NXPI', 'MAR', 'MRVL', 'FTNT', 'ABNB', 'TEAM', 'CHTR', 'FANG',
                'DXCM', 'EA', 'WBD', 'IDXX', 'GEHC', 'FAST', 'KDP', 'MRNA',
                'BIIB', 'CTSH', 'ZS', 'TTWO', 'ILMN', 'WBA', 'CCEP', 'LULU',
                'EXC', 'ROST', 'KHC', 'CRWD', 'ZM', 'ODFL', 'ALGN', 'FISV',
                'PANW', 'PAYX', 'ON', 'PCAR', 'MNST', 'VRSK', 'DLTR', 'XEL',
                'CPRT', 'LCID', 'SIRI', 'EBAY', 'RIVN', 'DOCU', 'MTCH', 'OKTA'
            ]

            logger.info(f"NASDAQ 100完全リスト: {len(nasdaq100_major)}銘柄")
            return nasdaq100_major
        except Exception as e:
            logger.error(f"NASDAQ 100取得エラー: {e}")
            return []

    def get_japanese_stocks_expanded(self) -> List[str]:
        """日本株式拡張リスト"""
        try:
            # 日経225の主要構成銘柄（実在）
            nikkei225_major = [
                # 自動車・輸送機器
                '7203.T', '7267.T', '7201.T', '7269.T', '7211.T', '7270.T',
                # 電機・精密
                '6758.T', '6861.T', '6954.T', '6971.T', '6976.T', '6981.T',
                '6857.T', '6779.T', '6702.T', '6753.T', '6762.T', '6367.T',
                # 金融
                '8306.T', '8316.T', '8411.T', '8601.T', '8628.T', '8766.T',
                # 商社
                '8058.T', '8031.T', '8001.T', '2768.T', '8053.T',
                # 化学・素材
                '4042.T', '4043.T', '4061.T', '4063.T', '4183.T', '4188.T',
                # 情報通信
                '9984.T', '9432.T', '9433.T', '9434.T', '4324.T', '4385.T',
                # 食品・消費財
                '2801.T', '2914.T', '2269.T', '2413.T', '2432.T', '2503.T',
                # 医薬品
                '4519.T', '4502.T', '4503.T', '4506.T', '4507.T', '4568.T',
                # 建設・不動産
                '1925.T', '1928.T', '1802.T', '1803.T', '1808.T', '1812.T',
                # 電力・ガス
                '9501.T', '9502.T', '9503.T', '9531.T', '9532.T',
                # 鉄道・航空
                '9020.T', '9021.T', '9022.T', '9201.T', '9202.T',
                # 小売
                '8267.T', '3382.T', '7974.T', '9983.T', '3099.T'
            ]

            logger.info(f"日本株拡張リスト: {len(nikkei225_major)}銘柄")
            return nikkei225_major
        except Exception as e:
            logger.error(f"日本株拡張リスト取得エラー: {e}")
            return []

    def get_major_etfs_expanded(self) -> List[str]:
        """主要ETF拡張リスト"""
        try:
            major_etfs = [
                # SPDR ETFs
                'SPY', 'XLK', 'XLF', 'XLV', 'XLI', 'XLE', 'XLY', 'XLP', 'XLB', 'XLU',
                'XLRE', 'XLC', 'XBI', 'XOP', 'XHB', 'XRT', 'XME', 'XTN', 'XNTK',

                # Vanguard ETFs
                'VTI', 'VOO', 'VEA', 'VWO', 'VTV', 'VUG', 'VBR', 'VBK', 'VOE', 'VOT',
                'VNQ', 'VGT', 'VFH', 'VHT', 'VIS', 'VDE', 'VCR', 'VDC', 'VAW', 'VPU',

                # iShares ETFs
                'IVV', 'IWM', 'EEM', 'EFA', 'AGG', 'TLT', 'IEF', 'SHY', 'LQD', 'HYG',
                'IEFA', 'IEMG', 'IJH', 'IJR', 'MTUM', 'QUAL', 'SIZE', 'USMV', 'VMOT',

                # ARK ETFs
                'ARKK', 'ARKQ', 'ARKW', 'ARKG', 'ARKF', 'ARKX',

                # その他の主要ETF
                'QQQ', 'DIA', 'MDY', 'GLD', 'SLV', 'USO', 'UNG', 'VXX', 'UVXY', 'SVXY',
                'TQQQ', 'SQQQ', 'SPXL', 'SPXS', 'TNA', 'TZA', 'UPRO', 'SPXU'
            ]

            logger.info(f"主要ETF拡張リスト: {len(major_etfs)}銘柄")
            return major_etfs
        except Exception as e:
            logger.error(f"ETF拡張リスト取得エラー: {e}")
            return []

    def get_crypto_pairs_expanded(self) -> List[str]:
        """仮想通貨ペア拡張リスト"""
        try:
            # メジャー暗号通貨
            major_cryptos = [
                'BTC', 'ETH', 'BNB', 'XRP', 'ADA', 'SOL', 'DOGE', 'DOT', 'AVAX', 'SHIB',
                'MATIC', 'LTC', 'UNI', 'LINK', 'ATOM', 'ETC', 'XLM', 'BCH', 'ALGO', 'VET',
                'FIL', 'TRX', 'ICP', 'EOS', 'XTZ', 'THETA', 'HBAR', 'FLOW', 'MANA', 'SAND'
            ]

            # 通貨ペア
            currencies = ['USD', 'EUR', 'JPY', 'GBP']

            crypto_pairs = []
            for crypto in major_cryptos:
                for currency in currencies:
                    crypto_pairs.append(f"{crypto}-{currency}")

            logger.info(f"仮想通貨ペア拡張リスト: {len(crypto_pairs)}銘柄")
            return crypto_pairs
        except Exception as e:
            logger.error(f"仮想通貨ペア取得エラー: {e}")
            return []

    def get_international_stocks(self) -> List[str]:
        """国際株式（実在のみ）"""
        try:
            international_stocks = [
                # 欧州
                'ASML', 'SAP', 'NESN.SW', 'NOVO-B.CO', 'MC.PA', 'OR.PA',
                'VOW3.DE', 'BMW.DE', 'MBG.DE', 'SIE.DE', 'BAS.DE',

                # 中国・香港
                'BABA', 'JD', 'BIDU', 'TCEHY', 'NTES', 'PDD', 'NIO', 'XPEV', 'LI',

                # 韓国
                '005930.KS', '000660.KS', '035420.KS', '051910.KS', '006400.KS',

                # カナダ
                'SHOP.TO', 'TD.TO', 'RY.TO', 'BNS.TO', 'CNR.TO',

                # オーストラリア
                'CBA.AX', 'WBC.AX', 'ANZ.AX', 'NAB.AX', 'BHP.AX',

                # 英国
                'SHEL', 'AZN', 'BP', 'ULVR.L', 'VOD.L', 'BT-A.L', 'BARC.L'
            ]

            logger.info(f"国際株式リスト: {len(international_stocks)}銘柄")
            return international_stocks
        except Exception as e:
            logger.error(f"国際株式取得エラー: {e}")
            return []

    def validate_symbol_batch(self, symbols: List[str], batch_size: int = 50) -> List[str]:
        """バッチで銘柄の存在確認"""
        valid_symbols = []

        for i in range(0, len(symbols), batch_size):
            batch = symbols[i:i+batch_size]
            logger.info(f"検証中... {i//batch_size + 1}/{(len(symbols) + batch_size - 1)//batch_size}")

            for symbol in batch:
                try:
                    # 既存銘柄はスキップ
                    if symbol in self.existing_symbols:
                        continue

                    ticker = yf.Ticker(symbol)
                    hist = ticker.history(period='5d', timeout=10)

                    if not hist.empty and len(hist) >= 1:
                        # 最新価格が有効かチェック
                        latest_price = hist['Close'].iloc[-1]
                        if pd.notna(latest_price) and latest_price > 0:
                            valid_symbols.append(symbol)
                            logger.info(f"✅ {symbol}: ${latest_price:.2f}")
                        else:
                            logger.warning(f"❌ {symbol}: 無効な価格データ")
                    else:
                        logger.warning(f"❌ {symbol}: データなし")

                except Exception as e:
                    logger.warning(f"❌ {symbol}: {str(e)}")

                time.sleep(0.1)  # レート制限対策

            # バッチ間の休憩
            time.sleep(1)

        logger.info(f"検証完了: {len(valid_symbols)}/{len(symbols)} 新規銘柄")
        return valid_symbols

    def expand_symbol_list(self) -> Dict[str, int]:
        """銘柄リストを拡張"""
        logger.info("🚀 実在銘柄拡張開始")

        all_new_symbols = []

        # 各カテゴリから取得
        logger.info("📊 S&P 500完全リスト取得中...")
        all_new_symbols.extend(self.get_sp500_complete_list())

        logger.info("📊 NASDAQ 100完全リスト取得中...")
        all_new_symbols.extend(self.get_nasdaq100_complete_list())

        logger.info("🏯 日本株拡張リスト取得中...")
        all_new_symbols.extend(self.get_japanese_stocks_expanded())

        logger.info("📈 ETF拡張リスト取得中...")
        all_new_symbols.extend(self.get_major_etfs_expanded())

        logger.info("💰 仮想通貨ペア拡張リスト取得中...")
        all_new_symbols.extend(self.get_crypto_pairs_expanded())

        logger.info("🌍 国際株式リスト取得中...")
        all_new_symbols.extend(self.get_international_stocks())

        # 重複除去
        unique_new_symbols = list(set(all_new_symbols))
        logger.info(f"収集完了: {len(unique_new_symbols)}銘柄（重複除去後）")

        # 存在確認
        logger.info("🔍 銘柄存在確認開始...")
        valid_new_symbols = self.validate_symbol_batch(unique_new_symbols)

        # 既存リストと結合
        total_symbols = list(self.existing_symbols) + valid_new_symbols

        # 結果をファイルに保存
        output_file = '/mnt/c/Users/yuuku/cursor/miraikakaku/miraikakakubatch/expanded_verified_symbols.txt'
        with open(output_file, 'w') as f:
            for symbol in sorted(total_symbols):
                f.write(f"{symbol}\n")

        results = {
            'existing_count': len(self.existing_symbols),
            'new_verified_count': len(valid_new_symbols),
            'total_count': len(total_symbols)
        }

        logger.info(f"""
        ==========================================
        実在銘柄拡張完了
        ==========================================
        既存銘柄数: {results['existing_count']}
        新規追加銘柄数: {results['new_verified_count']}
        合計銘柄数: {results['total_count']}

        保存先: {output_file}
        ==========================================
        """)

        return results

def main():
    """メイン実行"""
    expander = VerifiedSymbolExpander()
    results = expander.expand_symbol_list()

    print(f"""
    ✅ 実在銘柄拡張完了

    📊 結果:
    - 既存: {results['existing_count']}銘柄
    - 新規追加: {results['new_verified_count']}銘柄
    - 合計: {results['total_count']}銘柄

    すべて実在・検証済みの銘柄です。
    """)

if __name__ == "__main__":
    main()