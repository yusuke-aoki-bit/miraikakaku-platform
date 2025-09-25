#!/usr/bin/env python3
"""
Secure Configuration Manager for MiraiKakaku
環境変数とGoogle Secret Managerを使用した安全な認証情報管理
"""

import os
import sys
import json
import base64
from typing import Dict, Optional, Any
from pathlib import Path
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2KDF
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class SecureConfigManager:
    """セキュアな設定管理クラス"""

    def __init__(self):
        self.env_path = Path(__file__).parent
        self.use_secret_manager = os.getenv('USE_SECRET_MANAGER', 'false').lower() == 'true'

    def generate_encryption_key(self, salt: bytes = None) -> bytes:
        """暗号化キーを生成"""
        if not salt:
            salt = os.urandom(16)

        # システム固有の値を使用してキーを導出
        password = (
            os.getenv('SYSTEM_SECRET', 'default-secret') +
            os.getenv('HOSTNAME', 'localhost')
        ).encode()

        kdf = PBKDF2KDF(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
        )
        key = base64.urlsafe_b64encode(kdf.derive(password))
        return key

    def encrypt_credential(self, credential: str) -> Dict[str, str]:
        """認証情報を暗号化"""
        salt = os.urandom(16)
        key = self.generate_encryption_key(salt)
        f = Fernet(key)

        encrypted = f.encrypt(credential.encode())

        return {
            'encrypted': base64.b64encode(encrypted).decode('utf-8'),
            'salt': base64.b64encode(salt).decode('utf-8')
        }

    def decrypt_credential(self, encrypted_data: Dict[str, str]) -> str:
        """認証情報を復号化"""
        salt = base64.b64decode(encrypted_data['salt'])
        key = self.generate_encryption_key(salt)
        f = Fernet(key)

        encrypted = base64.b64decode(encrypted_data['encrypted'])
        decrypted = f.decrypt(encrypted)

        return decrypted.decode('utf-8')

    def load_secure_config(self) -> Dict[str, Any]:
        """セキュアな設定をロード"""
        config = {}

        # Google Secret Manager使用時
        if self.use_secret_manager:
            try:
                from google.cloud import secretmanager

                client = secretmanager.SecretManagerServiceClient()
                project_id = os.getenv('GCP_PROJECT_ID', 'pricewise-huqkr')

                # Secret Managerから認証情報を取得
                secrets = [
                    'db-password',
                    'jwt-secret',
                    'grafana-password',
                    'api-keys'
                ]

                for secret_name in secrets:
                    try:
                        name = f"projects/{project_id}/secrets/{secret_name}/versions/latest"
                        response = client.access_secret_version(request={"name": name})
                        payload = response.payload.data.decode("UTF-8")

                        if secret_name == 'api-keys':
                            config.update(json.loads(payload))
                        else:
                            config[secret_name.replace('-', '_')] = payload

                    except Exception as e:
                        logger.warning(f"Secret {secret_name} not found: {e}")

            except ImportError:
                logger.warning("Google Cloud Secret Manager not available")
                self.use_secret_manager = False

        # 環境変数からのフォールバック
        if not self.use_secret_manager:
            # 暗号化された設定ファイルを読み込む
            encrypted_config_path = self.env_path / '.env.encrypted'

            if encrypted_config_path.exists():
                with open(encrypted_config_path, 'r') as f:
                    encrypted_config = json.load(f)

                # 重要な認証情報のみ復号化
                sensitive_keys = ['db_password', 'jwt_secret', 'grafana_password']
                for key in sensitive_keys:
                    if key in encrypted_config:
                        config[key] = self.decrypt_credential(encrypted_config[key])

            # 環境変数から追加設定を読み込み
            config.update({
                'db_host': os.getenv('DB_HOST', 'localhost'),
                'db_port': int(os.getenv('DB_PORT', '5432')),
                'db_name': os.getenv('DB_NAME', 'miraikakaku'),
                'db_user': os.getenv('DB_USER', 'postgres'),
                'api_url': os.getenv('API_URL', 'http://localhost:8000'),
                'frontend_url': os.getenv('FRONTEND_URL', 'http://localhost:3000'),
            })

        return config

    def get_database_url(self, mask_password: bool = True) -> str:
        """データベース接続URLを取得"""
        config = self.load_secure_config()

        password = config.get('db_password', 'default-password')
        if mask_password:
            password = '*' * 8

        return (
            f"postgresql://{config.get('db_user', 'postgres')}:"
            f"{password}@{config.get('db_host', 'localhost')}:"
            f"{config.get('db_port', 5432)}/{config.get('db_name', 'miraikakaku')}"
        )

    def rotate_credentials(self):
        """認証情報のローテーション"""
        logger.info("認証情報のローテーションを開始")

        # 新しい暗号化キーを生成
        new_config = {}

        # パスワードを生成（実際の本番環境では強力なパスワード生成を使用）
        import secrets
        import string

        alphabet = string.ascii_letters + string.digits + string.punctuation
        new_password = ''.join(secrets.choice(alphabet) for _ in range(32))

        # 暗号化して保存
        encrypted_password = self.encrypt_credential(new_password)

        config_to_save = {
            'db_password': encrypted_password,
            'jwt_secret': self.encrypt_credential(secrets.token_urlsafe(64)),
            'session_secret': self.encrypt_credential(secrets.token_urlsafe(32)),
            'grafana_password': self.encrypt_credential(
                ''.join(secrets.choice(alphabet) for _ in range(24))
            ),
            'last_rotation': datetime.now().isoformat()
        }

        # 暗号化された設定を保存
        encrypted_config_path = self.env_path / '.env.encrypted'
        with open(encrypted_config_path, 'w') as f:
            json.dump(config_to_save, f, indent=2)

        logger.info("認証情報のローテーションが完了しました")

        # データベースパスワードの更新（実際の環境では要実装）
        # self.update_database_password(new_password)

        return True


def migrate_to_secure_config():
    """既存の.envファイルからセキュアな設定に移行"""
    manager = SecureConfigManager()
    env_path = Path(__file__).parent / 'miraikakakuapi' / '.env'

    if not env_path.exists():
        logger.error(".envファイルが見つかりません")
        return False

    # .envファイルを読み込み
    import dotenv
    config = dotenv.dotenv_values(env_path)

    # 重要な認証情報を暗号化
    sensitive_keys = {
        'DB_PASSWORD': 'db_password',
        'JWT_SECRET_KEY': 'jwt_secret',
        'GRAFANA_PASSWORD': 'grafana_password',
        'SESSION_SECRET': 'session_secret'
    }

    encrypted_config = {}
    for env_key, config_key in sensitive_keys.items():
        if env_key in config:
            encrypted_config[config_key] = manager.encrypt_credential(config[env_key])
            logger.info(f"✅ {env_key} を暗号化しました")

    # 暗号化された設定を保存
    encrypted_path = Path(__file__).parent / '.env.encrypted'
    with open(encrypted_path, 'w') as f:
        json.dump(encrypted_config, f, indent=2)

    # 新しい.env.templateを生成（機密情報を除外）
    safe_config = []
    for key, value in config.items():
        if key not in sensitive_keys:
            safe_config.append(f"{key}={value}")
        else:
            safe_config.append(f"{key}=*** ENCRYPTED - See .env.encrypted ***")

    template_path = Path(__file__).parent / '.env.template'
    with open(template_path, 'w') as f:
        f.write('\n'.join(safe_config))

    logger.info(f"✅ セキュアな設定への移行が完了しました")
    logger.info(f"   暗号化済み: {encrypted_path}")
    logger.info(f"   テンプレート: {template_path}")

    # オリジナルの.envファイルをバックアップして削除
    backup_path = env_path.with_suffix('.env.backup')
    env_path.rename(backup_path)
    logger.info(f"   バックアップ: {backup_path}")

    return True


if __name__ == "__main__":
    from datetime import datetime

    if len(sys.argv) > 1 and sys.argv[1] == "migrate":
        # 既存設定の移行
        logger.info("🔐 既存設定のセキュアな形式への移行を開始")
        if migrate_to_secure_config():
            logger.info("✅ 移行完了！")
            logger.info("⚠️  重要: .env.backupファイルは安全な場所に保管し、Gitには追加しないでください")

    elif len(sys.argv) > 1 and sys.argv[1] == "rotate":
        # 認証情報のローテーション
        manager = SecureConfigManager()
        manager.rotate_credentials()

    else:
        # 設定の確認（マスク表示）
        manager = SecureConfigManager()
        logger.info("現在の設定（マスク済み）:")
        logger.info(f"Database URL: {manager.get_database_url(mask_password=True)}")

        config = manager.load_secure_config()
        for key in ['api_url', 'frontend_url', 'db_host']:
            if key in config:
                logger.info(f"{key}: {config[key]}")