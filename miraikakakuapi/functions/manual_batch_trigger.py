#!/usr/bin/env python3
"""
手動バッチ実行 - ローカルからバッチ処理を直接実行してDBデータ充足
"""

from sqlalchemy import text
from database.database import get_db
import logging
import sys
import os
from datetime import datetime

# パスを追加
sys.path.append(os.path.dirname(os.path.abspath(__file__)))


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def execute_comprehensive_batch():
    """包括的バッチ処理の実行"""

    logger.info("🚀 手動バッチ処理開始")
    logger.info("=" * 80)

    # データベース接続確認
    try:
        db = next(get_db())
        result = db.execute(text("SELECT COUNT(*) FROM stock_master"))
        symbol_count = result.scalar()
        logger.info(f"✅ DB接続成功: {symbol_count:,}銘柄")
        db.close()
    except Exception as e:
        logger.error(f"❌ DB接続失敗: {e}")
        return False

    # バッチ処理スクリプト実行
    batch_scripts = [
        {
            "name": "fix_foreign_key_constraints",
            "script": "fix_foreign_key_constraints.py",
            "description": "外部キー制約修正",
            "priority": 1,
        },
        {
            "name": "turbo_expansion",
            "script": "turbo_expansion.py",
            "description": "89銘柄ターボ拡張",
            "priority": 2,
        },
        {
            "name": "comprehensive_batch",
            "script": "comprehensive_batch.py",
            "description": "8380銘柄包括処理",
            "priority": 3,
        },
        {
            "name": "ultimate_100_point_system",
            "script": "ultimate_100_point_system.py",
            "description": "2000銘柄×10年データ",
            "priority": 4,
        },
    ]

    successful_batches = []
    failed_batches = []

    for batch in batch_scripts:
        try:
            logger.info(f"📦 実行中: {batch['name']} - {batch['description']}")

            # Python スクリプト実行
            import subprocess

            cmd = [sys.executable, batch["script"]]
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=1800,  # 30分タイムアウト
                cwd=os.path.dirname(os.path.abspath(__file__)),
            )

            if result.returncode == 0:
                logger.info(f"  ✅ {batch['name']} 完了")
                successful_batches.append(batch["name"])
            else:
                logger.error(f"  ❌ {batch['name']} 失敗")
                logger.error(f"    STDERR: {result.stderr[-500:]}")  # 最後の500文字のみ
                failed_batches.append(batch["name"])

            # 進捗確認
            if result.returncode == 0:
                check_progress()

        except subprocess.TimeoutExpired:
            logger.error(f"  ⏱️  {batch['name']} タイムアウト")
            failed_batches.append(batch["name"])
        except Exception as e:
            logger.error(f"  💥 {batch['name']} エラー: {e}")
            failed_batches.append(batch["name"])

    # 結果サマリー
    logger.info("")
    logger.info("🎯 バッチ実行結果")
    logger.info("-" * 80)
    logger.info(f"  成功: {len(successful_batches)}個")
    for batch in successful_batches:
        logger.info(f"    ✅ {batch}")

    logger.info(f"  失敗: {len(failed_batches)}個")
    for batch in failed_batches:
        logger.info(f"    ❌ {batch}")

    return len(successful_batches) > 0


def check_progress():
    """進捗確認"""

    try:
        db = next(get_db())

        # 価格データ確認
        result = db.execute(
            text(
                """
            SELECT
                COUNT(DISTINCT symbol) as symbols,
                COUNT(*) as records
            FROM stock_prices
        """
            )
        )
        price_stats = result.fetchone()

        # 予測データ確認
        result = db.execute(text("SELECT COUNT(*) FROM stock_predictions"))
        pred_count = result.scalar()

        logger.info(f"  📊 現在のデータ状況:")
        logger.info(f"    価格データ: {price_stats[1]:,}件 ({price_stats[0]}銘柄)")
        logger.info(f"    予測データ: {pred_count:,}件")

        db.close()

    except Exception as e:
        logger.error(f"  ⚠️  進捗確認エラー: {e}")


def run_specific_batch(batch_name):
    """特定のバッチのみ実行"""

    logger.info(f"🎯 特定バッチ実行: {batch_name}")

    batch_map = {
        "fix_constraints": "fix_foreign_key_constraints.py",
        "turbo": "turbo_expansion.py",
        "comprehensive": "comprehensive_batch.py",
        "ultimate": "ultimate_100_point_system.py",
    }

    script = batch_map.get(batch_name)
    if not script:
        logger.error(f"❌ 未知のバッチ名: {batch_name}")
        return False

    try:
        import subprocess

        cmd = [sys.executable, script]
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=3600,  # 1時間
            cwd=os.path.dirname(os.path.abspath(__file__)),
        )

        if result.returncode == 0:
            logger.info(f"✅ {batch_name} 実行成功")
            check_progress()
            return True
        else:
            logger.error(f"❌ {batch_name} 実行失敗")
            logger.error(f"STDERR: {result.stderr[-1000:]}")
            return False

    except Exception as e:
        logger.error(f"💥 {batch_name} 実行エラー: {e}")
        return False


if __name__ == "__main__":
    if len(sys.argv) > 1:
        # 特定バッチ実行
        batch_name = sys.argv[1]
        success = run_specific_batch(batch_name)
    else:
        # 全バッチ実行
        success = execute_comprehensive_batch()

    if success:
        logger.info("🎉 バッチ処理完了!")

        # 最終データ状況確認
        logger.info("")
        logger.info("📈 最終データ状況")
        check_progress()
    else:
        logger.error("💥 バッチ処理で問題が発生しました")
