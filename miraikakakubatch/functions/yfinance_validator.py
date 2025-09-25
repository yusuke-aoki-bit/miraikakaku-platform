#!/usr/bin/env python3
"""
YFinance Real Symbol Validator
数百万銘柄からyfinanceで実在銘柄のみを抽出
"""

import yfinance as yf
import time
import logging
from typing import List, Set
import os
from concurrent.futures import ThreadPoolExecutor, as_completed

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class YFinanceValidator:
    """yfinance実在銘柄検証器"""

    def __init__(self):
        self.valid_symbols = set()
        self.processed_count = 0
        self.batch_size = 50

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

    def validate_symbol(self, symbol: str) -> bool:
        """yfinanceで銘柄検証"""
        try:
            ticker = yf.Ticker(symbol)

            # 短期間のヒストリカルデータ取得
            hist = ticker.history(period='5d', timeout=10)

            if not hist.empty and len(hist) > 0:
                latest_price = hist['Close'].iloc[-1]
                if latest_price > 0:
                    return True

        except Exception as e:
            # エラーの詳細をログに記録
            if "delisted" in str(e).lower():
                logger.debug(f"❌ {symbol}: 上場廃止")
            else:
                logger.debug(f"❌ {symbol}: {e}")

        return False

    def validate_batch(self, symbols: List[str]) -> List[str]:
        """バッチ検証"""
        valid_symbols = []

        for symbol in symbols:
            self.processed_count += 1

            if self.processed_count % 100 == 0:
                logger.info(f"🔄 進捗: {self.processed_count:,} (有効: {len(self.valid_symbols):,})")

            if self.validate_symbol(symbol):
                valid_symbols.append(symbol)
                self.valid_symbols.add(symbol)
                logger.info(f"✅ {symbol}")

            # レート制限対策
            time.sleep(0.1)

        return valid_symbols

    def smart_prioritization(self, all_symbols: List[str]) -> List[str]:
        """効率的優先順位付け"""
        logger.info("🧠 Smart Prioritization 開始")

        prioritized = []

        # 1. 実在可能性の高いパターンを優先
        high_priority_patterns = [
            # 米国株式 (3-5文字アルファベット)
            lambda s: len(s) >= 1 and len(s) <= 5 and s.isalpha() and not any(x in s for x in ['.', '-', '=']),

            # 東証 (.T)
            lambda s: s.endswith('.T') and len(s) <= 8,

            # ロンドン (.L)
            lambda s: s.endswith('.L') and len(s) <= 8,

            # 韓国 (.KS)
            lambda s: s.endswith('.KS') and len(s) <= 10,

            # 香港 (.HK)
            lambda s: s.endswith('.HK') and len(s) <= 8,

            # ドイツ (.DE)
            lambda s: s.endswith('.DE') and len(s) <= 8,

            # 暗号通貨 (-USD, -EUR)
            lambda s: '-USD' in s or '-EUR' in s or '-GBP' in s or '-JPY' in s,

            # FX (=X)
            lambda s: s.endswith('=X') and len(s) == 8,
        ]

        # 各パターンごとに銘柄を収集 (優先順)
        for i, pattern in enumerate(high_priority_patterns):
            matching = [s for s in all_symbols if pattern(s)]

            # 各パターンから最大2000銘柄
            sampled = matching[:2000]
            prioritized.extend(sampled)

            logger.info(f"📌 パターン{i+1}: {len(sampled):,}銘柄 (マッチ総数: {len(matching):,})")

        # 重複除去
        prioritized = list(set(prioritized))
        logger.info(f"🎯 優先検証対象: {len(prioritized):,}銘柄")

        return prioritized

    def parallel_validation(self, symbols: List[str], max_workers: int = 5) -> int:
        """並列検証実行"""
        logger.info(f"🚀 並列検証開始 (ワーカー数: {max_workers})")

        # バッチに分割
        batches = [symbols[i:i + self.batch_size]
                  for i in range(0, len(symbols), self.batch_size)]

        logger.info(f"📦 {len(batches):,}バッチに分割")

        # 時間制限: 最大500バッチ
        limited_batches = batches[:500]

        with ThreadPoolExecutor(max_workers=max_workers) as executor:
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
        output_file = '/mnt/c/Users/yuuku/cursor/miraikakaku/miraikakakubatch/yfinance_validated_symbols.txt'

        with open(output_file, 'w') as f:
            for symbol in sorted(self.valid_symbols):
                f.write(f"{symbol}\n")

        logger.info(f"💾 保存完了: {output_file}")
        logger.info(f"📊 検証済み銘柄数: {len(self.valid_symbols):,}")

def main():
    """メイン実行"""
    validator = YFinanceValidator()

    # 大規模銘柄リスト読み込み
    all_symbols = validator.load_massive_symbols()

    # 効率的優先順位付け
    prioritized_symbols = validator.smart_prioritization(all_symbols)

    # 並列検証実行
    validated_count = validator.parallel_validation(prioritized_symbols)

    # 結果保存
    validator.save_validated_symbols()

    print(f"""
    🎯 YFinance Validation 完了

    📊 結果:
    - 対象総数: {len(all_symbols):,}銘柄
    - 優先検証: {len(prioritized_symbols):,}銘柄
    - 処理済み: {validator.processed_count:,}銘柄
    - 実在確認: {validated_count:,}銘柄
    - 成功率: {(validated_count/validator.processed_count*100):.2f}%

    データソース: yfinance
    """)

if __name__ == "__main__":
    main()