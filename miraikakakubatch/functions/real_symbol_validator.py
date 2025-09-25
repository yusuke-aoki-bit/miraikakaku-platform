#!/usr/bin/env python3
"""
Real Symbol Validator
数百万銘柄から実在銘柄のみを抽出
pandas-datareader + yfinance 併用検証
"""

import yfinance as yf
import pandas_datareader as pdr
import pandas as pd
import time
import logging
from typing import List, Set
import os
from concurrent.futures import ThreadPoolExecutor, as_completed
import numpy as np

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class RealSymbolValidator:
    """実在銘柄検証器"""

    def __init__(self):
        self.valid_symbols = set()
        self.processed_count = 0
        self.batch_size = 100

    def load_massive_symbols(self) -> List[str]:
        """大規模銘柄リスト読み込み"""
        all_symbols = set()

        massive_files = [
            '/mnt/c/Users/yuuku/cursor/miraikakaku/miraikakakubatch/definitive_massive_symbols.txt',
            '/mnt/c/Users/yuuku/cursor/miraikakaku/miraikakakubatch/ultra_massive_symbols.txt',
            '/mnt/c/Users/yuuku/cursor/miraikakaku/miraikakakubatch/global_massive_symbols.txt'
        ]

        for file_path in massive_files:
            try:
                with open(file_path, 'r') as f:
                    symbols = [line.strip() for line in f if line.strip()]
                    all_symbols.update(symbols)
                    logger.info(f"✅ {os.path.basename(file_path)}: {len(symbols):,}銘柄読み込み")
            except Exception as e:
                logger.warning(f"⚠️ {file_path}読み込みエラー: {e}")

        logger.info(f"📊 総銘柄数: {len(all_symbols):,}")
        return list(all_symbols)

    def validate_with_yfinance(self, symbol: str) -> bool:
        """yfinanceで検証"""
        try:
            ticker = yf.Ticker(symbol)
            hist = ticker.history(period='5d', timeout=5)

            if not hist.empty and len(hist) > 0:
                latest_price = hist['Close'].iloc[-1]
                if pd.notna(latest_price) and latest_price > 0:
                    return True
        except Exception:
            pass
        return False

    def validate_with_pandas_datareader(self, symbol: str) -> bool:
        """pandas-datareaderで検証"""
        try:
            # Yahoo Finance経由
            data = pdr.get_data_yahoo(symbol, start='2024-09-01', end='2024-09-15')

            if not data.empty and len(data) > 0:
                latest_price = data['Close'].iloc[-1]
                if pd.notna(latest_price) and latest_price > 0:
                    return True
        except Exception:
            pass
        return False

    def validate_symbol_comprehensive(self, symbol: str) -> bool:
        """包括的検証 (yfinance + pandas-datareader)"""
        # まずyfinanceで高速チェック
        if self.validate_with_yfinance(symbol):
            return True

        # yfinanceで失敗した場合、pandas-datareaderで再検証
        time.sleep(0.1)  # レート制限対策
        return self.validate_with_pandas_datareader(symbol)

    def validate_batch(self, symbols: List[str]) -> List[str]:
        """バッチ検証"""
        valid_symbols = []

        for symbol in symbols:
            self.processed_count += 1

            if self.processed_count % 100 == 0:
                logger.info(f"🔄 進捗: {self.processed_count:,} (有効: {len(self.valid_symbols):,})")

            if self.validate_symbol_comprehensive(symbol):
                valid_symbols.append(symbol)
                self.valid_symbols.add(symbol)
                logger.debug(f"✅ {symbol}")
            else:
                logger.debug(f"❌ {symbol}")

            # レート制限対策
            time.sleep(0.05)

        return valid_symbols

    def parallel_validation(self, all_symbols: List[str], max_workers: int = 10) -> int:
        """並列検証実行"""
        logger.info(f"🚀 並列検証開始 (ワーカー数: {max_workers})")

        # バッチに分割
        batches = [all_symbols[i:i + self.batch_size]
                  for i in range(0, len(all_symbols), self.batch_size)]

        logger.info(f"📦 {len(batches):,}バッチに分割")

        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            # 最初の1000バッチのみ処理 (時間制限)
            limited_batches = batches[:1000]

            futures = {executor.submit(self.validate_batch, batch): i
                      for i, batch in enumerate(limited_batches)}

            for future in as_completed(futures):
                batch_idx = futures[future]
                try:
                    valid_batch = future.result()
                    logger.info(f"📊 バッチ{batch_idx}完了: {len(valid_batch)}銘柄有効")
                except Exception as e:
                    logger.error(f"❌ バッチ{batch_idx}エラー: {e}")

        return len(self.valid_symbols)

    def save_validated_symbols(self):
        """検証済み銘柄保存"""
        output_file = '/mnt/c/Users/yuuku/cursor/miraikakaku/miraikakakubatch/validated_real_symbols.txt'

        with open(output_file, 'w') as f:
            for symbol in sorted(self.valid_symbols):
                f.write(f"{symbol}\n")

        logger.info(f"💾 保存完了: {output_file}")
        logger.info(f"📊 検証済み銘柄数: {len(self.valid_symbols):,}")

    def smart_validation_strategy(self, all_symbols: List[str]) -> int:
        """効率的検証戦略"""
        logger.info("🧠 Smart Validation Strategy 開始")

        # 1. 実在可能性の高い銘柄を優先
        priority_patterns = [
            lambda s: len(s) == 4 and s.isalpha(),  # 4文字アルファベット
            lambda s: len(s) <= 5 and s.endswith('.T'),  # 東証
            lambda s: len(s) <= 5 and s.endswith('.L'),  # ロンドン
            lambda s: len(s) <= 8 and '.KS' in s,  # 韓国
            lambda s: len(s) <= 8 and '.HK' in s,  # 香港
            lambda s: '-USD' in s or '-EUR' in s,  # 暗号通貨
            lambda s: '=X' in s,  # FX
        ]

        prioritized_symbols = []

        for pattern in priority_patterns:
            matching_symbols = [s for s in all_symbols if pattern(s)]
            prioritized_symbols.extend(matching_symbols[:5000])  # 各パターン5000銘柄まで

        # 重複除去
        prioritized_symbols = list(set(prioritized_symbols))
        logger.info(f"🎯 優先検証対象: {len(prioritized_symbols):,}銘柄")

        # 並列検証実行
        return self.parallel_validation(prioritized_symbols)

def main():
    """メイン実行"""
    validator = RealSymbolValidator()

    # 大規模銘柄リスト読み込み
    all_symbols = validator.load_massive_symbols()

    # 効率的検証実行
    validated_count = validator.smart_validation_strategy(all_symbols)

    # 結果保存
    validator.save_validated_symbols()

    print(f"""
    🎯 Real Symbol Validation 完了

    📊 結果:
    - 検証対象: {len(all_symbols):,}銘柄
    - 処理済み: {validator.processed_count:,}銘柄
    - 実在確認: {validated_count:,}銘柄
    - 成功率: {(validated_count/validator.processed_count*100):.2f}%

    データソース: yfinance + pandas-datareader
    """)

if __name__ == "__main__":
    main()