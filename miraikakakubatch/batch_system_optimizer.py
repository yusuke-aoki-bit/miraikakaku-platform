#!/usr/bin/env python3
"""
バッチシステム最適化ツール
Batch System Optimizer

大量のPythonファイルを整理し、重複やレガシーコードを削除する
"""

import os
import shutil
import hashlib
from pathlib import Path
from typing import Dict, List, Set, Tuple
import ast
import re
from datetime import datetime, timedelta

class BatchSystemOptimizer:
    """バッチシステム最適化クラス"""

    def __init__(self, batch_dir: str = "functions"):
        self.batch_dir = Path(batch_dir)
        self.archive_dir = Path("legacy")
        self.duplicate_files: Dict[str, List[Path]] = {}
        self.outdated_files: List[Path] = []
        self.large_files: List[Tuple[Path, int]] = []
        self.active_files: Set[Path] = set()

    def analyze_file_system(self) -> Dict[str, any]:
        """ファイルシステムを分析"""
        if not self.batch_dir.exists():
            return {"error": "Batch directory not found"}

        python_files = list(self.batch_dir.rglob("*.py"))
        total_files = len(python_files)
        total_size = sum(f.stat().st_size for f in python_files)

        print(f"📊 Analysis Results:")
        print(f"   Total Python files: {total_files}")
        print(f"   Total size: {total_size / 1024 / 1024:.2f} MB")

        # ファイル重複チェック
        self._find_duplicate_files(python_files)

        # 古いファイルをチェック
        self._find_outdated_files(python_files)

        # 大きなファイルをチェック
        self._find_large_files(python_files)

        # アクティブファイルを特定
        self._identify_active_files(python_files)

        return {
            "total_files": total_files,
            "total_size_mb": total_size / 1024 / 1024,
            "duplicates": len(self.duplicate_files),
            "outdated": len(self.outdated_files),
            "large_files": len(self.large_files),
            "active_files": len(self.active_files)
        }

    def _find_duplicate_files(self, files: List[Path]):
        """重複ファイルを検索"""
        file_hashes: Dict[str, List[Path]] = {}

        for file_path in files:
            try:
                with open(file_path, 'rb') as f:
                    content = f.read()
                    file_hash = hashlib.md5(content).hexdigest()

                if file_hash not in file_hashes:
                    file_hashes[file_hash] = []
                file_hashes[file_hash].append(file_path)
            except:
                continue

        # 重複があるものを抽出
        self.duplicate_files = {
            hash_val: paths for hash_val, paths in file_hashes.items()
            if len(paths) > 1
        }

        if self.duplicate_files:
            print(f"\n🔍 Found {len(self.duplicate_files)} groups of duplicate files:")
            for i, (hash_val, paths) in enumerate(self.duplicate_files.items()):
                if i < 5:  # 最初の5つだけ表示
                    print(f"   Group {i+1}: {len(paths)} files")
                    for path in paths:
                        print(f"     - {path}")

    def _find_outdated_files(self, files: List[Path]):
        """古いファイルを検索（90日以上更新されていない）"""
        cutoff_date = datetime.now() - timedelta(days=90)

        for file_path in files:
            try:
                stat = file_path.stat()
                mod_time = datetime.fromtimestamp(stat.st_mtime)

                # ファイル名から古いパターンを検出
                outdated_patterns = [
                    'old_', 'backup_', 'temp_', 'test_', 'debug_',
                    '_old', '_backup', '_temp', '_test', '_debug',
                    '2024', '2023', '_v1', '_v2', '_v3'
                ]

                is_outdated = (
                    mod_time < cutoff_date or
                    any(pattern in file_path.name.lower() for pattern in outdated_patterns)
                )

                if is_outdated:
                    self.outdated_files.append(file_path)
            except:
                continue

        print(f"\n📅 Found {len(self.outdated_files)} potentially outdated files")

    def _find_large_files(self, files: List[Path]):
        """大きなファイルを検索（1MB以上）"""
        for file_path in files:
            try:
                size = file_path.stat().st_size
                if size > 1024 * 1024:  # 1MB以上
                    self.large_files.append((file_path, size))
            except:
                continue

        self.large_files.sort(key=lambda x: x[1], reverse=True)

        if self.large_files:
            print(f"\n📦 Found {len(self.large_files)} large files (>1MB):")
            for i, (path, size) in enumerate(self.large_files[:5]):
                print(f"   {i+1}. {path} ({size / 1024 / 1024:.2f} MB)")

    def _identify_active_files(self, files: List[Path]):
        """アクティブファイルを特定"""
        active_patterns = [
            'main', 'production', 'enhanced', 'improved', 'stable',
            'final', 'comprehensive', 'advanced', 'optimized'
        ]

        recent_date = datetime.now() - timedelta(days=30)

        for file_path in files:
            try:
                stat = file_path.stat()
                mod_time = datetime.fromtimestamp(stat.st_mtime)

                # 最近更新されたか、重要なファイル名パターンを含む
                is_active = (
                    mod_time > recent_date or
                    any(pattern in file_path.name.lower() for pattern in active_patterns) or
                    self._has_recent_imports(file_path)
                )

                if is_active:
                    self.active_files.add(file_path)
            except:
                continue

        print(f"\n✅ Identified {len(self.active_files)} active files")

    def _has_recent_imports(self, file_path: Path) -> bool:
        """最新のライブラリやモジュールをインポートしているかチェック"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            modern_patterns = [
                'from dataclasses import',
                'from typing import',
                'async def',
                'await ',
                'from pathlib import',
                'from datetime import',
                'logging.getLogger',
                'with open('
            ]

            return any(pattern in content for pattern in modern_patterns)
        except:
            return False

    def create_optimization_plan(self) -> Dict[str, any]:
        """最適化プランを作成"""
        plan = {
            "actions": [],
            "potential_savings": 0,
            "files_to_archive": 0,
            "files_to_remove": 0
        }

        # 重複ファイルの処理
        for hash_val, paths in self.duplicate_files.items():
            if len(paths) > 1:
                # 最新のファイルを1つ残し、他をアーカイブ
                newest = max(paths, key=lambda p: p.stat().st_mtime)
                duplicates = [p for p in paths if p != newest]

                plan["actions"].append({
                    "action": "archive_duplicates",
                    "keep": str(newest),
                    "archive": [str(p) for p in duplicates],
                    "savings_mb": sum(p.stat().st_size for p in duplicates) / 1024 / 1024
                })

                plan["files_to_archive"] += len(duplicates)
                plan["potential_savings"] += sum(p.stat().st_size for p in duplicates)

        # 古いファイルの処理
        outdated_not_active = [f for f in self.outdated_files if f not in self.active_files]
        if outdated_not_active:
            plan["actions"].append({
                "action": "archive_outdated",
                "files": [str(f) for f in outdated_not_active[:20]],  # 最初の20個
                "total_count": len(outdated_not_active),
                "savings_mb": sum(f.stat().st_size for f in outdated_not_active) / 1024 / 1024
            })

            plan["files_to_archive"] += len(outdated_not_active)
            plan["potential_savings"] += sum(f.stat().st_size for f in outdated_not_active)

        plan["potential_savings_mb"] = plan["potential_savings"] / 1024 / 1024

        return plan

    def execute_optimization(self, plan: Dict[str, any], dry_run: bool = True):
        """最適化を実行"""
        if dry_run:
            print(f"\n🔍 DRY RUN - No actual changes will be made")
        else:
            print(f"\n🚀 Executing optimization plan...")

        # アーカイブディレクトリを作成
        if not dry_run:
            self.archive_dir.mkdir(exist_ok=True)

        executed_actions = 0

        for action in plan["actions"]:
            if action["action"] == "archive_duplicates":
                print(f"\n📁 Archiving duplicate files:")
                print(f"   Keeping: {action['keep']}")
                for duplicate in action["archive"]:
                    print(f"   Archiving: {duplicate}")
                    if not dry_run:
                        self._archive_file(Path(duplicate))
                executed_actions += 1

            elif action["action"] == "archive_outdated":
                print(f"\n📅 Archiving {action['total_count']} outdated files")
                for file_path in action["files"][:10]:  # 最初の10個だけ表示
                    print(f"   Archiving: {file_path}")
                    if not dry_run:
                        self._archive_file(Path(file_path))
                executed_actions += 1

        print(f"\n✅ Optimization complete!")
        print(f"   Actions executed: {executed_actions}")
        print(f"   Potential space savings: {plan['potential_savings_mb']:.2f} MB")
        print(f"   Files to archive: {plan['files_to_archive']}")

    def _archive_file(self, file_path: Path):
        """ファイルをアーカイブ"""
        try:
            # アーカイブディレクトリ内の相対パスを保持
            relative_path = file_path.relative_to(self.batch_dir)
            archive_path = self.archive_dir / relative_path

            # アーカイブディレクトリ構造を作成
            archive_path.parent.mkdir(parents=True, exist_ok=True)

            # ファイルを移動
            shutil.move(str(file_path), str(archive_path))
            print(f"   ✅ Archived: {file_path} -> {archive_path}")

        except Exception as e:
            print(f"   ❌ Failed to archive {file_path}: {e}")

def main():
    """メイン実行関数"""
    print("🧹 Batch System Optimizer")
    print("=" * 50)

    optimizer = BatchSystemOptimizer()

    # システム分析
    results = optimizer.analyze_file_system()

    if "error" in results:
        print(f"❌ Error: {results['error']}")
        return

    # 最適化プラン作成
    plan = optimizer.create_optimization_plan()

    print(f"\n📋 Optimization Plan:")
    print(f"   Potential savings: {plan['potential_savings_mb']:.2f} MB")
    print(f"   Files to archive: {plan['files_to_archive']}")
    print(f"   Actions planned: {len(plan['actions'])}")

    # ドライランで実行
    optimizer.execute_optimization(plan, dry_run=True)

    print(f"\n💡 To execute the optimization plan:")
    print(f"   python batch_system_optimizer.py --execute")

if __name__ == "__main__":
    main()