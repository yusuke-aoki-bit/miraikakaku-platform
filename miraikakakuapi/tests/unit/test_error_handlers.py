"""
Unit tests for error handling functionality.
"""
import pytest
import asyncio
from unittest.mock import Mock, patch
from fastapi import HTTPException, Request
from fastapi.responses import JSONResponse
from sqlalchemy.exc import IntegrityError, OperationalError

from functions.error_handlers import (
    MiraikakakuError,
    DataFetchError,
    PredictionError,
    ValidationError,
    DatabaseError,
    RateLimitError,
    create_error_response,
    miraikakaku_exception_handler,
    validation_exception_handler,
    database_exception_handler,
    http_exception_handler,
    general_exception_handler,
    timeout_exception_handler,
    validate_stock_symbol,
    validate_date_range,
    safe_execute,
    safe_execute_async
)


@pytest.mark.unit
def test_create_error_response():
    """Test error response creation."""
    response = create_error_response(
        error_code="TEST_ERROR",
        message="Test message",
        status_code=400,
        details={"field": "value"}
    )

    assert response["error"]["code"] == "TEST_ERROR"
    assert response["error"]["message"] == "Test message"
    assert response["error"]["status_code"] == 400
    assert response["error"]["details"]["field"] == "value"


@pytest.mark.unit
def test_miraikakaku_error_creation():
    """Test custom error classes."""
    # Base MiraikakakuError
    error = MiraikakakuError("Test message", "TEST_CODE", 400)
    assert error.message == "Test message"
    assert error.error_code == "TEST_CODE"
    assert error.status_code == 400

    # DataFetchError
    data_error = DataFetchError("Custom message")
    assert data_error.error_code == "DATA_FETCH_ERROR"
    assert data_error.status_code == 503

    # PredictionError
    pred_error = PredictionError()
    assert pred_error.error_code == "PREDICTION_ERROR"
    assert pred_error.status_code == 500


@pytest.mark.unit
async def test_miraikakaku_exception_handler():
    """Test MiraiKakaku exception handler."""
    request = Mock(spec=Request)
    request.url.path = "/test"
    request.method = "GET"

    exc = DataFetchError("Test data fetch error")

    with patch('functions.error_handlers.logger') as mock_logger:
        response = await miraikakaku_exception_handler(request, exc)

        assert isinstance(response, JSONResponse)
        assert response.status_code == 503
        mock_logger.error.assert_called_once()


@pytest.mark.unit
async def test_timeout_exception_handler():
    """Test timeout exception handler."""
    request = Mock(spec=Request)
    request.url.path = "/test"
    request.method = "GET"

    exc = asyncio.TimeoutError()

    with patch('functions.error_handlers.logger') as mock_logger:
        response = await timeout_exception_handler(request, exc)

        assert isinstance(response, JSONResponse)
        assert response.status_code == 504
        mock_logger.warning.assert_called_once()


@pytest.mark.unit
async def test_database_exception_handler():
    """Test database exception handler."""
    request = Mock(spec=Request)
    request.url.path = "/test"
    request.method = "POST"

    # Test IntegrityError
    integrity_exc = IntegrityError("statement", "params", "orig")

    with patch('functions.error_handlers.logger') as mock_logger:
        response = await database_exception_handler(request, integrity_exc)

        assert isinstance(response, JSONResponse)
        assert response.status_code == 409
        mock_logger.error.assert_called_once()

    # Test OperationalError
    operational_exc = OperationalError("statement", "params", "orig")

    with patch('functions.error_handlers.logger') as mock_logger:
        response = await database_exception_handler(request, operational_exc)

        assert isinstance(response, JSONResponse)
        assert response.status_code == 503


@pytest.mark.unit
async def test_http_exception_handler():
    """Test HTTP exception handler."""
    request = Mock(spec=Request)
    request.url.path = "/test"
    request.method = "GET"

    exc = HTTPException(status_code=404, detail="Not found")

    with patch('functions.error_handlers.logger') as mock_logger:
        response = await http_exception_handler(request, exc)

        assert isinstance(response, JSONResponse)
        assert response.status_code == 404
        mock_logger.info.assert_called_once()


@pytest.mark.unit
async def test_general_exception_handler():
    """Test general exception handler."""
    request = Mock(spec=Request)
    request.url.path = "/test"
    request.method = "GET"

    exc = ValueError("Test error")

    with patch('functions.error_handlers.logger') as mock_logger:
        with patch.dict('os.environ', {'DEBUG': 'true'}):
            response = await general_exception_handler(request, exc)

            assert isinstance(response, JSONResponse)
            assert response.status_code == 500
            mock_logger.error.assert_called_once()


@pytest.mark.unit
def test_validate_stock_symbol():
    """Test stock symbol validation."""
    # Valid symbols
    validate_stock_symbol("AAPL")
    validate_stock_symbol("GOOGL")
    validate_stock_symbol("MSFT")
    validate_stock_symbol("TSM")

    # Invalid symbols
    with pytest.raises(ValidationError):
        validate_stock_symbol("")

    with pytest.raises(ValidationError):
        validate_stock_symbol("TOOLONGSTOCKSYMBOL")

    with pytest.raises(ValidationError):
        validate_stock_symbol("AAPL@")

    with pytest.raises(ValidationError):
        validate_stock_symbol("AA PL")


@pytest.mark.unit
def test_validate_date_range():
    """Test date range validation."""
    # Valid date ranges
    validate_date_range("2023-01-01", "2023-12-31")
    validate_date_range("2024-01-01T00:00:00Z", "2024-01-02T00:00:00Z")

    # Invalid date ranges
    with pytest.raises(ValidationError):
        validate_date_range("2023-12-31", "2023-01-01")  # End before start

    with pytest.raises(ValidationError):
        validate_date_range("2020-01-01", "2026-01-01")  # Too large range

    with pytest.raises(ValidationError):
        validate_date_range("invalid-date", "2023-01-01")  # Invalid format


@pytest.mark.unit
def test_safe_execute():
    """Test safe execution wrapper."""
    # Test successful execution
    def successful_func(x, y):
        return x + y

    result = safe_execute(successful_func, 2, 3)
    assert result == 5

    # Test execution with MiraikakakuError (should re-raise)
    def miraikakaku_error_func():
        raise DataFetchError("Test error")

    with pytest.raises(DataFetchError):
        safe_execute(miraikakaku_error_func)

    # Test execution with other exception (should wrap)
    def generic_error_func():
        raise ValueError("Generic error")

    with pytest.raises(MiraikakakuError):
        safe_execute(generic_error_func)


@pytest.mark.unit
async def test_safe_execute_async():
    """Test safe async execution wrapper."""
    # Test successful execution
    async def successful_async_func(x, y):
        return x * y

    result = await safe_execute_async(successful_async_func, 3, 4)
    assert result == 12

    # Test execution with MiraikakakuError (should re-raise)
    async def miraikakaku_error_async_func():
        raise PredictionError("Async test error")

    with pytest.raises(PredictionError):
        await safe_execute_async(miraikakaku_error_async_func)

    # Test execution with timeout (should re-raise)
    async def timeout_func():
        raise asyncio.TimeoutError()

    with pytest.raises(asyncio.TimeoutError):
        await safe_execute_async(timeout_func)

    # Test execution with other exception (should wrap)
    async def generic_async_error_func():
        raise RuntimeError("Generic async error")

    with pytest.raises(MiraikakakuError):
        await safe_execute_async(generic_async_error_func)


@pytest.mark.unit
def test_error_inheritance():
    """Test that custom errors inherit correctly."""
    error = DataFetchError("Test message")

    assert isinstance(error, MiraikakakuError)
    assert isinstance(error, Exception)
    assert str(error) == "Test message"


@pytest.mark.unit
def test_rate_limit_error():
    """Test rate limit error functionality."""
    error = RateLimitError("Custom rate limit message")

    assert error.error_code == "RATE_LIMIT_ERROR"
    assert error.status_code == 429
    assert error.message == "Custom rate limit message"