"""Add missing prediction columns

Revision ID: 001_add_prediction_columns
Revises:
Create Date: 2025-09-19 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '001_add_prediction_columns'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Add missing columns to stock_predictions table"""

    # Check if table exists
    connection = op.get_bind()
    inspector = sa.inspect(connection)

    if 'stock_predictions' not in inspector.get_table_names():
        print("stock_predictions table does not exist, skipping migration")
        return

    # Get existing columns
    existing_columns = [col['name'] for col in inspector.get_columns('stock_predictions')]

    # Add target_date column if it doesn't exist
    if 'target_date' not in existing_columns:
        op.add_column('stock_predictions', sa.Column('target_date', sa.TIMESTAMP(), nullable=True))
        print("Added target_date column")

    # Add actual_price column if it doesn't exist
    if 'actual_price' not in existing_columns:
        op.add_column('stock_predictions', sa.Column('actual_price', sa.NUMERIC(12, 4), nullable=True))
        print("Added actual_price column")

    # Add accuracy_score column if it doesn't exist
    if 'accuracy_score' not in existing_columns:
        op.add_column('stock_predictions', sa.Column('accuracy_score', sa.NUMERIC(5, 4), nullable=True))
        print("Added accuracy_score column")

    # Add is_validated column if it doesn't exist
    if 'is_validated' not in existing_columns:
        op.add_column('stock_predictions', sa.Column('is_validated', sa.Boolean(), nullable=True, default=False))
        print("Added is_validated column")

    # Create indexes for performance
    try:
        op.create_index('idx_predictions_symbol_date', 'stock_predictions', ['symbol', 'prediction_date'], unique=False, if_not_exists=True)
        op.create_index('idx_predictions_target_date', 'stock_predictions', ['target_date'], unique=False, if_not_exists=True, postgresql_where=sa.text('target_date IS NOT NULL'))
        op.create_index('idx_predictions_validated', 'stock_predictions', ['is_validated'], unique=False, if_not_exists=True, postgresql_where=sa.text('is_validated = TRUE'))
        op.create_index('idx_predictions_actual_price', 'stock_predictions', ['actual_price'], unique=False, if_not_exists=True, postgresql_where=sa.text('actual_price IS NOT NULL'))
        print("Created performance indexes")
    except Exception as e:
        print(f"Index creation warning: {e}")


def downgrade() -> None:
    """Remove added columns and indexes"""

    # Drop indexes
    try:
        op.drop_index('idx_predictions_actual_price', table_name='stock_predictions', if_exists=True)
        op.drop_index('idx_predictions_validated', table_name='stock_predictions', if_exists=True)
        op.drop_index('idx_predictions_target_date', table_name='stock_predictions', if_exists=True)
        op.drop_index('idx_predictions_symbol_date', table_name='stock_predictions', if_exists=True)
    except Exception as e:
        print(f"Index drop warning: {e}")

    # Drop columns
    connection = op.get_bind()
    inspector = sa.inspect(connection)

    if 'stock_predictions' in inspector.get_table_names():
        existing_columns = [col['name'] for col in inspector.get_columns('stock_predictions')]

        if 'is_validated' in existing_columns:
            op.drop_column('stock_predictions', 'is_validated')
        if 'accuracy_score' in existing_columns:
            op.drop_column('stock_predictions', 'accuracy_score')
        if 'actual_price' in existing_columns:
            op.drop_column('stock_predictions', 'actual_price')
        if 'target_date' in existing_columns:
            op.drop_column('stock_predictions', 'target_date')