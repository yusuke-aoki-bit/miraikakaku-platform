#!/usr/bin/env python3
"""
更新されたバッチスケジューラー - 修正済みスクリプトを使用
"""

import subprocess
import logging
from datetime import datetime
import os

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def run_data_collection():
    """修正済みデータ収集スクリプトを実行"""
    try:
        logger.info("🚀 修正済みデータ収集システム開始")

        # Step 1: リアルタイム価格更新 (修正済み)
        logger.info("=== 📈 リアルタイム価格更新 ===")
        result1 = subprocess.run([
            'python3', '/mnt/c/Users/yuuku/cursor/miraikakaku/miraikakakubatch/functions/realtime_price_updater.py'
        ], capture_output=True, text=True, timeout=300)

        if result1.returncode == 0:
            logger.info("✅ リアルタイム価格更新完了")
        else:
            logger.error(f"❌ リアルタイム価格更新エラー: {result1.stderr}")

        # Step 2: 拡張シンボル収集
        logger.info("=== 🌟 拡張シンボル収集 ===")
        result2 = subprocess.run([
            'python3', '/mnt/c/Users/yuuku/cursor/miraikakaku/miraikakakubatch/functions/expanded_symbol_collector.py'
        ], capture_output=True, text=True, timeout=600)

        if result2.returncode == 0:
            logger.info("✅ 拡張シンボル収集完了")
        else:
            logger.error(f"❌ 拡張シンボル収集エラー: {result2.stderr}")

        # Step 3: 生産データ収集 (修正済み)
        logger.info("=== 🏭 生産データ収集 ===")
        result3 = subprocess.run([
            'python3', '/mnt/c/Users/yuuku/cursor/miraikakaku/miraikakakubatch/functions/production_data_collector.py'
        ], capture_output=True, text=True, timeout=400)

        if result3.returncode == 0:
            logger.info("✅ 生産データ収集完了")
        else:
            logger.error(f"❌ 生産データ収集エラー: {result3.stderr}")

        logger.info("🎉 全体データ収集プロセス完了")

        # 結果レポート
        success_count = sum([
            1 for result in [result1, result2, result3]
            if result.returncode == 0
        ])

        logger.info(f"📊 実行結果: {success_count}/3 スクリプト成功")

        return success_count >= 2  # 2つ以上成功すればOK

    except Exception as e:
        logger.error(f"❌ データ収集プロセスエラー: {e}")
        return False

def main():
    """メインプロセス"""
    logger.info(f"🕐 バッチ実行開始: {datetime.now()}")

    success = run_data_collection()

    if success:
        logger.info("✅ バッチ実行成功")
    else:
        logger.error("❌ バッチ実行失敗")

    logger.info(f"🕐 バッチ実行終了: {datetime.now()}")

if __name__ == "__main__":
    main()