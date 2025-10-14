#!/bin/bash

# ============================================================
# Phase 7-10 E2E API Testing Script
# ============================================================
# This script tests all API endpoints for:
# - Phase 6: Authentication (login, register, me)
# - Phase 8: Watchlist (add, list, details, update, delete)
# - Phase 9: Portfolio (add, list, performance, summary, update, delete)
# - Phase 10: Alerts (create, list, details, triggered, check, update, delete)
# ============================================================

API_URL="${API_URL:-https://miraikakaku-api-465603676610.us-central1.run.app}"
TEST_USER="testuser2025"
TEST_PASSWORD="password123"

echo "========================================"
echo "Phase 7-10 API E2E Tests"
echo "========================================"
echo "API URL: $API_URL"
echo ""

# Color codes for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Test counter
TOTAL_TESTS=0
PASSED_TESTS=0
FAILED_TESTS=0

# Function to test endpoint
test_endpoint() {
    local test_name=$1
    local method=$2
    local endpoint=$3
    local data=$4
    local headers=$5

    TOTAL_TESTS=$((TOTAL_TESTS + 1))
    echo -n "[$TOTAL_TESTS] Testing: $test_name ... "

    if [ -z "$data" ]; then
        response=$(curl -s -X $method "$API_URL$endpoint" $headers -w "\nSTATUS:%{http_code}")
    else
        response=$(curl -s -X $method "$API_URL$endpoint" $headers -H "Content-Type: application/json" -d "$data" -w "\nSTATUS:%{http_code}")
    fi

    status=$(echo "$response" | grep "STATUS:" | cut -d':' -f2)
    body=$(echo "$response" | grep -v "STATUS:")

    if [[ $status -ge 200 && $status -lt 300 ]]; then
        echo -e "${GREEN}✅ PASS${NC} (HTTP $status)"
        PASSED_TESTS=$((PASSED_TESTS + 1))
        return 0
    else
        echo -e "${RED}❌ FAIL${NC} (HTTP $status)"
        echo "Response: $body"
        FAILED_TESTS=$((FAILED_TESTS + 1))
        return 1
    fi
}

# ============================================================
# Phase 6: Authentication Tests
# ============================================================
echo "=== Phase 6: Authentication Tests ==="

# Test 1: Login
test_endpoint "Login" "POST" "/api/auth/login" \
    '{"username":"'$TEST_USER'","password":"'$TEST_PASSWORD'"}'

# Extract access token from last response
ACCESS_TOKEN=$(echo "$response" | grep -o '"access_token":"[^"]*' | cut -d'"' -f4)

if [ -z "$ACCESS_TOKEN" ]; then
    echo -e "${RED}❌ Failed to extract access token. Exiting.${NC}"
    exit 1
fi

echo "Access Token: ${ACCESS_TOKEN:0:50}..."
echo ""

# Test 2: Get current user info
test_endpoint "Get user info (/me)" "GET" "/api/auth/me" \
    "" "-H 'Authorization: Bearer $ACCESS_TOKEN'"

echo ""

# ============================================================
# Phase 8: Watchlist Tests
# ============================================================
echo "=== Phase 8: Watchlist Tests ==="

# Test 3: Get watchlist (empty initially)
test_endpoint "Get watchlist" "GET" "/api/watchlist" \
    "" "-H 'Authorization: Bearer $ACCESS_TOKEN'"

# Test 4: Add stock to watchlist
test_endpoint "Add stock to watchlist (AAPL)" "POST" "/api/watchlist" \
    '{"symbol":"AAPL","notes":"Test watchlist item"}' \
    "-H 'Authorization: Bearer $ACCESS_TOKEN'"

# Test 5: Add another stock
test_endpoint "Add stock to watchlist (TSLA)" "POST" "/api/watchlist" \
    '{"symbol":"TSLA","notes":"Tesla stock"}' \
    "-H 'Authorization: Bearer $ACCESS_TOKEN'"

# Test 6: Get watchlist with details
test_endpoint "Get watchlist details" "GET" "/api/watchlist/details" \
    "" "-H 'Authorization: Bearer $ACCESS_TOKEN'"

# Test 7: Update watchlist item notes
test_endpoint "Update watchlist notes" "PUT" "/api/watchlist/AAPL" \
    '{"notes":"Updated notes for Apple"}' \
    "-H 'Authorization: Bearer $ACCESS_TOKEN'"

# Test 8: Delete watchlist item
test_endpoint "Delete watchlist item (TSLA)" "DELETE" "/api/watchlist/TSLA" \
    "" "-H 'Authorization: Bearer $ACCESS_TOKEN'"

echo ""

# ============================================================
# Phase 9: Portfolio Tests
# ============================================================
echo "=== Phase 9: Portfolio Tests ==="

# Test 9: Get portfolio (empty initially)
test_endpoint "Get portfolio" "GET" "/api/portfolio" \
    "" "-H 'Authorization: Bearer $ACCESS_TOKEN'"

# Test 10: Add holding to portfolio
test_endpoint "Add portfolio holding (AAPL)" "POST" "/api/portfolio" \
    '{"symbol":"AAPL","quantity":10,"average_buy_price":150.50,"buy_date":"2024-01-15","notes":"Long-term hold"}' \
    "-H 'Authorization: Bearer $ACCESS_TOKEN'"

# Extract portfolio ID from response
PORTFOLIO_ID=$(echo "$body" | grep -o '"id":[0-9]*' | cut -d':' -f2 | head -1)

# Test 11: Add another holding
test_endpoint "Add portfolio holding (MSFT)" "POST" "/api/portfolio" \
    '{"symbol":"MSFT","quantity":5,"average_buy_price":300.00,"buy_date":"2024-02-01","notes":"Tech diversification"}' \
    "-H 'Authorization: Bearer $ACCESS_TOKEN'"

# Test 12: Get portfolio with performance
test_endpoint "Get portfolio performance" "GET" "/api/portfolio/performance" \
    "" "-H 'Authorization: Bearer $ACCESS_TOKEN'"

# Test 13: Get portfolio summary
test_endpoint "Get portfolio summary" "GET" "/api/portfolio/summary" \
    "" "-H 'Authorization: Bearer $ACCESS_TOKEN'"

if [ ! -z "$PORTFOLIO_ID" ]; then
    # Test 14: Update portfolio holding
    test_endpoint "Update portfolio holding" "PUT" "/api/portfolio/$PORTFOLIO_ID" \
        '{"quantity":15,"notes":"Increased position"}' \
        "-H 'Authorization: Bearer $ACCESS_TOKEN'"

    # Test 15: Delete portfolio holding
    test_endpoint "Delete portfolio holding" "DELETE" "/api/portfolio/$PORTFOLIO_ID" \
        "" "-H 'Authorization: Bearer $ACCESS_TOKEN'"
fi

echo ""

# ============================================================
# Phase 10: Alerts Tests
# ============================================================
echo "=== Phase 10: Alerts Tests ==="

# Test 16: Get alerts (empty initially)
test_endpoint "Get alerts" "GET" "/api/alerts" \
    "" "-H 'Authorization: Bearer $ACCESS_TOKEN'"

# Test 17: Create price alert (price above)
test_endpoint "Create alert (AAPL price above)" "POST" "/api/alerts" \
    '{"symbol":"AAPL","alert_type":"price_above","threshold":200.00,"notes":"Sell target"}' \
    "-H 'Authorization: Bearer $ACCESS_TOKEN'"

# Extract alert ID from response
ALERT_ID=$(echo "$body" | grep -o '"id":[0-9]*' | cut -d':' -f2 | head -1)

# Test 18: Create another alert (price below)
test_endpoint "Create alert (AAPL price below)" "POST" "/api/alerts" \
    '{"symbol":"AAPL","alert_type":"price_below","threshold":140.00,"notes":"Buy opportunity"}' \
    "-H 'Authorization: Bearer $ACCESS_TOKEN'"

# Test 19: Get alerts with details
test_endpoint "Get alerts details" "GET" "/api/alerts/details" \
    "" "-H 'Authorization: Bearer $ACCESS_TOKEN'"

# Test 20: Check alerts manually
test_endpoint "Manual alert check" "POST" "/api/alerts/check" \
    "" "-H 'Authorization: Bearer $ACCESS_TOKEN'"

# Test 21: Get triggered alerts
test_endpoint "Get triggered alerts" "GET" "/api/alerts/triggered" \
    "" "-H 'Authorization: Bearer $ACCESS_TOKEN'"

if [ ! -z "$ALERT_ID" ]; then
    # Test 22: Update alert
    test_endpoint "Update alert threshold" "PUT" "/api/alerts/$ALERT_ID" \
        '{"threshold":210.00,"notes":"Updated sell target"}' \
        "-H 'Authorization: Bearer $ACCESS_TOKEN'"

    # Test 23: Deactivate alert
    test_endpoint "Deactivate alert" "PUT" "/api/alerts/$ALERT_ID" \
        '{"is_active":false}' \
        "-H 'Authorization: Bearer $ACCESS_TOKEN'"

    # Test 24: Delete alert
    test_endpoint "Delete alert" "DELETE" "/api/alerts/$ALERT_ID" \
        "" "-H 'Authorization: Bearer $ACCESS_TOKEN'"
fi

echo ""

# ============================================================
# Test Summary
# ============================================================
echo "========================================"
echo "Test Summary"
echo "========================================"
echo "Total Tests: $TOTAL_TESTS"
echo -e "${GREEN}Passed: $PASSED_TESTS${NC}"
if [ $FAILED_TESTS -gt 0 ]; then
    echo -e "${RED}Failed: $FAILED_TESTS${NC}"
else
    echo "Failed: $FAILED_TESTS"
fi

if [ $FAILED_TESTS -eq 0 ]; then
    echo ""
    echo -e "${GREEN}✅ ALL TESTS PASSED!${NC}"
    exit 0
else
    echo ""
    echo -e "${YELLOW}⚠️  Some tests failed. Review output above.${NC}"
    exit 1
fi
