# 📡 Miraikakaku API Documentation

The Miraikakaku API provides comprehensive endpoints for stock market data, AI-powered predictions, and real-time financial analysis. Built with FastAPI, it offers automatic OpenAPI documentation and high-performance data access.

## 🌍 Base URLs

| Environment | Base URL | WebSocket URL |
|-------------|----------|---------------|
| **Development** | `http://localhost:8000` | `ws://localhost:8000` |
| **Production** | `https://api.miraikakaku.com` | `wss://api.miraikakaku.com` |

## 🔐 Authentication

### Authentication Methods
- **API Keys**: Required for production access
- **JWT Tokens**: For user-specific operations
- **CORS**: Configured for frontend origins

### Headers
```http
Authorization: Bearer <your-jwt-token>
X-API-Key: <your-api-key>
Content-Type: application/json
```

## 📊 Core API Endpoints

### 🏥 Health & Status

#### GET `/`
Root endpoint returning API information.

**Response:**
```json
{
  "message": "Miraikakaku API Server",
  "version": "1.0.0"
}
```

#### GET `/health`
Health check endpoint for monitoring services.

**Response:**
```json
{
  "status": "healthy",
  "service": "miraikakaku-api",
  "environment": "development"
}
```

---

### 🔍 Stock Search & Data

#### GET `/api/finance/stocks/search`
Search for stocks by symbol or company name.

**Parameters:**
- `query` (string, required): Search query (min length: 1)
- `limit` (integer, optional): Results limit (1-100, default: 10)

**Example Request:**
```bash
GET /api/finance/stocks/search?query=AAPL&limit=5
```

**Response:**
```json
[
  {
    "symbol": "AAPL",
    "company_name": "Apple Inc.",
    "exchange": "NASDAQ",
    "sector": "Technology",
    "industry": "Consumer Electronics"
  }
]
```

#### GET `/api/finance/stocks/{symbol}/price`
Retrieve historical price data for a specific stock.

**Parameters:**
- `symbol` (string, required): Stock symbol (e.g., "AAPL")
- `days` (integer, optional): Number of days to retrieve (1-365, default: 30)

**Example Request:**
```bash
GET /api/finance/stocks/AAPL/price?days=7
```

**Response:**
```json
[
  {
    "symbol": "AAPL",
    "date": "2025-01-20T00:00:00Z",
    "open_price": 150.25,
    "high_price": 152.80,
    "low_price": 149.10,
    "close_price": 151.75,
    "volume": 45234567,
    "data_source": "alpha_vantage"
  }
]
```

---

### 🤖 AI Predictions

#### GET `/api/finance/stocks/{symbol}/predictions`
Get AI-powered price predictions for a stock.

**Parameters:**
- `symbol` (string, required): Stock symbol
- `model_type` (string, optional): Filter by model type
- `days` (integer, optional): Prediction period (1-30, default: 7)

**Example Request:**
```bash
GET /api/finance/stocks/AAPL/predictions?days=14&model_type=lstm
```

**Response:**
```json
[
  {
    "symbol": "AAPL",
    "prediction_date": "2025-01-21T00:00:00Z",
    "predicted_price": 153.45,
    "confidence_score": 0.87,
    "model_type": "lstm",
    "prediction_horizon": 1,
    "is_active": true
  }
]
```

#### POST `/api/finance/stocks/{symbol}/predict`
Generate new AI predictions for a stock.

**Parameters:**
- `symbol` (string, required): Stock symbol

**Response:**
```json
{
  "message": "予測生成完了",
  "prediction_id": "12345"
}
```

#### GET `/api/finance/stocks/{symbol}/historical-predictions`
Compare past predictions with actual performance.

**Parameters:**
- `symbol` (string, required): Stock symbol
- `days` (integer, optional): Historical period (1-365, default: 30)

**Response:**
```json
[
  {
    "date": "2025-01-20",
    "predicted_price": 151.75,
    "actual_price": 151.20,
    "accuracy": 0.996,
    "confidence": 0.85
  }
]
```

---

### 📈 Rankings & Analytics

#### GET `/api/finance/rankings/accuracy`
Retrieve stocks ranked by prediction accuracy.

**Parameters:**
- `limit` (integer, optional): Results limit (1-50, default: 10)

**Response:**
```json
[
  {
    "symbol": "AAPL",
    "company_name": "Apple Inc.",
    "accuracy_score": 89.45,
    "prediction_count": 28
  }
]
```

#### GET `/api/finance/rankings/growth-potential`
Get stocks ranked by growth potential.

**Parameters:**
- `limit` (integer, optional): Results limit (1-50, default: 10)

**Response:**
```json
[
  {
    "symbol": "TSLA",
    "company_name": "Tesla, Inc.",
    "current_price": 245.80,
    "predicted_price": 267.45,
    "growth_potential": 8.82,
    "confidence": 0.78
  }
]
```

#### GET `/api/finance/rankings/composite`
Composite rankings combining accuracy and growth potential.

**Parameters:**
- `limit` (integer, optional): Results limit (1-50, default: 10)

**Response:**
```json
[
  {
    "symbol": "NVDA",
    "company_name": "NVIDIA Corporation",
    "composite_score": 85.67,
    "accuracy_score": 87.23,
    "growth_potential": 4.12,
    "prediction_count": 25
  }
]
```

---

## 🔌 WebSocket API

### Connection
Connect to real-time data streams via WebSocket.

**Connection URL:**
```
ws://localhost:8000/ws/stocks
```

### Message Types

#### Stock Price Updates
Real-time stock price updates.

**Message Format:**
```json
{
  "type": "price_update",
  "data": {
    "symbol": "AAPL",
    "price": 151.75,
    "change": 1.25,
    "change_percent": 0.83,
    "volume": 1234567,
    "timestamp": "2025-01-20T15:30:00Z"
  },
  "timestamp": "2025-01-20T15:30:00Z"
}
```

#### Prediction Updates
AI model prediction updates.

**Message Format:**
```json
{
  "type": "prediction_update",
  "data": {
    "symbol": "AAPL",
    "predicted_price": 153.45,
    "confidence": 0.87,
    "model": "lstm",
    "horizon": "1d"
  },
  "timestamp": "2025-01-20T15:30:00Z"
}
```

#### Market Alerts
Important market events and alerts.

**Message Format:**
```json
{
  "type": "market_alert",
  "data": {
    "alert_type": "volatility",
    "symbol": "TSLA",
    "message": "High volatility detected",
    "severity": "medium"
  },
  "timestamp": "2025-01-20T15:30:00Z"
}
```

### WebSocket Commands

#### Subscribe to Stock
```json
{
  "action": "subscribe",
  "symbol": "AAPL",
  "data_types": ["price", "predictions", "alerts"]
}
```

#### Unsubscribe from Stock
```json
{
  "action": "unsubscribe",
  "symbol": "AAPL"
}
```

---

## 📋 Data Models

### Stock Search Response
```typescript
interface StockSearchResponse {
  symbol: string;
  company_name: string;
  exchange: string;
  sector?: string;
  industry?: string;
}
```

### Stock Price Response
```typescript
interface StockPriceResponse {
  symbol: string;
  date: string;
  open_price?: number;
  high_price?: number;
  low_price?: number;
  close_price: number;
  volume?: number;
  data_source: string;
}
```

### Stock Prediction Response
```typescript
interface StockPredictionResponse {
  symbol: string;
  prediction_date: string;
  predicted_price: number;
  confidence_score?: number;
  model_type: string;
  prediction_horizon: number;
  is_active: boolean;
}
```

---

## 🚨 Error Handling

### HTTP Status Codes
- **200**: Success
- **400**: Bad Request - Invalid parameters
- **401**: Unauthorized - Authentication required
- **404**: Not Found - Resource doesn't exist
- **429**: Too Many Requests - Rate limit exceeded
- **500**: Internal Server Error - Server-side error

### Error Response Format
```json
{
  "error": {
    "code": "INVALID_SYMBOL",
    "message": "The provided stock symbol is invalid",
    "details": "Symbol 'INVALID' not found in database",
    "timestamp": "2025-01-20T15:30:00Z"
  }
}
```

### Common Error Codes
- `INVALID_SYMBOL`: Stock symbol not found
- `RATE_LIMIT_EXCEEDED`: Too many requests
- `PREDICTION_UNAVAILABLE`: AI predictions not available
- `DATA_SOURCE_ERROR`: External data source error
- `AUTHENTICATION_FAILED`: Invalid credentials

---

## 📊 Rate Limiting

### Limits by Endpoint Category
- **Search Endpoints**: 100 requests/minute
- **Price Data**: 200 requests/minute  
- **Predictions**: 50 requests/minute
- **WebSocket Connections**: 10 concurrent connections

### Headers
Rate limit information is included in response headers:
```http
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 95
X-RateLimit-Reset: 1642694400
```

---

## 🔧 Integration Examples

### JavaScript/TypeScript (Frontend)
```typescript
// API Client Configuration
const apiClient = {
  baseURL: process.env.NEXT_PUBLIC_API_BASE_URL,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  }
};

// Search Stocks
async function searchStocks(query: string): Promise<StockSearchResponse[]> {
  const response = await fetch(
    `${apiClient.baseURL}/api/finance/stocks/search?query=${query}`
  );
  
  if (!response.ok) {
    throw new Error(`API Error: ${response.status}`);
  }
  
  return response.json();
}

// Get Stock Predictions
async function getStockPredictions(symbol: string): Promise<StockPredictionResponse[]> {
  const response = await fetch(
    `${apiClient.baseURL}/api/finance/stocks/${symbol}/predictions`
  );
  
  return response.json();
}

// WebSocket Connection
const ws = new WebSocket(`${process.env.NEXT_PUBLIC_WS_URL}/ws/stocks`);

ws.onmessage = (event) => {
  const message = JSON.parse(event.data);
  
  switch (message.type) {
    case 'price_update':
      handlePriceUpdate(message.data);
      break;
    case 'prediction_update':
      handlePredictionUpdate(message.data);
      break;
  }
};
```

### Python (Backend Integration)
```python
import httpx
import asyncio

class MiraikakakuClient:
    def __init__(self, base_url: str, api_key: str = None):
        self.base_url = base_url
        self.headers = {"X-API-Key": api_key} if api_key else {}
    
    async def search_stocks(self, query: str) -> list:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.base_url}/api/finance/stocks/search",
                params={"query": query},
                headers=self.headers
            )
            return response.json()
    
    async def get_stock_price(self, symbol: str, days: int = 30) -> list:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.base_url}/api/finance/stocks/{symbol}/price",
                params={"days": days},
                headers=self.headers
            )
            return response.json()

# Usage
client = MiraikakakuClient("http://localhost:8000")
stocks = await client.search_stocks("AAPL")
```

### cURL Examples
```bash
# Search for stocks
curl -X GET "http://localhost:8000/api/finance/stocks/search?query=Apple&limit=5" \
     -H "Content-Type: application/json"

# Get historical prices
curl -X GET "http://localhost:8000/api/finance/stocks/AAPL/price?days=30" \
     -H "Content-Type: application/json"

# Get predictions
curl -X GET "http://localhost:8000/api/finance/stocks/AAPL/predictions?days=7" \
     -H "Content-Type: application/json"

# Generate new prediction
curl -X POST "http://localhost:8000/api/finance/stocks/AAPL/predict" \
     -H "Content-Type: application/json"
```

---

## 🏗 Development & Testing

### Running the API Locally
```bash
# Backend setup
cd miraikakakuapi/functions
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt

# Initialize database
python init_db.py

# Start API server
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### API Documentation
- **Interactive Docs**: `http://localhost:8000/docs` (Swagger UI)
- **ReDoc**: `http://localhost:8000/redoc`
- **OpenAPI Schema**: `http://localhost:8000/api/v1/openapi.json`

### Testing Endpoints
```bash
# Install testing dependencies
pip install pytest httpx

# Run API tests
python -m pytest tests/api/ -v

# Load testing
pip install locust
locust -f tests/load/api_test.py --host=http://localhost:8000
```

---

## 🌐 Deployment Configuration

### Environment Variables
```bash
# Database
DATABASE_URL=postgresql://user:pass@localhost:5432/miraikakaku

# External APIs
ALPHA_VANTAGE_API_KEY=your_api_key_here
POLYGON_API_KEY=your_api_key_here

# Security
SECRET_KEY=your-secret-key-here
ALLOWED_ORIGINS=https://miraikakaku.com,https://www.miraikakaku.com

# AI/ML Configuration
MODEL_UPDATE_INTERVAL=3600
PREDICTION_CONFIDENCE_THRESHOLD=0.6

# Performance
WORKER_COUNT=4
MAX_CONNECTIONS=100
TIMEOUT=60
```

### Docker Deployment
```dockerfile
# Build and run API container
docker build -t miraikakaku-api ./miraikakakuapi
docker run -p 8000:8000 \
  -e DATABASE_URL=$DATABASE_URL \
  -e ALPHA_VANTAGE_API_KEY=$API_KEY \
  miraikakaku-api
```

### Google Cloud Run
```bash
# Deploy to Google Cloud Run
gcloud run deploy miraikakaku-api \
  --source ./miraikakakuapi \
  --platform managed \
  --region asia-northeast1 \
  --allow-unauthenticated \
  --set-env-vars DATABASE_URL=$DATABASE_URL
```

---

## 📚 Additional Resources

### Related Documentation
- [Design System Documentation](./DESIGN_SYSTEM.md)
- [Frontend Components](./COMPONENTS.md)
- [Project Architecture](./ARCHITECTURE.md)

### External APIs
- [Alpha Vantage API](https://www.alphavantage.co/documentation/)
- [Polygon.io API](https://polygon.io/docs/stocks)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)

### Support
- **GitHub Issues**: [Report bugs and feature requests](https://github.com/yourusername/miraikakaku/issues)
- **API Status**: [Status page](https://status.miraikakaku.com)
- **Email Support**: api-support@miraikakaku.com

---

**Last Updated**: January 2025 | **API Version**: 1.0.0