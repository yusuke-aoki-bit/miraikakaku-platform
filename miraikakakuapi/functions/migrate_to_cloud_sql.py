#!/usr/bin/env python3
"""
SQLiteからCloud SQLへのデータ移行スクリプト
Miraikakaku本格運用のためのデータベース移行
"""

import os
import sqlite3
import logging
from datetime import datetime
from sqlalchemy import create_engine, text, MetaData, Table
from sqlalchemy.orm import sessionmaker
import pandas as pd

# ログ設定
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class DatabaseMigrator:
    def __init__(self):
        # SQLite接続
        self.sqlite_path = "./miraikakaku.db"
        self.sqlite_engine = create_engine(f"sqlite:///{self.sqlite_path}")

        # Cloud SQL接続
        self.cloud_sql_url = "mysql+pymysql://miraikakaku-user:miraikakaku-secure-pass-2024@34.58.103.36:3306/miraikakaku"
        self.cloud_sql_engine = create_engine(self.cloud_sql_url)

    def check_connections(self):
        """データベース接続確認"""
        logger.info("=== データベース接続確認 ===")

        # SQLite確認
        try:
            with self.sqlite_engine.connect() as conn:
                result = conn.execute(
                    text("SELECT name FROM sqlite_master WHERE type='table'")
                )
                sqlite_tables = [row[0] for row in result.fetchall()]
                logger.info(f"✅ SQLite接続成功: {len(sqlite_tables)}テーブル")
        except Exception as e:
            logger.error(f"❌ SQLite接続失敗: {e}")
            return False

        # Cloud SQL確認
        try:
            with self.cloud_sql_engine.connect() as conn:
                result = conn.execute(text("SELECT VERSION()"))
                version = result.fetchone()[0]
                logger.info(f"✅ Cloud SQL接続成功: {version}")
        except Exception as e:
            logger.error(f"❌ Cloud SQL接続失敗: {e}")
            return False

        return True

    def analyze_data_differences(self):
        """SQLiteとCloud SQLのデータ差分分析"""
        logger.info("=== データ差分分析 ===")

        tables_to_check = [
            "stock_master",
            "stock_predictions",
            "stock_price_history",
            "ai_inference_log",
        ]

        for table in tables_to_check:
            try:
                # SQLiteからカウント
                with self.sqlite_engine.connect() as conn:
                    sqlite_result = conn.execute(text(f"SELECT COUNT(*) FROM {table}"))
                    sqlite_count = sqlite_result.fetchone()[0]

                # Cloud SQLからカウント
                with self.cloud_sql_engine.connect() as conn:
                    cloud_result = conn.execute(text(f"SELECT COUNT(*) FROM {table}"))
                    cloud_count = cloud_result.fetchone()[0]

                logger.info(
                    f"{table}: SQLite={
                        sqlite_count:,    }, Cloud SQL={
                        cloud_count:,        }"
                )

                if sqlite_count > cloud_count:
                    logger.warning(
                        f"⚠️  {table}: SQLiteの方が{
                            sqlite_count - cloud_count:,}レコード多い"
                    )
                elif cloud_count > sqlite_count:
                    logger.info(
                        f"ℹ️  {table}: Cloud SQLの方が{
                            cloud_count - sqlite_count:,}レコード多い"
                    )
                else:
                    logger.info(f"✅ {table}: レコード数一致")

            except Exception as e:
                logger.error(f"❌ {table}の確認失敗: {e}")

    def migrate_table_data(self, table_name, batch_size=1000):
        """テーブルデータの移行"""
        logger.info(f"=== {table_name}データ移行開始 ===")

        try:
            # SQLiteからデータを読み込み
            with self.sqlite_engine.connect() as conn:
                df = pd.read_sql(f"SELECT * FROM {table_name}", conn)

            if df.empty:
                logger.info(f"{table_name}: データなし")
                return True

            logger.info(f"{table_name}: {len(df):,}レコードを移行開始")

            # Cloud SQLに既存データがある場合の対応確認
            with self.cloud_sql_engine.connect() as conn:
                existing_result = conn.execute(
                    text(f"SELECT COUNT(*) FROM {table_name}")
                )
                existing_count = existing_result.fetchone()[0]

                if existing_count > 0:
                    logger.warning(
                        f"{table_name}: Cloud SQLに既存データ{
                            existing_count:,}レコードあり"
                    )
                    response = input(
                        f"{table_name}の既存データを削除して移行しますか? (y/N): "
                    )
                    if response.lower() == "y":
                        logger.info(f"{table_name}: 既存データ削除中...")
                        conn.execute(text(f"DELETE FROM {table_name}"))
                        conn.commit()
                        logger.info(f"{table_name}: 既存データ削除完了")
                    else:
                        logger.info(f"{table_name}: 移行をスキップ")
                        return True

            # バッチごとに挿入
            total_batches = (len(df) - 1) // batch_size + 1

            for i in range(0, len(df), batch_size):
                batch_df = df.iloc[i : i + batch_size]
                batch_num = (i // batch_size) + 1

                # Cloud SQLに挿入
                batch_df.to_sql(
                    table_name,
                    self.cloud_sql_engine,
                    if_exists="append",
                    index=False,
                    method="multi",
                )

                logger.info(
                    f"{table_name}: バッチ{batch_num}/{total_batches}完了 ({len(batch_df)}レコード)"
                )

            # 移行後の確認
            with self.cloud_sql_engine.connect() as conn:
                final_result = conn.execute(text(f"SELECT COUNT(*) FROM {table_name}"))
                final_count = final_result.fetchone()[0]

            logger.info(f"✅ {table_name}移行完了: {final_count:,}レコード")
            return True

        except Exception as e:
            logger.error(f"❌ {table_name}移行失敗: {e}")
            return False

    def update_application_config(self):
        """アプリケーション設定をCloud SQL用に更新"""
        logger.info("=== アプリケーション設定更新 ===")

        env_file = "./functions/.env"

        try:
            # 現在の設定を読み込み
            with open(env_file, "r", encoding="utf-8") as f:
                content = f.read()

            # SQLiteからMySQL接続に変更
            cloud_sql_database_url = "mysql+pymysql://miraikakaku-user:miraikakaku-secure-pass-2024@34.58.103.36:3306/miraikakaku"

            # DATABASE_URLを更新
            updated_content = content.replace(
                "DATABASE_URL=sqlite:///./miraikakaku.db",
                f"DATABASE_URL={cloud_sql_database_url}",
            )

            # バックアップを作成
            backup_file = f"{env_file}.backup.{
                datetime.now().strftime('%Y%m%d_%H%M%S')}"
            with open(backup_file, "w", encoding="utf-8") as f:
                f.write(content)
            logger.info(f"設定ファイルバックアップ: {backup_file}")

            # 新しい設定を書き込み
            with open(env_file, "w", encoding="utf-8") as f:
                f.write(updated_content)

            logger.info(f"✅ {env_file}更新完了")
            logger.info(f"Database URL: {cloud_sql_database_url}")
            return True

        except Exception as e:
            logger.error(f"❌ 設定ファイル更新失敗: {e}")
            return False

    def test_cloud_sql_connection(self):
        """Cloud SQL接続テスト"""
        logger.info("=== Cloud SQL接続テスト ===")

        try:
            with self.cloud_sql_engine.connect() as conn:
                # バージョン確認
                result = conn.execute(text("SELECT VERSION()"))
                version = result.fetchone()[0]
                logger.info(f"MySQL Version: {version}")

                # テーブル確認
                result = conn.execute(text("SHOW TABLES"))
                tables = [row[0] for row in result.fetchall()]
                logger.info(f"テーブル数: {len(tables)}")

                # 主要テーブルのレコード数確認
                for table in [
                    "stock_master",
                    "stock_predictions",
                    "stock_price_history",
                ]:
                    if table in tables:
                        result = conn.execute(text(f"SELECT COUNT(*) FROM {table}"))
                        count = result.fetchone()[0]
                        logger.info(f"{table}: {count:,} レコード")

                logger.info("✅ Cloud SQL接続テスト成功")
                return True

        except Exception as e:
            logger.error(f"❌ Cloud SQL接続テスト失敗: {e}")
            return False

    def run_full_migration(self):
        """完全移行の実行"""
        logger.info("🚀 Miraikakaku Cloud SQL移行開始")

        # 1. 接続確認
        if not self.check_connections():
            logger.error("データベース接続に失敗しました")
            return False

        # 2. データ差分分析
        self.analyze_data_differences()

        # 3. ユーザー確認
        print("\n" + "=" * 60)
        print("🔄 SQLite → Cloud SQL データ移行")
        print("現在のローカルSQLiteデータをCloud SQLに移行します")
        print("※既存のCloud SQLデータは上書きされる可能性があります")
        print("=" * 60)

        proceed = input("移行を実行しますか? (y/N): ")
        if proceed.lower() != "y":
            logger.info("移行をキャンセルしました")
            return False

        # 4. テーブル移行
        tables_to_migrate = [
            "stock_master",
            "stock_predictions",
            "stock_price_history",
            "ai_inference_log",
        ]

        success_count = 0
        for table in tables_to_migrate:
            if self.migrate_table_data(table):
                success_count += 1

        if success_count == len(tables_to_migrate):
            logger.info("✅ 全テーブル移行完了")
        else:
            logger.warning(
                f"⚠️  {success_count}/{len(tables_to_migrate)}テーブル移行完了"
            )

        # 5. アプリケーション設定更新
        if self.update_application_config():
            logger.info("✅ 設定ファイル更新完了")

        # 6. 最終テスト
        if self.test_cloud_sql_connection():
            logger.info("✅ Cloud SQL移行テスト成功")

        logger.info("🎉 Miraikakaku Cloud SQL移行完了!")
        logger.info("本格運用の準備が整いました")

        return True


def main():
    migrator = DatabaseMigrator()

    print("🔄 Miraikakaku Database Migration Tool")
    print("SQLiteからCloud SQLへの本格運用移行")
    print("-" * 50)

    migrator.run_full_migration()


if __name__ == "__main__":
    main()
