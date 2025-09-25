#!/bin/bash
# Production Health Check Script
set -e

API_URL="http://localhost:8080"
FRONTEND_URL="http://localhost:3000"

echo "🔍 Production Health Check - $(date)"
echo "=================================="

# Check API health
echo "Checking API health..."
if curl -f -s "$API_URL/health" > /dev/null; then
    echo "✅ API is healthy"
else
    echo "❌ API is down"
    exit 1
fi

# Check Frontend health
echo "Checking Frontend health..."
if curl -f -s "$FRONTEND_URL" > /dev/null; then
    echo "✅ Frontend is healthy"
else
    echo "❌ Frontend is down"
    exit 1
fi

# Check Database connection
echo "Checking Database connection..."
python3 -c "
import psycopg2
try:
    conn = psycopg2.connect(
        host='34.173.9.214',
        user='postgres',
        password='${DB_PASSWORD}',
        database='miraikakaku'
    )
    conn.close()
    print('✅ Database is connected')
except Exception as e:
    print(f'❌ Database connection failed: {e}')
    exit(1)
"

echo "✅ All systems healthy"
