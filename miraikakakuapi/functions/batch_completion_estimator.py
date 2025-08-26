#!/usr/bin/env python3
"""
バッチ完了予測 - 現在稼働中のバッチプロセスの完了予測時刻を算出
"""

import os
import sys
import logging
import re
from datetime import datetime, timedelta
from collections import defaultdict

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def analyze_progress_from_logs():
    """ログファイルから進捗を分析"""

    logger.info("📋 ログファイルから進捗分析中...")

    log_analysis = {}

    log_files = [
        {
            "file": "comprehensive_batch_bg.log",
            "name": "Comprehensive Batch",
            "target_count": 100,  # 処理対象銘柄数
            "typical_duration_hours": 4,
        },
        {
            "file": "turbo_expansion_bg.log",
            "name": "Turbo Expansion",
            "target_count": 89,
            "typical_duration_hours": 2,
        },
        {
            "file": "ultimate_system.log",
            "name": "Ultimate 100 Point System",
            "target_count": 2000,
            "typical_duration_hours": 12,
        },
        {
            "file": "instant_mega_boost.log",
            "name": "Instant Mega Boost",
            "target_count": 35,
            "typical_duration_hours": 1.5,
        },
        {
            "file": "quick_boost.log",
            "name": "Quick Boost",
            "target_count": 45,
            "typical_duration_hours": 1,
        },
        {
            "file": "continuous_247_restart.log",
            "name": "Continuous 247 Pipeline",
            "target_count": float("inf"),  # 無限ループ
            "typical_duration_hours": float("inf"),
        },
        {
            "file": "massive_expansion.log",
            "name": "Massive Data Expansion",
            "target_count": 1500,
            "typical_duration_hours": 8,
        },
    ]

    for log_info in log_files:
        log_file = log_info["file"]

        try:
            if not os.path.exists(log_file):
                log_analysis[log_info["name"]] = {
                    "status": "ログファイルなし",
                    "estimated_completion": "N/A",
                }
                continue

            with open(log_file, "r", encoding="utf-8") as f:
                content = f.read()
                lines = content.split("\n")

            # ファイル作成時刻
            file_start_time = datetime.fromtimestamp(os.path.getctime(log_file))
            file_age_hours = (datetime.now() - file_start_time).total_seconds() / 3600

            # 進捗パターンを検索
            progress_patterns = [
                r"\[(\d+)/(\d+)\]",  # [5/45] 形式
                r"処理中: (\w+)",  # 処理中: AAPL 形式
                r"✅ (\w+):",  # ✅ AAPL: 形式
                r"完了: (\d+)件",  # 完了: 123件 形式
            ]

            processed_count = 0
            total_target = log_info["target_count"]
            latest_activity = None
            success_count = 0
            error_count = 0

            processed_symbols = set()

            for line in lines:
                # 成功・エラーカウント
                if any(word in line for word in ["✅", "成功", "SUCCESS", "完了"]):
                    success_count += 1
                if any(
                    word in line.upper() for word in ["ERROR", "FAILED", "EXCEPTION"]
                ):
                    error_count += 1

                # 進捗パターンマッチング
                for pattern in progress_patterns:
                    match = re.search(pattern, line)
                    if match:
                        latest_activity = line.strip()

                        if pattern == r"\[(\d+)/(\d+)\]":
                            processed_count = int(match.group(1))
                            total_target = int(match.group(2))
                        elif pattern in [r"処理中: (\w+)", r"✅ (\w+):"]:
                            symbol = match.group(1)
                            processed_symbols.add(symbol)

            # シンボル数から進捗推定
            if processed_symbols:
                processed_count = len(processed_symbols)

            # 完了予測計算
            if total_target == float("inf"):
                estimated_completion = "継続実行（無限ループ）"
                progress_percent = "N/A"
            elif processed_count > 0 and total_target > processed_count:
                progress_percent = (processed_count / total_target) * 100

                # 処理速度計算
                if file_age_hours > 0:
                    processing_rate = processed_count / file_age_hours  # 件/時間
                    remaining_count = total_target - processed_count

                    if processing_rate > 0:
                        remaining_hours = remaining_count / processing_rate
                        estimated_completion_time = datetime.now() + timedelta(
                            hours=remaining_hours
                        )
                        estimated_completion = estimated_completion_time.strftime(
                            "%Y-%m-%d %H:%M:%S"
                        )
                    else:
                        estimated_completion = "速度不明"
                else:
                    estimated_completion = "開始直後"
            elif processed_count >= total_target:
                estimated_completion = "完了済み"
                progress_percent = 100
            else:
                # 典型的な実行時間から推定
                elapsed_ratio = file_age_hours / log_info["typical_duration_hours"]
                if elapsed_ratio < 1:
                    remaining_hours = (
                        log_info["typical_duration_hours"] - file_age_hours
                    )
                    estimated_completion_time = datetime.now() + timedelta(
                        hours=remaining_hours
                    )
                    estimated_completion = estimated_completion_time.strftime(
                        "%Y-%m-%d %H:%M:%S"
                    )
                    progress_percent = elapsed_ratio * 100
                else:
                    estimated_completion = "予定時間超過"
                    progress_percent = 100

            log_analysis[log_info["name"]] = {
                "file": log_file,
                "start_time": file_start_time,
                "running_hours": file_age_hours,
                "processed_count": processed_count,
                "total_target": (
                    total_target if total_target != float("inf") else "infinite"
                ),
                "progress_percent": progress_percent,
                "estimated_completion": estimated_completion,
                "latest_activity": latest_activity,
                "success_count": success_count,
                "error_count": error_count,
                "status": "稼働中" if file_age_hours < 2 else "長時間実行中",
            }

        except Exception as e:
            log_analysis[log_info["name"]] = {
                "status": f"分析エラー: {e}",
                "estimated_completion": "N/A",
            }

    return log_analysis


def generate_completion_report():
    """完了予測レポート生成"""

    logger.info("=" * 80)
    logger.info("⏰ バッチプロセス完了予測レポート")
    logger.info(f"📅 予測時刻: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    logger.info("=" * 80)

    analysis = analyze_progress_from_logs()

    # 完了予測一覧
    logger.info("🎯 各バッチプロセスの完了予測")
    logger.info("-" * 80)

    completion_times = []

    for name, info in analysis.items():
        if info.get("estimated_completion") == "N/A":
            continue

        logger.info(f"📦 {name}:")

        if "running_hours" in info:
            logger.info(f"  稼働時間: {info['running_hours']:.1f}時間")

        if "progress_percent" in info and info["progress_percent"] != "N/A":
            if isinstance(info["progress_percent"], (int, float)):
                logger.info(
                    f"  進捗: {info['progress_percent']:.1f}% ({info['processed_count']}/{info['total_target']})"
                )

        logger.info(f"  予想完了: {info['estimated_completion']}")

        if info.get("latest_activity"):
            activity = (
                info["latest_activity"][:60] + "..."
                if len(info["latest_activity"]) > 60
                else info["latest_activity"]
            )
            logger.info(f"  最新活動: {activity}")

        logger.info(
            f"  状態: ✅{info['success_count']}件成功, ❌{info['error_count']}件エラー"
        )

        # 完了時刻をリストに追加
        completion_str = info["estimated_completion"]
        if completion_str not in [
            "N/A",
            "継続実行（無限ループ）",
            "完了済み",
            "予定時間超過",
            "速度不明",
            "開始直後",
        ]:
            try:
                completion_time = datetime.strptime(completion_str, "%Y-%m-%d %H:%M:%S")
                completion_times.append((name, completion_time))
            except BaseException:
                pass

        logger.info("")

    # 全体完了予測
    logger.info("🏁 全体完了予測")
    logger.info("-" * 80)

    if completion_times:
        completion_times.sort(key=lambda x: x[1])

        logger.info("完了予定順:")
        for name, completion_time in completion_times:
            time_until = completion_time - datetime.now()
            if time_until.total_seconds() > 0:
                hours_until = time_until.total_seconds() / 3600
                logger.info(
                    f"  {completion_time.strftime('%H:%M')} - {name} (あと{hours_until:.1f}時間)"
                )
            else:
                logger.info(
                    f"  {completion_time.strftime('%H:%M')} - {name} (予定時刻経過)"
                )

        # 最後の完了予測
        last_completion = completion_times[-1][1]
        total_time_until = last_completion - datetime.now()

        if total_time_until.total_seconds() > 0:
            logger.info("")
            logger.info(
                f"🎉 全バッチ完了予測: {last_completion.strftime('%Y-%m-%d %H:%M:%S')}"
            )
            logger.info(f"   (あと約{total_time_until.total_seconds() / 3600:.1f}時間)")
        else:
            logger.info("")
            logger.info("🎉 主要バッチは完了予定時刻を経過")
            logger.info("   実際の処理状況を確認してください")
    else:
        logger.info("⚠️  明確な完了時刻を予測できるバッチがありません")
        logger.info("   継続実行型または分析不可能なプロセス")

    # 注意事項
    logger.info("")
    logger.info("📝 注意事項")
    logger.info("-" * 80)
    logger.info("• Continuous 247 Pipelineは24/7継続実行設計")
    logger.info("• Ultimate 100 Point Systemは大規模処理のため時間変動大")
    logger.info("• エラー発生時は処理時間が延長される可能性あり")
    logger.info("• 予測は現在の処理速度に基づく推定値")

    logger.info("=" * 80)

    return analysis


if __name__ == "__main__":
    analysis_results = generate_completion_report()
    logger.info("⏰ 完了予測分析完了")
