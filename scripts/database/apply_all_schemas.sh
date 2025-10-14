#!/bin/bash

# ============================================================
# Phase 7-10 Database Schema Application Script
# ============================================================
# This script applies all required database schemas for:
# - Phase 8: Watchlist (user_watchlists table)
# - Phase 9: Portfolio (portfolio_holdings, portfolio_snapshots tables + views)
# - Phase 10: Alerts (price_alerts table)
#
# Usage:
#   1. Ensure PostgreSQL client is installed
#   2. Update connection parameters if needed
#   3. Run: bash apply_all_schemas.sh
# ============================================================

# Database connection parameters
DB_HOST="${POSTGRES_HOST:-localhost}"
DB_PORT="${POSTGRES_PORT:-5433}"
DB_USER="${POSTGRES_USER:-postgres}"
DB_PASS="${POSTGRES_PASSWORD:-Miraikakaku2024!}"
DB_NAME="${POSTGRES_DB:-miraikakaku}"

echo "========================================"
echo "Phase 7-10 Schema Application"
echo "========================================"
echo "Database: $DB_NAME @ $DB_HOST:$DB_PORT"
echo ""

# Function to execute SQL file
execute_sql() {
    local sql_file=$1
    local description=$2

    echo "=== $description ==="
    PGPASSWORD="$DB_PASS" psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "$DB_NAME" -f "$sql_file"

    if [ $? -eq 0 ]; then
        echo "✅ $description completed successfully"
    else
        echo "❌ $description failed"
        return 1
    fi
    echo ""
}

# Apply schemas in order
execute_sql "create_watchlist_schema.sql" "Watchlist Schema (Phase 8)" || exit 1
execute_sql "apply_portfolio_schema.sql" "Portfolio Schema (Phase 9)" || exit 1
execute_sql "create_alerts_schema.sql" "Alerts Schema (Phase 10)" || exit 1

echo "========================================"
echo "✅ All schemas applied successfully!"
echo "========================================"
echo ""
echo "Next steps:"
echo "1. Verify tables with: psql -c '\dt' "
echo "2. Test API endpoints"
echo "3. Create frontend pages for watchlist/portfolio/alerts"
echo ""
