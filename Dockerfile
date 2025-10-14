FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY api_predictions.py .
COPY auth_utils.py .
COPY auth_endpoints.py .
COPY generate_predictions_simple.py .
COPY generate_news_enhanced_predictions.py .
COPY accuracy_checker.py .
COPY finnhub_news_collector.py .
COPY yfinance_jp_news_collector.py .
COPY newsapi_collector.py .
COPY scripts/news-sentiment/schema_news_sentiment.sql .
COPY schema_portfolio.sql .
COPY create_watchlist_schema.sql .
COPY create_performance_schema.sql .
COPY create_auth_schema.sql .
COPY src/ ./src/
COPY .env* ./

CMD ["uvicorn", "api_predictions:app", "--host", "0.0.0.0", "--port", "8080"]
