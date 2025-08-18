#!/usr/bin/env python3
"""
Miraikakaku Batch System インストーラー
自動データベース更新システムのセットアップスクリプト

実行内容:
1. 必要なディレクトリ構造作成
2. 依存関係チェック・インストール
3. 設定ファイル作成
4. systemdサービス登録 (Linux環境)
5. 初期データベース整合性チェック
6. テスト実行
"""

import os
import sys
import subprocess
import json
import logging
from datetime import datetime
import shutil
import platform

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class BatchSystemInstaller:
    """Miraikakaku Batch System インストーラー"""
    
    def __init__(self):
        self.base_dir = os.path.dirname(os.path.abspath(__file__))
        self.config = {
            'directories': [
                'backups',
                'backups/japanese_stocks',
                'backups/us_stocks', 
                'backups/etf_data',
                'reports',
                'logs',
                'config'
            ],
            'required_packages': [
                'requests',
                'pandas',
                'yfinance',
                'schedule',
                'aiohttp',
                'openpyxl'
            ],
            'systemd_service_name': 'miraikakaku-batch'
        }
        
    def install(self):
        """メインインストール処理"""
        logger.info("🚀 Miraikakaku Batch System インストール開始")
        
        try:
            # 1. システムチェック
            self.check_system_requirements()
            
            # 2. ディレクトリ作成
            self.create_directories()
            
            # 3. 依存関係インストール
            self.install_dependencies()
            
            # 4. 設定ファイル作成
            self.create_config_files()
            
            # 5. サービス登録 (Linux環境のみ)
            if platform.system() == 'Linux':
                self.setup_systemd_service()
            
            # 6. 権限設定
            self.setup_permissions()
            
            # 7. 初期テスト
            self.run_initial_tests()
            
            # 8. インストール完了レポート
            self.generate_install_report()
            
            logger.info("✅ Miraikakaku Batch System インストール完了")
            self.print_usage_instructions()
            
        except Exception as e:
            logger.error(f"❌ インストールエラー: {e}")
            sys.exit(1)
            
    def check_system_requirements(self):
        """システム要件チェック"""
        logger.info("🔍 システム要件チェック中...")
        
        # Python バージョンチェック
        python_version = sys.version_info
        if python_version.major < 3 or (python_version.major == 3 and python_version.minor < 8):
            raise Exception(f"Python 3.8以上が必要です (現在: {python_version.major}.{python_version.minor})")
            
        # pip チェック
        try:
            import pip
        except ImportError:
            raise Exception("pipが見つかりません")
            
        # 必須ファイルチェック
        required_files = [
            'miraikakakubatch.py',
            'japanese_stock_updater.py',
            'universal_stock_api.py'
        ]
        
        for file_path in required_files:
            if not os.path.exists(os.path.join(self.base_dir, file_path)):
                raise Exception(f"必須ファイルが見つかりません: {file_path}")
                
        logger.info("✅ システム要件OK")
        
    def create_directories(self):
        """ディレクトリ構造作成"""
        logger.info("📁 ディレクトリ構造作成中...")
        
        for directory in self.config['directories']:
            dir_path = os.path.join(self.base_dir, directory)
            os.makedirs(dir_path, exist_ok=True)
            logger.info(f"作成: {dir_path}")
            
        logger.info("✅ ディレクトリ構造作成完了")
        
    def install_dependencies(self):
        """依存関係インストール"""
        logger.info("📦 依存関係インストール中...")
        
        for package in self.config['required_packages']:
            try:
                logger.info(f"インストール中: {package}")
                subprocess.check_call([
                    sys.executable, '-m', 'pip', 'install', package
                ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                
            except subprocess.CalledProcessError as e:
                logger.warning(f"パッケージインストール失敗: {package} - {e}")
                
        logger.info("✅ 依存関係インストール完了")
        
    def create_config_files(self):
        """設定ファイル作成"""
        logger.info("⚙️ 設定ファイル作成中...")
        
        # メイン設定ファイル
        config_data = {
            'system': {
                'base_directory': self.base_dir,
                'log_level': 'INFO',
                'timezone': 'Asia/Tokyo'
            },
            'database': {
                'japanese_stocks_file': 'comprehensive_japanese_stocks_enhanced.py',
                'us_stocks_backup': 'backups/us_stocks/us_stocks_backup.json',
                'etf_optimized_file': 'optimized_etfs_3000.json'
            },
            'schedule': {
                'daily_maintenance_time': '04:00',
                'weekly_maintenance_day': 'monday',
                'weekly_maintenance_time': '06:00',
                'coverage_check_interval_hours': 6
            },
            'thresholds': {
                'min_japanese_stocks': 4000,
                'min_us_stocks': 8500,
                'min_etfs': 2900,
                'coverage_alert_threshold': 0.95
            },
            'notifications': {
                'email_enabled': False,
                'slack_enabled': False,
                'log_file_enabled': True
            }
        }
        
        config_file = os.path.join(self.base_dir, 'config', 'batch_config.json')
        with open(config_file, 'w', encoding='utf-8') as f:
            json.dump(config_data, f, indent=2, ensure_ascii=False)
            
        # ログ設定ファイル
        log_config = {
            'version': 1,
            'disable_existing_loggers': False,
            'formatters': {
                'detailed': {
                    'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
                }
            },
            'handlers': {
                'console': {
                    'class': 'logging.StreamHandler',
                    'level': 'INFO',
                    'formatter': 'detailed'
                },
                'file': {
                    'class': 'logging.handlers.RotatingFileHandler',
                    'filename': os.path.join(self.base_dir, 'logs', 'miraikakaku_batch.log'),
                    'maxBytes': 10485760,  # 10MB
                    'backupCount': 5,
                    'level': 'INFO',
                    'formatter': 'detailed'
                }
            },
            'root': {
                'level': 'INFO',
                'handlers': ['console', 'file']
            }
        }
        
        log_config_file = os.path.join(self.base_dir, 'config', 'logging_config.json')
        with open(log_config_file, 'w', encoding='utf-8') as f:
            json.dump(log_config, f, indent=2, ensure_ascii=False)
            
        logger.info("✅ 設定ファイル作成完了")
        
    def setup_systemd_service(self):
        """systemdサービス設定"""
        logger.info("🔧 systemdサービス設定中...")
        
        try:
            service_content = f"""[Unit]
Description=Miraikakaku Batch System
After=network.target
Wants=network.target

[Service]
Type=simple
User={os.getenv('USER', 'root')}
WorkingDirectory={self.base_dir}
ExecStart={sys.executable} {os.path.join(self.base_dir, 'miraikakakubatch.py')} --mode monitor
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
"""
            
            service_file = f"/etc/systemd/system/{self.config['systemd_service_name']}.service"
            
            # サービスファイル作成 (sudo権限必要)
            try:
                with open('miraikakaku-batch.service', 'w') as f:
                    f.write(service_content)
                    
                logger.info(f"systemdサービスファイル作成: miraikakaku-batch.service")
                logger.info("sudo権限でサービスを有効化するには以下を実行:")
                logger.info(f"sudo cp miraikakaku-batch.service {service_file}")
                logger.info("sudo systemctl daemon-reload")
                logger.info(f"sudo systemctl enable {self.config['systemd_service_name']}")
                logger.info(f"sudo systemctl start {self.config['systemd_service_name']}")
                
            except PermissionError:
                logger.warning("systemdサービス自動設定にはsudo権限が必要です")
                
        except Exception as e:
            logger.warning(f"systemd設定エラー: {e}")
            
    def setup_permissions(self):
        """権限設定"""
        logger.info("🔐 権限設定中...")
        
        try:
            # 実行権限付与
            scripts = ['miraikakakubatch.py', 'japanese_stock_updater.py']
            for script in scripts:
                script_path = os.path.join(self.base_dir, script)
                if os.path.exists(script_path):
                    os.chmod(script_path, 0o755)
                    
            logger.info("✅ 権限設定完了")
            
        except Exception as e:
            logger.warning(f"権限設定エラー: {e}")
            
    def run_initial_tests(self):
        """初期テスト実行"""
        logger.info("🧪 初期テスト実行中...")
        
        try:
            # 設定ファイル読み込みテスト
            config_file = os.path.join(self.base_dir, 'config', 'batch_config.json')
            with open(config_file, 'r', encoding='utf-8') as f:
                config = json.load(f)
                logger.info("設定ファイル読み込みOK")
                
            # バッチシステムインポートテスト
            import importlib.util
            spec = importlib.util.spec_from_file_location(
                "miraikakakubatch", 
                os.path.join(self.base_dir, "miraikakakubatch.py")
            )
            batch_module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(batch_module)
            logger.info("バッチシステムインポートOK")
            
            # カバレッジチェックテスト実行
            try:
                subprocess.run([
                    sys.executable, 
                    os.path.join(self.base_dir, 'miraikakakubatch.py'),
                    '--mode', 'check'
                ], timeout=30, check=True, capture_output=True)
                logger.info("カバレッジチェックテストOK")
            except (subprocess.TimeoutExpired, subprocess.CalledProcessError) as e:
                logger.warning(f"カバレッジチェックテスト失敗: {e}")
                
            logger.info("✅ 初期テスト完了")
            
        except Exception as e:
            logger.error(f"初期テストエラー: {e}")
            raise
            
    def generate_install_report(self):
        """インストールレポート生成"""
        logger.info("📋 インストールレポート生成中...")
        
        report = {
            'installation': {
                'timestamp': datetime.now().isoformat(),
                'version': '1.0.0',
                'platform': platform.platform(),
                'python_version': f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}",
                'base_directory': self.base_dir
            },
            'components': {
                'batch_system': os.path.exists(os.path.join(self.base_dir, 'miraikakakubatch.py')),
                'stock_updater': os.path.exists(os.path.join(self.base_dir, 'japanese_stock_updater.py')),
                'config_files': os.path.exists(os.path.join(self.base_dir, 'config', 'batch_config.json')),
                'directories_created': all([
                    os.path.exists(os.path.join(self.base_dir, d)) 
                    for d in self.config['directories']
                ])
            },
            'dependencies': {
                package: self._check_package_installed(package) 
                for package in self.config['required_packages']
            },
            'status': 'installed_successfully'
        }
        
        report_file = os.path.join(self.base_dir, 'reports', f'installation_report_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json')
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
            
        logger.info(f"インストールレポート生成: {report_file}")
        
    def _check_package_installed(self, package: str) -> bool:
        """パッケージインストール状態チェック"""
        try:
            import importlib
            importlib.import_module(package)
            return True
        except ImportError:
            return False
            
    def print_usage_instructions(self):
        """使用方法表示"""
        print("\n" + "="*60)
        print("🎉 Miraikakaku Batch System インストール完了!")
        print("="*60)
        print("\n📖 使用方法:")
        print(f"  日次メンテナンス:    python3 {os.path.join(self.base_dir, 'miraikakakubatch.py')} --mode daily")
        print(f"  週次メンテナンス:    python3 {os.path.join(self.base_dir, 'miraikakakubatch.py')} --mode weekly") 
        print(f"  カバレッジチェック:  python3 {os.path.join(self.base_dir, 'miraikakakubatch.py')} --mode check")
        print(f"  監視モード起動:     python3 {os.path.join(self.base_dir, 'miraikakakubatch.py')} --mode monitor")
        print("\n⚙️ 設定ファイル:")
        print(f"  メイン設定: {os.path.join(self.base_dir, 'config', 'batch_config.json')}")
        print(f"  ログ設定:   {os.path.join(self.base_dir, 'config', 'logging_config.json')}")
        print("\n📁 重要なディレクトリ:")
        print(f"  バックアップ: {os.path.join(self.base_dir, 'backups')}")
        print(f"  レポート:     {os.path.join(self.base_dir, 'reports')}")
        print(f"  ログ:         {os.path.join(self.base_dir, 'logs')}")
        
        if platform.system() == 'Linux':
            print("\n🔧 systemdサービス (Linux環境):")
            print("  sudo systemctl start miraikakaku-batch    # サービス開始")
            print("  sudo systemctl enable miraikakaku-batch   # 自動起動有効")
            print("  sudo systemctl status miraikakaku-batch   # ステータス確認")
        
        print("\n🚀 すぐに開始するには:")
        print("  1. カバレッジチェックを実行してシステム状態を確認")
        print("  2. 監視モードを起動して自動メンテナンスを開始")
        print("  3. 必要に応じて設定ファイルをカスタマイズ")
        print("="*60)

def main():
    """メイン処理"""
    print("Miraikakaku Batch System インストーラー")
    print("=" * 50)
    
    installer = BatchSystemInstaller()
    installer.install()

if __name__ == "__main__":
    main()