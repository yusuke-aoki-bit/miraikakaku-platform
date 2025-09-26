from logging.config import fileConfig
from sqlalchemy import engine_from_config
from sqlalchemy import pool
from alembic import context
import os
import sys
from dotenv import load_dotenv

load_dotenv()

# Alembic Config オブジェクト
config = context.config

# ログ設定
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# パッケージパスを追加
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

# Import all models to ensure they're registered with Base
from functions.database.models.stock_master import StockMaster
from functions.database.models.stock_price_history import StockPriceHistory
from functions.database.models.stock_predictions import StockPredictions
from functions.database.models.base import Base

target_metadata = Base.metadata

def get_url():
    # Use environment variable or secure default
    return os.getenv("DATABASE_URL", "postgresql://user:password@localhost:5432/miraikakaku")

def run_migrations_offline() -> None:
    """'オフライン'モードでマイグレーションを実行"""
    url = get_url()
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()

def run_migrations_online() -> None:
    """'オンライン'モードでマイグレーションを実行"""
    configuration = config.get_section(config.config_ini_section)
    configuration["sqlalchemy.url"] = get_url()
    
    connectable = engine_from_config(
        configuration,
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection, target_metadata=target_metadata
        )

        with context.begin_transaction():
            context.run_migrations()

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()