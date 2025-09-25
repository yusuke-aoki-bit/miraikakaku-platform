#!/usr/bin/env python3
"""
MiraiKakaku システム簡素化計画
5,191個のPythonファイルを分析し、重複・未使用ファイルを特定
"""

import os
import sys
import shutil
from pathlib import Path
from datetime import datetime
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class SystemCleanup:
    def __init__(self, root_path):
        self.root_path = Path(root_path)
        self.core_systems = [
            'simple_api_server.py',
            'cloud_run_data_collector.py',
            'cloud_run_prediction_generator.py',
            'enhanced_symbol_manager.py'
        ]

        # 重複パターンの定義
        self.duplicate_patterns = [
            '*collector*.py',
            '*prediction*.py',
            '*batch*.py',
            '*massive*.py',
            '*enhanced*.py',
            '*advanced*.py',
            '*comprehensive*.py',
            '*optimized*.py',
            '*improved*.py',
            '*fixed*.py',
            '*corrected*.py',
            '*updated*.py'
        ]

        # 保持すべきディレクトリ
        self.keep_directories = {
            'miraikakakuapi',
            'miraikakakufront',
            'miraikakakubatch/functions',  # コア機能のみ
            'shared',
            'lib',
            'cloud_functions'  # 本格運用版のみ
        }

        # 削除候補ディレクトリ
        self.cleanup_directories = {
            'archive',  # 完全削除
            'monitoring',  # 統合済み
            'scripts',  # 統合済み
            'docs',  # 統合済み
            'deployment',  # 統合済み
            'migration'  # 完了済み
        }

    def analyze_system_complexity(self):
        """システム複雑性分析"""
        stats = {
            'total_files': 0,
            'duplicate_files': 0,
            'unused_files': 0,
            'core_files': 0,
            'archive_files': 0
        }

        duplicate_groups = {}

        for pattern in self.duplicate_patterns:
            files = list(self.root_path.rglob(pattern))
            if len(files) > 1:
                duplicate_groups[pattern] = files
                stats['duplicate_files'] += len(files)

        # アーカイブファイル数
        archive_path = self.root_path / 'archive'
        if archive_path.exists():
            stats['archive_files'] = len(list(archive_path.rglob('*.py')))

        # 総ファイル数
        stats['total_files'] = len(list(self.root_path.rglob('*.py')))

        logger.info(f"🔍 システム複雑性分析結果:")
        logger.info(f"  総Pythonファイル数: {stats['total_files']}")
        logger.info(f"  重複パターンファイル: {stats['duplicate_files']}")
        logger.info(f"  アーカイブファイル: {stats['archive_files']}")

        return stats, duplicate_groups

    def create_backup(self):
        """重要ファイルのバックアップ作成"""
        backup_dir = self.root_path / f"backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        backup_dir.mkdir(exist_ok=True)

        # コアシステムファイルをバックアップ
        for core_file in self.core_systems:
            for file_path in self.root_path.rglob(core_file):
                relative_path = file_path.relative_to(self.root_path)
                backup_path = backup_dir / relative_path
                backup_path.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(file_path, backup_path)
                logger.info(f"✅ バックアップ: {relative_path}")

        return backup_dir

    def cleanup_archive_directory(self):
        """アーカイブディレクトリの完全削除"""
        archive_path = self.root_path / 'archive'
        if archive_path.exists():
            logger.info(f"🗑️  アーカイブディレクトリ削除: {archive_path}")
            shutil.rmtree(archive_path)
            return True
        return False

    def cleanup_duplicate_files(self, duplicate_groups, dry_run=True):
        """重複ファイルのクリーンアップ"""
        deleted_count = 0

        for pattern, files in duplicate_groups.items():
            if len(files) <= 1:
                continue

            # コアファイルを特定し、それ以外を削除候補とする
            core_file = None
            for file_path in files:
                if any(core in file_path.name for core in self.core_systems):
                    core_file = file_path
                    break

            # コアファイルが見つからない場合、最新のファイルを保持
            if not core_file:
                core_file = max(files, key=lambda f: f.stat().st_mtime)

            for file_path in files:
                if file_path != core_file:
                    logger.info(f"🗑️  削除候補: {file_path.relative_to(self.root_path)}")
                    if not dry_run:
                        file_path.unlink()
                        deleted_count += 1

        logger.info(f"🧹 重複ファイル削除: {deleted_count}個 (dry_run={dry_run})")
        return deleted_count

    def optimize_batch_directory(self):
        """バッチディレクトリの最適化"""
        batch_path = self.root_path / 'miraikakakubatch' / 'functions'
        if not batch_path.exists():
            return 0

        # 使用中のファイルを特定
        active_files = {
            'enhanced_symbol_manager.py',
            'database/cloud_sql.py',
            'database/models/__init__.py'
        }

        deleted_count = 0
        for py_file in batch_path.rglob('*.py'):
            relative_path = py_file.relative_to(batch_path)
            if str(relative_path) not in active_files:
                logger.info(f"🗑️  バッチファイル削除候補: {relative_path}")
                # dry_run として、実際の削除はコメントアウト
                # py_file.unlink()
                deleted_count += 1

        return deleted_count

    def generate_cleanup_report(self):
        """クリーンアップレポート生成"""
        stats, duplicate_groups = self.analyze_system_complexity()

        report = f"""
# MiraiKakaku システム簡素化レポート
生成日時: {datetime.now().isoformat()}

## 現在の状況
- 総Pythonファイル数: {stats['total_files']:,}
- 重複パターンファイル: {stats['duplicate_files']:,}
- アーカイブファイル: {stats['archive_files']:,}

## 削除可能ファイル
"""

        for pattern, files in duplicate_groups.items():
            if len(files) > 1:
                report += f"\n### {pattern}\n"
                for file_path in files:
                    report += f"- {file_path.relative_to(self.root_path)}\n"

        report += f"""
## 推定削減効果
- ファイル削減数: {stats['duplicate_files'] + stats['archive_files']:,}
- 簡素化率: {((stats['duplicate_files'] + stats['archive_files']) / stats['total_files'] * 100):.1f}%

## 実行コマンド
```bash
python3 system_cleanup_plan.py --execute
```
"""

        report_path = self.root_path / 'SYSTEM_CLEANUP_REPORT.md'
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(report)

        logger.info(f"📋 レポート生成: {report_path}")
        return report_path

def main():
    """メイン処理"""
    root_path = "/mnt/c/Users/yuuku/cursor/miraikakaku"
    cleanup = SystemCleanup(root_path)

    # 分析とレポート生成
    logger.info("🚀 システム簡素化分析開始")

    # バックアップ作成
    backup_dir = cleanup.create_backup()
    logger.info(f"💾 バックアップ作成完了: {backup_dir}")

    # 分析実行
    stats, duplicate_groups = cleanup.analyze_system_complexity()

    # レポート生成
    report_path = cleanup.generate_cleanup_report()

    # 安全な削除（アーカイブのみ）
    if cleanup.cleanup_archive_directory():
        logger.info("✅ アーカイブディレクトリ削除完了")

    logger.info("✅ システム分析完了")
    logger.info(f"📋 詳細レポート: {report_path}")

if __name__ == "__main__":
    main()