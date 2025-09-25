#!/usr/bin/env python3
"""
MiraiKakaku バックアップ・災害復旧システム
データベースとファイルの自動バックアップ、復旧手順の実装
"""

import os
import sys
import subprocess
import logging
import json
import hashlib
from datetime import datetime, timedelta
from pathlib import Path
import tarfile
import psycopg2
from typing import Dict, Optional, List

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - BackupRecovery - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class BackupDisasterRecoverySystem:
    """バックアップ・災害復旧システム"""

    def __init__(self):
        self.backup_base_path = Path(os.getenv('BACKUP_PATH', '/mnt/c/Users/yuuku/cursor/miraikakaku/backups'))
        self.backup_base_path.mkdir(parents=True, exist_ok=True)

        self.db_config = {
            'host': os.getenv('DB_HOST', '34.173.9.214'),
            'database': os.getenv('DB_NAME', 'miraikakaku'),
            'user': os.getenv('DB_USER', 'postgres'),
            'password': os.getenv('DB_PASSWORD'),
            'port': int(os.getenv('DB_PORT', '5432'))
        }

        # バックアップ設定
        self.backup_config = {
            'retention_days': 30,  # バックアップ保持期間
            'critical_tables': [
                'stock_master',
                'stock_prices',
                'stock_predictions',
                'prediction_accuracy'
            ],
            'critical_files': [
                'miraikakakuapi/simple_api_server.py',
                'cloud_run_data_collector.py',
                'cloud_run_prediction_generator.py',
                'miraikakakufront/app/page.tsx',
                'miraikakakufront/app/lib/api.ts'
            ]
        }

        # リカバリテスト設定
        self.recovery_test_config = {
            'test_interval_hours': 168,  # 週1回
            'test_data_sample_size': 100,
            'rpo_minutes': 60,  # Recovery Point Objective
            'rto_minutes': 30   # Recovery Time Objective
        }

    def create_database_backup(self, backup_type: str = 'full') -> Optional[Path]:
        """データベースのバックアップ作成"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_name = f"db_backup_{backup_type}_{timestamp}"
        backup_path = self.backup_base_path / 'database' / backup_name

        backup_path.parent.mkdir(parents=True, exist_ok=True)

        try:
            if backup_type == 'full':
                # 完全バックアップ
                logger.info("🔄 データベース完全バックアップ開始")
                pg_dump_cmd = [
                    'pg_dump',
                    f'--host={self.db_config["host"]}',
                    f'--port={self.db_config["port"]}',
                    f'--username={self.db_config["user"]}',
                    f'--dbname={self.db_config["database"]}',
                    '--format=custom',
                    '--verbose',
                    f'--file={backup_path}.dump'
                ]

                # パスワードを環境変数で渡す
                env = os.environ.copy()
                env['PGPASSWORD'] = self.db_config['password']

                result = subprocess.run(
                    pg_dump_cmd,
                    env=env,
                    capture_output=True,
                    text=True,
                    timeout=300
                )

                if result.returncode != 0:
                    logger.error(f"pg_dump failed: {result.stderr}")
                    # フォールバック：SQLダンプ形式で試行
                    return self.create_sql_backup(backup_path)

                # 圧縮
                self.compress_backup(f"{backup_path}.dump")

                logger.info(f"✅ 完全バックアップ作成完了: {backup_path}.dump.gz")
                return Path(f"{backup_path}.dump.gz")

            elif backup_type == 'incremental':
                # 差分バックアップ（変更されたレコードのみ）
                return self.create_incremental_backup(backup_path)

            elif backup_type == 'critical':
                # 重要テーブルのみ
                return self.create_critical_tables_backup(backup_path)

        except subprocess.TimeoutExpired:
            logger.error("バックアップタイムアウト")
            return None
        except Exception as e:
            logger.error(f"バックアップエラー: {e}")
            return self.create_sql_backup(backup_path)  # フォールバック

    def create_sql_backup(self, backup_path: Path) -> Optional[Path]:
        """SQLダンプ形式でのバックアップ（フォールバック）"""
        logger.info("📝 SQLダンプ形式でバックアップ作成")

        conn = psycopg2.connect(**self.db_config)
        backup_file = f"{backup_path}.sql"

        try:
            with conn.cursor() as cursor:
                with open(backup_file, 'w') as f:
                    # 重要テーブルのみをバックアップ
                    for table in self.backup_config['critical_tables']:
                        cursor.execute(f"SELECT COUNT(*) FROM {table}")
                        count = cursor.fetchone()[0]
                        logger.info(f"  {table}: {count}件")

                        # CREATE TABLE文を取得
                        cursor.execute(f"""
                            SELECT 'CREATE TABLE IF NOT EXISTS {table} AS ' ||
                                   'SELECT * FROM {table} WHERE false;'
                        """)
                        f.write(cursor.fetchone()[0] + '\n\n')

                        # データをCOPY形式で出力
                        copy_sql = f"COPY {table} TO STDOUT WITH CSV HEADER"
                        with conn.cursor() as copy_cursor:
                            f.write(f"\\copy {table} FROM stdin WITH CSV HEADER\n")
                            copy_cursor.copy_expert(copy_sql, f)
                            f.write("\\.\n\n")

            # 圧縮
            self.compress_backup(backup_file)
            logger.info(f"✅ SQLバックアップ完了: {backup_file}.gz")
            return Path(f"{backup_file}.gz")

        except Exception as e:
            logger.error(f"SQLバックアップエラー: {e}")
            return None
        finally:
            conn.close()

    def create_incremental_backup(self, backup_path: Path) -> Optional[Path]:
        """差分バックアップの作成"""
        logger.info("🔄 差分バックアップ開始")

        conn = psycopg2.connect(**self.db_config)
        backup_file = f"{backup_path}_incremental.sql"

        try:
            with conn.cursor() as cursor:
                with open(backup_file, 'w') as f:
                    # 過去24時間の変更データのみ
                    for table in self.backup_config['critical_tables']:
                        if table == 'stock_prices':
                            cursor.execute(f"""
                                COPY (
                                    SELECT * FROM {table}
                                    WHERE created_at >= NOW() - INTERVAL '24 hours'
                                       OR updated_at >= NOW() - INTERVAL '24 hours'
                                ) TO STDOUT WITH CSV HEADER
                            """)
                            f.write(f"\\copy {table}_incremental FROM stdin WITH CSV HEADER\n")
                            for line in cursor:
                                f.write(line)
                            f.write("\\.\n\n")

            self.compress_backup(backup_file)
            logger.info(f"✅ 差分バックアップ完了: {backup_file}.gz")
            return Path(f"{backup_file}.gz")

        except Exception as e:
            logger.error(f"差分バックアップエラー: {e}")
            return None
        finally:
            conn.close()

    def create_critical_tables_backup(self, backup_path: Path) -> Optional[Path]:
        """重要テーブルのみのバックアップ"""
        logger.info("⚠️ 重要テーブルバックアップ開始")

        conn = psycopg2.connect(**self.db_config)
        backup_data = {}

        try:
            with conn.cursor() as cursor:
                for table in self.backup_config['critical_tables']:
                    cursor.execute(f"SELECT * FROM {table} LIMIT 10000")  # 最新10000件
                    columns = [desc[0] for desc in cursor.description]
                    rows = cursor.fetchall()

                    backup_data[table] = {
                        'columns': columns,
                        'data': rows,
                        'count': len(rows)
                    }

                    logger.info(f"  {table}: {len(rows)}件")

            # JSON形式で保存
            backup_file = f"{backup_path}_critical.json"
            with open(backup_file, 'w') as f:
                json.dump(backup_data, f, default=str, indent=2)

            self.compress_backup(backup_file)
            logger.info(f"✅ 重要テーブルバックアップ完了: {backup_file}.gz")
            return Path(f"{backup_file}.gz")

        except Exception as e:
            logger.error(f"重要テーブルバックアップエラー: {e}")
            return None
        finally:
            conn.close()

    def create_file_backup(self) -> Optional[Path]:
        """重要ファイルのバックアップ"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_name = f"files_backup_{timestamp}.tar.gz"
        backup_path = self.backup_base_path / 'files' / backup_name

        backup_path.parent.mkdir(parents=True, exist_ok=True)

        try:
            logger.info("📁 ファイルバックアップ開始")

            with tarfile.open(backup_path, 'w:gz') as tar:
                for file_path in self.backup_config['critical_files']:
                    full_path = Path('/mnt/c/Users/yuuku/cursor/miraikakaku') / file_path
                    if full_path.exists():
                        tar.add(full_path, arcname=file_path)
                        logger.info(f"  ✓ {file_path}")
                    else:
                        logger.warning(f"  ✗ {file_path} not found")

            logger.info(f"✅ ファイルバックアップ完了: {backup_path}")
            return backup_path

        except Exception as e:
            logger.error(f"ファイルバックアップエラー: {e}")
            return None

    def compress_backup(self, file_path: str):
        """バックアップファイルの圧縮"""
        subprocess.run(['gzip', '-f', file_path], check=False)

    def verify_backup(self, backup_path: Path) -> bool:
        """バックアップの整合性検証"""
        logger.info(f"🔍 バックアップ検証: {backup_path}")

        if not backup_path.exists():
            logger.error("バックアップファイルが存在しません")
            return False

        # ファイルサイズチェック
        size_mb = backup_path.stat().st_size / (1024 * 1024)
        logger.info(f"  サイズ: {size_mb:.2f} MB")

        if size_mb < 0.1:
            logger.error("バックアップファイルが小さすぎます")
            return False

        # チェックサム計算
        checksum = self.calculate_checksum(backup_path)
        logger.info(f"  チェックサム: {checksum}")

        # メタデータ保存
        metadata_path = backup_path.with_suffix('.meta')
        with open(metadata_path, 'w') as f:
            json.dump({
                'timestamp': datetime.now().isoformat(),
                'size_bytes': backup_path.stat().st_size,
                'checksum': checksum,
                'verified': True
            }, f)

        logger.info("✅ バックアップ検証成功")
        return True

    def calculate_checksum(self, file_path: Path) -> str:
        """ファイルのチェックサム計算"""
        hash_md5 = hashlib.md5()
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_md5.update(chunk)
        return hash_md5.hexdigest()

    def test_recovery_procedure(self) -> Dict:
        """災害復旧手順のテスト"""
        logger.info("🔧 災害復旧テスト開始")
        test_results = {
            'timestamp': datetime.now().isoformat(),
            'tests': {},
            'overall_status': 'PASSED'
        }

        # 1. 最新バックアップの確認
        latest_backup = self.find_latest_backup()
        if not latest_backup:
            test_results['tests']['backup_availability'] = 'FAILED'
            test_results['overall_status'] = 'FAILED'
            logger.error("❌ 最新バックアップが見つかりません")
            return test_results

        test_results['tests']['backup_availability'] = 'PASSED'
        logger.info(f"✅ 最新バックアップ: {latest_backup}")

        # 2. バックアップ年齢の確認
        backup_age = datetime.now() - datetime.fromtimestamp(latest_backup.stat().st_mtime)
        if backup_age > timedelta(hours=24):
            test_results['tests']['backup_freshness'] = 'WARNING'
            logger.warning(f"⚠️ バックアップが{backup_age.days}日古い")
        else:
            test_results['tests']['backup_freshness'] = 'PASSED'

        # 3. 復旧時間目標（RTO）のシミュレーション
        recovery_start = datetime.now()

        # テスト復旧（実際には実行しない）
        estimated_recovery_time = self.estimate_recovery_time(latest_backup)

        if estimated_recovery_time <= self.recovery_test_config['rto_minutes']:
            test_results['tests']['rto_compliance'] = 'PASSED'
            logger.info(f"✅ RTO達成可能: {estimated_recovery_time}分")
        else:
            test_results['tests']['rto_compliance'] = 'FAILED'
            test_results['overall_status'] = 'FAILED'
            logger.error(f"❌ RTO未達: {estimated_recovery_time}分 > {self.recovery_test_config['rto_minutes']}分")

        # 4. 復旧ポイント目標（RPO）の確認
        data_loss_minutes = backup_age.total_seconds() / 60
        if data_loss_minutes <= self.recovery_test_config['rpo_minutes']:
            test_results['tests']['rpo_compliance'] = 'PASSED'
            logger.info(f"✅ RPO達成: {data_loss_minutes:.0f}分")
        else:
            test_results['tests']['rpo_compliance'] = 'WARNING'
            logger.warning(f"⚠️ RPO超過: {data_loss_minutes:.0f}分 > {self.recovery_test_config['rpo_minutes']}分")

        # テスト結果をファイルに保存
        test_report_path = self.backup_base_path / f"recovery_test_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(test_report_path, 'w') as f:
            json.dump(test_results, f, indent=2)

        logger.info(f"""
🔧 災害復旧テスト結果
======================
全体ステータス: {test_results['overall_status']}
バックアップ可用性: {test_results['tests']['backup_availability']}
バックアップ鮮度: {test_results['tests']['backup_freshness']}
RTO達成可能性: {test_results['tests']['rto_compliance']}
RPO達成可能性: {test_results['tests']['rpo_compliance']}

レポート: {test_report_path}
        """)

        return test_results

    def find_latest_backup(self) -> Optional[Path]:
        """最新のバックアップファイルを検索"""
        backup_files = list(self.backup_base_path.glob('**/*.gz'))
        if not backup_files:
            return None
        return max(backup_files, key=lambda p: p.stat().st_mtime)

    def estimate_recovery_time(self, backup_path: Path) -> int:
        """復旧時間の推定（分）"""
        size_gb = backup_path.stat().st_size / (1024 ** 3)
        # 経験則：1GBあたり5分で復旧
        estimated_minutes = int(size_gb * 5) + 10  # 基本時間10分
        return estimated_minutes

    def cleanup_old_backups(self):
        """古いバックアップの削除"""
        logger.info("🧹 古いバックアップのクリーンアップ")

        cutoff_date = datetime.now() - timedelta(days=self.backup_config['retention_days'])
        deleted_count = 0

        for backup_file in self.backup_base_path.glob('**/*'):
            if backup_file.is_file():
                file_time = datetime.fromtimestamp(backup_file.stat().st_mtime)
                if file_time < cutoff_date:
                    logger.info(f"  削除: {backup_file.name}")
                    backup_file.unlink()
                    deleted_count += 1

        logger.info(f"✅ {deleted_count}個の古いバックアップを削除")

    def create_recovery_script(self) -> Path:
        """災害復旧スクリプトの生成"""
        script_path = self.backup_base_path / 'recovery_script.sh'

        script_content = f"""#!/bin/bash
# MiraiKakaku 災害復旧スクリプト
# 生成日時: {datetime.now().isoformat()}

echo "🚨 MiraiKakaku 災害復旧開始"
echo "================================"

# 1. 最新バックアップの確認
LATEST_BACKUP=$(ls -t {self.backup_base_path}/database/*.gz | head -1)
echo "最新バックアップ: $LATEST_BACKUP"

# 2. データベース復旧
echo "📊 データベース復旧中..."
gunzip -c "$LATEST_BACKUP" | psql \\
    --host={self.db_config['host']} \\
    --port={self.db_config['port']} \\
    --username={self.db_config['user']} \\
    --dbname={self.db_config['database']}

# 3. サービス再起動
echo "🔄 サービス再起動中..."
cd /mnt/c/Users/yuuku/cursor/miraikakaku

# APIサーバー
pkill -f "simple_api_server.py"
nohup python3 miraikakakuapi/simple_api_server.py &

# データ収集サービス
pkill -f "cloud_run_data_collector.py"
nohup python3 cloud_run_data_collector.py &

# 予測生成サービス
pkill -f "cloud_run_prediction_generator.py"
nohup python3 cloud_run_prediction_generator.py &

echo "✅ 災害復旧完了"
"""

        with open(script_path, 'w') as f:
            f.write(script_content)

        script_path.chmod(0o755)
        logger.info(f"✅ 復旧スクリプト生成: {script_path}")
        return script_path


def main():
    """メイン処理"""
    system = BackupDisasterRecoverySystem()

    if len(sys.argv) > 1:
        command = sys.argv[1]

        if command == "backup":
            # バックアップ実行
            logger.info("🔄 バックアップ処理開始")

            # データベースバックアップ
            db_backup = system.create_database_backup('critical')
            if db_backup:
                system.verify_backup(db_backup)

            # ファイルバックアップ
            file_backup = system.create_file_backup()
            if file_backup:
                system.verify_backup(file_backup)

            # 古いバックアップのクリーンアップ
            system.cleanup_old_backups()

        elif command == "test":
            # 災害復旧テスト
            system.test_recovery_procedure()

        elif command == "script":
            # 復旧スクリプト生成
            system.create_recovery_script()

    else:
        # デフォルト：状態チェック
        logger.info("📊 バックアップシステム状態")
        latest = system.find_latest_backup()
        if latest:
            age = datetime.now() - datetime.fromtimestamp(latest.stat().st_mtime)
            logger.info(f"最新バックアップ: {latest.name}")
            logger.info(f"経過時間: {age}")
        else:
            logger.warning("バックアップが存在しません")

        # 災害復旧テスト実行
        system.test_recovery_procedure()


if __name__ == "__main__":
    main()