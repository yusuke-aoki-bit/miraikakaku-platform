"""
Unit tests for batch data collection functions
"""
import pytest
from unittest.mock import patch, MagicMock
from datetime import datetime
import pandas as pd

@pytest.mark.unit
class TestDataCollection:
    """Test data collection functions"""

    @patch('functions.simple_batch_worker.yf.download')
    def test_fetch_stock_data(self, mock_yf_download):
        """Test stock data fetching"""
        # Mock yfinance response
        mock_data = pd.DataFrame({
            'Close': [100, 101, 102],
            'Open': [99, 100, 101],
            'High': [101, 102, 103],
            'Low': [98, 99, 100],
            'Volume': [1000, 1100, 1200]
        }, index=pd.date_range('2023-01-01', periods=3))

        mock_yf_download.return_value = mock_data

        # Import function after environment setup
        from functions.simple_batch_worker import fetch_stock_data

        result = fetch_stock_data("AAPL", "2023-01-01", "2023-01-03")

        assert result is not None
        assert len(result) == 3
        assert 'Close' in result.columns
        mock_yf_download.assert_called_once()

    @patch('functions.simple_batch_worker.psycopg2.connect')
    def test_database_connection(self, mock_connect):
        """Test database connection"""
        mock_conn = MagicMock()
        mock_connect.return_value = mock_conn

        from functions.simple_batch_worker import get_database_connection

        conn = get_database_connection()
        assert conn is not None
        mock_connect.assert_called_once()

    @pytest.mark.integration
    def test_data_validation(self):
        """Test data validation logic"""
        from functions.simple_batch_worker import validate_stock_data

        # Valid data
        valid_data = pd.DataFrame({
            'Close': [100.5, 101.2],
            'Volume': [1000, 1100]
        })

        assert validate_stock_data(valid_data) is True

        # Invalid data (missing required columns)
        invalid_data = pd.DataFrame({
            'Price': [100, 101]  # Wrong column name
        })

        assert validate_stock_data(invalid_data) is False

    def test_symbol_validation(self):
        """Test stock symbol validation"""
        from functions.simple_batch_worker import is_valid_symbol

        assert is_valid_symbol("AAPL") is True
        assert is_valid_symbol("GOOGL") is True
        assert is_valid_symbol("") is False
        assert is_valid_symbol(None) is False
        assert is_valid_symbol("TOOLONGSYMBOL") is False