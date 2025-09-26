#!/usr/bin/env python3
"""
ハードコードされた認証情報をセキュアな環境変数使用に一括変換
"""

import os
import re
import glob
import logging
from pathlib import Path

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class CredentialSecurityFixer:
    def __init__(self):
        self.project_root = Path(__file__).parent
        self.fixes_applied = 0
        self.files_processed = 0

        # 修正パターン
        self.patterns = [
            # Python環境での修正
            {
                'pattern': r"'password':\s*['\"]os.getenv('DB_PASSWORD', '')['\"]",
                'replacement': "'password': os.getenv('DB_PASSWORD')",
                'description': "Python dictionary password"
            },
            {
                'pattern': r'"password":\s*["\']os.getenv('DB_PASSWORD', '')["\']',
                'replacement': '"password": os.getenv("DB_PASSWORD")',
                'description': "Python dictionary password (double quotes)"
            },
            {
                'pattern': r'password=[\'"]os.getenv('DB_PASSWORD', '')[\'"]',
                'replacement': 'password=os.getenv("DB_PASSWORD")',
                'description': "Python parameter password"
            },
            {
                'pattern': r'DB_PASSWORD=os.getenv('DB_PASSWORD', '')',
                'replacement': 'DB_PASSWORD=${DB_PASSWORD}',
                'description': "Environment variable in scripts"
            },
            # PGPASSWORD特殊ケース
            {
                'pattern': r'PGPASSWORD="os.getenv('DB_PASSWORD', '')"',
                'replacement': 'PGPASSWORD="${DB_PASSWORD}"',
                'description': "PGPASSWORD environment variable"
            },
            # psqlコマンド内
            {
                'pattern': r'-h\s+34\.173\.9\.214\s+-U\s+postgres\s+-d\s+miraikakaku\s+-c\s+"([^"]+)"',
                'replacement': r'-h ${DB_HOST:-34.173.9.214} -U ${DB_USER:-postgres} -d ${DB_NAME:-miraikakaku} -c "\1"',
                'description': "psql command parameters"
            }
        ]

        # 除外するファイル/ディレクトリ
        self.exclude_patterns = [
            '*/node_modules/*',
            '*/.next/*',
            '*/dist/*',
            '*/__pycache__/*',
            '*/playwright-report/*',
            '*/test-results/*',
            '.git/*',
            '*/archive/*',  # アーカイブフォルダは除外
        ]

    def should_process_file(self, file_path: Path) -> bool:
        """ファイルを処理すべきかどうか判定"""
        file_str = str(file_path)

        # 除外パターンに一致するかチェック
        for pattern in self.exclude_patterns:
            if glob.fnmatch.fnmatch(file_str, pattern):
                return False

        # 対象拡張子
        if file_path.suffix in ['.py', '.js', '.ts', '.sh', '.yaml', '.yml']:
            return True

        return False

    def fix_file(self, file_path: Path) -> bool:
        """単一ファイルの認証情報を修正"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            original_content = content
            file_fixes = 0

            for pattern_info in self.patterns:
                pattern = pattern_info['pattern']
                replacement = pattern_info['replacement']
                description = pattern_info['description']

                new_content, count = re.subn(pattern, replacement, content)
                if count > 0:
                    content = new_content
                    file_fixes += count
                    logger.info(f"  └─ {description}: {count} 箇所修正")

            # ファイルが変更された場合のみ書き込み
            if file_fixes > 0:
                # os.getenv を使用している場合、importを追加
                if 'os.getenv(' in content and file_path.suffix == '.py':
                    if 'import os' not in content and 'from os import' not in content:
                        content = 'import os\n' + content
                        logger.info(f"  └─ import os 追加")

                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)

                logger.info(f"✅ {file_path}: {file_fixes} 箇所修正")
                self.fixes_applied += file_fixes
                return True

            return False

        except Exception as e:
            logger.error(f"❌ {file_path}の処理中にエラー: {e}")
            return False

    def run_security_fixes(self):
        """全体の認証情報セキュリティ修正を実行"""
        logger.info("🔐 認証情報セキュリティ修正を開始")
        logger.info(f"   対象ディレクトリ: {self.project_root}")

        # 全ファイルを検索
        all_files = []
        for pattern in ['**/*.py', '**/*.js', '**/*.ts', '**/*.sh', '**/*.yaml', '**/*.yml']:
            for file_path in self.project_root.rglob(pattern):
                if self.should_process_file(file_path):
                    all_files.append(file_path)

        logger.info(f"📁 {len(all_files)} ファイルを検出")

        # 各ファイルを処理
        modified_files = 0
        for file_path in all_files:
            self.files_processed += 1
            if self.fix_file(file_path):
                modified_files += 1

        logger.info("=" * 60)
        logger.info(f"🎯 修正完了:")
        logger.info(f"   処理ファイル数: {self.files_processed}")
        logger.info(f"   変更ファイル数: {modified_files}")
        logger.info(f"   総修正箇所数: {self.fixes_applied}")

        if self.fixes_applied > 0:
            logger.info("")
            logger.info("⚠️  重要:")
            logger.info("   1. 環境変数 DB_PASSWORD を設定してください")
            logger.info("   2. Google Secret Manager の使用を推奨します")
            logger.info("   3. 変更をテストしてから本番環境にデプロイしてください")

if __name__ == "__main__":
    fixer = CredentialSecurityFixer()
    fixer.run_security_fixes()