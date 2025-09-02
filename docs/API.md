# Miraikakaku API Specification

## 1. Related Requirements

- The API must provide endpoints to support the following frontend features:
  - Searching for stocks.
  - Retrieving historical price data.
  - Retrieving future and historical predictions.
  - Retrieving AI decision factors.
- The prediction endpoints must support a horizon of 6 months based on 2 years of data.

---

## 2. API Endpoints

This document lists the API endpoints consumed by the Miraikakaku frontend.

### Stock Search

- **Endpoint**: `GET /api/finance/stocks/search`
- **Description**: Searches for stock symbols based on a query.
- **Query Parameters**:
  - `q` (string, required): The search query (e.g., "AAPL").
  - `limit` (integer, optional): The maximum number of results to return.

### Stock Price History

- **Endpoint**: `GET /api/finance/stocks/{symbol}/price`
- **Description**: Retrieves historical price data for a given stock symbol.
- **Path Parameters**:
  - `symbol` (string, required): The stock symbol (e.g., "AAPL").
- **Query Parameters**:
  - `days` (integer, optional): The number of days of historical data to retrieve (default: 730).

### Future Predictions

- **Endpoint**: `GET /api/finance/stocks/{symbol}/predictions`
- **Description**: Retrieves future stock price predictions.
- **Path Parameters**:
  - `symbol` (string, required): The stock symbol.
- **Query Parameters**:
  - `days` (integer, optional): The number of days into the future to predict (default: 180).

### Historical Predictions

- **Endpoint**: `GET /api/finance/stocks/{symbol}/predictions/history`
- **Description**: Retrieves historical prediction data to compare with actual prices.
- **Path Parameters**:
  - `symbol` (string, required): The stock symbol.
- **Query Parameters**:
  - `days` (integer, optional): The number of days of historical predictions to retrieve (default: 730).

### AI Decision Factors

- **Endpoint**: `GET /api/ai-factors/all`
- **Description**: Retrieves the factors and reasoning behind the AI's predictions.
- **Query Parameters**:
  - `symbol` (string, optional): Filter factors by stock symbol.