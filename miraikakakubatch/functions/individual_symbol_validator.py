#!/usr/bin/env python3
"""
個別銘柄検証システム
1つずつ確実に検証して1000銘柄以上を収集
"""

import yfinance as yf
import time
import logging
from typing import List, Set
import os

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class IndividualSymbolValidator:
    """個別銘柄検証クラス"""

    def __init__(self):
        self.existing_symbols = self.load_existing_symbols()
        self.valid_symbols = []

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

    def get_all_potential_symbols(self) -> List[str]:
        """潜在的な全銘柄リストを取得"""
        all_symbols = []

        # S&P 500主要銘柄（実在確認済み）
        sp500_core = [
            'AAPL', 'MSFT', 'GOOGL', 'GOOG', 'AMZN', 'NVDA', 'TSLA', 'META', 'AVGO', 'ORCL',
            'JPM', 'V', 'JNJ', 'WMT', 'PG', 'UNH', 'MA', 'HD', 'DIS', 'BAC',
            'PYPL', 'NFLX', 'ADBE', 'CRM', 'PFE', 'ABBV', 'TMO', 'CSCO', 'ACN', 'CVX',
            'PEP', 'NKE', 'COST', 'WFC', 'MRK', 'LLY', 'XOM', 'VZ', 'TXN', 'NEE',
            'T', 'ABT', 'DHR', 'BMY', 'PM', 'LOW', 'CVS', 'RTX', 'MS', 'SCHW',
            'HON', 'UPS', 'AMD', 'INTC', 'IBM', 'BLK', 'GS', 'CAT', 'NOW', 'DE',
            'SPGI', 'AXP', 'LMT', 'C', 'INTU', 'MU', 'GILD', 'BA', 'ISRG', 'MMM',
            'TGT', 'GE', 'ADI', 'SYK', 'MDLZ', 'BKNG', 'CI', 'ADP', 'PLD', 'AMT'
        ]

        # NASDAQ 100銘柄
        nasdaq100 = [
            'ABNB', 'ADSK', 'AEP', 'ALGN', 'AMAT', 'AMGN', 'ANSS', 'ASML', 'ATVI', 'AVGO',
            'AZN', 'BIIB', 'BKNG', 'CDNS', 'CEG', 'CHTR', 'CMCSA', 'CPRT', 'CRWD', 'CSGP',
            'CTAS', 'CTSH', 'DDOG', 'DLTR', 'DXCM', 'EA', 'EBAY', 'ENPH', 'EXC', 'FANG',
            'FAST', 'FISV', 'FTNT', 'GEHC', 'GFS', 'GILD', 'GOOGL', 'GOOG', 'HON', 'IDXX',
            'ILMN', 'INTC', 'INTU', 'ISRG', 'KDP', 'KHC', 'KLAC', 'LCID', 'LRCX', 'LULU',
            'MAR', 'MCHP', 'MDLZ', 'MELI', 'META', 'MNST', 'MRNA', 'MRVL', 'MSFT', 'MU',
            'NFLX', 'NVDA', 'NXPI', 'ODFL', 'ON', 'ORLY', 'PANW', 'PAYX', 'PCAR', 'PDD',
            'PEP', 'PYPL', 'QCOM', 'REGN', 'RIVN', 'ROST', 'SBUX', 'SGEN', 'SIRI', 'SNPS',
            'TEAM', 'TMUS', 'TSLA', 'TXN', 'VRSK', 'VRTX', 'WBA', 'WBD', 'WDAY', 'XEL',
            'ZM', 'ZS'
        ]

        # Dow Jones Industrial Average (30銘柄)
        djia = [
            'AXP', 'AMGN', 'AAPL', 'BA', 'CAT', 'CSCO', 'CVX', 'GS', 'HD', 'HON',
            'IBM', 'INTC', 'JNJ', 'KO', 'JPM', 'MCD', 'MMM', 'MRK', 'MSFT', 'NKE',
            'PG', 'TRV', 'UNH', 'CRM', 'VZ', 'V', 'WBA', 'WMT', 'DIS', 'DOW'
        ]

        # Russell 1000主要銘柄
        russell1000 = [
            'A', 'AAL', 'AAP', 'AAPL', 'ABBV', 'ABC', 'ABMD', 'ABT', 'ACN', 'ADBE',
            'ADI', 'ADM', 'ADP', 'ADSK', 'AEE', 'AEP', 'AES', 'AFL', 'AIG', 'AIZ',
            'AJG', 'AKAM', 'ALB', 'ALGN', 'ALK', 'ALL', 'ALLE', 'ALXN', 'AMAT', 'AMCR',
            'AMD', 'AME', 'AMGN', 'AMP', 'AMT', 'AMZN', 'ANET', 'ANSS', 'ANTM', 'AON',
            'AOS', 'APA', 'APD', 'APH', 'APTV', 'ARE', 'ATO', 'ATVI', 'AVB', 'AVGO',
            'AVY', 'AWK', 'AXP', 'AZO', 'BA', 'BAC', 'BAX', 'BBY', 'BDX', 'BEN',
            'BF.B', 'BIIB', 'BIO', 'BK', 'BKNG', 'BKR', 'BLK', 'BLL', 'BMY', 'BR',
            'BRK.B', 'BRO', 'BSX', 'BWA', 'BXP', 'C', 'CAG', 'CAH', 'CARR', 'CAT',
            'CB', 'CBOE', 'CBRE', 'CCI', 'CCL', 'CDNS', 'CDW', 'CE', 'CERN', 'CF',
            'CFG', 'CHD', 'CHRW', 'CHTR', 'CI', 'CINF', 'CL', 'CLX', 'CMA', 'CMCSA',
            'CME', 'CMG', 'CMI', 'CMS', 'CNC', 'CNP', 'COF', 'COG', 'COO', 'COP',
            'COST', 'CPB', 'CPRT', 'CRM', 'CSCO', 'CSX', 'CTAS', 'CTLT', 'CTSH', 'CTVA',
            'CTXS', 'CVS', 'CVX', 'CZR', 'D', 'DAL', 'DD', 'DE', 'DFS', 'DG',
            'DGX', 'DHI', 'DHR', 'DIS', 'DISCA', 'DISCK', 'DISH', 'DLR', 'DLTR', 'DOV'
        ]

        # 人気のある個別株
        popular_stocks = [
            'GME', 'AMC', 'BB', 'PLTR', 'SOFI', 'HOOD', 'LCID', 'RIVN', 'NIO', 'XPEV',
            'LI', 'SPCE', 'COIN', 'RBLX', 'DKNG', 'PENN', 'SKLZ', 'WISH', 'CLOV', 'CLNE',
            'BNGO', 'OCGN', 'MVIS', 'SENS', 'ATER', 'BBIG', 'PROG', 'CEI', 'SNDL', 'TLRY',
            'ACB', 'CGC', 'CRON', 'HEXO', 'OGI', 'APHA', 'MJ', 'YOLO', 'THCX', 'POTX'
        ]

        # 主要ETF
        major_etfs = [
            'SPY', 'QQQ', 'IWM', 'DIA', 'VOO', 'VTI', 'EEM', 'XLF', 'XLK', 'XLE',
            'XLV', 'XLI', 'XLY', 'XLP', 'XLB', 'XLRE', 'XLU', 'VNQ', 'AGG', 'TLT',
            'GLD', 'SLV', 'USO', 'UNG', 'VXX', 'UVXY', 'TQQQ', 'SQQQ', 'SPXL', 'SPXS',
            'ARKK', 'ARKQ', 'ARKW', 'ARKG', 'ARKF', 'ARKX', 'ICLN', 'TAN', 'LIT', 'HACK',
            'VEA', 'VWO', 'EFA', 'IEFA', 'IEMG', 'EWJ', 'EWZ', 'FXI', 'INDA', 'EWG'
        ]

        # 国際株式
        international = [
            # カナダ
            'SHOP', 'TD', 'RY', 'BNS', 'BMO', 'CNQ', 'SU', 'CP', 'CNR', 'BCE',
            # 中国ADR
            'BABA', 'JD', 'BIDU', 'NIO', 'XPEV', 'LI', 'PDD', 'BILI', 'IQ', 'VIPS',
            'TME', 'WB', 'NTES', 'EDU', 'TAL', 'YMM', 'FUTU', 'TIGR', 'DIDI', 'BEKE',
            # 欧州ADR
            'SAP', 'ASML', 'NVO', 'AZN', 'TM', 'TSM', 'SNY', 'GSK', 'BP', 'SHEL',
            'TOT', 'DEO', 'BUD', 'UL', 'RIO', 'VALE', 'BTI', 'NVS', 'RHHBY', 'BACHY',
            # その他
            'SE', 'MELI', 'STNE', 'PAGS', 'NU', 'GRAB', 'CPNG', 'COUPANG'
        ]

        # すべて結合
        all_symbols.extend(sp500_core)
        all_symbols.extend(nasdaq100)
        all_symbols.extend(djia)
        all_symbols.extend(russell1000)
        all_symbols.extend(popular_stocks)
        all_symbols.extend(major_etfs)
        all_symbols.extend(international)

        # 重複除去
        unique_symbols = list(set(all_symbols))
        return unique_symbols

    def validate_symbol(self, symbol: str) -> bool:
        """個別銘柄を検証"""
        try:
            ticker = yf.Ticker(symbol)
            hist = ticker.history(period='5d')

            if not hist.empty and len(hist) > 0:
                latest_price = hist['Close'].iloc[-1]
                if latest_price > 0:
                    return True
        except:
            pass
        return False

    def validate_all_symbols(self):
        """全銘柄を個別検証"""
        potential_symbols = self.get_all_potential_symbols()

        # 既存銘柄を除外
        new_symbols = [s for s in potential_symbols if s not in self.existing_symbols]

        logger.info(f"検証対象: {len(new_symbols)}銘柄")

        valid_count = 0
        invalid_count = 0

        for i, symbol in enumerate(new_symbols, 1):
            if i % 50 == 0:
                logger.info(f"進捗: {i}/{len(new_symbols)} ({valid_count}銘柄有効)")

            if self.validate_symbol(symbol):
                self.valid_symbols.append(symbol)
                valid_count += 1
                logger.debug(f"✅ {symbol}")
            else:
                invalid_count += 1
                logger.debug(f"❌ {symbol}")

            # レート制限対策
            time.sleep(0.1)

        logger.info(f"検証完了: {valid_count}銘柄有効, {invalid_count}銘柄無効")

        # 既存と結合
        total_symbols = list(self.existing_symbols) + self.valid_symbols

        # ファイル保存
        output_file = '/mnt/c/Users/yuuku/cursor/miraikakaku/miraikakakubatch/expanded_1000_symbols.txt'
        with open(output_file, 'w') as f:
            for symbol in sorted(total_symbols):
                f.write(f"{symbol}\n")

        return {
            'existing': len(self.existing_symbols),
            'new': len(self.valid_symbols),
            'total': len(total_symbols)
        }

def main():
    """メイン実行"""
    validator = IndividualSymbolValidator()
    results = validator.validate_all_symbols()

    print(f"""
    ✅ 個別検証完了

    📊 結果:
    - 既存: {results['existing']}銘柄
    - 新規: {results['new']}銘柄
    - 合計: {results['total']}銘柄

    目標1000銘柄: {'✅ 達成!' if results['total'] >= 1000 else '❌ 未達成'}
    """)

if __name__ == "__main__":
    main()