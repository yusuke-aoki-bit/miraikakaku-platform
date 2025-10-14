FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy scripts
COPY news_sentiment_analyzer.py .
COPY generate_sentiment_enhanced_predictions.py .

# Default command
CMD ["python", "news_sentiment_analyzer.py"]
