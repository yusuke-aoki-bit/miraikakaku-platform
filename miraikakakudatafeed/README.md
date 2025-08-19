# Miraikakaku Data Feed Service

独立した株価データフィード用マイクロサービス。15,868証券のリアルタイムデータ提供。

## 🎯 Purpose

**Single Source of Truth for Stock Data**  
- 日本株4,168社（TSE全上場企業100%カバレッジ）
- 米国株8,700社（NASDAQ, NYSE, その他主要取引所）
- ETF 3,000銘柄（最適化された流動性重視選別）

## 🚀 Features

- **Multi-Source Data Aggregation**: yfinance, Alpha Vantage, NASDAQ FTP
- **Real-time Price Feeds**: WebSocket & REST API
- **Smart Caching**: In-memory database with intelligent refresh
- **Universal Search**: Symbol, company name, sector cross-search
- **Performance Optimized**: <100ms response time for cached data

## 📡 API Endpoints

### Health Check
```
GET /health
Response: {"status":"healthy","service":"universal-stock-api"}
```

### Stock Search
```
GET /search?query=apple&limit=10
```

### Real-time Price
```
GET /price/{symbol}?period=1d
```

### Market Overview
```
GET /markets/overview
```

## 🐳 Docker Deployment

```bash
# Build image
docker build -t miraikakaku-datafeed .

# Run container
docker run -p 8000:8000 miraikakaku-datafeed
```

## 🔧 Configuration

Environment Variables:
- `ALPHA_VANTAGE_API_KEY`: Alpha Vantage API key
- `PORT`: Service port (default: 8000)
- `LOG_LEVEL`: Logging level (default: INFO)

## 📊 Data Sources Priority

1. **Primary**: yfinance (real-time, free)
2. **Secondary**: Alpha Vantage (fundamental data)
3. **Tertiary**: NASDAQ FTP (official listings)
4. **Cache**: In-memory (5min refresh cycle)

## 🔄 Integration with Main API

The main Miraikakaku API (`miraikakakuapi/functions/`) consumes this service:
- Database-driven predictions and analysis
- User authentication and portfolios  
- This service provides raw market data only

---

**Service Type**: Data Feed Microservice  
**Port**: 8000  
**Dependencies**: External APIs only  
**Database**: In-memory (no persistence required)